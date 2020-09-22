# -*- coding: utf-8 -*-

import string
import random
import os
import pytz
import os_storage

from general_helpers import highlight_submenu
from general_helpers import User_helpers
from general_helpers import set_form_id_and_get_submit_button


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def index():
    response.title = T("Settings")
    response.subtitle = T("")
    response.view = 'general/only_content.html'

    session.settings_groups_back = None

    content = T("Please use the main menu to navigate to shop settings pages")


    return dict(content=content)


def system_get_menu(page):
    """
        Menu for system settings pages
    """
    pages = [
        ['system_general',
        T('General'),
        URL('system_general')],
        ['system_storage',
        T('Storage'),
        URL('system_storage')],
        ['system_organizations',
        T('Organizations'),
        URL('system_organizations')],
        ['system_workflow',
        T('Workflow'),
        URL('system_workflow')]
    ]

    return os_gui.get_submenu(pages, page, horizontal=True, htype='tabs')


def system_general():
    """
        General OpenStudio settings
    """
    response.title = T('System Settings')
    response.subtitle = T('General')
    response.view = 'general/tabs_menu.html'

    split_location = get_sys_property('Customer_ShowLocation')
    show_welcome = get_sys_property('ShowWelcomeMessage')
    time_zone = get_sys_property('TimeZone')
    date_format = get_sys_property('DateFormat')
    sys_hostname = get_sys_property('sys_hostname')

    for f in DATE_FORMATS:
        if f[1] == date_format:
            date_format = f[0]

    form = SQLFORM.factory(
        Field('split_location', 'boolean',
              default=split_location,
              label=T('Separate customers by location')),
        Field('show_welcome', 'boolean',
              default=show_welcome,
              label=T('Show welcome message on Pin board')),
        Field('date_format',
              requires=IS_IN_SET(DATE_FORMATS,
                                 zero=T("Please select...")),
              default=date_format,
              label=T('Date format')),
        Field('time_zone',
              requires=IS_IN_SET(pytz.common_timezones,
                                 zero=T("Please select...")),
              default=time_zone,
              label=T('Time Zone')),
        Field('sys_hostname',
              requires=IS_NOT_EMPTY(),
              default=sys_hostname,
              label=T('Hostname of this OpenStudio installation'),
              comment=T("eg. demo.openstudioproject.com (without http or https)")),
        submit_button=T("Save"),
        separator=' ',
        formstyle='bootstrap3_stacked'
    )

    form_id = "MainForm"
    form_element = form.element('form')
    form['_id'] = form_id

    elements = form.elements('input, select, textarea')
    for element in elements:
        element['_form'] = form_id

    submit = form.element('input[type=submit]')

    if form.accepts(request.vars, session):
        # check separate by location (possible values are None and "on")
        split_location = request.vars['split_location']
        row = db.sys_properties(Property='Customer_ShowLocation')
        if not row:
            db.sys_properties.insert(Property='Customer_ShowLocation',
                                     PropertyValue=split_location)
        else:
            row.PropertyValue = split_location
            row.update_record()

        # update session variable
        if split_location == "on":
            session.show_location = True
        else:
            session.show_location = False

        # check show welcome message
        show_welcome = request.vars['show_welcome']
        row = db.sys_properties(Property='ShowWelcomeMessage')
        if not row:
            db.sys_properties.insert(Property='ShowWelcomeMessage',
                                     PropertyValue=show_welcome)
        else:
            row.PropertyValue = show_welcome
            row.update_record()

        # check date_format
        date_format = request.vars['date_format']
        row = db.sys_properties(Property='DateFormat')
        if not row:
            db.sys_properties.insert(
                Property='DateFormat', PropertyValue=date_format)
        else:
            row.PropertyValue = date_format
            row.update_record()
        session.date_format = date_format

        # check time_zone
        time_zone = request.vars['time_zone']
        row = db.sys_properties(Property='TimeZone')
        if not row:
            db.sys_properties.insert(
                Property='TimeZone', PropertyValue=time_zone)
        else:
            row.PropertyValue = time_zone
            row.update_record()

        # hostname
        sys_hostname = request.vars['sys_hostname']
        row = db.sys_properties(Property='sys_hostname')
        if not row:
            db.sys_properties.insert(
                Property='sys_hostname', PropertyValue=sys_hostname)
        else:
            row.PropertyValue = sys_hostname
            row.update_record()


        # Clear cache
        cache_clear_sys_properties()
        # User feedback
        session.flash = T('Saved')
        # reload so the user sees how the values are stored in the db now
        redirect(URL('system_general'))

    content = DIV(DIV(form, _class='col-md-6'),
                  _class='row')

    menu = system_get_menu(request.function)

    return dict(content=content,
                menu=menu,
                save=submit)


def system_workflow():
    """
        General OpenStudio settings
    """
    response.title = T('System Settings')
    response.subtitle = T('General')
    response.view = 'general/tabs_menu.html'


    class_attendance_max_complementary_checkins = get_sys_property('class_attendance_max_complementary_checkins')
    subscription_pauses_min_duration = get_sys_property('subscription_pauses_min_duration')
    subscription_max_pauses = get_sys_property('subscription_max_pauses')
    subscription_first_invoice_two_terms = get_sys_property('subscription_first_invoice_two_terms')
    system_enable_class_checkin_trialclass = get_sys_property('system_enable_class_checkin_trialclass')
    system_enable_class_checkin_reconcile_later = get_sys_property('system_enable_class_checkin_reconcile_later')
    system_allow_trial_cards_for_existing_customers = get_sys_property('system_allow_trial_cards_for_existing_customers')
    system_allow_trial_classes_for_existing_customers = get_sys_property('system_allow_trial_classes_for_existing_customers')


    form = SQLFORM.factory(
        Field('system_enable_class_checkin_reconcile_later', 'boolean',
              default=system_enable_class_checkin_reconcile_later,
              label=T('Enable reconcile later class booking option'),
              comment=T('Show or hide the reconcile later class booking option in the back-end')),
        Field('system_enable_class_checkin_trialclass', 'boolean',
              default=system_enable_class_checkin_trialclass,
              label=T('Enable trial class booking option'),
              comment=T('Show or hide the trial class booking option in the back-end')),
        Field('system_allow_trial_cards_for_existing_customers', 'boolean',
              default=system_allow_trial_cards_for_existing_customers,
              label=T('Allow existing customers to buy a trial card'),
              comment=T(
                  'Disable to prevent trial products from showing in backend for any customers who have or have had a subscription or card.')),
        Field('system_allow_trial_classes_for_existing_customers', 'boolean',
              default=system_allow_trial_classes_for_existing_customers,
              label=T('Allow existing customers to book a trial class'),
              comment=T(
                  'Disable to prevent trial class booking options from showing in backend for any customers who have or have had a subscription or card.')),
        Field('class_attendance_max_complementary_checkins',
              default=class_attendance_max_complementary_checkins,
              label=T('Max. class complementary check-ins'),
              comment=T('Maximum number of complementary check-ins for each class')),
        Field('subscription_pauses_min_duration', 'integer',
              default=subscription_pauses_min_duration,
              label=T('Min. duration of subscription pauses (in days)'),
              comment=T('Minimum length for subscription pauses in days. A warning will be shown if a pause is shorter than this length')),
        Field('subscription_max_pauses', 'integer',
              default=subscription_max_pauses,
              label=T('Max. pauses for each subscription in a year'),
              comment=T('Maximum number of subscription pauses in a year. A warning will be shown if a subscription is paused more.')),
        Field('subscription_first_invoice_two_terms', 'boolean',
              default=subscription_first_invoice_two_terms,
              label=T('Subscription first term bill two months'),
              comment=T('Enable to bill the current month and the next month on the first invoice for a subscription.')),
        submit_button=T("Save"),
        separator=' ',
        formstyle='bootstrap3_stacked'
    )

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']

    if form.process().accepted:
        form_vars = [
            'system_allow_trial_cards_for_existing_customers',
            'system_allow_trial_classes_for_existing_customers',
            'system_enable_class_checkin_trialclass',
            'system_enable_class_checkin_reconcile_later',
            'class_attendance_max_complementary_checkins',
            'subscription_pauses_min_duration',
            'subscription_max_pauses',
            'subscription_first_invoice_two_terms'
        ]

        for fvar in form_vars:
            if fvar in request.vars:
                set_sys_property(
                    fvar,
                    request.vars[fvar]
                )
            else:
                set_sys_property(
                    fvar,
                    None
                )

        # Clear cache
        cache_clear_sys_properties()
        # User feedback
        session.flash = T('Saved')
        # reload so the user sees how the values are stored in the db now
        redirect(URL('system_workflow'))

    content = DIV(DIV(form, _class='col-md-12'),
                  _class='row')

    menu = system_get_menu(request.function)

    return dict(content=content,
                menu=menu,
                save=submit)


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def system_storage():
    """
        Shows a page with the used and available storage
    """
    response.title = T("System Settings")
    response.subtitle = T("Storage")

    row = db.sys_properties(Property='storage_allowed_space')
    allowed_space = int(row.PropertyValue)

    uploads_dir = os.path.join(request.folder, 'uploads')
    used_space = os_storage.get_size(uploads_dir)
    available_space = allowed_space - used_space

    data = [available_space, used_space]
    labels = [T('Available'), T('Used')]
    json_data = []
    color = dict(red=82, green=136, blue=154)
    i = 0
    for item in data:
        current_color = 'rgb(' + str(color['red']) + ',' + \
            str(color['green']) + ',' + \
            str(color['blue']) + ')'
        json_data.append(dict(label=labels[i],
                              value=data[i],
                              color=current_color,
                              highlight="rgb(17,160,94)"))
        color['red'] += 20
        color['green'] += 20
        color['blue'] += 20

        i += 1

    data_table = TABLE(TR(TH(T("Space")), TH(T("MB"))),
                       _class="table table-condensed")
    i = 0
    for value in data:
        data_table.append(TR(labels[i], value))
        i += 1

    data_table = os_gui.get_box_table(T("Storage info"),
                                      data_table)

    menu = system_get_menu(request.function)

    return dict(data_table=data_table,
                json_data=json_data,
                menu=menu,
                left_sidebar_enabled=True)


@auth.requires(auth.has_membership(group_id='Admins') or \
                auth.has_permission('read', 'sys_organizations'))
def system_organizations():
    response.title = T("Settings")
    response.subtitle = T("Organizations")
    response.view = 'general/tabs_menu.html'

    show = 'current'
    query = (db.sys_organizations.Archived == False)

    if 'show_archive' in request.vars:
        show = request.vars['show_archive']
        session.settings_sys_organizations_show = show
        if show == 'current':
            query = (db.sys_organizations.Archived == False)
        elif show == 'archive':
            query = (db.sys_organizations.Archived == True)
    elif session.settings_sys_organizations_show == 'archive':
            query = (db.sys_organizations.Archived == True)
    else:
        session.settings_sys_organizations_show = show

    db.sys_organizations.id.readable=False
    #db.sys_organizations.DefaultOrganization.readable=True


    #TODO: check if there's a default organization, if not display a message
    #TODO: add link to set a default organization

    fields = [ db.sys_organizations.Archived,
               db.sys_organizations.Name,
               db.sys_organizations.Registration,
               db.sys_organizations.TaxRegistration,
               db.sys_organizations.DefaultOrganization ]
    links = [ system_organizations_get_link_set_default,
              lambda row: os_gui.get_button('edit',
                                     URL('system_organization_edit', vars={'soID':row.id}),
                                     T("Edit this organization")),
              system_organizations_get_link_archive ]
    grid = SQLFORM.grid(query,
        fields=fields,
        links=links,
        create=False,
        editable=False,
        deletable=False,
        details=False,
        searchable=False,
        csv=False,
        ondelete=cache_clear_sys_organizations,
        orderby = db.sys_organizations.Name,
        ui = grid_ui)
    grid.element('.web2py_counter', replace=None) # remove the counter
    grid.elements('span[title=Delete]', replace=None) # remove text from delete button

    add_url = URL('system_organization_add')
    add = os_gui.get_button('add', add_url, T("Add a new organization"), _class='pull-right')

    archive_buttons = os_gui.get_archived_radio_buttons(
        session.settings_sys_organizations_show)

    back = DIV(add, archive_buttons)

    menu = system_get_menu(request.function)

    return dict(content=grid, back=back, menu=menu)


def system_organizations_get_link_set_default(row):
    """
        Called from the index function. Add a "set default" link for all not default organizations
    """
    set_default = A(T('Set default'),
                    _href=URL('system_organizations_set_default', vars={'soID': row.id}))

    if row.DefaultOrganization:
        set_default = SPAN(os_gui.get_label('success', T('Default')), _class='w2p_grid_button_padding')

    return set_default


def system_organizations_get_link_archive(row):
    """
        Called from the index function. Changes title of archive button
        depending on whether a language is archived or not
    """
    if row.Archived:
        tt = T("Move to current")
    else:
        tt = T("Archive")

    return os_gui.get_button('archive',
                             URL('system_organizations_archive', vars={'soID':row.id}),
                             tooltip=tt)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('update', 'system_organizations'))
def system_organizations_set_default():
    """
        Set an organization as default
    """
    soID = request.vars['soID']

    query = (db.sys_organizations.id > 0)
    db(query).update(DefaultOrganization = False)

    query = (db.sys_organizations.id == soID)
    db(query).update(DefaultOrganization = True)

    cache_clear_sys_organizations()

    redirect(URL('system_organizations'))


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('update', 'system_organizations'))
def system_organizations_archive():
    """
        This function archives an organization
        request.vars[sdID] is expected to be from db.system_organizations
    """
    def go_back():
        redirect(URL('system_organizations'))

    soID = request.vars['soID']
    if not soID:
        session.flash = T('Unable to (un)archive organization')
    else:
        row = db.sys_organizations(soID)

        if row.DefaultOrganization:
            session.flash = T("The default organizations can't be archived")
            go_back()

        if row.Archived:
            session.flash = T('Moved to current')
        else:
            session.flash = T('Archived')

        row.Archived = not row.Archived
        row.update_record()

    cache_clear_sys_organizations()

    go_back()


@auth.requires_login()
def system_organization_add():
    """
        This function shows an add page for an organization
    """
    response.title = T("Settings")
    response.subtitle = T('New Organization')
    response.view = 'general/only_content.html'

    if len(ORGANIZATIONS) < 1:
        db.sys_organizations.DefaultOrganization.default = True

    return_url = URL('system_organizations')

    crud.messages.submit_button = T("Save")
    crud.messages.record_created = T("Saved")
    crud.settings.create_next = return_url
    crud.settings.create_onaccept = cache_clear_sys_organizations
    crud.settings.formstyle = 'bootstrap3_stacked'
    form = crud.create(db.sys_organizations)

    form_id = "MainForm"
    form_element = form.element('form')
    form['_id'] = form_id

    elements = form.elements('input, select, textarea')
    for element in elements:
        element['_form'] = form_id

    textareas = form.elements('textarea')
    for textarea in textareas:
        textarea['_class'] += ' tmced'

    submit = form.element('input[type=submit]')

    back = os_gui.get_button('back', return_url)

    return dict(content=form, back=back, save=submit)


