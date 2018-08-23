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
               auth.has_permission('read', 'ep'))
def index():
    '''
        Employee Portal page, a quick overview of today
    '''
    response.title = T("Employee Portal")
    response.subtitle = T('Welcome ') +auth.user.display_name

    print response.menu

    # welcome_message = ''
    # if ( db.sys_properties(Property='ShowWelcomeMessage') is None or
    #      db.sys_properties(Property='ShowWelcomeMessage').PropertyValue == 'on'):
    #     welcome_message = DIV(DIV(DIV(H3(T('Welcome to OpenStudio'), _class="box-title"),
    #                                DIV(A(I(_class='fa fa-times'),
    #                                      _href=URL('hide_welcome'),
    #                                      _class='btn btn-box-tool',
    #                                      _title=T("Hide this message")),
    #                                    _class='box-tools pull-right'),
    #                                _class='box-header with-border'),
    #                            DIV(_generate_welcome_message(),
    #                                _class='box-body'),
    #                            _class='box box-info'),
    #                         _class='col-md-12')

    # cancelled classes
    cancelled_classes = ep_get_cancelled_classes()


    # upcoming classes (for teachers)
    upcoming_classes = ep_get_teacher_upcoming_classes()

    # Classes that are open to substitute
    substitution_classes = ep_get_teacher_substitution_classes()




    content = DIV(
        # DIV(welcome_message, _class='row'),
                  DIV(DIV( upcoming_classes,_class='col-md-9'),
                      DIV(substitution_classes,_class='col-md-9'),
                      DIV(cancelled_classes,_class='col-md-9') ,

                      _class='row'))

    return dict(content=content)




