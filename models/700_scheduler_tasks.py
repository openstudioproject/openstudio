# # -*- coding: utf-8 -*-

import datetime
import Mollie

from openstudio.os_customer_subscription import CustomerSubscription
from openstudio.os_invoice import Invoice
from openstudio.os_mail import OsMail
from openstudio.os_scheduler_tasks import OsSchedulerTasks


def task_openstudio_daily():
    """
        Daily tasks for OpenStudio
    """
    today = datetime.date.today()
    if today.day == 1:
        _task_mollie_subscription_invoices_and_payments()

    return 'Daily task - OK'


def task_openstudio_test():
    """
        test scheduler
    """
    return 'Test task - OK'


def _task_mollie_subscription_invoices_and_payments():
    """
        Create subscription invoices for subscriptions with payment method 100
        Collect payment for these invoices
    """
    def send_mail_failed(cuID):
        """
            When a recurring payment fails, mail customer with request to pay manually
        """
        os_mail = OsMail()
        msgID = os_mail.render_email_template('email_template_payment_recurring_failed')
        os_mail.send(msgID, cuID)

    from openstudio.os_customer import Customer

    # hostname
    sys_hostname = get_sys_property('sys_hostname')
    # set up Mollie
    mollie = Mollie.API.Client()
    mollie_api_key = get_sys_property('mollie_website_profile')
    mollie.setApiKey(mollie_api_key)
    # set dates
    today = datetime.date.today()
    firstdaythismonth = datetime.date(today.year, today.month, 1)
    lastdaythismonth = get_last_day_month(firstdaythismonth)

    # call some function to do stuff

    # find all active subscriptions with payment method 100 (Mollie)
    query = (db.customers_subscriptions.payment_methods_id == 100) & \
            (db.customers_subscriptions.Startdate <= lastdaythismonth) & \
            ((db.customers_subscriptions.Enddate >= firstdaythismonth) |
             (db.customers_subscriptions.Enddate == None))
    rows = db(query).select(db.customers_subscriptions.ALL)

    # create invoices
    for i, row in enumerate(rows):
        cs = CustomerSubscription(row.id)
        # This function returns the invoice id if it already exists
        iID = cs.create_invoice_for_month(TODAY_LOCAL.year, TODAY_LOCAL.month)

        #print 'invoice created'
        #print iID

        # Do we have an invoice?
        if not iID:
            continue

        invoice = Invoice(iID)
        # Only do something if the invoice status is sent
        if not invoice.invoice.Status == 'sent':
            continue

        # We're good, continue processing
        invoice_amounts = invoice.get_amounts()
        #print invoice.invoice.InvoiceID
        description = invoice.invoice.Description + ' - ' + invoice.invoice.InvoiceID
        db.commit()

        #create recurring payments using mandates
        #subscription invoice
        customer = Customer(row.auth_customer_id)
        mollie_customer_id = customer.row.mollie_customer_id
        mandates = customer.get_mollie_mandates()
        valid_mandate = False
        # set default recurring type, change to recurring if a valid mandate is found.
        if mandates['count'] > 0:
            # background payment
            for mandate in mandates:
                if mandate['status'] == 'valid':
                    valid_mandate = True
                    break

            if valid_mandate:
                # Create recurring payment
                try:
                    webhook_url = URL('mollie', 'webhook', scheme='https', host=sys_hostname)
                    payment = mollie.payments.create({
                        'amount': invoice_amounts.TotalPriceVAT,
                        'customerId': mollie_customer_id,
                        'recurringType': 'recurring',  # important
                        'description': description,
                        'webhookUrl': webhook_url,
                        'metadata': {
                            'invoice_id': invoice.invoice.id,
                            'customers_orders_id': 'invoice' # This lets the webhook function know it's dealing with an invoice
                        }
                    })

                    # link invoice to mollie_payment_id
                    db.invoices_mollie_payment_ids.insert(
                        invoices_id=invoice.invoice.id,
                        mollie_payment_id=payment['id'],
                        RecurringType=payment['recurringType'],
                        WebhookURL=webhook_url
                    )

                except Mollie.API.Error as e:
                    print e
                    # send mail to ask customer to pay manually
                    send_mail_failed(cs.auth_customer_id)
                    # return error
                    # return 'API call failed: ' + e.message
        else:
            # send mail to ask customer to pay manually
            send_mail_failed(cs.auth_customer_id)

    # For scheduled tasks, db has to be committed manually
    db.commit()


def scheduler_task_test():
    return 'success!'


os_scheduler_tasks = OsSchedulerTasks()


scheduler_tasks = {
    'daily': task_openstudio_daily,
    'customers_subscriptions_create_invoices_for_month': os_scheduler_tasks.customers_subscriptions_create_invoices_for_month,
    'customers_exp_membership_check_subscriptions': os_scheduler_tasks.customers_exp_membership_check_subscriptions,
    'openstudio_test_task': task_openstudio_test
}