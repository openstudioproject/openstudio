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
        TH(T('Time')),
        TH(T('Location')),
        TH(T('Class Type')),
        TH(), #sub requested
        #TH(),  # actions
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
                TD(repr_row.classes.Starttime, '- ', repr_row.classes.Endtime),
                TD(repr_row.classes.school_locations_id),
                TD(repr_row.classes.school_classtypes_id),
                TD(sub_requested),
                #TD(button)
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

def my_claims_get_menu(page, status='not_verified'):
    pages = [
        [
            'my_claims_invoices',
            T('Credit invoices'),
            URL('my_claims_invoices')
        ]
    ]

    print status

    if ( auth.has_membership(group_id='Admins') or
         auth.has_permission('read', 'teachers_payment_classes_attendance') ):
        pages.append([ 'my_claims_classes_processed',
                       T('Processed'),
                       URL('my_claims_classes', vars={'status': 'processed'}) ])
        pages.append([ 'teacher_payment_classes_verified',
                       T('Verified'),
                       URL('my_claims_classes', vars={'status': 'verified'}) ])
        pages.append([ 'teacher_payment_classes_not_verified',
                       T('Not verified'),
                       URL('my_claims_classes', vars={'status': 'not_verified'}) ])


    return os_gui.get_submenu(pages, page, horizontal=True, htype='tabs')


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'invoices'))
def my_claims_invoices():
    """
        List teacher payments invoices by month and add button to add invoices for a
        selected month
    """
    response.title = T('Teacher payments')
    response.subtitle = T('')
    response.view = 'general/only_content_no_box.html'

    invoices = Invoices()
    status_filter = invoices.list_get_status_filter()
    list = invoices.list_invoices(only_teacher_credit_invoices=True)

    content = DIV(
        teacher_payments_get_menu(request.function),
         DIV(DIV(status_filter,
                 list,
                  _class='tab-pane active'),
             _class='tab-content'),
         _class='nav-tabs-custom')

    return dict(content=content)


# @auth.requires(auth.has_membership(group_id='Admins') or \
#                auth.has_permission('create', 'invoices'))
# def teacher_payments_generate_invoices_choose_month():
#     """
#         Choose year and month to create invoices
#     """
#     from openstudio.os_forms import OsForms
#
#     response.title = T('Teacher payments')
#     response.subtitle = T('')
#     response.view = 'general/only_content.html'
#
#     if 'year' in request.vars and 'month' in request.vars:
#         year = int(request.vars['year'])
#         month = int(request.vars['month'])
#         teacher_payments_generate_invoices(year, month)
#         redirect(URL('teacher_payments'))
#
#     os_forms = OsForms()
#     form = os_forms.get_month_year_form(
#         request.vars['year'],
#         request.vars['month'],
#         submit_button = T('Create invoices')
#     )
#
#     content = DIV(
#         H4(T('Create teacher credit invoices for month')),
#         DIV(form['form']),
#         _class='col-md-6'
#     )
#
#     back = os_gui.get_button('back', URL('teacher_payments'))
#
#     return dict(content=content,
#                 save=form['submit'],
#                 back=back)


