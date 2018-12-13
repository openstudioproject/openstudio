# -*- coding: utf-8 -*-

import os
import datetime
import cStringIO
import openpyxl

from general_helpers import get_submenu
from general_helpers import set_form_id_and_get_submit_button

from openstudio.os_customers import Customers
from openstudio.os_school_subscription import SchoolSubscription


@auth.requires(auth.has_membership(group_id='Admins') or \
                auth.has_permission('read', 'school_classtypes'))
def classtypes():
    response.title = T("School")
    response.subtitle = T("Class types")
    response.view = 'general/only_content.html'

    show = 'current'
    query = (db.school_classtypes.Archived == False)

    if 'show_archive' in request.vars:
        show = request.vars['show_archive']
        session.school_classtypes_show = show
        if show == 'current':
            query = (db.school_classtypes.Archived == False)
        elif show == 'archive':
            query = (db.school_classtypes.Archived == True)
    elif session.school_classtypes_show == 'archive':
            query = (db.school_classtypes.Archived == True)
    else:
        session.school_classtypes_show = show

    db.school_classtypes.id.readable=False
    fields = [ db.school_classtypes.thumbsmall,
               db.school_classtypes.Name,
               db.school_classtypes.Link,
               #db.school_classtypes.Description,
               db.school_classtypes.AllowAPI ]
    links = [ lambda row: os_gui.get_button('edit',
                                     URL('classtype_edit', args=[row.id]),
                                     T("Edit the name of this classtype")),
              classtypes_get_link_archive ]
    maxtextlengths = {'school_classtypes.Name' : 50,
                      'school_classtypes.Link' : 120,
                      'school_classtypes.Description' : 60}
    grid = SQLFORM.grid(query,
                        maxtextlengths=maxtextlengths,
                        fields=fields,
                        links=links,
                        create=False,
                        editable=False,
                        deletable=False,
                        details=False,
                        searchable=False,
                        csv=False,
                        orderby=db.school_classtypes.Name,
                        ui = grid_ui)
    grid.element('.web2py_counter', replace=None) # remove the counter
    grid.elements('span[title=Delete]', replace=None) # remove text from delete button

    add_url = URL('classtype_add')
    add = os_gui.get_button('add', add_url, T("Add a new class type"), _class='pull-right')

    archive_buttons = os_gui.get_archived_radio_buttons(
        session.school_classtypes_show)

    back = DIV(add, archive_buttons)

    return dict(content=grid, back=back)


def classtypes_get_link_archive(row):
    """
        Called from the index function. Changes title of archive button
        depending on whether a classtype is archived or not
    """
    row = db.school_classtypes(row.id)

    if row.Archived:
        tt = T("Move to current")
    else:
        tt = T("Archive")

    return os_gui.get_button('archive',
                             URL('classtypes_archive', vars={'ctID':row.id}),
                             tooltip=tt)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('update', 'school_classtypes'))
def classtypes_archive():
    """
        This function archives a subscription
        request.vars[ctID] is expected to be the school_classtypes ID
    """
    ctID = request.vars['ctID']
    if not ctID:
        session.flash = T('Unable to (un)archive class type')
    else:
        row = db.school_classtypes(ctID)

        if row.Archived:
            session.flash = T('Moved to current')
        else:
            session.flash = T('Archived')

        row.Archived = not row.Archived
        row.update_record()

    redirect(URL('classtypes'))


@auth.requires_login()
def classtype_add():
    """
        This function shows an add page for a classtype
    """
    response.title = T("New class type")
    response.subtitle = T('')
    response.view = 'general/only_content.html'

    return_url = URL('classtypes')

    crud.messages.submit_button = T("Save")
    crud.messages.record_created = T("Added new class type")
    crud.settings.create_next = return_url
    crud.settings.formstyle = 'bootstrap3_stacked'
    form = crud.create(db.school_classtypes)

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


@auth.requires_login()
def classtype_edit():
    """
        This function shows an edit page for a classtype
        request.args[0] is expected to be the school_classtypes_id (ctID)
    """
    ctID = request.args[0]
    response.title = T("Edit class type")
    response.subtitle = T('')
    response.view = 'general/only_content.html'

    return_url = URL('classtypes')

    crud.messages.submit_button = T("Save")
    crud.messages.record_updated = T("Saved")
    crud.settings.update_next = return_url
    crud.settings.update_deletable = False
    crud.settings.formstyle = 'bootstrap3_stacked'
    form = crud.update(db.school_classtypes, ctID)

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


@auth.requires(auth.has_membership(group_id='Admins') or \
                auth.has_permission('read', 'school_discovery'))
def discovery():
    response.title = T("School")
    response.subtitle = T("Discovery")
    response.view = 'general/only_content.html'

    show = 'current'
    query = (db.school_discovery.Archived == False)

    if 'show_archive' in request.vars:
        show = request.vars['show_archive']
        session.school_discovery_show = show
        if show == 'current':
            query = (db.school_discovery.Archived == False)
        elif show == 'archive':
            query = (db.school_discovery.Archived == True)
    elif session.school_discovery_show == 'archive':
            query = (db.school_discovery.Archived == True)
    else:
        session.school_discovery_show = show

    db.school_discovery.id.readable=False
    maxtextlengths = {'school_discovery.Name' : 60}
    fields = [db.school_discovery.Name]
    links = [ lambda row: os_gui.get_button('edit',
                                URL('discovery_edit', args=[row.id]),
                                T("Edit the name of this way of discovery")),
              discovery_get_link_archive ]
    grid = SQLFORM.grid(query, fields=fields, links=links,
        create=False,
        editable=False,
        deletable=False,
        details=False,
        searchable=False,
        csv=False,
        maxtextlengths=maxtextlengths,
        orderby=db.school_discovery.Name,
        ui = grid_ui)
    grid.element('.web2py_counter', replace=None) # remove the counter
    grid.elements('span[title=Delete]', replace=None) # remove text from delete button

    add_url = URL('discovery_add')
    add = os_gui.get_button('add', add_url, T("Add a new way of discovery"), _class='pull-right')

    archive_buttons = os_gui.get_archived_radio_buttons(
        session.school_discovery_show)

    back = DIV(add, archive_buttons)

    return dict(content=grid, back=back)


def discovery_get_link_archive(row):
    """
        Called from the index function. Changes title of archive button
        depending on whether a level is archived or not
    """
    row = db.school_discovery(row.id)

    if row.Archived:
        tt = T("Move to current")
    else:
        tt = T("Archive")

    return os_gui.get_button('archive',
                             URL('discovery_archive', vars={'sdID':row.id}),
                             tooltip=tt)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('update', 'school_discovery'))
def discovery_archive():
    """
        This function archives a subscription
        request.vars[sdID] is expected to be the school_discovery ID
    """
    sdID = request.vars['sdID']
    if not sdID:
        session.flash = T('Unable to (un)archive discovery')
    else:
        row = db.school_discovery(sdID)

        if row.Archived:
            session.flash = T('Moved to current')
        else:
            session.flash = T('Archived')

        row.Archived = not row.Archived
        row.update_record()

    redirect(URL('discovery'))


@auth.requires_login()
def discovery_add():
    """
        This function shows an add page for a way of discovery
    """
    response.title = T("New way of discovery")
    response.subtitle = T('')
    response.view = 'general/only_content.html'

    return_url = URL('discovery')

    crud.messages.submit_button = T("Save")
    crud.messages.record_created = T("Saved")
    crud.settings.create_next = return_url
    crud.settings.formstyle = 'bootstrap3_stacked'
    form = crud.create(db.school_discovery)

    form_id = "MainForm"
    form_element = form.element('form')
    form['_id'] = form_id

    elements = form.elements('input, select, textarea')
    for element in elements:
        element['_form'] = form_id

    submit = form.element('input[type=submit]')

    back = os_gui.get_button('back', return_url)

    return dict(content=form, back=back, save=submit)


@auth.requires_login()
def discovery_edit():
    """
        This function shows an edit page for a way of discovery
        request.args[0] is expected to be the discoveryID
    """
    discoveryID = request.args[0]
    response.title = T("Edit way of discovery")
    response.subtitle = T('')
    response.view = 'general/only_content.html'

    return_url = URL('discovery')

    crud.messages.submit_button = T("Save")
    crud.messages.record_updated = T("Saved")
    crud.settings.update_next = return_url
    crud.settings.update_deletable = False
    crud.settings.formstyle = 'bootstrap3_stacked'
    form = crud.update(db.school_discovery, discoveryID)

    form_id = "MainForm"
    form_element = form.element('form')
    form['_id'] = form_id

    elements = form.elements('input, select, textarea')
    for element in elements:
        element['_form'] = form_id

    submit = form.element('input[type=submit]')

    back = os_gui.get_button('back', return_url)

    return dict(content=form, back=back, save=submit)


@auth.requires(auth.has_membership(group_id='Admins') or \
                auth.has_permission('read', 'school_locations'))
def locations():
    response.title = T("School")
    response.subtitle = T("Locations")
    response.view = 'general/only_content.html'

    show = 'current'
    query = (db.school_locations.Archived == False)

    if 'show_archive' in request.vars:
        show = request.vars['show_archive']
        session.school_locations_show = show
        if show == 'current':
            query = (db.school_locations.Archived == False)
        elif show == 'archive':
            query = (db.school_locations.Archived == True)
    elif session.school_locations_show == 'archive':
            query = (db.school_locations.Archived == True)
    else:
        session.school_locations_show = show

    db.school_locations.id.readable=False
    fields = [db.school_locations.Name,
              db.school_locations.AllowAPI]
    links = [ lambda row: os_gui.get_button('edit',
                                      URL('location_edit', args=[row.id]),
                                      T("Edit the name of this location")),
              locations_get_link_archive ]
    grid = SQLFORM.grid(query, fields=fields, links=links,
        create=False,
        editable=False,
        deletable=False,
        details=False,
        searchable=False,
        csv=False,
        ui = grid_ui)
    grid.element('.web2py_counter', replace=None) # remove the counter
    grid.elements('span[title=Delete]', replace=None) # remove text from delete button

    add_url = URL('location_add')
    add = os_gui.get_button('add', add_url, T("Add a location"), _class="pull-right")

    archive_buttons = os_gui.get_archived_radio_buttons(
        session.school_locations_show)

    back = DIV(add, archive_buttons)

    return dict(content=grid, back=back)


