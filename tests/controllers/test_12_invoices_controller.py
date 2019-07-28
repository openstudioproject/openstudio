# -*- coding: utf-8 -*-

"""
    py.test test cases to test OpenStudio.
    These tests run based on webclient and need web2py server running.
"""

import datetime
from gluon.contrib.populate import populate
from populate_os_tables import prepare_classes
from populate_os_tables import populate_customers
from populate_os_tables import populate_customers_payment_info
from populate_os_tables import populate_customers_with_subscriptions
from populate_os_tables import populate_customers_with_memberships
from populate_os_tables import populate_customers_with_classcards
from populate_os_tables import populate_workshops_products_customers
from populate_os_tables import populate_invoices
from populate_os_tables import populate_invoices_items



def test_invoice_add_from_customer(client, web2py):
    """
        Can we add an invoice from a customer?
    """
    populate_customers(web2py, 1)

    url = '/customers/invoices?cuID=1001'
    client.get(url)
    assert client.status == 200

    data = {'invoices_groups_id' : 100,
            'Description'        : 'one crate of bananas'}
    client.post(url, data=data)
    assert client.status == 200

    # verify entry of data
    assert data['Description'] in client.text
    assert web2py.db(web2py.db.invoices).count() == 1

    # check setting of enddate and InvoiceID
    invoice = web2py.db.invoices(1)
    today = datetime.date.today()
    delta = datetime.timedelta(days = web2py.db.invoices_groups(100).DueDays)
    due = today + delta

    # verify redirection
    assert invoice.InvoiceID in client.text

    assert invoice.DateCreated == today
    assert invoice.DateDue == due

    assert invoice.InvoiceID == 'INV' + str(today.year) + '1'


