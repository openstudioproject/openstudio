# coding=utf-8


def get_menu(page):
    """
        Returns menu for school appointments
    """
    pages = []

    # Appointments
    if auth.has_membership(group_id='Admins') or \
       auth.has_permission('read', 'school_appointments'):
        pages.append(['index',
                       T('Appointments'),
                      URL('school_appointments', 'index')])

    # Categories
    if auth.has_membership(group_id='Admins') or \
       auth.has_permission('read', 'school_appointments_categories'):
        pages.append(['categories',
                       T('Categories'),
                      URL('school_appointments', 'categories')])


    return os_gui.get_submenu(pages,
                              page,
                              _id='os-customers_edit_menu',
                              horizontal=True,
                              htype='tabs')


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'school_appointments'))
def index():
    response.title = T("School")
    response.subtitle = T("Appointments")
    response.view = 'general/tabs_menu.html'

    show = 'current'
    query = (db.school_appointments.Archived == False)

    left = [
        db.school_appointments_categories.on(
            db.school_appointments.school_appointments_categories_id ==
            db.school_appointments_categories.id
        )
    ]

    if 'show_archive' in request.vars:
        show = request.vars['show_archive']
        session.school_appointments_show = show
        if show == 'current':
            query = (db.school_appointments.Archived == False)
        elif show == 'archive':
            query = (db.school_appointments.Archived == True)
    elif session.school_appointments_show == 'archive':
        query = (db.school_appointments.Archived == True)
    else:
        session.school_appointments_show = show

    db.school_appointments.id.readable = False

    fields = [
        # db.school_appointments.id,
        db.school_appointments.Name,
        db.school_appointments_categories.Name
    ]

    permission_edit = auth.has_membership(group_id='Admins') or \
                      auth.has_permission('update', 'school_appointments')
    permission_edit_categories = True

    links = [
        lambda row: os_gui.get_button('edit',
                                      URL('edit', vars={'saID': row.school_appointments.id}),
                                      T("Edit this appointment")) if permission_edit else "",
        index_get_link_archive
    ]

    maxtextlengths = {
        'school_appointments.Name': 40
    }

    grid = SQLFORM.grid(
        query,
        left=left,
        fields=fields,
        links=links,
        field_id=db.school_appointments.id,
        create=False,
        editable=False,
        deletable=False,
        details=False,
        searchable=False,
        maxtextlengths=maxtextlengths,
        orderby=db.school_appointments_categories.Name|db.school_appointments.Name,
        csv=False,
        ui=grid_ui)
    grid.element('.web2py_counter', replace=None)  # remove the counter
    grid.elements('span[title=Delete]', replace=None)  # remove text from delete button]

    add_url = URL('add')
    add = os_gui.get_button('add', add_url, T("Add an appoiment type"), _class="pull-right")

    archive_buttons = os_gui.get_archived_radio_buttons(
        session.school_appointments_show)

    back = DIV(add, archive_buttons)
    menu = get_menu(request.function)

    return dict(content=grid, back=back, menu=menu)


def index_get_link_archive(row):
    """
        Called from the index function. Changes title of archive button
        depending on whether a category is archived or not
    """
    appointment = db.school_appointments(row.school_appointments.id)

    if appointment.Archived:
        tt = T("Move to current")
    else:
        tt = T("Archive")

    return os_gui.get_button('archive',
                             URL('archive', vars={'saID':row.school_appointments.id}),
                             tooltip=tt)



def index_get_return_url():
    return URL('index')


@auth.requires_login()
def add():
    """
        Add a new appointment type
    """
    from openstudio.os_forms import OsForms
    response.title = T('School')
    response.subtitle = T("Appointments")
    response.view = 'general/tabs_menu.html'

    return_url = index_get_return_url()

    os_forms = OsForms()
    result = os_forms.get_crud_form_create(
        db.school_appointments,
        return_url,
        message_record_created=T("Added appointment type")
    )

    form = result['form']
    back = os_gui.get_button('back', return_url)

    content = DIV(
        H4(T('Add appointment type')),
        form
    )
    menu = get_menu('index')

    return dict(content=content,
                save=result['submit'],
                menu=menu,
                back=back)


def edit_get_menu(page, saID):
    """
        Returns menu for school appointments
    """
    pages = []

    vars = {'saID': request.vars['saID']}

    # Edit appointment
    if auth.has_membership(group_id='Admins') or \
       auth.has_permission('update', 'school_appointments'):
        pages.append(['edit',
                       T('Edit'),
                      URL('school_appointments', 'edit', vars=vars)])

    # Prices
    if auth.has_membership(group_id='Admins') or \
       auth.has_permission('view', 'school_appointments_teachers_price'):
        pages.append(['teachers_prices',
                       T('Teacher prices'),
                      URL('school_appointments', 'teachers_prices')])


    return os_gui.get_submenu(pages,
                              page,
                              _id='os-customers_edit_menu',
                              horizontal=True,
                              htype='tabs')



