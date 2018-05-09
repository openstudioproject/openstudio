# -*- coding: utf-8 -*-
"""
    py.test test cases to test the staff controller (staff.py)
"""

import datetime

from gluon.contrib.populate import populate
from populate_os_tables import populate_auth_user_teachers
from populate_os_tables import populate_auth_user_teachers_fixed_rate_default
from populate_os_tables import populate_auth_user_teachers_fixed_rate_class_1
from populate_os_tables import populate_auth_user_teachers_fixed_rate_travel
from populate_os_tables import prepare_classes


def next_weekday(d, weekday):
    """
        Function to find next weekday after given date
    """
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)


def test_payment_fixed_rate_default_add(client, web2py):
    """
        Can we add a default rate
    """
    populate_auth_user_teachers(web2py)

    url = '/teachers/payment_fixed_rate_default?teID=2'
    client.get(url)
    assert client.status == 200

    data = {
        'ClassRate': '30',
        'tax_rates_id': 1
    }

    client.post(url, data=data)
    assert client.status == 200

    row = web2py.db.teachers_payment_fixed_rate_default(1)
    assert row.ClassRate == float(data['ClassRate'])
    assert row.tax_rates_id == data['tax_rates_id']
    assert row.auth_teacher_id == 2


def test_payment_fixed_rate_default_edit(client, web2py):
    """
        Can we add a default rate
    """
    prepare_classes(web2py)
    populate_auth_user_teachers_fixed_rate_default(web2py)

    url = '/teachers/payment_fixed_rate_default?teID=2'
    client.get(url)
    assert client.status == 200

    data = {
        'id': 1,
        'ClassRate': '30232',
        'tax_rates_id': 1
    }

    client.post(url, data=data)
    assert client.status == 200

    row = web2py.db.teachers_payment_fixed_rate_default(1)
    assert row.ClassRate == float(data['ClassRate'])
    assert row.tax_rates_id == data['tax_rates_id']
    assert row.auth_teacher_id == 2


def test_payment_fixed_rate_class_add_list_classes(client, web2py):
    """
        Can we add a class specific rate
    """
    prepare_classes(web2py)

    next_monday = next_weekday(datetime.date.today(), 0)

    url = '/teachers/payment_fixed_rate_class_add?teID=2&date=' + unicode(next_monday)
    client.get(url)
    assert client.status == 200

    assert 'Add class payment rate' in client.text
    assert 'Set rate' in client.text


def test_payment_fixed_rate_class_add(client, web2py):
    """
        Can we add a class specific rate
    """
    prepare_classes(web2py)

    next_monday = next_weekday(datetime.date.today(), 0)

    url = '/teachers/payment_fixed_rate_class?teID=2&clsID=1'
    client.get(url)
    assert client.status == 200

    data = {
        'id': 1,
        'ClassRate': '30232',
        'tax_rates_id': 1
    }

    client.post(url, data=data)
    assert client.status == 200

    row = web2py.db.teachers_payment_fixed_rate_class(1)
    assert row.ClassRate == float(data['ClassRate'])
    assert row.tax_rates_id == data['tax_rates_id']
    assert row.classes_id == 1
    assert row.auth_teacher_id == 2


def test_payment_fixed_rate_class_edit(client, web2py):
    """
        Can we edit a class specific rate
    """
    prepare_classes(web2py)
    populate_auth_user_teachers_fixed_rate_class_1(web2py)

    next_monday = next_weekday(datetime.date.today(), 0)

    url = '/teachers/payment_fixed_rate_class?teID=2&clsID=1'
    client.get(url)
    assert client.status == 200

    data = {
        'id': 1,
        'ClassRate': '30232',
        'tax_rates_id': 1
    }

    client.post(url, data=data)
    assert client.status == 200

    row = web2py.db.teachers_payment_fixed_rate_class(1)
    assert row.ClassRate == float(data['ClassRate'])
    assert row.tax_rates_id == data['tax_rates_id']
    assert row.classes_id == 1
    assert row.auth_teacher_id == 2


def test_payment_fixed_rate_class_delete(client, web2py):
    """
        Can we delete a class specific rate
    """
    prepare_classes(web2py)
    populate_auth_user_teachers_fixed_rate_class_1(web2py)

    url = '/teachers/payment_fixed_rate_class_delete?teID=2&tpfrcID=1'
    client.get(url)
    assert client.status == 200

    query = (web2py.db.teachers_payment_fixed_rate_class.id > 0)
    assert web2py.db(query).count() == 0


def test_payment_fixed_rate(client, web2py):
    """
        Check display of default and class specific fixed rates
    """
    prepare_classes(web2py)
    populate_auth_user_teachers_fixed_rate_default(web2py)
    populate_auth_user_teachers_fixed_rate_class_1(web2py)
    populate_auth_user_teachers_fixed_rate_travel(web2py)

    next_monday = next_weekday(datetime.date.today(), 0)

    url = '/teachers/payment_fixed_rate?teID=2'
    client.get(url)
    assert client.status == 200

    default_rate = web2py.db.teachers_payment_fixed_rate_default(1)
    assert unicode(default_rate.ClassRate) in client.text.decode('utf-8')

    class_rate = web2py.db.teachers_payment_fixed_rate_class(1)
    assert unicode(class_rate.ClassRate) in client.text.decode('utf-8')

    travel_allowance = web2py.db.teachers_payment_fixed_rate_travel(1)
    assert unicode(travel_allowance.TravelAllowance) in client.text.decode('utf-8')


def test_payment_fixed_rate_travel_add(client, web2py):
    """
        Can we add travel allowance for a location?
    """
    prepare_classes(web2py)

    url = '/teachers/payment_fixed_rate_travel_add?teID=2'
    client.get(url)
    assert client.status == 200

    data = {
        'school_locations_id': 1,
        'TravelAllowance': '30232',
        'tax_rates_id': 1
    }

    client.post(url, data=data)
    assert client.status == 200

    row = web2py.db.teachers_payment_fixed_rate_travel(1)
    assert row.TravelAllowance == float(data['TravelAllowance'])
    assert row.tax_rates_id == data['tax_rates_id']
    assert row.school_locations_id == 1


def test_payment_fixed_rate_travel_edit(client, web2py):
    """
        Can we add travel allowance for a location?
    """
    prepare_classes(web2py)
    populate_auth_user_teachers_fixed_rate_travel(web2py)

    url = '/teachers/payment_fixed_rate_travel_edit?teID=2&tpfptID=1'
    client.get(url)
    assert client.status == 200

    data = {
        'id': 1,
        'school_locations_id': 1,
        'TravelAllowance': '30232',
        'tax_rates_id': 1
    }

    client.post(url, data=data)
    assert client.status == 200

    row = web2py.db.teachers_payment_fixed_rate_travel(1)
    assert row.TravelAllowance == float(data['TravelAllowance'])
    assert row.tax_rates_id == data['tax_rates_id']
    assert row.school_locations_id == 1


def test_payment_fixed_rate_travel_delete(client, web2py):
    """
        Can we delete a travel allowance for a location?
    """
    prepare_classes(web2py)
    populate_auth_user_teachers_fixed_rate_travel(web2py)

    url = '/teachers/payment_fixed_rate_travel_delete?teID=2&tpfptID=1'
    client.get(url)
    assert client.status == 200

    query = (web2py.db.teachers_payment_fixed_rate_travel.id > 0)
    assert web2py.db(query).count() == 0

