# -*- coding: utf-8 -*-

from general_helpers import max_string_length
from general_helpers import set_form_id_and_get_submit_button

@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'schedule_tags'))
def index():
    """
        Lists announcements
    """
    response.title = T("Schedule")
    response.subtitle = T("Tags")
    response.view = 'general/only_content.html'

    fields = [ db.schedule_tags.Name ]
    # check edit permission
    permission = auth.has_membership(group_id='Admins') or \
                 auth.has_permission('update', 'schedule_tags')
    if permission:
        links = [ lambda row: os_gui.get_button('edit',
                                                URL('edit', vars={'stID':row.id}),
                                                T("Edit tag")) ]
        deletable = True
    else:
        links = []
        deletable=False

    # check delete permission
    delete_permission = auth.has_membership(group_id='Admins') or \
                 auth.has_permission('delete', 'schedule_tags')
    deletable = delete_permission

    grid = SQLFORM.grid(db.schedule_tags, fields=fields, links=links,
        create=False,
        editable=False,
        deletable=deletable,
        details=False,
        searchable=False,
        csv=False,
        orderby=db.schedule_tags.Name,
        field_id=db.schedule_tags.id,
        ui = grid_ui)
    grid.element('.web2py_counter', replace=None) # remove the counter
    grid.elements('span[title=Delete]', replace=None) # remove text from delete button

    # add button
    add = ''
    permission = auth.has_membership(group_id='Admins') or \
                 auth.has_permission('create', 'schedule_tags')
    if permission:
        add = os_gui.get_button('add', URL('add'), T("New tag"))

    back = DIV(os_gui.get_button('back', URL('classes', 'schedule')),
               add)

    return dict(content=grid, back=back)


@auth.requires_login()
def add():
    """
        This function shows an add page for a tag
    """
    response.title = T("Schedule")
    response.subtitle = T("New tag")
    response.view = 'general/only_content.html'

    return_url = URL('index')

    crud.messages.submit_button = T("Save")
    crud.messages.record_created = T("Added tag")
    crud.settings.formstyle = "divs"
    crud.settings.create_next = return_url
    form = crud.create(db.schedule_tags)

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']

    back = os_gui.get_button('back', return_url)

    return dict(content=form, back=back, save=submit)


@auth.requires_login()
def edit():
    """
        Shows edit page for a tag
        request.vars['stID'] is expected to be schedule_tags.id
    """
    stID = request.vars['stID']
    response.title = T("Schedule")
    response.subtitle = T("Edit tag")
    response.view = 'general/only_content.html'

    return_url = URL('index')

    crud.messages.submit_button = T("Save")
    crud.messages.record_updated = T("Saved")
    crud.settings.update_next = return_url
    crud.settings.update_deletable = False
    crud.settings.formstyle = "divs"
    form = crud.update(db.schedule_tags, stID)

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']

    back = os_gui.get_button('back', return_url)

    return dict(content=form, back=back, save=submit)
