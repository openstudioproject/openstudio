#!/usr/bin/env python

'''py.test test cases to test OpenStudio.

These tests run based on webclient and need web2py server running.
'''

from gluon.contrib.populate import populate
from populate_os_tables import prepare_classes
from populate_os_tables import populate_customers
from populate_os_tables import populate_workshops_products_customers
from populate_os_tables import populate_school_classcards

#TODO: move these tests to stats tests and rename to reports
#
# def test_subscriptions_overview(client, web2py):
#     '''
#         Test the overview of subscriptions
#     '''
#     # get one url to initialize payment methods in db
#     url = '/default/user/login'
#     client.get(url)
#     assert client.status == 200
#
#
#     # now continue test
#     monthly_fee = 40123456
#     mst_name = '1 class a week'
#
#     populate_customers(web2py, 10)
#     web2py.db.school_subscriptions.insert(Name=mst_name,
#                                           MonthlyFee=monthly_fee,
#                                           NRofClasses=1,
#                                           Archived=False)
#     web2py.db.customers_subscriptions.insert(school_subscriptions_id=1,
#                                              Startdate='2014-01-01',
#                                              Enddate=None,
#                                              auth_customer_id=1002,
#                                              payment_methods_id=3)
#     web2py.db.customers_subscriptions.insert(school_subscriptions_id=1,
#                                              Startdate='2014-01-01',
#                                              Enddate=None,
#                                              auth_customer_id=1003,
#                                              payment_methods_id=3)
#     web2py.db.commit()
#     assert web2py.db(web2py.db.customers_subscriptions).count() == 2
#
#     url = '/subscriptions_overview'
#     client.get(url)
#     assert client.status == 200
#
#     data = dict(month=1,
#                 year=2014,
#                 _formname='form_select_data')
#     client.post(url, data=data)
#     assert client.status == 200
#
#     assert mst_name in client.text
#     assert unicode(monthly_fee*2) in client.text.decode('utf-8') # check whether total works
#
#
# def test_workshop_payments(client, web2py):
#     '''
#         Check overview of paid workshop products for a selected month
#     '''
#     populate_workshops_products_customers(web2py)
#     # Fetch random url to populate payment_methods table
#     url = '/default/workshop_payments?year=2014&month=1'
#     client.get(url)
#     assert client.status == 200
#
#     fwsp_price = web2py.db.workshops_products(1).Price
#     web2py.db.customers_payments.insert(auth_customer_id      = 1002,
#                                         workshops_products_id = 1,
#                                         Amount                = fwsp_price,
#                                         PaymentDate           = '2014-01-01',
#                                         payment_methods_id   = 1 )
#     web2py.db.commit()
#
#     client.get(url)
#     assert client.status == 200
#
#     customer = web2py.db.auth_user(1002)
#     assert customer.first_name.split(' ')[0] in client.text
#
#
# def test_workshop_payments_open(client, web2py):
#     '''
#         Check if unpaid products are listed
#     '''
#     populate_workshops_products_customers(web2py)
#
#     url = '/default/workshop_payments_open'
#     client.get(url)
#     assert client.status == 200
#
#     customer = web2py.db.auth_user(1002)
#     assert customer.first_name.split(' ')[0] in client.text
#     customer = web2py.db.auth_user(1001)
#     assert customer.first_name.split(' ')[0] in client.text
#
#
# def test_trialclasses(client, web2py):
#     '''
#         Are trialclasses listed properly?
#     '''
#     prepare_classes(web2py)
#
#     url = '/default/trialclasses?year=2014&month=1'
#     client.get(url)
#     assert client.status == 200
#
#     customer_name = web2py.db.auth_user(1001).first_name.split(' ')[0]
#     assert customer_name in client.text
#
#
# def test_classcards(client, web2py):
#     '''
#         Are sold classcards listed for a given month?
#     '''
#     nr_of_cards = 1
#     populate_school_classcards(web2py, nr_of_cards, trialcard=True)
#     populate_customers(web2py, 1)
#
#     trial_card_id = nr_of_cards + 1
#
#     web2py.db.customers_classcards.insert(
#         auth_customer_id     = 1001,
#         school_classcards_id = trial_card_id,
#         Startdate            = '2014-01-01')
#
#     web2py.db.commit()
#
#     url = '/default/trialcards?year=2014&month=1'
#     client.get(url)
#     assert client.status == 200
#
#     customer_name = web2py.db.auth_user(1001).first_name.split(' ')[0]
#     assert customer_name in client.text
