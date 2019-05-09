# -*- coding: utf-8 -*-

from general_helpers import set_form_id_and_get_submit_button

@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'shop_manage_workflow'))
def workflow():
    """
        Settings to control shop workflows
    """
    response.title = T('Shop')
    response.subtitle = T('Workflow')
    response.view = 'general/only_content.html'

    registration_requires_mobile = get_sys_property('registration_requires_mobile')
    shop_requires_complete_profile_classes = get_sys_property('shop_requires_complete_profile_classes')
    shop_requires_complete_profile_memberships = get_sys_property('shop_requires_complete_profile_memberships')
    shop_requires_complete_profile_classcards = get_sys_property('shop_requires_complete_profile_classcards')
    shop_requires_complete_profile_events = get_sys_property('shop_requires_complete_profile_events')
    shop_requires_complete_profile_subscriptions = get_sys_property('shop_requires_complete_profile_subscriptions')
    shop_allow_trial_cards_for_existing_customers = get_sys_property('shop_allow_trial_cards_for_existing_customers')
    shop_classes_advance_booking_limit = get_sys_property('shop_classes_advance_booking_limit')
    shop_classes_cancellation_limit = get_sys_property('shop_classes_cancellation_limit')
    shop_subscriptions_start = get_sys_property('shop_subscriptions_start')

    shop_subscriptions_payment_method = get_sys_property('shop_subscriptions_payment_method')

    form = SQLFORM.factory(
        Field('registration_requires_mobile', 'boolean',
              default=registration_requires_mobile,
              label=T('Phone number is required when registering'),
              comment=T('Customers will have to enter a phone number when creating an account')),
        Field('shop_requires_complete_profile_classes', 'boolean',
              default=shop_requires_complete_profile_classes,
              label=T('Booking classes require complete profiles'),
              comment=T('Require complete profiles before customers can book a class')),
        Field('shop_requires_complete_profile_memberships', 'boolean',
              default=shop_requires_complete_profile_memberships,
              label=T('Memberships require complete profiles'),
              comment=T('Require complete profiles before customers can get a membership')),
        Field('shop_requires_complete_profile_classcards', 'boolean',
              default=shop_requires_complete_profile_classcards,
              label=T('Classcards require complete profiles'),
              comment=T('Require complete profiles before customers can buy a classcard')),
        Field('shop_requires_complete_profile_events', 'boolean',
              default=shop_requires_complete_profile_events,
              label=T('Events require complete profiles'),
              comment=T('Require complete profiles before customers can book an event')),
        Field('shop_requires_complete_profile_subscriptions', 'boolean',
              default=shop_requires_complete_profile_subscriptions,
              label=T('Subscriptions require complete profiles'),
              comment=T('Require complete profiles before customers can sign up for a subscription')),
        Field('shop_allow_trial_cards_for_existing_customers', 'boolean',
              default=shop_allow_trial_cards_for_existing_customers,
              label=T('Allow existing customers to buy a trial card'),
              comment=T('Disable to prevent trial products from showing in shop for any customers who have or have had a subscription or card.')),
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
        Field('shop_subscriptions_payment_method',
              default=shop_subscriptions_payment_method,
              requires=IS_IN_SET([
                  ['directdebit', T('Direct Debit')],
                  ['mollie', T('Mollie')]],
                  zero=None),
              label=T('Subscriptions Payment Method'),
              comment=T("Set the default payment method for subscriptions in the shop")),
        submit_button=T("Save"),
        separator=' ',
        formstyle='bootstrap3_stacked'
    )

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']

    if form.process().accepted:
        form_vars = [
            'registration_requires_mobile',
            'shop_requires_complete_profile_classes',
            'shop_requires_complete_profile_memberships',
            'shop_requires_complete_profile_classcards',
            'shop_requires_complete_profile_events',
            'shop_requires_complete_profile_subscriptions',
            'shop_allow_trial_cards_for_existing_customers',
            'shop_classes_advance_booking_limit',
            'shop_classes_cancellation_limit',
            'shop_subscriptions_start',
            'shop_subscriptions_payment_method',

        ]

        for fvar in form_vars:
            if fvar in request.vars:
                set_sys_property(
                    fvar,
                    request.vars[fvar]
                )
            else:
                set_sys_property(
                    fvar,
                    None
                )

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


