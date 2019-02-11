# -*- coding: utf-8 -*-

import datetime

from setup_profile_tests import setup_profile_tests

from populate_os_tables import populate_customers
from populate_os_tables import populate_customers_orders
from populate_os_tables import populate_customers_orders_items
from populate_os_tables import populate_invoices
from populate_os_tables import populate_invoices_items
from populate_os_tables import populate_school_memberships
from populate_os_tables import populate_school_subscriptions


mollie_key = 'test_kBdWS2sfs2k9HcSCfx7cQkCbc3f5VQ'

def test_invoice_paid(client, web2py):
    """
        Is a payment added when an invoice is paid?
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_customers(web2py, 1)
    populate_invoices(web2py)
    populate_invoices_items(web2py)

    amounts = web2py.db.invoices_amounts(1)
    price = unicode(amounts.TotalPriceVAT)
    mollie_id = 'tr_test'
    date = '2014-01-01'

    url = '/mollie/test_webhook_invoice_paid?iID=1&payment_amount=' + price + '&payment_date='+date+'&mollie_payment_id='+mollie_id
    client.get(url)
    assert client.status == 200

    payment = web2py.db.invoices_payments(1)

    print payment

    assert payment.Amount == amounts.TotalPriceVAT
    assert payment.mollie_payment_id == mollie_id
    assert unicode(payment.PaymentDate) == date


def test_order_paid_delivery_invoice(client, web2py):
    """
        Is the order delivered after it's paid and is an invoice created?
    """
    setup_profile_tests(web2py)

    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_customers(web2py, 1) # so we have 2 orders, one for admin, one for a customer
    populate_customers_orders(web2py)
    populate_customers_orders_items(web2py, classcards=True)
    populate_customers_orders_items(web2py, workshops_products=True)
    populate_customers_orders_items(web2py, classes=True)
    populate_customers_orders_items(web2py, donation=True)

    web2py.db.sys_properties.insert(
        Property='shop_donations_tax_rates_id',
        PropertyValue='1'
    )
    web2py.db.sys_properties.insert(
        Property='shop_donations_create_invoice',
        PropertyValue='on'
    )

    web2py.db.commit()

    scd = web2py.db.school_classcards(1)
    wsp = web2py.db.workshops_products(1)
    class_price = web2py.db.classes_price(1)
    donation_price = 100 # 100 for the donation is fixed in the population of the tables
    price = unicode(round(scd.Price + wsp.Price + class_price.Dropin + donation_price, 2))

    #print web2py.db().select(web2py.db.customers_orders.ALL)

    url = '/mollie/test_webhook_order_paid?coID=1&payment_amount=' + price + '&payment_date=2014-01-01&mollie_payment_id=tr_test'
    client.get(url)
    assert client.status == 200

    # check class card delivery
    assert web2py.db(web2py.db.customers_classcards).count() == 1

    # check workshop product delivery
    assert web2py.db(web2py.db.workshops_products_customers).count() == 1

    # check drop in class delivery
    query = (web2py.db.classes_attendance.auth_customer_id == 1) & \
            (web2py.db.classes_attendance.ClassDate == '2099-01-01') & \
            (web2py.db.classes_attendance.classes_id == 1)
    assert web2py.db(query).count() == 1

    ## check invoice
    # invoice creation
    invoice = web2py.db.invoices(1)
    assert invoice.Status == 'paid'

    # invoice items
    assert web2py.db(web2py.db.invoices_items).count() == 4
    ii_1 = web2py.db.invoices_items(1)
    assert scd.Name in ii_1.Description
    assert ii_1.Price == scd.Price
    assert ii_1.Quantity == 1

    ii_2 = web2py.db.invoices_items(2)
    assert wsp.Name in ii_2.Description
    assert ii_2.Price == wsp.Price
    assert ii_2.Quantity == 1

    ii_3 = web2py.db.invoices_items(3)
    assert ii_3.Description == 'Bananas'
    assert ii_3.Price == class_price.Dropin
    assert ii_3.Quantity == 1

    ii_4 = web2py.db.invoices_items(4)
    assert ii_4.Description == 'Bananas'
    assert ii_4.Price == donation_price
    assert ii_4.Quantity == 1
    assert not ii_4.tax_rates_id is None

    # invoice links
    assert web2py.db(web2py.db.invoices_items_customers_classcards).count() == 1
    assert web2py.db(web2py.db.invoices_items_workshops_products_customers).count() == 1

    # invoice amounts
    amounts = web2py.db.invoices_amounts(1)
    assert amounts.TotalPriceVAT == scd.Price + wsp.Price + class_price.Dropin + donation_price

    # invoice footer & terms
    ig_100 = web2py.db.invoices_groups(100)
    assert ig_100.Terms == invoice.Terms
    assert ig_100.Footer == invoice.Footer

    # Check order status
    order = web2py.db.customers_orders(1)
    assert order.Status == 'delivered'

    # Check if all other orders have been cancelled. There should only be one space, which is filled after delivery
    assert web2py.db(web2py.db.customers_orders.Status == 'cancelled').count() == 2


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
          '&chargeback_details=Chargeback'

    client.get(url)
    assert client.status == 200

    payment = web2py.db.invoices_payments(1)

    assert payment.Amount == amounts.TotalPriceVAT * -1
    assert payment.mollie_payment_id == mollie_id
    assert payment.mollie_chargeback_id == chargeback_id
    assert unicode(payment.PaymentDate) == date
    assert payment.Note == 'Chargeback'

    # Check status changes back to 'sent'
    invoice = web2py.db.invoices(1)
    assert invoice.Status == 'sent'


def test_webhook_invoice_refund(client, web2py):
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
    refund_id = 're_test'
    date = '2014-01-01'

    url = '/mollie/test_webhook_invoice_refund?' + \
          'iID=1' +\
          '&refund_amount=' + price + \
          '&refund_date=' + date + \
          '&mollie_payment_id=' + mollie_id + \
          '&refund_id=' + refund_id + \
          '&refund_details=refund'

    client.get(url)
    assert client.status == 200

    payment = web2py.db.invoices_payments(1)

    print payment

    assert payment.Amount == amounts.TotalPriceVAT * -1
    assert payment.mollie_payment_id == mollie_id
    assert payment.mollie_refund_id == refund_id
    assert unicode(payment.PaymentDate) == date
    assert payment.Note == 'refund'

    # Check status changes back to 'sent'
    invoice = web2py.db.invoices(1)
    assert invoice.Status == 'sent'