def locations_get_link_archive(row):
    """
        Called from the index function. Changes title of archive button
        depending on whether a location is archived or not
    """
    row = db.school_locations(row.id)

    if row.Archived:
        tt = T("Move to current")
    else:
        tt = T("Archive")

    return os_gui.get_button('archive',
                             URL('locations_archive', vars={'locID':row.id}),
                             tooltip=tt)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('update', 'school_locations'))
def locations_archive():
    """
        This function archives a subscription
        request.vars[locID] is expected to be the school_locations ID
    """
    locID = request.vars['locID']
    if not locID:
        session.flash = T('Unable to (un)archive location')
    else:
        row = db.school_locations(locID)

        if row.Archived:
            session.flash = T('Moved to current')
        else:
            session.flash = T('Archived')

        row.Archived = not row.Archived
        row.update_record()

    redirect(URL('locations'))


@auth.requires_login()
def location_add():
    """
        This function shows an add page for a location
    """
    response.title = T("New location")
    response.subtitle = T('')
    response.view = 'general/only_content.html'

    return_url = URL('locations')

    crud.messages.submit_button = T("Save")
    crud.messages.record_created = T("Added location")
    crud.settings.create_next = return_url
    crud.settings.formstyle = 'bootstrap3_stacked'
    form = crud.create(db.school_locations)

    form_id = "MainForm"
    form_element = form.element('form')
    form['_id'] = form_id

    elements = form.elements('input, select, textarea')
    for element in elements:
        element['_form'] = form_id

    submit = form.element('input[type=submit]')

    back = os_gui.get_button('back', return_url)

    return dict(content=form, back=back, save=submit)


@auth.requires_login()
def location_edit():
    """
        This function shows an edit page for a location
        request.args[0] is expected to be the locationID (locID)
    """
    locID = request.args[0]
    response.title = T("Edit location")
    response.subtitle = T('')
    response.view = 'general/only_content.html'

    return_url = URL('locations')

    crud.messages.submit_button = T("Save")
    crud.messages.record_updated = T("Updated location")
    crud.settings.update_next = return_url
    crud.settings.update_deletable = False
    crud.settings.formstyle = 'bootstrap3_stacked'
    form = crud.update(db.school_locations, locID)

    form_id = "MainForm"
    form_element = form.element('form')
    form['_id'] = form_id

    elements = form.elements('input, select, textarea')
    for element in elements:
        element['_form'] = form_id

    submit = form.element('input[type=submit]')


    back = os_gui.get_button('back', return_url)

    return dict(content=form, back=back, save=submit)


@auth.requires(auth.has_membership(group_id='Admins') or \
                auth.has_permission('read', 'school_levels'))
def levels():
    response.title = T("School")
    response.subtitle = T("Practice levels")
    response.view = 'general/only_content.html'
    db.school_levels.id.readable=False

    show = 'current'
    query = (db.school_levels.Archived == False)

    if 'show_archive' in request.vars:
        show = request.vars['show_archive']
        session.school_levels_show = show
        if show == 'current':
            query = (db.school_levels.Archived == False)
        elif show == 'archive':
            query = (db.school_levels.Archived == True)
    elif session.school_levels_show == 'archive':
            query = (db.school_levels.Archived == True)
    else:
        session.school_levels_show = show


    fields = [db.school_levels.Name]
    links = [ lambda row: os_gui.get_button('edit',
                                     URL('level_edit', args=[row.id]),
                                     T("Edit this practice level")),
              levels_get_link_archive ]
    grid = SQLFORM.grid(query, fields=fields, links=links,
        create=False,
        editable=False,
        deletable=False,
        details=False,
        searchable=False,
        csv=False,
        orderby = db.school_levels.Name,
        ui = grid_ui)
    grid.element('.web2py_counter', replace=None) # remove the counter
    grid.elements('span[title=Delete]', replace=None) # remove text from delete button

    add_url = URL('level_add')
    add = os_gui.get_button('add', add_url, T("Add a new practice level"), _class="pull-right")

    archive_buttons = os_gui.get_archived_radio_buttons(
        session.school_levels_show)

    back = DIV(add, archive_buttons)

    return dict(content=grid, back=back)


def levels_get_link_archive(row):
    """
        Called from the index function. Changes title of archive button
        depending on whether a level is archived or not
    """
    row = db.school_levels(row.id)

    if row.Archived:
        tt = T("Move to current")
    else:
        tt = T("Archive")

    return os_gui.get_button('archive',
                             URL('levels_archive', vars={'slID':row.id}),
                             tooltip=tt)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('update', 'school_levels'))
def levels_archive():
    """
        This function archives a subscription
        request.vars[slID] is expected to be the school_levels ID
    """
    slID = request.vars['slID']
    if not slID:
        session.flash = T('Unable to (un)archive level')
    else:
        row = db.school_levels(slID)

        if row.Archived:
            session.flash = T('Moved to current')
        else:
            session.flash = T('Archived')

        row.Archived = not row.Archived
        row.update_record()

    redirect(URL('levels'))


@auth.requires_login()
def level_add():
    """
        This function shows an add page for a practice level
    """
    response.title = T("New practice level")
    response.subtitle = T('')
    response.view = 'general/only_content.html'

    return_url = URL('levels')

    crud.messages.submit_button = T("Save")
    crud.messages.record_created = T("Added practice level")
    crud.settings.create_next = return_url
    crud.settings.formstyle = 'bootstrap3_stacked'
    form = crud.create(db.school_levels)

    form_id = "MainForm"
    form_element = form.element('form')
    form['_id'] = form_id

    elements = form.elements('input, select, textarea')
    for element in elements:
        element['_form'] = form_id

    submit = form.element('input[type=submit]')

    back = os_gui.get_button('back', return_url)

    return dict(content=form, back=back, save=submit)


@auth.requires_login()
def level_edit():
    """
        This function shows an edit page for a practice level
        request.args[0] is expected to be the school levelID (plID)
    """
    slID = request.args[0]
    response.title = T("Edit practice level")
    response.subtitle = T('')
    response.view = 'general/only_content.html'

    return_url = URL('levels')

    crud.messages.submit_button = T("Save")
    crud.messages.record_updated = T("Updated practice level")
    crud.settings.update_next = return_url
    crud.settings.update_deletable = False
    crud.settings.formstyle = 'bootstrap3_stacked'
    form = crud.update(db.school_levels, slID)

    form_id = "MainForm"
    form_element = form.element('form')
    form['_id'] = form_id

    elements = form.elements('input, select, textarea')
    for element in elements:
        element['_form'] = form_id

    submit = form.element('input[type=submit]')

    back = os_gui.get_button('back', return_url)

    return dict(content=form, back=back, save=submit)


def memberships_get_return_url(var=None):
    """
    :return: URL linking back to memberships index
    """
    return URL('memberships')


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'school_memberships'))
def memberships():
    """
        This function shows a page to list memberships.
    """
    response.title = T("School")
    response.subtitle = T("Memberships")
    response.view = "general/only_content.html"

    show = 'current'
    query = (db.school_memberships.Archived == False)

    if 'show_archive' in request.vars:
        show = request.vars['show_archive']
        session.school_memberships_show = show
        if show == 'current':
            query = (db.school_memberships.Archived == False)
        elif show == 'archive':
            query = (db.school_memberships.Archived == True)
    elif session.school_memberships_show == 'archive':
        query = (db.school_memberships.Archived == True)
    else:
        session.school_memberships_show = show

    db.school_memberships.id.readable = False

    fields = [
        db.school_memberships.Name,
        db.school_memberships.Description,
        db.school_memberships.Validity,
        db.school_memberships.ValidityUnit,
        db.school_memberships.PublicMembership
    ]

    links = [dict(header=T('Price'),
                  body=memberships_get_link_current_price),
             lambda row: os_gui.get_button('edit',
                                           URL('membership_edit',
                                               vars={'smID': row.id}),
                                           T("Edit this membership type")),
             memberships_get_link_archive]
    maxtextlengths = {'school_memberships.Name': 40}
    maxtextlengths = {'school_memberships.Description': 40}
    grid = SQLFORM.grid(query, fields=fields, links=links,
                        maxtextlengths=maxtextlengths,
                        create=False,
                        editable=False,
                        deletable=False,
                        details=False,
                        searchable=False,
                        csv=False,
                        orderby=db.school_memberships.Name,
                        ui=grid_ui)
    grid.element('.web2py_counter', replace=None)  # remove the counter
    grid.elements('span[title=Delete]', replace=None)  # remove text from delete button

    add_url = URL('membership_add')
    add = os_gui.get_button('add', add_url, T("Add a new memberships"), _class='pull-right')
    archive_buttons = os_gui.get_archived_radio_buttons(
        session.school_memberships_show)

    back = DIV(add, archive_buttons)
    content = grid

    return dict(back=back,
                content=content)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('update', 'school_memberships'))
def membership_archive():
    """
        This function archives a membership
        request.vars[ssuID] is expected to be the school_memberships ID
    """
    smID = request.vars['smID']
    if not smID:
        session.flash = T('Unable to (un)archive membership')
    else:
        row = db.school_memberships(smID)

        if row.Archived:
            session.flash = T('Moved to current')
        else:
            session.flash = T('Archived')

        row.Archived = not row.Archived
        row.update_record()

        #cache_clear_school_memberships()

    redirect(URL('memberships'))


@auth.requires_login()
def membership_add():
    """
        This function shows an add page for a memberships
    """
    from openstudio.os_forms import OsForms
    response.title = T("New membership")
    response.subtitle = T('')
    response.view = 'general/only_content.html'

    return_url = memberships_get_return_url()

    os_forms = OsForms()
    result = os_forms.get_crud_form_create(
        db.school_memberships,
        return_url,
        tinymce_enabled=True
    )

    form = result['form']
    back = os_gui.get_button('back', return_url)

    return dict(content=form,
                save=result['submit'],
                back=back)


