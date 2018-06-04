# -*- coding: utf-8 -*-

from general_helpers import max_string_length
from general_helpers import datestr_to_python
from general_helpers import get_last_day_month

from openstudio.openstudio import Invoice, Order, Customer, CustomerSubscription, OsMail

from decimal import Decimal, ROUND_HALF_UP

import Mollie


def webhook():
    """
        Webhook called by mollie
    """
    id = request.vars['id']

    mlwID = db.mollie_log_webhook.insert(mollie_payment_id=id)
    mlw = db.mollie_log_webhook(mlwID)

    # try to get payment
    try:
        mollie = Mollie.API.Client()
        mollie_api_key = get_sys_property('mollie_website_profile')
        mollie.setApiKey(mollie_api_key)

        payment_id = id
        payment = mollie.payments.get(payment_id)

        mlw.mollie_payment = unicode(payment)
        mlw.update_record()

        iID = ''
        coID = payment['metadata']['customers_orders_id'] # customers_orders_id
        if coID == 'invoice':
            # Invoice payment instead of order payment
            iID = payment['metadata']['invoice_id']

        if payment.isRefunded():
            #
            # The payment has been refunded
            #
            return 'Refunded'
        elif payment.isPaid():
            #
            # At this point you'd probably want to start the process of delivering the
            # product to the customer.
            #
            payment_amount = float(payment['amount'])
            payment_date = datetime.datetime.strptime(payment[u'paidDatetime'].split('.')[0],
                                                      '%Y-%m-%dT%H:%M:%S').date()

            if coID == 'invoice':
                # Add payment to invoice, no delivery required
                webhook_invoice_paid(iID, payment_amount, payment_date, payment_id)
            else:
                # Deliver order
                webhook_order_paid(coID, payment_amount, payment_date, payment_id)

            return 'Paid'
        elif payment.isPending():
            #
            # The payment has started but is not complete yet.
            #
            return 'Pending'
        elif payment.isOpen():
            #
            # The payment has not started yet. Wait for it.
            #
            return 'Open'
        else:
            #
            # The payment isn't paid, pending nor open. We can assume it was aborted.
            #
            return 'Cancelled'
    except Mollie.API.Error as e:
        return 'API call failed: ' + e.message


def test_webhook_order_paid():
    """
        A test can call this function to check whether everything works after an order has been paid
    """
    if not web2pytest.is_running_under_test(request, request.application):
        redirect(URL('default', 'user', args=['not_authorized']))
    else:
        coID = request.vars['coID']
        payment_amount = request.vars['payment_amount']
        payment_date = request.vars['payment_date']
        mollie_payment_id = request.vars['mollie_payment_id']

        webhook_order_paid(coID, payment_amount, payment_date, mollie_payment_id)


def test_webhook_invoice_paid():
    """
        A test can call this function to check whether everything works after an invoice has been paid
    """
    if not web2pytest.is_running_under_test(request, request.application):
        redirect(URL('default', 'user', args=['not_authorized']))
    else:
        iID = request.vars['iID']
        payment_amount = request.vars['payment_amount']
        payment_date = request.vars['payment_date']
        mollie_payment_id = request.vars['mollie_payment_id']

        webhook_invoice_paid(iID, payment_amount, payment_date, mollie_payment_id)


def webhook_order_paid(coID, payment_amount=None, payment_date=None, mollie_payment_id=None, invoice=True):
    """
        :param coID: db.customers_orders.id
        :return: None
    """
    order = Order(coID)
    result = order.deliver()

    if invoice:
        # Add payment to invoice
        invoice = result['invoice']

        if not invoice is None:
            ipID = invoice.payment_add(
                payment_amount,
                payment_date,
                payment_methods_id=100,  # Static id for Mollie payments
                mollie_payment_id=mollie_payment_id
            )

            # link invoice to mollie_payment_id
            db.invoices_mollie_payment_ids.insert(
                invoices_id=invoice.invoice.id,
                mollie_payment_id=mollie_payment_id
            )

            # notify customer
            # os_mail = OsMail()
            # msg = os_mail.render_email_template('email_template_payment_received', invoices_payments_id=ipID)

            #os_mail.send(msg, invoice.invoice.auth_customer_id)