@auth.requires_login()
def system_organization_edit():
    """
        This function shows an edit page for a language
        request.vars['soID'] is expected to be db.sys_organizations.id
    """
    soID = request.vars['soID']

    response.title = T("Settings")
    response.subtitle = T('Edit Organization')
    response.view = 'general/only_content.html'

    return_url = URL('system_organizations')

    crud.messages.submit_button = T("Save")
    crud.messages.record_updated = T("Saved")
    crud.settings.update_next = return_url
    crud.settings.update_onaccept = cache_clear_sys_organizations
    crud.settings.formstyle = 'bootstrap3_stacked'
    form = crud.update(db.sys_organizations, soID)

    form_id = "MainForm"
    form_element = form.element('form')
    form['_id'] = form_id

    elements = form.elements('input, select, textarea')
    for element in elements:
        element['_form'] = form_id

    textareas = form.elements('textarea')
    for textarea in textareas:
        textarea['_class'] += ' tmced'

    submit = form.element('input[type=submit]')

    back = os_gui.get_button('back', return_url)

    return dict(content=form, back=back, save=submit)


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def email_outgoing():
    """
        Server settings
    """
    response.title = T('Email Settings')
    response.subtitle = T('Outgoing email')
    response.view = 'general/content_left_sidebar.html'

    smtp_signature = get_sys_property('smtp_signature')

    form = SQLFORM.factory(
        Field("smtp_signature", 'text',
              default=smtp_signature,
              label=T("Email signature")),
        submit_button=T("Save"),
        separator=' ',
        formstyle='bootstrap3_stacked')

    signature = form.element('#no_table_smtp_signature')
    signature['_class'] += ' tmced'

    if form.accepts(request.vars, session):
        # check smtp_signature
        setting = request.vars['smtp_signature']
        row = db.sys_properties(Property='smtp_signature')
        if not row:
            db.sys_properties.insert(
                Property='smtp_signature', PropertyValue=setting)
        else:
            row.PropertyValue = setting
            row.update_record()

        # Clear cache
        cache_clear_sys_properties()
        # User feedback
        session.flash = T('Saved Email settings')
        # reload so the user sees how the values are stored in the db now
        redirect(URL('email_outgoing'))

    back = os_gui.get_button('back', URL('index'), _class='full-width')

    return dict(content=DIV(form, _class='col-md-6'),
                back=back,
                left_sidebar_enabled=True)


def financial_get_menu(page=None):
    """
        Menu for financial settings pages
    """
    pages = [['financial_currency',
              T('Currency'),
              URL('financial_currency')],
             ['financial_invoices',
              T('Invoices'),
              URL('financial_invoices_groups')],
             ['financial_tax_rates',
              T('Tax rates'),
              URL('financial_tax_rates')],
             ['financial_payment_methods',
              T('Payment methods'),
              URL('financial_payment_methods')],
             ['financial_costcenters',
              T('Cost centers'),
              URL('financial_costcenters')],
             ['financial_glaccounts',
              T('G/L Accounts'),
              URL('financial_glaccounts')],
             ['financial_dd_categories',
              T('Direct debit extra'),
              URL('financial_dd_categories')],
             ['financial_teacher_payments',
              T('Teacher payments'),
              URL('financial_teacher_payments')]
             ]

    return os_gui.get_submenu(pages, page, horizontal=True, htype='tabs')


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def financial_teacher_payments():
    """
        Settings for teacher payments
    """
    response.title = T('Financial Settings')
    response.subtitle = T('Teacher payments')
    response.view = 'general/tabs_menu.html'

    tprt_property = 'TeacherPaymentRateType'
    tprt = get_sys_property(tprt_property)

    form = SQLFORM.factory(
        Field('tprt',
              requires=IS_IN_SET(teacher_payment_classes_rate_types,
                                 zero=None),
              default=tprt,
              label=T('Teacher Payments Rate type')),
        submit_button=T("Save"),
        separator=' ',
        formstyle='bootstrap3_stacked')

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']

    if form.accepts(request.vars, session):
        # check rate type
        set_sys_property(
            tprt_property,
            request.vars['tprt']
        )

        # Clear cache
        cache_clear_sys_properties()
        # User feedback
        session.flash = T('Saved')

        # Clear cache
        cache_clear_sys_properties()
        # User feedback
        session.flash = T('Saved')
        # reload so the user sees how the values are stored in the db now
        redirect(URL('financial_teacher_payments'))

    menu = financial_get_menu(request.function)

    return dict(content=DIV(DIV(form, _class="col-md-12"),
                            _class='row'),
                menu=menu,
                save=submit)


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings_finance'))
def financial_costcenters():
    """
    List finance costcenters
    """
    from openstudio.os_accounting_costcenters import AccountingCostCenters

    response.title = T('Financial Settings')
    response.subtitle = T('Cost centers')
    response.view = 'general/tabs_menu.html'

    if 'show_archive' in request.vars:
        show = request.vars['show_archive']
        session.settings_financial_costcenters_show = show

    archive = False
    if session.settings_financial_costcenters_show == 'archive':
        archive = True

    archive_buttons = os_gui.get_archived_radio_buttons(
        session.settings_financial_costcenters_show or 'current'
    )

    acc = AccountingCostCenters()
    content = DIV(archive_buttons, acc.list_formatted(archive))


    add = os_gui.get_button(
        'add',
        URL('financial_costcenter_add')
    )
    menu = financial_get_menu(request.function)


    return dict(content=content,
                menu=menu,
                tools=add)
                # save=submit)


def financial_costcenter_get_return_url():
    return URL('settings', 'financial_costcenters')


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('create', 'accounting_costcenters'))
def financial_costcenter_add():
    """

    :return:
    """
    from openstudio.os_forms import OsForms

    response.title = T('Financial Settings')
    response.subtitle = T('Cost centers')
    response.view = 'general/tabs_menu.html'

    return_url = financial_costcenter_get_return_url()

    os_forms = OsForms()
    result = os_forms.get_crud_form_create(
        db.accounting_costcenters,
        return_url,
        message_record_created=T("Saved")
    )

    form = result['form']
    back = os_gui.get_button('back', return_url)

    content = DIV(
        H4(T('Add cost center')),
        form
    )

    menu = financial_get_menu('financial_costcenters')

    return dict(content=content,
                save=result['submit'],
                back=back,
                menu=menu)


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('update', 'accounting_costcenters'))
def financial_costcenter_edit():
    """

    :return:
    """
    from openstudio.os_forms import OsForms

    response.title = T('Financial Settings')
    response.subtitle = T('Cost centers')
    response.view = 'general/tabs_menu.html'

    acID = request.vars['acID']

    return_url = financial_costcenter_get_return_url()

    os_forms = OsForms()
    result = os_forms.get_crud_form_update(
        db.accounting_costcenters,
        return_url,
        acID
    )

    form = result['form']
    back = os_gui.get_button('back', return_url)

    content = DIV(
        H4(T('Edit cost center')),
        form
    )

    menu = financial_get_menu('financial_costcenters')

    return dict(content=content,
                save=result['submit'],
                back=back,
                menu=menu)


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('update', 'accounting_costcenters'))
def financial_costcenter_archive():
    """

    :return:
    """
    from openstudio.os_accounting_costcenter import AccountingCostCenter
    acID = request.vars['acID']

    ac = AccountingCostCenter(acID)
    ac.archive()

    return_url = financial_costcenter_get_return_url()

    redirect(return_url)



@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings_finance'))
def financial_glaccounts():
    """
    List finance costcenters
    """
    from openstudio.os_accounting_glaccounts import AccountingGLAccounts

    response.title = T('Financial Settings')
    response.subtitle = T('General Ledger accounts')
    response.view = 'general/tabs_menu.html'

    if 'show_archive' in request.vars:
        show = request.vars['show_archive']
        session.settings_financial_glaccounts_show = show

    archive = False
    if session.settings_financial_glaccounts_show == 'archive':
        archive = True

    archive_buttons = os_gui.get_archived_radio_buttons(
        session.settings_financial_glaccounts_show or 'current'
    )

    acg = AccountingGLAccounts()
    content = DIV(archive_buttons, acg.list_formatted(archive))


    add = os_gui.get_button(
        'add',
        URL('financial_glaccount_add')
    )
    menu = financial_get_menu(request.function)


    return dict(content=content,
                menu=menu,
                tools=add)
                # save=submit)


def financial_glaccount_get_return_url():
    return URL('settings', 'financial_glaccounts')


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('create', 'accounting_glaccounts'))
def financial_glaccount_add():
    """

    :return:
    """
    from openstudio.os_forms import OsForms

    response.title = T('Financial Settings')
    response.subtitle = T('General ledger accounts')
    response.view = 'general/tabs_menu.html'

    return_url = financial_glaccount_get_return_url()

    os_forms = OsForms()
    result = os_forms.get_crud_form_create(
        db.accounting_glaccounts,
        return_url,
        message_record_created=T("Saved")
    )

    form = result['form']
    back = os_gui.get_button('back', return_url)

    content = DIV(
        H4(T('Add General ledger account')),
        form
    )

    menu = financial_get_menu('financial_glaccounts')

    return dict(content=content,
                save=result['submit'],
                back=back,
                menu=menu)


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('update', 'accounting_glaccounts'))
def financial_glaccount_edit():
    """

    :return:
    """
    from openstudio.os_forms import OsForms

    response.title = T('Financial Settings')
    response.subtitle = T('General ledger accounts')
    response.view = 'general/tabs_menu.html'

    agID = request.vars['agID']

    return_url = financial_glaccount_get_return_url()

    os_forms = OsForms()
    result = os_forms.get_crud_form_update(
        db.accounting_glaccounts,
        return_url,
        agID
    )

    form = result['form']
    back = os_gui.get_button('back', return_url)

    content = DIV(
        H4(T('Edit General ledger account')),
        form
    )

    menu = financial_get_menu('financial_glaccounts')

    return dict(content=content,
                save=result['submit'],
                back=back,
                menu=menu)


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('update', 'accounting_glaccounts'))
def financial_glaccount_archive():
    """

    :return:
    """
    from openstudio.os_accounting_glaccount import AccountingGLAccount
    agID = request.vars['agID']

    ag = AccountingGLAccount(agID)
    ag.archive()

    redirect(financial_glaccount_get_return_url())


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def financial_currency():
    """
        Settings for currency
    """
    response.title = T('Financial Settings')
    response.subtitle = T('Currency')
    response.view = 'general/tabs_menu.html'

    currency = get_sys_property('Currency')
    currency_symbol = get_sys_property('CurrencySymbol')
    only_iban_account_numbers = get_sys_property('OnlyIBANAccountNumbers')

    form = SQLFORM.factory(
        Field('currency', length=3,
              requires=IS_LENGTH(3, 3,
                                 error_message=T('Enter 3 letters representing the \
                                         currency, eg. "EUR" or "USD"')),
              default=currency,
              label=T('Currency')),
        Field('currency_symbol',
              requires=IS_LENGTH(maxsize=3,
                                 error_message=T('Enter the currency symbol (max. 3 characters)')),
              default=currency_symbol,
              label=T('Currency symbol')),
        Field('only_iban_account_numbers', 'boolean',
              default=only_iban_account_numbers,
              label=T('Only accept IBAN account number as customer bank account')),
        submit_button=T("Save"),
        separator=' ',
        formstyle='bootstrap3_stacked')

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']

    if form.accepts(request.vars, session):
        # check currency
        # make sure it's upper case.
        currency = request.vars['currency'].upper()
        row = db.sys_properties(Property='Currency')
        if not row:
            db.sys_properties.insert(
                Property='Currency', PropertyValue=currency)
        else:
            row.PropertyValue = currency
            row.update_record()

        # check currency symbol
        currency_symbol = request.vars['currency_symbol']
        row = db.sys_properties(Property='CurrencySymbol')
        if not row:
            db.sys_properties.insert(
                Property='CurrencySymbol', PropertyValue=currency_symbol)
        else:
            row.PropertyValue = currency_symbol
            row.update_record()

        # check IBAN
        only_iban_account_numbers = request.vars['only_iban_account_numbers']
        row = db.sys_properties(Property='OnlyIBANAccountNumbers')
        if not row:
            db.sys_properties.insert(
                Property='OnlyIBANAccountNumbers', PropertyValue=only_iban_account_numbers)
        else:
            row.PropertyValue = only_iban_account_numbers
            row.update_record()

        # Clear cache
        cache_clear_sys_properties()
        # User feedback
        session.flash = T('Saved')
        # reload so the user sees how the values are stored in the db now
        redirect(URL('financial_currency'))

    menu = financial_get_menu(request.function)

    return dict(content=DIV(DIV(form, _class="col-md-6"),
                            _class='row'),
                menu=menu,
                save=submit)


# helpers begin

def access_get_back(var=None):
    """
        Returns back button for access main menu pages
    """
    if session.settings_groups_back == 'teachers':
        url = URL('teachers', 'index')
    elif session.settings_groups_back == 'school_employees':
        url = URL('school_properties', 'employees')
    else:
        url = URL('index')


    return os_gui.get_button('back', url)


def access_get_menu(page):
    """
        This function returns the submenu used for the users/groups pages.
        It takes on argument, page, which is used to highlight the active element.
    """
    pages = (['access_groups',
              T("Groups"),
              URL('access_groups')],
             ['access_api_users',
              T("API Users"),
              URL('access_api_users')])

    return os_gui.get_submenu(pages, page, horizontal=True, htype='tabs')

