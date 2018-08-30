# -*- coding: utf-8 -*-
# this file is released under the gplv2 (or later at your choice) license

#########################################################################
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

from general_helpers import datestr_to_python
from general_helpers import get_label
from general_helpers import get_submenu
from general_helpers import get_months_list
from general_helpers import get_last_day_month
from general_helpers import User_helpers
from general_helpers import class_get_teachers
from general_helpers import max_string_length
from general_helpers import set_form_id_and_get_submit_button

from gluon.tools import prettydate

from openstudio.os_class import Class
from openstudio.os_class_schedule import ClassSchedule


import datetime

# helpers start


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'employee_portal'))
@auth.requires_login()
def index():
    """
        Employee Portal page, a quick overview of today
    """
    response.title = T("Employee Portal")
    response.subtitle = T('Welcome ') +auth.user.display_name

    # upcoming classes (for teachers)
    upcoming_classes = ep_index_teacher_upcoming_classes()

    # Classes that are open to substitute
    sub_classes = ep_index_teacher_sub_classes()

    content = DIV(
        DIV(upcoming_classes,_class='col-md-12'),
        DIV(sub_classes,_class='col-md-12'),
        _class='row'
    )

    return dict(content=content)


#TODO: Move to os_teacher (after merge)
def ep_index_teacher_upcoming_classes(days=3):
    """
        @return: List upcoming classes for a teacher
    """
    from openstudio.os_teacher import Teacher

    if auth.user.id and auth.user.teacher:
        teachers_id = auth.user.id
        cache_clear_classschedule()
    else:
        return ''

    teacher = Teacher(auth.user.id)


    return teacher.get_upcoming_classes_formatted(days)


#TODO: move to os_teacher for use in pinboard and here.
@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'employee_portal'))
def ep_index_teacher_sub_classes():
    """
        @return: List classes that need to get subbed
    """
    from openstudio.os_teacher import Teacher

    if auth.user.id and auth.user.teacher:
        teachers_id = auth.user.id
        cache_clear_classschedule()
    else:
        return ''

    session.ep_available_for_sub_back = 'ep_index'

    teacher = Teacher(auth.user.id)

    return teacher.get_subrequests_formatted()


