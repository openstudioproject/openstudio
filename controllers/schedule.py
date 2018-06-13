# -*- coding: utf-8 -*-
"""
    This controller contains functions shared by the classes, employees and
    workshop schedules.
"""

from general_helpers import class_get_teachers
from general_helpers import set_form_id_and_get_submit_button

from openstudio.os_class_schedule import ClassSchedule
from openstudio.os_staff_schedule import StaffSchedule


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'school_holidays'))
def holidays():
    """
        List holidays
    """
    response.title = T("School")
    response.subtitle = T("Holidays")
    response.view = 'general/only_content.html'
    db.school_holidays.id.readable=False
    fields = [ db.school_holidays.Description,
               db.school_holidays.Startdate,
               db.school_holidays.Enddate,
               db.school_holidays.school_locations_ids ]
    links = [ {'header':T('Locations'), 'body':holidays_get_link_locations},
              lambda row: os_gui.get_button('edit',
                                     URL('holiday_edit', vars={'shID':row.id}),
                                     T("Edit holiday")) ]

    delete_permission = auth.has_membership(group_id='Admins') or \
                        auth.has_permission('delete', 'school_holidays')

    maxtextlengths = {'school_holidays.Description':40}

    grid = SQLFORM.grid(db.school_holidays, fields=fields, links=links,
        create=False,
        editable=False,
        details=False,
        searchable=False,
        deletable=delete_permission,
        csv=False,
        maxtextlengths=maxtextlengths,
        ondelete=cache_clear_classschedule,
        orderby=~db.school_holidays.Startdate,
        field_id=db.school_holidays.id,
        ui = grid_ui)
    grid.element('.web2py_counter', replace=None) # remove the counter
    grid.elements('span[title=Delete]', replace=None) # remove text from delete button

    add_url = URL('holiday_add')
    add = os_gui.get_button('add', add_url, T("Add a holiday"))

    return dict(content=grid, add=add, back='')


def holidays_get_link_locations(row):
    """
        Lists all locations linked to a holiday as info bootstrap labels
    """
    query = (db.school_holidays_locations.school_holidays_id == row.id)
    left = [ db.school_locations.on(db.school_locations.id == \
                db.school_holidays_locations.school_locations_id) ]
    rows = db(query).select(db.school_locations.Name,
                            left=left,
                            orderby=db.school_locations.Name)
    labels = SPAN()
    for row in rows:
        labels.append(os_gui.get_label('info', row.Name))
        labels.append(' ')

    return labels


def holiday_edit_onacept(form):
    """
        :param form: crud form for db.school_holidays
        :return: None
    """
    cancel_class_bookings(form.vars.id)


def cancel_class_bookings(shID):
    """
        :param shID: db.school_holidays.id
        :return: None
    """
    from openstudio.os_attendance_helper import AttendanceHelper

    ah = AttendanceHelper()
    ah.attendance_cancel_classes_in_school_holiday(shID)


@auth.requires_login()
def holiday_add():
    """
        This function shows an add page for a holiday
    """
    response.title = T("New holiday")
    response.subtitle = T('')
    response.view = 'general/tabs_menu.html'

    db.school_holidays.Classes.readable = False
    db.school_holidays.Classes.writable = False
    db.school_holidays.Classes.default = True

    return_url = URL('holidays')

    crud.messages.submit_button = T("Next")
    crud.messages.record_created = T("Added holiday")
    crud.settings.create_onaccept = [cache_clear_classschedule]
    crud.settings.create_next = '/schedule/holiday_edit_locations?shID=[id]'
    crud.settings.formstyle = 'bootstrap3_stacked'
    form = crud.create(db.school_holidays)

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']

    back = os_gui.get_button('back', return_url)
    menu = holiday_add_get_menu(request.function)

    return dict(content=form, back=back, menu=menu, save=submit)