def catalog_get_menu(page):
    """
        Returns menu for shop catalog pages
    """
    pages = []

    # Products
    if auth.has_membership(group_id='Admins') or \
       auth.has_permission('read', 'shop_products'):
        pages.append(['products',
                       T('Products'),
                      URL('shop_manage', 'products')])
    # # Stock
    # if auth.has_membership(group_id='Admins') or \
    #    auth.has_permission('read', 'shop_stock'):
    #     pages.append(['Stock',
    #                    T('Stock'),
    #                   URL('shop_manage', 'stock')])
    # Categories
    if auth.has_membership(group_id='Admins') or \
       auth.has_permission('read', 'shop_categories'):
        pages.append(['categories',
                       T('Categories'),
                      URL('shop_manage', 'categories')])
    # Brands
    if auth.has_membership(group_id='Admins') or \
       auth.has_permission('read', 'shop_brands'):
        pages.append(['brands',
                       T('Brands'),
                      URL('shop_manage', 'brands')])
    # Suppliers
    if auth.has_membership(group_id='Admins') or \
       auth.has_permission('read', 'shop_suppliers'):
        pages.append(['suppliers',
                       T('Suppliers'),
                      URL('shop_manage', 'suppliers')])
    # Product sets
    if auth.has_membership(group_id='Admins') or \
       auth.has_permission('read', 'shop_products_sets'):
        pages.append(['products_sets',
                       T('Product sets'),
                      URL('shop_manage', 'products_sets')])
    # Sales
    if auth.has_membership(group_id='Admins') or \
       auth.has_permission('read', 'shop_products'):
        pages.append(['sales',
                       T('Sales'),
                      URL('shop_manage', 'sales')])

    return os_gui.get_submenu(pages,
                              page,
                              _id='os-customers_edit_menu',
                              horizontal=True,
                              htype='tabs')


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'shop_products'))
def products():
    """
        List products
    """
    from openstudio.os_shop_products import ShopProducts

    response.title = T('Shop')
    response.subtitle = T('Catalog')
    response.view = 'general/tabs_menu.html'

    products = ShopProducts()
    content = products.list_formatted()

    add = os_gui.get_button('add', URL('shop_manage', 'product_add'))
    menu = catalog_get_menu(request.function)

    return dict(content=content,
                add=add,
                menu=menu)


def shop_products_get_return_url(var=None):
    """
        :return: URL to shop product list page
    """
    return URL('shop_manage', 'products')


# def shop_products_get_add_edit_return_url(var=None):
#


@auth.requires_login()
def product_add():
    """
        Add a new product
    """
    from openstudio.os_forms import OsForms
    response.title = T('Shop')
    response.subtitle = T('Catalog')
    response.view = 'general/tabs_menu.html'

    return_url = shop_products_get_return_url()

    os_forms = OsForms()
    result = os_forms.get_crud_form_create(
        db.shop_products,
        '/shop_manage/product_edit?spID=[id]',
        onaccept=product_onaccept,
        message_record_created=T("Added product, you can now add variants and categories")
    )

    form = result['form']
    back = os_gui.get_button('back', return_url)

    content = DIV(
        H4(T('Add product')),
        form
    )

    menu = catalog_get_menu('products')

    return dict(content=content,
                save=result['submit'],
                back=back,
                menu=menu)


