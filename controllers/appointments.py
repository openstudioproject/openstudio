# coding=utf-8

@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'classes'))
def index():
    """
        Main list of classes
    """
    def get_day(date, trend_medium, trend_high):
        """
            Helper function that returns a dict containing a title for the weekday,
            a date for the class and
            a SQLFORM.grid for a selected day which is within 1 - 7 (ISO standard).
        """
        title = NRtoDay(weekday)
        date_formatted = date.strftime(DATE_FORMAT)

        cs = ClassSchedule(
            date,
            filter_id_school_appointment = session.appointmetns_index_filter_appointment,
            filter_id_school_location = session.appointmetns_index_filter_location,
            filter_id_teacher = session.appointmetns_index_filter_teacher,
            sorting = session.appointments_index_sort
        )

        return cs.get_day_table()


    ## sort form begin ##
    if 'sort' in request.vars:
        session.appointments_index_sort = request.vars['sort']
        #cache_clear_classschedule()
    elif session.appointments_index_sort is None or \
         session.appointments_index_sort == '':
        # check if we have a default value
        sys_property = 'appointments_default_sort'
        row = db.sys_properties(Property=sys_property)
        if row:
            session.appointments_index_sort = row.PropertyValue
        else:
            # default to sorting by location
            session.appointments_index_sort = 'location'

    ## sort form end ##

    if not session.schedule_show_date is None:
        date = datestr_to_python(DATE_FORMAT, session.schedule_show_date)
        year = date.year
        week = date.isocalendar()[1]
        session.schedule_show_date = None

    # if we used the jump date box to select a week
    if 'appointments_date' in request.vars:
        jump_date = datestr_to_python(DATE_FORMAT,
                                      request.vars['appointments_date'])
        jump_date_iso = jump_date.isocalendar()
        year = jump_date_iso[0]
        week = jump_date_iso[1]
        session.schedule_year = year
        session.schedule_week = week
    else:
        jump_date = datetime.date.today()

    # jump to date
    form_jump = schedule_get_form_jump(jump_date)

    current_week = A(T('Current week'),
                     _href=URL('index_current_week'),
                     _class='btn btn-default full-width input-margins',
                     _id='index_current_week')

    # show schedule status
    week_chooser = index_get_week_chooser()

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
        filter_form = schedule_get_filter_form(
            request.vars['location'],
            request.vars['teacher'],
            request.vars['appointment']
        )
        session.appointmetns_index_filter_location = location
        session.appointmetns_index_filter_teacher = teacher
        session.appointmetns_index_filter_appointment = appointment
    elif not session.appointmetns_index_filter_location is None:
        filter_form = schedule_get_filter_form(
            session.appointmetns_index_filter_location,
            session.appointmetns_index_filter_teacher,
            session.appointmetns_index_filter_appointment
        )
    else:
        filter_form = schedule_get_filter_form()
        session.appointmetns_index_filter_location = None
        session.appointmetns_index_filter_teacher = None
        session.appointmetns_index_filter_appointment = None

    title = T('Appointments')
    response.title = T('Appointments')
    response.subtitle = ""

    db.classes.id.readable = False
    db.classes.Week_day.readable = False
    db.classes.Maxstudents.readable = False

    # Get trend percentages here, so they don't have to be loaded for each day, if permission is granted
    trend_medium = ''
    trend_high = ''
    if (auth.has_membership(group_id='Admins') or
        auth.has_permission('read', 'classes_schedule_set_trend_precentages')):
        trend_medium = get_sys_property('classes_schedule_trend_medium', int)
        trend_high = get_sys_property('classes_schedule_trend_high', int)

    # Get classes for days
    days = dict()
    for day in range(1, 8):
        days[day] = get_day(day, trend_medium, trend_high)

    overlapping_workshops = ''
    if ( auth.has_membership(group_id='Admins') or
         auth.has_permission('update', 'workshops_activities') ):
        overlapping_workshops = DIV(
            LOAD('classes', 'schedule_get_overlapping_workshops.load',
                 vars={'year':year, 'week':week},
                 ajax=True,
                 content=''),
        _class='inline-block pull-right')

    schedule_tools = schedule_get_schedule_tools()
    export = schedule_get_export()

    # add new class
    add = ''
    permission = auth.has_membership(group_id='Admins') or \
                 auth.has_permission('create', 'classes')

    if permission:
        add = os_gui.get_button('add',
                URL('class_add'),
                tooltip=T("Add a new class"),
                _class='pull-right')


    return dict(filter_form=filter_form,
                year=year,
                title=title,
                add=add,
                schedule_tools=schedule_tools,
                export=export,
                overlapping_workshops=overlapping_workshops,
                days=days,
                schedule_status=schedule_status,
                week_chooser=week_chooser,
                current_week=current_week,
                day_chooser=day_chooser,
                form_jump=form_jump,
                form_week=form_week,
                form_year=form_year,
                )


