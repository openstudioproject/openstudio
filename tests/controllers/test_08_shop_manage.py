# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""py.test test cases to test OpenStudio.
These tests run based on webclient and need web2py server running.
"""

def test_workflow(client, web2py):
    """
        Can we edit the workflow settings?
    """
    url = '/shop_manage/workflow'
    client.get(url)
    assert client.status == 200

    data = {
        'shop_requires_complete_profile': 'on',
        'shop_classes_advance_booking_limit':'22',
        'shop_classes_cancellation_limit':'7',
        'shop_subscriptions_start':'today'
    }

    client.post(url, data=data)
    assert client.status == 200

    # Check that the settings have been saved in the db
    assert web2py.db.sys_properties(Property='shop_requires_complete_profile').PropertyValue == \
           data['shop_requires_complete_profile']
    assert web2py.db.sys_properties(Property='shop_classes_advance_booking_limit').PropertyValue == \
           data['shop_classes_advance_booking_limit']
    assert web2py.db.sys_properties(Property='shop_classes_cancellation_limit').PropertyValue == \
           data['shop_classes_cancellation_limit']
    assert web2py.db.sys_properties(Property='shop_subscriptions_start').PropertyValue == \
           data['shop_subscriptions_start']


def test_products_sets(client, web2py):
    """
        Is the products_sets page listing products_sets?
    """
    from populate_os_tables import populate_shop_products_sets
    populate_shop_products_sets(web2py)

    assert web2py.db(web2py.db.shop_products_sets).count() == 1

    url = '/shop_manage/products_sets'
    client.get(url)
    assert client.status == 200

    products_set = web2py.db.shop_products_sets(1)
    assert products_set.Name in client.text


def test_products_sets_add(client, web2py):
    """
        Can we add a products_set?
    """
    url = '/shop_manage/products_set_add'
    client.get(url)
    assert client.status == 200

    data = {
        'Name': 'Grapefruit',
        'Description': 'Also great as juice'
    }

    client.post(url, data=data)
    assert client.status == 200

    assert web2py.db(web2py.db.shop_products_sets).count() == 1


def test_products_set_edit(client, web2py):
    """
        Can we edit a products_set?
    """
    from populate_os_tables import populate_shop_products_sets
    populate_shop_products_sets(web2py)

    url = '/shop_manage/products_set_edit?spsID=1'
    client.get(url)
    assert client.status == 200

    data = {
        'id': '1',
        'Name': 'Grapefruit',
        'Description': 'Also great as juice'
    }

    client.post(url, data=data)
    assert client.status == 200

    products_set = web2py.db.shop_products_sets(1)
    assert products_set.Name == data['Name']


def test_products_set_delete(client, web2py):
    """
        Can we delete a product set?
    """
    from populate_os_tables import populate_shop_products_sets
    populate_shop_products_sets(web2py)

    url = '/shop_manage/products_set_delete?spsID=1'
    client.get(url)
    assert client.status == 200

    query = (web2py.db.shop_products_sets.id)
    assert web2py.db(query).count() == 0


def test_products_set_options(client, web2py):
    """
        Are options and values in a set listed correctly
    """
    from populate_os_tables import populate_shop_products_sets
    populate_shop_products_sets(web2py,
                                options=True,
                                values=True)

    url = '/shop_manage/products_set_options?spsID=1'
    client.get(url)
    assert client.status == 200

    option = web2py.db.shop_products_sets_options(1)
    value = web2py.db.shop_products_sets_options_values(1)

    assert option.Name in client.text
    assert value.Name in client.text


def test_products_set_options_add(client, web2py):
    """
        Can we add an options?
    """
    from populate_os_tables import populate_shop_products_sets
    populate_shop_products_sets(web2py)

    url = '/shop_manage/products_set_options?spsID=1'
    client.get(url)
    assert client.status == 200

    data = {
        'Name': 'Banana'
    }
    client.post(url, data=data)
    assert client.status == 200

    assert web2py.db(web2py.db.shop_products_sets_options).count() == 1
    assert data['Name'] in client.text


def test_products_set_options_value_add(client, web2py):
    """
        Can we add an option value?
    """
    from populate_os_tables import populate_shop_products_sets
    populate_shop_products_sets(web2py,
                                options=True)

    url = '/shop_manage/products_set_options?spsID=1'
    client.get(url)
    assert client.status == 200

    data = {
        'shop_products_sets_options_id': 1,
        'Name': 'Banana Value',
        '_formname': 'shop_products_sets_options_values/None'
    }
    client.post(url, data=data)
    assert client.status == 200

    assert web2py.db(web2py.db.shop_products_sets_options_values).count() == 1
    assert data['Name'] in client.text


def test_shop_products_sets_options_delete(client, web2py):
    """
        Can we delete an option?
    """
    from populate_os_tables import populate_shop_products_sets
    populate_shop_products_sets(web2py,
                                options=True)

    url = '/shop_manage/shop_products_sets_options_delete?spsoID=1'
    client.get(url)
    assert client.status == 200

    assert web2py.db(web2py.db.shop_products_sets_options).count() == 0


def test_shop_products_sets_options_value_delete(client, web2py):
    """
        Can we delete an option value?
    """
    from populate_os_tables import populate_shop_products_sets
    populate_shop_products_sets(web2py,
                                options=True,
                                values=True)

    url = '/shop_manage/shop_products_sets_options_value_delete?spsovID=1'
    client.get(url)
    assert client.status == 200

    assert web2py.db(web2py.db.shop_products_sets_options_values).count() == 0


def test_brands(client, web2py):
    """
        Is the brands page listing brands?
    """
    from populate_os_tables import populate_shop_brands
    populate_shop_brands(web2py)

    assert web2py.db(web2py.db.shop_brands).count() == 1

    url = '/shop_manage/brands'
    client.get(url)
    assert client.status == 200

    brand = web2py.db.shop_brands(1)
    assert brand.Name in client.text


def test_brand_add(client, web2py):
    """
        Can we add a brand?
    """
    url = '/shop_manage/brand_add'
    client.get(url)
    assert client.status == 200

    data = {
        'Name': 'Grapefruit',
        'Description': 'Also great as juice'
    }

    client.post(url, data=data)
    assert client.status == 200

    assert web2py.db(web2py.db.shop_brands).count() == 1


def test_brand_edit(client, web2py):
    """
        Can we edit a brand?
    """
    from populate_os_tables import populate_shop_brands
    populate_shop_brands(web2py)

    url = '/shop_manage/brand_edit?sbID=1'
    client.get(url)
    assert client.status == 200

    data = {
        'id': '1',
        'Name': 'Grapefruit',
        'Description': 'Also great as juice'
    }

    client.post(url, data=data)
    assert client.status == 200

    brand = web2py.db.shop_brands(1)
    assert brand.Name == data['Name']


def test_brand_archive(client, web2py):
    """
        Can we archive a brand?
    """
    from populate_os_tables import populate_shop_brands
    populate_shop_brands(web2py)

    url = '/shop_manage/brand_archive?sbID=1'
    client.get(url)
    assert client.status == 200

    brand = web2py.db.shop_brands(1)
    assert brand.Archived == True


def test_categories(client, web2py):
    """
        Is the categories page listing categories?
    """
    from populate_os_tables import populate_shop_categories
    populate_shop_categories(web2py)

    assert web2py.db(web2py.db.shop_categories).count() == 1

    url = '/shop_manage/categories'
    client.get(url)
    assert client.status == 200

    category = web2py.db.shop_categories(1)
    assert category.Name in client.text


def test_category_add(client, web2py):
    """
        Can we add a category?
    """
    url = '/shop_manage/category_add'
    client.get(url)
    assert client.status == 200

    data = {
        'Name': 'Grapefruit',
        'Description': 'Also great as juice'
    }

    client.post(url, data=data)
    assert client.status == 200

    assert web2py.db(web2py.db.shop_categories).count() == 1


def test_category_edit(client, web2py):
    """
        Can we edit a category?
    """
    from populate_os_tables import populate_shop_categories
    populate_shop_categories(web2py)

    url = '/shop_manage/category_edit?scID=1'
    client.get(url)
    assert client.status == 200

    data = {
        'id': '1',
        'Name': 'Grapefruit',
        'Description': 'Also great as juice'
    }

    client.post(url, data=data)
    assert client.status == 200

    category = web2py.db.shop_categories(1)
    assert category.Name == data['Name']


def test_category_archive(client, web2py):
    """
        Can we archive a category?
    """
    from populate_os_tables import populate_shop_categories
    populate_shop_categories(web2py)

    url = '/shop_manage/category_archive?scID=1'
    client.get(url)
    assert client.status == 200

    category = web2py.db.shop_categories(1)
    assert category.Archived == True


def test_suppliers(client, web2py):
    """
        Is the suppliers page listing suppliers?
    """
    from populate_os_tables import populate_shop_suppliers
    populate_shop_suppliers(web2py)

    assert web2py.db(web2py.db.shop_suppliers).count() == 1

    url = '/shop_manage/suppliers'
    client.get(url)
    assert client.status == 200

    supplier = web2py.db.shop_suppliers(1)
    assert supplier.Name in client.text


def test_supplier_add(client, web2py):
    """
        Can we add a supplier?
    """
    url = '/shop_manage/supplier_add'
    client.get(url)
    assert client.status == 200

    data = {
        'Name': 'Grapefruit',
        'Description': 'Also great as juice'
    }

    client.post(url, data=data)
    assert client.status == 200

    assert web2py.db(web2py.db.shop_suppliers).count() == 1


def test_supplier_edit(client, web2py):
    """
        Can we edit a supplier?
    """
    from populate_os_tables import populate_shop_suppliers
    populate_shop_suppliers(web2py)

    url = '/shop_manage/supplier_edit?supID=1'
    client.get(url)
    assert client.status == 200

    data = {
        'id': '1',
        'Name': 'Grapefruit',
        'Description': 'Also great as juice'
    }

    client.post(url, data=data)
    assert client.status == 200

    supplier = web2py.db.shop_suppliers(1)
    assert supplier.Name == data['Name']


def test_supplier_archive(client, web2py):
    """
        Can we archive a supplier?
    """
    from populate_os_tables import populate_shop_suppliers
    populate_shop_suppliers(web2py)

    url = '/shop_manage/supplier_archive?supID=1'
    client.get(url)
    assert client.status == 200

    supplier = web2py.db.shop_suppliers(1)
    assert supplier.Archived == True
    