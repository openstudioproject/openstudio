# -*- coding: utf-8 -*-

from general_helpers import max_string_length
from general_helpers import set_form_id_and_get_submit_button

@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'automated_tasks'))
def index():
    """
        Lists automated tasks
    """
    response.title = T("Automation")
    response.subtitle = T("Customer subscriptions")
    response.view = 'general/only_content.html'

    header = THEAD(TR(
        TH(T("Task")),
        TH(T("Run results")),
        TH(), #Actions
    ))

    table = TABLE(header, _class='table table-striped table-hover')

    table = index_get_month_invoices(table)
    table = index_get_currnet_month_mollie_recurring(table)


    return dict(content=table)


def index_get_currnet_month_mollie_recurring(table):
    """
    :param table:
    :return: table appended with current month recurring Mollie payments
    """
    import json

    permission = (auth.has_membership(group_id='Admins') or
                  auth.has_permission('create', 'invoices'))

    if permission:
        run = os_gui.get_button(
            'noicon',
            URL('collect_mollie_recurring_payments_current_month'),
            title=T("Collect payments"),
            tooltip=T("Collect payments for this month"),
            btn_class='btn-primary',
            _class='pull-right',
            btn_size=''
        )

        left = [
            db.scheduler_run.on(
                db.scheduler_task.id ==
                db.scheduler_run.task_id
            )
        ]

        query = (db.scheduler_task.task_name == 'customers_subscriptions_collect_mollie_recurring_current_month')
        rows = db(query).select(
            db.scheduler_task.ALL,
            db.scheduler_run.ALL,
            left=left,
            orderby=~db.scheduler_task.start_time,
            limitby=(0,3)
        )

        result_table = TABLE(_class='table-condensed automated-tasks-results')
        for row in rows:
            vars = json.loads(row.scheduler_task.vars)
            vars_display = DIV()

            for v in sorted(vars):
                vars_display.append(DIV(
                    B(v.capitalize() + ': '),
                    vars[v]
                ))

            run_result = row.scheduler_run.run_result or ''


            result_table.append(TR(
                TD(B(T("Start"), ': '),
                   pytz.utc.localize(row.scheduler_task.start_time).astimezone(pytz.timezone(TIMEZONE)).strftime(DATETIME_FORMAT), BR(),
                   vars_display),
                TD(row.scheduler_run.status or T("Pending...")),
                TD(XML(run_result.replace('"', ''))),
            ))

        tr = TR(
            TD(T("Collect recurring Mollie payments for subscriptions (this month)")),
            TD(result_table),
            TD(run)
        )

        table.append(tr)

    return table


def index_get_month_invoices(table):
    """
    :return:
    """
    import json

    permission = (auth.has_membership(group_id='Admins') or
                  auth.has_permission('create', 'invoices'))

    if permission:
        run = os_gui.get_button(
            'noicon',
            URL('create_invoices_for_month'),
            title=T("Create invoices"),
            tooltip=T("Select month for which to create invoices"),
            btn_class='btn-primary',
            _class='pull-right',
            btn_size=''
        )

        left = [
            db.scheduler_run.on(
                db.scheduler_task.id ==
                db.scheduler_run.task_id
            )
        ]

        query = (db.scheduler_task.task_name == 'customers_subscriptions_create_invoices_for_month')
        rows = db(query).select(
            db.scheduler_task.ALL,
            db.scheduler_run.ALL,
            left=left,
            orderby=~db.scheduler_task.start_time,
            limitby=(0,3)
        )

        result_table = TABLE(_class='table-condensed automated-tasks-results')
        for row in rows:
            vars = json.loads(row.scheduler_task.vars)
            vars_display = DIV()

            for v in sorted(vars):
                vars_display.append(DIV(
                    B(v.capitalize() + ': '),
                    vars[v]
                ))

            run_result = row.scheduler_run.run_result or ''

            result_table.append(TR(
                TD(B(T("Start"), ': '),
                   pytz.utc.localize(row.scheduler_task.start_time).astimezone(pytz.timezone(TIMEZONE)).strftime(DATETIME_FORMAT), BR(),
                   vars_display),
                TD(row.scheduler_run.status or T("Pending...")),
                TD(XML(run_result.replace('"', ''))),
            ))

        tr = TR(
            TD(T("Create customer subscription invoices for month")),
            TD(result_table),
            TD(run)
        )

        table.append(tr)

    return table


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('create', 'invoices'))
def create_invoices_for_month():
    """

    :return:
    """
    response.title = T("Automation")
    response.subtitle = T("Customer subscriptions - create invoices for month")
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
              comment=T(
                  "This will be the invoice description and shown on the customers' " + \
                  "bank statement in case you create a collection batch. " + \
                  "When an alt. price has been added for this month, this description will be used for that subscription.")),
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

        scheduler.queue_task(
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

        session.flash = SPAN(
            T("Started creating customer subscription invoices... "),
            T("please refresh this page in a few minutes."), BR(),
            T("Please note that you can continue to work on other things in the meantime and you don't have to wait on this page.")
        )
        redirect(URL('index'))


    back = os_gui.get_button('back', URL('index'))

    return dict(
        save=submit,
        content=form,
        back=back,
    )


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('create', 'invoices'))
def collect_mollie_recurring_payments_current_month():
    """

    :return:
    """
    scheduler.queue_task(
        'customers_subscriptions_collect_mollie_recurring_current_month',
        stop_time=datetime.datetime.now() + datetime.timedelta(hours=1),
        last_run_time=datetime.datetime(1963, 8, 28, 14, 30),
        timeout=1800, # run for max. half an hour.
    )

    session.flash = SPAN(
        T("Started collecting customer subscription recurring payments using Mollie... "),
        T("please refresh this page in a few minutes."), BR(),
        T("Please note that you can continue to work on other things in the meantime and you don't have to wait on this page.")
    )

    redirect(URL('index'))
