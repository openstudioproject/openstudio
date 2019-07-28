# -*- coding: utf-8 -*-

import os
import datetime
import io
import openpyxl

from general_helpers import get_submenu
from general_helpers import set_form_id_and_get_submit_button

from openstudio.os_customers import Customers
from openstudio.os_school_subscription import SchoolSubscription

def account_get_tools_link_groups(var=None):
    """
        @return: link to settings/groups
    """
    return A(SPAN(os_gui.get_fa_icon('fa-users'), ' ', T('Groups')),
             _href=URL('settings', 'access_groups'),
             _title=T('Define groups and permission for teachers'))


@auth.requires(auth.has_membership(group_id='Admins') or \
                auth.has_permission('read', 'teachers'))
def index():
    response.title = T("School")
    response.subtitle = T("Teachers")
    # response.view = 'general/tabs_menu.html'
    response.search_available = True

    if 'q' in request.vars:
        session.teachers_index_q = request.vars['q']

    response.q = session.teachers_index_q or ""

    session.customers_back = 'teachers'
    session.customers_add_back = 'teachers'
    session.settings_groups_back = 'teachers'

    # show back, add and export buttons above teachers list
    back = os_gui.get_button('back', URL('school_properties', 'index'))

    # add employee
    customers = Customers()
    add = customers.get_add(redirect_vars={'teacher':True})

    contact_list = A(SPAN(os_gui.get_fa_icon('fa-volume-control-phone'), ' ',
                          T("Contact list")),
                     _href=URL('index_export_excel'))
    links = [ contact_list ]
    export = os_gui.get_dropdown_menu(
        links = links,
        btn_text = '',
        btn_size = 'btn-sm',
        btn_icon = 'download',
        menu_class='pull-right')

    tools = index_get_tools()
    header_tools = ''

    content = index_get_content(response.q)

    menu = index_get_menu(request.function)

    back = DIV(add, export, tools)

    return dict(back=back,
                header_tools=header_tools,
                menu=menu,
                content=content)


def index_get_content(search_name):
    """
    :param var: dummy to prevent this being a public function
    :return: HTML table containing teachers
    """
    from openstudio.os_teachers import Teachers

    teachers = Teachers()

    return teachers.list(search_name, formatted=True)


def index_get_tools(var=None):
    """
        @return: tools dropdown for teachers
    """
    tools = ''
    links = []
    # Groups
    permission = auth.has_membership(group_id='Admins') or \
                 auth.has_permission('read', 'settings')

    if permission:
        groups = account_get_tools_link_groups()
        links.append(groups)

    if len(links) > 0:
        tools = os_gui.get_dropdown_menu(links,
                                         '',
                                         btn_size='btn-sm',
                                         btn_icon='wrench',
                                         menu_class='pull-right')

    return tools


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('update', 'teachers'))
def teaches_classes():
    """
        Changes the value of auth_user.teaches_classes boolean
    """
    uID = request.vars['uID']

    user = db.auth_user(uID)
    user.teaches_classes = not user.teaches_classes
    user.update_record()

    redirect(URL('index'))


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('update', 'teachers'))
def teaches_events():
    """
        Changes the value of auth_user.teaches_workshops boolean
    """
    uID = request.vars['uID']

    user = db.auth_user(uID)
    user.teaches_workshops = not user.teaches_workshops
    user.update_record()

    redirect(URL('index'))


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('delete', 'teachers'))
def delete():
    """
        This function archives a subscription
        request.vars[uID] is expected to be the auth_userID
    """
    uID = request.vars['uID']
    if not uID:
        session.flash = T('Unable to remove from teachers list')
    else:
        row = db.auth_user(uID)
        row.teacher = False
        row.update_record()

        session.flash = SPAN(
            T('Removed'), ' ',
            row.display_name, ' ',
            T('from teacher list'))

    redirect(URL('index'))


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('update', 'teachers'))
def edit_classtypes():
    # generate the form
    uID = request.vars['uID']
    record = db.auth_user(uID)
    teachername = record.display_name
    response.title = T("Classtypes")
    response.subtitle = teachername
    response.view = 'general/only_content.html'

    table = TABLE(TR(TH(), TH(T('Class type')), _class='header'),
                  _class='table table-hover')
    query = (db.teachers_classtypes.auth_user_id == uID)
    rows = db(query).select(db.teachers_classtypes.school_classtypes_id)
    classtypeids = []
    for row in rows:
        classtypeids.append(str(row.school_classtypes_id))

    list_query = (db.school_classtypes.Archived == False)
    rows = db(list_query).select(db.school_classtypes.id,
                                 db.school_classtypes.Name,
                                 orderby=db.school_classtypes.Name)
    for row in rows:
        if str(row.id) in classtypeids:
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

    return_url = URL('index')

    # make a list of all classtypes
    rows = db().select(db.school_classtypes.id)
    classtypeids = list()
    for row in rows:
        classtypeids.append(str(row.id))

    # After submitting, check which classtypes are 'on'
    if form.accepts(request,session):
        #remove all current records
        db(db.teachers_classtypes.auth_user_id==uID).delete()
        # insert new records for teacher
        for classtypeID in classtypeids:
            if request.vars[classtypeID] == 'on':
                db.teachers_classtypes.insert(auth_user_id=uID,
                                              school_classtypes_id=classtypeID)

        # Clear teachers (API) cache
        cache_clear_school_teachers()

        session.flash = T('Saved classtypes')
        redirect(return_url)

    description = H4(T("Here you can specify which kinds of classes a teacher teaches at this school."))
    content = DIV(BR(), description, BR(), form)

    back = os_gui.get_button('back', return_url)

    return dict(content=content, back=back, save=os_gui.get_submit_button('MainForm'))