@auth.requires_login()
def product_edit():
    """
        Edit a product
    """
    from openstudio.os_forms import OsForms

    spID = request.vars['spID']
    sp = db.shop_products(spID)

    response.title = T('Shop')
    response.subtitle = T('Edit product - {product_name}'.format(
        product_name=sp.Name)
    )
    response.view = 'general/tabs_menu.html'

    return_url = shop_products_get_return_url()

    os_forms = OsForms()
    result = os_forms.get_crud_form_update(
        db.shop_products,
        URL(vars={'spID': spID}),
        spID,
        onaccept=product_onaccept
    )

    form = result['form']
    back = os_gui.get_button('back', return_url)

    content = DIV(
        H4(T('Edit product')),
        form
    )

    menu = product_edit_get_menu(request.function, spID)

    return dict(content=content,
                save=result['submit'],
                back=back,
                menu=menu)


def product_edit_get_menu(page, spID):
    """
        Returns menu for shop edit pages
    """
    pages = []

    vars = {
        'spID': spID
    }

    # Products
    if auth.has_membership(group_id='Admins') or \
       auth.has_permission('update', 'shop_products'):
        pages.append(['product_edit',
                       T('Edit'),
                      URL('shop_manage', 'product_edit', vars=vars)])
    # Variants
    if auth.has_membership(group_id='Admins') or \
       auth.has_permission('read', 'shop_products_variants'):
        pages.append(['product_variants',
                       T('Variants'),
                      URL('shop_manage', 'product_variants', vars=vars)])
    # Categories
    if auth.has_membership(group_id='Admins') or \
       auth.has_permission('read', 'shop_categories_products'):
        pages.append(['product_categories',
                       T('Categories'),
                      URL('shop_manage', 'product_categories', vars=vars)])

    # Categories
    # if auth.has_membership(group_id='Admins') or \
    #    auth.has_permission('read', 'shop_categories'):
    #     pages.append(['categories',
    #                    T('Categories'),
    #                   URL('shop_manage', 'categories')])
    # # Brands
    # if auth.has_membership(group_id='Admins') or \
    #    auth.has_permission('read', 'shop_brands'):
    #     pages.append(['brands',
    #                    T('Brands'),
    #                   URL('shop_manage', 'brands')])
    # # Suppliers
    # if auth.has_membership(group_id='Admins') or \
    #    auth.has_permission('read', 'shop_suppliers'):
    #     pages.append(['suppliers',
    #                    T('Suppliers'),
    #                   URL('shop_manage', 'suppliers')])
    # # Product sets
    # if auth.has_membership(group_id='Admins') or \
    #    auth.has_permission('read', 'shop_products_sets'):
    #     pages.append(['products_sets',
    #                    T('Product sets'),
    #                   URL('shop_manage', 'products_sets')])

    return os_gui.get_submenu(pages,
                              page,
                              _id='os-customers_edit_menu',
                              horizontal=True,
                              htype='tabs')



