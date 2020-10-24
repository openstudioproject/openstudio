# -*- coding: utf-8 -*-

from openstudio.os_scheduler_tasks import OsSchedulerTasks


@auth.requires(auth.user_id == 1)
def test_create_invoices():
    """
    Function to expose class & method used by scheduler task
    to create monthly invoices
    """
    if ( not web2pytest.is_running_under_test(request, request.application)
         and not auth.has_membership(group_id='Admins') ):
        redirect(URL('default', 'user', args=['not_authorized']))


    ost = OsSchedulerTasks()

    year = request.vars['year']
    month = request.vars['month']
    description = request.vars['description']
    invoice_date = request.vars['invoice_date'] or 'today'

    return ost.customers_subscriptions_create_invoices_for_month(year, month, description, invoice_date)


@auth.requires(auth.user_id == 1)
def test_add_subscription_credits_for_month():
    """
    Function to expose class & method used by scheduler task
    to add subscription credits for a given month
    """
    if ( not web2pytest.is_running_under_test(request, request.application)
         and not auth.has_membership(group_id='Admins') ):
        redirect(URL('default', 'user', args=['not_authorized']))


    ost = OsSchedulerTasks()

    year = request.vars['year']
    month = request.vars['month']

    return ost.customers_subscriptions_add_credits_for_month(year, month)