@auth.requires(auth.has_membership(group_id='Admins') or \
                auth.has_permission('read', 'teachers'))
def index_export_excel():
    export_type = "contactlist"
    date = datetime.date.today()
    date = date.strftime(DATE_FORMAT)

    error = False

    if export_type == "contactlist":
        title = T("ContactList") + " " + date
        wb = openpyxl.workbook.Workbook(write_only=True)
        ws = wb.create_sheet(title=title)
        ws.append([T("Teachers contact list") + " " + date])
        ws.append([])


        # write the header
        header = [ "First name", "Last name", "Telephone", "Mobile", "Email" ]
        ws.append(header)
        # fill the columns
        query = (db.auth_user.teacher == True)
        rows = db().select(db.auth_user.display_name,
                           db.auth_user.phone,
                           db.auth_user.mobile,
                           db.auth_user.email,
                           orderby=db.auth_user.display_name)

        for row in rows:
            data = [ row.display_name,
                     row.phone,
                     row.mobile,
                     row.email ]
            ws.append(data)

        fname = T('Contactlist') + '.xlsx'
        # create filestream
        stream = io.StringIO()

        wb.save(stream)
        response.headers['Content-Type']='application/vnd.ms-excel'
        response.headers['Content-disposition']='attachment; filename=' + fname

        return stream.getvalue()


def back_index(var=None):
    return os_gui.get_button('back', URL('index'))


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'teachers_payment_travel'))
def payment_travel():
    """
        Configure travel allowance for teachers
    """
    from openstudio.os_customer import Customer
    from openstudio.os_teacher import Teacher

    teID = request.vars['teID']
    response.view = 'general/only_content.html'

    customer = Customer(teID)
    response.title = customer.get_name()
    response.subtitle = T("Travel allowance")

    teacher = Teacher(teID)
    content = teacher.get_payment_travel_display()

    add = os_gui.get_button('add',
                            URL('teachers',
                                'payment_travel_add',
                                vars={'teID': teID}),
                            _class='pull-right')

    back = back_index()

    return dict(content=content,
                header_tools=add,
                back=back)


@auth.requires(auth.has_membership(group_id='Admins') or \
                auth.has_permission('read', 'teachers_payment_fixed_rate_default'))
