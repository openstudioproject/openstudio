#!/usr/bin/env python

"""
    py.test test cases to test OpenStudio.
    These tests run based on webclient and need web2py server running.
"""

from gluon.contrib.populate import populate

from populate_os_tables import prepare_classes
from populate_os_tables import populate_customers
from populate_os_tables import populate_invoices
from populate_os_tables import populate_invoices_items

from populate_os_tables import populate_auth_user_teachers_fixed_rate_default
from populate_os_tables import populate_auth_user_teachers_fixed_rate_class_1
from populate_os_tables import populate_auth_user_teachers_fixed_rate_travel

from populate_os_tables import populate_workshops_messages
from populate_os_tables import populate_customers_with_subscriptions


import datetime


def test_teacher_payments(client, web2py):
    """
         Are teacher payment invoices listed correctly?
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_customers(web2py)
    populate_invoices(web2py, teacher_fixed_price_invoices=True)

    url = '/finance/teacher_payments'
    client.get(url)
    assert client.status == 200

    assert 'INV1001' in client.text


def test_teacher_payments_generate_invoices_choose_month(client, web2py):
    """
        Is the month chooser working like it should?
    """
    url = '/finance/teacher_payments_generate_invoices_choose_month'
    client.get(url)
    assert client.status  == 200

    assert 'Create teacher credit invoices for month' in client.text


def test_teacher_payments_generate_invoices(client, web2py):
    """
        Are the credit invoices created like they should?
        Check default rate
        Check class specific rate
        Check travel allowance
    """
    prepare_classes(web2py)
    populate_auth_user_teachers_fixed_rate_default(web2py)
    populate_auth_user_teachers_fixed_rate_class_1(web2py)
    populate_auth_user_teachers_fixed_rate_travel(web2py)

    url = '/finance/teacher_payments_generate_invoices_choose_month'
    client.get(url)
    assert client.status == 200

    today = datetime.date.today()

    data = {
        'month': today.month,
        'year': today.year
    }
    client.post(url, data=data)
    assert client.status == 200

    # Teacher 2 should have an item with the class specific rate
    query = (web2py.db.invoices_customers.auth_customer_id == 2)
    ic = web2py.db(query).select(web2py.db.invoices_customers.ALL).first()
    invoice = web2py.db.invoices(ic.invoices_id)

    assert invoice.TeacherPayment == True
    assert invoice.TeacherPaymentMonth == data['month']
    assert invoice.TeacherPaymentYear == data['year']

    query = (web2py.db.invoices_items.invoices_id == ic.invoices_id)
    rows = web2py.db(query).select(web2py.db.invoices_items.ALL)
    item = rows.first()

    # Check class_specific_rate
    tpfrc = web2py.db.teachers_payment_fixed_rate_class(1)
    assert item.Price == tpfrc.ClassRate * -1

    # Check travel allowance
    tpfrt = web2py.db.teachers_payment_fixed_rate_travel(1)
    item_2 = rows[1]
    assert item_2.ProductName == 'Travel allowance'
    assert item_2.Price == tpfrt.TravelAllowance * -1


    # Teacher 3 should have an item with the default rate
    query = (web2py.db.invoices_customers.auth_customer_id == 3)
    ic = web2py.db(query).select(web2py.db.invoices_customers.ALL).first()

    query = (web2py.db.invoices_items.invoices_id == ic.invoices_id)
    rows = web2py.db(query).select(web2py.db.invoices_items.ALL)
    item = rows.first()

    # check default_specific_rate
    tpfrd = web2py.db.teachers_payment_fixed_rate_default(auth_teacher_id=3)
    assert item.Price == tpfrd.ClassRate * -1


def test_batches_index_collection(client, web2py):
    """
        Check whether the list of batches shows correctly
    """
    url = '/finance/batches_index?export=collection'
    client.get(url)
    assert client.status == 200

    assert 'Collection' in client.text


def test_batches_index_payment(client, web2py):
    """
        Check whether the list of batches shows correctly
    """
    url = '/finance/batches_index?export=payment'
    client.get(url)
    assert client.status == 200

    assert 'Payment' in client.text


def test_add_batch_default_without_zero_lines(client, web2py):
    """
        Check whether we can add a default batch and items are generated
        propery
    """
    url = '/finance/batch_add?export=collection&what=invoices'
    client.get(url)
    assert client.status == 200

    populate_customers_with_subscriptions(web2py, 10)

    # create invoices
    inv_url = '/invoices/subscriptions_create_invoices?month=1&year=2014'
    client.get(inv_url)
    assert client.status == 200

    data = {'description':'Default invoice description'}
    client.post(inv_url, data=data)
    assert client.status == 200

    # go back to the page where we have to submit the data for the new batch
    client.get(url)
    assert client.status == 200

    # Add a batch
    data = {'Name'        : 'Test export',
            'Description' : 'Cherry shake',
            'Exdate'      : '2014-02-01',
            'Note'        : 'Who loves bananas? Gorilla does!'}

    client.post(url, data=data)
    assert client.status == 200

    # check note
    assert 'Gorilla' in client.text

    # check amount total
    sum = web2py.db.invoices_amounts.TotalPriceVAT.sum()
    amount = web2py.db().select(sum).first()[sum]
    assert unicode(amount) in client.text.decode('utf-8')

    # check batch item text
    acc_holder = web2py.db.customers_payment_info(1).AccountHolder.split(' ')[0]
    assert acc_holder in client.text

    ## check batch total items
    # customer2's subscription is paused
    # Customer 8 & 9's subscription don't have an invoice
    # customer10's subscription has price 0, so should be skipped

    assert web2py.db(web2py.db.payment_batches_items).count() == 6


def test_add_batch_default_with_zero_lines(client, web2py):
    """
        Check whether we can add a default batch and items are generated
        propery and check whether lines with amount 0 are included
    """
    url = '/finance/batch_add?export=collection&what=invoices'
    client.get(url)
    assert client.status == 200

    populate_customers_with_subscriptions(web2py, 10)

    # create invoices
    inv_url = '/invoices/subscriptions_create_invoices?month=1&year=2014'
    client.get(inv_url)
    assert client.status == 200

    data = {'description':'Default invoice description'}
    client.post(inv_url, data=data)
    assert client.status == 200

    # remove the amount for 1 invoice
    amount = web2py.db.invoices_amounts(1)
    amount.TotalPriceVAT = 0
    amount.update_record()
    web2py.db.commit()

    # go back to the page where we have to submit the data for the new batch
    client.get(url)
    assert client.status == 200

    # Add a batch
    data = {'Name'        : 'Test export',
            'Description' : 'Cherry shake',
            'Exdate'      : '2014-02-01',
            'Note'        : 'Who loves bananas? Gorilla does!',
            'IncludeZero' : 'on'}

    client.post(url, data=data)
    assert client.status == 200

    # check note
    assert 'Gorilla' in client.text

    # check amount total
    sum = web2py.db.invoices_amounts.TotalPriceVAT.sum()
    amount = web2py.db().select(sum).first()[sum]
    assert unicode(amount) in client.text.decode('utf-8')

    # check batch item text
    acc_holder = web2py.db.customers_payment_info(1).AccountHolder.split(' ')[0]
    assert acc_holder in client.text

    ## check batch total items
    # customer2's subscription is paused
    # customer10's subscription has price 0, so no invoice was created

    assert web2py.db(web2py.db.payment_batches_items).count() == 6



def test_add_batch_default_location(client, web2py):
    """
        Check whether we can add an invoice based batch and items are generated
        propery for a selected location
    """
    ## set sys_property
    # without this, the form doesn't accept 'school_locations_id'
    web2py.db.sys_properties.insert(
        Property='Customer_ShowLocation',
        PropertyValue='on'
        )
    web2py.db.commit()

    school_locations_id = 1

    url = '/finance/batch_add?export=collection&what=invoices'
    client.get(url)
    assert client.status == 200

    populate_customers_with_subscriptions(web2py, 10)

    # create invoices
    inv_url = '/invoices/subscriptions_create_invoices?month=1&year=2014&create=do_stuff'
    client.get(inv_url)
    assert client.status == 200

    data = {'description':'Default invoice description'}
    client.post(inv_url, data=data)
    assert client.status == 200

    # back to the place where we want to be to create a batch
    client.get(url)
    assert client.status == 200

    data = {'Name'                : 'Test export',
            'Description'         : 'Cherry shake',
            'Exdate'              : '2014-02-01',
            'school_locations_id' : school_locations_id,
            'Note'                : 'Who loves bananas? Gorilla does!'}

    client.post(url, data=data)
    assert client.status == 200

    # check redirection
    assert 'Added batch' in client.text

    # check note
    assert 'Gorilla' in client.text

    # count customers
    query = (web2py.db.auth_user.school_locations_id == school_locations_id)
    customers_count = web2py.db(query).count() - 1 # one subscription is paused
    # check amount total
    left = [ web2py.db.invoices.on(web2py.db.invoices.id ==
                web2py.db.invoices_amounts.invoices_id),
             web2py.db.auth_user.on(web2py.db.auth_user.id ==
                web2py.db.invoices.auth_customer_id)]

    sum = web2py.db.invoices_amounts.TotalPriceVAT.sum()
    query = (web2py.db.auth_user.school_locations_id == school_locations_id)
    amount = web2py.db(query).select(sum, left=left).first()[sum]
    assert unicode(amount) in client.text.decode('utf-8')



    # check batch item text (first 5 customers get school_locations_id 1)
    payinfo = web2py.db.customers_payment_info(1) # check that the first customer is in the batch
    acc_holder = payinfo.AccountHolder.split(' ')[0]
    assert acc_holder in client.text

    # nr of batches should be equal to nr of customers with locations_id 1
    query = (web2py.db.auth_user.school_locations_id == 1)

    items_count = web2py.db(web2py.db.payment_batches_items).count()
    assert customers_count == items_count



def test_add_batch_category_without_zero_lines(client, web2py):
    """
        Check if a batch for a direct debit extra category is exported correctly
    """
    url = '/finance/batch_add?export=collection&what=category'
    client.get(url)
    assert client.status == 200

    populate_customers_with_subscriptions(web2py, 10)

    web2py.db.payment_categories.insert(
        Name         = 'Papaya',
        CategoryType = 0 )

    alt_amount_1 = 200
    alt_desc_1 = 'Papaya'
    web2py.db.alternativepayments.insert(
        auth_customer_id       = 1001,
        PaymentYear            = 2014,
        PaymentMonth           = 1,
        Amount                 = alt_amount_1,
        Description            = alt_desc_1,
        payment_categories_id  = 1)

    alt_amount_2 = 2009
    alt_desc_2 = 'Pineapple'
    web2py.db.alternativepayments.insert(
        auth_customer_id       = 1002,
        PaymentYear            = 2014,
        PaymentMonth           = 1,
        Amount                 = alt_amount_2,
        Description            = alt_desc_2,
        payment_categories_id  = 1)

    alt_amount_3 = 0
    alt_desc_3 = 'Mango'
    web2py.db.alternativepayments.insert(
        auth_customer_id       = 1003,
        PaymentYear            = 2014,
        PaymentMonth           = 1,
        Amount                 = alt_amount_3,
        Description            = alt_desc_3,
        payment_categories_id  = 1)

    web2py.db.commit()

    #print web2py.db().select(web2py.db.customers_payment_info.ALL)

    data = {'Name'                  : 'Test export',
            'Description'           : 'Cherry shake',
            'ColYear'               : '2014',
            'ColMonth'              : '1',
            'Exdate'                : '2014-02-01',
            'Note'                  : 'Who loves bananas? Gorilla does!',
            'payment_categories_id' : '1'}

    client.post(url, data=data)
    assert client.status == 200

    ## check amount total
    amount = 0
    rows = web2py.db().select(web2py.db.alternativepayments.ALL)
    for row in rows:
        amount += row.Amount
    assert unicode(amount) in client.text.decode('utf-8')

    # check batch total items
    assert web2py.db(web2py.db.payment_batches_items).count() == 2

    # check description
    assert alt_desc_2 in client.text

    # check ignore zero lines
    assert not alt_desc_3 in client.text


def test_batch_set_status_sent_to_bank_add_payments(client, web2py):
    """
        Check if payments are added to invoices when the status of a batch
        becomes 'sent to bank'
    """
    url = '/finance/batch_add?export=collection&what=invoices'
    client.get(url)
    assert client.status == 200

    populate_customers_with_subscriptions(web2py, 10)

    # create invoices
    inv_url = '/invoices/subscriptions_create_invoices?month=1&year=2014&create=do_stuff'
    client.get(inv_url)
    assert client.status == 200

    data = {'description':'Default invoice description'}
    client.post(inv_url, data=data)
    assert client.status == 200

    # go back to the page where we have to submit the data for the new batch
    client.get(url)
    assert client.status == 200

    # Add a batch
    data = {'Name'        : 'Test export',
            'Description' : 'Cherry shake',
            'Exdate'      : '2014-02-01',
            'Note'        : 'Who loves bananas? Gorilla does!'}

    client.post(url, data=data)
    assert client.status == 200

    # check note
    assert 'Gorilla' in client.text

    # check setting of status 'sent_to_bank'
    url = '/finance/batch_content_set_status?pbID=1&status=sent_to_bank'
    client.get(url)
    assert client.status == 200

    # check if 8 payments have been added
    assert web2py.db(web2py.db.invoices_payments.id > 0).count() == 6

    # check payment amounts
    sum = web2py.db.invoices_amounts.TotalPriceVAT.sum()
    invoices_amount = web2py.db().select(sum).first()[sum]

    sum = web2py.db.invoices_payments.Amount.sum()
    payments_amount = web2py.db().select(sum).first()[sum]

    assert invoices_amount == payments_amount
