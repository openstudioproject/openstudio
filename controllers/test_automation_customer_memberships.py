# -*- coding: utf-8 -*-

from openstudio.os_scheduler_tasks import OsSchedulerTasks


@auth.requires(auth.user_id == 1)
def test_check_memberships_subscriptions():
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

    ost.customers_memberships_renew_expired(year, month)