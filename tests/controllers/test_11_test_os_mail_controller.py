#!/usr/bin/env python

"""py.test test cases to test OpenStudio.

These tests run based on webclient and need web2py server running.
"""
import datetime

from gluon.contrib.populate import populate

from populate_os_tables import populate_tax_rates
from populate_os_tables import populate_invoices
from populate_os_tables import populate_invoices_items
from populate_os_tables import populate_customers
from populate_os_tables import populate_customers_orders
from populate_os_tables import populate_customers_orders_items
from populate_os_tables import populate_workshops_messages
from populate_os_tables import populate_payment_methods


def test_osmail_render_footer(client, web2py):
    """
        Is the footer correctly included in rendered messages
    """
    # get a random url to init OpenStudio environment
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_customers(web2py)

    footer_content = 'FooterTest'
    row = web2py.db.sys_email_templates(Name='sys_email_footer')
    row.TemplateContent = footer_content
    row.update_record()

    web2py.db.commit()

    # render message and check
    url = '/test_os_mail/test_osmail_render_template?email_template=sys_reset_password'
    client.get(url)
    assert client.status == 200

    assert footer_content in client.text


def test_osmail_render_order_received(client, web2py):
    """
        Is the order received mail rendering correctly?
    """
    # get a random url to init OpenStudio environment
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_customers(web2py, 10)
    populate_customers_orders(web2py)
    populate_customers_orders_items(web2py)

    url = '/test_os_mail/test_osmail_render_template?email_template=order_received&customers_orders_id=1'
    client.get(url)
    assert client.status == 200

    oi = web2py.db.customers_orders_items(1)
    assert oi.ProductName in client.text
    assert oi.Description in client.text
    assert str(oi.TotalPriceVAT).encode('utf8') in client.text


def test_osmail_render_order_delivered(client, web2py):
    """
        Is the order delivered mail rendering correctly?
    """
    # get a random url to init OpenStudio environment
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_customers(web2py, 10)
    populate_customers_orders(web2py)
    populate_customers_orders_items(web2py)

    url = '/test_os_mail/test_osmail_render_template?email_template=order_delivered&customers_orders_id=1'
    client.get(url)
    assert client.status == 200

    oi = web2py.db.customers_orders_items(1)
    assert oi.ProductName in client.text
    assert oi.Description in client.text
    assert str(oi.TotalPriceVAT).encode('utf8') in client.text


def test_osmail_render_sys_notification_order_created(client, web2py):
    """
    Is the order created mail rendered correctly?
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_customers(web2py, 10)
    populate_customers_orders(web2py)
    populate_customers_orders_items(web2py)

    url = '/test_os_mail/test_osmail_render_sys_notification?sys_notification=order_created&customers_orders_id=1'
    client.get(url)
    assert client.status == 200

    # Check title
    assert "New order" in client.text

    # Check content
    oi = web2py.db.customers_orders_items(1)
    assert oi.ProductName in client.text
    assert oi.Description in client.text
    assert str(oi.TotalPriceVAT).encode('utf8') in client.text

    # Check comments / customer note
    order = web2py.db.customers_orders(1)
    assert order.CustomerNote in client.text