# helpers end


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'auth_group'))
def access_groups():
    """
        This function shows a page which lists all user groups
    """
    def get_edit_button(row):
        if not row.id == 1:
            return os_gui.get_button('edit', URL('access_group_edit', args=[row.id]))

    def get_permissions_button(row):
        if not row.id == 1:
            return A(SPAN(_class='glyphicon glyphicon-lock'), ' ',
                     T("Permissions"),
                     _href=URL("access_group_permissions", args=[row.id]),
                     _class='btn btn-default btn-sm')

    response.title = T("Access Settings")
    response.subtitle = T("OpenStudio user groups")
    response.view = 'general/tabs_menu.html'

    db.auth_group.id.readable = False

    links = [get_permissions_button,
             get_edit_button]
    maxtextlengths = {'auth_group.role': 30, 'auth_group.description': 50}
    query = ~(db.auth_group.role.contains('user_'))  # '~' is the NOT operator

    delete_permission = auth.has_membership(group_id='Admins') or \
        auth.has_permission('delete', 'auth_group')

    grid = SQLFORM.grid(query, links=links, user_signature=False,
                        create=False,
                        editable=False,
                        details=False,
                        csv=False,
                        searchable=False,
                        deletable=delete_permission,
                        maxtextlengths=maxtextlengths,
                        orderby=db.auth_group.role,
                        field_id=db.auth_group.id,
                        ui=grid_ui)
    grid.element('.web2py_counter', replace=None)  # remove the counter
    # remove text from delete button
    grid.elements('span[title=Delete]', replace=None)

    add_url = URL('access_group_add')
    add = os_gui.get_button('add', add_url, T("Add a new group"))


    menu = access_get_menu(request.function)

    return dict(content=grid,
                menu=menu,
                add=add)


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def access_group_add():
    """
        This function shows a page to add a new user group
    """
    response.title = T("New user group")
    response.subtitle = T("")
    response.view = 'general/only_content.html'

    return_url = URL('access_groups')

    crud.messages.submit_button = T("Save")
    crud.messages.record_created = T("Added user group")
    crud.settings.create_next = return_url
    form = crud.create(db.auth_group)

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']

    back = os_gui.get_button('back', return_url)

    return dict(content=form, back=back, save=submit)


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def access_group_edit():
    """
        This function shows an edit page for a user group
        request.args[0] is expected to be the groupID
    """
    groupID = request.args[0]
    response.title = T("Edit user group")
    response.subtitle = T("")
    response.view = 'general/only_content.html'

    return_url = URL('access_groups')

    crud.messages.submit_button = T("Save")
    crud.messages.record_updated = T("Updated user group")
    crud.settings.update_next = return_url
    crud.settings.update_deletable = False
    form = crud.update(db.auth_group, groupID)

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']

    back = os_gui.get_button('back', return_url)

    return dict(content=form, back=back, save=submit)


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('update', 'auth_group_permissions'))
def access_group_permissions():
    """
        This page allows the user to configure the permissions of a group
        request.args[0] is expected to the the id from auth_group (gID)
    """
    def append_table(permissions_list, parent=None, depth=0):
        """
            This is a helper function to make a nice overview from the permissions list.
            Layout permissions list: [ name, label, bold(boolean), [optional submenu list] ]
        """
        table = TABLE(TR(TH(T('Permission')),
                         TH()),
                      _class='unselectable',
                      _id=permissions_list[1])
        odd = False

        for field in permissions_list[0]:
            """
                check if we're at the top level, if so set an id for the
                container div
            """

            # process permissions list
            value = check_permission(group_id, field[0])
            row = TR(TD(field[1],
                        _class="level_" + str(depth)),
                     TD(INPUT(_type="checkbox",
                              _name=field[0],
                              value=value),
                        _class='checkbox'))
            table.append(row)
            if parent is None:
                parent = table
            else:
                if depth != 0:
                    parent.append(row)
            try:
                if isinstance(field[2], list):
                    append_table([field[2], None], parent, depth + 1)
            except IndexError:
                pass
        return parent

    def check_permission(group_id, permission):
        """
            This function checks whether a group has a certain permission
        """
        (obj, name) = permission.split('-')
        row = db.auth_permission(group_id=group_id, name=name, table_name=obj)
        if row:
            return True
        else:
            return False

    group_id = request.args[0]
    response.title = T("Settings")
    row = db.auth_group(group_id)
    response.subtitle = T("Edit permissions for") + " " + row.role

    pinboard_permissions = [
        ['pinboard-read', T('View pin board'), [
            ['announcements-read', T('View announcements')],
            ['announcements-create', T("Add announcements")],
            ['announcements-update', T("Edit announcements")],
            ['announcements-delete', T("Delete announcements")],
            ['upcoming_classes-read', T('View upcoming classes (for teachers only)')]]],
    ]

    reports_permissions = [
        ['reports-read', T("View reports"), [
            ['reports_customers-read', T("View customers reports")],
            ['reports_classcards-read', T("View class cards reports")],
            ['reports_subscriptions-read', T("View subscriptions reports")],
            ['reports_memberships-read', T("View memberships report(s)")],
            ['reports_dropinclasses-read', T("View drop in classes reports")],
            ['reports_trial-read', T("View trial classes & trial cards reports")],
            ['reports_attendance-read', T("View attendance reports")],
            ['reports_teacherclasses-read', T("View teacher classes reports"), [
                ['reports_teacherclasses_revenue-read', T('View revenue for each class')]
            ]],
            ['reports_revenue-read', T("View revenue report")],
            ['reports_tax_summary-read', T("View tax summary report")],
            ['reports_discovery-read', T("View Discovery report")],
            ['reports_retention-read', T("View Retention report")],
            ['reports_geography-read', T("View Geography report"), [
                ['postcode_groups-read', T("View postcode groups")],
                ['postcode_groups-create', T("Add postcode groups")],
                ['postcode_groups-update', T("Edit postcode groups")],
                ['postcode_groups-delete', T("Delete postcode groups")]
            ]]
        ]]
    ]

    finance_permisisons = [
        ['finance-read', T("View finance menu"), [
            ['invoices-read', T('View invoices'), [
                ['invoices-create', T('Add invoices')],
                ['invoices-update', T('Edit invoices')],
                ['invoices-delete', T('Delete invoices')],
                ['invoices_items-create', T('Add invoice items')],
                ['invoices_items-update', T('Edit invoice items')],
                ['invoices_items-delete', T('Delete invoice items')],
                ['invoices_payments-create', T('Add invoice payments')],
                ['invoices_payments-update', T('Edit invoice payments')],
                ['invoices_payments-delete', T('Delete invoice payments')]]],
            ['receipts-read', T("View receipts")],
            ['accounting_cashbooks-read', T("View cash books"), [
                ['accounting_cashbooks_cash_count-create', T("Set cash book balance")],
                ['accounting_cashbooks_cash_count-update', T("Edit cash book balance")]
            ]],
            ['accounting_expenses-read', T("View Expenses"), [
                ['accounting_expenses-create', T("Set expenses")],
                ['accounting_expenses-update', T("Edit expenses")],
                ['accounting_expenses-delete', T("Delete expenses")],
            ]],
            ['payment_batches-read', T('View payment batches'), [
                ['payment_batches-create', T('Add payment batches')],
                ['payment_batches-update', T('Edit payment batches')],
                ['payment_batches-delete', T('Delete payment batches')]]],
            ['reports_direct_debit_extra-read', T('View direct debit extra')],
            ['payment_methods-read', T('View payment methods')],
            ['tax_rates-read', T('View tax rates')]
            ],
         ]
    ]

    shop_permissions = [
        ['shop_manage-read', T("View shop menu"), [
            ['customers_orders-read', T('View orders'), [
                ['customers_orders-update', T('Edit orders')],
                ['customers_orders-delete', T('Delete orders')]]],
            ['shop_manage_workflow-read', T('Manage shop workflow')],
            ['shop_categories-read', T('View categories'), [
                ['shop_categories-create', T('Add categories')],
                ['shop_categories-update', T('Edit categories')],
                ['shop_categories-delete', T('Delete categories')],
                ['shop_categories_products-view', T('View products in categories'), [
                    ['shop_categories_products-create', T('Add products to categories')],
                    ['shop_categories_products-delete', T('Delete products from categories')]]]]],
            ['shop_products-read', T('View products'), [
                ['shop_products-create', T('Add products')],
                ['shop_products-update', T('Edit products')],
                ['shop_products-delete', T('Delete products')],
                ['shop_products_variants-read', T('Read product variants'), [
                    ['shop_products_variants-create', T('Add product variants')],
                    ['shop_products_variants-update', T('Edit product variants')],
                    ['shop_products_variants-delete', T('Delete product variants')]]]]],
            ['shop_products_sets-read', T('View product sets'), [
                ['shop_products_sets-create', T('Add product sets')],
                ['shop_products_sets-update', T('Update product sets')],
                ['shop_products_sets-delete', T('Delete product sets')],
                ['shop_products_options-read', T('View product options in sets'), [
                    ['shop_products_sets_options-create', T('Add product options to a set')],
                    ['shop_products_sets_options-update', T('Edit product options in a set')],
                    ['shop_products_sets_options-delete', T('Delete product options from a set')],
                    ['shop_products_sets_options_values-read', T('View product option values'), [
                        ['shop_products_sets_options_values-create', T('Add product option values')],
                        ['shop_products_sets_options_values-update', T('Edit product option values')],
                        ['shop_products_sets_options_values-delete', T('Delete product option values')]]]
                ]],
            ]],
            ['shop_brands-read', T('View brands'), [
                ['shop_brands-create', T('Add brands')],
                ['shop_brands-update', T('Edit brands')],
                ['shop_brands-delete', T('Delete brands')]]],
            ['shop_suppliers-read', T('View suppliers'), [
                ['shop_suppliers-create', T('Add suppliers')],
                ['shop_suppliers-update', T('Edit suppliers')],
                ['shop_suppliers-delete', T('Delete suppliers')]]],
            ]
         ]
    ]

    tasks_permissions = [
        ['tasks-read', T("View tasks"), [
            ['tasks-create', T('Add tasks')],
            ['tasks-update', T('Edit tasks')],
            ['tasks-delete', T('Delete tasks')],
            ['tasks-assign', T('Assign tasks to other users')]]
         ]
    ]

    customers_permissions = [
        ['auth_user-read', T("View customers"), [
            ['auth_user-create', T("Add customers")],
            ['auth_user-update', T("Edit customers' general info"), [
                ['customers_contact-update', T("View & Update contact info")],
                ['customers_address-update', T("View & Update address info")],
                ['customers_memberships-read', T("View memberships"), [
                    ['customers_memberships-create', T("Add memberships")],
                    ['customers_memberships-update', T("Edit memberships")],
                    ['customers_memberships-delete', T("Delete memberships")],
                ]],
                ['customers_subscriptions-read', T("View subscriptions"), [
                    ['customers_subscriptions-create', T("Add subscriptions")],
                    ['customers_subscriptions-update',
                        T("Edit subscriptions")],
                    ['customers_subscriptions-delete',
                        T("Delete subscriptions")],
                    ['customers_subscriptions_alt_prices-read', T("View alternative prices"), [
                        ['customers_subscriptions_alt_prices-create', T("Add alternative prices")],
                        ['customers_subscriptions_alt_prices-update', T("Edit alternative prices")],
                        ['customers_subscriptions_alt_prices-delete', T("Delete alternative prices")],
                    ]],
                    ['customers_subscriptions_credits-read', T("View credits"), [
                        ['customers_subscriptions_credits-create', T("Add credits")],
                        ['customers_subscriptions_credits-update', T("Edit credits")],
                        ['customers_subscriptions_credits-delete', T("Delete credits")],
                    ]],                    
                    ['customers_subscriptions_pauses-read', T("View pauses"), [
                        ['customers_subscriptions_pauses-create', T("Add pauses")],
                        ['customers_subscriptions_pauses-update', T("Edit pauses")],
                        ['customers_subscriptions_pauses-delete', T("Delete pauses")],
                    ]],
                    ['customers_subscriptions_blocks-read', T("View class check-in blocks"), [
                        ['customers_subscriptions_blocks-create', T("Add class check-in blocks")],
                        ['customers_subscriptions_blocks-update', T("Edit class check-in blocks")],
                        ['customers_subscriptions_blocks-delete', T("Delete class check-in blocks")],
                    ]],
                ]],
                ['customers_classcards-read', T("View class cards"), [
                    ['customers_classcards-create', T("Add class cards")],
                    ['customers_classcards-update', T("Edit class cards"), [
                        ['customers_classcards_enddate-update', T("Edit class cards enddate")]]],
                    ['customers_classcards-delete', T("Delete class cards")]]],
                ['customers_notes-read', T("View notes"), [
                    ['customers_notes-create', T("Add notes")],
                    ['customers_notes-update', T("Edit notes")],
                    ['customers_notes-delete', T("Delete notes")],
                    ['customers_notes_backoffice-read', T("View back office notes")],
                    ['customers_notes_teachers-read', T("View teachers' notes")]]],
                ['customers_documents-read', T("View documents"), [
                    ['customers_documents-create', T("Upload new documents")],
                    ['customers_documents-update', T("Edit uploaded documents")],
                    ['customers_documents-delete', T("Delete uploaded documents")],
                ]],
                ['customers_payment_info-read', T("View bank account"), [
                    ['customers_payment_info-update', T("Edit bank account"), [
                        ['customers_payment_info_mandates-create', T("Add direct debit mandates")],
                        ['customers_payment_info_mandates-delete', T("Delete direct debit mandates")],
                    ]]]],
                ['auth_user_account-read', T('View account settings'), [
                    ['auth_user_account-update', T('Edit account settings')],
                    ['auth_user-set_password', T('Set a new password for accounts')],
                    ['auth_user-merge', T('Merge accounts')]]]],
             ],  # end customers-edit
            ['auth_user-delete', T("Delete customers")]]],
    ]

    schedule_permissions = [
        ['classes-read', T("Schedule"), [
            ['classes-create', T("Add classes"), ],
            ['classes-update', T("Edit classes"), [
                ['classes_teachers-create', T("Add teachers")],
                ['classes_teachers-update', T("Edit teachers")],
                ['classes_teachers-delete', T("Delete teachers")],
                ['classes_price-create', T("Add prices")],
                ['classes_price-update', T("Edit prices")],
                ['classes_price-delete', T("Delete prices")],
                ['classes_mail-update', T("Edit info mail")],
                ['classes_otc-create', T("Add one time changes")],
                ['classes_otc-update', T("Edit one time changes")],
                ['classes_otc-delete', T("Delete one time changes")],
                ['classes_otc_mail-update', T("Edit one time change info mail")],
            ]],
            ['classes-delete', T('Delete classes')],
            ['schedule_classes_status-read', T("View weekly schedule status"), [
                ['schedule_classes_status-update', T("Edit weekly schedule status")]]],
            ['classes_reservation-read', T("View enrollments"), [
                ['classes_reservation-create', T('Add enrollments')],
                ['classes_reservation-update', T('Edit enrollments')],
                ['classes_reservation-delete', T('Delete enrollments')]]],
            ['classes_waitinglist-read', T("View waitinglist"), [
                ['classes_waitinglist-update', T("Edit waitinglist")],
                ['classes_waitinglist-delete', T("Delete from waitinglist")]]],
            ['classes_attendance-read', T('View attendance'), [
                ['classes_attendance-create', T("Add attendance")],
                ['classes_attendance-update', T("Edit attendance")],
                ['classes_attendance-delete', T("Delete from attendance")],
                ['classes_attendance-complementary', T("Use complementary check-ins")]]],
            ['classes_attendance_override-create', T("Add attendance count")],
            ['classes_attendance_override-update', T("Edit attendance count")],
            ['class_status-update', T("Edit class status")],
            ['classes_notes-read', T("View notes"), [
                ['classes_notes-create', T("Add notes")],
                ['classes_notes-update', T("Edit notes")],
                ['classes_notes-delete', T("Delete notes")],
                ['classes_notes_backoffice-read', T("View back office notes")],
                ['classes_notes_teachers-read', T("View teachers' notes")]]],
            ['classes_revenue-read', T("View revenue")],
            ['classes_school_subscriptions_groups-read', T("View allowed subscriptions groups"), [
                ['classes_school_subscriptions_groups-create', T("Add allowed subscriptions groups")],
                ['classes_school_subscriptions_groups-update', T("Edit allowed subscriptions groups")],
                ['classes_school_subscriptions_groups-delete', T("Delete allowed subscriptions groups")]]],
            ['classes_school_classcards_groups-read', T("View allowed class cards groups"), [
                ['classes_school_classcards_groups-create', T("Add allowed class cards groups")],
                ['classes_school_classcards_groups-update', T("Edit allowed class cards groups")],
                ['classes_school_classcards_groups-delete', T("Delete allowed class cards groups")]]],
            ['classes_otc_sub_avail-read', T("Manage sub teachers request list"), [
                ['classes_otc_sub_avail-update', T("Accept/Decline sub teacher requests")]]],
            ['teacher_classes-read', T('Teacher classes by month')],
            ['teachers_payment_attendance-update', T("Verify teacher payments")],
            ['classes_open-read', T('View all open classes')],
            ['schedule_set_default_sort-update', T('Set default sorting of classes')],
            ['classes_schedule_set_trend_precentages-read', T('View trend colors'), [
                ['classes_schedule_set_trend_precentages-update', T('Set trend color percentages')]]],
        ]]]

    staff_permissions = [
        ['shifts-read', T("Schedule"), [
            ['shifts-create', T("Add shifts"), ],
            ['shifts-update', T("Edit shifts"), [
                ['shifts_staff-read', T("View employees assigned to shifts")],
                ['shifts_staff-create', T("Add employees to shifts")],
                ['shifts_staff-update', T("Edit employee shift assignments")],
                ['shifts_staff-delete', T("Delete employee shift assignments ")],
                ['shifts_otc-update', T("Make one time changes")],
                ['shifts_otc-delete', T("Delete one time changes")],
            ]],
            ['shifts-delete', T('Delete shifts')],
            ['shifts_open-read', T('View all open shifts')],
            ['schedule_staff_status-read', T("View weekly schedule status"), [
                ['schedule_staff_status-update', T("Edit weekly schedule status")]]],
            ['staff_schedule_set_default_sort-update',
                T('Set default sorting of classes')],
            ['teacher_holidays-read', T('View Staff holidays'), [
                ['teacher_holidays-create', T('Add Staff holidays')],
                ['teacher_holidays-update', T('Edit Staff holidays')],
                ['teacher_holidays-delete', T('Delete Staff holidays')]]],
        ]]]

    workshops_permissions = [
        ['workshops-read', T("Events"), [
            ['workshops-create', T("Add events")],
            ['workshops-update', T("Edit events")],
            ['workshops-delete', T("Delete events")],
            ['workshops_products-read', T('View tickets'), [
                ['workshops_products-create', T('Add tickets')],
                ['workshops_products-update', T('Edit tickets')],
                ['workshops_products-delete', T('Delete tickets')],
                ['workshops_products_activities-update', T('Edit activities for tickets')],
                ['workshops_products_customers-read', T('View customers for tickets')],
                ['workshops_products_customers-update', T('Sell tickets')],
                ['workshops_products_customers-delete', T('Unsell tickets')],
            ]],
            ['workshops_activities-read', T('View activities'), [
                ['workshops_activities-create', T("Add activities")],
                ['workshops_activities-update', T("Edit activities")],
                ['workshops_activities-delete', T("Delete activities")],
                ['workshops_activities_customers-update', T('Edit activity attendance')]]],
            ['workshops-archive', T("Archive events")],
            ['workshops_mail-update', T("Edit info mail")]
        ]],
    ]

    school_permissions = [
        ['schoolproperties-read', T("School properties"), [
            ['teachers-read', T("Teachers"), [
                ['teachers-create', T("Add teachers")],
                ['teachers-update', T("Edit teachers")],
                ['teachers-delete', T("Remove teacher status")],
                ['teachers_payment_fixed_rate_default-read', T('View payment rates (fixed rate)'), [
                    ['teachers_payment_fixed_rate_default-create', T('Set default payment (fixed rate)')],
                    ['teachers_payment_fixed_rate_default-create', T('Edit default payment (fixed rate)')],
                    ['teachers_payment_fixed_rate_class-read', T('View class specific rates (fixed rate)'), [
                        ['teachers_payment_fixed_rate_class-create', T('Add class specific rates (fixed rate)')],
                        ['teachers_payment_fixed_rate_class-update', T('Edit class specific rates (fixed rate)')],
                        ['teachers_payment_fixed_rate_class-delete', T('Delete class specific rates (fixed rate)')],
                    ]],
                ]],
                ['teachers_payment_attendance_lists-read', T("View payment rate lists (attendance based)"), [
                    ['teachers_payment_attendance_lists-create', T('Add payment rate lists (attendance based)')],
                    ['teachers_payment_attendance_lists-update', T('Edit payment rate lists (attendance based)')],
                    ['teachers_payment_attendance_lists-delete', T('Delete payment rate lists (attendance based)')],
                    ['teachers_payment_attendance_lists_rates-read', T('View list rates'), [
                        ['teachers_payment_attendance_lists_rates-create', T('Add rates to lists')],
                        ['teachers_payment_attendance_lists_rates-update', T('Edit rates in lists')],
                        ['teachers_payment_attendance_lists_rates-delete', T('Delete rates from lists')],
                    ]],
                    ['teachers_payment_attendance_lists_school_classtypes-update', T("Assign list to classtypes")]
                ]],
                ['teachers_payment_travel-read', T('View travel allowances'), [
                    ['teachers_payment_travel-create', T('Add travel allowance')],
                    ['teachers_payment_travel-update', T('Edit travel allowance')],
                    ['teachers_payment_travel-delete', T('Delete travel allowance')],
                ]],
                ['teachers_payment_classes-read', T('View payment for classes'), [
                    ['teachers_payment_travel-create', T('Add payment for a class')],
                    ['teachers_payment_travel-update', T('Edit payment for a class')],
                    ['teachers_payment_travel-delete', T('Delete payment for a class')],
                ]],
            ]],
            ['employees-read', T("Employees"), [
                ['employees-create', T("Add employees")],
                ['employees-update', T("Edit employees")],
                ['employees-delete', T("Remove employee status")],
            ]],
            ['school_memberships-read', T("Memberships"), [
                ['school_memberships-create', T("Add memberships")],
                ['school_memberships-update', T("Edit memberships")],
                ['school_memberships_price-read', T('View membership prices'), [
                    ['school_memberships_price-create', T("Add membership prices")],
                    ['school_memberships_price-update', T("Edit membership prices")],
                    ['school_memberships_price-delete', T("Delete membership prices")]]]]],
            ['school_subscriptions-read', T("Subscriptions"), [
                ['school_subscriptions-create', T("Add subscription")],
                ['school_subscriptions-update', T("Edit subscriptions")],
                ['school_subscriptions_price-read', T("View subscription prices"), [
                    ['school_subscriptions_price-create', T("Add subscription prices")],
                    ['school_subscriptions_price-update', T("Edit subscription prices")]]],
                ['school_subscriptions_groups-read', T('View subscription groups'), [
                    ['school_subscriptions_groups-create', T('Add subscription groups')],
                    ['school_subscriptions_groups-update', T('Edit subscription groups')],
                    ['school_subscriptions_groups-delete', T('Delete subscription groups')],
                    ['school_subscriptions_groups_subscriptions-read', T('View subscription group subscriptions')],
                    ['school_subscriptions_groups_subscriptions-create', T('Add subscription group subscriptions')],
                    ['school_subscriptions_groups_subscriptions-delete', T('Delete subscription group subscriptions')]]],
                ['school_subscriptions_cancel_reasons-read', T("View subscription cancel reasons"), [
                    ['school_subscriptions_cancel_reasons-create', T("Add subscription cancel reasons")],
                    ['school_subscriptions_cancel_reasons-update', T("Edit subscription cancel reasons")],
                ]]
            ]],

            ['school_classcards-read', T("Class cards"), [
                ['school_classcards-create', T("Add class card")],
                ['school_classcards-update', T("Edit class cards")],
                ['school_classcards_groups-read', T('View classcard groups'), [
                     ['school_classcards_groups-create', T('Add classcard groups')],
                     ['school_classcards_groups-update', T('Edit classcard groups')],
                     ['school_classcards_groups-delete', T('Delete classcard groups')],
                     ['school_classcards_groups_classcards-read', T('View classcard group classcards')],
                     ['school_classcards_groups_classcards-create', T('Add classcard group classcards')],
                     ['school_classcards_groups_classcards-delete', T('Delete classcard group classcards')]]]
                 ]],
            ['school_levels-read', T("Practice levels"), [
                ['school_levels-create', T("Add practice levels")],
                ['school_levels-update', T("Edit practice levels")]]],
            ['school_discovery-read', T("Discovery"), [
                ['school_discovery-create', T("Add discovery")],
                ['school_discovery-update', T("Edit discovery")]]],
            ['school_classtypes-read', T("Class types"), [
                ['school_classtypes-create', T("Add classtypes")],
                ['school_classtypes-update', T("Edit classtypes")]]],
            ['school_locations-read', T("Locations"), [
                ['school_locations-create', T("Add locations")],
                ['school_locations-update', T("Edit locations")]]],
            ['school_shifts-read', T("Shifts"), [
                ['school_shifts-create', T("Add shifts")],
                ['school_shifts-update', T("Edit shifts")]]],
            ['school_holidays-read', T('School holidays'), [
                ['school_holidays-create', T('Add holidays')],
                ['school_holidays-update', T('Edit holidays')],
                ['school_holidays-delete', T('Delete holidays')],
            ]],
            ['schoolproperties_keys-read', T("Keys")],
            ['school_languages-read', T("Languages"), [
                ['school_languages-create', T("Add languages")],
                ['school_languages-update', T("Edit languages")]]]]],
    ]

    settings_permissions = [
        ['settings-read', T("Settings"), [
            ['customers_profile_features-update', T("Set which profile features are available for customers when they login")],
            ['auth_group-read', T("View groups"), [
                ['auth_group-create', T("Add groups")],
                ['auth_group-update', T("Edit groups")],
                ['auth_group-delete', T("Delete groups")]]],

            ['user_group_membership-update', T("Edit users' group")],
            ['auth_group_permissions-update', T("Edit group permissions")],
            ['mailing_lists-create', T('Add mailing lists')],
            ['mailing_lists-update', T('Edit mailing lists')],
            ['mailing_lists-delete', T('Delete mailing lists')]]],
        ['settings_finance-read', T("View finance settings"), [
            ['accounting_costcenters-read', T("View Cost centers"), [
                ['accounting_costcenters-create', T("Add Cost centers")],
                ['accounting_costcenters-update', T("Edit Cost centers")],
            ]],
            ['accounting_glaccounts-read', T("View General ledger accounts"), [
                ['accounting_glaccounts-create', T("Add General ledger accounts")],
                ['accounting_glaccounts-update', T("Edit General ledger accounts")],
            ]]
        ]],
        ['postcode_groups-read', T("View postcode groups"), [
            ['postcode_groups-create', T('Add postcode groups')],
            ['postcode_groups-update', T('Edit postcode groups')],
            ['postcode_groups-delete', T('Delete postcode groups')],
        ]],
        ['sys_organizations-read', T('View organizations'), [
            ['sys_organizations-create', T('Add organizations')],
            ['sys_organizations-update', T('Edit organizations')],
            ['sys_organizations-delete', T('Delete organizations')],
        ]],
        ['sys_api_users-delete', T("Delete API users")],
    ]

    other_permissions = [
        ['selfcheckin-read', T("Use self check-in")],
        ['pos-read', T("Use point of sale")],
        ['employee_portal-read', T("Use employee portal")],
        ['automated_tasks-read', T("Use automated tasks (back-end)")],
    ]

    permissions_list = [[pinboard_permissions, 'pinboard'],
                        [tasks_permissions, 'tasks'],
                        [customers_permissions, 'customers'],
                        [schedule_permissions, 'schedule'],
                        [staff_permissions, 'staff'],
                        [workshops_permissions, 'events'],
                        [school_permissions, 'school'],
                        [reports_permissions, 'reports'],
                        [finance_permisisons, 'finance'],
                        [shop_permissions, 'shop'],
                        [settings_permissions, 'settings'],
                        [other_permissions, 'other']]

    form = FORM(_id="MainForm")

    for permission in permissions_list:
        form.append(append_table(permission))

    if form.process().accepted:
        for key in form.vars:
            (obj, name) = key.split('-')
            if form.vars[key] is None:
                if obj == 'class_status':  # subteachers uses a crud form
                    auth.del_permission(group_id, 'create',
                                        'classes_subteachers', 0)
                    auth.del_permission(group_id, 'update',
                                        'classes_subteachers', 0)
                if obj == 'shifts_status':  # staff_sub uses a crud form
                    auth.del_permission(group_id, 'create',
                                        'shifts_sub', 0)
                    auth.del_permission(group_id, 'update',
                                        'shifts_sub', 0)

                # 0 means all records
                auth.del_permission(group_id, name, obj, 0)
            else:
                if obj == 'class_status':  # subteachers uses a crud form
                    auth.add_permission(group_id, 'create',
                                        'classes_subteachers', 0)
                    auth.add_permission(group_id, 'update',
                                        'classes_subteachers', 0)
                if obj == 'shifts_status':  # staff_sub uses a crud form
                    auth.add_permission(group_id, 'create',
                                        'shifts_sub', 0)
                    auth.add_permission(group_id, 'update',
                                        'shifts_sub', 0)

                # 0 means all records
                auth.add_permission(group_id, name, obj, 0)
        response.flash = T("Saved permissions")
        session.flash = T("Saved permissions")

        # clear menu backend menu cache
        cache_clear_menu_backend()
        # redirect user
        redirect(URL(args=group_id))

    submenu = UL(_class='nav nav-tabs',
                 _id='os-menu-settings-permissions')

    menu_items = [['pinboard', T('Pinboard'), True],
                  ['tasks', T('Tasks'), False],
                  ['customers', T('Customers'), False],
                  ['schedule', T('Classes'), False],
                  ['staff', T('Studio staff'), False],
                  ['events', T('Events'), False],
                  ['school', T('School'), False],
                  ['reports', T('Reports'), False],
                  ['finance', T('Finance'), False],
                  ['shop', T('Shop'), False],
                  ['settings', T('Settings'), False],
                  ['other', T('Other'), False],
                  ]

    for item in menu_items:
        _class = ''
        active = item[2]
        if active:
            _class = 'active'
        submenu.append(LI(A(item[1], _href='#'),
                          _class=_class,
                          _id='tab-' + item[0]))

    content = DIV(DIV(submenu,
                      DIV(form, _class='tab-content'),
                      _class='nav-tabs-custom'),
                  _id='os-permissions')

    return_url = URL('access_groups')
    back = os_gui.get_button('back', return_url)

    return dict(content=content, back=back, save=os_gui.get_submit_button('MainForm'))


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def financial_dd_categories():
    response.title = T("Financial Settings")
    response.subtitle = T("Direct debit categories")
    response.view = 'general/tabs_menu.html'

    show = 'current'
    query = (db.payment_categories.Archived == False)

    if 'show_archive' in request.vars:
        show = request.vars['show_archive']
        session.settings_payment_categories_show = show
        if show == 'current':
            query = (db.payment_categories.Archived == False)
        elif show == 'archive':
            query = (db.payment_categories.Archived == True)
    elif session.settings_payment_categories_show == 'archive':
        query = (db.payment_categories.Archived == True)
    else:
        session.settings_payment_categories_show = show

    db.payment_categories.id.readable = False
    fields = [db.payment_categories.Name,
              db.payment_categories.CategoryType]
    links = [lambda row: os_gui.get_button('edit',
                                           URL('financial_dd_category_edit',
                                               args=[row.id])),
             financial_dd_category_get_link_archive]

    maxtextlengths = {'payment_categories.Name': 50}
    grid = SQLFORM.grid(query, fields=fields, links=links,
                        create=False,
                        editable=False,
                        details=False,
                        searchable=False,
                        deletable=False,
                        csv=False,
                        maxtextlengths=maxtextlengths,
                        ui=grid_ui)
    grid.element('.web2py_counter', replace=None)  # remove the counter
    # remove text from delete button
    grid.elements('span[title=Delete]', replace=None)

    menu = financial_get_menu(request.function)

    add = os_gui.get_button('add', URL('financial_dd_category_add'))
    archive_buttons = os_gui.get_archived_radio_buttons(
        session.settings_payment_categories_show)

    content = DIV(archive_buttons, grid)

    return dict(content=content,
                menu=menu,
                add=add)


