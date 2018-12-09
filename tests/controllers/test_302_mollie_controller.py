# -*- coding: utf-8 -*-

import datetime

from setup_profile_tests import setup_profile_tests

from populate_os_tables import populate_school_memberships
from populate_os_tables import populate_school_subscriptions


mollie_key = 'test_kBdWS2sfs2k9HcSCfx7cQkCbc3f5VQ'

def test_subscription_buy_now(client, web2py):
    """
        Can a subscription be bought
    """
    setup_profile_tests(web2py)
    populate_school_subscriptions(web2py)

    web2py.db.sys_properties.insert(
        Property='mollie_website_profile',
        PropertyValue=mollie_key # Mollie test key
    )

    web2py.db.commit()

    url = '/mollie/subscription_buy_now?ssuID=1'
    client.get(url)
    assert client.status == 200

    cs = web2py.db.customers_subscriptions(1)
    assert cs.auth_customer_id == 300
    assert cs.Startdate == datetime.date.today()
    assert cs.school_subscriptions_id == 1


def test_subscription_buy_now_start_first_day_of_next_month(client, web2py):
    """
        Can a subscription be bought
    """
    import calendar

    setup_profile_tests(web2py)
    populate_school_subscriptions(web2py)

    web2py.db.sys_properties.insert(
        Property='mollie_website_profile',
        PropertyValue='test_kBdWS2sfs2k9HcSCfx7cQkCbc3f5VQ' # Mollie test key
    )

    web2py.db.sys_properties.insert(
        Property='shop_subscriptions_start',
        PropertyValue='next_month'
    )

    web2py.db.commit()

    url = '/mollie/subscription_buy_now?ssuID=1'
    client.get(url)
    assert client.status == 200

    today = datetime.date.today()
    first_next_month = datetime.date(today.year,
                                     today.month,
                                     calendar.monthrange(today.year,today.month)[1]) + datetime.timedelta(days=1)

    cs = web2py.db.customers_subscriptions(1)
    assert cs.auth_customer_id == 300
    assert cs.Startdate == first_next_month
    assert cs.school_subscriptions_id == 1


def test_membership_buy_now(client, web2py):
    """
    Is the membership buy now function working?
    """
    # Get random url to init env
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200


    setup_profile_tests(web2py)
    populate_school_memberships(web2py)

    web2py.db.sys_properties.insert(
        Property='mollie_website_profile',
        PropertyValue=mollie_key # Mollie test key
    )

    web2py.db.commit()

    url = '/mollie/membership_buy_now?smID=1'
    client.get(url)
    assert client.status == 200

    cm = web2py.db.customers_memberships(1)
    assert cm.auth_customer_id == 300
    assert cm.Startdate == datetime.date.today()
    assert cm.school_memberships_id == 1
    assert cm.DateID == datetime.date.today().strftime('%Y%m%d') + '00001'
    assert not cm.Barcode == None