@auth.requires_login()
def membership_edit():
    """
        This function shows an edit page for a membership
        request.vars['smID'] is expected to be the db.school_memberships.id
    """
    from openstudio.os_forms import OsForms
    response.title = T("Edit membership")
    response.subtitle = T('')
    response.view = 'general/tabs_menu.html'

    smID = request.vars['smID']

    return_url = memberships_get_return_url()

    os_forms = OsForms()
    result = os_forms.get_crud_form_update(
        db.school_memberships,
        return_url,
        smID,
        tinymce_enabled=True
    )

    form = result['form']
    menu = membership_get_submenu(request.function, smID)
    back = membership_edit_get_back(return_url)

    return dict(content=form,
                save=result['submit'],
                menu=menu,
                back=back)


def membership_edit_get_back(return_url):
    """
        Returns back button for membership edit pages
    """
    return os_gui.get_button('back', return_url)


def membership_get_submenu(page, smID):
    """
        Returns submenu for memberships
    """
    vars = {'smID': smID}
    pages = [['membership_edit',
              T('Edit'),
              URL('membership_edit', vars=vars)],
             ['membership_prices',
              T('Prices'),
              URL('membership_prices', vars=vars)]]

    return get_submenu(pages, page, horizontal=True, htype='tabs')


def memberships_get_link_current_price(row):
    """
        Returns the current price for a membership
    """
    from openstudio.os_school_membership import SchoolMembership

    smID = row.id
    sm = SchoolMembership(smID)

    price = sm.get_price_on_date(TODAY_LOCAL)
    link = A(price,
             _href=URL('memberships_prices', vars={'smID': smID}),
             _title=T("Edit prices"))

    return link


def memberships_get_link_archive(row):
    """
        Called from the index function. Changes title of archive button
        depending on whether a workshop is archived or not
    """
    row = db.school_memberships(row.id)

    if row.Archived:
        tt = T("Move to current")
    else:
        tt = T("Archive")

    return os_gui.get_button('archive',
                             URL('membership_archive', vars={'smID': row.id}),
                             tooltip=tt)


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'school_memberships_price'))
def membership_prices():
    """
        Shows list of prices for a membership
    """
    smID = request.vars['smID']
    response.title = T("Edit membership")
    response.subtitle = T('')
    response.view = 'general/tabs_menu.html'

    return_url = URL('memberships')

    db.school_memberships_price.id.readable = False

    query = (db.school_memberships_price.school_memberships_id == smID)
    fields = [db.school_memberships_price.Startdate,
              db.school_memberships_price.Enddate,
              db.school_memberships_price.Price,
              db.school_memberships_price.tax_rates_id]
    links = [lambda row: os_gui.get_button('edit',
                                           URL('membership_price_edit',
                                               vars={'smID': smID,
                                                     'smpID': row.id}),
                                           T("Edit this price for this memberships"))]

    delete_permission = (auth.has_membership(group_id='Admins') or
                         auth.has_permission('delete', 'school_memberships_price'))

    grid = SQLFORM.grid(query, fields=fields, links=links,
                        create=False,
                        editable=False,
                        details=False,
                        searchable=False,
                        csv=False,
                        deletable=delete_permission,
                        # orderby = db.school_memberships_price.Startdate,
                        field_id=db.school_memberships_price.id,
                        ui=grid_ui)
    grid.element('.web2py_counter', replace=None)  # remove the counter
    grid.elements('span[title=Delete]', replace=None)  # remove text from delete button

    alert_msg = T("Please make sure the new price starts on the first day of a month and the previous price ends on the last day of the month before. ")
    alert_msg += T("Otherwise you might see unexpected results in the revenue stats.")
    alert_icon = SPAN(_class='glyphicon glyphicon-info-sign')
    alert = os_gui.get_alert('default', SPAN(alert_icon, ' ', alert_msg))

    add = os_gui.get_button('add',
                            URL('membership_price_add',
                                vars={'smID': smID}))

    menu = membership_get_submenu(request.function, smID)
    back = membership_edit_get_back(return_url)

    content = DIV(alert, grid)

    return_url = URL('memberships')

    return dict(content=content,
                back=back,
                add=add,
                menu=menu)


@auth.requires_login()
def membership_price_add():
    """
        Add a new price for a membership
    """
    from openstudio.os_forms import OsForms
    response.title = T("New membership price")
    response.subtitle = T('')
    response.view = 'general/only_content.html'
    smID = request.vars['smID']

    return_url = return_url = membership_price_get_return_url(smID)

    db.school_memberships_price.school_memberships_id.default = smID

    os_forms = OsForms()
    result = os_forms.get_crud_form_create(
        db.school_memberships_price,
        return_url,
    )

    form = result['form']
    back = membership_edit_get_back(return_url)

    return dict(content=form,
                save=result['submit'],
                back=back)


@auth.requires_login()
def membership_price_edit():
    """
        Edit price for a membership
    """
    from openstudio.os_forms import OsForms
    response.title = T("Edit membership price")
    response.subtitle = T('')
    response.view = 'general/only_content.html'
    smID = request.vars['smID']
    smpID = request.vars['smpID']

    return_url = return_url = membership_price_get_return_url(smID)

    os_forms = OsForms()
    result = os_forms.get_crud_form_update(
        db.school_memberships_price,
        return_url,
        smpID
    )

    form = result['form']
    back = membership_edit_get_back(return_url)

    return dict(content=form,
                save=result['submit'],
                back=back)


def membership_price_get_return_url(smID):
    """
        Returns returl url for memberships
    """
    return URL('membership_prices', vars={'smID': smID})


def subscriptions_get_menu(page=None):
    pages = []

    if auth.has_membership(group_id='Admins') or \
       auth.has_permission('read', 'school_subscriptions'):
        pages.append(['subscriptions',
                      T("Subscriptions"),
                      URL("school_properties","subscriptions")])
    if auth.has_membership(group_id='Admins') or \
       auth.has_permission('read', 'school_subscriptions_groups'):
        pages.append(['subscriptions_groups',
                      T("Groups"),
                      URL("school_properties","subscriptions_groups",)])

    return os_gui.get_submenu(pages, page, _id='os-customers_edit_menu', horizontal=True, htype='tabs')


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'school_subscriptions'))
def subscriptions():
    """
        This function shows a page to list subscriptions.
    """
    response.title = T("School")
    response.subtitle = T("Subscriptions")
    response.view = 'general/tabs_menu.html'

    show = 'current'
    query = (db.school_subscriptions.Archived == False)

    if 'show_archive' in request.vars:
        show = request.vars['show_archive']
        session.school_subscriptions_show = show
        if show == 'current':
            query = (db.school_subscriptions.Archived == False)
        elif show == 'archive':
            query = (db.school_subscriptions.Archived == True)
    elif session.school_subscriptions_show == 'archive':
            query = (db.school_subscriptions.Archived == True)
    else:
        session.school_subscriptions_show = show

    db.school_subscriptions.id.readable=False

    fields = [ db.school_subscriptions.Name,
               db.school_subscriptions.sys_organizations_id,
               db.school_subscriptions.Classes,
               db.school_subscriptions.SubscriptionUnit,
               db.school_subscriptions.PublicSubscription,
               db.school_subscriptions.SortOrder,
               db.school_subscriptions.Unlimited ]

    links = [ dict(header=T('Monthly Fee incl. VAT'),
                   body  =subscriptions_get_link_current_price),
              lambda row: os_gui.get_button('edit',
                                     URL('subscription_edit',
                                         vars={'ssuID':row.id}),
                                     T("Edit this subscription type")),
              subscriptions_get_link_archive ]
    maxtextlengths = {'school_subscriptions.Name' : 40}
    headers = {'school_subscriptions.SortOrder':'Sorting'}
    grid = SQLFORM.grid(query, fields=fields, links=links,
        maxtextlengths=maxtextlengths,
        headers=headers,
        create=False,
        editable=False,
        deletable=False,
        details=False,
        searchable=False,
        csv=False,
        orderby = ~db.school_subscriptions.SortOrder|db.school_subscriptions.Name,
        ui = grid_ui)
    grid.element('.web2py_counter', replace=None) # remove the counter
    grid.elements('span[title=Delete]', replace=None) # remove text from delete button

    add_url = URL('subscription_add')
    add = os_gui.get_button('add', add_url, T("Add a new subscription"), _class='pull-right')
    archive_buttons = os_gui.get_archived_radio_buttons(
        session.school_subscriptions_show)

    back = DIV(add, archive_buttons)
    menu = subscriptions_get_menu(request.function)

    content = grid

    return dict(back=back,
                menu=menu,
                content=content)


def subscriptions_get_link_current_price(row):
    """
        Returns the current price for a subscription
    """
    ssuID = row.id
    today = datetime.date.today()

    ssu = SchoolSubscription(ssuID)

    price = ssu.get_price_on_date(today)
    link = A(price,
             _href=URL('subscriptions_prices', vars={'ssuID':ssuID}),
             _title=T("Edit prices"))

    return link


def subscriptions_get_link_archive(row):
    """
        Called from the index function. Changes title of archive button
        depending on whether a workshop is archived or not
    """
    row = db.school_subscriptions(row.id)

    if row.Archived:
        tt = T("Move to current")
    else:
        tt = T("Archive")

    return os_gui.get_button('archive',
                             URL('subscriptions_archive', vars={'ssuID':row.id}),
                             tooltip=tt)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('update', 'school_subscriptions'))
def subscriptions_archive():
    """
        This function archives a subscription
        request.vars[ssuID] is expected to be the school_subscriptions ID
    """
    ssuID = request.vars['ssuID']
    if not ssuID:
        session.flash = T('Unable to (un)archive subscription')
    else:
        row = db.school_subscriptions(ssuID)

        if row.Archived:
            session.flash = T('Moved to current')
        else:
            session.flash = T('Archived')

        row.Archived = not row.Archived
        row.update_record()

        cache_clear_school_subscriptions()

    redirect(URL('subscriptions'))


