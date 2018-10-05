# -*- coding: utf-8 -*-

from general_helpers import max_string_length
from general_helpers import set_form_id_and_get_submit_button

@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'automated_tasks'))
def index():
    """
        Lists automated tasks
    """
    response.title = T("Automated tasks")
    response.subtitle = T("")
    response.view = 'general/only_content.html'

    button = os_gui.get_button(
        'noicon',
        URL('create_customers_subscriptions_invoices_for_month'),
        title=T("Create customers subscriptions invoices")
    )

    return dict()


def create_customers_subscriptions_invoices_for_month():
    """

    :return:
    """
    response.title = T("Automated tasks")
    response.subtitle = T("Create customers subscriptions invoices")
    response.view = 'general/only_content.html'



    if 'year' in request.vars and 'month' in request.vars:
        scheduler.queue_task(
            'customers_subscriptions_create_invoices_for_month',
            pvars={'year': 2018, 'month': 12},
            timeout=300,
            immediate=True
        )

        session.flash = T("Started creating customer subscription invoices... please wait")
        redirect(URL('index'))

    return dict(content='hello world')