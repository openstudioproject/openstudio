# -*- coding: utf-8 -*-

from general_helpers import set_form_id_and_get_submit_button

@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'shop_manage_workflow'))
def workflow():
    '''
        Settings to control shop workflows
    '''
    response.title = T('Shop')
    response.subtitle = T('Workflow')
    response.view = 'general/only_content.html'

    shop_requires_complete_profile = get_sys_property('shop_requires_complete_profile')
    shop_classes_advance_booking_limit = get_sys_property('shop_classes_advance_booking_limit')
    shop_classes_cancellation_limit = get_sys_property('shop_classes_cancellation_limit')
    shop_subscriptions_start = get_sys_property('shop_subscriptions_start')

    form = SQLFORM.factory(
        Field('shop_requires_complete_profile', 'boolean',
              default=shop_requires_complete_profile,
              label=T('Orders require complete profiles'),
              comment=T('Require complete profiles before customers can place an order')),
        Field('shop_classes_advance_booking_limit', 'integer',
              default=shop_classes_advance_booking_limit,
              requires=IS_INT_IN_RANGE(0, 1099),
              label=T('Classes advance booking limit in days'),
              comment=T("Number of days in advance customers will be able to book classes")),
        Field('shop_classes_cancellation_limit', 'integer',
              default=shop_classes_cancellation_limit,
              requires=IS_INT_IN_RANGE(0, 745),
              label=T('Classes cancellation limit in hours'),
              comment=T("Number of hours before a class starts a booking can be cancelled while returning credit")),
        Field('shop_subscriptions_start',
              default=shop_subscriptions_start,
              requires=IS_IN_SET([
                  ['today', T('Today')],
                  ['next_month', T('First day of next month')]],
                  zero=None),
              label=T('Subscriptions start date'),
              comment=T("Set the default start date for subscriptions in the shop")),
        submit_button=T("Save"),
        separator=' ',
        formstyle='bootstrap3_stacked'
    )

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']

    if form.process().accepted:
        # check shop require complete profiles
        shop_requires_complete_profile = request.vars['shop_requires_complete_profile']
        row = db.sys_properties(Property='shop_requires_complete_profile')
        if not row:
            db.sys_properties.insert(Property='shop_requires_complete_profile',
                                     PropertyValue=shop_requires_complete_profile)
        else:
            row.PropertyValue = shop_requires_complete_profile
            row.update_record()

        # check shop_classes_advance_booking_limit
        shop_classes_advance_booking_limit = request.vars['shop_classes_advance_booking_limit']
        row = db.sys_properties(Property='shop_classes_advance_booking_limit')
        if not row:
            db.sys_properties.insert(Property='shop_classes_advance_booking_limit',
                                     PropertyValue=shop_classes_advance_booking_limit)
        else:
            row.PropertyValue = shop_classes_advance_booking_limit
            row.update_record()

        # check shop_classes_cancellation_limit
        shop_classes_cancellation_limit = request.vars['shop_classes_cancellation_limit']
        row = db.sys_properties(Property='shop_classes_cancellation_limit')
        if not row:
            db.sys_properties.insert(Property='shop_classes_cancellation_limit',
                                     PropertyValue=shop_classes_cancellation_limit)
        else:
            row.PropertyValue = shop_classes_cancellation_limit
            row.update_record()

        # check shop_subscriptions_start
        shop_subscriptions_start = request.vars['shop_subscriptions_start']
        row = db.sys_properties(Property='shop_subscriptions_start')
        if not row:
            db.sys_properties.insert(Property='shop_subscriptions_start',
                                     PropertyValue=shop_subscriptions_start)
        else:
            row.PropertyValue = shop_subscriptions_start
            row.update_record()

        # Clear cache
        cache_clear_sys_properties()
        cache_clear_classschedule()
        # User feedback
        session.flash = T('Saved')
        # reload so the user sees how the values are stored in the db now
        redirect(URL('workflow'))

    content = DIV(DIV(form, _class='col-md-6'),
                  _class='row')

    return dict(content=content,
                back='',
                menu='',
                save=submit)


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'shop_products_sets'))
def products_sets():
    """
        List shop product_sets
    """
    from openstudio import ShopProductsSets
    from openstudio_tools import OsSession

    response.title = T('Shop')
    response.subtitle = T('Products sets')
    response.view = 'general/only_content.html'

    product_sets = ShopProductsSets()
    content = product_sets.list_formatted()

    add = os_gui.get_button('add', URL('shop_manage', 'products_set_add'))

    return dict(content=content,
                add=add)


