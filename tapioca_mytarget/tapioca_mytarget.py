# coding: utf-8
import logging
import time
from datetime import datetime, timedelta

import pandas as pd
import requests
from dateutil import parser
from pandas.io.json import json_normalize
from tapioca import (
    TapiocaAdapter, generate_wrapper_from_adapter, JSONAdapterMixin)

from tapioca_mytarget import exceptions
from .resource_mapping import RESOURCE_MAPPING

logging.basicConfig(level=logging.DEBUG)


class MytargetClientAdapter(JSONAdapterMixin, TapiocaAdapter):
    end_point = 'https://{}/'
    api_root = end_point+'api/'
    resource_mapping = RESOURCE_MAPPING

    PRODUCTION_HOST = 'target.my.com'
    SANDBOX_HOST = 'target-sandbox.my.com'

    def __init__(self, *args, **kwargs):
        """
        Низкоуровневый API.

        :param access_token: str : токен доступа
        :param retry_request_if_limit: bool : ожидать и повторять запрос,
            если закончилась квота запросов к апи.
        :param language: str : ru|en|{other} :
            язык в котором будут возвращены некоторые данные, например справочников.

        low_api = Mytarget(access_token=ACCESS_TOKEN,
                       retry_request_if_limit=True)
        result = low_api.user2().get()
        data = result().data  # данные в формате json
        df = result().to_df()  # данные в формате pandas dataframe
        """
        super().__init__(*args, **kwargs)

    def get_url_root(self, api_params):
        if api_params.get('is_sandbox', False):
            return self.end_point.format(self.SANDBOX_HOST)
        return self.end_point.format(self.PRODUCTION_HOST)

    def get_api_root(self, api_params):
        return self.get_url_root(api_params)+'api/'

    def get_request_kwargs(self, api_params, *args, **kwargs):
        params = super().get_request_kwargs(api_params, *args, **kwargs)

        token = api_params.get('access_token')
        if token:
            params['headers'].update(
                {'Authorization': 'Bearer {}'.format(token)})

        if api_params.get('language', False):
            params['headers'].update(
                {'Accept-Language': api_params.get('language')})
        else:
            params['headers'].update({'Accept-Language': 'ru'})

        return params

    def wrapper_call_exception(self, response, tapioca_exception,
                               api_params, *args, **kwargs):
        if response.status_code == 400:
            raise exceptions.MytargetApiError(response)
        elif response.status_code == 401:
            raise exceptions.MytargetTokenError(response)
        elif response.status_code == 429:
            raise exceptions.MytargetLimitError(response)
        elif response.status_code == 404:
            raise exceptions.MytargetApiError(response)
        raise tapioca_exception

    def retry_request(self, response, tapioca_exception, api_params,
                      *args, **kwargs):
        """
        Условия повторения запроса.

        response = tapioca_exception.client().response
        status_code = tapioca_exception.client().status_code
        response_data = tapioca_exception.client().data
        """
        response_data = tapioca_exception.client().data
        remaining = response_data.get('remaining')
        if remaining:
            if api_params.get('retry_request_if_limit', False):
                if remaining.get('3600', remaining.get('60', True)):
                    if remaining.get('1') == 0:
                        logging.debug('Исчерпан лимит запросов, '
                                      'повтор через 1 секунду')
                        time.sleep(1)
                        return True
                else:
                    logging.info('Исчерпан лимит запросов')
        return False

    def to_df(self, data, *args, **kwargs):
        """Преобразование в DataFrame"""
        try:
            df = json_normalize(data.get('items') or data)
        except Exception:
            raise TypeError('Не удалось преобразовать в DataFrame')
        else:
            return df


Mytarget = generate_wrapper_from_adapter(MytargetClientAdapter)


