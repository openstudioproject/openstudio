# -*- coding: utf-8 -*-

from openstudio.os_scheduler_tasks import OsSchedulerTasks


@auth.requires(auth.has_membership(group_id='Admins'))
def email_teachers_sub_requests_daily_summary():
    """
    Function to expose class & method used by scheduler task
    to create send a daily summary available classes for subbing
    """
    if ( not web2pytest.is_running_under_test(request, request.application)
         and not auth.has_membership(group_id='Admins') ):
        redirect(URL('default', 'user', args=['not_authorized']))


    ost = OsSchedulerTasks()
    ost.email_teachers_sub_requests_daily_summary()