def product_onaccept(form):
    """
        Function run when adding or editing a product
        If there is a product set, add all possible variants
        If not, add a default variant
    """
    from openstudio.os_shop_product import ShopProduct
    from openstudio.os_shop_products_set import ShopProductsSet
    spID = form.vars.id
    spsID = form.vars.shop_products_sets_id

    if not spsID:
        # Check if we have > 1 variant
        product = ShopProduct(spID)
        if not product.count_variants():
            product.add_default_variant()
    else:
        products_set = ShopProductsSet(spsID)
        products_set.insert_variants_for_product(spID)


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('delete', 'shop_products'))
def product_delete():
    """
        Delete a product
    """
    spID = request.vars['spID']

    query = (db.shop_products.id == spID)
    db(query).delete()

    session.flash = T('Deleted product')
    redirect(shop_products_get_return_url())


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'shop_categories_products'))
def product_categories():
    """

    :return:
    """
    from general_helpers import set_form_id_and_get_submit_button
    from openstudio.os_shop_product import ShopProduct

    spID = request.vars['spID']
    product = ShopProduct(spID)

    response.title = T('Shop')
    response.subtitle = T('Edit product - {product_name}'.format(
        product_name=product.row.Name)
    )
    response.view = 'general/tabs_menu.html'

    header = THEAD(TR(
        TH(),
        TH(T("Category"))
    ))

    table = TABLE(header, _class='table table-hover')
    query = (db.shop_categories_products.shop_products_id == spID)
    # rows = db(query).select(db.teachers_classtypes.school_classtypes_id)
    rows = db(query).select(db.shop_categories_products.shop_categories_id)
    selected_ids = []
    for row in rows:
        selected_ids.append(unicode(row.shop_categories_id))

    query = (db.shop_categories.Archived == False)
    rows = db(query).select(
        db.shop_categories.id,
        db.shop_categories.Name,
        orderby=db.shop_categories.Name
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

    return_url = URL(vars={'spID':spID})
    # After submitting, check which categories are 'on'
    if form.accepts(request,session):
        # Remove all current records
        query = (db.shop_categories_products.shop_products_id == spID)
        db(query).delete()
        # insert new records for product
        for row in rows:
            if request.vars[unicode(row.id)] == 'on':
                db.shop_categories_products.insert(
                    shop_categories_id = row.id,
                    shop_products_id = spID
                )

        session.flash = T('Saved')
        redirect(return_url)


    back = os_gui.get_button('back', shop_products_get_return_url())
    menu = product_edit_get_menu(request.function, spID)

    return dict(content=form,
                save=os_gui.get_submit_button('MainForm'),
                back=back,
                menu=menu)


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'shop_products_variants'))
def product_variants():
    """
        List Product variants for a product
    """
    from openstudio.os_shop_product import ShopProduct
    from openstudio.os_shop_products_variants import ShopProductsVariants

    spID = request.vars['spID']
    product = ShopProduct(spID)

    response.title = T('Shop')
    response.subtitle = T('Edit product - {product_name}'.format(
        product_name=product.row.Name)
    )
    response.view = 'general/tabs_menu.html'

    variants = ShopProductsVariants(spID)
    content = variants.list_formatted()

    add = ''
    if not product.has_products_set():
        add = os_gui.get_button('add',
                                URL('shop_manage', 'product_variant_add',
                                    vars={'spID':spID}))

    back = os_gui.get_button('back', shop_products_get_return_url())
    menu = product_edit_get_menu(request.function, spID)

    return dict(content=content,
                add=add,
                back=back,
                menu=menu)


def product_variants_get_return_url(spID):
    """
        :return: URL to shop product variants list page
    """
    return URL('shop_manage', 'product_variants',
               vars={'spID':spID})


@auth.requires_login()
def product_variant_add():
    """
        Add a product variant
    """
    from openstudio.os_shop_product import ShopProduct
    from openstudio.os_forms import OsForms

    spID = request.vars['spID']
    product_variant_add_check_products_set(spID)

    product = ShopProduct(spID)

    response.title = T('Shop')
    response.subtitle = T('Edit product - {product_name}'.format(
        product_name=product.row.Name)
    )
    response.view = 'general/tabs_menu.html'

    return_url = product_variants_get_return_url(spID)

    db.shop_products_variants.shop_products_id.default = spID
    os_forms = OsForms()
    result = os_forms.get_crud_form_create(
        db.shop_products_variants,
        return_url,
    )

    form = result['form']
    content = DIV(
        H4(T("Add variant")), BR(),
        form
    )

    back = os_gui.get_button('back', return_url)

    menu = product_edit_get_menu('product_variants', spID)

    return dict(content=content,
                save=result['submit'],
                back=back,
                menu=menu)


def product_variant_add_check_products_set(spID):
    """
    Check if a product has a set, if so, don't allow adding variants.
    :param spID: db.shop_products.id
    :return: None
    """
    from openstudio.os_shop_product import ShopProduct
    product = ShopProduct(spID)
    if product.has_products_set():
        session.flash = T("Unable to add variants for a product with a set")
        redirect(product_variants_get_return_url(spID))