class MytargetLight:
    CAMPAIGN_STATS = 'campaigns'
    BANNER_STATS = 'banners'
    USER_STATS = 'users'
    _SUMMARY_STATS = 'summary'
    _DAY_STATS = 'day'

    def __init__(self, access_token,
                 as_dataframe=False,
                 retry_request_if_limit=True,
                 language='ru',
                 *args, **kwargs):
        """
        Обертка над классом Mytarget (низкоуровневой оберткой).

        :param access_token: str : токен доступа
        :param as_dataframe: bool : преобразовывать в DataFrame
        :param retry_request_if_limit: bool : ожидать и повторять запрос,
            если закончилась квота запросов к апи.
        :param default_url_params: dict : параметры по умолчанию для вставки в url
        :param language: str : ru|en|{other} :
            язык в котором будут возвращены некоторые данные, например справочников.
        :param args:
        :param kwargs:
        """
        self._adapter = MytargetClientAdapter(
            access_token=access_token,
            retry_request_if_limit=retry_request_if_limit,
            language=language,
            *args, **kwargs)
        self.low_api = Mytarget(
            access_token=access_token,
            retry_request_if_limit=retry_request_if_limit,
            language=language,
            *args, **kwargs)
        self.as_dataframe = as_dataframe

    def _grouper_list(self, arr, count):
        if count == 1:
            return [[i] for i in arr]
        else:
            count = len(arr) // count+1
            return [arr[i::count] for i in range(count)]

    def _period_range(self, date_from, date_to, delta):
        """
        Генерация периодов для получения статистики.

        :param delta: int : кол-во дней в одном периоде
        :return: [..., ('2019-01-01', '2019-01-01')]
        """
        if not isinstance(date_from, datetime):
            date_from = parser.parse(date_from)
        if not isinstance(date_to, datetime):
            date_to = parser.parse(date_to)

        periods = []
        dt2 = None
        while True:
            dt1 = dt2+timedelta(1) if dt2 else date_from
            dt2 = dt1+timedelta(delta)
            if dt2 > date_to:
                if dt1 <= date_to:
                    periods.append((dt1.strftime('%Y-%m-%d'),
                                    date_to.strftime('%Y-%m-%d')))
                break
            periods.append((dt1.strftime('%Y-%m-%d'),
                            dt2.strftime('%Y-%m-%d')))
        return periods

    def _stats_to_df(self, results):
        """Преобразует данные статистики в dataframe."""
        try:
            df_list = []
            for result in results:
                result = result().data
                for i in result['items']:
                    rows = i.get('rows') or i.get('total')
                    df_ = json_normalize(rows)
                    df_['id'] = i['id']
                    df_list.append(df_)
            df = pd.concat(df_list, sort=False).reset_index(drop=True)
        except Exception:
            raise TypeError('Не удалось преобразовать в DataFrame')
        else:
            return df

    def _objects_to_df(self, results):
        """Преобразует данные объектов в dataframe."""
        try:
            df_list = []
            for result in results:
                data = result().data
                df_ = json_normalize(data.get('items') or result)
                df_list.append(df_)
            df = pd.concat(df_list, sort=False).reset_index(drop=True)
        except Exception:
            raise TypeError('Не удалось преобразовать в DataFrame')
        else:
            return df

    def _to_format(self, method, results, as_dataframe=None,
                   is_union_results=True):
        """Преобразует в указанный формат."""
        if (self.as_dataframe and as_dataframe is not False) \
                or as_dataframe:
            if method == self.get_stats.__name__:
                return self._stats_to_df(results)
            else:
                return self._objects_to_df(results)

        elif is_union_results:
            # Объединить данные в один список.
            union = []
            for result in results:
                try:
                    union += result().data['items']
                except KeyError:
                    logging.info('Не смог найти ключ items в {}'
                                 .format(result))
                    raise
            return union
        else:
            # Каждый ответ отдельно, в списке.
            return results

    def _request_objects(self, method, limit=None, params=None,
                         limit_in_request=50, as_dataframe=False):
        """
        Метод запрашивает все объекты.
        """
        if params and params.get('limit'):
            raise ValueError('Укажите limit при вызове метода, а не в параметре.')
        params = params or {}
        offset = params.get('offset') or 0
        # 1 ставим, чтоб сделать первый запрос,
        # а в ответе станет ясно, сколько сделать запросов.
        count = limit or 1
        results = []
        while count > offset:
            if limit and limit_in_request > limit:
                limit_in_request = limit
            if limit and (count-offset) / limit_in_request < 1:
                # При последнем запросе, нужно ограничить
                # кол-во запрашиваемых объектов до оставшегося кол-ва.
                limit_in_request = count-offset
            result = method.get(
                params={'limit': limit_in_request,
                        'offset': offset,
                        **params})
            data = result().data
            results.append(result)

            if not data.get('count'):
                # Есть нет count, значит в ответе только один объект.
                break
            elif limit and data.get('count') < limit:
                # Если объектов меньше, чем указанный limit,
                # то он уменьшается до count.
                count = data.get('count')
            elif limit:
                # Ограничение по указанному limit.
                count = limit
            else:
                # Получение всех объектов.
                count = data.get('count')
            offset = data['offset']+limit_in_request

        return self._to_format(self._request_objects.__name__,
                               results, as_dataframe=as_dataframe)

    def _get_objects_for_request_stats(self, object_type, limit):
        """
        Получение идентификаторов объектов,
        по которым будет запрошена статистика.
        """
        if object_type == self.CAMPAIGN_STATS:
            data = self.get_campaigns(
                limit=limit, as_dataframe=False, params={'fields': 'id'})
            ids = [i['id'] for i in data]

        elif object_type == self.BANNER_STATS:
            data = self.get_banners(
                limit=limit, as_dataframe=False, params={'fields': 'id'})
            ids = [i['id'] for i in data]

        elif object_type == self.USER_STATS:
            r = self.low_api.user2().get()
            data = r().data
            ids = [data['id']]
        else:
            raise ValueError('Не известный object_type, '
                             'разерешены только: {}, {}, {}'
                             .format(self.CAMPAIGN_STATS,
                                     self.BANNER_STATS,
                                     self.USER_STATS))
        return ids

    def get_stats(self, object_type=CAMPAIGN_STATS,
                  date_from=None, date_to=None, metrics=None,
                  ids=None, as_dataframe=None, limit=None,
                  limit_in_request=200, interval=92,
                  is_union_results=True):
        """
        https://target.my.com/adv/api-marketing/doc/stat-v2

        Если не указаны date_from и date_to, то вернется суммарная статистика.
        Если не указаны идентификаторы объектов в ids, то они все будут получены
        и вставлены в запрос статистики. Ограничить можно через limit.

        :param object_type: str : banners|campaigns|users :
            Если нету, то будет сделан запрос объектов и
            потом вставлены в запрос к статистике.
        :param date_from: none, str, datatime : YYYY-MM-DD[THH:MM[:SS]] :
            Начальная дата. Только для day.json.
            Если отсутствует, будет запрошена стат. за все время.
        :param date_to: none, str, datatime : YYYY-MM-DD[THH:MM[:SS]] :
            Конечная дата (включительно). Только для day.json.
            Если отсутствует, будет запрошена стат. за все время.
        :param ids: list : Список идентификаторов баннеров, кампаний или пользователей.
        :param metrics: str, list : Список наборов метрик.
        :param as_dataframe: bool : преобразовать в формат Pandas DataFrame.
        :param limit: int : Макс. кол-во случайных объектов,
            для которых запросить статистику. Например для теста.
        :param interval: int : кол-во дней в периоде в одном запросе, максимум 92
        :param is_union_results: bool : объединить результаты в один список
        :return dict, list :

        if as_dataframe True:
            DataFrame
        elif is_union_results True:
            [{"items": [...], "total": [...]},
             {"items": [...], "total": [...]}]
        elif is_union_results False:
            {"items": [...], "total": [...]}

        =====

        data: {
            "items": [{
                "id": 857683,
                "rows": [{
                    "date": "2017-09-20",
                    "base": {
                        "shows": 123757,
                        "clicks": 672,
                        "goals": 9,
                        "spent": "155.8",
                        "cpm": "1.25",
                        ...
                    },
                    "events": {
                        "opening_app": 0,
                        "opening_post": 0,
                        "moving_into_group": 0,
                        "clicks_on_external_url": 0,
                        ...
                    },
                    "uniques": {...},
                    "video": {...},
                    "viral": {...},
                    "tps": {...}
                },
                {
                    "date": "2017-09-21",
                    "base": {...},
                    "events": {...},
                    "uniques": {...},
                    "video": {...},
                    "viral": {...},
                    "tps": {...}
                }],
                "total": {
                    "base": {...},
                    "events": {...},
                    "uniques": {...},
                    "video": {...},
                    "viral": {...},
                    "tps": {...}
                }
            }],
            "total": {
                "base": {...},
                "events": {...},
                "video": {...},
                "viral": {...},
                "tps": {...}
            }
        }
        """
        if limit_in_request > 200:
            raise ValueError('limit_in_request должен быть <= 200')
        if interval > 92:
            raise ValueError('delta_period должен быть <= 92')
        if interval < 1:
            raise ValueError('interval должен быть больше 0')

        if not ids:
            ids = self._get_objects_for_request_stats(
                object_type, limit=limit)

        get_params = {}
        if metrics:
            if isinstance(metrics, list):
                metrics = ','.join(map(str, metrics))
            get_params.update(metrics=metrics)

        if date_from or date_to:
            # Макс. период запроса 92 дня.
            # Если запрашиваемый интервал превышает,
            # то разделяется на несколько перидов.
            time_mode = self._DAY_STATS
            periods = self._period_range(
                date_from, date_to, delta=interval-1)
        else:
            time_mode = self._SUMMARY_STATS
            periods = [{}]

        # Создаются список списков из объектов, для запросов.
        # Макс. кол-во объектов для запроса 200 дня.
        ids_groups = self._grouper_list(ids, limit_in_request)

        results = []
        for ids in ids_groups:
            ids_str = ','.join(map(str, ids))

            for period in periods:
                if period:
                    get_params.update(date_from=period[0])
                    get_params.update(date_to=period[1])

                result = self.low_api.stats2(object_type=object_type,
                                             time_mode=time_mode, ids=ids_str) \
                    .get(params=get_params)

                results.append(result)

        return self._to_format(self.get_stats.__name__, results,
                               as_dataframe, is_union_results)

    def get_campaigns(self, params=None, as_dataframe=None,
                      limit=None, limit_in_request=50):
        """
        https://target.my.com/doc/apiv2/ru/resources/campaigns.html
        https://target.my.com/doc/apiv2/ru/objects/ads2.api_v2.campaigns.CampaignResource.html

        :param limit: int : количество объектов в ответе, если None будут получены все
        :param params: dict :
            Поля
                fields=age_restrictions,audit_pixels,autobidding_mode,banner_uniq_shows_limit,budget_limit,budget_limit_day,cr_max_price,created,date_end,date_start,delivery,enable_utm,id,issues,mixing,name,objective,package_id,price,priced_goal,pricelist_id,shows_limit,status,targetings,uniq_shows_limit,uniq_shows_period,updated,utm
            Фильтры
                _id=6617841
                _id__in=6617841,6711647
                _status=active
                _status__ne=active
                _status__in=active,blocked
                _last_updated__gt=2018-01-01 00:00:00
                _last_updated__gte=2018-01-01 00:00:00
                _last_updated__lt=2018-01-01 00:00:00
                _last_updated__lte=2018-01-01 00:00:00
            Сортировка
                sorting=id - по возрастанию
                sorting=-id - по убыванию
                sorting=name - по возрастанию
                sorting=-name - по убыванию
                sorting=status - по возрастанию
                sorting=-status - по убыванию
            по нескольким полям
                sorting=status,name,-id
        :param limit_in_request: int : кол-во объектов в одном запросе
        :param as_dataframe: bool : вернуть в формате dataframe
        :return: list, dataframe
        """
        return self._request_objects(method=self.low_api.campaigns2(),
                                     limit=limit, params=params,
                                     limit_in_request=limit_in_request,
                                     as_dataframe=as_dataframe)

    def get_banners(self, params=None, as_dataframe=None,
                    limit=None, limit_in_request=50):
        """
        https://target.my.com/doc/apiv2/ru/resources/banners.html
        https://target.my.com/doc/apiv2/ru/objects/ads2.api_v2.banners.BannerResource.html

        :param limit: int : количество объектов в ответе,
            по умолчанию будут получены все
        :param params: dict :
            Поля
                fields=call_to_action,campaign_id,content,created,deeplink,delivery,id,issues,moderation_reasons,moderation_status,products,status,textblocks,updated,urls,user_can_request_remoderation,video_params
            Фильтры
                _id=26617841
                _id__in=26617841,26711647
                _campaign_id=6617841
                _campaign_id__in=6617841,6711647
                _campaign_status=active
                _campaign_status__ne=active
                _campaign_status__in=active,blocked
                _status=active
                _status__ne=active
                _status__in=active,blocked
                _updated__gt=2018-01-01 00:00:00
                _updated__gte=2018-01-01 00:00:00
                _updated__lt=2018-01-01 00:00:00
                _updated__lte=2018-01-01 00:00:00
                _url=mail.ru
                _textblock=купить насос
        :param limit_in_request: int : кол-во объектов в одном запросе
        :param as_dataframe: bool : вернуть в формате dataframe
        :return: list, dataframe
        """
        return self._request_objects(method=self.low_api.banners2(),
                                     limit=limit, params=params,
                                     limit_in_request=limit_in_request,
                                     as_dataframe=as_dataframe)