@auth.requires_login()
def subscription_add():
    """
        This function shows an add page for a subscription
    """
    response.title = T("New subscription")
    response.subtitle = T('')
    response.view = 'general/only_content.html'

    db.school_subscriptions.Archived.readable=False
    db.school_subscriptions.Archived.writable=False

    return_url = URL('subscriptions')

    crud.messages.submit_button = T("Save")
    crud.messages.record_created = T("Added subscription")
    crud.settings.create_next = return_url
    crud.settings.create_onaccept = [cache_clear_school_subscriptions]
    crud.settings.formstyle = 'bootstrap3_stacked'
    form = crud.create(db.school_subscriptions)

    textareas = form.elements('textarea')
    for textarea in textareas:
        textarea['_class'] += ' tmced'

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']

    # placeholder for credits validity
    form.element('#school_subscriptions_CreditValidity')['_placeholder'] = T("Credits don't expire")


    submit = form.element('input[type=submit]')

    back = os_gui.get_button('back', return_url)

    return dict(content=form, back=back, save=submit)


@auth.requires_login()
def subscription_edit():
    """
        This function shows an edit page for a subscription
        request.vars['ssuID'] is expected to be the subscriptionID (ssuID)
    """
    ssuID = request.vars['ssuID']
    response.title = T("Edit subscription")
    subscription = db.school_subscriptions(ssuID)
    response.subtitle = subscription.Name
    response.view = 'general/tabs_menu.html'

    return_url = URL('subscriptions')

    crud.messages.submit_button = T("Save")
    crud.messages.record_updated = T("Updated subscription")
    crud.settings.update_next = return_url
    crud.settings.update_deletable = False
    crud.settings.update_onaccept = [cache_clear_school_subscriptions]
    crud.settings.formstyle = 'bootstrap3_stacked'
    form = crud.update(db.school_subscriptions, ssuID)

    textareas = form.elements('textarea')
    for textarea in textareas:
        textarea['_class'] += ' tmced'

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']

    form.element('#school_subscriptions_CreditValidity')['_placeholder'] = T("Credits don't expire")

    # input_classes = form.element('#school_subscriptions_NRofClasses')
    # input_classes['_placeholder'] = T('Unlimited')

    menu = subscriptions_get_submenu(request.function, ssuID)
    back = subscription_edit_get_back(return_url)

    return dict(content=form,
                back=back,
                save=submit,
                menu=menu)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'school_subscriptions_price'))
def subscriptions_prices():
    """
        Shows list of prices for a subscription
    """
    ssuID = request.vars['ssuID']
    response.title = T("Edit subscription")
    subscription = db.school_subscriptions(ssuID)
    response.subtitle = subscription.Name
    response.view = 'general/tabs_menu.html'

    return_url = URL('subscriptions')

    db.school_subscriptions_price.id.readable=False

    query = (db.school_subscriptions_price.school_subscriptions_id == ssuID)
    fields = [
        db.school_subscriptions_price.Startdate,
        db.school_subscriptions_price.Enddate,
        db.school_subscriptions_price.Price,
        db.school_subscriptions_price.tax_rates_id,
        db.school_subscriptions_price.GLAccount
    ]
    links = [ lambda row: os_gui.get_button('edit',
                                     URL('subscription_price_edit',
                                         vars={'ssuID':ssuID,
                                               'sspID':row.id}),
                                     T("Edit this price for this subscription"))]
    grid = SQLFORM.grid(query, fields=fields, links=links,
        create=False,
        editable=False,
        details=False,
        searchable=False,
        csv=False,
        #orderby = db.school_subscriptions_price.Startdate,
        field_id=db.school_subscriptions_price.id,
        ui = grid_ui)
    grid.element('.web2py_counter', replace=None) # remove the counter
    grid.elements('span[title=Delete]', replace=None) # remove text from delete button

    alert_msg = T("Please make sure the new price starts on the first day of a month and the previous price ends on the last day of the month before. ")
    alert_msg += T("Otherwise you might see unexpected results in the revenue stats.")
    alert_icon = SPAN(_class='glyphicon glyphicon-info-sign')
    alert = os_gui.get_alert('default', SPAN(alert_icon, ' ', alert_msg))

    add = os_gui.get_button('add',
                            URL('subscription_price_add',
                                vars={'ssuID':ssuID}))

    menu = subscriptions_get_submenu(request.function, ssuID)
    back = subscription_edit_get_back(return_url)

    content = DIV(alert, grid)

    return_url = URL('subscriptions')

    return dict(content=content,
                back=back,
                add=add,
                menu=menu)


@auth.requires_login()
def subscription_price_add():
    """
        Add a new price for a subscription
    """
    ssuID = request.vars['ssuID']
    response.title = T("New subscription price")
    subscription = db.school_subscriptions(ssuID)
    response.subtitle = subscription.Name
    response.view = 'general/only_content.html'

    return_url = subscription_price_get_return_url(ssuID)

    db.school_subscriptions_price.school_subscriptions_id.default = ssuID

    crud.messages.submit_button = T("Save")
    crud.messages.record_created = T("Saved price")
    crud.settings.formstyle = "bootstrap3_stacked"
    crud.settings.create_next = return_url
    crud.settings.create_onaccept = [cache_clear_school_subscriptions]
    form = crud.create(db.school_subscriptions_price)

    form_id = "MainForm"
    form_element = form.element('form')
    form['_id'] = form_id

    elements = form.elements('input, select, textarea')
    for element in elements:
        element['_form'] = form_id

    submit = form.element('input[type=submit]')

    back = os_gui.get_button('back', return_url)

    return dict(content=form, back=back, save=submit)


@auth.requires_login()
def subscription_price_edit():
    """
        Edit price for a subscription
    """
    ssuID = request.vars['ssuID']
    sspID = request.vars['sspID']
    response.title = T("Edit subscription price")
    subscription = db.school_subscriptions(ssuID)
    response.subtitle = subscription.Name
    response.view = 'general/only_content.html'

    return_url = subscription_price_get_return_url(ssuID)

    crud.messages.submit_button = T("Save")
    crud.messages.record_updated = T("Saved price")
    crud.settings.formstyle = "bootstrap3_stacked"
    crud.settings.update_next = return_url
    crud.settings.update_deletable = False
    crud.settings.update_onaccept = [cache_clear_school_subscriptions]
    form = crud.update(db.school_subscriptions_price, sspID)

    form_id = "MainForm"
    form_element = form.element('form')
    form['_id'] = form_id

    elements = form.elements('input, select, textarea')
    for element in elements:
        element['_form'] = form_id

    submit = form.element('input[type=submit]')

    back = os_gui.get_button('back', return_url)

    return dict(content=form, back=back, save=submit)


def subscription_edit_get_back(return_url):
    """
        Returns back button for subscription edit pages
    """
    return os_gui.get_button('back', return_url)


def subscription_price_get_return_url(ssuID):
    """
        Returns returl url for subscriptions
    """
    return URL('subscriptions_prices', vars={'ssuID':ssuID})


def subscriptions_get_submenu(page, ssuID):
    """
        Returns submenu for subscriptions
    """
    vars = {'ssuID':ssuID}
    pages = [ ['subscription_edit',
               T('Edit'),
               URL('subscription_edit', vars=vars)],
              ['subscriptions_prices',
               T('Prices'),
               URL('subscriptions_prices', vars=vars) ] ]

    return get_submenu(pages, page, horizontal=True, htype='tabs')


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'school_subscriptions_groups'))
def subscriptions_groups():
    """
        This function shows a page to list subscriptions.
    """
    response.title = T("School")
    response.subtitle = T("Subscriptions")
    response.view = 'general/tabs_menu.html'


    header = THEAD(TR(TH(T('Name')),
                      TH(T('Description'))))
    table = TABLE(header, _class='table table-striped table-hover')

    query = db.school_subscriptions_groups
    rows = db(query).select(db.school_subscriptions_groups.ALL)

    for i, row in enumerate(rows):
        tr = TR(TD(row.Name),
                TD(row.Description),
                TD(subscriptions_groups_get_link_subscriptions(row)),
                TD(subscriptions_groups_get_link_delete(row),
                   subscriptions_groups_get_link_edit(row)))

        table.append(tr)

    add_url = URL('subscriptions_group_add')
    add = os_gui.get_button('add', add_url, T("Add a new subscription group"), _class='pull-right')
    archive_buttons = os_gui.get_archived_radio_buttons(
        session.school_subscriptions_show)

    back = add
    menu = subscriptions_get_menu(request.function)

    return dict(back=back,
                menu=menu,
                content=table)


def subscriptions_groups_get_link_subscriptions(row):
    """
        Return list of subscriptions in this group as list of labels
    """
    ssgID = row.id

    left = [ db.school_subscriptions.on(db.school_subscriptions_groups_subscriptions.school_subscriptions_id ==
                                        db.school_subscriptions.id) ]
    query = (db.school_subscriptions_groups_subscriptions.school_subscriptions_groups_id == ssgID)
    rows = db(query).select(db.school_subscriptions.Name,
                            left=left,
                            orderby=db.school_subscriptions.Name)

    subscriptions = SPAN()
    for row in rows:
        subscriptions.append(os_gui.get_label('info', row.Name))
        subscriptions.append(' ')

    return subscriptions


def subscriptions_groups_get_link_delete(row):
    """
        Returns delete button for subscription group
    """
    delete_onclick = "return confirm('" + \
                     T('Are you sure you want to delete this group?') + "');"

    delete = ''
    delete_permission = auth.has_membership(group_id='Admins') or \
                        auth.has_permission('delete', 'school_subscriptions_groups')
    if delete_permission:
        delete = os_gui.get_button('delete_notext',
                                   URL('subscriptions_groups_delete', vars={'ssgID': row.id}),
                                   onclick=delete_onclick,
                                   _class='pull-right')

    return delete


