# -*- coding: utf-8 -*-
"""
    This file holds the settings for integrations
"""

def integration_get_menu(page):
    """
        Menu for system settings pages
    """
    pages = [
        [ 'exact_online',
          T('Exact online'),
          URL('exact_online')],
        [ 'mollie',
          T('Mollie'),
          URL('mollie') ],
        [ 'mailchimp',
          T('MailChimp'),
          URL('mailchimp') ],
    ]

    return os_gui.get_submenu(pages, page, horizontal=True, htype='tabs')


def exact_online_tools():
    """
    Get tools for exact online integration
    """
    links = [
        A(SPAN(_class="fa fa-lock"), " ", T("Authorize"),
          _href=URL('exact_online', 'authorize'),
          _title=T("Authorize")),
        A(SPAN(_class="fa fa-bank"), " ", T("Divisions"),
          _href=URL('exact_online', 'divisions'),
          _title=T("Divisions")),
    ]

    tools = os_gui.get_dropdown_menu(links,
                                     '',
                                     btn_size='',
                                     btn_icon='wrench',
                                     menu_class='pull-right' )

    return tools


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def exact_online():
    """
        Page to set Mollie website profile
    """
    from general_helpers import set_form_id_and_get_submit_button
    from openstudio.os_exact_online import OSExactOnline
    from ConfigParser import NoOptionError

    response.title = T("Settings")
    response.subtitle = T("Integration")
    response.view = 'general/tabs_menu.html'


    os_eo = OSExactOnline()
    storage = os_eo.get_storage()

    try:
        server_auth_url = storage.get('server', 'auth_url')
    except NoOptionError:
        server_auth_url = None
    try:
        server_rest_url = storage.get('server', 'rest_url')
    except NoOptionError:
        server_rest_url = None
    try:
        server_token_url = storage.get('server', 'token_url')
    except NoOptionError:
        server_token_url = None

    try:
        client_base_url = storage.get('application', 'base_url')
    except NoOptionError:
        client_base_url = None
    try:
        client_id = storage.get('application', 'client_id')
    except NoOptionError:
        client_id = None
    try:
        client_secret = storage.get('application', 'client_secret')
    except NoOptionError:
        client_secret = None


    form = SQLFORM.factory(
        Field('auth_url',
              requires=IS_URL(),
              default=server_auth_url,
              label=T("Server auth URL")),
        Field('rest_url',
              requires=IS_URL(),
              default=server_rest_url,
              label=T('Server rest URL')),
        Field('token_url',
              requires=IS_URL(),
              default=server_token_url,
              label=T('Server token URL')),
        Field('base_url',
              requires=IS_URL(),
              default=client_base_url,
              label=T('Client base URL'),
              comment=T('The base URL this OpenStudio installation eg. "https://demo.openstudioproject.com"')),
        Field('client_id',
              requires=IS_NOT_EMPTY(),
              default=client_id,
              label=T('Client ID')),
        Field('client_secret',
              requires=IS_NOT_EMPTY(),
              default=client_secret,
              label=T('Client Secret')),
        submit_button=T("Save"),
        formstyle='bootstrap3_stacked',
        separator=' ')

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = DIV(result['submit'], _class='pull-right')

    if form.accepts(request.vars, session):
        #TODO: set using ini storage

        # check server vars
        server_vars = [
            'auth_url',
            'rest_url',
            'token_url'
        ]
        for var in server_vars:
            value = request.vars[var]
            storage.set('server', var, value)

        # # check application vars
        application_vars = [
            'base_url',
            'client_id',
            'client_secret'
        ]
        for var in application_vars:
            value = request.vars[var]
            storage.set('application', var, value)

        # User feedback
        session.flash = T('Saved')
        # reload so the user sees how the values are stored in the db now
        redirect(URL('exact_online'))

    menu = integration_get_menu(request.function)
    tools = exact_online_tools()

    return dict(content=form,
                menu=menu,
                tools=tools,
                save=submit)



@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def mailchimp():
    """
        Page to set mailchimp API key
    """
    response.title = T("Settings")
    response.subtitle = T("Integration")
    response.view = 'general/tabs_menu.html'

    mailchimp_api_key = get_sys_property('mailchimp_api_key')
    mailchimp_username = get_sys_property('mailchimp_username')

    form = SQLFORM.factory(
        Field('mailchimp_username',
              requires=IS_NOT_EMPTY(),
              default=mailchimp_username,
              label=T('MailChimp User name')),
        Field('mailchimp_api_key',
              requires=IS_NOT_EMPTY(),
              default=mailchimp_api_key,
              label=T('MailChimp API key')),
        submit_button=T("Save"),
        formstyle='bootstrap3_stacked',
        separator=' ')

    form_id = "MainForm"
    form_element = form.element('form')
    form['_id'] = form_id

    elements = form.elements('input, select, textarea')
    for element in elements:
        element['_form'] = form_id

    submit = form.element('input[type=submit]')

    if form.accepts(request.vars, session):
        mailchimp_api_key = request.vars['mailchimp_api_key']
        set_sys_property('mailchimp_api_key', mailchimp_api_key)
        mailchimp_username = request.vars['mailchimp_username']
        set_sys_property('mailchimp_username', mailchimp_username)

        # User feedback
        session.flash = T('Saved')
        # reload so the user sees how the values are stored in the db now
        redirect(URL('mailchimp'))

    menu = integration_get_menu(request.function)

    return dict(content=form,
                menu=menu,
                save=submit)


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def mollie():
    """
        Page to set Mollie website profile
    """
    response.title = T("Settings")
    response.subtitle = T("Integration")
    response.view = 'general/tabs_menu.html'

    payment_providers = [
        [ 'disabled', T("Don't accept online payments") ],
        [ 'mollie', T('Mollie') ]
    ]

    online_payment_provider = get_sys_property('online_payment_provider')
    mollie_website_profile = get_sys_property('mollie_website_profile')

    form = SQLFORM.factory(
        Field('online_payment_provider',
              requires=IS_IN_SET(payment_providers),
              default=online_payment_provider,
              label=T("Payment provider")),
        Field('mollie_website_profile',
              requires=IS_NOT_EMPTY(),
              default=mollie_website_profile,
              label=T('Mollie website profile (API-Key)')),
        submit_button=T("Save"),
        formstyle='bootstrap3_stacked',
        separator=' ')

    form_id = "MainForm"
    form_element = form.element('form')
    form['_id'] = form_id

    elements = form.elements('input, select, textarea')
    for element in elements:
        element['_form'] = form_id

    submit = form.element('input[type=submit]')

    mollie_signup = ''
    if not mollie_website_profile:
        create_mollie_account = A(T('Create Mollie account'),
                                  _href='https://www.mollie.com/nl/signup/2488481',
                                  _target="_blank",
                                  _class='btn btn-info')
        mollie_signup = os_gui.get_alert('info',
            SPAN(SPAN(T('Mollie website profile not found'), _class='bold'), BR(),
            T("Please click the button below to sign up with Mollie and create a website profile, or enter the website profile key below."), BR(),
            BR(),
            create_mollie_account))

    if form.accepts(request.vars, session):
        # check payment provider and profile id
        vars = [
            'online_payment_provider',
            'mollie_website_profile'
        ]
        for var in vars:
            value = request.vars[var]
            set_sys_property(var, value)

        online_payment_provider = request.vars['online_payment_provider']

        # User feedback
        session.flash = T('Saved')
        # reload so the user sees how the values are stored in the db now
        redirect(URL('mollie'))

    menu = integration_get_menu(request.function)

    return dict(content=DIV(mollie_signup, form),
                menu=menu,
                save=submit)