def payment_fixed_rate():
    """
        Configure fixed rate payments for this teacher
    """
    from openstudio.os_customer import Customer
    from openstudio.os_teacher import Teacher

    teID = request.vars['teID']
    response.view = 'general/only_content.html'

    customer = Customer(teID)
    response.title = customer.get_name()
    response.subtitle = T("Payments")

    teacher = Teacher(teID)
    content = DIV(
        teacher.get_payment_fixed_rate_default_display(),
        teacher.get_payment_fixed_rate_classes_display()
    )

    back = back_index()

    return dict(content=content,
                #menu=menu,
                back=back)


def payment_fixed_rate_default_return_url(teID):
    """
    :return: URL to redirect back to after adding/editing the default rate
    """
    return URL('payment_fixed_rate', vars={'teID':teID})


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'teachers_payment_fixed_rate_default'))
def payment_fixed_rate_default():
    """
        Add default fixed rate for this teacher
    """
    from openstudio.os_customer import Customer
    from openstudio.os_teacher import Teacher
    from openstudio.os_forms import OsForms

    teID = request.vars['teID']
    response.view = 'general/only_content.html'

    customer = Customer(teID)
    response.title = customer.get_name()
    response.subtitle = T("Teacher profile")

    os_forms = OsForms()
    return_url = payment_fixed_rate_default_return_url(teID)

    db.teachers_payment_fixed_rate_default.auth_teacher_id.default = teID

    teacher = Teacher(teID)
    default_payments = teacher.get_payment_fixed_rate_default()
    if default_payments:
        title = H4(T('Edit default rate'))
        result = os_forms.get_crud_form_update(
            db.teachers_payment_fixed_rate_default,
            return_url,
            default_payments.first().id
        )
    else:
        title = H4(T('Add default rate'))
        result = os_forms.get_crud_form_create(
            db.teachers_payment_fixed_rate_default,
            return_url,
        )

    form = result['form']

    content = DIV(
        title,
        form
    )

    back = os_gui.get_button('back', return_url)

    return dict(content=content,
                #menu=menu,
                back=back,
                save=result['submit'])


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('create', 'teachers_payment_fixed_rate_class'))
def payment_fixed_rate_class_add():
    """
        Add customers to attendance for a class
    """
    from openstudio.os_customer import Customer
    from openstudio.os_customers import Customers
    from general_helpers import datestr_to_python

    response.view = 'general/only_content.html'

    teID = request.vars['teID']
    customer = Customer(teID)
    response.title = customer.get_name()
    response.subtitle = T("Add class payment rate")

    if 'date' in request.vars:
        date = datestr_to_python(DATE_FORMAT, request.vars['date'])
    else:
        date = TODAY_LOCAL

    customers = Customers()
    result = customers.classes_add_get_form_date(teID, date)
    form = result['form']
    form_date = result['form_styled']

    db.classes.id.readable = False
    # list of classes
    grid = customers.classes_add_get_list(date, 'tp_fixed_rate', teID=teID)

    back = os_gui.get_button('back',
                             URL('payment_fixed_rate',
                                 vars={'teID':teID}),
                             _class='left')

    return dict(content=DIV(form_date, grid),
                back=back)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'teachers_payment_fixed_rate_class'))
