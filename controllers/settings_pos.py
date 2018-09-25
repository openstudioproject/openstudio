# -*- coding: utf-8 -*-
"""
    This file holds the settings for integrations
"""



def pos_get_menu(page):
    """
        Menu for system settings pages
    """
    pages = [['index',
              T('General'),
              URL('index')],
             ]

    return os_gui.get_submenu(pages, page, horizontal=True, htype='tabs')


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def index():
    """
        Page to set mailchimp API key
    """
    from general_helpers import set_form_id_and_get_submit_button

    response.title = T("Settings")
    response.subtitle = T("Point of Sale")
    response.view = 'general/tabs_menu.html'

    pos_barcodes_checkin = get_sys_property('pos_customers_barcodes')

    form = SQLFORM.factory(
        Field('pos_customers_barcodes',
              requires=IS_IN_SET([
                  ['customer_id', T("Customer ID")],
                  ['membership_id', T("Customer membership ID")],
                ],
                zero=None),
              default=pos_barcodes_checkin,
              label=T('Checkin barcodes'),
              comment=T("Does the barcode scanner read customer ids or customer membership ids when checking in customers?")),
        submit_button=T("Save"),
        formstyle='bootstrap3_stacked',
        separator=' ')

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']

    if form.accepts(request.vars, session):
        pos_barcodes_checkin = request.vars['pos_customers_barcodes']
        set_sys_property('pos_customers_barcodes', pos_barcodes_checkin)

        # User feedback
        session.flash = T('Saved')
        # reload so the user sees how the values are stored in the db now
        redirect(URL('index'))

    menu = pos_get_menu(request.function)

    return dict(content=form,
                menu=menu,
                save=submit)