def financial_dd_category_get_link_archive(row):
    """
        Called from the index function. Changes title of archive button
        depending on whether a category is archived or not
    """
    row = db.payment_categories(row.id)

    if row.Archived:
        tt = T("Move to current")
    else:
        tt = T("Archive")

    return os_gui.get_button('archive',
                             URL('financial_dd_category_archive',
                                 vars={'pcID': row.id}),
                             tooltip=tt)


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('update', 'payment_categories'))
def financial_dd_category_archive():
    """
        This function archives a subscription
        request.vars[pcID] is expected to be the payment_category ID
    """
    pcID = request.vars['pcID']
    if not pcID:
        session.flash = T('Unable to (un)archive category')
    else:
        row = db.payment_categories(pcID)

        if row.Archived:
            session.flash = T('Moved to current')
        else:
            session.flash = T('Archived')

        row.Archived = not row.Archived
        row.update_record()

    redirect(URL('financial_dd_categories'))


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def financial_dd_category_add():
    """
        This function shows an add page for a payment category
    """
    response.title = T("New direct debit category")
    response.subtitle = T('')
    response.view = 'general/only_content.html'

    return_url = URL('financial_dd_categories')

    crud.messages.submit_button = T("Save")
    crud.messages.record_created = T("Saved")
    crud.settings.create_next = return_url
    form = crud.create(db.payment_categories)

    form_id = "MainForm"
    form_element = form.element('form')
    form['_id'] = form_id

    elements = form.elements('input, select, textarea')
    for element in elements:
        element['_form'] = form_id

    submit = form.element('input[type=submit]')

    back = os_gui.get_button('back', return_url)

    return dict(content=form, back=back, save=submit)


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def financial_dd_category_edit():
    """
        This function shows an edit page for a payment category
        request.args[0] is expected to be the paymentcategoryID (pcID)
    """
    pcID = request.args[0]
    response.title = T("Edit direct debit category")
    response.subtitle = T('')
    response.view = 'general/only_content.html'

    return_url = URL('financial_dd_categories')

    crud.messages.submit_button = T("Save")
    crud.messages.record_updated = T("Saved")
    crud.settings.update_next = return_url
    crud.settings.update_deletable = False
    form = crud.update(db.payment_categories, pcID)

    form_id = "MainForm"
    form_element = form.element('form')
    form['_id'] = form_id

    elements = form.elements('input, select, textarea')
    for element in elements:
        element['_form'] = form_id

    submit = form.element('input[type=submit]')

    back = os_gui.get_button('back', return_url)

    return dict(content=form, back=back, save=submit)


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def financial_payment_methods():
    response.title = T("Financial Settings")
    response.subtitle = T("Payment methods")
    response.view = 'general/tabs_menu.html'

    show = 'current'
    query = (db.payment_methods.Archived == False)

    if 'show_archive' in request.vars:
        show = request.vars['show_archive']
        session.settings_payment_methods_show = show
        if show == 'current':
            query = (db.payment_methods.Archived == False)
        elif show == 'archive':
            query = (db.payment_methods.Archived == True)
    elif session.settings_payment_methods_show == 'archive':
        query = (db.payment_methods.Archived == True)
    else:
        session.settings_payment_methods_show = show

    db.payment_methods.id.readable = False
    fields = [
        db.payment_methods.Name,
        db.payment_methods.SystemMethod,
        db.payment_methods.AccountingCode
    ]
    links = [
        financial_payment_methods_get_link_edit,
        financial_payment_methods_get_link_archive
    ]

    maxtextlengths = {'payment_methods.Name': 40}
    grid = SQLFORM.grid(query,
                        fields=fields,
                        links=links,
                        maxtextlengths=maxtextlengths,
                        create=False,
                        editable=False,
                        deletable=False,
                        details=False,
                        searchable=False,
                        csv=False,
                        orderby=~db.payment_methods.SystemMethod | db.payment_methods.Name,
                        ui=grid_ui)
    grid.element('.web2py_counter', replace=None)  # remove the counter
    # remove text from delete button
    grid.elements('span[title=Delete]', replace=None)

    add_url = URL('financial_payment_method_add')
    add = os_gui.get_button('add', add_url, T("Add a new payment method"))
    archive_buttons = os_gui.get_archived_radio_buttons(
        session.settings_payment_methods_show)

    content = DIV(archive_buttons, grid)

    menu = financial_get_menu(request.function)

    return dict(content=content,
                menu=menu,
                add=add)


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def financial_payment_method_add():
    """
        This function shows an add page for a payment method
    """
    response.title = T("New payment method")
    response.subtitle = T('')
    response.view = 'general/only_content.html'

    return_url = URL('financial_payment_methods')

    crud.messages.submit_button = T("Save")
    crud.messages.record_created = T("Added payment method")
    crud.settings.formstyle = 'bootstrap3_stacked'
    crud.settings.create_next = return_url
    form = crud.create(db.payment_methods)

    form_id = "MainForm"
    form_element = form.element('form')
    form['_id'] = form_id

    elements = form.elements('input, select, textarea')
    for element in elements:
        element['_form'] = form_id

    submit = form.element('input[type=submit]')

    back = os_gui.get_button('back', return_url)

    return dict(content=form, back=back, save=submit)


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def financial_payment_method_edit():
    """
        This function shows an edit page for a payment method
        request.args[0] is expected to be the payment_methodID (pmID)
    """
    pmID = request.args[0]
    response.title = T("Edit payment method")
    response.subtitle = T('')
    response.view = 'general/only_content.html'

    return_url = URL('financial_payment_methods')

    pm = db.payment_methods(pmID)
    if pm.SystemMethod:
        db.payment_methods.Name.writable = False

    crud.messages.submit_button = T("Save")
    crud.messages.record_updated = T("Updated payment method")
    crud.settings.formstyle = 'bootstrap3_stacked'
    crud.settings.update_next = return_url
    crud.settings.update_deletable = False
    form = crud.update(db.payment_methods, pmID)

    form_id = "MainForm"
    form_element = form.element('form')
    form['_id'] = form_id

    elements = form.elements('input, select, textarea')
    for element in elements:
        element['_form'] = form_id

    submit = form.element('input[type=submit]')

    back = os_gui.get_button('back', return_url)

    return dict(content=form, back=back, save=submit)


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def financial_payment_method_archive():
    """
        This function archives a subscription
        request.vars[pmID] is expected to be the payment_methods ID
    """
    pmID = request.vars['pmID']
    if not pmID:
        session.flash = T('Unable to (un)archive method')
    else:
        row = db.payment_methods(pmID)

        if row.Archived:
            session.flash = T('Moved to current')
        else:
            session.flash = T('Archived')

        row.Archived = not row.Archived
        row.update_record()

    redirect(URL('financial_payment_methods'))


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def financial_payment_methods_get_link_edit(row):
    """
        This function returns the edit link for a payment method,
        if the id is > 3. The first 3 are reserved for OpenStudio defined
        methods.
    """
    edit = os_gui.get_button('edit',
                              URL('financial_payment_method_edit',
                                  args=[row.id]),
                              T("Edit this payment method"))

    return edit


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def financial_payment_methods_get_link_archive(row):
    """
        This function returns the archive link for a payment method,
        if the id is > 3. The first 3 are reserved for OpenStudio defined
        methods.
    """
    archive = ''
    if not row.SystemMethod:
        row = db.payment_methods(row.id)

        if row.Archived:
            tt = T("Move to current")
        else:
            tt = T("Archive")

        archive = os_gui.get_button('archive',
                                    URL('financial_payment_method_archive',
                                        vars={'pmID': row.id}),
                                    tooltip=tt)

    return archive


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def financial_tax_rates():
    """
        List tax rates
    """
    response.title = T("Financial Settings")
    response.subtitle = T("Tax rates")
    response.view = 'general/tabs_menu.html'

    show = 'current'
    query = (db.tax_rates.Archived == False)

    if 'show_archive' in request.vars:
        show = request.vars['show_archive']
        session.settings_tax_rates_show = show
        if show == 'current':
            query = (db.tax_rates.Archived == False)
        elif show == 'archive':
            query = (db.tax_rates.Archived == True)
    elif session.settings_tax_rates_show == 'archive':
        query = (db.tax_rates.Archived == True)
    else:
        session.settings_tax_rates_show = show

    db.tax_rates.id.readable = False
    fields = [
        db.tax_rates.Name,
        db.tax_rates.Percentage,
        db.tax_rates.VATCodeID
    ]

    links = [lambda row: os_gui.get_button('edit',
                                           URL('financial_tax_rate_edit', vars={'tID': row.id})),
             financial_tax_rates_get_link_archive]

    maxtextlengths = {'tax_rates.Name': 50}
    grid = SQLFORM.grid(query,
                        fields=fields,
                        links=links,
                        maxtextlengths=maxtextlengths,
                        create=False,
                        editable=False,
                        deletable=False,
                        details=False,
                        searchable=False,
                        csv=False,
                        orderby=db.tax_rates.id,
                        ui=grid_ui)
    grid.element('.web2py_counter', replace=None)  # remove the counter
    # remove text from delete button
    grid.elements('span[title=Delete]', replace=None)

    add_url = URL('financial_tax_rate_add')
    add = os_gui.get_button('add', add_url, T("Add a tax rate"), _class='pull-right')
    archive_buttons = os_gui.get_archived_radio_buttons(
        session.settings_tax_rates_show)

    content = DIV(DIV(archive_buttons),
                  grid)

    menu = financial_get_menu(request.function)

    return dict(content=content,
                menu=menu,
                add=add)