def payment_fixed_rate_class():
    """
        Add default fixed rate for this teacher
    """
    from openstudio.os_customer import Customer
    from openstudio.os_teacher import Teacher
    from openstudio.os_forms import OsForms

    teID = request.vars['teID']
    clsID = request.vars['clsID']
    response.view = 'general/only_content.html'

    customer = Customer(teID)
    response.title = customer.get_name()
    response.subtitle = T("Set class rate")

    record = db.classes(clsID)
    location = db.school_locations[record.school_locations_id].Name
    classtype = db.school_classtypes[record.school_classtypes_id].Name
    class_name = NRtoDay(record.Week_day) + ' ' + \
                 record.Starttime.strftime(TIME_FORMAT) + ' - ' + \
                 classtype + ', ' + location

    os_forms = OsForms()
    return_url = payment_fixed_rate_default_return_url(teID)

    db.teachers_payment_fixed_rate_class.auth_teacher_id.default = teID
    db.teachers_payment_fixed_rate_class.classes_id.default = clsID

    teacher = Teacher(teID)
    payment = db.teachers_payment_fixed_rate_class(
        classes_id = clsID,
        auth_teacher_id = teID
    )
    if payment:
        title = H4(T('Edit class rate for'), ' ', class_name)
        result = os_forms.get_crud_form_update(
            db.teachers_payment_fixed_rate_class,
            return_url,
            payment.id
        )
    else:
        title = H4(T('Add class rate for'), ' ', class_name)
        result = os_forms.get_crud_form_create(
            db.teachers_payment_fixed_rate_class,
            return_url,
        )

    form = result['form']

    content = DIV(
        title,
        form
    )

    back = os_gui.get_button('back', return_url)

    return dict(content=content,
                back=back,
                save=result['submit'])


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('delete', 'teachers_payment_fixed_rate_class'))
def payment_fixed_rate_class_delete():
    """
    Delete teacher fixed rate class rate
    :return: None
    """
    teID = request.vars['teID']
    tpfrcID = request.vars['tpfrcID']

    query = (db.teachers_payment_fixed_rate_class.id == tpfrcID)
    db(query).delete()

    session.flash = T('Deleted class rate')
    redirect(payment_fixed_rate_default_return_url(teID))


def payment_fixed_rate_return_url(teID):
    return URL('payment_fixed_rate', vars={'teID':teID})


def payment_travel_return_url(teID):
    return URL('payment_travel', vars={'teID':teID})


@auth.requires_login()
def payment_travel_add():
    """
        Add travel allowance for a teacher
    """
    from openstudio.os_customer import Customer
    from openstudio.os_forms import OsForms

    teID = request.vars['teID']

    customer = Customer(teID)
    response.title = customer.get_name()
    response.subtitle = T("Add travel allowance")
    response.view = 'general/only_content.html'


    db.teachers_payment_travel.auth_teacher_id.default = teID
    return_url = payment_travel_return_url(teID)

    os_forms = OsForms()
    result = os_forms.get_crud_form_create(
        db.teachers_payment_travel,
        return_url,
    )

    form = result['form']
    back = os_gui.get_button('back', return_url)

    return dict(content=form,
                save=result['submit'],
                back=back)


@auth.requires_login()
def payment_travel_edit():
    """
        Add travel allowance for a teacher
    """
    from openstudio.os_customer import Customer
    from openstudio.os_forms import OsForms

    teID = request.vars['teID']
    tpfrtID = request.vars['tpfrtID']

    customer = Customer(teID)
    response.title = customer.get_name()
    response.subtitle = T("Edit travel allowance")
    response.view = 'general/only_content.html'

    return_url = payment_travel_return_url(teID)

    os_forms = OsForms()
    result = os_forms.get_crud_form_update(
        db.teachers_payment_travel,
        return_url,
        tpfrtID
    )

    form = result['form']
    back = os_gui.get_button('back', return_url)

    return dict(content=form,
                save=result['submit'],
                back=back)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('delete', 'teachers_payment_travel'))