def schedule_get_query(weekday, date):
    """
        Returns the default query for the schedule workshops check
    """
    return (db.classes.Week_day == weekday) & \
           (db.classes.Startdate <= date) & \
           ((db.classes.Enddate >= date) |
            (db.classes.Enddate == None)) # can't use is here, query doesn't work


def schedule_get_form_jump(jump_date):
    """
        Returns a form to jump to a date
    """
    form_jump = SQLFORM.factory(
                Field('appointments_date', 'date',
                      requires=IS_DATE_IN_RANGE(
                                format=DATE_FORMAT,
                                minimum=datetime.date(1900,1,1),
                                maximum=datetime.date(2999,1,1)),
                      default=jump_date,
                      label=T(""),
                      widget=os_datepicker_widget_small),
                submit_button=T('Go'),
                )

    submit_jump = form_jump.element('input[type=submit]')
    submit_jump['_class'] = 'full-width'

    form_jump = DIV(form_jump.custom.begin,
                    DIV(form_jump.custom.widget.appointments_date,
                        DIV(form_jump.custom.submit,
                            _class='input-group-btn'),
                        _class='input-group'),
                    form_jump.custom.end,
                    _class='form_inline',
                    _id='form_jump')

    return form_jump


def index_get_week_chooser(var=None):
    """
        Returns a week chooser for the schedule
    """
    year = session.schedule_year
    week = session.schedule_week

    lastweek = get_lastweek_year(year)

    if week == 1:
        prev_week  = lastweek
        prev_year  = year - 1
    else:
        prev_week  = week - 1
        prev_year  = year

    if week == lastweek:
        next_week  = 1
        next_year  = year + 1
    else:
        next_week  = week + 1
        next_year  = year


    previous = A(I(_class='fa fa-angle-left'),
                 _href=URL('schedule_set_week', vars={ 'week' : prev_week,
                                                       'year' : prev_year }),
                 _class='btn btn-default')
    nxt = A(I(_class='fa fa-angle-right'),
            _href=URL('schedule_set_week', vars={ 'week' : next_week,
                                                  'year' : next_year }),
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
               auth.has_permission('read', 'classes'))
def index_current_week():
    session.schedule_week = None
    session.schedule_year = None

    redirect(URL('schedule'))


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'classes'))
def _schedule_clear_filter():
    session.appointmetns_index_filter_location = None
    session.appointmetns_index_filter_teacher = None
    session.appointmetns_index_filter_appointment = None
    session.appointmetns_index_filter_level = None
    session.appointmetns_index_filter_status = None

    #cache_clear_classschedule()

    redirect(URL('schedule'))


def schedule_get_filter_form(school_locations_id='',
                             teachers_id='',
                             school_appointment_id='',
                             school_levels_id='',
                             status=''):

    ct_query = (db.school_appointment.Archived == False)
    slo_query = (db.school_locations.Archived == False)
    sle_query = (db.school_levels.Archived == False)

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
            requires=IS_IN_DB(db(ct_query),'school_appointment.id', '%(Name)s',
                              zero=T('All appointments')),
            default=school_appointment_id,
            label=""),
        Field('level',
            requires=IS_IN_DB(db(sle_query),'school_levels.id', '%(Name)s',
                              zero=T('All levels')),
            default=school_levels_id,
            label=""),
        Field('status',
            requires=IS_IN_SET(session.class_status,
                               zero=T('All statuses')),
            default=status,
            label=''),
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
            _class='col-md-2'),
        DIV(form.custom.widget.teacher,
            _class='col-md-2'),
        DIV(form.custom.widget.appointment,
            _class='col-md-2'),
        DIV(form.custom.widget.level,
            _class='col-md-2'),
        DIV(form.custom.widget.status,
            _class='col-md-2'),
        DIV(DIV(form.custom.submit,
                clear,
                _class="pull-right"),
            _class='col-md-2'),
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
