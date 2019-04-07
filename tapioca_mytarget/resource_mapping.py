# coding: utf-8

RESOURCE_MAPPING = {

    # USER

    'user2': {
        'resource': 'v2/user.json',
        'docs': 'https://target.my.com/doc/apiv2/ru/resources/user.html'
    },
    'agency_client2': {
        'resource': 'v2/agency/clients/{client_id}.json',
        'docs': 'https://target.my.com/doc/apiv2/ru/resources/agency.clients.client_id.html'
    },
    'agency_clients2': {
        'resource': 'v2/agency/clients.json',
        'docs': 'https://target.my.com/doc/apiv2/ru/resources/agency.clients.html'
    },
    'agency_clients_count2': {
        'resource': 'v2/agency/clients/count.json',
        'docs': 'https://target.my.com/doc/apiv2/ru/resources/agency.clients.count.html'
    },
    'agency_manager2': {
        'resource': 'v2/agency/managers/{manager_id}.json',
        'docs': 'https://target.my.com/doc/apiv2/ru/resources/agency.managers.manager_id.html'
    },
    'agency_managers2': {
        'resource': 'v2/agency/managers.json',
        'docs': 'https://target.my.com/doc/apiv2/ru/resources/agency.managers.html'
    },
    'agency_manager_client2': {
        'resource': 'v2/agency/managers/{manager_id}/clients/{client_id}.json',
        'docs': 'https://target.my.com/doc/apiv2/ru/resources/agency.managers.manager_id.clients.client_id.html'
    },
    'agency_manager_client_mass_action2': {
        'resource': 'v2/agency/managers/{manager_id}/clients/mass_action.json',
        'docs': 'https://target.my.com/doc/apiv2/ru/resources/agency.managers.manager_id.clients.mass_action.html'
    },
    'branch_client2': {
        'resource': 'v2/branch/clients/{client_id}.json',
        'docs': 'https://target.my.com/doc/apiv2/ru/resources/branch.clients.client_id.html'
    },
    'branch_clients2': {
        'resource': 'v2/branch/clients.json',
        'docs': 'https://target.my.com/doc/apiv2/ru/resources/branch.clients.html'
    },
    'branch_clients_count2': {
        'resource': 'v2/branch/clients/count.json',
        'docs': 'https://target.my.com/doc/apiv2/ru/resources/branch.clients.count.html'
    },
    'manager_clients3': {
        'resource': 'v3/manager/clients.json',
        'docs': 'https://target.my.com/doc/apiv2/ru/resources/v3.manager.clients.html'
    },
    'manager_clients_count2': {
        'resource': 'v2/manager/clients/count.json',
        'docs': 'https://target.my.com/doc/apiv2/ru/resources/manager.clients.count.html'
    },
    'reserved_amounts2': {
        'resource': 'v2/reserved_amounts/{client_ids}.json',
        'docs': 'https://target.my.com/doc/apiv2/ru/resources/reserved_amounts.user_ids.html'
    },

    # STATS

    'stats2': {
        'resource': 'v2/statistics/{object_type}/{time_mode}.json?id={ids}',
        'docs': 'https://target.my.com/adv/low_api-marketing/doc/stat-v2'
    },

    # OBJECTS

    'campaigns2': {
        'resource': 'v2/campaigns.json',
        'docs': 'https://target.my.com/doc/apiv2/ru/resources/campaigns.html'
    },
    'campaign2': {
        'resource': 'v2/campaigns/{campaign_id}.json',
        'docs': 'https://target.my.com/doc/apiv2/ru/resources/campaigns.campaign_id.html'
    },
    'campaign_banners2': {
        'resource': 'v2/campaigns/{campaign_id}/banners.json',
        'docs': 'https://target.my.com/doc/apiv2/ru/resources/campaigns.campaign_id.banners.html'
    },
    'campaigns_mass_action2': {
        'resource': 'v2/campaigns/mass_action.json',
        'docs': 'https://target.my.com/doc/apiv2/ru/resources/campaigns.mass_action.html'
    },
    'campaign_black_list2': {
        'resource': 'v2/place_black_lists/{blacklist_id}.json',
        'docs': 'https://target.my.com/doc/apiv2/ru/resources/place_black_lists.blacklist_id.html'
    },
    'campaign_black_lists2': {
        'resource': 'v2/place_black_lists.json',
        'docs': 'https://target.my.com/doc/apiv2/ru/resources/place_black_lists.html'
    },
    'banners2': {
        'resource': 'v2/banners.json',
        'docs': 'https://target.my.com/doc/apiv2/ru/resources/banners.html'
    },
    'banner2': {
        'resource': 'v2/banners/{banner_id}.json',
        'docs': 'https://target.my.com/doc/apiv2/ru/resources/banners.banner_id.html'
    },
    'banners_mass_action2': {
        'resource': 'v2/banners/mass_action.json',
        'docs': 'https://target.my.com/doc/apiv2/ru/resources/banners.mass_action.html'
    },
    'banners_mass_replace1': {
        'resource': 'v1/banners/mass_replace.json',
        'docs': 'https://target.my.com/doc/apiv2/ru/resources/v1.banners.mass_replace.html'
    },

    # RESOURCES

    'regions2': {
        'resource': 'v2/regions.json',
        'docs': 'https://target.my.com/doc/apiv2/ru/resources/regions.html'
    },
}
