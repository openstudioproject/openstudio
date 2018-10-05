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

    return dict(content=button)


def create_customers_subscriptions_invoices_for_month():
    """

    :return:
    """
    response.title = T("Automated tasks")
    response.subtitle = T("Create customers subscriptions invoices")
    response.view = 'general/only_content.html'

    months = get_months_list()

    form = SQLFORM.factory(
        Field('month',
               requires=IS_IN_SET(months, zero=None),
               default=TODAY_LOCAL.month,
               label=T("Month")),
        Field('year', 'integer',
              default=TODAY_LOCAL.year,
              requires=IS_INT_IN_RANGE(2010, 2999),
              label=T("Year")),
        Field('description',
              label=T("Description"),
              comment=T("This will be the invoice description and shown on the customers' bank statement in case you create a collection batch.")),
        formstyle="bootstrap3_stacked",
        submit_button=T("Create invoices")
    )

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']


    if 'year' in request.vars and 'month' in request.vars:
        year = request.vars['year']
        month = request.vars['month']
        description = request.vars['description'] or ''

        print scheduler.queue_task(
            'customers_subscriptions_create_invoices_for_month',
            pvars={
                'year': year,
                'month': month,
                'description': description
            },
            stop_time=datetime.datetime.now() + datetime.timedelta(hours=1),
            last_run_time=datetime.datetime(1963, 8, 28, 14, 30),
            timeout=1800, # run for max. half an hour.
        )

        session.flash = T("Started creating customer subscription invoices... please wait")
        redirect(URL('index'))

    return dict(
        save=submit,
        content=form
    )