@auth.requires_login()
def holiday_edit():
    """
        This function shows an edit page for a holiday
        request.args[0] is expected to be the holidayID (hoID)
    """
    shID = request.vars['shID']
    response.title = T("Edit holiday")
    response.subtitle = T('')
    response.view = 'general/tabs_menu.html'

    db.school_holidays.Classes.readable = False
    db.school_holidays.Classes.writable = False

    db.school_holidays.Classes.default = True

    return_url = URL('holidays')

    crud.messages.submit_button = T("Save")
    crud.messages.record_updated = T("Updated holiday")
    crud.settings.update_onaccept = [cache_clear_classschedule, holiday_edit_onacept]
    crud.settings.update_next = return_url
    crud.settings.update_deletable = False
    crud.settings.formstyle = 'bootstrap3_stacked'
    form = crud.update(db.school_holidays, shID)

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']

    back = os_gui.get_button('back', return_url)
    menu = holiday_edit_get_menu(request.function, shID)

    return dict(content=form, back=back, menu=menu, save=submit)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('update', 'school_holidays_locations'))
def holiday_edit_locations():
    """
        Edit locations assigned to a school holiday
    """
    shID = request.vars['shID']

    holiday = db.school_holidays(shID)
    response.title = T("Holiday locations")
    response.subtitle = holiday.Description
    response.view = 'general/tabs_menu.html'

    table = TABLE(TR(TH(), TH(T('Location')), _class='header'),
                  _class='table table-hover')
    # make a list of locations to which this holiday applies
    query = (db.school_holidays_locations.school_holidays_id == shID)
    rows = db(query).select(db.school_holidays_locations.school_locations_id)
    location_ids = list()
    for row in rows:
        location_ids.append(unicode(row.school_locations_id))

    # get all locations
    rows = db().select(db.school_locations.id,
                       db.school_locations.Name,
                       orderby=db.school_locations.Name)
    # Get list of all locations and check those found in location_ids
    for row in rows:
        if unicode(row.id) in location_ids:
            # check the row
            table.append(TR(TD(INPUT(_type='checkbox',
                                  _name=row.id,
                                  _value="on",
                                  value="on"),
                                _class='td_status_marker'),
                            TD(row.Name)))
        else:
            table.append(TR(TD(INPUT(_type='checkbox',
                                     _name=row.id,
                                     _value="on"),
                               _class='td_status_marker'),
                            TD(row.Name)))
    form = FORM(table, _id='MainForm')

    # After submitting, check which classtypes are 'on'
    if form.accepts(request,session):
        #remove all current records
        db(db.school_holidays_locations.school_holidays_id==shID).delete()
        # make a list of all classtypes
        rows = db().select(db.school_locations.id)
        location_ids = []
        for row in rows:
            location_ids.append(unicode(row.id))
        # insert new records
        for locID in location_ids:
            if request.vars[locID] == 'on':
                db.school_holidays_locations.insert(
                    school_holidays_id = shID,
                    school_locations_id = locID)

        # Cancel bookings for classes in holiday
        cancel_class_bookings(shID)
        # Notify user
        session.flash = T('Saved')
        redirect(URL('holidays'))

    description = B(T("To which locations does this holiday apply?"))
    content = DIV(description, BR(), BR(), form)

    back = os_gui.get_button('back', URL('holidays'))
    menu = holiday_edit_get_menu(request.function, shID)

    return dict(content=content, back=back, menu=menu, save=os_gui.get_submit_button('MainForm'))


def holiday_add_get_menu(page):
    """
        Returns submenu for adding an holiday
    """
    pages = [ ['holiday_add', T('1. Add holiday'), "#"],
              ['holiday_edit_locations', T('2. Choose locations'), "#"] ]

    return os_gui.get_submenu(pages, page, horizontal=True, htype='tabs')


def holiday_edit_get_menu(page, shID):
    """
        Returns submenu for editing an holiday
    """
    vars = {'shID':shID}

    pages = [ ['holiday_edit',
               T('Edit'),
               URL('holiday_edit', vars=vars)],
              ['holiday_edit_locations',
               T('Locations'),
               URL('holiday_edit_locations', vars=vars)] ]

    return os_gui.get_submenu(pages, page, horizontal=True, htype='tabs')