class MytargetAuth:
    OAUTH_TOKEN_URL = 'api/v2/oauth2/token.json'
    DELETE_TOKEN_URL = 'api/v2/oauth2/token/delete.json'
    OAUTH_USER_URL = 'oauth2/authorize'
    GRANT_CLIENT = 'client_credentials'
    GRANT_AGENCY_CLIENT = 'agency_client_credentials'
    GRANT_RERFESH = 'refresh_token'
    GRANT_AUTH_CODE = 'authorization_code'
    OAUTH_ADS_SCOPES = ('read_ads', 'read_payments', 'create_ads')
    OAUTH_AGENCY_SCOPES = (
        'create_clients', 'read_clients', 'create_agency_payments'
    )
    OAUTH_MANAGER_SCOPES = (
        'read_manager_clients', 'edit_manager_clients', 'read_payments'
    )

    def __init__(self, is_sandbox=False):
        self.adapter = MytargetClientAdapter(access_token=None)
        self.is_sandbox = is_sandbox

    def _request_oauth(self, scheme, **kwargs):
        """
        https://target.my.com/adv/api-marketing/doc/authorization
        
        :return: str, json
        """
        url = self.adapter.get_url_root(kwargs)+scheme
        response = requests.post(url, data=kwargs)

        if response.status_code == 403:
            raise exceptions.MytargetTokenLimitError(response)
        elif response.status_code == 401:
            raise exceptions.MytargetTokenError(response)
        elif 200 <= response.status_code < 300:
            try:
                return response.json()
            except Exception:
                return response.text
        else:
            raise exceptions.MytargetApiError(response)

    def get_client_token(self, client_id, client_secret,
                         permanent='false', **kwargs):
        """
        https://target.my.com/adv/api-marketing/doc/authorization

        :param permanent: str : false|true : вечный токен
        :return: {
            "access_token": "...",
            "token_type": "Bearer",
            "expires_in": "None",
            "refresh_token": "...",
            "tokens_left": 0
        }
        """
        return self._request_oauth(
            scheme=self.OAUTH_TOKEN_URL, grant_type=self.GRANT_CLIENT,
            client_id=client_id, client_secret=client_secret,
            permanent=permanent, is_sandbox=self.is_sandbox, **kwargs)

    def get_agency_client_token(self, client_id, client_secret,
                                agency_client_name,
                                permanent='false', **kwargs):
        """
        https://target.my.com/adv/api-marketing/doc/authorization

        Эта схема протокола OAuth2 не является стандартной.
        Она была реализована для того, чтобы дать возможность агентствам
        и менеджерам создавать токены доступа для своих клиентов
        без подтверждения от клиента. Схема очень похожа на стандартную
        Client Credentials Grant за исключением того, что в запросе
        нужно передавать дополнительный параметр "agency_client_name"
        (username из запроса AgencyClients или ManagerClients)

        :param agency_client_name: username из запроса AgencyClients или ManagerClients
        :param permanent: str : false|true : вечный токен
        :return:
        """
        return self._request_oauth(
            scheme=self.OAUTH_TOKEN_URL,
            grant_type=self.GRANT_AGENCY_CLIENT,
            client_id=client_id, client_secret=client_secret,
            agency_client_name=agency_client_name,
            permanent=permanent, is_sandbox=self.is_sandbox,
            **kwargs)

    def oauth_url(self, client_id, scopes=OAUTH_ADS_SCOPES,
                  state=None):
        """
        https://target.my.com/adv/api-marketing/doc/authorization
        Формирует ссылку для перенаправления юзера на страницу авторизации

        :param scopes: разрешения
            В одном запросе могут быть указаны права разных групп.
            myTarget определяет тип аккаунта текущего пользователя и
            открывает только соответствующие права. Более того,
            если в запросе, к примеру, перечислены все права,
            и пользователь при этом является агентством, то ему будет
            предложено выбрать к какому аккаунту он хочет
            дать доступ - к агентсткому с агентскими правами,
            какому-либо из менеджерских с менеджерскими или к одному
            из клиентских с правами доступа к клиентским данным.

            Для обычного пользователя-рекламодателя:
            read_ads — чтение статистики и РК;
            read_payments — чтение денежных транзакций и баланса;
            create_ads — создание и редактирование настроек РК, баннеров,
                аудиторий (ставки, статус, таргетинги и т.п.).

            Для пользователей-агентств и пользователей-представительств:
            create_clients — создание новых клиентов;
            read_clients — просмотр клиентов и операции от их имени;
            create_agency_payments — переводы средств на счёта клиентов и обратно.

            Для пользователей-менеджеров:
            read_manager_clients — просмотр клиентов и операции от их имени;
            edit_manager_clients — изменение параметров клиентов;
            read_payments — чтение денежных транзакций и баланса;

        :param state: сгенерированный на стороне клиента токен,
            используется для предотвращения CSRF
        :return: {'state': state, 'url': url}
        """
        url_root = self.adapter.get_url_root({'is_sandbox': self.is_sandbox})
        if not state:
            state = 'none123'
        scopes = ','.join(map(str, scopes))
        url = '{}{}?response_type=code&client_id={}&state={}&scope={}' \
            .format(url_root, self.OAUTH_USER_URL, client_id, state, scopes)

        return {'state': state, 'url': url}

    def get_authorization_token(self, client_id, code, **kwargs):
        """
        https://target.my.com/adv/api-marketing/doc/authorization

        :param code: код, полученный после авторизации
        :return: {
            "access_token": "...",
            "token_type": "Bearer",
            "expires_in": "None",
            "refresh_token": "...",
            "tokens_left": 0
        }
        """
        return self._request_oauth(
            scheme=self.OAUTH_TOKEN_URL, grant_type=self.GRANT_AUTH_CODE,
            code=code, client_id=client_id, is_sandbox=self.is_sandbox,
            **kwargs)

    def refresh_token(self, client_id, client_secret,
                      refresh_token, **kwargs):
        """
        https://target.my.com/adv/api-marketing/doc/authorization
        Обновление токена доступа

        :return: {
          "access_token": "{new_access_token}",
          "token_type": "bearer",
          "scope": "{scope}",
          "expires_in": "86400",
          "refresh_token": "{refresh_token}"
        }
        """
        return self._request_oauth(
            scheme=self.OAUTH_TOKEN_URL, grant_type=self.GRANT_RERFESH,
            refresh_token=refresh_token, client_id=client_id,
            client_secret=client_secret, is_sandbox=self.is_sandbox,
            **kwargs)

    def delete_tokens(self, client_id, client_secret):
        """https://target.my.com/adv/api-marketing/doc/authorization"""
        return self._request_oauth(scheme=self.DELETE_TOKEN_URL,
                                   client_id=client_id,
                                   client_secret=client_secret,
                                   is_sandbox=self.is_sandbox)
