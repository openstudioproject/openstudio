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