def subscriptions_groups_get_link_edit(row):
    """
        Returns drop down link for index edit
    """
    vars = {'ssgID': row.id}

    links = []

    permission = (auth.has_membership(group_id='Admins') or
                  auth.has_permission('update', 'school_subscriptions_groups'))
    if permission:
        edit = A((os_gui.get_fa_icon('fa-pencil'), T('Edit group')),
                 _href=URL('subscriptions_group_edit', vars=vars))
        links.append(edit)

    permission = (auth.has_membership(group_id='Admins') or
                  auth.has_permission('read', 'school_subscriptions_groups_subscriptions'))
    if permission:
        edit = A((os_gui.get_fa_icon('fa-pencil'), T('Edit subscriptions in group')),
                 _href=URL('subscriptions_group_subscriptions', vars=vars))
        links.append(edit)

    menu = os_gui.get_dropdown_menu(
        links=links,
        btn_text='',
        btn_size='btn-sm',
        btn_icon='pencil',
        menu_class='btn-group pull-right')

    return menu


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('delete', 'school_subscriptions_groups'))
def subscriptions_groups_delete():
    """
        Delete a workshop
    """
    ssgID = request.vars['ssgID']

    query = (db.school_subscriptions_groups.id == ssgID)
    db(query).delete()

    session.flash = T('Subscription group deleted')

    redirect(URL('subscriptions_groups'))


@auth.requires_login()
def subscriptions_group_add():
    """
        This function shows an add page for a subscription
    """
    response.title = T("School")
    response.subtitle = T('Subscriptions')
    response.view = 'general/tabs_menu.html'

    db.school_subscriptions.Archived.readable=False
    db.school_subscriptions.Archived.writable=False

    return_url = URL('subscriptions_groups')

    crud.messages.submit_button = T("Save")
    crud.messages.record_created = T("Added subscription group")
    crud.settings.create_next = return_url
    crud.settings.formstyle = 'bootstrap3_stacked'
    #crud.settings.create_onaccept = [cache_clear_school_subscriptions]
    form = crud.create(db.school_subscriptions_groups)

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']

    back = os_gui.get_button('back', return_url)
    menu = subscriptions_get_menu('subscriptions_groups')

    title = H4(T('New subscription group'))

    return dict(content=DIV(title, BR(), form), menu=menu, back=back, save=submit)


@auth.requires_login()
def subscriptions_group_edit():
    """
        This function shows an edit page for a subscription
        request.vars['ssuID'] is expected to be the subscriptionID (ssuID)
    """
    ssgID = request.vars['ssgID']
    response.title = T("School")
    response.subtitle = T('Subscriptions')
    response.view = 'general/tabs_menu.html'

    db.school_subscriptions.Archived.readable=False
    db.school_subscriptions.Archived.writable=False

    return_url = URL('subscriptions_groups')

    crud.messages.submit_button = T("Save")
    crud.messages.record_updated = T("Saved")
    crud.settings.update_next = return_url
    crud.settings.formstyle = 'bootstrap3_stacked'
    #crud.settings.create_onaccept = [cache_clear_school_subscriptions]
    form = crud.update(db.school_subscriptions_groups, ssgID)

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']

    back = os_gui.get_button('back', return_url)
    menu = subscriptions_get_menu('subscriptions_groups')

    title = H4(T('Edit subscription group'))

    return dict(content=DIV(title, BR(), form), menu=menu, back=back, save=submit)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'school_subscriptions_groups_subscriptions'))
def subscriptions_group_subscriptions():
    """
        Page to list subscriptions for a group
    """
    ssgID = request.vars['ssgID']
    response.title = T("School")
    response.subtitle = T("Subscriptions")
    response.view = 'general/tabs_menu.html'

    db.school_subscriptions_groups_subscriptions.id.readable = False

    fields = [ db.school_subscriptions_groups_subscriptions.id,
               db.school_subscriptions.Name ]

    maxtextlengths = {'school_subscriptions.Name' : 50}

    delete_permission = auth.has_membership(group_id='Admins') or \
                        auth.has_permission('delete', 'school_subscriptions_groups_subscriptions')

    query = (db.school_subscriptions_groups_subscriptions.school_subscriptions_groups_id == ssgID)
    grid = SQLFORM.grid(query, fields=fields,
        maxtextlengths=maxtextlengths,
        create=False,
        editable=False,
        deletable=delete_permission,
        details=False,
        searchable=False,
        csv=False,
        left = [ db.school_subscriptions.on(db.school_subscriptions_groups_subscriptions.school_subscriptions_id ==
                                            db.school_subscriptions.id) ],
        field_id = db.school_subscriptions_groups_subscriptions.id,
        orderby = db.school_subscriptions.Name,
        ui = grid_ui)
    grid.element('.web2py_counter', replace=None) # remove the counter
    grid.elements('span[title=Delete]', replace=None) # remove text from delete button

    add_url = URL('subscriptions_group_subscription_add', vars={'ssgID':ssgID})
    add = os_gui.get_button('add', add_url, T("Add a new subscription to this group"), _class='pull-right')

    back = os_gui.get_button('back', URL('subscriptions_groups'))

    back = DIV(back, add)
    menu = subscriptions_get_menu('subscriptions_groups')

    ssg = db.school_subscriptions_groups(ssgID)
    title = DIV(H4(T('Subscriptions in group'), ': ', ssg.Name))

    content = DIV(title, grid)

    return dict(back=back,
                menu=menu,
                content=content)


@auth.requires_login()
def subscriptions_group_subscription_add():
    """
        This function shows an add page for a subscription
    """
    ssgID = request.vars['ssgID']
    response.title = T("School")
    response.subtitle = T('Subscriptions')
    response.view = 'general/tabs_menu.html'

    ids = subscriptions_group_subscription_add_get_already_added(ssgID)

    db.school_subscriptions_groups_subscriptions.school_subscriptions_groups_id.default = ssgID

    query = (db.school_subscriptions.Archived == False)  & \
            (~db.school_subscriptions.id.belongs(ids))


    db.school_subscriptions_groups_subscriptions.school_subscriptions_id.requires = IS_IN_DB(
        db(query), 'school_subscriptions.id', '%(Name)s'
    )

    return_url = URL('subscriptions_group_subscriptions', vars={'ssgID':ssgID})

    crud.messages.submit_button = T("Add")
    crud.messages.record_created = T("Added subscription to group")
    crud.settings.create_next = return_url
    crud.settings.formstyle = 'bootstrap3_stacked'
    form = crud.create(db.school_subscriptions_groups_subscriptions)

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']

    back = os_gui.get_button('back', return_url)
    menu = subscriptions_get_menu('subscriptions_groups')

    ssg = db.school_subscriptions_groups(ssgID)

    title = H4(T('Add subscription to group'), ' ', ssg.Name)

    return dict(content=DIV(title, BR(), form), menu=menu, back=back, save=submit)


def subscriptions_group_subscription_add_get_already_added(ssgID):
    """
        :param ssgID: db.school_subscriptions_groups.id
        :return: list of ids in this group
    """
    query = (db.school_subscriptions_groups_subscriptions.school_subscriptions_groups_id == ssgID)
    rows = db(query).select(db.school_subscriptions_groups_subscriptions.school_subscriptions_id)

    ids = []
    for row in rows:
        ids.append(row.school_subscriptions_id)

    return ids


def classcards_get_menu(page=None):
    pages = []

    if auth.has_membership(group_id='Admins') or \
       auth.has_permission('read', 'school_classcards'):
        pages.append(['classcards',
                      T("Class cards"),
                      URL("school_properties","classcards")])
    if auth.has_membership(group_id='Admins') or \
       auth.has_permission('read', 'school_classcards_groups'):
        pages.append(['classcards_groups',
                      T("Groups"),
                      URL("school_properties","classcards_groups",)])

    return os_gui.get_submenu(pages, page, _id='os-customers_edit_menu', horizontal=True, htype='tabs')


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'school_classcards'))
def classcards():
    """
        This function shows a page to list class cards.
    """
    response.title = T("School")
    response.subtitle = T("Class cards")
    response.view = 'general/tabs_menu.html'

    show = 'current'
    query = (db.school_classcards.Archived == False)

    if 'show_archive' in request.vars:
        show = request.vars['show_archive']
        session.school_classcards_show = show
        if show == 'current':
            query = (db.school_classcards.Archived == False)
        elif show == 'archive':
            query = (db.school_classcards.Archived == True)
    elif session.school_classcards_show == 'archive':
            query = (db.school_classcards.Archived == True)
    else:
        session.school_classcards_show = show

    db.school_classcards.id.readable=False
    db.school_classcards.Description.readable=False

    fields = [db.school_classcards.Name,
              db.school_classcards.sys_organizations_id,
              db.school_classcards.Description,
              db.school_classcards.Price,
              db.school_classcards.GLAccount,
              db.school_classcards.Validity,
              db.school_classcards.ValidityUnit,
              db.school_classcards.Classes,
              db.school_classcards.Unlimited,
              db.school_classcards.Trialcard,
              db.school_classcards.PublicCard ]

    links = [ lambda row: os_gui.get_button('edit',
                                     URL('classcard_edit', args=[row.id]),
                                     T("Edit this class card")),
              classcards_get_link_archive ]

    maxtextlengths = {'school_classcards.Name' : 40,
                      'school_classcards.Description' : 40}

    grid = SQLFORM.grid(query, fields=fields, links=links,
        maxtextlengths=maxtextlengths,
        create=False,
        editable=False,
        deletable=False,
        details=False,
        searchable=False,
        csv=False,
        orderby = db.school_classcards.Name,
        ui = grid_ui)
    grid.element('.web2py_counter', replace=None) # remove the counter
    grid.elements('span[title=Delete]', replace=None) # remove text from delete button

    add_url = URL('classcard_add')
    add = os_gui.get_button('add', add_url, T("Add a new class card"), _class='pull-right')
    archive_buttons = os_gui.get_archived_radio_buttons(
        session.school_classcards_show)

    back = DIV(add, archive_buttons)

    content = grid

    return dict(back=back,
                menu = classcards_get_menu(request.function),
                content=content)


def classcards_get_link_archive(row):
    """
        Called from the index function. Changes title of archive button
        depending on whether a class card is archived or not
    """
    row = db.school_classcards(row.id)

    if row.Archived:
        tt = T("Move to current")
    else:
        tt = T("Archive")

    return os_gui.get_button('archive',
                             URL('classcards_archive', vars={'clcID':row.id}),
                             tooltip=tt)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('update', 'school_classcards'))
def classcards_archive():
    """
        This function archives a class card
        request.vars[clcID] is expected to be the school_classcards ID
    """
    clcID = request.vars['clcID']
    if not clcID:
        session.flash = T('Unable to (un)archive class cards')
    else:
        row = db.school_classcards(clcID)

        if row.Archived:
            session.flash = T('Moved to current')
        else:
            session.flash = T('Archived')

        row.Archived = not row.Archived
        row.update_record()

        cache_clear_school_classcards()

    redirect(URL('classcards'))