def test_invoice_add_from_customer_automatic_reset_numbering(client, web2py):
    """
        Can we add an invoice from a customer?
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    prepare_classes(web2py, invoices=True)

    # Set date created to a previous year for all invoices
    web2py.db(web2py.db.invoices).update(DateCreated="2014-01-01")
    web2py.db.commit()

    invoices_count = web2py.db(web2py.db.invoices).count()

    url = '/customers/invoices?cuID=1001'
    client.get(url)
    assert client.status == 200

    data = {'invoices_groups_id' : 100,
            'Description'        : 'one crate of bananas'}
    client.post(url, data=data)
    assert client.status == 200

    # verify entry of data
    assert data['Description'] in client.text
    assert web2py.db(web2py.db.invoices).count() == invoices_count + 1

    # check setting of enddate and InvoiceID
    max = web2py.db.invoices.id.max()
    iID = web2py.db().select(max).first()[max]

    invoice = web2py.db.invoices(iID)

    # verify redirection
    assert invoice.InvoiceID in client.text

    # Make sure the numbering has been reset
    today = datetime.date.today()
    assert invoice.InvoiceID == 'INV' + str(today.year) + '1'

    ig = web2py.db.invoices_groups(100)
    assert ig.NextID == 2


def test_invoice_add_from_customer_subscription(client, web2py):
    """
        Can we add a subscription from an invoice and does it set the
        cusotmers_subscriptions_id, year and month correctly
    """
    # get random URL to initialize OpenStudio environment
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_customers_with_subscriptions(web2py, 2)

    url = '/customers/subscription_invoices?cuID=1001&csID=1'
    client.get(url)
    assert client.status == 200

    data = {'invoices_groups_id' : 100,
            'SubscriptionMonth'  : 1,
            'SubscriptionYear'   : 2014,
            'Description'        : 'Cherry blossom'}

    client.post(url, data=data)
    assert client.status == 200

    # verify display of some values on the page
    assert data['Description'] in client.text

    # Check invoice terms & footer
    ig_1 = web2py.db.invoices_groups(100)
    invoice = web2py.db.invoices(1)

    assert invoice.SubscriptionYear == 2014
    assert invoice.SubscriptionMonth == 1
    assert invoice.Terms == ig_1.Terms
    assert invoice.Footer == ig_1.Footer
    assert invoice.SubscriptionYear           == 2014
    assert invoice.SubscriptionMonth          == 1

    # Verify linking of invoice to customer and subscription
    ic = web2py.db.invoices_customers(1)
    assert ic.invoices_id == 1
    assert ic.auth_customer_id == 1001
    iics = web2py.db.invoices_items_customers_subscriptions(1)
    assert iics.invoices_items_id == 1
    assert iics.customers_subscriptions_id == 1
    # verify redirection
    assert invoice.InvoiceID in client.text

    # check default invoice group
    query = (web2py.db.invoices_groups_product_types.ProductType == 'subscription')
    row = web2py.db(query).select(web2py.db.invoices_groups_product_types.ALL).first()
    igptID = row.invoices_groups_id

    assert invoice.invoices_groups_id == igptID


def test_invoice_add_from_customer_subscription_with_registration_fee(client, web2py):
    """
        Can we add a subscription from an invoice and does it set the
        cusotmers_subscriptions_id, year and month correctly
    """
    # get random URL to initialize OpenStudio environment
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_customers_with_subscriptions(web2py, 2)

    # Update first school subscription to have a registration fee
    web2py.db.school_subscriptions[1] = dict(RegistrationFee=25.00)
    web2py.db.commit()
    url = '/customers/subscription_invoices?cuID=1001&csID=1'
    client.get(url)
    assert client.status == 200

    data = {'invoices_groups_id' : 100,
            'SubscriptionMonth'  : 1,
            'SubscriptionYear'   : 2014,
            'Description'        : 'Cherry blossom',
            }

    client.post(url, data=data)
    assert client.status ==200

    url = '/customers/subscription_invoices?cuID=1001&csID=1'
    client.get(url)
    assert client.status == 200
    data = {'invoices_groups_id': 100,
            'SubscriptionMonth': 2,
            'SubscriptionYear': 2014,
            'Description': 'Cherry blossom',
            }

    client.post(url, data=data)
    assert client.status == 200


    # verify if registration fee is added
    assert web2py.db(web2py.db.invoices_items.ProductName =='Registration fee').count() == 1
    assert web2py.db(web2py.db.invoices.id >0).count()        == 2


def test_invoice_edit(client, web2py):
    """
        Can we edit an invoice?
    """
    populate_customers(web2py, 3)

    url = '/customers/invoices?cuID=1001'
    client.get(url)
    assert client.status == 200

    populate_invoices(web2py)

    data = {'Description'   : 'Mangoes'}

    client.post(url, data=data)
    assert client.status == 200

    assert data['Description'] in client.text


def test_invoice_show_duplicate_button(client, web2py):
    """
    Does the Button show and doesn't when it shouldn't
    """
    populate_customers(web2py,3)

    url = '/customers/invoices?cuID=1001'
    client.get(url)
    assert client.status == 200

    populate_invoices(web2py)

    populate_invoices_items(web2py)

    url = '/invoices/edit?iID=1'
    client.get(url)
    assert client.status == 200

    assert 'Duplicate' in client.text


def test_invoice_dont_show_duplicate_button_class_attendance_invoice(client, web2py):
    """
    DOes the button not show when teacher payment?
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    prepare_classes(web2py, invoices=True)

    url = '/invoices/edit?iID=1'
    client.get(url)
    assert client.status == 200

    assert 'Duplicate' not in client.text


def test_invoice_dont_show_duplicate_button_teacher_payment(client, web2py):
    """
    DOes the button not show when teacher payment?
    """
    populate_customers(web2py,3)

    url = '/customers/invoices?cuID=1001'
    client.get(url)
    assert client.status == 200

    populate_invoices(web2py, teacher_fixed_price_invoices= True)

    populate_invoices_items(web2py)

    url = '/invoices/edit?iID=1'
    client.get(url)
    assert client.status == 200

    assert 'Duplicate' not in client.text