def financial_tax_rates_get_link_archive(row):
    """
        Returns archive button for list of tax rates
    """
    row = db.tax_rates(row.id)

    if row.Archived:
        tt = T("Move to current")
    else:
        tt = T("Archive")

    return os_gui.get_button('archive',
                             URL('financial_tax_rate_archive',
                                 vars={'tID': row.id}),
                             tooltip=tt)


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def financial_tax_rate_add():
    """
        Add a tax rate
    """
    response.title = T("New tax rate")
    response.subtitle = T('')
    response.view = 'general/only_content.html'

    return_url = URL('financial_tax_rates')

    crud.messages.submit_button = T("Save")
    crud.messages.record_created = T("Saved")
    crud.settings.formstyle = 'bootstrap3_stacked'
    crud.settings.create_next = return_url
    form = crud.create(db.tax_rates)

    form_id = "MainForm"
    form_element = form.element('form')
    form['_id'] = form_id

    elements = form.elements('input, select, textarea')
    for element in elements:
        element['_form'] = form_id

    submit = form.element('input[type=submit]')

    back = os_gui.get_button('back', return_url)

    return dict(content=form, back=back, save=submit)


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def financial_tax_rate_edit():
    """
        Edit a tax rate
        request.vars['tID'] is expected to be db.tax_rates.id
    """
    tID = request.vars['tID']
    response.title = T("Edit tax rate")
    response.subtitle = T('')
    response.view = 'general/only_content.html'

    return_url = URL('financial_tax_rates')

    crud.messages.submit_button = T("Save")
    crud.messages.record_updated = T("Saved")
    crud.settings.formstyle = 'bootstrap3_stacked'
    crud.settings.update_next = return_url
    crud.settings.update_deletable = False
    form = crud.update(db.tax_rates, tID)

    form_id = "MainForm"
    form_element = form.element('form')
    form['_id'] = form_id

    elements = form.elements('input, select, textarea')
    for element in elements:
        element['_form'] = form_id

    submit = form.element('input[type=submit]')

    back = os_gui.get_button('back', return_url)

    return dict(content=form, back=back, save=submit)


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def financial_tax_rate_archive():
    """
        This function archives a subscription
        request.vars[tID] is expected to be the tax_rates.id
    """
    tID = request.vars['tID']
    if not tID:
        session.flash = T('Unable to (un)archive tax rate')
    else:
        row = db.tax_rates(tID)

        if row.Archived:
            session.flash = T('Moved to current')
        else:
            session.flash = T('Archived')

        row.Archived = not row.Archived
        row.update_record()

    redirect(URL('financial_tax_rates'))


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def financial_invoices_groups():
    """
        List invoice groups
    """
    response.title = T("Financial Settings")
    response.subtitle = T("Invoices")
    response.view = 'general/tabs_menu.html'

    show = 'current'
    query = (db.invoices_groups.Archived == False)

    if 'show_archive' in request.vars:
        show = request.vars['show_archive']
        session.settings_invoices_groups_show = show
        if show == 'current':
            query = (db.invoices_groups.Archived == False)
        elif show == 'archive':
            query = (db.invoices_groups.Archived == True)
    elif session.settings_invoices_groups_show == 'archive':
        query = (db.invoices_groups.Archived == True)
    else:
        session.settings_invoices_groups_show = show

    db.invoices_groups.id.readable = False
    db.invoices_groups.Terms.readable = False
    db.invoices_groups.Footer.readable = False

    links = [lambda row: os_gui.get_button('edit',
                                           URL('financial_invoices_group_edit', vars={'igID': row.id})),
             financial_invoices_groups_get_link_archive]

    maxtextlengths = {'invoices_groups.Name': 50}
    grid = SQLFORM.grid(query,
                        # fields=fields,
                        links=links,
                        maxtextlengths=maxtextlengths,
                        create=False,
                        editable=False,
                        deletable=False,
                        details=False,
                        searchable=False,
                        csv=False,
                        orderby=db.invoices_groups.Name,
                        ui=grid_ui)
    grid.element('.web2py_counter', replace=None)  # remove the counter
    # remove text from delete button
    grid.elements('span[title=Delete]', replace=None)

    add_url = URL('financial_invoices_group_add')
    add = os_gui.get_button('add', add_url, T("Add an invoice group"))
    archive_buttons = os_gui.get_archived_radio_buttons(
        session.settings_invoices_groups_show)

    submenu = financial_invoices_get_submenu(request.function)
    content = DIV(submenu, BR(),
                  archive_buttons,
                  grid)

    menu = financial_get_menu('financial_invoices')

    return dict(content=content,
                menu=menu,
                add=add)


