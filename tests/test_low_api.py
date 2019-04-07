# coding: utf-8

from pandas import set_option

from tapioca_mytarget import Mytarget

set_option('display.max_columns', 100)
set_option('display.width', 1500)

CLIENT_ID = ''
CLIENT_SECRET = ''
ACCESS_TOKEN = ''
REFRESH_TOKEN = ''

api = Mytarget(access_token=ACCESS_TOKEN, retry_request_if_limit=True)


def test_user2():
    print(dir(api))
    r = api.user2().get()
    print(r())


def test_user2_to_df():
    r = api.user2().get()
    df = r().to_df()
    print(df.columns)
    print(df)


def test_campaigns2():
    r = api.campaigns2().get(params={'limit': 50})
    df = r().to_df()
    print(len(df))
    print(df)


def test_campaign2():
    r = api.campaign2(campaign_id='5815884').get(params={'fields': 'id,name,status'})
    df = r().to_df()
    print(len(df))
    print(df)


def test_banners2():
    r = api.banners2().get(params={'limit': 1, 'offset': 1})
    print(r().data)


def test_regions2():
    r = api.regions2().get()
    print(r().data)


def test_open_docs():
    api.regions2().open_docs()


def test_open_in_browser():
    api.regions2().open_in_browser()