def ep_get_teacher_upcoming_classes(days=3):
    '''
        @return: List upcoming classes for a teacher
    '''
    if auth.user.id and auth.user.teacher:
        teachers_id = auth.user.id
        cache_clear_classschedule()
    else:
        return ''

    attendance_permission = (auth.has_membership(group_id='Admins') or \
                             auth.has_permission('update', 'classes_attendance'))

    date = datetime.date.today()
    delta = datetime.timedelta(days=1)

    header = THEAD(TR(TH(T('Class date')),
                      TH(T('Time')),
                      TH(T('Location')),
                      TH(T('Class type')),
                      TH(T('Teacher')),
                      TH(T('Teacher2')),
                      TH(),
                      ))

    table = TABLE(header, _class='table table-hover dataTable')


    for day in range(0, days):
        cs = ClassSchedule(
            date,
            filter_id_teacher=teachers_id)

        rows = cs.get_day_rows()
        for i, row in enumerate(rows):
            if row.classes_otc.Status == 'cancelled' or row.school_holidays.id:
                continue

            repr_row = list(rows[i:i + 1].render())[0]

            result = cs._get_day_row_teacher_roles(row, repr_row)

            teacher = result['teacher_role']
            teacher2 = result['teacher_role2']

            attendance = ''
            if attendance_permission:
                # attendance = A(T('Attendance'),
                #                _href=URL('classes', 'attendance', vars={'clsID':row.classes.id,
                #                                                         'date':date.strftime(DATE_FORMAT)}))
                attendance = os_gui.get_button('noicon', URL('classes', 'attendance',
                                                           vars={'clsID':row.classes.id,
                                                                 'date':date.strftime(DATE_FORMAT)}),
                                               title=T('Attendance'),
                                               _class=T('pull-right'))

            tr = TR(TD(date.strftime(DATE_FORMAT), _class='bold green' if day == 0 else ''),
                    TD(repr_row.classes.Starttime, ' - ', repr_row.classes.Endtime),
                    TD(repr_row.classes.school_locations_id),
                    TD(repr_row.classes.school_classtypes_id),
                    TD(teacher),
                    TD(teacher2),
                    TD(attendance)
                    )

            table.append(tr)


        date += delta

    upcoming_classes = DIV(DIV(H3(T('My upcoming classes'), _class="box-title"),
                               DIV(A(I(_class='fa fa-minus'),
                                     _href='#',
                                     _class='btn btn-box-tool',
                                     _title=T("Collapse"),
                                     **{'_data-widget': 'collapse'}),
                                   _class='box-tools pull-right'),
                               _class='box-header with-border'),
                               DIV(table, _class='box-body'),
                          _class='box box-success')

    return upcoming_classes


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'pinboard'))
def ep_get_teacher_substitution_classes():
    '''
        @return: List classes that need to get subbed
    '''
    if auth.user.id and auth.user.teacher:
        teachers_id = auth.user.id
        cache_clear_classschedule()
    else:
        return ''



    header = THEAD(TR(TH(T('Class date')),
                      TH(T('Time')),
                      TH(T('Location')),
                      TH(T('Class type')),
                      TH(),
                      ))

    table = TABLE(header, _class='table table-hover dataTable')

    query = (db.teachers_classtypes.auth_user_id==teachers_id)
    rows = db(query).select(db.teachers_classtypes.school_classtypes_id)
    ctIDs= [ row.school_classtypes_id for row in rows]



    left = [
        db.classes.on(
            db.classes_otc.classes_id == db.classes.id,

        ),
        db.classes_teachers.on(
            db.classes_teachers.classes_id == db.classes.id
        )

    ]


    query = ((db.classes_otc.Status=='Open') &\
             (db.classes_otc.school_classtypes_id.belongs(ctIDs)) &\
             (db.classes_otc.auth_teacher_id != teachers_id) & \
             (db.classes_otc.ClassDate >= db.classes_teachers.Startdate) & \
             (db.classes_otc.ClassDate <= db.classes_teachers.Enddate) & \
             (db.classes_otc.classes_id == db.classes_teachers.classes_id) & \
             (db.classes_teachers.auth_teacher_id != teachers_id))



    rows=db(query).select(
        db.classes_otc.ALL,
        left=left,
        orderby= db.classes.id
    )


    for i, row in enumerate(rows):
        repr_row = list(rows[i:i + 1].render())[0]


        row_avail=db.classes_otc_sub_avail(classes_otc_id=row.id, auth_user_id = teachers_id)

        if not row_avail:
            button = os_gui.get_button('astronaut',
                                      URL('available_for_sub',
                                          vars={'clsID': row.id, 'teachers_id':teachers_id}),
                                      title='Available', _class='pull-right', btn_class='btn-success')
        else:
            button = os_gui.get_button('astronaut',
                                      URL('cancel_available_for_sub',
                                          vars={'clsID': row.id, 'teachers_id':teachers_id}),
                                      title='Cancel', _class='pull-right', btn_class='btn-warning')
        tr = TR(TD(repr_row.ClassDate),
                TD(repr_row.Starttime, ' - ', repr_row.Endtime),
                TD(repr_row.school_locations_id),
                TD(repr_row.school_classtypes_id),
                TD(button)
                )
        table.append(tr)
    if not len(rows):
        table = TABLE(TD("At the moment no substitution required!"),_class='table table-hover dataTable')

    upcoming_classes = DIV(DIV(H3(T('Substitute Teacher Requested'), _class="box-title"),
                               DIV(A(I(_class='fa fa-minus'),
                                     _href='#',
                                     _class='btn btn-box-tool',
                                     _title=T("Collapse"),
                                     **{'_data-widget': 'collapse'}),
                                   _class='box-tools pull-right'),
                               _class='box-header with-border'),
                               DIV(table, _class='box-body'),
                          _class='box box-success')

    return upcoming_classes


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'pinboard'))
def available_for_sub():
    '''
    adds class and teacher to classes_oct_sub_avail table
    :return:
    '''
    clsID = request.vars['clsID']
    teachers_id = request.vars['teachers_id']

    row = db.classes_otc_sub_avail(id=clsID, auth_user_id=teachers_id )
    if not row:
        db.classes_otc_sub_avail.insert(classes_otc_id=clsID,
                              auth_user_id=teachers_id)
        redirect(URL('index'))
    redirect(URL('index'))


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'pinboard'))
def cancel_available_for_sub():
    clsID = request.vars['clsID']
    teachers_id = request.vars['teachers_id']
    row = db.classes_otc_sub_avail(classes_otc_id=clsID, auth_user_id=teachers_id)
    print row
    if row:
        db(db.classes_otc_sub_avail.id==row.id).delete()
        redirect(URL('index'))
    redirect(URL('index'))


