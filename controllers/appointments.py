# coding=utf-8

@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'classes'))
def index():
    """
        Main list of classes
    """
    from general_helpers import datestr_to_python
    from openstudio.os_appointment_schedule import AppointmentSchedule
    from openstudio.os_cache_manager import OsCacheManager

    def get_day(day):
        """
            Helper function that returns a dict containing a title for the weekday,
            a date for the class and
            a SQLFORM.grid for a selected day which is within 1 - 7 (ISO standard).
        """
        # date.isocalendar()
        # Return a 3-tuple, (ISO year, ISO week number, ISO weekday).
        date = session.appointments_schedule_date + datetime.timedelta(days=day)
        print date
        # title = NRtoDay(date.isocalendar()[2])

        cs = AppointmentSchedule(
            date,
            filter_id_school_appointment = session.appointments_index_filter_appointment,
            filter_id_school_location = session.appointments_index_filter_location,
            filter_id_teacher = session.appointments_index_filter_teacher,
            sorting = session.appointments_index_sort
        )

        return cs.get_day_table()


    ocm = OsCacheManager()


    ## sort form begin ##
    if 'sort' in request.vars:
        session.appointments_index_sort = request.vars['sort']
        ocm.clear_appointments_schedule()
    elif session.appointments_index_sort is None or \
         session.appointments_index_sort == '':
        # check if we have a default value
        sys_property = 'appointments_default_sort'
        row = db.sys_properties(Property=sys_property)
        if row:
            session.appointments_index_sort = row.PropertyValue
        else:
            # default to sorting by location and then time
            session.appointments_index_sort = 'location'

    ## sort form end ##

    # if we used the jump date box to select a week
    if 'date' in request.vars:
        date = datestr_to_python(DATE_FORMAT, request.vars['date'])
    elif session.appointments_schedule_date:
        date = session.appointments_schedule_date
    else:
        date = TODAY_LOCAL

    session.appointments_schedule_date = date

    # go to date
    form_date = index_get_form_date(session.appointments_schedule_date)

    print '######## form date:'
    print form_date

    goto_today = A(T('Today'),
                     _href=URL('index_today'),
                     _class='btn btn-default full-width input-margins',
                     _id='index_today')

    # show schedule status

    ## week selection end ##

    # filter
    if 'appointment' in request.vars:
        # Clear cache
        #cache_clear_classschedule()
        # Set new values
        location = request.vars['location']
        teacher = request.vars['teacher']
        appointment = request.vars['appointment']
        status = request.vars['status']
        filter_form = index_get_filter_form(
            request.vars['location'],
            request.vars['teacher'],
            request.vars['appointment']
        )
        session.appointments_index_filter_location = location
        session.appointments_index_filter_teacher = teacher
        session.appointments_index_filter_appointment = appointment
    elif not session.appointments_index_filter_location is None:
        filter_form = index_get_filter_form(
            session.appointments_index_filter_location,
            session.appointments_index_filter_teacher,
            session.appointments_index_filter_appointment
        )
    else:
        filter_form = index_get_filter_form()
        session.appointments_index_filter_location = None
        session.appointments_index_filter_teacher = None
        session.appointments_index_filter_appointment = None

    title = T('Appointments')
    response.title = T('Appointments')
    response.subtitle = ""

    db.classes.id.readable = False
    db.classes.Week_day.readable = False
    db.classes.Maxstudents.readable = False

    # Get classes for days
    days = dict()
    for day in range(0, 7):
        days[day] = get_day(day)


    # schedule_tools = schedule_get_schedule_tools()
    # export = schedule_get_export()

    # add new class
    add = ''
    permission = auth.has_membership(group_id='Admins') or \
                 auth.has_permission('create', 'appointments')

    if permission:
        add = os_gui.get_button(
            'add',
            URL('add'),
            tooltip=T("Add a new appointment"),
            _class='pull-right'
        )


    return dict(filter_form=filter_form,
                title=title,
                add=add,
                # schedule_tools=schedule_tools,
                # export=export,
                days=days,
                week_chooser=index_get_week_chooser(),
                goto_today=goto_today,
                # day_chooser=day_chooser,
                form_date=form_date,
                )