@auth.requires_login()
def edit():
    """
        Edit an appointment type
    """
    from openstudio.os_forms import OsForms
    response.title = T('School')
    response.subtitle = T("Edit appointment type")
    response.view = 'general/tabs_menu.html'

    saID = request.vars['saID']

    return_url = index_get_return_url()

    os_forms = OsForms()
    result = os_forms.get_crud_form_update(
        db.school_appointments,
        return_url,
        saID,
        message_record_updated=T("Saved")
    )

    form = result['form']
    back = os_gui.get_button('back', return_url)

    content = form
    menu = edit_get_menu(request.function, saID)

    return dict(content=content,
                save=result['submit'],
                back=back,
                menu=menu)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('delete', 'school_appointments'))
def archive():
    """
        Archive an appointment type
    """
    from openstudio.tools import OsArchiver

    archiver = OsArchiver()
    archiver.archive(
        db.school_appointments,
        request.vars['saID'],
        T('Unable to (un)archive appointment'),
        index_get_return_url()
    )


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'school_appointments_categories'))
def categories():
    response.title = T("School")
    response.subtitle = T("Appointments")
    response.view = 'general/tabs_menu.html'

    show = 'current'
    query = (db.school_appointments_categories.Archived == False)

    if 'show_archive' in request.vars:
        show = request.vars['show_archive']
        session.school_appointments_categories_show = show
        if show == 'current':
            query = (db.school_appointments_categories.Archived == False)
        elif show == 'archive':
            query = (db.school_appointments_categories.Archived == True)
    elif session.school_appointments_categories_show == 'archive':
            query = (db.school_appointments_categories.Archived == True)
    else:
        session.school_appointments_categories_show = show

    db.school_appointments_categories.id.readable=False
    fields = [
        db.school_appointments_categories.Name
    ]
    links = [ 
        lambda row: os_gui.get_button('edit',
            URL('category_edit', vars={'sacID': row.id}),
            T("Edit this category")),
        categories_get_link_archive
    ]

    maxtextlengths = {
        'school_appointments_categories.Name': 40
    }
    
    grid = SQLFORM.grid(
        query, 
        fields=fields, 
        links=links,
        field_id=db.school_appointments_categories.id,
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
        session.school_appointments_categories_show)

    back = DIV(add, archive_buttons)
    menu = get_menu(request.function)

    return dict(content=grid, back=back, menu=menu)


def categories_get_link_archive(row):
    """
        Called from the categories function. Changes title of archive button
        depending on whether a category is archived or not
    """
    row = db.school_appointments_categories(row.id)

    if row.Archived:
        tt = T("Move to current")
    else:
        tt = T("Archive")

    return os_gui.get_button('archive',
                             URL('category_archive', vars={'sacID':row.id}),
                             tooltip=tt)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('delete', 'school_appointments_categories'))
def category_archive():
    """
        This function archives a category
        request.vars[sacID] is expected to be db.school_appointments.id
    """
    sacID = request.vars['sacID']
    if not sacID:
        session.flash = T('Unable to (un)archive category')
    else:
        row = db.school_appointments_categories(sacID)

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
    response.subtitle = T("Appointments")
    response.view = 'general/tabs_menu.html'

    return_url = categories_get_return_url()

    os_forms = OsForms()
    result = os_forms.get_crud_form_create(
        db.school_appointments_categories,
        return_url,
        message_record_created=T("Added category ")
    )

    form = result['form']
    back = os_gui.get_button('back', return_url)

    content = DIV(
        H4(T('Add category')),
        form
    )
    menu = get_menu('categories')

    return dict(content=content,
                save=result['submit'],
                menu=menu,
                back=back)


@auth.requires_login()
def category_edit():
    """
        Edit a category
    """
    from openstudio.os_forms import OsForms

    response.title = T('School')
    response.subtitle = T("Appointments")
    response.view = 'general/tabs_menu.html'

    sacID = request.vars['sacID']

    return_url = categories_get_return_url()

    os_forms = OsForms()
    result = os_forms.get_crud_form_update(
        db.school_appointments_categories,
        URL(vars={'sacID': sacID}),
        sacID,
        message_record_updated=T("Saved")
    )

    form = result['form']
    back = os_gui.get_button('back', return_url)

    content = DIV(
        H4(T('Edit category')),
        form
    )

    menu = get_menu('categories')

    return dict(content=content,
                save=result['submit'],
                back=back,
                menu=menu)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('view', 'school_appointments_teachers_price'))
def teachers_prices():
    """
        List prices for an appointment type
    """
    response.title = T('School')
    response.subtitle = T("Edit appointment type")
    response.view = 'general/tabs_menu.html'

    saID = request.vars['saID']
    return_url = index_get_return_url()


    back = os_gui.get_button('back', return_url)

    content = 'hello world'
    menu = edit_get_menu(request.function, saID)

    return dict(content=content,
                back=back,
                menu=menu)