def ep_get_cancelled_classes(days=3):
    '''
    :return: list of cancelled classes
    '''
    today = TODAY_LOCAL

    delta =  datetime.timedelta(days=days)
    query = ((db.classes_otc.ClassDate >= today) &
             (db.classes_otc.ClassDate <= (today + delta)) &
             (db.classes_otc.Status == 'cancelled'))
    rows = db(query).select(db.classes_otc.classes_id,
                            db.classes_otc.ClassDate,
                            db.school_locations.Name,
                            db.school_classtypes.Name,
                            db.classes.Starttime,
                            orderby=db.classes_otc.ClassDate|\
                                    ~db.classes.school_locations_id|\
                                    db.classes.Starttime,
        left = [db.classes.on(db.classes_otc.classes_id==db.classes.id),
                db.school_locations.on(db.classes.school_locations_id==\
                                       db.school_locations.id),
                db.school_classtypes.on(db.classes.school_classtypes_id==\
                                        db.school_classtypes.id)],
        cache = (cache.ram, 30)
        )

    # don't do anything of there are no cancelled classes
    if rows.first() is None:
        return ''


    cancelled_classes = DIV(H3(T("Cancelled classes")))
    goto = []
    thead = THEAD(TR(TH(T('Date')),
                     TH(T('Time')),
                     TH(T('Location')),
                     TH(T('Class type'))))
    tbody = TBODY()
    for row in rows:
        class_date = row.classes_otc.ClassDate
        date_formatted = class_date.strftime(DATE_FORMAT)
        clsID = row.classes_otc.classes_id

        tr = TR(
            TD(date_formatted),
            TD(row.classes.Starttime.strftime('%H:%M')),
            TD(row.school_locations.Name),
            TD(row.school_classtypes.Name)
        )

        tbody.append(tr)

    table = TABLE(thead, tbody, _class='table table-hover')

    classes = DIV(DIV(H3(T('Cancelled classes'), _class="box-title"),
                               DIV(A(I(_class='fa fa-minus'),
                                     _href='#',
                                     _class='btn btn-box-tool',
                                     _title=T("Collapse"),
                                     **{'_data-widget': 'collapse'}),
                                   _class='box-tools pull-right'),
                               _class='box-header with-border'),
                               DIV(table, _class='box-body'),
                          _class='box box-warning')

    return classes