def webhook_invoice_paid(iID, payment_amount, payment_date, mollie_payment_id):
    """
        :param iID: db.invoices.id
        :return: None
    """
    invoice = Invoice(iID)

    ipID = invoice.payment_add(
        payment_amount,
        payment_date,
        payment_methods_id=100,  # Static id for Mollie payments
        mollie_payment_id=mollie_payment_id
    )

    # link invoice to mollie_payment_id
    db.invoices_mollie_payment_ids.insert(
        invoices_id=invoice.invoice.id,
        mollie_payment_id=mollie_payment_id
    )

    # notify customer
    #os_mail = OsMail()
    #msgID = os_mail.render_email_template('email_template_payment_received', invoices_payments_id=ipID)

    #os_mail.send(msgID, invoice.invoice.auth_customer_id)


@auth.requires_login()
def invoice_pay():
    """
        Link to mollie payment page from invoice payment
    """
    #response.title = T("Pay invoice")
    iID = request.vars['iID']

    invoice = Invoice(iID)
    invoice_amounts = invoice.get_amounts()

    if not invoice.get_linked_customer_id() == auth.user.id:
        return 'Not authorized'

    mollie = Mollie.API.Client()
    mollie_api_key = get_sys_property('mollie_website_profile')
    mollie.setApiKey(mollie_api_key)

    description = invoice.invoice.Description + ' [' + invoice.invoice.InvoiceID + ']'
    recurring_type = None
    mollie_customer_id = None

    # Subscription invoice?
    if invoice.get_linked_customer_subscription_id():
        # subscription invoice
        # customer = Customer(auth.user.id)
        # mollie_customer_id = customer.row.mollie_customer_id
        # check if we have a mollie customer id
        os_customer = Customer(auth.user.id)
        if os_customer.row.mollie_customer_id:
            # yep
            mollie_customer_id = os_customer.row.mollie_customer_id
            try:
                mollie_customer = mollie.customers.get(mollie_customer_id)
                # print "we've got one!"
                # print mollie_customer
                # print mollie.customers.all()
            except Exception as e:
                # print e.__class__.__name__
                # print str(e)
                # print 'customer id invalid, create new customer'
                if 'The customer id is invalid' in str(e):
                    create_mollie_customer(os_customer)
        else:
            create_mollie_customer(os_customer, mollie)

        mandates = os_customer.get_mollie_mandates()
        # set default recurring type, change to recurring if a valid mandate is found.
        recurring_type = 'first'
        if mandates['count'] > 0:
            # background payment
            valid_mandate = False
            for mandate in mandates:
                if mandate['status'] == 'valid':
                    valid_mandate = True
                    break

            if valid_mandate:
                # Do a normal payment, probably an automatic payment failed somewhere in the process
                # and customer should pay manually now
                recurring_type = None

    # Do a regular payment or first recurring payment
    try:
        payment = mollie.payments.create({
            'amount':      invoice_amounts.TotalPriceVAT,
            'description': description,
            'recurringType': recurring_type,
            'customerId': mollie_customer_id,
            'redirectUrl': 'https://' + request.env.http_host + '/shop/complete?iID=' + unicode(iID),
            'webhookUrl': 'https://' + request.env.http_host + '/mollie/webhook',
            'metadata': {
                'invoice_id': invoice.invoice.id,
                'customers_orders_id': 'invoice' # This lets the webhook function know it's dealing with an invoice
            }
        })

        db.invoices_mollie_payment_ids.insert(
            invoices_id=iID,
            mollie_payment_id=payment['id']
        )

        # Send the customer off to complete the payment.
        redirect(payment.getPaymentUrl())

    except Mollie.API.Error as e:
        return 'API call failed: ' + e.message


@auth.requires_login()
def order_pay():
    """
        Page to pay an order
    """
    coID = request.vars['coID']

    order = Order(coID)
    invoice_id = ''
    mollie_payment_id = ''

    # check if the order belongs to the currently logged in customer
    if not order.order.auth_customer_id == auth.user.id:
        session.flash = T("What are you doing? This order isn't yours")
        redirect(URL('cart'))


    mollie = Mollie.API.Client()
    mollie_api_key = get_sys_property('mollie_website_profile')
    mollie.setApiKey(mollie_api_key)

    amounts = order.get_amounts()

    # Go to Mollie for payment
    amount = amounts.TotalPriceVAT
    description = T('Order') + ' #' + unicode(coID)

    try:
        payment = mollie.payments.create({
            'amount': amount,
            'description': description,
            'redirectUrl': 'https://' + request.env.http_host + '/shop/complete?coID=' + unicode(coID),
            'webhookUrl': 'https://' + request.env.http_host + '/mollie/webhook',
            'metadata': {
                'customers_orders_id': coID
            }
        })

        db.customers_orders_mollie_payment_ids.insert(
            customers_orders_id=coID,
            mollie_payment_id=payment['id']
        )

        # Send the customer off to complete the payment.
        redirect(payment.getPaymentUrl())

    except Mollie.API.Error as e:
        return 'API call failed: ' + e.message


