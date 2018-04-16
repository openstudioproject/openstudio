# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
    py.test test cases to test OpenStudio.
    These tests run based on webclient and need web2py server running.
"""

from gluon.contrib.populate import populate

from populate_os_tables import populate_customers
from populate_os_tables import populate_sys_organizations
from populate_os_tables import populate_postcode_groups
from populate_os_tables import populate_settings_shop_links
from populate_os_tables import populate_settings_shop_customers_profile_announcements


def test_mailchimp(client, web2py):
    """
        Can we set the mailchimp api key
    """
    url = '/settings_integration/mailchimp'
    client.get(url)
    assert client.status == 200

    data = {
        'mailchimp_api_key': '123456_test'
    }
    client.post(url, data=data)
    assert client.status == 200

    row = web2py.db.sys_properties(Property='mailchimp_api_key')
    assert row.PropertyValue == data['mailchimp_api_key']


def test_mollie(client, web2py):
    """
        Can we set mollie settings
    """
    url = '/settings_integration/mollie'
    client.get(url)
    assert client.status == 200

    data = {
        'online_payment_provider': 'mollie',
        'mollie_website_profile': '123456_test'
    }
    client.post(url, data=data)
    assert client.status == 200

    row = web2py.db.sys_properties(Property='online_payment_provider')
    assert row.PropertyValue == data['online_payment_provider']
    row = web2py.db.sys_properties(Property='mollie_website_profile')
    assert row.PropertyValue == data['mollie_website_profile']
