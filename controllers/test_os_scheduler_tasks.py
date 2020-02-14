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
    return ost.email_teachers_sub_requests_daily_summary()


@auth.requires(auth.has_membership(group_id='Admins'))
def email_reminders_teachers_sub_request_open():
    """
    Function to test sending reminders to teachers forclasses
    where they requestest a subteacher, which hasn't been found yet.
    :return:
    """
    if ( not web2pytest.is_running_under_test(request, request.application)
         and not auth.has_membership(group_id='Admins') ):
        redirect(URL('default', 'user', args=['not_authorized']))

    ost = OsSchedulerTasks()
    return ost.email_reminders_teachers_sub_request_open()


@auth.requires(auth.has_membership(group_id='Admins'))
def email_trailclass_follow_up():
    """
    Function to test sending follow up emails the day after a trial class
    :return:
    """
    if ( not web2pytest.is_running_under_test(request, request.application)
         and not auth.has_membership(group_id='Admins') ):
        redirect(URL('default', 'user', args=['not_authorized']))

    ost = OsSchedulerTasks()
    return ost.email_trailclass_follow_up()


@auth.requires(auth.has_membership(group_id='Admins'))
def email_trailcard_follow_up():
    """
    Function to test sending follow up emails the day after a trial class
    :return:
    """
    if ( not web2pytest.is_running_under_test(request, request.application)
         and not auth.has_membership(group_id='Admins') ):
        redirect(URL('default', 'user', args=['not_authorized']))

    ost = OsSchedulerTasks()
    return ost.email_trailcard_follow_up()