# coding: utf-8

from tapioca_mytarget import MytargetAuth

CLIENT_ID = ''
CLIENT_SECRET = ''
ACCESS_TOKEN = ''
REFRESH_TOKEN = ''

auth = MytargetAuth()


def test_refresh_token():
    print(auth.refresh_token(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, refresh_token=REFRESH_TOKEN))


def test_get_client_token():
    print(auth.get_client_token(
        client_id=CLIENT_ID, client_secret=CLIENT_SECRET, permanent='false'))


def test_delete_token():
    print(auth.delete_tokens(client_id=CLIENT_ID, client_secret=CLIENT_SECRET))


def test_get_agency_client_token():
    print(auth.get_agency_client_token(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, agency_client_name=''))
