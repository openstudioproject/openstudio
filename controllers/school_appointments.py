# coding=utf-8


def index_get_menu(page):
    """
        Returns menu for shop catalog pages
    """
    pages = []

    # Appointments
    if auth.has_membership(group_id='Admins') or \
       auth.has_permission('read', 'shop_products'):
        pages.append(['school_appointments',
                       T('Products'),
                      URL('shop_manage', 'products')])

    # Categories
    if auth.has_membership(group_id='Admins') or \
       auth.has_permission('read', 'shop_categories'):
        pages.append(['categories',
                       T('Categories'),
                      URL('shop_manage', 'categories')])


    return os_gui.get_submenu(pages,
                              page,
                              _id='os-customers_edit_menu',
                              horizontal=True,
                              htype='tabs')


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'school_appointment_categories'))
def index():
    response.title = T("School")
    response.subtitle = T("Appointment categories")
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
    fields = [
        db.school_appointment_categories.Name
    ]
    links = [ 
        lambda row: os_gui.get_button('edit',
            URL('edit', vars={'sacID': row.id}),
            T("Edit this category")),
        categories_get_link_archive
    ]

    maxtextlengths = {
        'school_appointment_categories.Name': 40
    }
    
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
        maxtextlengths=maxtextlengths,
        csv=False,
        ui = grid_ui)
    grid.element('.web2py_counter', replace=None) # remove the counter
    grid.elements('span[title=Delete]', replace=None) # remove text from delete button

    add_url = URL('category_add')
    add = os_gui.get_button('add', add_url, T("Add a category"), _class="pull-right")

    archive_buttons = os_gui.get_archived_radio_buttons(
        session.school_appointment_categories_show)

    back = DIV(add, archive_buttons)

    return dict(content=grid, back=back)


def categories_get_link_archive(row):
    """
        Called from the categories function. Changes title of archive button
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
def category_archive():
    """
        This function archives a category
        request.vars[sacID] is expected to be db.school_appointments.id
    """
    sacID = request.vars['sacID']
    if not sacID:
        session.flash = T('Unable to (un)archive category')
    else:
        row = db.school_appointment_categories(sacID)

        if row.Archived:
            session.flash = T('Moved to current')
        else:
            session.flash = T('Archived')

        row.Archived = not row.Archived
        row.update_record()

    redirect(URL('categories'))


def categories_get_return_url():
    return URL('categories')


@auth.requires_login()
def category_add():
    """
        Add a new category
    """
    from openstudio.os_forms import OsForms
    response.title = T('School')
    response.subtitle = T('Add appointment category')
    response.view = 'general/only_content.html'

    return_url = categories_get_return_url()

    os_forms = OsForms()
    result = os_forms.get_crud_form_create(
        db.school_appointment_categories,
        return_url,
        message_record_created=T("Added category ")
    )

    form = result['form']
    back = os_gui.get_button('back', return_url)

    content = form

    return dict(content=content,
                save=result['submit'],
                back=back)


@auth.requires_login()
def edit():
    """
        Edit a category
    """
    from openstudio.os_forms import OsForms
    response.title = T('School')
    response.subtitle = T('Edit appointment category')
    response.view = 'general/only_content.html'

    sacID = request.vars['sacID']

    return_url = categories_get_return_url()

    os_forms = OsForms()
    result = os_forms.get_crud_form_update(
        db.school_appointment_categories,
        URL(vars={'sacID': sacID}),
        sacID,
        message_record_updated=T("Saved")
    )

    form = result['form']
    back = os_gui.get_button('back', return_url)

    content = form

    return dict(content=content,
                save=result['submit'],
                back=back)