def test_invoice_dont_show_duplicate_button_employee_claim(client, web2py):
    """
    Does the Button not show when it is an employee Claim?
    """
    populate_customers(web2py,3)

    url = '/customers/invoices?cuID=1001'
    client.get(url)
    assert client.status == 200

    populate_invoices(web2py, employee_claim= True)

    populate_invoices_items(web2py)

    url = '/invoices/edit?iID=1'
    client.get(url)
    assert client.status == 200

    assert 'Duplicate' not in client.text


def test_invoice_dont_show_duplicate_button_subscription(client, web2py):
    """
    Does the Button not show when it is a subscription?
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_customers_with_subscriptions(web2py, 3, invoices=True)

    url = '/invoices/edit?iID=1'
    client.get(url)
    assert client.status == 200

    assert 'Duplicate' not in client.text


def test_invoice_dont_show_duplicate_button_membership(client, web2py):
    """
    Does the Button not show when it is a membership?
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200
    populate_customers_with_memberships(web2py, invoices=True)

    # url = '/customers/invoices?cuID=1001'
    # client.get(url)
    # assert client.status == 200

    url = '/invoices/edit?iID=1'
    client.get(url)
    assert client.status == 200

    assert 'Duplicate' not in client.text


def test_invoice_dont_show_duplicate_button_classcards(client, web2py):
    """
    Does the Button  not show when it is a classcard?
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200
    populate_customers_with_classcards(web2py,3, invoices = True)


    url = '/invoices/edit?iID=1'
    client.get(url)
    assert client.status == 200

    assert 'Duplicate' not in client.text


def test_invoice_dont_show_duplicate_button_workshop(client, web2py):
    """
    Does the Button not show when it is a workshop order?
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200
    populate_workshops_products_customers(web2py,3)


    url = '/invoices/edit?iID=1'
    client.get(url)
    assert client.status == 200

    assert 'Duplicate' not in client.text


def test_invoice_duplicate_invoice(client, web2py):
    """
    Does the Duplicate get generated correctly with all possible connections?
    """
    populate_customers(web2py,3)


    url = '/customers/invoices?cuID=1001'
    client.get(url)
    assert client.status == 200

    populate_invoices(web2py, customers_orders = True)
    # print 1

    populate_invoices_items(web2py)
    # print 2

    url = '/invoices/edit?iID=1'
    client.get(url)
    assert client.status == 200
    # print 3

    url = '/invoices/duplicate_invoice?iID=1'
    client.get(url)
    assert client.status == 200
    # print 4
    oldrow = web2py.db.invoices(id = 1)
    query = ((web2py.db.invoices.CustomerName == oldrow.CustomerName) &
             (web2py.db.invoices.invoices_groups_id == oldrow.invoices_groups_id) &
             (web2py.db.invoices.payment_methods_id == oldrow.payment_methods_id) &
             (web2py.db.invoices.id != oldrow.id) &
             (web2py.db.invoices.InvoiceID != oldrow.InvoiceID))

    assert web2py.db(query).count() == 1

    newrow = web2py.db(query).select().first()

    cusrow= web2py.db(web2py.db.invoices_customers.invoices_id == newrow.id).select().first()

    oldcusrow = web2py.db(web2py.db.invoices_customers.invoices_id == oldrow.id).select().first()

    assert cusrow.auth_customer_id == oldcusrow.auth_customer_id

    #Are all the items correctly duplicated?
    query = (web2py.db.invoices_items.invoices_id == oldrow.id)
    oldrows = web2py.db(query).select()
    query = (web2py.db.invoices_items.invoices_id == oldrow.id)
    rows = web2py.db(query).select()
    for row in oldrows:
         query = ((web2py.db.invoices_items.invoices_id == newrow.id) &
                  (web2py.db.invoices_items.ProductName == row.ProductName) &
                  (web2py.db.invoices_items.Description == row.Description) &
                  (web2py.db.invoices_items.Quantity == row.Quantity) &
                  (web2py.db.invoices_items.Price == row.Price) &
                  (web2py.db.invoices_items.tax_rates_id == row.tax_rates_id) &
                  (web2py.db.invoices_items.accounting_glaccounts_id == row.accounting_glaccounts_id) &
                  (web2py.db.invoices_items.accounting_costcenters_id == row.accounting_costcenters_id)
                  )
         assert web2py.db(query).count() == 1

    #Is the connection to invoices_customers_order there?
    oldcusorderrow = web2py.db(web2py.db.invoices_customers_orders.invoices_id == oldrow.id).select().first()
    if oldcusorderrow:
        query = ((web2py.db.invoices_customers_orders.invoices_id == newrow.id)&
                (web2py.db.invoices_customers_orders.customers_orders_id == oldcusorderrow.customers_orders_id))
        assert web2py.db(query).count() == 1


