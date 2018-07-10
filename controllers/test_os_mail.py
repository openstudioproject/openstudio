# coding: utf8

from openstudio.os_mail import OsMail
from openstudio.os_workshops_helper import WorkshopsHelper


def test_osmail_render_template():
    """
        function to be used when testing rendering of OsMail messages
    """
    if not web2pytest.is_running_under_test(request, request.application) and not auth.has_membership(group_id='Admins'):
        redirect(URL('default', 'user', args=['not_authorized']))

    email_template = request.vars['email_template']
    invoices_id = request.vars['invoices_id']
    customers_orders_id = request.vars['customers_orders_id']
    invoices_payments_id = request.vars['invoices_payments_id']

    os_mail = OsMail()
    rendered_message = T('template not found...')
    if email_template == 'email_template_payment_recurring_failed':
        #TODO: write test

        pass
    elif email_template == 'email_template_order_received' or email_template == 'email_template_order_delivered':
        rendered_message = os_mail.render_email_template(
            email_template,
            customers_orders_id = customers_orders_id,
            return_html = True
        )
    elif email_template == 'email_template_sys_reset_password':
        rendered_message = os_mail.render_email_template(email_template,
                                                         return_html = True)

    return rendered_message


def test_osmail_render_sys_notification():
    """
        function to be used when testing rendering of OsMail messages
    """
    if not web2pytest.is_running_under_test(request, request.application) and not auth.has_membership(group_id='Admins'):
        redirect(URL('default', 'user', args=['not_authorized']))

    sys_notification = request.vars['sys_notification']
    invoices_id = request.vars['invoices_id']
    customers_orders_id = request.vars['customers_orders_id']
    invoices_payments_id = request.vars['invoices_payments_id']

    os_mail = OsMail()
    rendered_message = T('notification not found...')
    if sys_notification == 'order_created':
        rendered_message = os_mail.render_sys_notification(
            sys_notification,
            customers_orders_id=customers_orders_id
        )

    return rendered_message


