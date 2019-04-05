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
    print(light_api.get_stats(
        limit=1, object_type=light_api.CAMPAIGN_STATS,
        date_from=datetime(2019, 1, 1),
        date_to=datetime(2019, 1, 1)))


def test_camapign_stats_():
    print(light_api.get_stats(
        limit=1, object_type=light_api.CAMPAIGN_STATS,
        date_from='2018-06-01',
        date_to='2019-01-01',))


def test_banner_stats():
    print(light_api.get_stats(object_type=light_api.BANNER_STATS,
                              limit=10, limit_in_request=1,
                              as_dataframe=True))


def test_user_stats():
    print(light_api.get_stats(object_type=light_api.USER_STATS, metrics=''))


def test_campaigns():
    print(light_api.get_campaigns(limit=5, limit_in_request=2, params={
        'fields': 'age_restrictions,audit_pixels,autobidding_mode,banner_uniq_shows_limit,budget_limit,budget_limit_day,cr_max_price,created,date_end,date_start,delivery,enable_utm,id,issues,mixing,name,objective,package_id,price,priced_goal,pricelist_id,shows_limit,status,targetings,uniq_shows_limit,uniq_shows_period,updated,utm'}))


def test_banners():
    print(light_api.get_banners(limit=5, params={
        'fields': 'call_to_action,campaign_id,content,created,deeplink,delivery,id,issues,moderation_reasons,moderation_status,products,status,textblocks,updated,urls,user_can_request_remoderation,video_params'}))


def test_campaigns_as_df():
    print(light_api.get_campaigns(limit=5, as_dataframe=True,
                                  limit_in_request=2, params={
            'fields': 'age_restrictions,audit_pixels,autobidding_mode,banner_uniq_shows_limit,budget_limit,budget_limit_day,cr_max_price,created,date_end,date_start,delivery,enable_utm,id,issues,mixing,name,objective,package_id,price,priced_goal,pricelist_id,shows_limit,status,targetings,uniq_shows_limit,uniq_shows_period,updated,utm'}))


def test_banners_as_df():
    print(light_api.get_banners(limit=5, as_dataframe=True, params={
        'fields': 'call_to_action,campaign_id,content,created,deeplink,delivery,id,issues,moderation_reasons,moderation_status,products,status,textblocks,updated,urls,user_can_request_remoderation,video_params'}))