def test_invoice_item_add(client, web2py):
    """
        Can we add an item to an invoice?
    """
    populate_customers(web2py, 3)

    url = '/customers/invoices?cuID=1001'
    client.get(url)
    assert client.status == 200

    populate_invoices(web2py)

    url = '/invoices/list_items?iID=1'
    client.get(url)
    assert client.status == 200

    data = {
        'ProductName'       : 'Fruits',
        'Description'       : 'Mangoes',
        'Quantity'          : 10,
        'Price'             : 1234,
        'tax_rates_id'      : 1,
    }
    client.post(url, data=data)
    assert client.status == 200

    # Check DB
    assert web2py.db(web2py.db.invoices_items).count() == 1

    # Check updated listing
    assert data['Description'] in client.text

    # Check sorting & prices in item
    item = web2py.db.invoices_items(1)
    # Sorting has no default value from the db, so if we get a 1, it's generating the sorting numbers correctly
    assert item.Sorting == 1

    # calculate total incl. vat
    TotalPriceVAT = data['Quantity'] * data['Price']
    assert item.TotalPriceVAT == TotalPriceVAT

    # calculate vat
    tax_rate = web2py.db.tax_rates(data['tax_rates_id'])
    percentage = tax_rate.Percentage / 100
    VAT = round(TotalPriceVAT - (TotalPriceVAT / (1 + percentage)), 2)
    assert item.VAT == VAT

    # calculate total without vat
    TotalPrice = TotalPriceVAT - VAT
    assert item.TotalPrice == TotalPrice

    # Check amounts in Invoices_amounts
    amounts = web2py.db.invoices_amounts(1)
    assert amounts.TotalPrice == TotalPrice
    assert amounts.VAT == VAT
    assert amounts.TotalPriceVAT == TotalPriceVAT


def test_invoice_item_edit(client, web2py):
    """
        Can we edit an item in an invoice?
    """
    populate_customers(web2py, 3)

    url = '/customers/invoices?cuID=1001'
    client.get(url)
    assert client.status == 200

    populate_invoices(web2py)
    populate_invoices_items(web2py)

    url = '/invoices/item_edit?iID=1&iiID=1'
    client.get(url)
    assert client.status == 200

    data = {
        'id'          : 1,
        'ProductName' : 'Cherries'
    }
    client.post(url, data=data)
    assert client.status == 200

    assert data['ProductName'] in client.text


def test_invoice_item_delete(client, web2py):
    """
        Can we delete an item from an invoice?
    """
    populate_customers(web2py, 3)

    url = '/customers/invoices?cuID=1001'
    client.get(url)
    assert client.status == 200

    populate_invoices(web2py)
    populate_invoices_items(web2py)

    # Is the confirmation page showing?
    url = '/invoices/item_delete_confirm?iID=1&iiID=1'
    client.get(url)
    assert client.status == 200

    url ='/invoices/item_delete?iID=1&iiID=1'
    client.get(url)
    assert client.status == 200

    assert web2py.db.invoices_items(1) is None

    # check amounts
    amounts = web2py.db.invoices_amounts(1)
    assert amounts.TotalPriceVAT == 0