def payment_travel_delete():
    """
    Delete teacher fixed rate travel allowance
    :return: None
    """
    teID = request.vars['teID']
    tpfrtID = request.vars['tpfrtID']

    query = (db.teachers_payment_travel.id == tpfrtID)
    db(query).delete()

    session.flash = T('Deleted travel allowance')
    redirect(payment_travel_return_url(teID))


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'teachers_payment_attendance_lists'))
def payment_attendance_lists():
    """
    Display Payment Attendance Lists page
    :return:
    """
    response.title = T("Teachers")
    response.subtitle = T("Payment Attendance List")

    # response.view = 'general/only_content.html'

    response.view = 'general/tabs_menu.html'

    show = 'current'
    query = (db.teachers_payment_attendance_lists.Archived == False)

    if 'show_archive' in request.vars:
        show = request.vars['show_archive']
        session.teachers_payment_attendance_lists_show = show
        if show == 'current':
            query = (db.teachers_payment_attendance_lists.Archived == False)
        elif show == 'archive':
            query = (db.teachers_payment_attendance_lists.Archived == True)
    elif session.teachers_payment_attendance_list == 'archive':
        query = (db.teachers_payment_attendance_lists.Archived == True)
    else:
        session.teachers_payment_attendance_lists_show = show

    db.teachers_payment_attendance_lists.id.readable = False

    fields = [
        db.teachers_payment_attendance_lists.Name,
        db.teachers_payment_attendance_lists.tax_rates_id,
    ]

    links = [
            lambda row: A(SPAN(os_gui.get_fa_icon('fa-usd'),
                               " " + T("Rates")),
                               _class="btn btn-default btn-sm",
                               _href=URL('teachers', 'payment_attendance_list_rates',
                                         vars={'tpalID':row.id})),
            lambda row: A(SPAN(_class="buttontext button",
                                    _title=T("Class types")),
                               SPAN(_class="glyphicon glyphicon-edit"),
                               " " + T("Class types"),
                               _class="btn btn-default btn-sm",
                               _href=URL('payment_attendance_list_classtypes',
                                         vars={'tpalID':row.id})),
             lambda row: os_gui.get_button('edit',
                                           URL('payment_attendance_list_edit',
                                               vars={'tpalID': row.id}),
                                           T("Edit Name of the Attendance List")),
             payment_attendance_lists_get_link_archive
    ]
    maxtextlengths = {'teachers_payment_attendance_list.Name': 40}
    headers = {'payment_attendance_list': 'Sorting'}
    grid = SQLFORM.grid(query, fields=fields, links=links,
                        maxtextlengths=maxtextlengths,
                        headers=headers,
                        create=False,
                        editable=False,
                        deletable=False,
                        details=False,
                        searchable=False,
                        csv=False,
                        orderby=~db.teachers_payment_attendance_lists.Name,
                        ui=grid_ui)
    grid.element('.web2py_counter', replace=None)  # remove the counter
    grid.elements('span[title=Delete]', replace=None)  # remove text from delete button

    add_url = URL('payment_attendance_list_add')
    add = os_gui.get_button('add', add_url, T("Add a new attendance list"), _class='pull-right')
    archive_buttons = os_gui.get_archived_radio_buttons(
        session.teachers_payment_attendance_lists_show)

    back = DIV(add, archive_buttons)
    menu = index_get_menu(request.function)

    content = grid

    return dict(back=back,
                menu=menu,
                content=content)


def payment_attendance_list_add_edit_return_url(var=None):
    """
    URL to return back to list
    """
    return URL('payment_attendance_lists')


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'teachers_payment_attendance_list'))
def payment_attendance_list_add():
    """
    page to add a new attendance list
    :return:
    """
    from openstudio.os_forms import OsForms
    response.title = T("Payment Attendance List")
    response.subtitle = T('New Payment Attendance List')
    response.view = 'general/only_content.html'
    return_url = payment_attendance_list_add_edit_return_url()

    os_forms = OsForms()
    result = os_forms.get_crud_form_create(
        db.teachers_payment_attendance_lists,
        return_url,
    )

    form = result['form']
    back = os_gui.get_button('back', return_url)


    content = DIV(
        H4(T('Add Attendance List')),
        form
    )

    return dict(content=content,
                save=result['submit'],
                back=back)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'teachers_payment_attendance_list'))
def payment_attendance_list_edit():
    """
        Edit an attendance list
        request.vars['tpalID'] is expected to be db.teachers_payment_attendance_lists.id
    """
    from openstudio.os_forms import OsForms

    response.title = T("Payment Attendance List")
    response.subtitle = T('Edit Name')
    response.view = 'general/only_content.html'
    tpalID = request.vars['tpalID']

    return_url = payment_attendance_list_add_edit_return_url()

    os_forms = OsForms()
    result = os_forms.get_crud_form_update(
        db.teachers_payment_attendance_lists,
        return_url,
        tpalID
    )

    form = result['form']
    back = os_gui.get_button('back', return_url)

    content = DIV(
        H4(T('Edit name of attendance list')),
        form
    )

    return dict(content=content,
                save=result['submit'],
                back=back)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('update', 'teachers_payment_attendance_list_school_classtypes'))
