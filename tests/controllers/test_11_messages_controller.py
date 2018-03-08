#!/usr/bin/env python

'''py.test test cases to test OpenStudio.

These tests run based on webclient and need web2py server running.
'''
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


# def test_message_display(client, web2py):
#     '''
#         Check whether a message shows correctly
#     '''
#     populate_workshops_messages(web2py)
#     message = web2py.db.messages(1)
#
#     # set session.workshops_msgID by visiting workshop messages page
#     url = '/workshops/messages?wsID=1'
#     client.get(url)
#     assert client.status == 200
#
#     url = '/messages/message?category=workshops&wsID=1&msgID=1'
#     client.get(url)
#     assert client.status == 200
#
#     assert message.msg_subject.split(' ')[0] in client.text
#     assert message.msg_content in client.text
#
#
# def test_get_workshops_customers_reached_and_resend(client, web2py):
#     '''
#         Check if we get a list of customers for a mail
#         and a resend link for failed sending.
#     '''
#     populate_workshops_messages(web2py)
#
#     web2py.db.customers_messages.insert(messages_id      = 1,
#                                         auth_customer_id = 1001,
#                                         Status           = 'fail')
#     web2py.db.customers_messages.insert(messages_id      = 1,
#                                         auth_customer_id = 1002,
#                                         Status           = 'fail')
#     web2py.db.commit()
#
#     url = '/messages/message_get_workshops_customers_reached?msgID=1'
#     client.get(url)
#     assert client.status == 200
#
#     customer_1 = web2py.db.auth_user(1001)
#     assert customer_1.first_name in client.text
#     assert "Sending failed" in client.text
#
#     # Test resend
#     url_resend = '/messages/message_send_to_customer?msgID=1&cuID=1001'
#     client.get(url_resend)
#     assert client.status == 200
#
#     # for now check redirect (will change at some time in the future)
#     assert "Sending failed" in client.text
#     # there should be 3 customers_messages in db now, 2 initial, 1 from resend
#     assert web2py.db(web2py.db.customers_messages).count() == 3


def test_osmail_render_footer(client, web2py):
    '''
        Is the footer correctly included in rendered messages
    '''
    # get a random url to init OpenStudio environment
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_customers(web2py)

    footer_content = 'FooterTest'
    web2py.db(web2py.db.sys_properties.Property == 'email_template_sys_footer').update(PropertyValue=footer_content)
    web2py.db.commit()

    # render message and check
    url = '/messages/test_osmail_render_template?email_template=email_template_sys_reset_password'
    client.get(url)
    assert client.status == 200

    assert footer_content in client.text


# def test_osmail_render_invoice_created(client, web2py):
#     '''
#         Is the invoice created mail rendering correctly?
#     '''
#     # get a random url to init OpenStudio environment
#     url = '/default/user/login'
#     client.get(url)
#     assert client.status == 200
#
#     populate_customers(web2py, 10)
#     populate_invoices(web2py)
#     populate_invoices_items(web2py)
#
#     url = '/messages/test_osmail_render_template?email_template=email_template_invoice_created&invoices_id=1'
#     client.get(url)
#     assert client.status == 200
#
#     ii = web2py.db.invoices_items(1)
#     assert ii.ProductName in client.text
#     assert ii.Description in client.text
#     assert unicode(ii.TotalPriceVAT).encode('utf8') in client.text


def test_osmail_render_order_received(client, web2py):
    '''
        Is the order received mail rendering correctly?
    '''
    # get a random url to init OpenStudio environment
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_customers(web2py, 10)
    populate_customers_orders(web2py)
    populate_customers_orders_items(web2py)

    url = '/messages/test_osmail_render_template?email_template=email_template_order_received&customers_orders_id=1'
    client.get(url)
    assert client.status == 200

    oi = web2py.db.customers_orders_items(1)
    assert oi.ProductName in client.text
    assert oi.Description in client.text
    assert unicode(oi.TotalPriceVAT).encode('utf8') in client.text


def test_osmail_render_order_delivered(client, web2py):
    '''
        Is the order delivered mail rendering correctly?
    '''
    # get a random url to init OpenStudio environment
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_customers(web2py, 10)
    populate_customers_orders(web2py)
    populate_customers_orders_items(web2py)

    url = '/messages/test_osmail_render_template?email_template=email_template_order_delivered&customers_orders_id=1'
    client.get(url)
    assert client.status == 200

    oi = web2py.db.customers_orders_items(1)
    assert oi.ProductName in client.text
    assert oi.Description in client.text
    assert unicode(oi.TotalPriceVAT).encode('utf8') in client.text


# def test_osmail_render_payment_received(client, web2py):
#     '''
#         Is the payment received mail rendering correctly?
#     '''
#     # get a random url to init OpenStudio environment
#     url = '/default/user/login'
#     client.get(url)
#     assert client.status == 200
#
#     populate_customers(web2py, 10)
#     populate_invoices(web2py)
#     populate_invoices_items(web2py)
#
#     amounts = web2py.db.invoices_amounts(1)
#     web2py.db.invoices_payments.insert(
#         invoices_id = 1,
#         Amount = amounts.TotalPriceVAT,
#         PaymentDate = datetime.date.today(),
#         payment_methods_id = 100,
#     )
#
#     web2py.db.commit()
#
#     url = '/messages/test_osmail_render_template?email_template=email_template_payment_received&invoices_payments_id=1'
#     client.get(url)
#     assert client.status == 200
#
#     ip = web2py.db.invoices_payments(1)
#
#     assert unicode(ip.PaymentDate).encode('utf8') in client.text
#     assert unicode(ip.Amount).encode('utf8') in client.text