def test_invoice_overdue_duedate_is_red(client, web2py):
    """
        Make sure the due date for overdue invoices becomes red in the list
        of invoices
    """
    url = '/finance/invoices'
    client.get(url)
    assert client.status == 200

    populate_customers(web2py, 10)
    populate_invoices(web2py)

    # make the invoice overdue
    invoice = web2py.db.invoices(1)
    invoice.DateDue = '2013-01-01'
    invoice.update_record()

    web2py.db.commit()

    client.get(url)
    assert client.status == 200

    # check for css class
    assert 'bold red' in client.text


def test_invoice_payment_add_set_status_paid(client, web2py):
    """
        Set status to paid after adding a payment >= invoice amount
    """
    url = '/finance/invoices'
    client.get(url)
    assert client.status == 200

    populate_customers(web2py, 10)
    populate_invoices(web2py)

    amounts = web2py.db.invoices_amounts(1)
    amounts.TotalPrice       = 20
    amounts.VAT              = 2
    amounts.TotalPriceVAT    = 22
    amounts.Paid             = 0
    amounts.Balance          = 22
    amounts.update_record()

    web2py.db.commit()

    url = '/invoices/payment_add?iID=1'
    client.get(url)
    assert client.status == 200

    data = {
        'invoices_id'         : 1,
        'Amount'              : 20,
        'PaymentDate'         : '2014-01-01',
        'payment_methods_id'  : 3,
        'Note'                : 'first payment using bananas'
    }

    client.post(url, data=data)
    assert client.status == 200

    client.get('/invoices/invoice_payments?iID=1')
    assert client.status == 200
    assert data['Note'] in client.text

    invoice = web2py.db.invoices(1)
    assert invoice.Status == 'sent'

    # go back to the page where we want to submit payments
    client.get(url)
    assert client.status == 200

    data = {
        'invoices_id'         : 1,
        'Amount'              : 2,
        'PaymentDate'         : '2014-01-02',
        'payment_methods_id'  : 3,
        'Note'                : 'second payment using bananas'
    }

    client.post(url, data=data)
    assert client.status == 200

    invoice = web2py.db.invoices(1)
    assert invoice.Status == 'paid'


def test_list_invoices_status_filter(client, web2py):
    """
        Test if the status filter for list_invoices works
    """
    url = '/finance/invoices'
    client.get(url)
    assert client.status == 200

    populate_customers(web2py, 10)
    populate_invoices(web2py)

    # change invoice 1 to paid and set a recognizable description so we can check the list
    description = 'Grapefruit'
    invoice = web2py.db.invoices(1)
    invoice.Description = description
    invoice.Status = 'draft'
    invoice.update_record()

    web2py.db.commit()

    post_url = '/finance/invoices'
    data = {'status':'draft'}

    client.post(post_url, data=data)
    assert client.status == 200

    assert description in client.text


def test_list_invoices_search(client, web2py):
    """
        Is the search box working?
    """
    url = '/finance/invoices'
    client.get(url)
    assert client.status == 200

    populate_customers(web2py, 10)
    populate_invoices(web2py)

    search_string = 'Banana'
    invoice = web2py.db.invoices(1)
    invoice.InvoiceID = search_string
    invoice.update_record()
    web2py.db.commit()

    data = {'search':search_string}
    client.post(url, data=data)
    assert client.status == 200

    assert search_string in client.text


def test_cancel_and_create_credit_invoice(client, web2py):
    """
        Is an invoice cancelled and a credit invoice created?
    """
    populate_customers(web2py, 3)

    url = '/customers/invoices?cuID=1001'
    client.get(url)
    assert client.status == 200

    populate_invoices(web2py)
    populate_invoices_items(web2py)

    url = '/invoices/cancel_and_create_credit_invoice?iID=1'
    client.get(url)
    assert client.status == 200

    assert web2py.db.invoices_items(5).Price == -12
    assert web2py.db.invoices_items(5).TotalPriceVAT == -120

    assert "This is a credit invoice for invoice" in client.text