#TODO move code from this function to integrate with attendance based payments
def my_claims_generate_invoices(year, month):
    """
        Actually generate teacher payment credit invoices
    """
    from openstudio.os_invoices import Invoices

    invoices = Invoices()
    nr_created = invoices.batch_generate_teachers_invoices(year, month)
    session.flash = SPAN(T('Created'), ' ', nr_created, ' ', T('invoice'))
    if nr_created > 1:
        session.flash.append('s')


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'teachers_payment_attendance'))
def my_claims():
    """

    :return:
    """
    from openstudio.os_teachers_payment_classes import TeachersPaymentClasses

    response.title = T('Teacher payments')
    response.subtitle = T('')
    response.view = 'ep/only_content_no_box.html'

    status = request.vars['status']

    try:
        page = int(request.args[0])
    except IndexError:
        page = 0

    tpc = TeachersPaymentClasses()

    tools = ''
    # if status == 'not_verified':
    create_permission = auth.has_membership(group_id='Admins') or \
                        auth.has_permission('create', 'my_claims_classes')
    update_permission = auth.has_membership(group_id='Admins') or \
                        auth.has_permission('update', 'my_claims_classes')

    verify_all = ''
    check_classes = ''

    if create_permission:
        verify_all = os_gui.get_button(
            'noicon',
            URL('my_claims_verify_all'),
            title=T("Verify all"),
            tooltip="Verify all listed claims",
            btn_class='btn-primary'
        )

    if update_permission:
        check_classes = os_gui.get_button(
            'noicon',
            URL('my_claims_find_caims'),
            title=T("Find claims"),
            tooltip=T("Find claims in range of dates that are not yet registered for teacher payment")
        )

    tools = DIV(
        check_classes,
        verify_all,
    )

    table = tpc.get_not_verified(
        formatted=True,

    )

    # elif status == 'verified':
    #     permission = auth.has_membership(group_id='Admins') or \
    #                  auth.has_permission('create', 'invoices')
    #
    #     if permission:
    #         links = []
    #         # Process all
    #         links.append(A(os_gui.get_fa_icon('fa-check'), T("All verified classes"),
    #                        _href=URL('my_claims_classes_process_verified'),
    #                        _title=T("Create credit invoices")))
    #         links.append('divider')
    #         # Process between dates
    #         links.append(A(os_gui.get_fa_icon('fa-calendar-o'), T('Verified classes between dates'),
    #                        _href='my_claims_classes_process_choose_dates',
    #                        _title=T("Choose which verified classes to process")))
    #
    #         tools = os_gui.get_dropdown_menu(
    #             links=links,
    #             btn_text=T('Process'),
    #             btn_size='btn-sm',
    #             btn_class='btn-primary',
    #             btn_icon='actions',
    #             menu_class='btn-group pull-right')
    #
    #     table = tpc.get_verified(
    #         formatted=True
    #     )
    #
    # elif status == 'processed':
    #     table = tpc.get_processed(
    #         formatted=True,
    #         page = page
    #     )

    content = DIV(
        # my_claims_get_menu(request.function + '_' + status, status),
        DIV(DIV(table,
                 _class='tab-pane active'),
            _class='tab-content'),
        _class='nav-tabs-custom'
    )

    return dict(
        content=content,
        header_tools=tools
    )


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('create', 'teachers_payment_classes'))
def my_claims_find_claims():
    """
    :return: None
    """
    from openstudio.os_teachers_payment_classes import TeachersPaymentClasses
    from general_helpers import set_form_id_and_get_submit_button

    response.title = T('Teacher payments')
    response.subtitle = T('Find claims')
    response.view = 'ep/only_content.html'

    # Add some explanation
    content = DIV(
        B(T("Choose a period to check for claims not yet in Not verfied, verified or processed.")), BR(), BR(),
    )

    return_url = URL('my_claims', vars={'status': 'not_verified'})

    # choose period and then do something
    form = SQLFORM.factory(
        Field('Startdate', 'date', required=True,
            requires=IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                      minimum=datetime.date(1900,1,1),
                                      maximum=datetime.date(2999,1,1)),
            represent=represent_date,
            default=datetime.date(TODAY_LOCAL.year,
                                  TODAY_LOCAL.month,
                                  1),
            label=T("Start date"),
            widget=os_datepicker_widget),
        Field('Enddate', 'date', required=False,
            requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                  minimum=datetime.date(1900,1,1),
                                  maximum=datetime.date(2999,1,1))),
            represent=represent_date,
            default=get_last_day_month(TODAY_LOCAL),
            label=T("End date"),
            widget=os_datepicker_widget),
        formstyle='bootstrap3_stacked',
        submit_button=T("Find")
    )

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']

    if form.process().accepted:
        start = form.vars.Startdate
        end = form.vars.Enddate

        tpc = TeachersPaymentClasses()
        result = tpc.check_missing(
            start,
            end
        )

        if result['error']:
            response.flash = result['message']
        else:
            session.flash = SPAN(result['message'], ' ', T("Class(es) added to Not verified"))
            redirect(return_url)

    content.append(form)

    back = os_gui.get_button('back', return_url)

    return dict(content=content,
                back=back,
                save=submit)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('update', 'teachers_payment_classes'))