@auth.requires_login()
def classcard_add():
    """
        This function shows an add page for a class cards
    """
    response.title = T("New class card")
    response.subtitle = T('')
    response.view = 'general/only_content.html'

    db.school_classcards.Archived.readable=False
    db.school_classcards.Archived.writable=False

    return_url = URL('classcards')

    crud.messages.submit_button = T("Save")
    crud.messages.record_created = T("Saved")
    crud.settings.formstyle = 'bootstrap3_stacked'
    crud.settings.create_next = return_url
    crud.settings.create_onaccept = [cache_clear_school_classcards]
    form = crud.create(db.school_classcards)

    form_id = "MainForm"
    form_element = form.element('form')
    form['_id'] = form_id

    elements = form.elements('input, select, textarea')
    for element in elements:
        element['_form'] = form_id

    submit = form.element('input[type=submit]')

    # classes = form.element('#school_classcards_Classes')
    # classes['_placeholder'] = T("Unlimited")

    back = os_gui.get_button('back', return_url)

    return dict(content=form, back=back, save=submit)


@auth.requires_login()
def classcard_edit():
    """
        This function shows an edit page for a class cards
        request.args[0] is expected to be the classcardsID (clcID)
    """
    clcID = request.args[0]
    response.title = T("Edit class card")
    response.subtitle = T('')
    response.view = 'general/only_content.html'

    return_url = URL('classcards')

    crud.messages.submit_button = T("Save")
    crud.messages.record_updated = T("Saved")
    crud.settings.formstyle = 'bootstrap3_stacked'
    crud.settings.update_next = return_url
    crud.settings.update_deletable = False
    crud.settings.update_onaccept = [cache_clear_school_classcards]
    form = crud.update(db.school_classcards, clcID)

    form_id = "MainForm"
    form_element = form.element('form')
    form['_id'] = form_id

    elements = form.elements('input, select, textarea')
    for element in elements:
        element['_form'] = form_id

    submit = form.element('input[type=submit]')

    # classes = form.element('#school_classcards_Classes')
    # classes['_placeholder'] = T("Unlimited")

    back = os_gui.get_button('back', return_url)

    return dict(content=form, back=back, save=submit)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'school_classcards_groups'))
def classcards_groups():
    """
        This function shows a page to list subscriptions.
    """
    response.title = T("School")
    response.subtitle = T("Class cards")
    response.view = 'general/tabs_menu.html'


    header = THEAD(TR(TH(T('Name')),
                      TH(T('Description'))))
    table = TABLE(header, _class='table table-striped table-hover')

    query = db.school_classcards_groups
    rows = db(query).select(db.school_classcards_groups.ALL)

    for i, row in enumerate(rows):
        tr = TR(TD(row.Name),
                TD(row.Description),
                TD(classcards_groups_get_link_classcards(row)),
                TD(classcards_groups_get_link_delete(row),
                   classcards_groups_get_link_edit(row)))

        table.append(tr)

    add_url = URL('classcards_group_add')
    add = os_gui.get_button('add', add_url, T("Add a new class card group"), _class='pull-right')

    back = add
    menu = classcards_get_menu(request.function)

    return dict(back=back,
                menu=menu,
                content=table)


def classcards_groups_get_link_classcards(row):
    """
        Return list of subscriptions in this group as list of labels
    """
    scgID = row.id

    left = [ db.school_classcards.on(db.school_classcards_groups_classcards.school_classcards_id ==
                                        db.school_classcards.id) ]
    query = (db.school_classcards_groups_classcards.school_classcards_groups_id == scgID)
    rows = db(query).select(db.school_classcards.Name,
                            left=left,
                            orderby=db.school_classcards.Name)

    classcards = SPAN()
    for row in rows:
        classcards.append(os_gui.get_label('info', row.Name))
        classcards.append(' ')

    return classcards


def classcards_groups_get_link_delete(row):
    """
        Returns delete button for subscription group
    """
    delete_onclick = "return confirm('" + \
                     T('Are you sure you want to delete this group?') + "');"

    delete = ''
    delete_permission = auth.has_membership(group_id='Admins') or \
                        auth.has_permission('delete', 'school_classcards_groups')
    if delete_permission:
        delete = os_gui.get_button('delete_notext',
                                   URL('classcards_groups_delete', vars={'scgID': row.id}),
                                   onclick=delete_onclick,
                                   _class='pull-right')

    return delete


def classcards_groups_get_link_edit(row):
    """
        Returns drop down link for index edit
    """
    vars = {'scgID': row.id}

    links = []

    permission = (auth.has_membership(group_id='Admins') or
                  auth.has_permission('update', 'school_classcards_groups'))
    if permission:
        edit = A((os_gui.get_fa_icon('fa-pencil'), T('Edit group')),
                 _href=URL('classcards_group_edit', vars=vars))
        links.append(edit)

    permission = (auth.has_membership(group_id='Admins') or
                  auth.has_permission('read', 'school_classcards_groups_classcards'))
    if permission:
        edit = A((os_gui.get_fa_icon('fa-pencil'), T('Edit class cards in group')),
                 _href=URL('classcards_group_classcards', vars=vars))
        links.append(edit)

    menu = os_gui.get_dropdown_menu(
        links=links,
        btn_text='',
        btn_size='btn-sm',
        btn_icon='pencil',
        menu_class='btn-group pull-right')

    return menu


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('delete', 'school_classcards_groups'))
def classcards_groups_delete():
    """
        Delete a workshop
    """
    scgID = request.vars['scgID']

    query = (db.school_classcards_groups.id == scgID)
    db(query).delete()

    session.flash = T('Group deleted')

    redirect(URL('classcards_groups'))


@auth.requires_login()
def classcards_group_add():
    """
        This function shows an add page for a subscription
    """
    response.title = T("School")
    response.subtitle = T('Class cards')
    response.view = 'general/tabs_menu.html'

    db.school_classcards.Archived.readable=False
    db.school_classcards.Archived.writable=False

    return_url = URL('classcards_groups')

    crud.messages.submit_button = T("Save")
    crud.messages.record_created = T("Added class card group")
    crud.settings.create_next = return_url
    crud.settings.formstyle = 'bootstrap3_stacked'
    #crud.settings.create_onaccept = [cache_clear_school_classcards]
    form = crud.create(db.school_classcards_groups)

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']

    back = os_gui.get_button('back', return_url)
    menu = classcards_get_menu('classcards_groups')

    title = H4(T('New class card group'))

    return dict(content=DIV(title, BR(), form), menu=menu, back=back, save=submit)


@auth.requires_login()
def classcards_group_edit():
    """
        This function shows an edit page for a classcard
        request.vars['ssuID'] is expected to be the classcardID (ssuID)
    """
    scgID = request.vars['scgID']
    response.title = T("School")
    response.subtitle = T('Class cards')
    response.view = 'general/tabs_menu.html'

    db.school_classcards.Archived.readable=False
    db.school_classcards.Archived.writable=False

    return_url = URL('classcards_groups')

    crud.messages.submit_button = T("Save")
    crud.messages.record_updated = T("Saved")
    crud.settings.update_next = return_url
    crud.settings.formstyle = 'bootstrap3_stacked'
    #crud.settings.create_onaccept = [cache_clear_school_classcards]
    form = crud.update(db.school_classcards_groups, scgID)

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']

    back = os_gui.get_button('back', return_url)
    menu = classcards_get_menu('classcards_groups')

    title = H4(T('Edit class card group'))

    return dict(content=DIV(title, BR(), form), menu=menu, back=back, save=submit)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'school_classcards_groups_classcards'))
def classcards_group_classcards():
    """
        Page to list classcards for a group
    """
    scgID = request.vars['scgID']
    response.title = T("School")
    response.subtitle = T("Class cards")
    response.view = 'general/tabs_menu.html'

    db.school_classcards_groups_classcards.id.readable = False

    fields = [ db.school_classcards_groups_classcards.id,
               db.school_classcards.Name ]

    maxtextlengths = {'school_classcards.Name' : 50}

    delete_permission = auth.has_membership(group_id='Admins') or \
                        auth.has_permission('delete', 'school_classcards_groups_classcards')

    query = (db.school_classcards_groups_classcards.school_classcards_groups_id == scgID)
    grid = SQLFORM.grid(query, fields=fields,
        maxtextlengths=maxtextlengths,
        create=False,
        editable=False,
        deletable=delete_permission,
        details=False,
        searchable=False,
        csv=False,
        left = [ db.school_classcards.on(db.school_classcards_groups_classcards.school_classcards_id ==
                                            db.school_classcards.id) ],
        field_id = db.school_classcards_groups_classcards.id,
        orderby = db.school_classcards.Name,
        ui = grid_ui)
    grid.element('.web2py_counter', replace=None) # remove the counter
    grid.elements('span[title=Delete]', replace=None) # remove text from delete button

    add_url = URL('classcards_group_classcard_add', vars={'scgID':scgID})
    add = os_gui.get_button('add', add_url, T("Add a new classcard to this group"), _class='pull-right')

    back = os_gui.get_button('back', URL('classcards_groups'))

    back = DIV(back, add)
    menu = classcards_get_menu('classcards_groups')

    scg = db.school_classcards_groups(scgID)
    title = DIV(H4(T('classcards in group'), ': ', scg.Name))

    content = DIV(title, grid)

    return dict(back=back,
                menu=menu,
                content=content)