@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'teacher_holidays'))
def staff_holidays():
    """
        Select a staff member and set all classes as open within a range of dates.
        response.flash allows you to flash a message to the user when the page
        is returned.
        Use session.flash instead of response.flash to display a message
        after redirection.
    """
    response.view = 'general/only_content.html'
    response.title = T('Staff holidays')
    response.subtitle = ''

    links = []
    permission = auth.has_membership(group_id='Admins') or \
                 auth.has_permission('update', 'class_status')
    if permission:
        links.append(lambda row: A(SPAN(_class='glyphicon glyphicon-edit'), ' ',
                                   T("Class & shift status"),
                                   _href=URL('staff_holidays_choose_status',
                                            vars={'sthID':row.id}),
                                   _class='btn btn-default btn-sm'))
    links.append(lambda row: os_gui.get_button('edit', URL('staff_holiday_edit',
                                                 vars={'sthID':row.id})))

    fields = [ db.teachers_holidays.auth_teacher_id,
               db.teachers_holidays.Startdate,
               db.teachers_holidays.Enddate,
               db.teachers_holidays.Note ]

    maxtextlengths = {'teachers_holidays.Note': 40}

    delete_permission = auth.has_membership(group_id='Admins') or \
                        auth.has_permission('delete', 'teacher_holidays')

    grid = SQLFORM.grid(db.teachers_holidays,
                        fields=fields,
                        links=links,
                        details=False,
                        searchable=False,
                        deletable=delete_permission,
                        csv=False,
                        create=False,
                        editable=False,
                        maxtextlengths=maxtextlengths,
                        ondelete=cache_clear_classschedule,
                        orderby=~db.teachers_holidays.Startdate,
                        field_id=db.teachers_holidays.id,
                        ui = grid_ui)
    grid.element('.web2py_counter', replace=None) # remove the counter
    grid.elements('span[title=Delete]', replace=None) # remove text from delete button

    add_url = URL('staff_holiday_add')
    add = os_gui.get_button('add', add_url, T("Add a new holiday"))
    content = grid

    if session.schedule_staff_holidays_back == 'staff_schedule':
        return_url = URL('staff', 'schedule')
    else:
        return_url = URL('classes', 'schedule')

    back = os_gui.get_button('back', return_url)
    back = DIV(back, add)

    return dict(content=content,
                 back=back)


@auth.requires_login()
def staff_holiday_add():
    """
        This function shows an add page for a teacher holiday
    """
    response.view = 'general/only_content.html'
    response.title = T("Add holiday")
    response.subtitle = ''

    return_url = URL('staff_holidays')

    crud.messages.submit_button = T("Next")
    crud.messages.record_created = T("Saved")
    crud.settings.create_next = return_url
    crud.settings.create_onaccept = [cache_clear_classschedule]
    form = crud.create(db.teachers_holidays)

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']

    back = os_gui.get_button("back", return_url)

    return dict(content=form, back=back, save=submit)


@auth.requires_login()
def staff_holiday_edit():
    """
        This function shows an edit page for a teacher holiday
    """
    response.view = 'general/only_content.html'
    response.title = T("Edit holiday")
    response.subtitle = ''

    sthID = request.vars['sthID']

    return_url = URL('staff_holidays')

    crud.messages.submit_button = T("Save")
    crud.messages.record_updated = T("Saved")
    crud.settings.update_onaccept = [cache_clear_classschedule]
    crud.settings.update_deletable = False
    crud.settings.update_next = return_url
    form = crud.update(db.teachers_holidays, sthID)

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']

    back = os_gui.get_button("back", return_url)

    return dict(content=form, back=back, save=submit)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('update', 'class_status'))
