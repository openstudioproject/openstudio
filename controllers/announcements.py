# -*- coding: utf-8 -*-

from general_helpers import max_string_length
from general_helpers import set_form_id_and_get_submit_button

@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'announcements'))
def index():
    '''
        Lists announcements
    '''
    response.title = T("Pinboard")
    response.subtitle = T("Announcements")
    response.view = 'general/only_content.html'

    fields = [ db.announcements.Title,
               db.announcements.Note,
               db.announcements.Startdate,
               db.announcements.Enddate,
               db.announcements.Priority,
               db.announcements.Visible ]
    # check edit permission
    permission = auth.has_membership(group_id='Admins') or \
                 auth.has_permission('update', 'announcements')
    if permission:
        links = [ lambda row: os_gui.get_button('edit',
                                                URL('edit', vars={'aID':row.id}),
                                                T("Edit anouncement")) ]
        deletable = True
    else:
        links = []
        deletable=False

    # check delete permission
    delete_permission = auth.has_membership(group_id='Admins') or \
                 auth.has_permission('delete', 'announcements')
    deletable = delete_permission

    grid = SQLFORM.grid(db.announcements, fields=fields, links=links,
        create=False,
        editable=False,
        deletable=deletable,
        details=False,
        searchable=False,
        csv=False,
        orderby = ~db.announcements.Startdate|\
                  db.announcements.Priority|\
                  db.announcements.Title,
        field_id=db.announcements.id,
        ui = grid_ui)
    grid.element('.web2py_counter', replace=None) # remove the counter
    grid.elements('span[title=Delete]', replace=None) # remove text from delete button

    # add button
    add = ''
    permission = auth.has_membership(group_id='Admins') or \
                 auth.has_permission('create', 'announcements')
    if permission:
        add = os_gui.get_button('add', URL('add'), T("New announcement"))

    back = DIV(os_gui.get_button('back', URL('pinboard', 'index')),
               add)

    return dict(content=grid, back=back)


@auth.requires_login()
def add():
    """
        This function shows an add page for an announcement
    """
    response.title = T("Pinboard")
    response.subtitle = T("New announcement")
    response.view = 'general/only_content.html'

    return_url = URL('index')

    crud.messages.submit_button = T("Save")
    crud.messages.record_created = T("Added announcement")
    crud.settings.create_next = return_url
    form = crud.create(db.announcements)

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']

    back = os_gui.get_button('back', return_url)

    return dict(content=form, back=back, save=submit)


@auth.requires_login()
def edit():
    '''
        Shows edit page for an announcement
        request.vars['aID'] is expected to be announcements.id
    '''
    aID = request.vars['aID']
    response.title = T("Pinboard")
    response.subtitle = T("Edit announcement")
    response.view = 'general/only_content.html'

    return_url = URL('index')

    crud.messages.submit_button = T("Save")
    crud.messages.record_updated = T("Saved")
    crud.settings.update_next = return_url
    crud.settings.update_deletable = False
    form = crud.update(db.announcements, aID)

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']

    back = os_gui.get_button('back', return_url)

    return dict(content=form, back=back, save=submit)
