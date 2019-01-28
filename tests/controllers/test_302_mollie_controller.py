# -*- coding: utf-8 -*-

import datetime

from setup_profile_tests import setup_profile_tests

from populate_os_tables import populate_customers
from populate_os_tables import populate_invoices
from populate_os_tables import populate_invoices_items
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


def test_webhook_invoice_chargeback(client, web2py):
    """
        Is a payment added when an invoice is paid with chargeback(s)?
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_customers(web2py, 1)
    populate_invoices(web2py)
    populate_invoices_items(web2py)

    invoice = web2py.db.invoices(1)
    invoice.Status = 'paid'
    invoice.update_record()
    web2py.db.commit()

    amounts = web2py.db.invoices_amounts(1)
    price = unicode(amounts.TotalPriceVAT * -1)
    mollie_id = 'tr_test'
    chargeback_id = 'chb_test'
    date = '2014-01-01'

    url = '/mollie/test_webhook_invoice_chargeback?' + \
          'iID=1' +\
          '&chargeback_amount=' + price + \
          '&chargeback_date=' + date + \
          '&mollie_payment_id=' + mollie_id + \
          '&chargeback_id=' + chargeback_id + \
          'chargeback_details=Chargeback'

    client.get(url)
    assert client.status == 200

    payment = web2py.db.invoices_payments(1)
    assert payment.Amount == amounts.TotalPriceVAT * -1
    assert payment.mollie_payment_id == mollie_id
    assert unicode(payment.PaymentDate) == date
    assert chargeback_id in payment.Note
    assert 'Chargeback' in payment.Note

    # Check status changes back to 'sent'
    invoice = web2py.db.invoices(1)
    assert invoice.Status == 'sent'