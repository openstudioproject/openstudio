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
        db.school_appointments.Name
    ]

    permission_edit = auth.has_membership(group_id='Admins') or \
                      auth.has_permission('update', 'school_appointments')
    permission_edit_categories = True

    links = [
        lambda row: os_gui.get_button('edit',
                                      URL('edit', vars={'saID': row.id}),
                                      T("Edit this appointment")) if permission_edit else "",
        lambda row: os_gui.get_button('edit_categories',
                                      URL('edit_categories', vars={'saID': row.id}),
                                      T("Assign categories to this appointment type")) if permission_edit_categories else "",
        index_get_link_archive
    ]

    maxtextlengths = {
        'school_appointments.Name': 40
    }

    grid = SQLFORM.grid(
        query,
        fields=fields,
        links=links,
        field_id=db.school_appointments.id,
        create=False,
        editable=False,
        deletable=False,
        details=False,
        searchable=False,
        maxtextlengths=maxtextlengths,
        csv=False,
        ui=grid_ui)
    grid.element('.web2py_counter', replace=None)  # remove the counter
    grid.elements('span[title=Delete]', replace=None)  # remove text from delete button

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
    row = db.school_appointments(row.id)

    if row.Archived:
        tt = T("Move to current")
    else:
        tt = T("Archive")

    return os_gui.get_button('archive',
                             URL('archive', vars={'saID':row.id}),
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
        '/school_appointments/edit?saID=[id]',
        message_record_created=T("Added appointment type, you can now edit it and assign it to categories")
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
        URL(vars={'saID': saID}),
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



def edit_get_menu(page, saID):
    """
        Returns menu for school appointment edit page
    """
    pages = []

    vars = {'saID': saID}

    # Edit appointment
    if auth.has_membership(group_id='Admins') or \
       auth.has_permission('update', 'school_appointments'):
        pages.append(['edit',
                       T('Edit'),
                      URL('school_appointments', 'edit', vars=vars)])

    # Edit appointment type categories
    if auth.has_membership(group_id='Admins') or \
       auth.has_permission('update', 'school_appointments_categories'):
        pages.append(['edit_categories',
                      T('Categories'),
                      URL('school_appointments', 'edit_categories', vars=vars)])


    return os_gui.get_submenu(pages,
                              page,
                              _id='os-customers_edit_menu',
                              horizontal=True,
                              htype='tabs')


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'school_appointments_categories'))
def edit_categories():
    """

    :return:
    """
    from general_helpers import set_form_id_and_get_submit_button
    from openstudio.os_shop_product import ShopProduct

    saID = request.vars['saID']
    sa = db.school_appointments(saID)
    # product = ShopProduct(spID)

    response.title = T('Shop')
    response.subtitle = T("Edit appointment type")
    # response.subtitle = T('Edit product - {product_name}'.format(
    #     school=product.row.Name)
    # )
    response.view = 'general/tabs_menu.html'

    header = THEAD(TR(
        TH(),
        TH(T("Category"))
    ))

    table = TABLE(header, _class='table table-hover')
    query = (db.school_appointments_categories_appointments.school_appointments_id == saID)
    rows = db(query).select(db.school_appointments_categories_appointments.school_appointments_categories_id)
    selected_ids = []
    for row in rows:
        selected_ids.append(unicode(row.school_appointments_categories_id))

    query = (db.school_appointments_categories.Archived == False)
    rows = db(query).select(
        db.school_appointments_categories.id,
        db.school_appointments_categories.Name,
        orderby=db.school_appointments_categories.Name
    )

    for row in rows:
        if unicode(row.id) in selected_ids:
            # check the row
            table.append(TR(TD(INPUT(_type='checkbox',
                                     _name=row.id,
                                     _value="on",
                                     value="on"),
                                     _class='td_status_marker'),
                            TD(row.Name)))
        else:
            table.append(TR(TD(INPUT(_type='checkbox',
                                     _name=row.id,
                                     _value="on"),
                                     _class='td_status_marker'),
                            TD(row.Name)))
    form = FORM(table, _id='MainForm')

    return_url = URL(vars={'saID':saID})
    # After submitting, check which categories are 'on'
    if form.accepts(request,session):
        # Remove all current records
        # query = (db.shop_categories_products.shop_products_id == spID)
        query = (db.school_appointments_categories_appointments.school_appointments_id == saID)
        db(query).delete()
        # insert new records for product
        for row in rows:
            if request.vars[unicode(row.id)] == 'on':
                db.school_appointments_categories_appointments.insert(
                    school_appointments_categories_id = row.id,
                    school_appointments_id = saID
                )

        session.flash = T('Saved')
        redirect(return_url)


    back = os_gui.get_button('back', index_get_return_url())
    menu = edit_get_menu(request.function, saID)

    return dict(content=form,
                save=os_gui.get_submit_button('MainForm'),
                back=back,
                menu=menu)


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