# -*- coding: utf-8 -*-

from general_helpers import max_string_length
from general_helpers import datestr_to_python
from general_helpers import get_last_day_month

from openstudio.os_customer_subscription import CustomerSubscription
from openstudio.os_mail import OsMail
from openstudio.os_invoice import Invoice
from openstudio.os_order import Order

from decimal import Decimal, ROUND_HALF_UP

from mollie.api.client import Client
from mollie.api.error import Error as MollieError


def webhook():
    """
        Webhook called by mollie
    """
    id = request.vars['id']

    mlwID = db.mollie_log_webhook.insert(mollie_payment_id=id)
    mlw = db.mollie_log_webhook(mlwID)

    # try to get payment
    try:
        mollie = Client()
        mollie_api_key = get_sys_property('mollie_website_profile')
        mollie.set_api_key(mollie_api_key)

        payment_id = id
        payment = mollie.payments.get(payment_id)

        mlw.mollie_payment = unicode(payment)
        mlw.update_record()

        iID = ''
        coID = payment['metadata']['customers_orders_id'] # customers_orders_id

        if coID == 'invoice':
            # Invoice payment instead of order payment
            iID = payment['metadata']['invoice_id']

        if payment.is_paid():
            #
            # At this point you'd probably want to start the process of delivering the
            # product to the customer.
            #
            payment_amount = float(payment.amount['value'])
            payment_date = datetime.datetime.strptime(payment.paid_at.split('+')[0],
                                                      '%Y-%m-%dT%H:%M:%S').date()


            # Process refunds
            if payment.refunds:
                webook_payment_is_paid_process_refunds(coID, iID, payment.refunds)

            # Process chargebacks
            if payment.chargebacks:
                webhook_payment_is_paid_process_chargeback(coID, iID, payment)

            if coID == 'invoice':
                # add payment to invoice
                webhook_invoice_paid(iID, payment_amount, payment_date, payment_id)
            else:
                # Deliver order
                webhook_order_paid(coID, payment_amount, payment_date, payment_id)

            return 'Paid'
        elif payment.is_pending():
            #
            # The payment has started but is not complete yet.
            #
            return 'Pending'
        elif payment.is_open():
            #
            # The payment has not started yet. Wait for it.
            #
            return 'Open'
        else:
            #
            # The payment isn't paid, pending nor open. We can assume it was aborted.
            #
            return 'Cancelled'
    except MollieError as e:
        return 'API call failed: {error}'.format(error=e)


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

    if result and invoice:
        # Add payment to invoice
        invoice = result['invoice']

        if not invoice is None:
            ipID = invoice.payment_add(
                payment_amount,
                payment_date,
                payment_methods_id=100,  # Static id for Mollie payments
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
    query = (db.invoices_payments.mollie_payment_id == mollie_payment_id)
    if not db(query).count():
        # Don't process a payment twice
        invoice = Invoice(iID)

        ipID = invoice.payment_add(
            payment_amount,
            payment_date,
            payment_methods_id=100,  # Static id for Mollie payments
            mollie_payment_id=mollie_payment_id
        )

    # notify customer
    #os_mail = OsMail()
    #msgID = os_mail.render_email_template('email_template_payment_received', invoices_payments_id=ipID)

    #os_mail.send(msgID, invoice.invoice.auth_customer_id)


def webook_payment_is_paid_process_refunds(coID, iID, mollie_refunds):
    """
    Process refunds
    :return:
    """
    if coID and coID != 'invoice':
        query = (db.invoices_customers_orders.customers_orders_id == coID)
        row = db(query).select(db.invoices_customers_orders.ALL).first()
        iID = row.invoices_id

    if mollie_refunds[u'count']:
        for refund in mollie_refunds[u'_embedded'][u'refunds']:
            refund_id = refund[u'id']
            amount = float(refund['settlementAmount']['value'])
            refund_date = datetime.datetime.strptime(refund[u'createdAt'].split('+')[0],
                                                     '%Y-%m-%dT%H:%M:%S').date()
            try:
                description = refund[u'description']
            except:
                description = ''

            refund_description = "Mollie refund(%s) - %s" % (refund_id, description)

            query = (db.invoices_payments.mollie_refund_id == refund_id)
            count = db(query).count()

            if not db(query).count() and iID:
                # Only process the refund if it hasn't been processed already
                webhook_invoice_refund(
                    iID,
                    amount,
                    refund_date,
                    refund[u'paymentId'],
                    refund[u'id'],
                    refund_description
                )


def webhook_invoice_refund(iID,
                           amount,
                           date,
                           mollie_payment_id,
                           mollie_refund_id,
                           note):
    """
    Actually add refund invoice payment
    This function is separate for testability
    """
    from openstudio.os_invoice import Invoice
    invoice = Invoice(iID)

    ipID = invoice.payment_add(
        amount,
        date,
        payment_methods_id=100,  # Static id for Mollie payments
        mollie_payment_id=mollie_payment_id,
        mollie_refund_id=mollie_refund_id,
        note=note
    )


def test_webhook_invoice_refund():
    """
        A test can call this function to check whether everything works after a
        chargeback payment has been added to a customer payment
    """
    if not web2pytest.is_running_under_test(request, request.application):
        redirect(URL('default', 'user', args=['not_authorized']))
    else:
        iID = request.vars['iID']
        refund_amount = request.vars['refund_amount']
        refund_date = request.vars['refund_date']
        mollie_payment_id = request.vars['mollie_payment_id']
        refund_id = request.vars['refund_id']
        refund_details = request.vars['refund_details']

        webhook_invoice_refund(
            iID,
            refund_amount,
            refund_date,
            mollie_payment_id,
            refund_id,
            refund_details
        )


def webhook_payment_is_paid_process_chargeback(coID,
                                               iID,
                                               mollie_payment):
    """
    Chargebacks occur when a direct debit payment fails due to insufficient funds in the customers' bank account
    :return:
    """
    if coID and coID != 'invoice':
        query = (db.invoices_customers_orders.customers_orders_id == coID)
        row = db(query).select(db.invoices_customers_orders.ALL).first()
        iID = row.invoices_id

    # Check if we have a chargeback
    mollie_chargebacks = mollie_payment.chargebacks
    if mollie_chargebacks[u'count']:
        for chargeback in mollie_chargebacks[u'_embedded'][u'chargebacks']:
            chargeback_id = chargeback[u'id']
            chargeback_amount = float(chargeback['settlementAmount']['value'])
            chargeback_date = datetime.datetime.strptime(chargeback[u'createdAt'].split('+')[0],
                                                         '%Y-%m-%dT%H:%M:%S').date()
            try:
                chargeback_details = "Failure reason: %s (Bank reason code: %s)" % (
                    mollie_payment[u'details']['bankReason'],
                    mollie_payment[u'details']['bankReasonCode']
                )
            except:
                chargeback_details = ''


            query = (db.invoices_payments.mollie_chargeback_id == chargeback_id)
            if not db(query).count():
                # Only process the chargeback if it hasn't been processed already
                webhook_invoice_chargeback(
                    iID,
                    chargeback_amount,
                    chargeback_date,
                    mollie_payment[u'id'],
                    chargeback_id,
                    "Mollie Chargeback (%s) - %s" % (chargeback_id, chargeback_details)
                )


def webhook_invoice_chargeback(iID,
                               amount,
                               date,
                               mollie_payment_id,
                               mollie_chargeback_id,
                               note):
    """
    Actuall add chargeback invoice payment
    This function is separate for testability
    """
    from openstudio.os_invoice import Invoice
    invoice = Invoice(iID)

    print "note in wic"
    print note

    ipID = invoice.payment_add(
        amount,
        date,
        payment_methods_id=100,  # Static id for Mollie payments
        mollie_payment_id=mollie_payment_id,
        mollie_chargeback_id=mollie_chargeback_id,
        note=note
    )

    # Notify customer of chargeback
    cuID = invoice.get_linked_customer_id()
    os_mail = OsMail()
    msgID = os_mail.render_email_template('payment_recurring_failed')
    os_mail.send_and_archive(msgID, cuID)


def test_webhook_invoice_chargeback():
    """
        A test can call this function to check whether everything works after a
        chargeback payment has been added to a customer payment
    """
    if not web2pytest.is_running_under_test(request, request.application):
        redirect(URL('default', 'user', args=['not_authorized']))
    else:
        iID = request.vars['iID']
        chargeback_amount = request.vars['chargeback_amount']
        chargeback_date = request.vars['chargeback_date']
        mollie_payment_id = request.vars['mollie_payment_id']
        chargeback_id = request.vars['chargeback_id']
        chargeback_details = request.vars['chargeback_details']

        print 'cb_details'
        print request.vars
        print chargeback_details

        webhook_invoice_chargeback(
            iID,
            chargeback_amount,
            chargeback_date,
            mollie_payment_id,
            chargeback_id,
            chargeback_details
        )


@auth.requires_login()
def invoice_pay():
    """
        Link to mollie payment page from invoice payment
    """
    from openstudio.os_customer import Customer

    #response.title = T("Pay invoice")
    iID = request.vars['iID']

    invoice = Invoice(iID)
    invoice_amounts = invoice.get_amounts()

    if not invoice.get_linked_customer_id() == auth.user.id:
        return 'Not authorized'

    mollie = Client()
    mollie_api_key = get_sys_property('mollie_website_profile')
    mollie.set_api_key(mollie_api_key)

    description = invoice.invoice.Description + ' - ' + invoice.invoice.InvoiceID
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
                    create_mollie_customer(auth.user.id, mollie)
                    os_customer = Customer(auth.user.id) # refresh
        else:
            create_mollie_customer(auth.user.id, mollie)
            os_customer = Customer(auth.user.id) # refresh

        mandates = os_customer.get_mollie_mandates()
        # set default recurring type, change to recurring if a valid mandate is found.
        recurring_type = 'first'
        if mandates['count'] > 0:
            # background payment
            valid_mandate = False
            for mandate in mandates['_embedded']['mandates']:
                if mandate['status'] == 'valid':
                    valid_mandate = True
                    break

            if valid_mandate:
                # Do a normal payment, probably an automatic payment failed somewhere in the process
                # and customer should pay manually now
                recurring_type = None

    # Do a regular payment or first recurring payment
    try:
        webhook_url = 'https://' + request.env.http_host + '/mollie/webhook'
        payment = mollie.payments.create({
            'amount': {
                'currency': CURRENCY,
                'value': format(invoice_amounts.TotalPriceVAT, '.2f')
            },
            'description': description,
            'sequenceType': recurring_type,
            'customerId': mollie_customer_id,
            'redirectUrl': 'https://' + request.env.http_host + '/shop/complete?iID=' + unicode(iID),
            'webhookUrl': webhook_url,
            'metadata': {
                'invoice_id': invoice.invoice.id,
                'customers_orders_id': 'invoice' # This lets the webhook function know it's dealing with an invoice
            }
        })

        db.invoices_mollie_payment_ids.insert(
            invoices_id=iID,
            mollie_payment_id=payment['id'],
            RecurringType=recurring_type,
            WebhookURL=webhook_url
        )

        # Send the customer off to complete the payment.
        redirect(payment.checkout_url)

    except MollieError as e:
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
        session.flash = T("Unable to show order")
        redirect(URL('cart'))


    mollie = Client()
    mollie_api_key = get_sys_property('mollie_website_profile')
    mollie.set_api_key(mollie_api_key)

    amounts = order.get_amounts()

    # Go to Mollie for payment
    amount = format(amounts.TotalPriceVAT, '.2f')
    description = T('Order') + ' #' + unicode(coID)

    try:
        payment = mollie.payments.create({
            'amount': {
                'currency': CURRENCY,
                'value': amount
            },
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
        redirect(payment.checkout_url)

    except MollieError as e:
        return 'API call failed: ' + e.message


def mollie_customer_check_valid(os_customer):
    """
    :param var: None
    :return: Boolean - True if there is a valid mollie customer for this OpenStudio customer
    """
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
    :param auth_user_id: db.auth_user.id
    :param mollie: mollie api client object
    :return:
    """
    from openstudio.os_customer import Customer
    os_customer = Customer(auth_user_id)

    if not mollie_customer_check_valid(os_customer):
        mollie_customer = mollie.customers.create({
            'name': os_customer.row.display_name,
            'email': os_customer.row.email
        })

        os_customer.row.mollie_customer_id = mollie_customer['id']
        os_customer.row.update_record()


@auth.requires_login()
def subscription_buy_now():
    """
        Get a subscription
    """
    from openstudio.os_customer import Customer
    from openstudio.os_invoice import Invoice
    from openstudio.os_school_subscription import SchoolSubscription
    from openstudio.os_school_membership import SchoolMembership

    ssuID = request.vars['ssuID']

    # init mollie
    mollie = Client()
    mollie_api_key = get_sys_property('mollie_website_profile')
    mollie.set_api_key(mollie_api_key)

    create_mollie_customer(auth.user.id, mollie)

    # add subscription to customer
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

    # Add accepted terms
    customer = Customer(auth.user.id)
    customer.log_subscription_terms_acceptance(ssuID)
    ssu = SchoolSubscription(ssuID, set_db_info=True)

    # Create invoice
    cs = CustomerSubscription(csID)
    iID = cs.create_invoice_for_month(startdate.year, startdate.month)

    # check membership requirements and sell if required
    if ssu.school_memberships_id and not customer.has_given_membership_on_date(ssu.school_memberships_id, TODAY_LOCAL):
        sm = SchoolMembership(ssu.school_memberships_id)
        cmID = sm.sell_to_customer(
            auth.user.id,
            TODAY_LOCAL,
            invoice=False,
            payment_methods_id=100,
        )

        # Add membership to invoice
        invoice = Invoice(iID)
        invoice.item_add_membership(cmID)

        # Log acceptance of terms
        customer.log_membership_terms_acceptance(ssu.school_memberships_id)


    # clear cache to make sure it shows in the back end
    cache_clear_customers_subscriptions(auth.user.id)

    # Pay invoice ... SHOW ME THE MONEY!! :)
    redirect(URL('invoice_pay', vars={'iID':iID}))


@auth.requires_login()
def classcard_buy_now():
    """
        Get a subscription
    """
    from openstudio.os_customer import Customer
    from openstudio.os_invoice import Invoice
    from openstudio.os_school_classcard import SchoolClasscard
    from openstudio.os_school_membership import SchoolMembership

    scdID = request.vars['scdID']

    # init mollie
    mollie = Client()
    mollie_api_key = get_sys_property('mollie_website_profile')
    mollie.set_api_key(mollie_api_key)

    # add classcard to customer
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

    # Add accepted terms
    customer = Customer(auth.user.id)
    customer.log_subscription_terms_acceptance(ssuID)
    ssu = SchoolSubscription(ssuID, set_db_info=True)

    # Create invoice
    cs = CustomerSubscription(csID)
    iID = cs.create_invoice_for_month(startdate.year, startdate.month)

    # check membership requirements and sell if required
    if ssu.school_memberships_id and not customer.has_given_membership_on_date(ssu.school_memberships_id, TODAY_LOCAL):
        sm = SchoolMembership(ssu.school_memberships_id)
        cmID = sm.sell_to_customer(
            auth.user.id,
            TODAY_LOCAL,
            invoice=False,
            payment_methods_id=100,
        )

        # Add membership to invoice
        invoice = Invoice(iID)
        invoice.item_add_membership(cmID)

        # Log acceptance of terms
        customer.log_membership_terms_acceptance(ssu.school_memberships_id)


    # clear cache to make sure it shows in the back end
    cache_clear_customers_subscriptions(auth.user.id)

    # Pay invoice ... SHOW ME THE MONEY!! :)
    redirect(URL('invoice_pay', vars={'iID':iID}))


@auth.requires_login()
def membership_buy_now():
    """
        Get a membership
    """
    from openstudio.os_customer_membership import CustomerMembership
    from openstudio.os_school_membership import SchoolMembership

    smID = request.vars['smID']

    # init mollie
    mollie = Client()
    mollie_api_key = get_sys_property('mollie_website_profile')
    mollie.set_api_key(mollie_api_key)

    # check if we have a mollie customer id
    create_mollie_customer(auth.user.id, mollie)

    # Create invoice
    sm = SchoolMembership(smID)
    cmID = sm.sell_to_customer(auth.user.id, TODAY_LOCAL)

    cm = CustomerMembership(cmID)
    iID = cm.get_linked_invoice()

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
        'amount': {
            'currency': CURRENCY,
            'value': amount
        },
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
        mollie_payment_id=payment['id'],
        WebhookURL=payment['webhookUrl']
    )

    # Send the customer off to complete the payment.
    redirect(payment.checkout_url)