@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'pinboard'))
def my_classes():
    '''
    creates page that displays the classes tought montlhy
    :return:
    '''
    response.title = T("My Monthly Classes")
    response.subtitle = T("")
    response.view = 'ep/only_content.html'


    if 'month' in request.vars:
        session.reports_te_classes_month = int(request.vars['month'])
        session.reports_te_classes_year = int(request.vars['year'])
    elif session.reports_te_classes_month is None or \
            session.reports_te_classes_year is None:
        today = datetime.date.today()
        session.reports_te_classes_year = today.year
        session.reports_te_classes_month = today.month

    if auth.user.id and auth.user.teacher:
        teachers_id = auth.user.id
        cache_clear_classschedule()


        table = TABLE(_class='table table-hover')


        table.append(THEAD(TR(
            TH(),
            TH(T('Date')),
            TH(T('Start')),
            TH(T('End')),
            TH(T('Location')),
            TH(T('Class Type')),
            TH(),  # actions))
        )))

        date = datetime.date(session.reports_te_classes_year,
                             session.reports_te_classes_month, 5)
        last_day = get_last_day_month(date)



        for each_day in range(1, last_day.day + 1):
            # list days
            day = datetime.date(session.reports_te_classes_year,
                                session.reports_te_classes_month, each_day)
            weekday = day.isoweekday()

            class_schedule = ClassSchedule(
                date=day,
                filter_id_teacher=teachers_id
            )

            rows = class_schedule.get_day_rows()

            for i, row in enumerate(rows):
                repr_row = list(rows[i:i + 1].render())[0]

                result = class_schedule._get_day_row_status(row)
                status_marker = result['marker']



                date_formatted = day.strftime(DATE_FORMAT)
                open_class = db.classes_otc(classes_id=row.classes.id,  ClassDate=date_formatted, Status = 'Open')
                if not open_class:
                    sub_requested = ""
                    button= os_gui.get_button('astronaut',
                                         URL( 'request_sub',
                                             vars={'clsID': row.classes.id,
                                                   'date': date_formatted,
                                                   'teachers_id':teachers_id}),
                                         title='Find sub', _class='pull-right', btn_class='btn-success')
                else:
                    sub_requested= os_gui.get_label('primary', T("Sub requested"))
                    button= os_gui.get_button('astronaut',
                                         URL('cancel_request_sub',
                                             vars={'clsID': row.classes.id,
                                                                            'date': date_formatted}),
                                         title='Cancel', _class='pull-right', btn_class='btn-warning')
                tr = TR(
                    TD(status_marker,
                       _class='td_status_marker'),
                    TD(date_formatted),
                    TD(repr_row.classes.Starttime),
                    TD(repr_row.classes.Endtime),
                    TD(repr_row.classes.school_locations_id),
                    TD(repr_row.classes.school_classtypes_id),
                    TD(sub_requested),
                    TD(button)
                )

                table.append(tr)

    else:
        table = ''
    form_subtitle = get_form_subtitle(session.reports_te_classes_month,
                                      session.reports_te_classes_year,
                                      request.function,
                                      _class='col-md-8')
    response.subtitle = form_subtitle['subtitle']
    month_chooser = form_subtitle['month_chooser']
    current_month = form_subtitle['current_month']

    response.subtitle = SPAN(T('Classes'), ' ',
                             form_subtitle['subtitle'])

    header_tools = month_chooser + current_month
    return dict(
                header_tools=header_tools,
                content=table,
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
    url_current_month = URL('teacher_classes_show_current')
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


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'pinboard'))
def teacher_classes_set_month():
    """
        Sets the session variables for teacher_classes year and month
    """
    year  = request.vars['year']
    month = request.vars['month']
    back  = request.vars['back']

    session.reports_te_classes_year = int(year)
    session.reports_te_classes_month = int(month)

    redirect(URL(back))


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'pinboard'))
def teacher_classes_show_current():
    """
        Resets some session variables to show the current month for
        teacher_classes
    """
    session.reports_te_classes_year = None
    session.reports_te_classes_month = None
    back = request.vars['back']

    redirect(URL('teacher_monthly_classes'))


def overview_get_month_chooser(page):
    """
        Returns month chooser for overview
    """

    year  = session.reports_te_classes_year
    month = session.reports_te_classes_month

    link = 'teacher_classes_set_month'


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


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'pinboard'))
def request_sub():
    clsID = request.vars['clsID']
    date = request.vars ['date']
    teachers_id = request.vars['teachers_id']
    row_classes= db.classes(id=clsID)

    row = db.classes_otc(classes_id=clsID,
                         ClassDate = date
                         )
    if not row:
        db.classes_otc.insert(classes_id = clsID,
                              ClassDate=date,
                              Status ='Open',
                              Starttime= row_classes.Starttime,
                              Endtime= row_classes.Endtime,
                              school_locations_id=row_classes.school_locations_id,
                              school_classtypes_id= row_classes.school_classtypes_id,
                              auth_teacher_id=teachers_id)
        redirect(URL('my_classes'))\


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'pinboard'))
def cancel_request_sub():
    clsID = request.vars['clsID']
    date = request.vars ['date']
    row = db.classes_otc(classes_id=clsID, ClassDate = date)
    if row:
        db(db.classes_otc.id==row.id).delete()
        redirect(URL('my_classes'))