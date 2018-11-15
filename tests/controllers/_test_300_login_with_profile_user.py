#!/usr/bin/env python

"""
    py.test test cases to test the Profile controller (profile.py)
"""

from gluon.contrib.populate import populate

from populate_os_tables import populate_payment_methods
from populate_os_tables import populate_invoices
from populate_os_tables import populate_customers_orders
from populate_os_tables import populate_customers_orders_items
from populate_os_tables import populate_classes
from populate_os_tables import prepare_classes
from populate_os_tables import populate_customers_with_classcards
from populate_os_tables import populate_customers_with_subscriptions
from populate_os_tables import populate_customers_with_memberships
from populate_os_tables import populate_workshops_products_customers
from populate_os_tables import populate_settings_shop_customers_profile_announcements
from setup_profile_tests import setup_profile_tests

import datetime


def test_logout_for_profile(client, web2py):
    """
        This is not an actual test, but just logs out the user
    """
    url = '/default/user/logout'
    client.get(url)
    assert client.status == 200


def test_login_profile_user(client, web2py):
    """
        Logs in with a user without any permissions by default
    """
    setup_profile_tests(web2py)

    data = dict(email='profile@openstudioproject.com',
                password='Password@1',
                _formname='login')
    client.post('/default/user/login', data=data)
    assert client.status == 200
    assert '<li class="header">Account</li>' in client.text

