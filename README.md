# Python обертка для запросов к API Mytarget

## Установка
```
pip install git+https://github.com/pavelmaksimov/tapioca-mytarget.git
```

## Документация

### Mytarget - Низкоуровневая обертка

Написанна на базе [Tapioca](http://tapioca-wrapper.readthedocs.org/en/stable/quickstart.html). 

``` python
from tapioca_mytarget import Mytarget

api = Mytarget(access_token='{access-token}', 
               # Будет ожидать и повторять запросы, если закончится квота 
               retry_request_if_limit=True)
```

Генерация класса Mytarget происходит динамически, 
поэтому узнать о добавленных в схему методах, можно так.
``` python
print(dir(api))
```

Ресурсы API указываются в схеме в файле: tapioca_mytarget/resource_mapping.py.

```python
# tapioca_mytarget/resource_mapping.py

RESOURCE_MAPPING = {
    'user2': {
        'resource': 'v2/user.json',
        'docs': 'https://target.my.com/doc/apiv2/ru/resources/user.html'
    },
}
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

Значение указанное в методе, будет подставлено в ссылкую
```python
api.campaign2(campaign_id='12345').get()
```

Доступные GET параметры для ресурса указываются в params.
```python
api.campaign2(campaign_id='12345').get(params={'fields': 'id,name,status'})
```

Данные в POST запросе отправить можно так.
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

#### Формат возвращаемых данных.
Данные возвращаются в формате объекта Tapioca.

```python
result = api.user2().get()
print(result().status_code)
print(result().response)
print(result().response.headers)
print(result())
``` 
    
Преобразовать в JSON можно так:
```python
result().data
```

Преобразование в DataFrame:
```python
result().to_df()
```

Мне лень было добавлять все ресурсы API в схему. 
Вы можете сделать это сами и потом прислать мне схему ;)


### MytargetLight - Высокоуровневая обертка 

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
    # Будет ожидать и повторять запросы, если закончится квота
    retry_request_if_limit=True,
    # Будет возвращать данные в формате dataframe
    as_dataframe=True)
 ```   

#### Получение статистики

``` python
# По умолчанию будет возвращена суммарная статистика за все время.
data = light_api.get_stats()
 ```   

``` python
# Если указать date_from и date_to, 
# то будет запрошена стата по дням за указанный период.
# В формате строки или datetime.
data = light_api.get_stats(
    object_type=light_api.BANNER_STATS, 
    date_from=datetime(2019, 1, 1),
    date_to=datetime(2019, 1, 1))
 ```   

``` python
# По умолчанию будет получена стат. по всем кампаниям.
data = light_api.get_stats()
 ```   

``` python
# Статистика по всем баннерам.
data = light_api.get_stats(object_type=light_api.BANNER_STATS)
 ```   

``` python
# Статистика аккаунта.
data = light_api.get_stats(object_type=light_api.USER_STATS)
 ```   

``` python
# Можно ограничить для теста кол-во объектов 
# по которым будет запрошена статистика.
df = light_api.get_stats(limit=2)
 ```   

``` python
# Метод делает несколько запросов для поулчения данных.
# Регулировать сколько в одном запросе будет запрошено 
# объектов или за какой интервал можно так
df = light_api.get_stats(
    limit_in_request=10,  # в одном запросе получать не более 2 объектов
    interval=30,  # кол-во дней статистики в одном запросе)
 ```   

``` python
# Вернуть данные в формате dataframe
df = light_api.get_stats(as_dataframe=True)
 ```   

#### Получение объектов

``` python
# Получение всех кампаний
data = light_api.get_campaigns()

# Получение всех объявлений
data = light_api.get_banners()

# Выбрать возвращаемые поля
data = light_api.get_campaigns(params={'fields': 'id,name'}))

# Получить 5 случайных кампаний.
data = light_api.get_campaigns(limit=5)

# Получить в формате dataframe.
df = light_api.get_campaigns(as_dataframe=True)
 ```   

``` python
# Доступ к низкоуровневой обертке.
regions = light_api.low_api.regions2().get()
regions().data
```

### MytargetAuth - Операции с токенами

https://target.my.com/adv/api-marketing/doc/authorization

Для операций с токенами используйте методы в классе MytargetAuth.
Я не смог сделать эти операции через низкоуровневую обертку, 
т.к. отправляемый параметр grand_type, Mytarget не видел.
Поэтому пришлось сделать отдельным классом.

``` python
from tapioca_mytarget import MytargetAuth

CLIENT_ID = ''
CLIENT_SECRET = ''
REFRESH_TOKEN = ''

auth = Mytarget()

auth.get_client_token(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET, 
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

Удачи тебе, друг! Поставь звездочку ;)

## Другое
- Как работает обертка [Tapioca](http://tapioca-wrapper.readthedocs.org/en/stable/quickstart.html)
