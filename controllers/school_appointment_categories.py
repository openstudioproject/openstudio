# coding=utf-8

@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'school_appointment_categories'))
def index():
    response.title = T("School")
    response.subtitle = T("Appointments")
    response.view = 'general/only_content.html'

    show = 'current'
    query = (db.school_appointment_categories.Archived == False)

    if 'show_archive' in request.vars:
        show = request.vars['show_archive']
        session.school_appointment_categories_show = show
        if show == 'current':
            query = (db.school_appointment_categories.Archived == False)
        elif show == 'archive':
            query = (db.school_appointment_categories.Archived == True)
    elif session.school_appointment_categories_show == 'archive':
            query = (db.school_appointment_categories.Archived == True)
    else:
        session.school_appointment_categories_show = show

    db.school_appointment_categories.id.readable=False
    fields = [db.school_appointment_categories.Name,
              db.school_appointment_categories.AllowAPI]
    links = [ 
        lambda row: os_gui.get_button('edit',
            URL('edit', vars={'sacID': row.id}),
            T("Edit this category")),
        index_get_link_archive
    ]
    
    grid = SQLFORM.grid(
        query, 
        fields=fields, 
        links=links,
        field_id=db.school_appointment_categories.id,
        create=False,
        editable=False,
        deletable=False,
        details=False,
        searchable=False,
        csv=False,
        ui = grid_ui)
    grid.element('.web2py_counter', replace=None) # remove the counter
    grid.elements('span[title=Delete]', replace=None) # remove text from delete button

    add_url = URL('ladd')
    add = os_gui.get_button('add', add_url, T("Add a category"), _class="pull-right")

    archive_buttons = os_gui.get_archived_radio_buttons(
        session.school_appointment_categories_show)

    back = DIV(add, archive_buttons)

    return dict(content=grid, back=back)


def index_get_link_archive(row):
    """
        Called from the index function. Changes title of archive button
        depending on whether a category is archived or not
    """
    row = db.school_appointment_categories(row.id)

    if row.Archived:
        tt = T("Move to current")
    else:
        tt = T("Archive")

    return os_gui.get_button('archive',
                             URL('category_archive', vars={'sacID':row.id}),
                             tooltip=tt)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('delete', 'school_appointment_categories'))
def locations_archive():
    """
        This function archives a category
        request.vars[sacID] is expected to be db.school_appointments.id
    """
    sacID = request.vars['sacID']
    if not sacID:
        session.flash = T('Unable to (un)archive category')
    else:
        row = db.school_locations(sacID)

        if row.Archived:
            session.flash = T('Moved to current')
        else:
            session.flash = T('Archived')

        row.Archived = not row.Archived
        row.update_record()

    redirect(URL('index'))