def shop_products_sets_get_return_url(var=None):
    """
        :return: URL to shop product_sets list page
    """
    return URL('shop_manage', 'products_sets')


@auth.requires_login()
def products_set_add():
    """
        Add a new product_set
    """
    from openstudio import OsForms
    response.title = T('Shop')
    response.subtitle = T('Add product set')
    response.view = 'general/only_content.html'

    return_url = shop_products_sets_get_return_url()

    os_forms = OsForms()
    result = os_forms.get_crud_form_create(
        db.shop_products_sets,
        return_url,
    )

    form = result['form']
    back = os_gui.get_button('back', return_url)

    return dict(content=form,
                save=result['submit'],
                back=back)


@auth.requires_login()
def products_set_edit():
    """
        Edit a product_set
        request.vars['spsID'] is expected to be db.shop_product_sets.id
    """
    from openstudio import OsForms

    response.title = T('Shop')
    response.subtitle = T('Edit product set')
    response.view = 'general/only_content.html'
    spsID = request.vars['spsID']

    return_url = shop_products_sets_get_return_url()

    os_forms = OsForms()
    result = os_forms.get_crud_form_update(
        db.shop_products_sets,
        return_url,
        spsID
    )

    form = result['form']
    back = os_gui.get_button('back', return_url)

    return dict(content=form,
                save=result['submit'],
                back=back)


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('delete', 'shop_products_sets'))
def products_set_delete():
    """
        Delete a products set
    """
    spsID = request.vars['spsID']

    query = (db.shop_products_sets.id == spsID)
    db(query).delete()

    redirect(shop_products_sets_get_return_url())


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'shop_products_sets_options'))
def products_set_options():
    """
        List products set options
    """
    from openstudio import ShopProductsSetsOptions
    response.title = T('Shop')
    response.subtitle = T('Products set options')
    response.view = 'general/only_content.html'

    spsID = request.vars['spsID']
    products_set = db.shop_products_sets(spsID)
    response.subtitle += ' - ' + products_set.Name

    spso = ShopProductsSetsOptions(spsID,
                                   URL(request.function,
                                       vars={'spsID': spsID}))
    content = DIV(spso.list_formatted())
    back = os_gui.get_button('back',
                             shop_products_sets_get_return_url())

    return dict(content=content,
                back=back)


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'shop_categories'))
def categories():
    """
        List shop categories
    """
    from openstudio import ShopCategories
    from openstudio_tools import OsSession

    response.title = T('Shop')
    response.subtitle = T('Categories')
    response.view = 'general/only_content.html'

    os_session = OsSession()
    value = os_session.get_request_var_or_session(
        'show_archive',
        'current',
        'shop_manage_categories_show'
    )

    show_archived = False
    if value == 'archive':
        show_archived = True

    categories = ShopCategories(show_archived)
    content = categories.list_formatted()

    add = os_gui.get_button('add', URL('shop_manage', 'category_add'))
    archive_buttons = os_gui.get_archived_radio_buttons(
        session.shop_manage_categories_show)

    return dict(content=content,
                add=add,
                header_tools=archive_buttons)


def shop_categories_get_return_url(var=None):
    """
        :return: URL to shop categories list page
    """
    return URL('shop_manage', 'categories')


@auth.requires_login()
def category_add():
    """
        Add a new category
    """
    from openstudio import OsForms
    response.title = T('Shop')
    response.subtitle = T('Add category')
    response.view = 'general/only_content.html'

    return_url = shop_categories_get_return_url()

    os_forms = OsForms()
    result = os_forms.get_crud_form_create(
        db.shop_categories,
        return_url,
    )

    form = result['form']
    back = os_gui.get_button('back', return_url)

    return dict(content=form,
                save=result['submit'],
                back=back)


@auth.requires_login()
def category_edit():
    """
        Edit a category
        request.vars['scID'] is expected to be db.shop_categories.id
    """
    from openstudio import OsForms

    response.title = T('Shop')
    response.subtitle = T('Edit category')
    response.view = 'general/only_content.html'
    scID = request.vars['scID']

    return_url = shop_categories_get_return_url()

    os_forms = OsForms()
    result = os_forms.get_crud_form_update(
        db.shop_categories,
        return_url,
        scID
    )

    form = result['form']
    back = os_gui.get_button('back', return_url)

    return dict(content=form,
                save=result['submit'],
                back=back)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('update', 'shop_categories'))
