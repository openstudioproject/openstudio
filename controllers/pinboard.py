# -*- coding: utf-8 -*-


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

@auth.requires_login()
def _generate_welcome_message():
    message = DIV(T("Quick start: first add subscriptions, class types and locations \
        in the"), " ", A(T("school properties"), _href=URL('school_properties', 'index')), " ", T("pages"), ".",
        BR(),
        T("Then add"), " ", A(T("teachers"), _href=URL('school_properties', 'teachers')), " ",  T("and after that add"), " ",
        A(T("classes"), _href=URL('classes', 'schedule')), " " , T("to the schedule"), ". ",
        T("Now you're ready to start adding"), " ", A(T("customers"), _href=URL('customers', 'index')), ". ",
        BR(),
        T("If you have any questions, please have a look at the"), " ", A(T("manual"), _href='http://www.openstudioproject.com/content/manual', _target="_blank")," ",
        ".", BR(),
        T("When using OpenStudio for the first time, please have look at the"), " ",
        A(T("license"), _href=URL('about', 'about')), ".",
        BR())

    return message

# helpers end


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'pinboard'))
def hide_welcome():
    row = db.sys_properties(Property='ShowWelcomeMessage')
    if row:
        row.PropertyValue='off'
        row.update_record()
    else:
        db.sys_properties.insert(Property='ShowWelcomeMessage', PropertyValue='off')

    # Clear cache
    cache_clear_sys_properties()

    redirect(URL('index'))


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'pinboard'))
def index():
    """
        Pinboard page, a quick overview of today
    """
    response.title = T("Pinboard")
    response.subtitle = T("")

    session.customers_back = 'pinboard'
    session.workshops_manage_back = 'pinboard'
    session.ep_available_for_sub_back = 'pinboard_index'

    welcome_message = ''
    if ( db.sys_properties(Property='ShowWelcomeMessage') is None or
         db.sys_properties(Property='ShowWelcomeMessage').PropertyValue == 'on'):
        welcome_message = DIV(DIV(DIV(H3(T('Welcome to OpenStudio'), _class="box-title"),
                                   DIV(A(I(_class='fa fa-times'),
                                         _href=URL('hide_welcome'),
                                         _class='btn btn-box-tool',
                                         _title=T("Hide this message")),
                                       _class='box-tools pull-right'),
                                   _class='box-header with-border'),
                               DIV(_generate_welcome_message(),
                                   _class='box-body'),
                               _class='box box-info'),
                            _class='col-md-12')

    # cancelled classes
    cancelled_classes = pinboard_get_cancelled_classes()

    # Announcements (shown at top)
    announcements = ''
    permission = auth.has_membership(group_id='Admins') or \
                  auth.has_permission('read', 'announcements')
    if permission:
        announcements = pinboard_get_announcements()

    # tasks
    tasks = pinboard_get_tasks()

    # upcoming classes (for teachers)
    upcoming_classes = pinboard_get_teacher_upcoming_classes()

    # Classes that are open to substitute
    sub_classes = pinboard_get_teacher_sub_classes()


    # birthdays
    birthdays = get_birthdays()

    content = DIV(DIV(welcome_message, _class='row'),
                  DIV(DIV(announcements, upcoming_classes,sub_classes, tasks, cancelled_classes, _class='col-md-9'),
                      DIV(birthdays, _class='col-md-3'),
                      _class='row'))

    return dict(content=content)


def pinboard_get_tasks(var=None):
    """
        Add todays and tomorrow's tasks to the pinboard
    """
    tasks = ''
    permission = (auth.has_membership(group_id='Admins') or
                  auth.has_permission('read', 'tasks'))

    if permission:
        tasks = DIV(LOAD('tasks', 'list_tasks_today.load',
                             vars=request.vars,
                             content=os_gui.get_ajax_loader()))

    return tasks


