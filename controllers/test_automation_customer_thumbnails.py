# -*- coding: utf-8 -*-

from openstudio.os_scheduler_tasks import OsSchedulerTasks


@auth.requires(auth.user_id == 1)
def test_recreate_customer_thumbnails():
    """
    Function to expose class & method used by scheduler task
    to recreate customer thumbnails
    """
    if ( not web2pytest.is_running_under_test(request, request.application)
         and not auth.has_membership(group_id='Admins') ):
        redirect(URL('default', 'user', args=['not_authorized']))


    ost = OsSchedulerTasks()
    return ost.recreate_customer_thumbnails()