@auth.requires_login()
def product_variant_edit():
    """
        Edit a product variant
    """
    from openstudio.os_forms import OsForms
    from openstudio.os_shop_product import ShopProduct

    spID = request.vars['spID']
    spvID = request.vars['spvID']

    product = ShopProduct(spID)

    response.title = T('Shop')
    response.subtitle = T('Edit product - {product_name}'.format(
        product_name=product.row.Name)
    )
    response.view = 'general/tabs_menu.html'

    return_url = product_variants_get_return_url(spID)

    if product.has_products_set():
        db.shop_products_variants.Name.writable = False

    os_forms = OsForms()
    result = os_forms.get_crud_form_update(
        db.shop_products_variants,
        return_url,
        spvID,
    )

    form = result['form']
    content = DIV(
        H4(T("Edit variant")), BR(),
        form
    )

    back = os_gui.get_button('back', return_url)

    menu = product_edit_get_menu('product_variants', spID)

    return dict(content=content,
                save=result['submit'],
                back=back,
                menu=menu)


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'shop_products_variants'))
def product_variant_sales():
    """
        Edit a product variant
    """
    from openstudio.os_shop_product import ShopProduct
    from openstudio.os_shop_products_variant import ShopProductsVariant
    from openstudio.os_shop_sales import ShopSales

    spID = request.vars['spID']
    spvID = request.vars['spvID']

    product = ShopProduct(spID)
    variant = ShopProductsVariant(spvID)

    response.title = T('Shop')
    response.subtitle = T('Edit product - {product_name}'.format(
        product_name=product.row.Name)
    )
    response.view = 'general/tabs_menu.html'

    return_url = product_variants_get_return_url(spID)

    sales = ShopSales(spvID)
    content = DIV(
        H4(T("Sales history for variant %s" % variant.row.Name)), BR(),
        sales.list_formatted()
    )

    # add = os_gui.get_button('add', URL('shop_manage', 'product_add'))
    back = os_gui.get_button('back', return_url)
    menu = product_edit_get_menu('product_variants', spID)

    return dict(content=content,
                back=back,
                menu=menu)


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('delete', 'shop_products_variants'))
def product_variant_delete():
    """
        Delete variant when not linked to a set
        Disable variant when linked to a set
    """
    from openstudio.os_shop_product import ShopProduct
    from openstudio.os_shop_products_variant import ShopProductsVariant

    spID = request.vars['spID']
    spvID = request.vars['spvID']

    product = ShopProduct(spID)
    if product.has_products_set():
        variant = ShopProductsVariant(spvID)
        variant.disable()
        session.flash = T('Disabled variant')
    else:
        query = (db.shop_products_variants.id == spvID)
        db(query).delete()
        session.flash = T('Deleted variant')

    redirect(product_variants_get_return_url(spID))


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'shop_products_variants'))
def product_variant_set_default():
    """
        Set product variant as default
    """
    from openstudio.os_shop_products_variant import ShopProductsVariant

    spID = request.vars['spID']
    spvID = request.vars['spvID']

    variant = ShopProductsVariant(spvID)
    variant.set_default()

    redirect(product_variants_get_return_url(spID))


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('update', 'shop_products'))
def product_variant_enable():
    """
         Enable a product variant
    """
    from openstudio.os_shop_products_variant import ShopProductsVariant

    spID = request.vars['spID']
    spvID = request.vars['spvID']

    variant = ShopProductsVariant(spvID)
    variant.enable()

    session.flash = T('Enabled variant')
    redirect(product_variants_get_return_url(spID))


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'shop_products_sets'))
def products_sets():
    """
        List shop product_sets
    """
    from openstudio.os_shop_products_sets import ShopProductsSets
    from openstudio.tools import OsSession

    response.title = T('Shop')
    response.subtitle = T('Catalog')
    response.view = 'general/tabs_menu.html'

    product_sets = ShopProductsSets()
    content = product_sets.list_formatted()

    add = os_gui.get_button('add', URL('shop_manage', 'products_set_add'))
    menu = catalog_get_menu(request.function)

    return dict(content=content,
                add=add,
                menu=menu)


def shop_products_sets_get_return_url(var=None):
    """
        :return: URL to shop product_sets list page
    """
    return URL('shop_manage', 'products_sets')