def category_archive():
    """
        Archive a category
        request.vars[scID] is expected to be in db.shop_categories.id
        :return: None
    """
    from openstudio_tools import OsArchiver

    archiver = OsArchiver()
    archiver.archive(
        db.shop_categories,
        request.vars['scID'],
        T('Unable to (un)archive brand'),
        shop_categories_get_return_url()
    )


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'shop_brands'))
def brands():
    """
        List shop brands
    """
    from openstudio import ShopBrands
    from openstudio_tools import OsSession

    response.title = T('Shop')
    response.subtitle = T('Brands')
    response.view = 'general/only_content.html'

    os_session = OsSession()
    value = os_session.get_request_var_or_session(
        'show_archive',
        'current',
        'shop_manage_brands_show'
    )

    show_archived = False
    if value == 'archive':
        show_archived = True

    brands = ShopBrands(show_archived)
    content = brands.list_formatted()

    add = os_gui.get_button('add', URL('shop_manage', 'brand_add'))
    archive_buttons = os_gui.get_archived_radio_buttons(
        session.shop_manage_brands_show)

    return dict(content=content,
                add=add,
                header_tools=archive_buttons)


def shop_brand_get_return_url(var=None):
    """
        :return: URL to shop brands list page
    """
    return URL('shop_manage', 'brands')


@auth.requires_login()
def brand_add():
    """
        Add a new brand
    """
    from openstudio import OsForms
    response.title = T('Shop')
    response.subtitle = T('Add brand')
    response.view = 'general/only_content.html'

    return_url = shop_brand_get_return_url()

    os_forms = OsForms()
    result = os_forms.get_crud_form_create(
        db.shop_brands,
        return_url,
    )

    form = result['form']
    back = os_gui.get_button('back', return_url)

    return dict(content=form,
                save=result['submit'],
                back=back)


@auth.requires_login()
def brand_edit():
    """
        Edit a brand
        request.vars['sbID'] is expected to be db.shop_brands.id
    """
    from openstudio import OsForms

    response.title = T('Shop')
    response.subtitle = T('Edit brand')
    response.view = 'general/only_content.html'
    sbID = request.vars['sbID']

    return_url = shop_brand_get_return_url()

    os_forms = OsForms()
    result = os_forms.get_crud_form_update(
        db.shop_brands,
        return_url,
        sbID
    )

    form = result['form']
    back = os_gui.get_button('back', return_url)

    return dict(content=form,
                save=result['submit'],
                back=back)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('update', 'shop_brands'))
def brand_archive():
    """
        Archive a brand
        request.vars[sbID] is expected to be in db.shop_brands.id
        :return: None
    """
    from openstudio_tools import OsArchiver

    archiver = OsArchiver()
    archiver.archive(
        db.shop_brands,
        request.vars['sbID'],
        T('Unable to (un)archive brand'),
        shop_brand_get_return_url()
    )


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'shop_suppliers'))
def suppliers():
    """
        List shop suppliers
    """
    from openstudio import ShopSuppliers
    from openstudio_tools import OsSession

    response.title = T('Shop')
    response.subtitle = T('Suppliers')
    response.view = 'general/only_content.html'

    os_session = OsSession()
    value = os_session.get_request_var_or_session(
        'show_archive',
        'current',
        'shop_manage_suppliers_show'
    )

    show_archived = False
    if value == 'archive':
        show_archived = True

    suppliers = ShopSuppliers(show_archived)
    content = suppliers.list_formatted()

    add = os_gui.get_button('add', URL('shop_manage', 'supplier_add'))
    archive_buttons = os_gui.get_archived_radio_buttons(
        session.shop_manage_suppliers_show)

    return dict(content=content,
                add=add,
                header_tools=archive_buttons)


def shop_supplier_get_return_url(var=None):
    """
        :return: URL to shop suppliers list page
    """
    return URL('shop_manage', 'suppliers')


@auth.requires_login()
def supplier_add():
    """
        Add a new supplier
    """
    from openstudio import OsForms
    response.title = T('Shop')
    response.subtitle = T('Add supplier')
    response.view = 'general/only_content.html'

    return_url = shop_supplier_get_return_url()

    os_forms = OsForms()
    result = os_forms.get_crud_form_create(
        db.shop_suppliers,
        return_url,
    )

    form = result['form']
    back = os_gui.get_button('back', return_url)

    return dict(content=form,
                save=result['submit'],
                back=back)


@auth.requires_login()
def supplier_edit():
    """
        Edit a supplier
        request.vars['sbID'] is expected to be db.shop_brands.id
    """
    from openstudio import OsForms

    response.title = T('Shop')
    response.subtitle = T('Edit supplier')
    response.view = 'general/only_content.html'
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

    return dict(content=form,
                save=result['submit'],
                back=back)


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