@auth.requires_login()
def classcards_group_classcard_add():
    """
        This function shows an add page for a classcard
    """
    scgID = request.vars['scgID']
    response.title = T("School")
    response.subtitle = T('Class cards')
    response.view = 'general/tabs_menu.html'

    ids = classcards_group_classcard_add_get_already_added(scgID)

    db.school_classcards_groups_classcards.school_classcards_groups_id.default = scgID

    query = (db.school_classcards.Archived == False)  & \
            (~db.school_classcards.id.belongs(ids))


    db.school_classcards_groups_classcards.school_classcards_id.requires = IS_IN_DB(
        db(query), 'school_classcards.id', '%(Name)s'
    )

    return_url = URL('classcards_group_classcards', vars={'scgID':scgID})

    crud.messages.submit_button = T("Add")
    crud.messages.record_created = T("Added class card to group")
    crud.settings.create_next = return_url
    crud.settings.formstyle = 'bootstrap3_stacked'
    form = crud.create(db.school_classcards_groups_classcards)

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']

    back = os_gui.get_button('back', return_url)
    menu = classcards_get_menu('classcards_groups')

    ssg = db.school_classcards_groups(scgID)

    title = H4(T('Add class card to group'), ' ', ssg.Name)

    return dict(content=DIV(title, BR(), form), menu=menu, back=back, save=submit)


def classcards_group_classcard_add_get_already_added(ssgID):
    """
        :param ssgID: db.school_classcards_groups.id
        :return: list of ids in this group
    """
    query = (db.school_classcards_groups_classcards.school_classcards_groups_id == ssgID)
    rows = db(query).select(db.school_classcards_groups_classcards.school_classcards_id)

    ids = []
    for row in rows:
        ids.append(row.school_classcards_id)

    return ids


@auth.requires(auth.has_membership(group_id='Admins') or \
                auth.has_permission('read', 'schoolproperties_keys'))
def list_keys():
    response.title = T("School")
    response.subtitle = T("Keys")
    response.view = 'general/only_content.html'

    session.customers_back = 'keys'

    search = ''
    query = (db.auth_user.keynr != None) & (db.auth_user.keynr != '') # generic show all active customers query
    if 'search' in request.vars: # check whether a search filter is in use
        if request.vars['search'] != '':
            search = request.vars['search']
            search_name = '%' + request.vars['search'] + '%'
            query &= ((db.auth_user.display_name.like(search_name)) |
                      (db.auth_user.keynr.like(search_name)))

    form = SQLFORM.factory(
        Field('search', default=search, label=T("")),
        submit_button='Search',
        )
    form.element('input[name=search]')['_placeholder']='Search...'
    form.element('input[name=search]')['_class']='search'

    show_all = A(T('Clear'),
                 _href=URL(request.function),
                 _class='btn btn-default')

    form_display = DIV(form.custom.begin,
                       DIV(form.custom.widget.search,
                           _class='col-md-10 no-padding'),
                       DIV(DIV(form.custom.submit,
                               show_all,
                               _class="pull-right"),
                           _class='col-md-2 no-padding'),
                       form.custom.end,
                       _class='form_inline')

    if 'edit' in request.args:
        customerID = request.args[2]
        redirect(URL('customers', 'edit', args=[customerID]))

    fields = [ db.auth_user.keynr,
               db.auth_user.display_name ]

    grid = SQLFORM.grid(query,
        fields=fields,
        create=False,
        details=False,
        deletable=False,
        searchable=False,
        csv=False,
        orderby = db.auth_user.keynr,
        ui=grid_ui)
    grid.element('.web2py_counter', replace=None) # remove the counter

    return dict(content=DIV(form_display, grid), back='')


@auth.requires(auth.has_membership(group_id='Admins') or \
                auth.has_permission('read', 'school_languages'))
def languages():
    response.title = T("School")
    response.subtitle = T("Languages")
    response.view = 'general/only_content.html'

    show = 'current'
    query = (db.school_languages.Archived == False)

    if 'show_archive' in request.vars:
        show = request.vars['show_archive']
        session.school_languages_show = show
        if show == 'current':
            query = (db.school_languages.Archived == False)
        elif show == 'archive':
            query = (db.school_languages.Archived == True)
    elif session.school_languages_show == 'archive':
            query = (db.school_languages.Archived == True)
    else:
        session.school_languages_show = show

    db.school_languages.id.readable=False
    fields = [db.school_languages.Name]
    links = [ lambda row: os_gui.get_button('edit',
                                     URL('language_edit', args=[row.id]),
                                     T("Edit this language")),
              languages_get_link_archive ]
    grid = SQLFORM.grid(query, fields=fields, links=links,
        create=False,
        editable=False,
        deletable=False,
        details=False,
        searchable=False,
        csv=False,
        orderby = db.school_languages.Name,
        ui = grid_ui)
    grid.element('.web2py_counter', replace=None) # remove the counter
    grid.elements('span[title=Delete]', replace=None) # remove text from delete button

    add_url = URL('language_add')
    add = os_gui.get_button('add', add_url, T("Add a new language"), _class='pull-right')

    archive_buttons = os_gui.get_archived_radio_buttons(
        session.school_languages_show)

    back = DIV(add, archive_buttons)

    return dict(content=grid, back=back)


def languages_get_link_archive(row):
    """
        Called from the index function. Changes title of archive button
        depending on whether a language is archived or not
    """
    row = db.school_languages(row.id)

    if row.Archived:
        tt = T("Move to current")
    else:
        tt = T("Archive")

    return os_gui.get_button('archive',
                             URL('languages_archive', vars={'laID':row.id}),
                             tooltip=tt)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('update', 'school_languages'))
def languages_archive():
    """
        This function archives a subscription
        request.vars[laID] is expected to be the school_languages ID
    """
    laID = request.vars['laID']
    if not laID:
        session.flash = T('Unable to (un)archive language')
    else:
        row = db.school_languages(laID)

        if row.Archived:
            session.flash = T('Moved to current')
        else:
            session.flash = T('Archived')

        row.Archived = not row.Archived
        row.update_record()

    redirect(URL('languages'))


@auth.requires_login()
def language_add():
    """
        This function shows an add page for a language
    """
    response.title = T("New language")
    response.subtitle = T('')
    response.view = 'general/only_content.html'

    return_url = URL('languages')

    crud.messages.submit_button = T("Save")
    crud.messages.record_created = T("Added language")
    crud.settings.create_next = return_url
    crud.settings.formstyle = 'bootstrap3_stacked'
    form = crud.create(db.school_languages)

    form_id = "MainForm"
    form_element = form.element('form')
    form['_id'] = form_id

    elements = form.elements('input, select, textarea')
    for element in elements:
        element['_form'] = form_id

    submit = form.element('input[type=submit]')

    back = os_gui.get_button('back', return_url)

    return dict(content=form, back=back, save=submit)


@auth.requires_login()
def language_edit():
    """
        This function shows an edit page for a language
        request.args[0] is expected to be the language id (lID)
    """
    lID = request.args[0]
    response.title = T("Edit language")
    response.subtitle = T('')
    response.view = 'general/only_content.html'

    return_url = URL('languages')

    crud.messages.submit_button = T("Save")
    crud.messages.record_updated = T("Updated languages")
    crud.settings.update_next = return_url
    crud.settings.update_deletable = False
    crud.settings.formstyle = 'bootstrap3_stacked'
    form = crud.update(db.school_languages, lID)

    form_id = "MainForm"
    form_element = form.element('form')
    form['_id'] = form_id

    elements = form.elements('input, select, textarea')
    for element in elements:
        element['_form'] = form_id

    submit = form.element('input[type=submit]')

    back = os_gui.get_button('back', return_url)

    return dict(content=form, back=back, save=submit)

@auth.requires(auth.has_membership(group_id='Admins') or \
                auth.has_permission('read', 'school_shifts'))
def shifts():
    response.title = T("School")
    response.subtitle = T("Shifts")
    response.view = 'general/only_content.html'

    show = 'current'
    query = (db.school_shifts.Archived == False)

    if 'show_archive' in request.vars:
        show = request.vars['show_archive']
        session.school_shifts_show = show
        if show == 'current':
            query = (db.school_shifts.Archived == False)
        elif show == 'archive':
            query = (db.school_shifts.Archived == True)
    elif session.school_shifts_show == 'archive':
            query = (db.school_shifts.Archived == True)
    else:
        session.school_shifts_show = show

    db.school_shifts.id.readable=False
    maxtextlengths = {'school_shifts.Name' : 60}
    fields = [db.school_shifts.Name]
    links = [ lambda row: os_gui.get_button('edit',
                                URL('shifts_edit', vars={'ssID':row.id}),
                                T("Edit the name this shift")),
              shifts_get_link_archive ]
    grid = SQLFORM.grid(query, fields=fields, links=links,
        create=False,
        editable=False,
        deletable=False,
        details=False,
        searchable=False,
        csv=False,
        maxtextlengths=maxtextlengths,
        orderby=db.school_shifts.Name,
        ui = grid_ui)
    grid.element('.web2py_counter', replace=None) # remove the counter
    grid.elements('span[title=Delete]', replace=None) # remove text from delete button

    add_url = URL('shifts_add')
    add = os_gui.get_button('add', add_url, T("Add a new type of shifts"), _class='pull-right')

    archive_buttons = os_gui.get_archived_radio_buttons(
        session.school_shifts_show)

    back = DIV(add, archive_buttons)

    return dict(content=grid, back=back)


def shifts_get_link_archive(row):
    """
        Called from the index function. Changes title of archive button
        depending on whether a level is archived or not
    """
    row = db.school_shifts(row.id)

    if row.Archived:
        tt = T("Move to current")
    else:
        tt = T("Archive")

    return os_gui.get_button('archive',
                             URL('shifts_archive', vars={'ssID':row.id}),
                             tooltip=tt)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('update', 'school_shifts'))
def shifts_archive():
    """
        This function archives a shift
        request.vars[sdID] is expected to be the school_shifts ID
    """
    ssID = request.vars['ssID']
    if not ssID:
        session.flash = T('Unable to (un)archive shifts')
    else:
        row = db.school_shifts(ssID)
        if row.Archived:
            session.flash = T('Moved to current')
        else:
            session.flash = T('Archived')

        row.Archived = not row.Archived
        row.update_record()

    redirect(URL('shifts'))


@auth.requires_login()
def shifts_add():
    """
        This function shows an add page for shifts
    """
    response.title = T("New shift")
    response.subtitle = T('')
    response.view = 'general/only_content.html'

    return_url = URL('shifts')

    crud.messages.submit_button = T("Save")
    crud.messages.record_created = T("Added shift")
    crud.settings.create_next = return_url
    crud.settings.formstyle = 'bootstrap3_stacked'
    form = crud.create(db.school_shifts)

    form_id = "MainForm"
    form_element = form.element('form')
    form['_id'] = form_id

    elements = form.elements('input, select, textarea')
    for element in elements:
        element['_form'] = form_id

    submit = form.element('input[type=submit]')

    back = os_gui.get_button('back', return_url)

    return dict(content=form, back=back, save=submit)


