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
    response.subtitle = T("Customer class cards")
    response.view = 'general/only_content.html'

    header = THEAD(TR(
        TH(T("Task")),
        TH(T("Run results")),
        TH(), #Actions
    ))

    table = TABLE(header, _class='table table-striped table-hover')

    table = index_get_extend_validity(table)



    return dict(content=table)


def index_get_extend_validity(table):
    """
    :param var:
    :return:
    """
    import json

    permission = (auth.has_membership(group_id='Admins') or
                  auth.has_permission('update', 'customers_classcards'))

    if permission:
        run = os_gui.get_button(
            'noicon',
            URL('extend_validity'),
            title=T("Extend validity"),
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

        query = (db.scheduler_task.task_name == 'customers_classcards_extend_validity')
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
            TD(T("Bulk extend class card validity")),
            TD(result_table),
            TD(run)
        )

        table.append(tr)

    return table


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('create', 'invoices'))
def extend_validity():
    """

    :return:
    """
    response.title = T("Automation")
    response.subtitle = T("Customer class cards - bulk extend validity")
    response.view = 'general/only_content.html'

    months = get_months_list()

    form = SQLFORM.factory(
        Field('valid_on',
              requires=IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                        minimum=datetime.date(1900, 1, 1),
                                        maximum=datetime.date(2999, 1, 1)),
               default=TODAY_LOCAL,
               label=T("For cards valid on")),
        Field('days_to_add', 'integer',
              default=1,
              requires=IS_INT_IN_RANGE(1, 5000),
              label=T("Extend the validity with the following number of days to add")),
        formstyle="bootstrap3_stacked",
        submit_button=T("Extend validity")
    )

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']


    if 'valid_on' in request.vars and 'days_to_add' in request.vars:
        valid_on = request.vars['valid_on']
        days_to_add = request.vars['days_to_add']

        scheduler.queue_task(
            'customers_classcards_extend_validity',
            pvars={
                'valid_on': valid_on,
                'days_to_add': days_to_add
            },
            stop_time=datetime.datetime.now() + datetime.timedelta(hours=1),
            last_run_time=datetime.datetime(1963, 8, 28, 14, 30),
            timeout=1800, # run for max. half an hour.
        )

        session.flash = SPAN(
            T("Started extending selected class cards... "),
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