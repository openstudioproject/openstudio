# -*- coding: utf-8 -*-

import os
import datetime
import cStringIO
import openpyxl

from general_helpers import get_submenu
from general_helpers import set_form_id_and_get_submit_button

from openstudio.openstudio import CustomersHelper, SchoolSubscription

def account_get_tools_link_groups(var=None):
    """
        @return: link to settings/groups
    """
    return A(SPAN(os_gui.get_fa_icon('fa-users'), ' ', T('Groups')),
             _href=URL('settings', 'access_groups'),
             _title=T('Define groups and permission for employees'))


def account_get_link_group(row):
    """
        This function returns the group a user belongs to and shows it as a link
        to a page which allows users to change it.
    """
    no_group = A(os_gui.get_label('default', T('No group')),
                 _href=URL('school_properties', 'account_group_add', args=[row.id]))

    if row.id == 1:
        ret_val = os_gui.get_label('info', "Admins")
    else:  # check if the user had a group
        if db(db.auth_membership.user_id == row.id).count() > 0:  # change group
            query = (db.auth_membership.user_id == row.id)
            left = [db.auth_group.on(db.auth_group.id ==
                                     db.auth_membership.group_id)]
            rows = db(query).select(db.auth_group.ALL,
                                    db.auth_membership.ALL,
                                    left=left)
            for query_row in rows:
                role = query_row.auth_group.role
                if 'user' not in role:
                    ret_val = A(os_gui.get_label('info', role),
                                _href=URL('school_properties',
                                          "account_group_edit",
                                          args=[query_row.auth_membership.id]))
                else:  # no group added yet
                    ret_val = no_group
        else:  # no group added yet
            ret_val = no_group

    return ret_val


@auth.requires(auth.has_membership(group_id='Admins') or \
                auth.has_permission('read', 'teachers'))
def index():
    response.title = T("School")
    response.subtitle = T("Teachers")

    response.view = 'general/only_content.html'

    session.customers_back = 'teachers'
    session.customers_add_back = 'teachers'
    session.settings_groups_back = 'teachers'

    query = (db.auth_user.trashed == False) & \
            (db.auth_user.teacher == True) & \
            (db.auth_user.id > 1)

    db.auth_user.id.readable = False
    db.auth_user.education.readable = False
    db.auth_user.gender.readable = False
    db.auth_user.address.readable = False
    db.auth_user.postcode.readable = False
    db.auth_user.country.readable = False
    db.auth_user.country.readable = False

    delete_onclick = "return confirm('" + \
        T('Remove from teachers list? - This person will still be a customer.') + "');"

    permission = auth.has_membership(group_id='Admins') or \
                 auth.has_permission('update', 'teachers')
    if permission:
        links = [{'header':T('Classes'),
                  'body':index_get_link_classes},
                 {'header':T('Events'),
                  'body':teachers_get_link_workshops},
                 {'header':T('Group (Permissions)'),
                  'body':account_get_link_group},
                 lambda row: A(SPAN(_class="buttontext button",
                                    _title=T("Class types")),
                               SPAN(_class="glyphicon glyphicon-edit"),
                               " " + T("Class types"),
                               _class="btn btn-default btn-sm",
                               _href=URL('edit_classtypes',
                                         vars={'uID':row.id})),
                 lambda row: A(os_gui.get_fa_icon('fa-usd'),
                               " " + T("Payments"),
                               _class="btn btn-default btn-sm",
                               _href=URL('payment_fixed_rate',
                                         vars={'teID':row.id})),
                 lambda row: os_gui.get_button('edit',
                                    URL('customers', 'edit',
                                        args=[row.id]),
                                    T("Edit this teacher")),
                 lambda row: os_gui.get_button(
                     'delete_notext',
                     URL('teachers',
                         'delete',
                         vars={'uID':row.id}),
                     onclick=delete_onclick
                    )
                 ]
    else:
        links = []

    maxtextlengths = {'auth_user.email' : 40}
    headers = {'auth_user.display_name' : T('Teacher'),
               'auth_user.thumbsmall' : ''}

    fields = [ db.auth_user.enabled,
               db.auth_user.thumbsmall,
               db.auth_user.trashed,
               db.auth_user.birthday,
               db.auth_user.display_name,
               db.auth_user.teaches_classes,
               db.auth_user.teaches_workshops ]

    grid = SQLFORM.grid(query,
                        fields=fields,
                        links=links,
                        headers=headers,
                        create=False,
                        editable=False,
                        details=False,
                        csv=False,
                        searchable=False,
                        deletable=False,
                        maxtextlengths=maxtextlengths,
                        orderby=db.auth_user.display_name,
                        ui = grid_ui)
    grid.element('.web2py_counter', replace=None) # remove the counter
    grid.elements('span[title=Delete]', replace=None) # remove text from delete button

    # show back, add and export buttons above teachers list
    back = os_gui.get_button('back', URL('school_properties', 'index'))

    #add = os_gui.get_button('add', URL('teacher_add'))
    ch = CustomersHelper()
    result = ch.get_add_modal(redirect_vars={'teacher':True}, button_class='btn-sm pull-right')
    add = SPAN(result['button'], result['modal'])

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

    content = grid

    back = DIV(add, export, tools)

    return dict(back=back,
                header_tools=header_tools,
                content=content)


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