def payment_attendance_list_classtypes():
    """
        Edit an attendance list
        request.vars['tpalID'] is expected to be db.teachers_payment_attendance_lists.id
    """
    from openstudio.os_forms import OsForms

    response.title = T("Payment Attendance List")
    response.view = 'general/only_content.html'
    tpalID = request.vars['tpalID']


    tpal = db.teachers_payment_attendance_lists(tpalID)
    response.subtitle = SPAN(
        tpal.Name, ' ',
        T('classtypes')

    )

    return_url = payment_attendance_list_add_edit_return_url()

    table = TABLE(TR(TH(), TH(T('Class type')), _class='header'),
                  _class='table table-hover')


    # Get unique list of classtype ids in db.teachers_payment_attendance_lists_school_classtypes
    query = (db.teachers_payment_attendance_lists_school_classtypes.id > 0)
    rows = db(query).select(
        db.teachers_payment_attendance_lists_school_classtypes.school_classtypes_id,
        distinct = True
    )

    tpalsc_clt_ids = set()
    for row in rows:
        tpalsc_clt_ids.add(row.school_classtypes_id)

    # Get list of all not archived classtypes
    query = (db.school_classtypes.Archived == False)
    rows = db(query).select(
        db.school_classtypes.id,
        distinct = True
    )

    all_clt_ids = set()
    for row in rows:
        all_clt_ids.add(row.id)

    available_ids = (all_clt_ids - tpalsc_clt_ids)

    # Add currently assigned ids to complete the set
    query = (db.teachers_payment_attendance_lists_school_classtypes.teachers_payment_attendance_lists_id == tpalID)
    rows = db(query).select(db.teachers_payment_attendance_lists_school_classtypes.school_classtypes_id)
    classtypeids = []
    for row in rows:
        classtypeids.append(str(row.school_classtypes_id))
        available_ids.add(row.school_classtypes_id)


    list_query = (db.school_classtypes.Archived == False) & \
                 (db.school_classtypes.id.belongs(available_ids))
    rows = db(list_query).select(db.school_classtypes.id,
                                 db.school_classtypes.Name,
                                 orderby=db.school_classtypes.Name)
    for row in rows:
        if str(row.id) in classtypeids:
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

    return_url = URL('payment_attendance_lists')

    # make a list of all classtypes
    rows = db().select(db.school_classtypes.id)
    classtypeids = list()
    for row in rows:
        classtypeids.append(str(row.id))

    # After submitting, check which classtypes are 'on'
    if form.accepts(request, session):
        # remove all current records
        query = (db.teachers_payment_attendance_lists_school_classtypes.teachers_payment_attendance_lists_id ==
                 tpalID)
        db(query).delete()
        # insert new records for teacher
        for classtypeID in classtypeids:
            if request.vars[classtypeID] == 'on':
                db.teachers_payment_attendance_lists_school_classtypes.insert(
                    teachers_payment_attendance_lists_id=tpalID,
                    school_classtypes_id=classtypeID
                )

        # Clear teachers (API) cache
        cache_clear_school_teachers()

        session.flash = T('Saved classtypes')
        redirect(return_url)

    description = H4(T("Here you can specify for which class types this list should be used."))
    content = DIV(BR(), description, BR(), form)

    back = os_gui.get_button('back', return_url)

    return dict(content=content,
                back=back,
                save=os_gui.get_submit_button('MainForm'))