def mollie_customer_check_valid(auth_user_id):
    """
    :param var: None
    :return: Boolean - True if there is a valid mollie customer for this OpenStudio customer
    """
    os_customer = Customer(auth_user_id)
    if not os_customer.row.mollie_customer_id:
        return False
    else:
        try:
            mollie_customer = mollie.customers.get(mollie_customer_id)
            return True
        except Exception as e:
            return False


def create_mollie_customer(auth_user_id, mollie):
    """
    :param os_customer: Customer object
    :return:
    """
    if not mollie_customer_check_valid(auth_user_id):
        mollie_customer = mollie.customers.create({
            'name': os_customer.row.display_name,
            'email': os_customer.row.email
        })

        #print mollie_customer

        os_customer.row.mollie_customer_id = mollie_customer['id']
        os_customer.row.update_record()

        #print 'created mollie customer'


@auth.requires_login()
def subscription_buy_now():
    """
        Get a subscription
    """
    ssuID = request.vars['ssuID']

    # init mollie
    mollie = Mollie.API.Client()
    mollie_api_key = get_sys_property('mollie_website_profile')
    mollie.setApiKey(mollie_api_key)

    create_mollie_customer(auth.user.id, mollie)

    # add subscription to customer﻿​_
    startdate = TODAY_LOCAL
    shop_subscriptions_start = get_sys_property('shop_subscriptions_start')
    if not shop_subscriptions_start == None:
        if shop_subscriptions_start == 'next_month':
            startdate = get_last_day_month(TODAY_LOCAL) + datetime.timedelta(days=1)

    csID = db.customers_subscriptions.insert(
        auth_customer_id = auth.user.id,
        school_subscriptions_id = ssuID,
        Startdate = startdate,
        payment_methods_id = 100, # important, 100 is the payment_methods_id for Mollie
    )

    # Add credits for the first month
    cs = CustomerSubscription(csID)
    cs.add_credits_month(startdate.year, startdate.month)

    # clear cache to make sure it shows in the back end
    cache_clear_customers_subscriptions(auth.user.id)

    # Create invoice
    cs = CustomerSubscription(csID)
    iID = cs.create_invoice_for_month(TODAY_LOCAL.year, TODAY_LOCAL.month)

    # Pay invoice ... SHOW ME THE MONEY!! :)
    redirect(URL('invoice_pay', vars={'iID':iID}))


@auth.requires_login()
def membership_buy_now():
    """
        Get a membership
    """
    from openstudio.os_school_membership import SchoolMembership

    smID = request.vars['smID']

    # init mollie
    mollie = Mollie.API.Client()
    mollie_api_key = get_sys_property('mollie_website_profile')
    mollie.setApiKey(mollie_api_key)

    # check if we have a mollie customer id
    create_mollie_customer(auth.user.id, mollie)

    # add membership to customer﻿​_

    cmID = db.customers_memberships.insert(
        auth_customer_id = auth.user.id,
        school_memberships_id = smID,
        Startdate = TODAY_LOCAL,
        payment_methods_id = 100, # important, 100 is the payment_methods_id for Mollie
    )

    # clear cache to make sure it shows in the back end
    # cache_clear_customers_subscriptions(auth.user.id)

    # Create invoice
    sm = SchoolMembership(smID)
    iID = sm.sell_to_customer_create_invoice(cmID)

    # Pay invoice ... SHOW ME THE MONEY!! :)
    redirect(URL('invoice_pay', vars={'iID':iID}))


@auth.requires_login()
def donate():
    """
        Allow customers to make a donation 
    """
    amount = request.vars['amount']
    description = request.vars['description']


    payment = mollie.payments.create({
        'amount': amount,
        'description': description,
        'redirectUrl': 'https://' + request.env.http_host + '/shop/complete?iID=' + unicode(iID),
        'webhookUrl': 'https://' + request.env.http_host + '/mollie/webhook',
        'metadata': {
            'invoice_id': invoice.invoice.id,
            'customers_orders_id': 'invoice'  # This lets the webhook function know it's dealing with an invoice
        }
    })

    db.invoices_mollie_payment_ids.insert(
        invoices_id=iID,
        mollie_payment_id=payment['id']
    )

    # Send the customer off to complete the payment.
    redirect(payment.getPaymentUrl())