def financial_invoices_groups_get_link_archive(row):
    """
        Returns archive button for list of tax rates
    """
    row = db.invoices_groups(row.id)

    if row.Archived:
        tt = T("Move to current")
    else:
        tt = T("Archive")

    return os_gui.get_button('archive',
                             URL('financial_invoices_group_archive',
                                 vars={'igID': row.id}),
                             tooltip=tt)


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def financial_invoices_group_add():
    """
        Add an invoice group
    """
    response.title = T("New invoice group")
    response.subtitle = T('')
    response.view = 'general/only_content.html'

    return_url = URL('financial_invoices_groups')

    crud.messages.submit_button = T("Save")
    crud.messages.record_created = T("Saved")
    crud.settings.create_next = return_url
    crud.settings.formstyle = 'bootstrap3_stacked'
    form = crud.create(db.invoices_groups)

    textareas = form.elements('textarea')
    for textarea in textareas:
        textarea['_class'] += ' tmced'

    form_id = "MainForm"
    form_element = form.element('form')
    form['_id'] = form_id

    elements = form.elements('input, select, textarea')
    for element in elements:
        element['_form'] = form_id

    submit = form.element('input[type=submit]')

    back = os_gui.get_button('back', return_url)

    return dict(content=form, back=back, save=submit)


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def financial_invoices_group_edit():
    """
        Edit a tax rate
        request.vars['igID'] is expected to be db.invoices_groups.id
    """
    igID = request.vars['igID']
    response.title = T("Edit invoice group")
    response.subtitle = T('')
    response.view = 'general/only_content.html'

    return_url = URL('financial_invoices_groups')

    crud.messages.submit_button = T("Save")
    crud.messages.record_updated = T("Saved")
    crud.settings.update_next = return_url
    crud.settings.update_deletable = False
    crud.settings.formstyle = 'bootstrap3_stacked'
    form = crud.update(db.invoices_groups, igID)

    textareas = form.elements('textarea')
    for textarea in textareas:
        textarea['_class'] += ' tmced'

    form_id = "MainForm"
    form_element = form.element('form')
    form['_id'] = form_id

    elements = form.elements('input, select, textarea')
    for element in elements:
        element['_form'] = form_id

    submit = form.element('input[type=submit]')

    back = os_gui.get_button('back', return_url)

    return dict(content=form, back=back, save=submit)


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def financial_invoices_group_archive():
    """
        This function archives a subscription
        request.vars[igID] is expected to be the invoices_groups.id
    """
    igID = request.vars['igID']
    if not igID:
        session.flash = T('Unable to (un)archive invoice group')
    else:
        row = db.invoices_groups(igID)

        if row.Archived:
            session.flash = T('Moved to current')
        else:
            session.flash = T('Archived')

        row.Archived = not row.Archived
        row.update_record()

    redirect(URL('financial_invoices_groups'))


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def financial_invoices_groups_default():
    """
        Page to list the default invoice groups for certain categories in
        OpenStudio (subscriptions, workshop products, etc.)
    """
    response.title = T("Financial Settings")
    response.subtitle = T("Invoices")
    response.view = 'general/tabs_menu.html'


    header = THEAD(TR(TH(T('Type of product')),
                      TH(T('Default invoice group')),
                      TH()))
    table=TABLE(header, _class='table table-hover table-striped')

    product_types = get_invoices_groups_product_types()
    for product, product_name in product_types:
        left  = [ db.invoices_groups.on(
            db.invoices_groups_product_types.invoices_groups_id == \
            db.invoices_groups.id)  ]
        query = (db.invoices_groups_product_types.ProductType == product)
        rows  = db(query).select(db.invoices_groups_product_types.ALL,
                                 db.invoices_groups.Name,
                                 left=left)

        if rows:
            row = rows.first()
            igptID = row.invoices_groups_product_types.id
            group = row.invoices_groups.Name
        else:
            igptID = ''
            group  = ''

        edit = os_gui.get_button(
            'edit_notext',
            URL('financial_invoices_groups_default_edit',
                vars={'igptID':igptID,
                      'product':product,
                      'product_name':product_name}),
            _class='pull-right')

        tr = TR(TD(product_name),
                TD(group),
                TD(edit))

        table.append(tr)


    submenu = financial_invoices_get_submenu(request.function)
    content = DIV(submenu,
                  table)

    menu = financial_get_menu('financial_invoices')

    return dict(content=content,
                menu=menu,
                left_sidebar_enabled=True)


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def financial_invoices_groups_default_edit():
    """
        Edit default invoice group for product categories
    """
    response.title = T("Set default invoice group")

    igptID       = request.vars['igptID']
    product      = request.vars['product']
    product_name = request.vars['product_name']

    response.subtitle = product_name
    response.view = 'general/only_content.html'

    return_url = URL('financial_invoices_groups_default')

    crud.messages.submit_button = T("Save")
    crud.messages.record_created = T("Saved")
    crud.messages.record_updated = T("Saved")
    crud.settings.formstyle = 'bootstrap3_stacked'
    crud.settings.create_next = return_url
    crud.settings.update_next = return_url
    crud.settings.update_deletable = False

    if igptID:
        form = crud.update(db.invoices_groups_product_types, igptID)
    else:
        db.invoices_groups_product_types.ProductType.default = product
        form = crud.create(db.invoices_groups_product_types)

    form_id = "MainForm"
    form_element = form.element('form')
    form['_id'] = form_id

    elements = form.elements('input, select, textarea')
    for element in elements:
        element['_form'] = form_id

    submit = form.element('input[type=submit]')

    back = os_gui.get_button('back', URL('financial_invoices_groups_default'))

    return dict(content=form, save=submit, back=back)


# @auth.requires(auth.has_membership(group_id='Admins') or
#                auth.has_permission('read', 'settings'))
# def financial_invoices_texts():
#     """
#         View default texts for invoices
#     """
#     response.title = T("Financial Settings")
#     response.subtitle = T("Invoices")
#     response.view = 'general/tabs_menu.html'
#
#     default_footer = get_sys_property('invoices_default_footer')
#     default_terms = get_sys_property('invoices_default_terms')
#
#     form = SQLFORM.factory(
#         Field('default_footer', 'text',
#               default=default_footer,
#               label=T('Default footer')),
#         Field('default_terms', 'text',
#               default=default_terms,
#               label=T('Default terms')),
#         submit_button=T("Save"),
#         separator=' '
#     )
#
#     textareas = form.elements('textarea')
#     for textarea in textareas:
#         textarea['_class'] += ' tmced'
#
#     form_id = "MainForm"
#     form_element = form.element('form')
#     form['_id'] = form_id
#
#     elements = form.elements('input, select, textarea')
#     for element in elements:
#         element['_form'] = form_id
#
#     submit = form.element('input[type=submit]')
#
#     if form.accepts(request.vars, session):
#         # check default footer
#         default_footer = request.vars['default_footer']
#         row = db.sys_properties(Property='invoices_default_footer')
#         if not row:
#             db.sys_properties.insert(Property='invoices_default_footer',
#                                      PropertyValue=default_footer)
#         else:
#             row.PropertyValue = default_footer
#             row.update_record()
#
#         # check default terms
#         default_terms = request.vars['default_terms']
#         row = db.sys_properties(Property='invoices_default_terms')
#         if not row:
#             db.sys_properties.insert(Property='invoices_default_terms',
#                                      PropertyValue=default_terms)
#         else:
#             row.PropertyValue = default_terms
#             row.update_record()
#
#         # Clear cache
#         cache_clear_sys_properties()
#         # User feedback
#         session.flash = T('Saved')
#         # reload so the user sees how the values are stored in the db now
#         redirect(URL('financial_invoices_texts'))
#
#     form = DIV(
#         XML('<form action="#" class="form-horizontal" enctype="multipart/form-data" id="MainForm" method="post">'),
#         LABEL(form.custom.label.default_footer), BR(),
#         form.custom.widget.default_footer,
#         LABEL(form.custom.label.default_terms), BR(),
#         form.custom.widget.default_terms,
#         form.custom.submit,
#         form.custom.end)
#
#     submenu = financial_invoices_get_submenu(request.function)
#     content = DIV(submenu, form)
#
#     back = financial_get_back()
#     menu = financial_get_menu('financial_invoices')
#
#     return dict(content=content,
#                 back=back,
#                 menu=menu,
#                 save=submit)


def financial_invoices_get_submenu(page):
    """
        Returns submenu for financial invoices pages
    """
    pages = [['financial_invoices_groups',
              T('Groups'), URL('financial_invoices_groups')],
             ['financial_invoices_groups_default',
              T('Default groups'), URL('financial_invoices_groups_default')],

             ]

    horizontal = True

    return os_gui.get_submenu(pages, page, horizontal=horizontal, htype='tabs')


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def access_api_users():
    """
        This page shows an overview of current API users
    """
    response.title = T("Access Settings")
    response.subtitle = T("API users")
    response.view = 'general/tabs_menu.html'

    db.sys_api_users.id.readable = False
    maxtextlengths = {'sys_api_users.APIKey': 30,
                      'sys_api_users.Description': 50}

    new_key_onclick_msg = T('Do you really want to renew this key?') + ' ' + \
        T('The old key wil STOP working!')
    new_key_onclick = "return confirm('" + new_key_onclick_msg + "');"
    links = [lambda row: A(SPAN(_class='glyphicon glyphicon-link'), ' ',
                           T("Generate new key"),
                           _href=URL('access_api_user_generate_new_key',
                                     args=[row.id]),
                           _onclick=new_key_onclick,
                           _class='btn btn-info'),
             access_api_user_link_active, ]

    query = (db.sys_api_users.id > 0)

    delete_permission = auth.has_membership(group_id='Admins') or \
        auth.has_permission('delete', 'sys_api_users')

    grid = SQLFORM.grid(query, links=links, user_signature=False,
                        create=False,
                        editable=False,
                        details=False,
                        csv=False,
                        searchable=False,
                        deletable=delete_permission,
                        maxtextlengths=maxtextlengths,
                        orderby=db.sys_api_users.Username,
                        field_id=db.sys_api_users.id,
                        ui=grid_ui)
    grid.element('.web2py_counter', replace=None)  # remove the counter
    # remove text from delete button
    grid.elements('span[title=Delete]', replace=None)

    menu = access_get_menu(request.function)

    add_url = URL('access_api_user_add')
    add = os_gui.get_button('add', add_url, T("Add a new api user"))

    return dict(content=grid,
                menu=menu,
                add=add)


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def access_api_user_add():
    """
        Shows a page to add a new api user
    """
    response.title = T("New API user")
    response.subtitle = T('')
    response.view = 'general/only_content.html'

    db.sys_api_users.ActiveUser.readable = False
    db.sys_api_users.APIKey.readable = False
    db.sys_api_users.APIKey.default = access_api_user_generate_key()

    return_url = URL('access_api_users')

    crud.messages.submit_button = T("Save")
    crud.messages.record_created = T("Added new api user")
    crud.settings.create_next = return_url
    form = crud.create(db.sys_api_users)

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']

    back = os_gui.get_button('back', return_url)

    return dict(content=form, back=back, save=submit)


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def access_api_user_generate_new_key():
    """
        Sets a new API key for an api user.
        request.args[0] is expected to be the sys_api_users id (suaID)
    """
    suaID = request.args[0]
    key = access_api_user_generate_key()

    record = db.sys_api_users(suaID)
    record.APIKey = key
    record.update_record()

    redirect(URL('access_api_users'))


def access_api_user_generate_key(length=30):
    """
        Function to generate a key for an api user.
        Keys are auto generated to increase security, it's impossible now to
        add weak keys.
    """
    key = generate_password(length)

    return key


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def access_api_user_change_active_state():
    """
        Enables or disables an api user.
        request.args[0] is expected to be the sys_api_users id (suaID)
    """
    suaID = request.args[0]
    record = db.sys_api_users(suaID)

    # invert active state
    active = not record.ActiveUser
    record.ActiveUser = not record.ActiveUser
    record.update_record()

    redirect(URL('access_api_users'))


@auth.requires_login()
def access_api_user_link_active(row):
    """
        Returns a link which allows (de)activating an api user.
    """
    record = db.sys_api_users(row.id)
    active = record.ActiveUser
    if active:
        link_text = SPAN(SPAN(_class='glyphicon glyphicon-ok'), ' ',
                         T("Enabled"))
        link_class = 'btn-success'
    else:
        link_text = SPAN(SPAN(_class='glyphicon glyphicon-remove'), ' ',
                         T("Disabled"))
        link_class = 'btn-danger'

    link = A(link_text,
             _href=URL('access_api_user_change_active_state', args=[row.id]),
             _class='btn btn-sm ' + link_class)

    return link


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def selfcheckin():
    """
        Self check-in settings
    """
    response.title = T("Settings")
    response.subtitle = T('Self check-in')
    response.view = 'general/only_content.html'

    show_subscriptions_prop = 'selfcheckin_show_subscriptions'
    show_subscriptions = get_sys_property(show_subscriptions_prop)

    form = SQLFORM.factory(
        Field('show_subscriptions', 'boolean',
              default=show_subscriptions,
              label=T("Show subscriptions under customer name")),
        submit_button=T("Save"),
        separator=' ',
        formstyle='bootstrap3_stacked'
    )

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']

    if form.accepts(request.vars, session):
        # check show subscriptions
        show_subscriptions = request.vars['show_subscriptions']

        row = db.sys_properties(Property=show_subscriptions_prop)
        if not row:
            db.sys_properties.insert(Property=show_subscriptions_prop,
                                     PropertyValue=show_subscriptions)
        else:
            row.PropertyValue = show_subscriptions
            row.update_record()

        # Clear cache
        cache_clear_sys_properties()
        # User feedback
        session.flash = T('Saved')
        # reload so the user sees how the values are stored in the db now
        redirect(URL('selfcheckin'))

    return dict(content=DIV(form, _class="col-md-6"),
                save=submit)


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def shop_customer_profile_features():
    """
        Customer profile settings
    """
    response.title = T("Settings")
    response.subtitle = T('Shop profiles')
    response.view = 'general/tabs_menu.html'

    crud.messages.submit_button = T("Save")
    crud.messages.record_updated = T("Saved")
    crud.settings.update_next = URL('settings', 'shop_customer_profile_features')
    crud.settings.update_deletable = False
    crud.settings.formstyle='bootstrap3_stacked'
    form = crud.update(db.customers_profile_features, 1) # there is and only will be one record

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']

    content = DIV(H4(T('Profile features')),
                  form)

    menu = shop_get_menu(request.function)

    return dict(content=content,
                menu=menu,
                save=submit)


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def shop_customers_profile_announcements():
    """
        List announcements for customer profiles
    """
    response.title = T("Settings")
    response.subtitle = T('Shop customer profile announcements')
    response.view = 'general/tabs_menu.html'

    db.customers_profile_announcements.id.readable = False
    # fields = [ db.cus.id,
    #            db.shop_links.Name,
    #            db.shop_links.URL ]
    links = [ shop_customers_profile_announcements_get_link_edit ]

    #maxtextlengths = {'shop_links.Name': 30,
    #                  'shop_links.URL': 50}
    grid = SQLFORM.grid(db.customers_profile_announcements,
                        #fields=fields,
                        links=links,
                        #maxtextlengths=maxtextlengths,
                        create=False,
                        editable=False,
                        deletable=True,
                        details=False,
                        searchable=False,
                        csv=False,
                        orderby=db.customers_profile_announcements.Startdate|\
                                db.customers_profile_announcements.Title,
                        field_id=db.customers_profile_announcements.id,
                        ui=grid_ui)
    grid.element('.web2py_counter', replace=None)  # remove the counter
    # remove text from delete button
    grid.elements('span[title=Delete]', replace=None)

    add_url = URL('shop_customers_profile_announcement_add')
    add = os_gui.get_button('add', add_url, T("Add a new announcement to profiles"))

    menu = shop_get_menu(request.function)

    return dict(content=grid,
                menu=menu,
                add=add)


def shop_customers_profile_announcements_get_link_edit(row):
    """
        This function returns the edit link for a payment method,
        if the id is > 3. The first 3 are reserved for OpenStudio defined
        methods.
    """
    edit = os_gui.get_button('edit',
                             URL('shop_customers_profile_announcement_edit', vars={'cpaID':row.id}),
                             T("Edit this announcement"))

    return edit


def shop_customers_profile_announcement_add():
    """
        Add a new announcement to profiles
    """
    response.title = T("New profile announcement")
    response.subtitle = T('')
    response.view = 'general/only_content.html'

    return_url = URL('shop_customers_profile_announcements')

    crud.messages.submit_button = T("Save")
    crud.messages.record_created = T("Saved")
    crud.settings.create_next = return_url
    form = crud.create(db.customers_profile_announcements)

    # textareas = form.elements('textarea')
    # for textarea in textareas:
    #     textarea['_class'] += ' tmced'

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']

    submit = form.element('input[type=submit]')

    back = os_gui.get_button('back', return_url)

    return dict(content=form, back=back, save=submit)


def shop_customers_profile_announcement_edit():
    """
        Edit an announcement
    """
    response.title = T("Edit customer profile announcement")
    response.subtitle = T('')
    response.view = 'general/only_content.html'

    cpaID = request.vars['cpaID']

    return_url = URL('shop_customers_profile_announcements')

    crud.messages.submit_button = T("Save")
    crud.messages.record_created = T("Saved")
    crud.settings.update_next = return_url
    form = crud.update(db.customers_profile_announcements, cpaID)

    # textareas = form.elements('textarea')
    # for textarea in textareas:
    #     textarea['_class'] += ' tmced'

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']

    submit = form.element('input[type=submit]')

    back = os_gui.get_button('back', return_url)

    return dict(content=form, back=back, save=submit)