def schedule_get_query(weekday, date):
    """
        Returns the default query for the schedule workshops check
    """
    return (db.classes.Week_day == weekday) & \
           (db.classes.Startdate <= date) & \
           ((db.classes.Enddate >= date) |
            (db.classes.Enddate == None)) # can't use is here, query doesn't work


def index_get_form_date(date):
    """
        Returns a form to jump to a date
    """
    form_date = SQLFORM.factory(
                Field('date', 'date',
                      requires=IS_DATE_IN_RANGE(
                                format=DATE_FORMAT,
                                minimum=datetime.date(1900,1,1),
                                maximum=datetime.date(2999,1,1)),
                      default=date,
                      label=T(""),
                      widget=os_datepicker_widget_small),
                submit_button=T('Go'),
                )

    submit = form_date.element('input[type=submit]')
    submit['_class'] = 'full-width'

    form_date = DIV(form_date.custom.begin,
                    DIV(form_date.custom.widget.date,
                        DIV(form_date.custom.submit,
                            _class='input-group-btn'),
                        _class='input-group'),
                    form_date.custom.end,
                    _class='form_inline',
                    _id='form_date')

    return form_date


def index_set_date():
    """
    Set appointments schedule date
    """
    from general_helpers import datestr_to_python
    date_formatted = request.vars['date']

    session.appointments_schedule_date = datestr_to_python(DATE_FORMAT, request.vars['date'])

    redirect(URL('index'))


def index_get_week_chooser(var=None):
    """
        Returns a week chooser for the schedule
    """
    date = session.appointments_schedule_date
    delta = datetime.timedelta(days=7)

    prev_week = (date - delta).strftime(DATE_FORMAT)
    next_week = (date + delta).strftime(DATE_FORMAT)

    previous = A(I(_class='fa fa-angle-left'),
                 _href=URL('index_set_date', vars={ 'date': prev_week }),
                 _class='btn btn-default')
    nxt = A(I(_class='fa fa-angle-right'),
            _href=URL('index_set_date', vars={ 'date': next_week }),
            _class='btn btn-default')

    return DIV(previous, nxt, _class='btn-group', _id='schedule_week_chooser')


def schedule_get_schedule_tools(var=None):
    """
        Returns tools for schedule
    """
    schedule_tools = []

    # teacher holidays
    permission = auth.has_membership(group_id='Admins') or \
                 auth.has_permission('read', 'teacher_holidays')

    if permission:
        teacher_holidays = A(os_gui.get_fa_icon('fa-sun-o'),
                             T("Staff holidays"),
                             _href=URL('schedule', 'staff_holidays'),
                             _title=T('Open classes & shifts in a range of dates'))
        schedule_tools.append(teacher_holidays)

    # Set default sorting
    permission = auth.has_membership(group_id='Admins') or \
                 auth.has_permission('update', 'schedule_set_default_sort')
    if permission:
        set_default_sorting = A(os_gui.get_fa_icon('fa-sort-amount-asc'), ' ',
                                T('Set default sorting'),
                                _href=URL('schedule_set_sort_default'),
                                _title=T('Set default sorting for classes'))
        schedule_tools.append(set_default_sorting)

    # Set trend percentages
    permission = auth.has_membership(group_id='Admins') or \
                 auth.has_permission('update', 'classes_schedule_set_trend_precentages')
    if permission:
        set_trend_percentages = A(os_gui.get_fa_icon('fa-percent'), ' ',
                                  T('Set trend colors'),
                                  _href=URL('schedule_set_trend_percentages'),
                                  _title=T('Set percentage colors for trend column'))
        schedule_tools.append(set_trend_percentages)




    # get menu
    tools = os_gui.get_dropdown_menu(schedule_tools,
                                     '',
                                     btn_size='btn-sm',
                                     btn_icon='wrench',
                                     menu_class='pull-right'
                                     )

    return tools