def available_for_sub_get_return_url(var=None):
    """
    See if we're coming from pinboard, if so, go back there, otherwise back to ep
    """
    if session.ep_available_for_sub_back == 'pinboard_index':
        url = URL('pinboard', 'index')
    else:
        url = URL('ep', 'index')

    return url


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'employee_portal'))
def available_for_sub():
    """
    Add class and teacher to classes_oct_sub_avail table
    """
    cotcID = request.vars['cotcID']
    teachers_id = auth.user.id

    row = db.classes_otc_sub_avail(
        classes_otc_id=cotcID,
        auth_teacher_id=teachers_id
    )
    if not row:
        db.classes_otc_sub_avail.insert(
            classes_otc_id=cotcID,
            auth_teacher_id=teachers_id
        )


    redirect(available_for_sub_get_return_url())


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'employee_portal'))
def cancel_available_for_sub():
    """
    Remove entry from classes_otc_sub_avail
    """
    cotcsaID = request.vars['cotcsaID']

    query = (db.classes_otc_sub_avail.id == cotcsaID)
    db(query).delete()

    redirect(available_for_sub_get_return_url())


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'employee_portal'))
def my_classes():
    """
    creates page that displays the classes tought montlhy
    :return:
    """
    response.title = T("My classes")
    response.subtitle = T("")
    response.view = 'ep/only_content.html'

    if session.ep_my_classes_month is None or session.ep_my_classes_year is None:
        session.ep_my_classes_year = TODAY_LOCAL.year
        session.ep_my_classes_month = TODAY_LOCAL.month

    table = TABLE(_class='table table-hover')
    table.append(THEAD(TR(
        TH(),
        TH(T('Date')),
        TH(T('Start')),
        TH(T('Location')),
        TH(T('Class Type')),
        TH(),  # actions))
    )))

    date = datetime.date(
        session.ep_my_classes_year,
        session.ep_my_classes_month,
        1
    )
    last_day = get_last_day_month(date)

    for each_day in range(1, last_day.day + 1):
        # list days
        day = datetime.date(session.ep_my_classes_year,
                            session.ep_my_classes_month,
                            each_day)

        class_schedule = ClassSchedule(
            date=day,
            filter_id_teacher=auth.user.id
        )

        rows = class_schedule.get_day_rows()
        for i, row in enumerate(rows):
            repr_row = list(rows[i:i + 1].render())[0]

            result = class_schedule._get_day_row_status(row)
            status_marker = result['marker']

            open_class = db.classes_otc(
                classes_id=row.classes.id,
                ClassDate=day,
                Status='open'
            )

            if not open_class:
                sub_requested = ""
                button = os_gui.get_button('noicon',
                                           URL('request_sub',
                                               vars={'clsID': row.classes.id,
                                                     'date': day,
                                                     'teachers_id': auth.user.id}),
                                           title='Find sub', _class='pull-right', btn_class='btn-success')
            else:
                sub_requested = os_gui.get_label('primary', T("Sub requested"))
                button = os_gui.get_button('noicon',
                                           URL('cancel_request_sub',
                                               vars={'cotcID': open_class.id}),
                                           title='Cancel', _class='pull-right', btn_class='btn-warning')
            tr = TR(
                TD(status_marker,
                   _class='td_status_marker'),
                TD(day.strftime(DATE_FORMAT)),
                TD(repr_row.classes.Starttime),
                TD(repr_row.classes.Endtime),
                TD(repr_row.classes.school_locations_id),
                TD(repr_row.classes.school_classtypes_id),
                TD(sub_requested),
                TD(button)
            )

            table.append(tr)

    form_subtitle = get_form_subtitle(session.ep_my_classes_month,
                                      session.ep_my_classes_year,
                                      request.function,
                                      _class='col-md-8')
    response.subtitle = form_subtitle['subtitle']
    month_chooser = form_subtitle['month_chooser']
    current_month = form_subtitle['current_month']

    response.subtitle = form_subtitle['subtitle']

    header_tools = month_chooser + current_month
    return dict(
        header_tools=header_tools,
        content=table
    )


def get_form_subtitle(month=None, year=None, function=None, _class='col-md-4'):
    months = get_months_list()
    subtitle = ''
    if year and month:
        for m in months:
            if m[0] == month:
                month_title = m[1]
        subtitle = month_title + " " + unicode(year)
    else:
        year = TODAY_LOCAL.year
        month = TODAY_LOCAL.month

    form = SQLFORM.factory(
        Field('month',
              requires=IS_IN_SET(months, zero=None),
              default=month,
              label=T("")),
        Field('year', 'integer',
              default=year,
              label=T("")),
        submit_button=T("Run report")
    )
    form.attributes['_name'] = 'form_select_date'
    form.attributes['_class'] = 'overview_form_select_date'

    input_month = form.element('select[name=month]')
    # input_month.attributes['_onchange'] = "this.form.submit();"

    input_year = form.element('input[name=year]')
    # input_year.attributes['_onchange'] = "this.form.submit();"
    input_year.attributes['_type'] = 'number'
    # input_year.attributes['_class']    = 'input_margins'

    form.element('input[name=year]')

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']

    ## Show current
    url_current_month = URL('my_classes_show_current')
    show_current_month = A(T("Current month"),
                           _href=url_current_month,
                           _class='btn btn-default')
    month_chooser = ''
    if not function == 'attendance_classes':
        month_chooser = overview_get_month_chooser(function)

    form = DIV(XML('<form id="MainForm" action="#" enctype="multipart/form-data" method="post">'),
               DIV(form.custom.widget.month,
                   form.custom.widget.year,
                   _class=_class),
               form.custom.end,
               _class='row')

    return dict(
        form=form,
        subtitle=subtitle,
        month_chooser=month_chooser,
        current_month=show_current_month,
        submit=submit
    )