@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def shop_features():
    """
        Customer shop settings
    """
    response.title = T("Settings")
    response.subtitle = T('Shop features')
    response.view = 'general/tabs_menu.html'

    crud.messages.submit_button = T("Save")
    crud.messages.record_updated = T("Saved")
    crud.settings.update_next = URL('settings', 'shop_features')
    crud.settings.update_deletable = False
    crud.settings.formstyle='bootstrap3_stacked'
    form = crud.update(db.customers_shop_features, 1) # there is and only will be one record

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']

    content = DIV(H4(T('Shop features')),
                  form)

    menu = shop_get_menu(request.function)

    return dict(content=content,
                menu=menu,
                save=submit)


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def shop_subscriptions():
    """
        Set default terms for all subscriptions
    """
    response.title = T("Settings")
    response.subtitle = T('Shop subscriptions')
    response.view = 'general/tabs_menu.html'

    sprop_terms = 'shop_subscriptions_terms'
    sprop_message_activated = 'shop_subscriptions_message_activated'
    sprop_mandate = 'shop_direct_debit_mandate_text'

    terms = get_sys_property(sprop_terms)
    mandate = get_sys_property(sprop_mandate)
    message_activated = get_sys_property(sprop_message_activated)

    form = SQLFORM.factory(
        Field("subscriptions_terms", 'text',
              default=terms,
              label=T("Terms & conditions for all subscriptions")),
        Field("direct_debit_mandate_text", 'text',
              default=mandate,
              label=T("Mandate terms for direct debit"),
              comment=T(
                  'This has to be filled with a text to make clear to your customer, that he is agreeing to a direct debit Mandate, by accepting these terms. '
                  'This text will be added under the terms and conditions box when buying a subscription over the shop ')),
        Field("subscription_activated", 'text',
              default=message_activated,
              label=T("Subscription activated message"),
              comment=T('Message shown to customers in shop after a customer activates a subscription when using the "direct debit" workflow. This message is not shown when using Mollie as a payment provider for subscriptions.')),
        submit_button=T("Save"),
        separator=' ',
        formstyle='bootstrap3_stacked')

    form_elements = form.elements('textarea')
    for fe in form_elements:
        fe['_class'] += ' tmced'

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']

    if form.accepts(request.vars, session):
        # check subscription terms
        set_sys_property(
            sprop_terms,
            request.vars['subscriptions_terms']
        )

        # check mandate
        set_sys_property(
            sprop_mandate,
            request.vars['direct_debit_mandate_text']
        )

        # check message activated
        set_sys_property(
            sprop_message_activated,
            request.vars['subscription_activated']
        )

        # Clear cache
        cache_clear_sys_properties()
        # User feedback
        session.flash = T('Saved')

        # reload so the user sees how the values are stored in the db now
        redirect(URL())

    content = form
    menu = shop_get_menu(request.function)

    return dict(content=content,
                menu=menu,
                save=submit)


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def shop_classcards():
    """
        Set default terms for all subscriptions
    """
    response.title = T("Settings")
    response.subtitle = T('Shop classcards')
    response.view = 'general/tabs_menu.html'

    sprop_terms = 'shop_classcards_terms'

    terms = get_sys_property(sprop_terms)

    form = SQLFORM.factory(
        Field("classcards_terms", 'text',
              default=terms,
              label=T("Terms & conditions for all classcards")),
        submit_button=T("Save"),
        separator=' ',
        formstyle='bootstrap3_stacked')

    form_elements = form.elements('textarea')
    for fe in form_elements:
        fe['_class'] += ' tmced'

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']

    if form.accepts(request.vars, session):
        # check subscription terms
        set_sys_property(
            sprop_terms,
            request.vars['classcards_terms']
        )

        # Clear cache
        cache_clear_sys_properties()
        # User feedback
        session.flash = T('Saved')

        # reload so the user sees how the values are stored in the db now
        redirect(URL())

    content = form
    menu = shop_get_menu(request.function)

    return dict(content=content,
                menu=menu,
                save=submit)


# @auth.requires(auth.has_membership(group_id='Admins') or
#                auth.has_permission('read', 'settings'))
# def shop_direct_debit_mandate():
#     """
#         Set default terms for all subscriptions
#     """
#     response.title = T("Settings")
#     response.subtitle = T('Shop Direct Debit Mandate ')
#     response.view = 'general/tabs_menu.html'
#
#     sys_property = 'shop_direct_debit_mandate_text'
#     mandate = get_sys_property(sys_property)
#
#     form = SQLFORM.factory(
#         Field("direct_debit_mandate_text", 'text',
#               default=mandate,
#               label=T("Mandate terms for direct debit"),
#               comment= T('This has to be filled with a text to make clear to your customer, that he is agreeing to a direct debit Mandate, by accepting these terms. '
#                          'This text will be added under the terms and conditions box when buying a subscription over the shop ')),
#         submit_button=T("Save"),
#         separator=' ',
#         formstyle='bootstrap3_stacked')
#
#     form_element = form.element('#no_table_direct_debit_mandate_text')
#     form_element['_class'] += ' tmced'
#
#     result = set_form_id_and_get_submit_button(form, 'MainForm')
#     form = result['form']
#     submit = result['submit']
#
#     if form.accepts(request.vars, session):
#         # check mandate
#         direct_debit_mandate_text = request.vars['direct_debit_mandate_text']
#         row= db.sys_properties(Property=sys_property)
#         if not row:
#             db.sys_properties.insert(
#                 Property=sys_property,
#                 PropertyValue= direct_debit_mandate_text)
#         else:
#             row.PropertyValue = direct_debit_mandate_text
#             row.update_record()
#         # Clear cache
#         cache_clear_sys_properties()
#         # User feedback
#         session.flash = T('Saved')
#
#         # reload so the user sees how the values are stored in the db now
#         redirect(URL())
#
#     content = form
#     menu = shop_get_menu(request.function)
#
#     return dict(content=content,
#                 menu=menu,
#                 save=submit)


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def shop_membership_terms():
    """
        Set default terms for all subscriptions
    """
    response.title = T("Settings")
    response.subtitle = T('Shop membership terms')
    response.view = 'general/tabs_menu.html'

    sys_property = 'shop_memberships_terms'
    terms = get_sys_property(sys_property)

    form = SQLFORM.factory(
        Field("membership_terms", 'text',
              default=terms,
              label=T("Terms & conditions for all memberships")),
        submit_button=T("Save"),
        separator=' ',
        formstyle='bootstrap3_stacked')

    form_element = form.element('#no_table_membership_terms')
    form_element['_class'] += ' tmced'

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']

    if form.accepts(request.vars, session):
        # check terms
        set_sys_property(
            sys_property,
            request.vars['membership_terms']
        )

        # Clear cache
        cache_clear_sys_properties()
        # User feedback
        session.flash = T('Saved')

        # reload so the user sees how the values are stored in the db now
        redirect(URL())

    content = form
    menu = shop_get_menu(request.function)

    return dict(content=content,
                menu=menu,
                save=submit)

@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def shop_donations():
    """
        Set default terms for all subscriptions
    """
    response.title = T("Settings")
    response.subtitle = T('Shop donations')
    response.view = 'general/tabs_menu.html'

    tr_query = (db.tax_rates.Archived == False)

    sys_property = 'shop_donations_tax_rates_id'
    tax_rates_id = get_sys_property(sys_property)
    sys_property_shop_text = 'shop_donations_shop_text'
    shop_text = get_sys_property(sys_property_shop_text)
    sys_property_create_invoice = 'shop_donations_create_invoice'
    create_invoice = get_sys_property(sys_property_create_invoice)
    if create_invoice == 'on':
        create_invoice = True
    else:
        create_invoice = False

    form = SQLFORM.factory(
        Field('create_invoice', 'boolean',
              default=create_invoice,
              label=T("Create invoices for donations")),
        Field('tax_rates_id', db.tax_rates,
              requires=IS_IN_DB(db(tr_query),
                                'tax_rates.id',
                                '%(Name)s'),
              default=tax_rates_id,
              label=T("Default tax rate for donations received through the shop")),
        Field('shop_text', 'text',
              default=shop_text,
              label=T("Text above form in shop")),
        submit_button=T("Save"),
        separator=' ',
        formstyle='bootstrap3_stacked')


    form_element = form.element('#no_table_shop_text')
    form_element['_class'] += ' tmced'

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']

    if form.accepts(request.vars, session):
        # check tax rates
        tax_rates_id = request.vars['tax_rates_id']
        row = db.sys_properties(Property=sys_property)
        if not row:
            db.sys_properties.insert(
                Property=sys_property, PropertyValue=tax_rates_id)
        else:
            row.PropertyValue = tax_rates_id
            row.update_record()

        # create invoices setting
        create_invoice = request.vars['create_invoice']
        row = db.sys_properties(Property=sys_property_create_invoice)
        if not row:
            db.sys_properties.insert(
                Property=sys_property_create_invoice, PropertyValue=create_invoice)
        else:
            row.PropertyValue = create_invoice
            row.update_record()

        # shop text setting
        shop_text = request.vars['shop_text']
        row = db.sys_properties(Property=sys_property_shop_text)
        if not row:
            db.sys_properties.insert(
                Property=sys_property_shop_text, PropertyValue=shop_text)
        else:
            row.PropertyValue = shop_text
            row.update_record()

        # Clear cache
        cache_clear_sys_properties()
        # User feedback
        session.flash = T('Saved')

        # reload so the user sees how the values are stored in the db now
        redirect(URL())

    content = DIV(B(T('Invoices')), form)
    menu = shop_get_menu(request.function)

    return dict(content=content,
                menu=menu,
                save=submit)


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def shop_links():
    """
        Add links to shop menu
    """
    response.title = T("Settings")
    response.subtitle = T('Shop links')
    response.view = 'general/tabs_menu.html'

    db.shop_links.id.readable = False
    fields = [ db.shop_links.id,
               db.shop_links.Name,
               db.shop_links.URL ]
    links = [ shop_links_get_link_edit ]
    # links = [financial_payment_methods_get_link_edit,
    #          financial_payment_methods_get_link_archive]

    maxtextlengths = {'shop_links.Name': 30,
                      'shop_links.URL': 50}
    grid = SQLFORM.grid(db.shop_links,
                        fields=fields,
                        links=links,
                        maxtextlengths=maxtextlengths,
                        create=False,
                        editable=False,
                        deletable=True,
                        details=False,
                        searchable=False,
                        csv=False,
                        orderby=db.shop_links.Name,
                        field_id=db.shop_links.id,
                        ui=grid_ui)
    grid.element('.web2py_counter', replace=None)  # remove the counter
    # remove text from delete button
    grid.elements('span[title=Delete]', replace=None)

    add_url = URL('shop_link_add')
    add = os_gui.get_button('add', add_url, T("Add a new link to the shop menu"))

    content = grid
    menu = shop_get_menu(request.function)

    return dict(content=content,
                menu=menu,
                add=add)


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def shop_link_add():
    """
        This function shows an add page for shop link
    """
    response.title = T("New shop link")
    response.subtitle = T('')
    response.view = 'general/only_content.html'

    return_url = URL('shop_links')

    crud.messages.submit_button = T("Save")
    crud.messages.record_created = T("Saved")
    crud.settings.create_next = return_url
    form = crud.create(db.shop_links)

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']

    submit = form.element('input[type=submit]')

    back = os_gui.get_button('back', return_url)

    return dict(content=form, back=back, save=submit)


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def shop_link_edit():
    """
        This function shows an edit page for a shop link
    """
    response.title = T("Edit shop link")
    response.subtitle = T('')
    response.view = 'general/only_content.html'

    slID = request.vars['slID']

    return_url = URL('shop_links')

    crud.messages.submit_button = T("Save")
    crud.messages.record_created = T("Saved")
    crud.settings.update_next = return_url
    form = crud.update(db.shop_links, slID)

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']

    submit = form.element('input[type=submit]')

    back = os_gui.get_button('back', return_url)

    return dict(content=form, back=back, save=submit)


def shop_links_get_link_edit(row):
    """
        This function returns the edit link for a payment method,
        if the id is > 3. The first 3 are reserved for OpenStudio defined
        methods.
    """
    edit = os_gui.get_button('edit',
                             URL('shop_link_edit', vars={'slID':row.id}),
                             T("Edit this link"))

    return edit


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def shop_settings():
    """
        Page for general shop settings
    """
    response.title = T('Settings')
    response.subtitle = T('Shop General')
    response.view = 'general/tabs_menu.html'

    shop_header_logo_url = get_sys_property('shop_header_logo_url')
    shop_classes_dropin_message = get_sys_property('shop_classes_dropin_message')
    shop_classes_trial_message = get_sys_property('shop_classes_trial_message')
    shop_checkout_message_classes = get_sys_property('shop_checkout_message_classes')
    shop_checkout_message_memberships = get_sys_property('shop_checkout_message_memberships')
    shop_checkout_message_subscriptions = get_sys_property('shop_checkout_message_subscriptions')
    shop_checkout_message_classcards = get_sys_property('shop_checkout_message_classcards')
    shop_checkout_message_events = get_sys_property('shop_checkout_message_events')


    form = SQLFORM.factory(
        Field('shop_header_logo_url',
              requires=IS_EMPTY_OR(IS_URL()),
              default=shop_header_logo_url,
              label=T('Header logo link')),
        Field('shop_classes_dropin_message',
              default=shop_classes_dropin_message,
              label=T('Drop-in class booking options message'),
              comment=T('Message shown on the drop-in class option on the class booking options pages')),
        Field('shop_classes_trial_message',
              default=shop_classes_trial_message,
              label=T('Trial class booking options message'),
              comment=T('Message shown on the trial class option on the class booking options pages')),
        Field('shop_checkout_message_classes', 'text',
              default=shop_checkout_message_classes,
              label=T('Check out message classes'),
              comment=T('Message shown on the classes check out page')),
        Field('shop_checkout_message_memberships', 'text',
              default=shop_checkout_message_memberships,
              label=T('Check out message memberships'),
              comment=T('Message shown on the memberships check out page')),
        Field('shop_checkout_message_subscriptions', 'text',
              default=shop_checkout_message_subscriptions,
              label=T('Check out message subscriptions'),
              comment=T('Message shown on the subscriptions check out page')),
        Field('shop_checkout_message_classcards', 'text',
              default=shop_checkout_message_classcards,
              label=T('Check out message classcards'),
              comment=T('Message shown on the classcards check out page')),
        Field('shop_checkout_message_events', 'text',
              default=shop_checkout_message_events,
              label=T('Check out message events'),
              comment=T('Message shown on the events check out page')),
        submit_button=T("Save"),
        separator=' ',
        formstyle='bootstrap3_stacked'
    )

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']

    textareas = form.elements('textarea')
    for textarea in textareas:
        textarea['_class'] += ' tmced'

    if form.accepts(request.vars, session):
        value_names = [
            'shop_header_logo_url',
            'shop_classes_dropin_message',
            'shop_classes_trial_message',
            'shop_checkout_message_classes',
            'shop_checkout_message_memberships',
            'shop_checkout_message_subscriptions',
            'shop_checkout_message_classcards',
            'shop_checkout_message_events',
        ]

        # process vars
        for value_name in value_names:
            value = request.vars[value_name]
            set_sys_property(value_name, value)

        # Clear cache
        cache_clear_sys_properties()
        # User feedback
        session.flash = T('Saved')
        # reload so the user sees how the values are stored in the db now
        redirect(URL('shop_settings'))

    content = DIV(DIV(form, _class="col-md-12"),
                  _class='row')

    menu = shop_get_menu(request.function)

    return dict(content=content,
                menu=menu,
                save=submit)