def schedule_get_export(var=None):
    """
        Returns export drop down for schedule
    """
    export_locations = A(os_gui.get_fa_icon('fa-calendar'), T("Schedule"),
                          _href=URL('schedule_export_excel',
                                    vars=dict(year=session.schedule_year,
                                              week=session.schedule_week,
                                              export='locations')))

    links = [ export_locations ]

    export = os_gui.get_dropdown_menu(
        links = links,
        btn_text = '',
        btn_size = 'btn-sm',
        btn_icon = 'download',
        menu_class='pull-right')
    
    return export


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'appointments'))
def index_today():
    """
    Reset date chooser for schedule
    """
    session.appointments_schedule_date = TODAY_LOCAL
    redirect(URL('index'))


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'classes'))
def _schedule_clear_filter():
    session.appointments_index_filter_location = None
    session.appointments_index_filter_teacher = None
    session.appointments_index_filter_appointment = None
    session.appointments_index_filter_level = None
    session.appointments_index_filter_status = None

    #cache_clear_classschedule()

    redirect(URL('schedule'))


def index_get_filter_form(school_locations_id='',
                             teachers_id='',
                             school_appointment_id='',
                             school_levels_id='',
                             status=''):

    sa_query = (db.school_appointments.Archived == False)
    slo_query = (db.school_locations.Archived == False)

    au_query = (db.auth_user.teacher == True) & \
               (db.auth_user.trashed == False)

    form = SQLFORM.factory(
        Field('location',
            requires=IS_IN_DB(db(slo_query),'school_locations.id', '%(Name)s',
                              zero=T('All locations')),
            default=school_locations_id,
            label=""),
        Field('teacher',
            requires=IS_IN_DB(db(au_query),'auth_user.id',
                              '%(full_name)s',
                              zero=T('All teachers')),
            default=teachers_id,
            label=""),
        Field('appointment',
            requires=IS_IN_DB(db(sa_query),'school_appointments.id', '%(Name)s',
                              zero=T('All appointment types')),
            default=school_appointment_id,
            label=""),
        submit_button=T('Filter'),
        formstyle='divs',
        )

    # sumbit form on change
    selects = form.elements('select')
    for select in selects:
        select.attributes['_onchange'] = "this.form.submit();"

    clear = A(T("Clear"), _class="btn btn-default",
                _href=URL('_schedule_clear_filter'),
                _title=T("Reset filter to default"))

    div = DIV(
        form.custom.begin,
        DIV(form.custom.widget.location,
            _class='col-md-3'),
        DIV(form.custom.widget.teacher,
            _class='col-md-3'),
        DIV(form.custom.widget.appointment,
            _class='col-md-3'),
        DIV(DIV(form.custom.submit,
                clear,
                _class="pull-right"),
            _class='col-md-3'),
        form.custom.end,
        _id="schedule_filter_form")

    return div


@auth.requires(auth.has_membership(group_id='Admins') or \
                auth.has_permission('read', 'classes'))