def staff_holidays_choose_status():
    """
        Page to choose status for all classes in period
    """
    response.view = 'general/content_left_sidebar.html'
    response.title = T("Staff holiday")
    response.subtitle = T('Choose class & shift status')

    sthID = request.vars['sthID']

    statuses = [ ['normal', T('Normal')],
                 ['cancelled', T('Cancelled')],
                 ['open', T('Open')] ]

    form = SQLFORM.factory(
        Field('status',
            requires=IS_IN_SET(statuses, zero=T("Please select...")),
            label=T("Change status of shifts and classes during holiday to")),
        # Field('apply_teacher2', 'boolean',
        #     label=T("Also when teacher2")),
        submit_button = T("Set status"),
        formstyle = 'divs'
        )

    if form.process().accepted:
        staff_holidays_set_status(sthID,
                                    form.vars.status,
                                    form.vars.apply_teacher2)
        redirect(URL('staff_holidays'))

    query = (db.teachers_holidays.id == sthID)
    left  = [ db.auth_user.on(db.teachers_holidays.auth_teacher_id ==
                              db.auth_user.id) ]
    rows = db(query).select(db.teachers_holidays.ALL,
                            db.auth_user.display_name,
                            left=left)
    row = rows.first()

    title = H2(row.auth_user.display_name)
    description = DIV(row.teachers_holidays.Startdate.strftime(DATE_FORMAT),
                      ' - ',
                      row.teachers_holidays.Enddate.strftime(DATE_FORMAT), BR(),
                      row.teachers_holidays.Note)
    content = DIV(title,
                  description,
                  BR(), BR(),
                  DIV(form, _class='col-md-6 no_padding-left'))

    back = os_gui.get_button('back', URL('staff_holidays'), _class='full-width')

    return dict(content=content, back=back)


def staff_holidays_set_status(sthID, status, apply_teacher2):
    """
        This function sets the status for classes during a teachers' holiday
    """
    from openstudio.os_shift import Shift

    holiday = db.teachers_holidays(sthID)
    teachers_id = holiday.auth_teacher_id
    startdate = holiday.Startdate
    enddate = holiday.Enddate
    # Find classes
    delta = datetime.timedelta(days=1)
    current_date = startdate
    changed = 0

    while current_date <= enddate:
        # find all classes for teacher and set them as open
        weekday = current_date.isoweekday()

        cs = ClassSchedule(
            current_date,
            filter_id_teacher = teachers_id
        )

        rows = cs.get_day_rows()

        for row in rows:
            cotcID = row.classes_otc.id

            if cotcID:
                record = db.classes_otc(cotcID)
                if not record is None: # final check to see if we really get something from the db
                # we have a record
                    if status != 'normal':
                        record.Status = status
                        record.update_record()
                    else:
                        """
                         if the status is normal:
                            check if there are any other changes
                            otherwise just delete. """
                        change = False
                        fields = [
                            record.school_locations_id,
                            record.school_classtypes_id,
                            record.Starttime,
                            record.Endtime,
                            record.auth_teacher_id,
                            record.auth_teacher_id2,
                            record.Description
                        ]
                        for field in fields:
                            if not field is None or field == '':
                                change = True

                        if not change:
                            query = (db.classes_otc.id == cotcID)
                            result = db(query).delete()

            elif status != 'normal':
                # no record found, insert one (status normal doesn't need a record)
                db.classes_otc.insert(
                    classes_id = row.classes.id,
                    ClassDate  = current_date,
                    Status     = status
                )

        # Shift status
        staff_schedule = StaffSchedule(current_date,
                                       filter_id_employee = teachers_id)
        shifts = staff_schedule.get_day_list(show_id = True)
        for shift in shifts:
            shift = Shift(shift['id'], current_date)
            # apply new status
            if status == 'normal':
                shift.set_status_normal()
            elif status == 'open':
                shift.set_status_open()
            elif status == 'cancelled':
                shift.set_status_cancelled()

        current_date += delta

    session.flash = T("Changed class statuses")
