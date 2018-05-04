#!/usr/bin/env python

'''
    py.test test cases to test OpenStudio.
    These tests run based on webclient and need web2py server running.
'''

import datetime

from gluon.contrib.populate import populate

from populate_os_tables import populate_customers_orders
from populate_os_tables import populate_customers_orders_items
from setup_profile_tests import setup_profile_tests


def test_edit(client, web2py):
    '''
        Can we update the order status?
    '''
    url = '/user/login'
    client.get(url)
    assert client.status == 200

    setup_profile_tests(web2py)
    populate_customers_orders(web2py)
    populate_customers_orders_items(web2py)

    url = '/orders/edit?coID=2'
    client.get(url)
    assert client.status == 200

    data = {'Status':'cancelled',
            'id': 2}

    client.post(url, data=data)
    assert client.status == 200

    order = web2py.db.customers_orders(2)
    assert order.Status == 'cancelled'


def test_deliver(client, web2py):
    '''
        Are orders delivered and unpaid invoices created correctly?
    '''
    url = '/user/login'
    client.get(url)
    assert client.status == 200

    setup_profile_tests(web2py)
    populate_customers_orders(web2py)
    populate_customers_orders_items(web2py)

    url = '/orders/deliver?coID=2'
    client.get(url)
    assert client.status == 200

    assert 'Delivered order' in client.text

    ##
    # Check whether order status was changed
    ##
    order = web2py.db.customers_orders(2)
    assert order.Status == 'delivered'

    ##
    # Check whether an invoice was created
    ##
    assert web2py.db(web2py.db.invoices).count() == 1

    print web2py.db().select(web2py.db.customers_orders.ALL)
    print web2py.db().select(web2py.db.customers_orders_items.ALL)
    print web2py.db().select(web2py.db.invoices.ALL)
    print web2py.db().select(web2py.db.invoices_items.ALL)