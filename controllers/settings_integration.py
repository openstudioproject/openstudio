# -*- coding: utf-8 -*-
"""
    This file holds the settings for integrations
"""

def integration_get_menu(page):
    """
        Menu for system settings pages
    """
    pages = [['mollie',
              T('Mollie'),
              URL('mollie')],
             ['mailchimp',
              T('MailChimp'),
              URL('mailchimp')],
             ]

    return os_gui.get_submenu(pages, page, horizontal=True, htype='tabs')


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def mollie():
    """
        Page to set Mollie website profile
    """
    response.title = T("Integration")
    response.subtitle = T("Mollie")
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
        # check payment provider
        online_payment_provider = request.vars['online_payment_provider']
        row = db.sys_properties(Property='online_payment_provider')
        if not row:
            db.sys_properties.insert(Property='online_payment_provider',
                                     PropertyValue=online_payment_provider)
        else:
            row.PropertyValue = online_payment_provider
            row.update_record()

        # Check mollie profile
        mollie_website_profile = request.vars['mollie_website_profile']
        row = db.sys_properties(Property='mollie_website_profile')
        if not row:
            db.sys_properties.insert(Property='mollie_website_profile',
                                     PropertyValue=mollie_website_profile)
        else:
            row.PropertyValue = mollie_website_profile
            row.update_record()

        # Clear cache
        cache_clear_sys_properties()
        # User feedback
        session.flash = T('Saved')
        # reload so the user sees how the values are stored in the db now
        redirect(URL('mollie'))

    menu = integration_get_menu(request.function)

    return dict(content=DIV(mollie_signup, form),
                menu=menu,
                save=submit)