# @auth.requires(auth.has_membership(group_id='Admins') or \
#                auth.has_permission('read', 'teachers_payment_attendance_list'))
# def payment_attendance_list_rates_get_fp():
#     """
#         Edit an attendance list
#         request.vars['tpalID'] is expected to be db.teachers_payment_attendance_lists.id
#     """
#     from openstudio.os_forms import OsForms
#
#     response.title = T("Payment Attendance List")
#     response.subtitle = T('Classtype/s connected to this list')
#     response.view = 'general/only_content.html'
#     tpalID = request.vars['tpalID']
#
#     return_url = URL('payment_attendance_list')
#
#     os_forms = OsForms()
#     result = os_forms.get_crud_form_update(
#         db.teachers_payment_attendance_lists_school_classtypes,
#         return_url,
#         tpalID
#     )
#
#     form = result['form']
#     back = os_gui.get_button('back', return_url)
#
#     content = DIV(
#         H4(T('Edit Classtype/s of attendance list')),
#         form
#     )
#
#     return dict(content=content,
#                 save=result['submit'],
#                 back=back)


def payment_attendance_lists_get_link_archive(row):
    """
        Called from the index function. Changes title of archive button
        depending on whether an attendance list is archived or not
    """
    row = db.teachers_payment_attendance_lists(row.id)

    if row.Archived:
        tt = T("Move to current")
    else:
        tt = T("Archive")

    return os_gui.get_button('archive',
                             URL('payment_attendance_list_archive', vars={'tpalID':row.id}),
                             tooltip=tt)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('update', 'teachers_payment_attendance_lists'))
def payment_attendance_list_archive():
    """
        This function archives an attendance list
        request.vars[tpalID] is expected to be the payment attendance list ID
    """
    tpalID = request.vars['tpalID']
    if not tpalID:
        session.flash = T('Unable to (un)archive attendance list')
    else:
        row = db.teachers_payment_attendance_lists(tpalID)

        if row.Archived:
            session.flash = T('Moved to current')
        else:
            # Unlink all classtypes
            query = (db.teachers_payment_attendance_lists_school_classtypes.teachers_payment_attendance_lists_id == tpalID)
            db(query).delete()

            session.flash = T('Archived and unlinked all classtypes')

        row.Archived = not row.Archived
        row.update_record()

        # cache_clear_payment_attendance_list()

    redirect(payment_attendance_list_add_edit_return_url())


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'teachers_payment_attendance_lists_rates'))
def payment_attendance_list_rates():
    """
            Lists rates for the attendance list and shows an add form at the top of the
            page, intended to be used as LOAD component
            request.vars['tpalID'] is expected to be teachers payment attendance list Id
        """
    # call js for styling the form
    response.js = 'set_form_classes();'
    response.title = T("Payment Attendance List Rates")
    response.subtitle = T('Add/Edit list rates')
    response.view = 'general/only_content.html'

    tpalID = request.vars['tpalID']

    form = list_rates_get_form_add(tpalID)

    content = DIV(XML('<form id="MainForm" action="#" enctype="multipart/form-data" method="post">'))

    table = TABLE(THEAD(TR(
            TH(T('# Attendance')),
            TH(T('Rate')),
            TH(),
            _class='header')
            ),
        _class='table table-hover table-striped table-condensed',
        _id=tpalID)

    query = (db.teachers_payment_attendance_lists_rates.teachers_payment_attendance_lists_id == tpalID)
    rows = db(query).select(db.teachers_payment_attendance_lists_rates.ALL,
                            orderby=db.teachers_payment_attendance_lists_rates.AttendanceCount)
    delete_onclick = "return confirm('" + \
                     T('Remove List Rate? ') + "');"
    for i, row in enumerate(rows):
        repr_row = list(rows[i:i + 1].render())[0]

        btn_vars = {'tpalID': tpalID, 'tpalrID': row.id}
        btn_size = 'btn-xs'
        buttons = DIV(_class='pull-right')
        permission = auth.has_membership(group_id='Admins') or \
                     auth.has_permission('update', 'teachers_payment_attendance_list_rates')
        if permission:
            btn_edit = os_gui.get_button('edit_notext',
                                         URL('payment_attendance_lists_rate_edit',
                                             vars=btn_vars),
                                         cid=request.cid)
            buttons.append(btn_edit)

        permission = auth.has_membership(group_id='Admins') or \
                     auth.has_permission('delete', 'teachers_payment_attendance_lists_rates')
        count = payment_attendance_list_count_rates(tpalID)
        if permission and row.AttendanceCount == count:
            btn_delete = os_gui.get_button('delete_notext',
                                           URL('payment_attendance_list_rate_delete',
                                               vars=btn_vars),
                                            onclick=delete_onclick)

            buttons.append(btn_delete)

        tr = TR(
                TD(row.AttendanceCount),
                TD(represent_float_as_amount(row.Rate), _class='Rate'),
                TD(buttons))

        table.append(tr)


    # Add form
    tr = TR(
        TD(),
        TD(form.custom.widget.Rate),
        TD(DIV(form.custom.submit, _class='pull-right')))
    table.append(tr)

    content.append(table)
    content.append(form.custom.end)

    focus_script = SCRIPT(
        """
        $(document).ready(function() {
            $("#teachers_payment_attendance_lists_rates_Rate").focus()
        });
        """,
        _type="text/javascript"
    )

    content.append(focus_script)

    back = os_gui.get_button(
        'back',
        payment_attendance_list_add_edit_return_url()
    )

    return dict(content=content, back=back)