def schedule_export_excel():
    iso_year = request.vars['year']
    iso_week = request.vars['week']
    export = request.vars['export']


    def get_cell_id(col, row):
        """
            Returns cell id for colums / row
        """
        col_letter = openpyxl.utils.get_column_letter(col)
        return col_letter + unicode(row)


    def writer_location(locID=None):
        """
        This helper function writes the locations schedule
        """
        teachers_dict = create_teachers_dict()
        locations_dict = create_locations_dict()
        appointments_dict = create_appointments_dict()

        for day in range(1,8):
            date = iso_to_gregorian(iso_year, iso_week, day)
            col = day
            dayname = NRtoDay(day)
            c_id = get_cell_id(col, 2)
            ws[c_id] = dayname + " \n" + unicode(date)
            ws[c_id].alignment = alignment

            cs = ClassSchedule(
                date,
                filter_id_school_location = locID
            )

            rows = cs.get_day_rows()

            r = 3
            for i, row in enumerate(rows):
                repr_row = list(rows[i:i + 1].render())[0]

                clsID = row.classes.id

                location = repr_row.classes.school_locations_id
                appointment = repr_row.classes.school_appointment_id
                teacher = repr_row.classes_teachers.auth_teacher_id
                teacher2 = repr_row.classes_teachers.auth_teacher_id2
                class_data = ''
                if row.classes_otc.Status == 'cancelled':
                    class_data += T("CANCELLED") + "\n"

                time = repr_row.classes.Starttime + " - " + repr_row.classes.Endtime
                if locID is None:
                    class_data += location.decode('utf-8') + "\n" + \
                                  time + " \n" + \
                                  appointment.decode('utf-8') + " \n" + \
                                  teacher.decode('utf-8') + " \n" + \
                                  teacher2.decode('utf-8') + " \n"
                else:
                    class_data += time + " \n" + \
                                  appointment.decode('utf-8') + " \n" + \
                                  teacher.decode('utf-8') + " \n" + \
                                  teacher2.decode('utf-8') + " \n"
                c_id = get_cell_id(col, r)
                ws[c_id] = class_data
                ws[c_id].font = font
                ws[c_id].alignment = alignment
                r += 1

    # Set some general values
    font = openpyxl.styles.Font(size=10)
    alignment = openpyxl.styles.Alignment(wrap_text=True,
                                          shrink_to_fit=True,
                                          vertical='top')

    if export == 'locations':
        # Full schedule
        wb = openpyxl.workbook.Workbook()
        title = "ALL"
        ws = wb.active
        ws.title = title
        ws['A1'] = T("Schedule week") + " " + unicode(iso_week)
        writer_location()
        # schedule by location
        rows = db().select(db.school_locations.id,
                           db.school_locations.Name,
                           orderby=db.school_locations.Name)
        for row in rows:
            location = locations_dict.get(row.id, None)
            title = location.decode('utf-8')[0:30]
            ws = wb.create_sheet(title=title)
            ws['A1'] = "Schedule" + " " + title + " " + \
                       "week " + unicode(iso_week)
            writer_location(row.id)

        # create filestream
        stream = cStringIO.StringIO()

        fname = T("Schedule") + '.xlsx'
        wb.save(stream)
        response.headers['Content-Type']='application/vnd.ms-excel'
        response.headers['Content-disposition']='attachment; filename=' + fname

        return stream.getvalue()


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('create', 'appointments'))
def add():
    """
    First page shown in series to add an appointment. This page will ask the user
    if a single or recurring appointment should be scheduled
    """
    response.title = T("Add a new appointment")
    response.subtitle = T("")
    response.view = 'general/tabs_menu.html'

    arrow_right = SPAN(os_gui.get_fa_icon('fa-angle-right '), _class='pull-right')

    content = DIV(
        H4(T("What kind of appointment would you like to schedule?")),
        DIV(A(arrow_right,
              B(os_gui.get_fa_icon('fa-arrow-circle-o-down'), ' ', T("One time")), BR(),
              T("Schedule a single appointment on a specific date"),
              _href=URL('add_one_time'),
              _class="list-group-item"),
            A(arrow_right,
              B(os_gui.get_fa_icon('fa-refresh'), ' ', T("Weekly recurring")), BR(),
              T("Schedule an appointment that appears every week on the same day & time"),
              _href=URL('add_recurriing'),
              _class="list-group-item"),
            _class='list-group'
        )
    )

    back = os_gui.get_button('back', URL('index'))


    return dict(content = content,
                back = back,
                menu = add_get_menu(request.function))



@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('create', 'appointments'))
def add_one_time():
    """
    Second page shown in series to add an appointment. This page will ask the user
    if a single or recurring appointment should be scheduled
    """
    from openstudio.os_forms import OsForms

    response.title = T("Add a new appointment")
    response.subtitle = T("")
    response.view = 'general/tabs_menu.html'

    db.schedule.FrequencyType.default = 'specific'
    db.schedule.Startdate.label = T("Date")
    db.schedule.Enddate.readable = False
    db.schedule.Enddate.writable = False

    return_url = URL('index')

    os_forms = OsForms()
    result = os_forms.get_crud_form_create(
        db.schedule,
        return_url,
    )
    form = result['form']

    content = DIV(
        H4(T("Add one time appointment")),
        form
    )

    back = os_gui.get_button('back', URL('add'))

    return dict(content = content,
                back = back,
                menu = add_get_menu("add_2"))



def add_get_menu(page):
    """
        Returns submenu for adding a workshop
    """
    from openstudio.os_gui import OsGui
    os_gui = OsGui()

    pages = [
        ['add', T('1. Choose Frequency'), "#"],
        ['add_2', T('2. Set details'), "#"],
    ]

    return os_gui.get_submenu(pages, page, horizontal=True, htype='tabs')