def shop_products_sets_options_get_return_url(shop_products_sets_id):
    """
        :return: URL to shop products_sets_options list
    """
    return URL('shop_manage', 'products_set_options',
               vars={'spsID':shop_products_sets_id})


@auth.requires_login()
def products_set_add():
    """
        Add a new product_set
    """
    from openstudio.os_forms import OsForms
    response.title = T('Shop')
    response.subtitle = T('Catalog')
    response.view = 'general/tabs_menu.html'

    return_url = shop_products_sets_get_return_url()

    os_forms = OsForms()
    result = os_forms.get_crud_form_create(
        db.shop_products_sets,
        return_url,
    )

    form = result['form']
    back = os_gui.get_button('back', return_url)

    content = DIV(
        H4(T('Add product set')),
        form
    )

    menu = catalog_get_menu('products_sets')

    return dict(content=content,
                save=result['submit'],
                back=back,
                menu=menu)


@auth.requires_login()
def products_set_edit():
    """
        Edit a product_set
        request.vars['spsID'] is expected to be db.shop_product_sets.id
    """
    from openstudio.os_forms import OsForms

    response.title = T('Shop')
    response.subtitle = T('Catalog')
    response.view = 'general/tabs_menu.html'
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

    content = DIV(
        H4(T('Edit product set')),
        form
    )

    menu = catalog_get_menu('products_sets')

    return dict(content=content,
                save=result['submit'],
                back=back,
                menu=menu)


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
    from openstudio.os_shop_products_sets_options import ShopProductsSetsOptions
    response.title = T('Shop')
    response.subtitle = T('Catalog')
    response.view = 'general/tabs_menu.html'

    spsID = request.vars['spsID']
    products_set = db.shop_products_sets(spsID)

    spso = ShopProductsSetsOptions(spsID,
                                   URL(request.function,
                                       vars={'spsID': spsID}))
    content = DIV(
        H4(T("Product set options"), ': ',
           XML('<small>' + products_set.Name + '</small>')),
        spso.list_formatted()
    )
    back = os_gui.get_button('back',
                             shop_products_sets_get_return_url())
    menu = catalog_get_menu('products_sets')

    return dict(content=content,
                back=back,
                menu=menu)


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('delete', 'shop_products_sets_options'))
def products_sets_options_delete():
    """
        Delete products sets options value
    """
    spsoID = request.vars['spsoID']
    row = db.shop_products_sets_options(spsoID)
    spsID = row.shop_products_sets_id

    query = (db.shop_products_sets_options.id == spsoID)
    db(query).delete()

    session.flash = T('Deleted option')

    redirect(shop_products_sets_options_get_return_url(spsID))


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('delete', 'shop_products_sets_options_values'))
def products_sets_options_value_delete():
    """
        Delete products sets options value
    """
    spsovID = request.vars['spsovID']

    spsov_row = db.shop_products_sets_options_values(spsovID)
    spso_row = db.shop_products_sets_options(
        spsov_row.shop_products_sets_options_id)
    spsID = spso_row.shop_products_sets_id

    query = (db.shop_products_sets_options_values.id == spsovID)
    db(query).delete()

    redirect(shop_products_sets_options_get_return_url(spsID))


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'shop_categories'))
def categories():
    """
        List shop categories
    """
    from openstudio.os_shop_categories import ShopCategories
    from openstudio.tools import OsSession

    response.title = T('Shop')
    response.subtitle = T('Catalog')
    response.view = 'general/tabs_menu.html'

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
    menu = catalog_get_menu(request.function)

    return dict(content=content,
                add=add,
                menu=menu,
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
    from openstudio.os_forms import OsForms
    response.title = T('Shop')
    response.subtitle = T('Catalog')
    response.view = 'general/tabs_menu.html'

    return_url = shop_categories_get_return_url()

    os_forms = OsForms()
    result = os_forms.get_crud_form_create(
        db.shop_categories,
        return_url,
    )

    form = result['form']
    back = os_gui.get_button('back', return_url)
    menu = catalog_get_menu('categories')

    content = DIV(
        H4(T('Add category')),
        form
    )

    return dict(content=content,
                save=result['submit'],
                back=back,
                menu=menu)


@auth.requires_login()
def category_edit():
    """
        Edit a category
        request.vars['scID'] is expected to be db.shop_categories.id
    """
    from openstudio.os_forms import OsForms

    response.title = T('Shop')
    response.subtitle = T('Catalog')
    response.view = 'general/tabs_menu.html'
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
    menu = catalog_get_menu('categories')

    content = DIV(
        H4(T('Edit category')),
        form
    )

    return dict(content=content,
                save=result['submit'],
                back=back,
                menu=menu)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('update', 'shop_categories'))
