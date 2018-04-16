# -*- coding: utf-8 -*-
"""
    This file holds the settings for email
"""

def mail_get_menu(page):
    """
        Menu for system settings pages
    """
    pages = [['lists',
              T('Lists'),
              URL('lists')],
             ['templates',
              T('Templates'),
              URL('templates')],
             ]

    return os_gui.get_submenu(pages, page, horizontal=True, htype='tabs')


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def lists():
    """
        Show mailing lists
    """
    from openstudio import ShopSuppliers
    from openstudio_tools import OsSession

    response.title = T('Settings')
    response.subtitle = T('Mail')
    response.view = 'general/tabs_menu.html'

    suppliers = ShopSuppliers()
    content = suppliers.list_formatted()

    add = os_gui.get_button('add', URL('shop_manage', 'supplier_add'))
    archive_buttons = os_gui.get_archived_radio_buttons(
        session.shop_manage_suppliers_show)
    menu = catalog_get_menu(request.function)

    return dict(content=content,
                add=add,
                header_tools=archive_buttons,
                menu=menu)


def shop_supplier_get_return_url(var=None):
    """
        :return: URL to lists
    """
    return URL('settings_mail', 'lists')


@auth.requires_login()
def supplier_add():
    """
        Add a new supplier
    """
    from openstudio import OsForms
    response.title = T('Shop')
    response.subtitle = T('Catalog')
    response.view = 'general/tabs_menu.html'

    return_url = shop_supplier_get_return_url()

    os_forms = OsForms()
    result = os_forms.get_crud_form_create(
        db.shop_suppliers,
        return_url,
    )

    form = result['form']
    back = os_gui.get_button('back', return_url)
    menu = catalog_get_menu('suppliers')

    content = DIV(
        H4(T('Add supplier')),
        form
    )

    return dict(content=content,
                save=result['submit'],
                back=back,
                menu=menu)


@auth.requires_login()
def supplier_edit():
    """
        Edit a supplier
        request.vars['sbID'] is expected to be db.shop_brands.id
    """
    from openstudio import OsForms

    response.title = T('Shop')
    response.subtitle = T('Catalog')
    response.view = 'general/tabs_menu.html'
    supID = request.vars['supID']

    return_url = shop_supplier_get_return_url()

    os_forms = OsForms()
    result = os_forms.get_crud_form_update(
        db.shop_suppliers,
        return_url,
        supID
    )

    form = result['form']
    back = os_gui.get_button('back', return_url)
    menu = catalog_get_menu('suppliers')

    content = DIV(
        H4(T('Edit supplier')),
        form
    )

    return dict(content=content,
                save=result['submit'],
                back=back,
                menu=menu)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('update', 'shop_suppliers'))
def supplier_archive():
    """
        Archive a supplier
        request.vars[supID] is expected to be in db.shop_suppliers.id
        :return: None
    """
    from openstudio_tools import OsArchiver

    archiver = OsArchiver()
    archiver.archive(
        db.shop_suppliers,
        request.vars['supID'],
        T('Unable to (un)archive supplier'),
        shop_supplier_get_return_url()
    )







@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def email_templates():
    """
        Server settings
    """
    response.title = T('Settings')
    response.subtitle = T('Email')

    #NOTE: in the end, the drop down select will go here to select a default template
    content = T('For now you can only use the default template for emails. At some point in the future you can use your own.')
    content += T(' ')
    content += T('Until then, this page does nothing.')

    back = os_gui.get_button('back', URL('index'), _class='full-width')

    return dict(content=content,
                back=back,
                menu=email_templates_get_menu(request.function),
                left_sidebar_enabled=True)


def email_templates_get_menu(page):
    """
        Return menu for invoice templates
    """
    pages = [ ['email_templates', T('Default template'),
               URL('email_templates')],
              # ['email_template_invoice_created', T('Invoice created'),
              #  URL('email_template', vars={'template':'email_template_invoice_created'})],
              ['email_template_order_received', T('Order received'),
               URL('email_template', vars={'template': 'email_template_order_received'})],
              ['email_template_order_delivered', T('Order delivered'),
               URL('email_template', vars={'template': 'email_template_order_delivered'})],
              # ['email_template_payment_received', T('Payment received'),
              #  URL('email_template', vars={'template':'email_template_payment_received'})],
              ['email_template_payment_recurring_failed', T('Payment recurring failed'),
               URL('email_template', vars={'template':'email_template_payment_recurring_failed'})],
              ['email_template_sys_footer', T('Email footer'),
               URL('email_template', vars={'template':'email_template_sys_footer'})],
              ['email_template_sys_reset_password', T('System reset password'),
               URL('email_template', vars={'template':'email_template_sys_reset_password'})],
              ['email_template_sys_verify_email', T('System verify email'),
               URL('email_template', vars={'template':'email_template_sys_verify_email'})]
              ]

    return os_gui.get_submenu(pages, page, horizontal=True, htype='tabs')


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def email_template():
    """
        Page to edit an email_template
    """
    response.title = T('Email Settings')
    response.subtitle = T('Templates')
    response.view = 'settings/email_templates.html'

    template = request.vars['template']

    template_content = get_sys_property(template)

    form = SQLFORM.factory(
        Field("email_template", 'text',
              default=template_content,
              label=T("Edit template")),
        submit_button=T("Save"),
        separator=' ',
        formstyle='bootstrap3_stacked')

    form_element = form.element('#no_table_email_template')
    form_element['_class'] += ' tmced'

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']

    if form.accepts(request.vars, session):
        # check smtp_signature
        email_template = request.vars['email_template']
        row = db.sys_properties(Property=template)
        if not row:
            db.sys_properties.insert(
                Property=template, PropertyValue=email_template)
        else:
            row.PropertyValue = email_template
            row.update_record()

        # Clear cache
        cache_clear_sys_properties()
        # User feedback
        session.flash = T('Saved')

        # reload so the user sees how the values are stored in the db now
        redirect(URL(vars={'template':template}))

    content = form

    back = os_gui.get_button('back', URL('index'))

    return dict(content=content,
                back=back,
                menu=email_templates_get_menu(template),
                save=submit)