@auth.requires_login()
def payment_attendance_list_rate_edit():
    """
        Edit a supplier
        request.vars['tpalID'] is expected to be teachers payment attendance list Id
    """
    from openstudio.os_forms import OsForms

    response.title = T('Teachers Payment Attendance List')
    response.subtitle = T('Edit')
    response.view = 'general/only_content.html'
    tpalrID = request.vars['tpalrID']
    tpalID = request.vars['tpalID']

    return_url = URL('payment_attendance_list_rates', vars = dict(tpalID=tpalID))

    os_forms = OsForms()
    result = os_forms.get_crud_form_update(
        db.teachers_payment_attendance_lists_rates,
        return_url,
        tpalrID
    )

    form = result['form']
    back = os_gui.get_button('back', return_url)

    content = DIV(
        H4(T('Edit List Rate')),
        form
    )

    return dict(content=content,
                save=result['submit'],
                back=back)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('delete', 'invoices_items'))
def payment_attendance_list_rate_delete():
    """
        Delete rate from attendance list
    """
    tpalID = request.vars['tpalID']
    tpalrID = request.vars['tpalrID']

    query = (db.teachers_payment_attendance_lists_rates.id == tpalrID)
    db(query).delete()


    session.flash = T('Deleted rate')

    redirect(URL('payment_attendance_list_rates', vars=dict(tpalID=tpalID)))


def payment_attendance_list_count_rates(tpalID):
    query= (db.teachers_payment_attendance_lists_rates.teachers_payment_attendance_lists_id == tpalID)
    count = db(query).count()
    if not count:
        count=0

    return count


def list_rates_get_form_add(tpalID):
    """
        Returns add form for invoice items
    """
    from openstudio.os_forms import OsForms

    db.teachers_payment_attendance_lists_rates.teachers_payment_attendance_lists_id.default = tpalID

    number_of_rates = payment_attendance_list_count_rates(tpalID)
    db.teachers_payment_attendance_lists_rates.AttendanceCount.default = number_of_rates + 1

    return_url = URL(vars={'tpalID': tpalID})

    os_forms = OsForms()
    result = os_forms.get_crud_form_create(
        db.teachers_payment_attendance_lists_rates,
        return_url,
    )

    return result['form']


def index_get_menu(page=None):
    pages = []

    pages.append(['index',
                  T("Teachers"),
                  URL("index")])
    if auth.has_membership(group_id='Admins') or \
            auth.has_permission('read', 'payment_attendance_list'):
        pages.append(['payment_attendance_lists',
                      T("Payment Attendance Lists"),
                      URL("teachers", "payment_attendance_lists")])

    return os_gui.get_submenu(pages, page, _id='os-customers_edit_menu', horizontal=True, htype='tabs')