def category_archive():
    """
        Archive a category
        request.vars[scID] is expected to be in db.shop_categories.id
        :return: None
    """
    from openstudio.tools import OsArchiver

    archiver = OsArchiver()
    archiver.archive(
        db.shop_categories,
        request.vars['scID'],
        T('Unable to (un)archive category'),
        shop_categories_get_return_url()
    )


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'shop_brands'))
def brands():
    """
        List shop brands
    """
    from openstudio.os_shop_brands import ShopBrands
    from openstudio.tools import OsSession

    response.title = T('Shop')
    response.subtitle = T('Catalog')
    response.view = 'general/tabs_menu.html'

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
    menu = catalog_get_menu(request.function)

    return dict(content=content,
                add=add,
                menu = menu,
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
    from openstudio.os_forms import OsForms
    response.title = T('Shop')
    response.subtitle = T('Catalog')
    response.view = 'general/tabs_menu.html'

    return_url = shop_brand_get_return_url()

    os_forms = OsForms()
    result = os_forms.get_crud_form_create(
        db.shop_brands,
        return_url,
    )

    form = result['form']
    back = os_gui.get_button('back', return_url)
    menu = catalog_get_menu('brands')

    content = DIV(
        H4(T('Add brand')),
        form
    )

    return dict(content=content,
                save=result['submit'],
                back=back,
                menu=menu)


@auth.requires_login()
def brand_edit():
    """
        Edit a brand
        request.vars['sbID'] is expected to be db.shop_brands.id
    """
    from openstudio.os_forms import OsForms

    response.title = T('Shop')
    response.subtitle = T('Catalog')
    response.view = 'general/tabs_menu.html'
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
    menu = catalog_get_menu('brands')

    content = DIV(
        H4(T('Edit brand')),
        form
    )

    return dict(content=content,
                save=result['submit'],
                back=back,
                menu=menu)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('update', 'shop_brands'))
def brand_archive():
    """
        Archive a brand
        request.vars[sbID] is expected to be in db.shop_brands.id
        :return: None
    """
    from openstudio.tools import OsArchiver

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
    from openstudio.os_shop_suppliers import ShopSuppliers
    from openstudio.tools import OsSession

    response.title = T('Shop')
    response.subtitle = T('Catalog')
    response.view = 'general/tabs_menu.html'

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
    menu = catalog_get_menu(request.function)

    return dict(content=content,
                add=add,
                header_tools=archive_buttons,
                menu=menu)


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
    from openstudio.os_forms import OsForms
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
    from openstudio.os_forms import OsForms

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
    from openstudio.tools import OsArchiver

    archiver = OsArchiver()
    archiver.archive(
        db.shop_suppliers,
        request.vars['supID'],
        T('Unable to (un)archive supplier'),
        shop_supplier_get_return_url()
    )


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'shop_sales'))
def sales():
    """
        List products
    """
    from openstudio.os_shop_sales import ShopSales

    response.title = T('Shop')
    response.subtitle = T('Catalog')
    response.view = 'general/tabs_menu.html'

    sales = ShopSales()
    content = sales.list_formatted()


    # add = os_gui.get_button('add', URL('shop_manage', 'product_add'))
    menu = catalog_get_menu(request.function)

    return dict(content=content,
                menu=menu)