def shop_get_menu(page):
    """
        Menu for system settings pages
    """
    pages = [['shop_settings',
              T('General'),
              URL('shop_settings')],
             ['shop_features',
              T('Features'),
              URL('shop_features')],
             ['shop_customer_profile_features',
              T('Profiles'),
              URL('shop_customer_profile_features')],
             ['shop_customers_profile_announcements',
              T('Profile announcements'),
              URL('shop_customers_profile_announcements')],
             ['shop_subscriptions',
              T('Subscriptions'),
              URL('shop_subscriptions')],
             # ['shop_classcards',
             #  T('Classcards'),
             #  URL('shop_classcards')],
             ['shop_membership_terms',
              T('Membership terms'),
              URL('shop_membership_terms')],
             ['shop_donations',
              T('Donations'),
              URL('shop_donations')],
             ['shop_links',
              T('Links'),
              'shop_links']
             ]

    return os_gui.get_submenu(pages, page, horizontal=True, htype='tabs')


@auth.requires(auth.user_id == 1)
def admin_redis_cache():
    """
        View cache stats
    """
    response.title = T("Sysadmin")
    response.subtitle = T('Redis cache')
    response.view = 'general/tabs_menu.html'

    cache_stats = cache.redis.stats()

    total = int(cache_stats['w2p_stats']['hit_total']) + int(cache_stats['w2p_stats']['misses'])
    try:
        hit_percent = round((float(cache_stats['w2p_stats']['hit_total']) / float(total)), 2)
    except ZeroDivisionError:
        hit_percent = 0

    try:
        miss_percent = round((float(cache_stats['w2p_stats']['misses']) / float(total)) , 2)
    except ZeroDivisionError:
        miss_percent = 0


    content = DIV(
        H3(T('Performance')),
        DIV(DIV(TABLE(TR(TH(T('Total')), TD(total), TD()),
                      TR(TH(T('Hits')), TD(cache_stats['w2p_stats']['hit_total']), TD(hit_percent * 100, '%')),
                      TR(TH(T('Misses')), TD(cache_stats['w2p_stats']['misses']), TD(miss_percent * 100, '%')),
                      TR(TH(T('Keys')), TD(cache_stats['db0']['keys']), TD()),
                      _class='table table-condensed table-hover'),
                _class='col-md-4'),
            _class='row'),
        H3(T('Resources')),
        DIV(DIV(TABLE(TR(TH(T('Memory Used')), TD(cache_stats['used_memory_human'])),
                      TR(TH(T('Memory Peak')), TD(cache_stats['used_memory_peak_human'])),
                      TR(TH(T('CPU Used')), TD(cache_stats['used_cpu_user'])),
                      _class='table table-condensed table-hover'),
                _class='col-md-4'),
            _class='row'),
        H3(T('Tools')),
        os_gui.get_button('noicon',
                          URL('admin_redis_cache_clear'),
                          title=T('Clear Redis cache'),
                          btn_size=''),
    )

    menu = admin_get_menu(request.function)

    return dict(content=content,
                menu=menu)


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def admin_redis_cache_clear():
    """
        Clears the cache
    """
    cache.ram.clear(regex='.*')

    redirect(URL('admin_redis_cache'))


@auth.requires(auth.user_id == 1)
def admin_storage_set_limit():
    """
        page to set the storage limit for this OpenStudio installation
    """
    response.title = T("Sysadmin")
    response.subtitle = T("Storage limit")
    response.view = 'general/tabs_menu.html'

    row = db.sys_properties(Property='storage_allowed_space')
    allowed_space = row.PropertyValue

    form = SQLFORM.factory(
        Field('space', 'integer',
              default=allowed_space,
              label=T("Allowed space in MB"),),
        submit_button=T("Save"),
        separator=' ',
        formstyle='bootstrap3_stacked'
    )

    if 'space' in request.vars:
        row = db.sys_properties(Property='storage_allowed_space')
        row.PropertyValue = request.vars['space']
        row.update_record()

        redirect(URL('system_storage'))

    menu = admin_get_menu(request.function)

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']

    return dict(
        content=form,
        menu=menu,
        save=submit
    )


@auth.requires(auth.user_id == 1)
def admin_scheduled_tasks_run():
    """
        List items in scheduler_run
    """
    from general_helpers import max_string_length

    page = request.vars['page'] or 0

    response.title = T("Sysadmin")
    response.subtitle = T("")
    response.view = 'general/tabs_menu.html'

    ## Pagination begin
    if 'page' in request.vars:
        try:
            page = int(request.vars['page'])
        except ValueError:
            page = 0
    else:
        page = 0
    items_per_page = 11
    limitby=(page*items_per_page,(page+1)*items_per_page+1)
    ## Pagination end

    header = THEAD(TR(TH(T('TaskID')),
                      TH(T('Status')),
                      TH(T('Start time')),
                      TH(T('Stop time')),
                      TH(T('vars')),
                      TH(T('Run output')),
                      TH(T('Run result')),
                      TH(T('Traceback')),
                      TH(T('Worker')),
                      TH(T('Actions')),
                      ))
    table = TABLE(header, _class='table table-condensed table-striped table-hover small_font')

    left = [
        db.scheduler_task.on(
            db.scheduler_run.task_id ==
            db.scheduler_task.id
        )
    ]


    query = (db.scheduler_run.id > 0)
    rows = db(query).select(
        db.scheduler_run.ALL,
        db.scheduler_task.ALL,
        left=left,
        orderby=~db.scheduler_run.start_time,
        limitby=limitby)

    for i, row in enumerate(rows):
        repr_row = list(rows[i:i + 1].render())[0]

        details = os_gui.get_button('noicon',
                                    URL('admin_scheduled_tasks_run_result',
                                        vars={'srID':row.scheduler_run.id}),
                                    title=T('Details'),
                                    _class='pull-right')

        label_type = 'primary'
        if row.scheduler_run.status == 'FAILED':
            label_type = 'danger'
        elif row.scheduler_run.status == 'COMPLETED':
            label_type = 'success'

        status = os_gui.get_label(label_type, row.scheduler_run.status)

        tr = TR(
            TD(row.scheduler_task.id),
            TD(status),
            TD(row.scheduler_run.start_time),
            TD(row.scheduler_run.stop_time),
            TD(row.scheduler_task.vars),
            TD(row.scheduler_run.run_output),
            TD(row.scheduler_run.run_result),
            TD(max_string_length(row.scheduler_run.traceback, 32)),
            TD(row.scheduler_run.worker_name),
            TD(details),
        )

        table.append(tr)


    ## Pager begin
    navigation = ''
    url_previous = ''
    url_next = ''
    if len(rows) > items_per_page or page:
        previous = SPAN(_class='fa fa-chevron-left grey')
        if page:
            url_previous = URL(request.function, vars={'page':page-1})
            previous = A(SPAN(_class='fa fa-chevron-left'),
                         _href=url_previous)

        nxt = SPAN(_class='fa fa-chevron-right grey')
        if len(rows) > items_per_page:
            url_next = URL(request.function, vars={'page':page+1})
            nxt = A(SPAN(_class='fa fa-chevron-right'),
                    _href=url_next)


        navigation = os_gui.get_page_navigation_simple(url_previous, url_next, page + 1, request.cid)

    ## Pager End

    submenu = admin_scheduler_get_menu(request.function)
    menu = admin_get_menu('admin_scheduled_tasks')

    return dict(content=DIV(submenu, table, navigation),
                menu=menu)


@auth.requires(auth.user_id == 1)
def admin_scheduled_tasks_run_result():
    """
        Show result of scheduler run
    """
    response.title = T("Sysadmin")
    response.subtitle = T("")
    response.view = 'general/tabs_menu.html'

    srID = request.vars['srID']

    sr = db.scheduler_run(srID)

    content = DIV(
        H4(T('Run result details')), BR(),
        DIV(DIV(LABEL(T('TaskID')), _class='col-md-2'),
            DIV(sr.task_id, _class='col-md-3'),
            _class='row'),
        DIV(DIV(LABEL(T('Status')), _class='col-md-2'),
            DIV(sr.status, _class='col-md-3'),
            _class='row'),
        DIV(DIV(LABEL(T('Start')), _class='col-md-2'),
            DIV(sr.start_time, _class='col-md-3'),
            _class='row'),
        DIV(DIV(LABEL(T('Stop')), _class='col-md-2'),
            DIV(sr.stop_time, _class='col-md-3'),
            _class='row'),
        DIV(DIV(LABEL(T('Worker')), _class='col-md-2'),
            DIV(sr.worker_name, _class='col-md-3'),
            _class='row'),
        DIV(DIV(LABEL(T('Run output')), _class='col-md-2'),
            DIV(sr.run_output, _class='col-md-9'),
            _class='row'),
        DIV(DIV(LABEL(T('Run result')), _class='col-md-2'),
            DIV(sr.run_result, _class='col-md-9'),
            _class='row'),
        DIV(DIV(LABEL(T('Traceback')), _class='col-md-2'),
            DIV(XML(sr.traceback.replace("\n", "<br>") if sr.traceback else ''), _class='col-md-9'),
            _class='row'),
    )

    back = os_gui.get_button('back', URL('admin_scheduled_tasks_run'))
    menu = admin_get_menu('admin_scheduled_tasks_run')

    return dict(content=content,
                back=back,
                menu=menu)


@auth.requires(auth.user_id == 1)
def admin_scheduled_tasks():
    """
        List tasks in db.scheduler_tasks
    """
    response.title = T("Sysadmin")
    response.subtitle = T("")
    response.view = 'general/tabs_menu.html'

    header = THEAD(TR(TH(T('id')),
                      TH(T('App, Task & Function name')),
                      TH(T('Vars')),
                      TH(T('Group name')),
                      TH(T('Status')),
                      TH(T('enabled')),
                      TH(T('Start')),
                      TH(T('Next run')),
                      TH(T('Last run')),
                      TH(T('Stop')),
                      TH(T('Period')),
                      TH(T('Prevent drift')),
                      ))
    table = TABLE(header, _class='table table-striped table-hover small_font')

    query = (db.scheduler_task)
    rows = db(query).select(db.scheduler_task.ALL,
                            orderby=~db.scheduler_task.id)

    for i, row in enumerate(rows):
        repr_row = list(rows[i:i + 1].render())[0]

        edit = os_gui.get_button('edit',
                                 URL('admin_scheduled_tasks_edit', vars={'stID':row.id}))

        tr = TR(
            TD(row.id),
            TD(row.application_name, BR(),
               row.task_name, BR(),
               row.function_name),
            TD(row.vars),
            TD(row.group_name),
            TD(row.status),
            TD(row.enabled),
            TD(row.start_time),
            TD(row.next_run_time),
            TD(row.last_run_time),
            TD(row.stop_time),
            TD(row.period),
            TD(row.prevent_drift),
            TD(edit)
        )

        table.append(tr)


    submenu = admin_scheduler_get_menu(request.function)
    add = os_gui.get_button('add', URL('admin_scheduled_tasks_add'))
    menu = admin_get_menu(request.function)

    return dict(content=DIV(submenu, table),
                add = add,
                menu=menu)



@auth.requires(auth.user_id == 1)
def admin_scheduler_workers():
    """
        List tasks in db.scheduler_tasks
    """
    response.title = T("Sysadmin")
    response.subtitle = T("")
    response.view = 'general/tabs_menu.html'

    header = THEAD(TR(TH(T('Name')),
                      TH(T('First Heartbeat')),
                      TH(T('Last heartbeat')),
                      TH(T('Status')),
                      TH(T('Ticker')),
                      TH(T('Groups')),
                      ))
    table = TABLE(header, _class='table table-striped table-hover')

    query = (db.scheduler_worker)
    rows = db(query).select(db.scheduler_worker.ALL,
                            orderby=db.scheduler_worker.status|db.scheduler_worker.worker_name)

    for i, row in enumerate(rows):
        repr_row = list(rows[i:i + 1].render())[0]

        # edit = os_gui.get_button('edit',
        #                          URL('admin_scheduled_tasks_edit', vars={'stID':row.id}))

        tr = TR(
            TD(row.worker_name),
            TD(row.first_heartbeat),
            TD(row.last_heartbeat),
            TD(row.status),
            TD(row.is_ticker),
            TD(row.group_names),
        )

        table.append(tr)

    submenu = admin_scheduler_get_menu(request.function)
    menu = admin_get_menu('admin_scheduled_tasks')

    return dict(content=DIV(submenu, table),
                menu=menu)


@auth.requires(auth.user_id == 1)
def admin_scheduled_tasks_add():
    """
        Add a scheduled task
    """
    response.title = T("Sysadmin")
    response.subtitle = T("")
    response.view = 'general/tabs_menu.html'

    return_url = URL('admin_scheduled_tasks')

    db.scheduler_task.prevent_drift.default = True

    crud.messages.submit_button = T("Save")
    crud.messages.record_created = T("Saved")
    crud.settings.create_next = return_url
    crud.settings.formstyle='bootstrap3_stacked'
    form = crud.create(db.scheduler_task)


    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']

    back = os_gui.get_button('back', return_url)
    menu = admin_get_menu('admin_scheduled_tasks')

    return dict(content=DIV(H4(T("Add task")), form),
                back=back,
                save=submit,
                menu=menu)


@auth.requires(auth.user_id == 1)
def admin_scheduled_tasks_edit():
    """
        Add a scheduled task
    """
    response.title = T("Sysadmin")
    response.subtitle = T("")
    response.view = 'general/tabs_menu.html'

    stID = request.vars['stID']

    return_url = URL('admin_scheduled_tasks')

    db.scheduler_task.status.writable = True

    crud.messages.submit_button = T("Save")
    crud.messages.record_updated = T("Saved")
    crud.settings.update_next = return_url
    crud.settings.formstyle='bootstrap3_stacked'
    form = crud.update(db.scheduler_task, stID)


    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']

    back = os_gui.get_button('back', return_url)
    menu = admin_get_menu('admin_scheduled_tasks')

    return dict(content=DIV(H4(T('Edit task')), form),
                back=back,
                save=submit,
                menu=menu)


def admin_scheduler_get_menu(page):
    """
        Submenu for scheduler admin pages
    """
    pages = [['admin_scheduled_tasks',
              T('Tasks'),
              URL('admin_scheduled_tasks')],
             ['admin_scheduled_tasks_run',
              T('Run log'),
              URL('admin_scheduled_tasks_run')],
             ['admin_scheduler_workers',
              T('Workers'),
              URL('admin_scheduler_workers')]
             ]

    return os_gui.get_submenu(pages, page, horizontal=True, htype='tabs')


def admin_get_menu(page):
    """
        Menu for admin pages
    """
    pages = [ ['admin_redis_cache',
               T('Redis cache'),
               URL('admin_redis_cache')],
              ['admin_storage_set_limit',
               T('Storage limit'),
               URL('admin_storage_set_limit')],
              ['admin_scheduled_tasks',
               T('Scheduler'),
               URL('admin_scheduled_tasks')]
        ]

    return os_gui.get_submenu(pages, page, horizontal=True, htype='tabs')


