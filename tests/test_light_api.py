# coding: utf-8
from datetime import datetime

from pandas import set_option

from tapioca_mytarget import MytargetLight

set_option('display.max_columns', 100)
set_option('display.width', 1500)

CLIENT_ID = ''
CLIENT_SECRET = ''
ACCESS_TOKEN = ''
REFRESH_TOKEN = ''

light_api = MytargetLight(
    access_token=ACCESS_TOKEN, retry_request_if_limit=True,
    as_dataframe=False)


def test_camapign_stats():
    print(light_api.get_stats(object_type=light_api.CAMPAIGN_STATS))


def test_banner_stats():
    print(light_api.get_stats(object_type=light_api.BANNER_STATS))


def test_user_stats():
    print(light_api.get_stats(object_type=light_api.USER_STATS))


def test_camapign_summary_stats():
    print(light_api.get_stats(limit=5, as_dataframe=False))


def test_camapign_summary_stats_df():
    print(light_api.get_stats(limit=5, as_dataframe=True))


def test_banner_summary_stats():
    print(light_api.get_stats(limit=5, as_dataframe=False))


def test_banner_summary_stats_df():
    print(light_api.get_stats(limit=5, as_dataframe=True))


def test_period_datetime():
    print(light_api.get_stats(
        limit=5,
        date_from=datetime(2019, 1, 1),
        date_to=datetime(2019, 1, 1)))


def test_period_string_datetime():
    print(light_api.get_stats(
        limit=1,
        date_from='2019-01-01',
        date_to='2019-01-01'))


def test_count_ids():
    df = light_api.get_stats(
        limit=3,
        limit_in_request=2,
        interval=1,
        date_from='2019-01-01',
        date_to='2019-01-03',
        as_dataframe=True)
    assert len(df['id'].drop_duplicates()) == 3


def test_camapign_stats_of_id():
    print(light_api.get_stats(ids=['5815884']))


def test_campaigns_of_fields():
    print(light_api.get_campaigns(limit=5, params={
        'fields': 'age_restrictions,audit_pixels,autobidding_mode,banner_uniq_shows_limit,budget_limit,budget_limit_day,cr_max_price,created,date_end,date_start,delivery,enable_utm,id,issues,mixing,name,objective,package_id,price,priced_goal,pricelist_id,shows_limit,status,targetings,uniq_shows_limit,uniq_shows_period,updated,utm'}))


def test_banners_of_fields():
    print(light_api.get_banners(limit=5, params={
        'fields': 'call_to_action,campaign_id,content,created,deeplink,delivery,id,issues,moderation_reasons,moderation_status,products,status,textblocks,updated,urls,user_can_request_remoderation,video_params'}))


def test_campaigns_as_df():
    print(light_api.get_campaigns(limit=5, as_dataframe=True, params={
        'fields': 'age_restrictions,audit_pixels,autobidding_mode,banner_uniq_shows_limit,budget_limit,budget_limit_day,cr_max_price,created,date_end,date_start,delivery,enable_utm,id,issues,mixing,name,objective,package_id,price,priced_goal,pricelist_id,shows_limit,status,targetings,uniq_shows_limit,uniq_shows_period,updated,utm'}))


def test_banners_as_df():
    print(light_api.get_banners(limit=5, as_dataframe=True, params={
        'fields': 'call_to_action,campaign_id,content,created,deeplink,delivery,id,issues,moderation_reasons,moderation_status,products,status,textblocks,updated,urls,user_can_request_remoderation,video_params'}))
