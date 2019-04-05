# Tapioca Mytarget

## Установка
```
pip install tapioca-mytarget
```

## Документация

Для получения токена используйте методы в классе MytargetAuth
``` python
from tapioca_mytarget import MytargetAuth

api = Mytarget()
auth.get_client_token(client_id='{client_id}', 
                      client_secret='{client_secret}', 
                      permanent='false')
```

Низкоуровневый код, написанный на базе
[Tapioca](http://tapioca-wrapper.readthedocs.org/en/stable/quickstart.html). 
``` python
from tapioca_mytarget import Mytarget

api = Mytarget(access_token='{access-token}', 
               retry_request_if_limit=True)

# Показать добавленные методы API
print(dir(api))
```

Обертка для легкого использования. 
В API MyTarget есть ограничения для получения статистики под дням, 
не более чем за 92 дня и не более 200 объектов и др.
Так вот эта обертка закрывает эти ограничения, 
автоматически получая необходимые объекты и 
посылая нескололько запросов, укладываясь во все ограничения.

``` python
from tapioca_mytarget import MytargetLight

light_api = MytargetLight(access_token='{access-token}', 
                          retry_request_if_limit=True,
                          as_dataframe)

# Получить стат. по всем кампаниям за все время.
data = light_api.get_stats()
# или
data = light_api.get_stats(object_type=light_api.CAMPAIGN_STATS)

# Получить стат. по всем объявлениям за указанный период.
data = light_api.get_stats(
    object_type=light_api.BANNER_STATS, 
    date_from=datetime(2019, 1, 1),
    date_to=datetime(2019, 1, 1))

# Получить стат. по 2 случайнвм объявлениям в формате Pandas DataFrame.
df = light_api.get_stats(
    limit=2,
    object_type=light_api.BANNER_STATS,
    date_from='2019-01-01',
    date_to='2019-01-01',
    as_dataframe=True)

# Доступ к низкоуровнему апи.
user = light_api.low_api.user2().get()
print(user().data)                      
```

- Узнайте, как работает [Tapioca](http://tapioca-wrapper.readthedocs.org/en/stable/quickstart.html)
- Удачи!
