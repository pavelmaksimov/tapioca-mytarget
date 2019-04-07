# Tapioca Mytarget

## Установка
```
pip install tapioca-mytarget
```

## Документация

#### MytargetAuth - Операции с токенами

https://target.my.com/adv/api-marketing/doc/authorization

Для операций с токенами используйте методы в классе MytargetAuth.
Я не смог сделать эти операции через низкоуровневую обертку, 
поэтому пришлось сделать отдельным классом.

``` python
from tapioca_mytarget import MytargetAuth

auth = Mytarget()

auth.get_client_token(
    client_id='{client_id}',
    client_secret='{client_secret}', 
    permanent='false')

auth.refresh_token(
    client_id=CLIENT_ID, 
    client_secret=CLIENT_SECRET,
    refresh_token=REFRESH_TOKEN)

auth.get_agency_client_token(
    client_id=CLIENT_ID, 
    client_secret=CLIENT_SECRET, 
    agency_client_name='{agency_client_name}'))

auth.oauth_url(
    client_id=CLIENT_ID, 
    scopes=auth.OAUTH_ADS_SCOPES) 

auth.get_authorization_token(
    code='{code}', 
    client_id=CLIENT_ID)

auth.delete_tokens(
    client_id=CLIENT_ID, 
    client_secret=CLIENT_SECRET)

```

## Mytarget - Низкоуровневая обертка

Написанна на базе [Tapioca](http://tapioca-wrapper.readthedocs.org/en/stable/quickstart.html). 

``` python
from tapioca_mytarget import Mytarget

api = Mytarget(access_token='{access-token}', 
               retry_request_if_limit=True)
```

Ресурсы API указываются в схеме tapioca_mytarget/resource_mapping.py.

```python
# tapioca_mytarget/resource_mapping.py

RESOURCE_MAPPING = {
    'user2': {
        'resource': 'v2/user.json',
        'docs': 'https://target.my.com/doc/apiv2/ru/resources/user.html'
    },
}
```

Т.к. генерация класса происходит динамически, 
то узнать о добавленных в схему методах, можно только так.
``` python
print(dir(api))
```

Указав ресурс под ключом user2, появляется соответствующий метод.
```python
api.user2()
```

Доступны разные типы запросов.
```python
api.user2().get()
api.user2().post()
api.user2().put()
api.user2().patch()
api.user2().delete()
api.user2().options()
```

Пример, если ресурс требует указание данных.
```python
# tapioca_mytarget/resource_mapping.py

RESOURCE_MAPPING = {
    'campaign2': {
        'resource': 'v2/campaigns/{campaign_id}.json',
        'docs': 'https://target.my.com/doc/apiv2/ru/resources/campaigns.campaign_id.html'
    },
}
```

Доступные GET параметры для метода указываются в params.
```python
api.campaign2(campaign_id='12345').get(params={'fields': 'id,name,status'})
```

Данные в POST запросе.
```python
api.campaign2(campaign_id='12345').post(data={'...': '...'})
```

Открываем в браузере документацию метода.
```python
api.user2().open_docs()
```

Посылаем запрос в браузере.
```python
api.user2().open_in_browser()
```

##### Формат возвращаемых данных.
Данные возвращаются в формате объекта Tapioca.
Преобразовать в JSON можно так:
```python
result = api.user2().get()
result().data
```

Преобразование в DataFrame:
```python
result = api.user2().get()
result().to_df()
```

Мне лень было добавлять все ресурсы API в схему. 
Вы можете сделать это сами и потом прислать мне схему ;)


## MytargetLight - Высокоуровневая обертка 

В API MyTarget есть ограничения для получения статистики под дням, 
не более чем за 92 дня и не более 200 объектов в одном запросе.

Для методов объектов в одном запросе можно запросить не более 50 объектов

Так вот, эта обертка закрывает эти ограничения, 
автоматически получая необходимые объекты, 
посылая нескололько запросов, укладываясь во все ограничения.

``` python
from tapioca_mytarget import MytargetLight

light_api = MytargetLight(
    access_token='{access-token}', 
    # будет ожидать и повторять запросы, если закончится квота
    retry_request_if_limit=True,
    # Будет возвращать данные в формате dataframe
    as_dataframe=True)

# По умолчанию будет получена стат. по всем кампаниям.
# Если не указать даты периода получения, 
# будет возвращена суммарная статистика за все время.
data = light_api.get_stats()

# Если указать date_from и date_to, 
# то будет запрошена стата по дням за указанный период.
# В формате строки или datetime.
data = light_api.get_stats(
    object_type=light_api.BANNER_STATS, 
    date_from=datetime(2019, 1, 1),
    date_to=datetime(2019, 1, 1))

# Можно ограничить для теста кол-во объектов 
# по которым будет запрошена статистика.
df = light_api.get_stats(
    limit=2,
    object_type=light_api.BANNER_STATS,
    date_from='2019-01-01',
    date_to='2019-01-01')

# Изменить ограничения в одном запросе по умолчанию.
df = light_api.get_stats(
    limit=3,  # запросить 3 кампании
    limit_in_request=2,  # в одном запросе получать не более 2 объектов
    interval=1,  # кол-во дней статистики в одном запросе
    date_from='2019-01-01',
    date_to='2019-01-03',
    as_dataframe=True)
 ```   

``` python
# Доступ к низкоуровневой обертке.
user = light_api.low_api.user2().get()
user().data
```

## Зависимости
- requests 
- pandas
- [tapioca_wrapper](https://github.com/pavelmaksimov/tapioca-wrapper.git#egg=tapioca-wrapper-2019.4.5) 

## Автор
Павел Максимов

Связаться со мной можно в 
[Телеграм](https://t.me/pavel_maksimow) 
и в 
[Facebook](https://www.facebook.com/pavel.maksimow)

Удачи тебе, друг!

## Другое
- Как работает обертка [Tapioca](http://tapioca-wrapper.readthedocs.org/en/stable/quickstart.html)
