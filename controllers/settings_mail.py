# -*- coding: utf-8 -*-
"""
    This file holds the settings for email
"""

def mail_get_menu(page):
    """
        Menu for system settings pages
    """
    pages = [['mailing_lists',
              T('Mailing lists'),
              URL('mailing_lists')],
             ['templates',
              T('Templates'),
              URL('templates')],
             ]

    return os_gui.get_submenu(pages, page, horizontal=True, htype='tabs')


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def mailing_lists():
    """
        Show mailing lists
    """
    from openstudio.os_mailinglists import MailingLists

    response.title = T('Settings')
    response.subtitle = T('Mail')
    response.view = 'general/tabs_menu.html'

    mailing_lists = MailingLists()
    content = mailing_lists.list_formatted()

    add = os_gui.get_button('add', URL('settings_mail', 'mailing_list_add'))
    menu = mail_get_menu(request.function)

    return dict(content=content,
                add=add,
                menu=menu)


def mailing_list_get_return_url(var=None):
    """
        :return: URL to lists
    """
    return URL('settings_mail', 'mailing_lists')


@auth.requires_login()
def mailing_list_add():
    """
        Add a new mailing_list
    """
    from openstudio.os_forms import OsForms
    response.title = T('Settings')
    response.subtitle = T('Mail')
    response.view = 'general/tabs_menu.html'

    return_url = mailing_list_get_return_url()

    os_forms = OsForms()
    result = os_forms.get_crud_form_create(
        db.mailing_lists,
        return_url,
    )

    form = result['form']
    back = os_gui.get_button('back', return_url)
    menu = mail_get_menu('mailing_lists')

    content = DIV(
        H4(T('Add mailing list')),
        form
    )

    return dict(content=content,
                save=result['submit'],
                back=back,
                menu=menu)


@auth.requires_login()
def mailing_list_edit():
    """
        Edit a mailing_list
        request.vars['mlID'] is expected to be db.mailing_lists.id
    """
    from openstudio.os_forms import OsForms

    response.title = T('Shop')
    response.subtitle = T('Catalog')
    response.view = 'general/tabs_menu.html'
    mlID = request.vars['mlID']

    return_url = mailing_list_get_return_url()

    os_forms = OsForms()
    result = os_forms.get_crud_form_update(
        db.mailing_lists,
        return_url,
        mlID
    )

    form = result['form']
    back = os_gui.get_button('back', return_url)
    menu = mail_get_menu('mailing_lists')

    content = DIV(
        H4(T('Edit mailing list')),
        form
    )

    return dict(content=content,
                save=result['submit'],
                back=back,
                menu=menu)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('delete', 'mailing_lists'))
def mailing_list_delete():
    """
        Delete a mailing list
        request.vars[mlID] is expected to be in db.mailing_lists.id
        :return: None
    """
    mlID = request.vars['mlID']

    query = (db.mailing_lists.id == mlID)
    db(query).delete()

    session.flash = T('Deleted mailing list')
    redirect(mailing_list_get_return_url())


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def templates():
    """
        Templates main
    """
    response.title = T('System Settings')
    response.subtitle = T('Email templates')
    response.view = 'settings/email_templates.html'

    #NOTE: in the end, the drop down select will go here to select a default template
    header = THEAD(TR(
        TH('Templates'),

        TH(T(''))
    ))

    table = TABLE(header, _class='table table-hover table-striped')

    query = (db.sys_email_templates.id >0)
    rows = db(query).select(db.sys_email_templates.id,
                            db.sys_email_templates.Title,
                            orderby= db.sys_email_templates.Title)
    for i, row in enumerate(rows):
        repr_row = list(rows[i:i + 1].render())[0]


        tr = TR(
                TD(repr_row.Title),
                os_gui.get_button('edit',
                              URL('template_edit', args=[row.id]),
                              T("Edit the content of this template"))
                )

        table.append(tr)
    # submenu = email_templates_get_menu(request.function)

    content = DIV(table)
    return dict(content=content,
                menu=mail_get_menu(request.function),
                left_sidebar_enabled=True)


def email_templates_get_menu(page):
    """
        Return menu for invoice templates
    """
    pages = [ ['templates', T('Info'),
               URL('templates')],
              # ['email_template_invoice_created', T('Invoice created'),
              #  URL('email_template', vars={'template':'email_template_invoice_created'})],
              ['email_template_order_received', T('Order received'),
               URL('template', vars={'template': 'email_template_order_received'})],
              ['email_template_order_delivered', T('Order delivered'),
               URL('template', vars={'template': 'email_template_order_delivered'})],
              # ['email_template_payment_received', T('Payment received'),
              #  URL('email_template', vars={'template':'email_template_payment_received'})],
              ['email_template_payment_recurring_failed', T('Payment recurring failed'),
               URL('template', vars={'template':'email_template_payment_recurring_failed'})],
              ['email_template_sys_footer', T('Email footer'),
               URL('template', vars={'template':'email_template_sys_footer'})],
              ['email_template_sys_reset_password', T('System reset password'),
               URL('template', vars={'template':'email_template_sys_reset_password'})],
              ['email_template_sys_verify_email', T('System verify email'),
               URL('template', vars={'template':'email_template_sys_verify_email'})]
              ]

    return os_gui.get_submenu(pages, page, horizontal=True, htype='tabs')


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def template():
    """
        Page to edit an email_template
    """
    from openstudio.os_forms import OsForms

    response.title = T('System Settings')
    response.subtitle = T('Email Templates')
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

    os_forms = OsForms()
    result = os_forms.set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']

    if form.accepts(request.vars, session):
        # check smtp_signature
        email_template = request.vars['email_template']
        set_sys_property(template, email_template)

        # User feedback
        session.flash = T('Saved')

        # reload so the user sees how the values are stored in the db now
        redirect(URL(vars={'template':template}))

    submenu = email_templates_get_menu(template)
    content = DIV(submenu, BR(), form)

    return dict(content=content,
                menu=mail_get_menu('templates'),
                save=submit)