def pinboard_get_teacher_sub_classes(var=None):
    """
    Returns list of classes available for subbing
    """
    from openstudio.os_teacher import Teacher

    if auth.user.id and auth.user.teacher:
        teachers_id = auth.user.id
        cache_clear_classschedule()
    else:
        return ''

    teacher = Teacher(auth.user.id)

    return teacher.get_subrequests_formatted()


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'pinboard'))
def pinboard_get_announcements(var=None):
    """
        Announcements for pinboard in a nice list
    """
    today = datetime.date.today()
    query = (db.announcements.Visible == True) & \
            (db.announcements.Startdate <= today) & \
            ((db.announcements.Enddate >= today) | \
             (db.announcements.Enddate == None))

    rows = db(query).select(db.announcements.ALL,
                            orderby=~db.announcements.Startdate|\
                            db.announcements.Priority|\
                            db.announcements.Title)

    body = DIV(_class='box-body')
    if len(rows):

        for row in rows:
            body.append(DIV(
                H4(row.Title),
                row.Note))

    announcements = DIV(DIV(H3(T('Announcements'), _class="box-title"),
                            DIV(A(I(_class='fa fa-pencil'),
                                  _href=URL('announcements', 'index'),
                                  _class='btn btn-box-tool',
                                  _title=T("Edit announcements")),
                                A(I(_class='fa fa-minus'),
                                  _href='#',
                                  _class='btn btn-box-tool',
                                  _title=T("Collapse"),
                                  **{'_data-widget': 'collapse'}),
                                _class='box-tools pull-right'),
                            _class='box-header with-border'),
                         body,
                       _class='box box-primary')

    return announcements


def get_birthdays(var=None):
    db.auth_user.birthday.represent=lambda value, row: value.strftime("%B %d") if value else ''

    today = datetime.date.today()
    if today.month == 2 and today.day == 29:
        day = 28
    else:
        day = today.day
    birthday_check = datetime.date(1900, today.month, day)

    edit_permission = (auth.has_membership(group_id='Admins') or
                       auth.has_permission('update', 'auth_user'))

    query = (db.auth_user.trashed == False) & \
            (db.auth_user.customer == True) & \
            (db.auth_user.birthday >= birthday_check) & \
            (db.auth_user.birthday <= birthday_check + datetime.timedelta(days=7))
    rows = db(query).select(db.auth_user.id,
                            db.auth_user.display_name,
                            db.auth_user.birthday,
                            orderby=db.auth_user.birthday,
                            cache=(cache.ram, 300))
    table = TABLE(_class='full-width')
    for row in rows.render():
        if edit_permission:
            customer = A(row.display_name,
                         _href=URL('customers', 'edit', args=[row.id]))
        else:
            customer = B(row.display_name)

        table.append(TR(TD(row.birthday,
                           _class='os-date_month_name'),
                        TD(customer)))


    table_customers = table

    query = (db.auth_user.teacher == True) &\
            (db.auth_user.birthday >= birthday_check) & \
            (db.auth_user.birthday <= birthday_check +
                                     datetime.timedelta(days=7))
    teacher_rows = db(query).select(db.auth_user.id,
                                    db.auth_user.display_name,
                                    db.auth_user.birthday,
                                    orderby=db.auth_user.birthday,
                                    cache=(cache.ram, 300))

    table = TABLE(_class='full-width')
    for row in teacher_rows.render():
        if edit_permission:
            customer = A(row.display_name,
                         _href=URL('customers', 'edit', args=[row.id]))
        else:
            customer = B(row.display_name)

        table.append(TR(TD(row.birthday,
                           _class='os-date_month_name'),
                        TD(customer)))
    table_teachers = table


    birthdays = DIV(DIV(H3(T('Birthdays this week'), _class="box-title"),
                               DIV(A(I(_class='fa fa-minus'),
                                     _href='#',
                                     _class='btn btn-box-tool',
                                     _title=T("Collapse"),
                                     **{'_data-widget': 'collapse'}),
                                   _class='box-tools pull-right'),
                               _class='box-header with-border'),
                          _class='box box-info')

    body = DIV(table_customers, _class='box-body')

    if not teacher_rows.first() is None:
        body.append(H4(T("Teachers")))
        body.append(table_teachers)

    birthdays.append(body)

    return birthdays


def pinboard_get_teacher_upcoming_classes(days=3):
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

  
def pinboard_get_cancelled_classes(days=3):
    """
    :return: list of cancelled classes
    """
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


def get_form_subtitle(month=None, year=None, function=None, _class='col-md-4'):
    months = get_months_list()
    subtitle = ''
    if year and month:
        for m in months:
            if m[0] == month:
                month_title = m[1]
        subtitle = month_title + " " + str(year)
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

  