def get_month_subtitle(month, year):
    """
    :param month: int 1 - 12
    :return: subtitle
    """
    months = get_months_list()
    subtitle = ''
    if year and month:
        for m in months:
            if m[0] == month:
                month_title = m[1]
        subtitle = month_title + " " + unicode(year)

    return subtitle


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'employee_portal'))
def my_classes_set_month():
    """
        Sets the session variables for teacher_classes year and month
    """
    year  = request.vars['year']
    month = request.vars['month']
    back  = request.vars['back']

    session.ep_my_classes_year = int(year)
    session.ep_my_classes_month = int(month)

    redirect(URL(back))


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'employee_portal'))
def my_classes_show_current():
    """
        Resets some session variables to show the current month for
        teacher_classes
    """
    session.ep_my_classes_year = None
    session.ep_my_classes_month = None
    back = request.vars['back']

    redirect(URL('my_classes'))


def overview_get_month_chooser(page):
    """
        Returns month chooser for overview
    """

    year  = session.ep_my_classes_year
    month = session.ep_my_classes_month

    link = 'my_classes_set_month'


    if month == 1:
        prev_month = 12
        prev_year  = year - 1
    else:
        prev_month = month - 1
        prev_year  = year

    if month == 12:
        next_month = 1
        next_year  = year + 1
    else:
        next_month = month + 1
        next_year  = year

    url_prev = URL(link, vars={'month':prev_month,
                               'year' :prev_year,
                               'back' :page})

    url_next = URL(link, vars={'month':next_month,
                                  'year' :next_year,
                                  'back' :page})

    previous = A(I(_class='fa fa-angle-left'),
                 _href=url_prev,
                 _class='btn btn-default')
    nxt = A(I(_class='fa fa-angle-right'),
            _href=url_next,
            _class='btn btn-default')

    return DIV(previous, nxt, _class='btn-group pull-right')


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'employee_portal'))
def request_sub():
    clsID = request.vars['clsID']
    date = request.vars ['date']
    teachers_id = request.vars['teachers_id']
    row_classes= db.classes(id=clsID)

    row = db.classes_otc(classes_id=clsID,
                         ClassDate = date)
    if not row:
        db.classes_otc.insert(
            classes_id = clsID,
            ClassDate = date,
            Status = 'open',
        )
    else:
        row.Status='open'
        row.update_record()

    redirect(URL('my_classes'))


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'employee_portal'))
def cancel_request_sub():
    """
    Cancel request for sub teacher
    """
    cotcID = request.vars['cotcID']
    row = db.classes_otc(cotcID)

    if (row.school_classtypes_id or
        row.school_classtypes_id or
        row.Starttime or
        row.Endtime or
        row.auth_teacher_id or
        row.teacher_role or
        row.auth_teacher_id2 or
        row.teacher_role2 or
        row.MaxOnlineBooking or
        row.Maxstudents
    ):
        row.Status = None
        row.update_record()
    else:
        query = (db.classes_otc.id==row.id)
        db(query).delete()

    session.flash = T("Cancelled request for sub teacher.")
    redirect(URL('my_classes'))


@auth.requires_login()
def my_payments():
    """
        List staff payments
    """
    response.title = T('My Payments')
    response.view = 'ep/only_content.html'

    if auth.user.teacher == False and auth.user.employee == False:
        redirect(URL('ep', 'index'))

    content = my_payments_get_content()

    return dict(content=content)


def my_payments_get_content(var=None):
    """

    :param var:
    :return:
    """
    from openstudio.os_customer import Customer

    customer = Customer(auth.user.id)
    rows = customer.get_invoices_rows(
        public_group=False,
        payments_only=True
    )

    header = THEAD(TR(
        TH(T('Invoice #')),
        TH(T('Date')),
        TH(T('Due')),
        TH(T('Amount')),
        TH(T('Status')),
        TH(),
    ))

    table = TABLE(header, _class='table table-striped table-hover')

    for i, row in enumerate(rows):
        repr_row = list(rows[i:i + 1].render())[0]

        pdf = os_gui.get_button(
            'print',
            URL('invoices', 'pdf',
                vars={'iID': row.invoices.id}),
            btn_size='',
            _class='pull-right'
        )

        table.append(TR(
            TD(row.invoices.InvoiceID),
            TD(repr_row.invoices.DateCreated),
            TD(repr_row.invoices.DateDue),
            TD(repr_row.invoices_amounts.TotalPriceVAT),
            TD(repr_row.invoices.Status),
            TD(pdf)
        ))

    return table