def index_get_link_classes(row):
    """
        Returns 'yes' if a teacher teaches classes and no if otherwise
    """
    if row.teaches_classes:
        label = os_gui.get_label('success', T('Yes'))
    else:
        label = os_gui.get_label('default', T('No'))

    return A(label, _href=URL('teaches_classes', vars={'uID':row.id}))


def teachers_get_link_workshops(row):
    """
        Returns 'yes' if a teacher teaches workshops and no if otherwise
    """
    if row.teaches_workshops:
        label = os_gui.get_label('success', T('Yes'))
    else:
        label = os_gui.get_label('default', T('No'))

    return A(label, _href=URL('teaches_workshops', vars={'uID':row.id}))


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
def teaches_workshops():
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
        classtypeids.append(unicode(row.school_classtypes_id))

    list_query = (db.school_classtypes.Archived == False)
    rows = db(list_query).select(db.school_classtypes.id,
                                 db.school_classtypes.Name,
                                 orderby=db.school_classtypes.Name)
    for row in rows:
        if unicode(row.id) in classtypeids:
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
        classtypeids.append(unicode(row.id))

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
        stream = cStringIO.StringIO()

        wb.save(stream)
        response.headers['Content-Type']='application/vnd.ms-excel'
        response.headers['Content-disposition']='attachment; filename=' + fname

        return stream.getvalue()


def back_index(var=None):
    return os_gui.get_button('back', URL('index'))


@auth.requires(auth.has_membership(group_id='Admins') or \
                auth.has_permission('read', 'teachers_payment_fixed_rate_default'))
def payment_fixed_rate():
    """
        Configure fixed rate payments for this teacher
    """
    from openstudio.os_teacher import Teacher

    teID = request.vars['teID']
    response.view = 'general/only_content.html'

    customer = Customer(teID)
    response.title = customer.get_name()
    response.subtitle = T("Payments")

    teacher = Teacher(teID)
    content = DIV(
        teacher.get_payment_fixed_rate_default_display(),
        teacher.get_payment_fixed_rate_classes_display(),
        teacher.get_payment_fixed_rate_travel_display()
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
    from openstudio.openstudio import CustomersHelper
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

    ch = CustomersHelper()
    result = ch.classes_add_get_form_date(teID, date)
    form = result['form']
    form_date = result['form_styled']

    db.classes.id.readable = False
    # list of classes
    grid = ch.classes_add_get_list(date, 'tp_fixed_rate', teID)

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


@auth.requires_login()
def payment_fixed_rate_travel_add():
    """
        Add travel allowance for a teacher
    """
    from openstudio.os_forms import OsForms

    teID = request.vars['teID']

    customer = Customer(teID)
    response.title = customer.get_name()
    response.subtitle = T("Add travel allowance")
    response.view = 'general/only_content.html'


    db.teachers_payment_fixed_rate_travel.auth_teacher_id.default = teID
    return_url = payment_fixed_rate_return_url(teID)

    os_forms = OsForms()
    result = os_forms.get_crud_form_create(
        db.teachers_payment_fixed_rate_travel,
        return_url,
    )

    form = result['form']
    back = os_gui.get_button('back', return_url)

    return dict(content=form,
                save=result['submit'],
                back=back)


@auth.requires_login()
def payment_fixed_rate_travel_edit():
    """
        Add travel allowance for a teacher
    """
    from openstudio.os_forms import OsForms

    teID = request.vars['teID']
    tpfrtID = request.vars['tpfrtID']

    customer = Customer(teID)
    response.title = customer.get_name()
    response.subtitle = T("Edit travel allowance")
    response.view = 'general/only_content.html'

    return_url = payment_fixed_rate_return_url(teID)

    os_forms = OsForms()
    result = os_forms.get_crud_form_update(
        db.teachers_payment_fixed_rate_travel,
        return_url,
        tpfrtID
    )

    form = result['form']
    back = os_gui.get_button('back', return_url)

    return dict(content=form,
                save=result['submit'],
                back=back)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('delete', 'teachers_payment_fixed_rate_travel'))
def payment_fixed_rate_travel_delete():
    """
    Delete teacher fixed rate travel allowance
    :return: None
    """
    teID = request.vars['teID']
    tpfrtID = request.vars['tpfrtID']

    query = (db.teachers_payment_fixed_rate_travel.id == tpfrtID)
    db(query).delete()

    session.flash = T('Deleted travel allowance')
    redirect(payment_fixed_rate_return_url(teID))