@auth.requires_login()
def shifts_edit():
    """
        This function shows an edit page for shifts
    """
    ssID = request.vars['ssID']
    response.title = T("Edit shift")
    response.subtitle = T('')
    response.view = 'general/only_content.html'

    return_url = URL('shifts')

    crud.messages.submit_button = T("Save")
    crud.messages.record_updated = T("Saved")
    crud.settings.update_next = return_url
    crud.settings.update_deletable = False
    crud.settings.formstyle = 'bootstrap3_stacked'
    form = crud.update(db.school_shifts, ssID)

    form_id = "MainForm"
    form_element = form.element('form')
    form['_id'] = form_id

    elements = form.elements('input, select, textarea')
    for element in elements:
        element['_form'] = form_id

    submit = form.element('input[type=submit]')


    back = os_gui.get_button('back', return_url)

    return dict(content=form, back=back, save=submit)


def account_get_tools_link_groups(var=None):
    """
        @return: link to settings/groups
    """
    return A(SPAN(os_gui.get_fa_icon('fa-users'), ' ', T('Groups')),
             _href=URL('settings', 'access_groups'),
             _title=T('Define groups and permission for employees'))


def employees_get_tools(var=None):
    """
        @return: tools dropdown for employees
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


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'employees'))
def employees():
    """
        This function shows a page which lists OpenStudio users
    """
    response.title = T("School")
    response.subtitle = T("Employees")
    response.view = 'general/only_content.html'

    session.customers_back = 'school_employees'
    session.customers_add_back = 'school_employees'
    session.settings_groups_back = 'school_employees'

    query = (db.auth_user.trashed == False)
    # hide admin user for all other users
    if auth.user.id > 1:
        query &= (db.auth_user.id > 1)
    # show only employees
    query &= (db.auth_user.employee == True)

    db.auth_user.id.readable = False


    if request.user_agent()['is_mobile']:
        db.auth_user.email.readable = False

    maxtextlengths = {'auth_user.email': 35}
    headers = {'auth_user.display_name': T('Employee'),
               'auth_user.thumbsmall': ''}

    delete_onclick = "return confirm('" + \
        T('Remove from employees list? - This person will still be a customer.') + "');"

    # set links for general
    links = [lambda row: os_gui.get_button('edit',
                                           URL('customers', 'edit',
                                               args=[row.id])),
             lambda row: os_gui.get_button(
                 'delete_notext',
                 URL('school_properties',
                     'employee_delete',
                     vars={'uID': row.id}),
                 onclick=delete_onclick)
             ]

    fields = [
        db.auth_user.trashed,
        db.auth_user.birthday,
        db.auth_user.thumbsmall,
        db.auth_user.display_name,
        db.auth_user.email,
        db.auth_user.enabled,
    ]

    links.append(dict(header=T('Group (Permissions)'), body=account_get_link_group))

    user_helpers = User_helpers()
    grid = SQLFORM.grid(query,
                        links=links,
                        fields=fields,
                        headers=headers,
                        user_signature=False,
                        create=False,
                        editable=False,
                        details=False,
                        deletable=False,
                        csv=False,
                        searchable=False,
                        maxtextlengths=maxtextlengths,
                        orderby=db.auth_user.display_name,
                        ui=grid_ui)
    grid.element('.web2py_counter', replace=None)  # remove the counter
    # remove text from delete button
    grid.elements('span[title=Delete]', replace=None)

    # modal to add employee
    customers = Customers()
    result = customers.get_add_modal(redirect_vars={'employee':True}, button_class='btn-sm pull-right')
    add = SPAN(result['button'], result['modal'])

    tools = employees_get_tools()
    back = DIV(add, tools)

    return dict(back=back,
                menu=school_get_menu(request.function),
                header_tools='',
                content=grid)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('delete', 'employees'))
def employee_delete():
    """
        This function archives a subscription
        request.vars[uID] is expected to be the auth_userID
    """
    uID = request.vars['uID']
    if not uID:
        session.flash = T('Unable to remove from employees list')
    else:
        row = db.auth_user(uID)
        row.employee = False
        row.update_record()

        session.flash = SPAN(
            T('Removed'), ' ',
            row.display_name, ' ',
            T('from employees list'))

    redirect(URL('employees'))


def account_get_link_group(row):
    """
        This function returns the group a user belongs to and shows it as a link
        to a page which allows users to change it.
    """
    no_group = A(os_gui.get_label('default', T('No group')),
                 _href=URL('account_group_add', args=[row.id]))

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
                                _href=URL("account_group_edit",
                                          args=[query_row.auth_membership.id]))
                else:  # no group added yet
                    ret_val = no_group
        else:  # no group added yet
            ret_val = no_group

    return ret_val


def account_get_user_group_form(selected=None):
    """
        This function returns the roles of the auth_group table as a list
        of radio buttons.
    """
    form = FORM()

    # show a no group option only when editing
    if not selected is None:
        form.append(DIV(LABEL(INPUT(_type="radio",
                                    _name="group_id",
                                    _value=0,
                                    value=0), " ",
                              T("No group")),
                        _class='radio'))

    query = ~(db.auth_group.role.contains('user'))
    rows = db(query).select(db.auth_group.ALL, orderby=db.auth_group.role)
    for row in rows:
        form.append(DIV(LABEL(INPUT(_type="radio",
                                    _name="group_id",
                                    _value=row.id,
                                    value=selected), " ", row.role),
                        _class='radio'))
    form.append(INPUT(_type="submit", _value=T("Save")))

    return form



@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('update', 'employees') or
               auth.has_permission('update', 'teachers'))
def account_group_add():
    """
        This function shows a page that allows setting of a group for a user
        request.args[0] is expected to be the user id
    """
    response.title = T("Assign group")
    user_id = request.args[0]
    row = db.auth_user(user_id)
    response.subtitle = row.display_name
    response.view = 'general/only_content.html'

    form = account_get_user_group_form()

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']

    submit = result['submit']

    return_url = account_change_get_redirect_url()

    if form.process().accepted:
        group_id = form.vars.group_id
        group_name = db.auth_group(group_id).role
        auth.add_membership(group_id, user_id)
        session.flash = T("Added") + " " + row.display_name + " " + \
                        T("to group") + ": " + group_name
        redirect(return_url)

    content = DIV(form, _class="os-user_group_form")
    back = os_gui.get_button("back", return_url)

    return dict(content=content, back=back, save=submit)


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('update', 'employees') or
               auth.has_permission('update', 'teachers'))
def account_group_edit():
    """
        This function shows a page that allows setting of a group for a user
        request.args[0] is expected to be the auth_membership id (am_id)
    """
    response.title = T("Assign group")
    am_id = request.args[0]
    am_row = db.auth_membership(am_id)
    user_id = am_row.user_id
    row = db.auth_user(user_id)
    response.subtitle = row.display_name
    response.view = 'general/only_content.html'

    form = account_get_user_group_form(am_row.group_id)

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']

    return_url = account_change_get_redirect_url()

    if form.process().accepted:
        db(db.auth_membership.id == am_id).delete()
        group_id = form.vars.group_id
        if group_id != '0':
            group_name = db.auth_group(group_id).role
            message =  T("Added") + " " + row.display_name + " " + \
                       T("to group") + ": " + group_name
            auth.add_membership(group_id, user_id)
        else:
            message = T("Removed") + " " + row.display_name + " " + \
                      T('from all groups with permissions')

        # Clear cache to regenerate all menus
        cache_clear_menu_backend()

        session.flash = message
        redirect(return_url)

    content = DIV(form, _class="os-user_group_form")
    back = os_gui.get_button("back", return_url)

    return dict(content=content, back=back, save=submit)


def account_change_get_redirect_url():
    """
        Redirect either to teachers or employees after:
        - archive
        - enable / disable
    """
    if session.customers_back == 'teachers':
        return URL('teachers', 'index')
    #elif session.customers_back == 'school_employees':
    else:
        return URL('employees')


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('update', 'auth_user'))
def account_change_status():
    """
        Changes status of an account from enabled to disabled or the
        other way around
    """
    auID = request.vars['auID']

    user = db.auth_user(auID)
    user.enabled = not user.enabled
    user.update_record()

    redirect(account_change_get_redirect_url())


def account_get_link_archive(row):
    """
        This function returns the archive link for a user
    """
    row = db.auth_user(row.id)

    if row.archived:
        tt = T("Move to current")
    else:
        tt = T("Archive")

    return os_gui.get_button('archive',
                             URL('account_archive',
                                 vars={'auID': row.id}),
                             tooltip=tt)


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('update', 'employees') or
               auth.has_permission('update', 'teachers'))
def account_archive():
    """
        This function archives a subscription
        request.vars[auID] is expected to be auth_user.id
    """
    auID = request.vars['auID']
    if not auID:
        session.flash = T('Unable to (un)archive account')
    else:
        row = db.auth_user(auID)

        if row.archived:
            session.flash = T('Moved to current')
        else:
            session.flash = T('Archived')

        row.archived = not row.archived
        row.update_record()

    redirect(account_change_get_redirect_url())


def school_get_menu(page):
    """
    @param page: current page
    @return: sidebar menu for school
    """
    pages = []

    if auth.has_membership(group_id='Admins') or \
       auth.has_permission('read', 'teachers'):
        pages.append(['teachers', T('Teachers'),
                      URL('teachers')])
    if auth.has_membership(group_id='Admins') or \
       auth.has_permission('read', 'employees'):
        pages.append(['employees', T('Employees'),
                      URL('employees')])

    return get_submenu(pages, page)
    # return get_submenu(pages, page, _id='os-customers_edit_menu')


@auth.requires(auth.has_membership(group_id='Admins') or \
                auth.has_permission('read', 'schoolproperties'))
def index():
    response.title = T("School")
    response.subtitle = T("")
    response.view = 'general/only_content.html'

    content = ''

    return dict(content=content)