def my_claims_verify_all():
    """
    Verify all not-verified classes
    :return: None
    """
    from openstudio.os_teachers_payment_classes import TeachersPaymentClasses

    tpcs = TeachersPaymentClasses()
    number_verified = tpcs.verify_all()

    if number_verified:
        session.flash = T("All not verified classes have been verified")
    else:
        session.flash = T("No classes were verified")

    redirect(URL('teacher_payment_classes', vars={'status': 'verified'}))


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('update', 'teachers_payment_classes'))
def my_claims_attendance_class_verify():
    """
    Verify attendance / payment
    :return: None
    """
    from openstudio.os_teachers_payment_class import TeachersPaymentClass

    tpcID = request.vars['tpcID']

    tpc = TeachersPaymentClass(tpcID)
    success = tpc.verify()

    if success:
        session.flash = T("Class verified")
    else:
        session.flash = T("Error verifying class")

    redirect(URL('teacher_payment_classes', vars={'status': 'verified'}))


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('update', 'teachers_payment_classes'))
def my_claims_attendance_class_unverify():
    """
    Verify attendance / payment
    :return: None
    """
    from openstudio.os_teachers_payment_class import TeachersPaymentClass

    tpcID = request.vars['tpcID']

    tpc = TeachersPaymentClass(tpcID)
    success = tpc.unverify()

    if success:
        session.flash = T("Class moved to Not verified")
    else:
        session.flash = T("Error moving class to Not verified")

    redirect(URL('teacher_payment_classes', vars={'status': 'not_verified'}))


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('create', 'invoices'))
def my_claims_classes_process_verified():
    """
    Process verified classes; create credit invoices based on verified classes
    :return:
    """
    from openstudio.os_teachers_payment_classes import TeachersPaymentClasses

    tpc = TeachersPaymentClasses()
    count_processed = tpc.process_verified()

    classes = T('classes')
    if count_processed == 1:
        classes = T("class")

    session.flash = SPAN(
        T("Processed"), ' ',
        count_processed, ' ',
        classes
    )

    redirect(URL('teacher_payment_classes', vars={'status': 'processed'}))


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('create', 'invoices'))
def my_claims_process_choose_dates():
    """
    :return: None
    """
    from openstudio.os_teachers_payment_classes import TeachersPaymentClasses
    from general_helpers import set_form_id_and_get_submit_button

    response.title = T('Teacher payments')
    response.subtitle = T('Process verified')
    response.view = 'ep/only_content.html'

    # Add some explanation
    content = DIV(
        B(T("Choose a period within which to process verified classes.")), BR(), BR(),
    )

    return_url = URL('my_claims', vars={'status': 'not_verified'})

    # choose period and then do something
    form = SQLFORM.factory(
        Field('Startdate', 'date', required=True,
            requires=IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                      minimum=datetime.date(1900,1,1),
                                      maximum=datetime.date(2999,1,1)),
            represent=represent_date,
            default=datetime.date(TODAY_LOCAL.year,
                                  TODAY_LOCAL.month,
                                  1),
            label=T("Start date"),
            widget=os_datepicker_widget),
        Field('Enddate', 'date', required=False,
            requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                  minimum=datetime.date(1900,1,1),
                                  maximum=datetime.date(2999,1,1))),
            represent=represent_date,
            default=get_last_day_month(TODAY_LOCAL),
            label=T("End date"),
            widget=os_datepicker_widget),
        formstyle='bootstrap3_stacked',
        submit_button=T("Find")
    )

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']

    if form.process().accepted:
        start = form.vars.Startdate
        end = form.vars.Enddate

        tpc = TeachersPaymentClasses()
        result = tpc.process_verified(
            start,
            end
        )

        if result['error']:
            response.flash = result['message']
        else:
            session.flash = SPAN(result['message'], ' ', T("Class(es) processed"))
            redirect(return_url)

    content.append(form)

    back = os_gui.get_button('back', return_url)

    return dict(content=content,
                back=back,
                save=submit)

