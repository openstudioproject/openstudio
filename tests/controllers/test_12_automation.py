# -*- coding: utf-8 -*-

import datetime
from populate_os_tables import populate_customers_with_subscriptions

def test_customers_subscriptions_create_montly_invoices(client, web2py):
    """
        Can we create subscription invoices for a month?
    """
    # Get random url to initialize OpenStudio environment
    url = '/default/user/login'

    client.get(url)
    assert client.status == 200

    populate_customers_with_subscriptions(web2py, 10)

    url = '/test_automation/test_customers_subscriptions_create_invoices?month=1&year=2014&description=Subscription_Jan'
    client.get(url)
    assert client.status == 200


    # check the created invoices
    ig_100 = web2py.db.invoices_groups(100)
    invoice = web2py.db.invoices(1)
    assert invoice.Status == 'sent'
    assert invoice.InvoiceID == 'INV' + unicode(datetime.date.today().year) + '1'
    assert ig_100.Terms == invoice.Terms
    assert ig_100.Footer == invoice.Footer

    ics = web2py.db.invoices_customers_subscriptions(1)
    assert ics.invoices_id == 1
    assert ics.customers_subscriptions_id == 1

    # make sure the 2nd customer (1002) doesn't have an invoice, the subscription is paused
    assert web2py.db(web2py.db.invoices_customers.auth_customer_id==1002).count() == 0

    ## check created invoice items
    # alt. Price subscription item (first subscription gets a different price)
    altp = web2py.db.customers_subscriptions_alt_prices(1)
    item = web2py.db.invoices_items(1)
    assert altp.Amount == item.Price
    assert altp.Description == item.Description

    # regular item
    ssup = web2py.db.school_subscriptions_price(1)
    item = web2py.db.invoices_items(2)
    assert item.Price == ssup.Price
