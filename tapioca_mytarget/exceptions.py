# -*- coding: utf-8 -*-
import logging


class MytargetApiError(Exception):
    def __init__(self, response, *args, **kwargs):
        self.response = response

    def __str__(self):
        logging.info('HEADERS = '+str(self.response.headers))
        logging.info('URL = '+self.response.url)
        return f'{self.response.status_code} {self.response.reason} ' \
            f'{self.response.text}'


class MytargetTokenError(MytargetApiError):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        jdata = self.response.json()
        self.code = jdata.get('code', None) or jdata.get('error', '')
        self.message = jdata.get('message', None) or jdata.get('error_description', '')

    def __str__(self):
        return f'{self.response.status_code} {self.response.reason}, ' \
            f'{self.code}, {self.message}'


class MytargetTokenLimitError(MytargetApiError):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return f'{self.response.status_code} {self.response.reason} ' \
            f'Получено максимальное кол-во токенов\n {self.response.text}'


class MytargetLimitError(MytargetApiError):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return 'Исчерпан лимит запросов. Повторите запрос.'
