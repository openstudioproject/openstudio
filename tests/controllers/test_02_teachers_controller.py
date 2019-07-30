# -*- coding: utf-8 -*-
"""
    py.test test cases to test the staff controller (staff.py)
"""

import datetime

from gluon.contrib.populate import populate
from populate_os_tables import populate_teachers_payment_attendance_lists
from populate_os_tables import populate_teachers_payment_attendance_lists_school_classtypes
from populate_os_tables import populate_teachers_payment_attendance_lists_rates
from populate_os_tables import populate_auth_user_teachers
from populate_os_tables import populate_auth_user_teachers_fixed_rate_default
from populate_os_tables import populate_auth_user_teachers_fixed_rate_class_1
from populate_os_tables import populate_auth_user_teachers_travel
from populate_os_tables import prepare_classes
from populate_os_tables import populate_customers
from populate_os_tables import populate_tax_rates


def next_weekday(d, weekday):
    """
        Function to find next weekday after given date
    """
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)


def test_payment_attendance_lists(client, web2py):
    """
    Is the list showing?
    """
    populate_teachers_payment_attendance_lists(web2py)

    url = '/teachers/payment_attendance_lists'
    client.get(url)
    assert client.status == 200

    tpal = web2py.db.teachers_payment_attendance_lists(1)
    assert tpal.Name in client.text


def test_payment_attendance_list_add(client, web2py):
    """
    Can we add a list?
    """
    populate_tax_rates(web2py)

    url = '/teachers/payment_attendance_list_add'
    client.get(url)
    assert client.status == 200

    data = {
        "Name": "Big list",
        "tax_rates_id": 1
    }

    client.post(url, data=data)
    assert client.status == 200

    tpal = web2py.db.teachers_payment_attendance_lists(1)
    assert data['Name'] == tpal.Name


def test_payment_attendance_list_edit(client, web2py):
    """
    Can we edit a list?
    """
    populate_teachers_payment_attendance_lists(web2py)

    url = '/teachers/payment_attendance_list_edit?tpalID=1'
    client.get(url)
    assert client.status == 200

    data = {
        "id": 1,
        "Name": "Big list",
        "tax_rates_id": 1
    }

    client.post(url, data=data)
    assert client.status == 200

    tpal = web2py.db.teachers_payment_attendance_lists(1)
    assert data['Name'] == tpal.Name


def test_payment_attendance_list_archive(client, web2py):
    """
    Is the list showing?
    """
    populate_teachers_payment_attendance_lists(web2py)

    url = '/teachers/payment_attendance_list_archive?tpalID=1'
    client.get(url)
    assert client.status == 200

    tpal = web2py.db.teachers_payment_attendance_lists(1)
    assert tpal.Archived == True


def test_payment_attendance_list_rates(client, web2py):
    """
    Is the list showing?
    """
    populate_teachers_payment_attendance_lists(web2py)

    url = '/teachers/payment_attendance_list_rates?tpalID=1'
    client.get(url)
    assert client.status == 200

    tpalr = web2py.db.teachers_payment_attendance_lists_rates(1)
    assert format(tpalr.Rate, '.2f') in client.text


def test_payment_attendance_list_rates_add(client, web2py):
    """
    Can we add a rate to the list?
    """
    populate_teachers_payment_attendance_lists(web2py, with_rates=False)

    url = "/teachers/payment_attendance_list_rates?tpalID=1"
    client.get(url)
    assert client.status == 200

    data = {
        'Rate': 20.5
    }

    client.post(url, data=data)
    assert client.status == 200

    tpalr = web2py.db.teachers_payment_attendance_lists_rates(1)
    assert tpalr.Rate == data['Rate']


def test_payment_attendance_list_rates_add_increase_attendanceNR(client, web2py):
    """
    Can we add a rate to the list?
    """
    populate_teachers_payment_attendance_lists(web2py)

    query = (web2py.db.teachers_payment_attendance_lists_rates.teachers_payment_attendance_lists_id == 1)
    count = web2py.db(query).count()

    url = "/teachers/payment_attendance_list_rates?tpalID=1"
    client.get(url)
    assert client.status == 200

    data = {
        'Rate': 20.5
    }

    client.post(url, data=data)
    assert client.status == 200

    new_count = count_rates = web2py.db(query).count()
    new_id = count + 1
    tpalr = web2py.db.teachers_payment_attendance_lists_rates(new_id)
    assert tpalr.AttendanceCount == new_count


def test_payment_attendance_list_rate_edit(client, web2py):
    """
    Can we add a rate to the list?
    """
    populate_teachers_payment_attendance_lists(web2py)

    url = "/teachers/payment_attendance_list_rate_edit?tpalID=1&tpalrID=1"
    client.get(url)
    assert client.status == 200

    data = {
        'id': 1,
        'Rate': 20.5
    }

    client.post(url, data=data)
    assert client.status == 200

    tpalr = web2py.db.teachers_payment_attendance_lists_rates(1)
    assert tpalr.Rate == data['Rate']


def test_payment_attendance_list_rate_delete(client, web2py):
    """
    Can we delete a rate from a list?
    """
    populate_teachers_payment_attendance_lists(web2py)

    query = (web2py.db.teachers_payment_attendance_lists_rates.teachers_payment_attendance_lists_id == 1)
    count = web2py.db(query).count()

    url = "/teachers/payment_attendance_list_rate_delete?tpalID=1&tpalrID=1"
    client.get(url)
    assert client.status == 200

    count_after = web2py.db(query).count()
    assert count_after == count - 1


def test_payment_attendance_list_classtypes(client, web2py):
    """
    List classtypes for attendance payment list?
    """
    populate_teachers_payment_attendance_lists_school_classtypes(web2py)

    url = "/teachers/payment_attendance_list_classtypes?tpalID=1"
    client.get(url)
    assert client.status == 200

    assert 'input checked="checked" name="1" type="checkbox" value="on"' in client.text


def test_payment_attendance_list_classtypes_save(client, web2py):
    """
    List classtypes for attendance payment list?
    """
    populate_teachers_payment_attendance_lists_school_classtypes(web2py)

    url = "/teachers/payment_attendance_list_classtypes?tpalID=1"
    client.get(url)
    assert client.status == 200

    data = {
        '1': 'on'
    }

    client.post(url, data=data)
    assert client.status == 200

    tpalsc = web2py.db.teachers_payment_attendance_lists_school_classtypes(4)
    assert tpalsc.school_classtypes_id == 1
    assert tpalsc.teachers_payment_attendance_lists_id == 1

    assert web2py.db(web2py.db.teachers_payment_attendance_lists_school_classtypes).count() == 1


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

    url = '/teachers/payment_fixed_rate_class_add?teID=2&date=' + str(next_monday)
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
    populate_auth_user_teachers_travel(web2py)

    next_monday = next_weekday(datetime.date.today(), 0)

    url = '/teachers/payment_fixed_rate?teID=2'
    client.get(url)
    assert client.status == 200

    default_rate = web2py.db.teachers_payment_fixed_rate_default(1)
    assert str(default_rate.ClassRate) in client.text

    class_rate = web2py.db.teachers_payment_fixed_rate_class(1)
    assert str(class_rate.ClassRate) in client.text


def test_payment_travel(client, web2py):
    """
        Check display of travel allowance for a teacher
    """
    prepare_classes(web2py)
    populate_auth_user_teachers_fixed_rate_default(web2py)
    populate_auth_user_teachers_fixed_rate_class_1(web2py)
    populate_auth_user_teachers_travel(web2py)

    next_monday = next_weekday(datetime.date.today(), 0)

    url = '/teachers/payment_travel?teID=2'
    client.get(url)
    assert client.status == 200

    travel_allowance = web2py.db.teachers_payment_travel(1)
    assert str(travel_allowance.TravelAllowance) in client.text


def test_payment_travel_add(client, web2py):
    """
        Can we add travel allowance for a location?
    """
    prepare_classes(web2py)

    url = '/teachers/payment_travel_add?teID=2'
    client.get(url)
    assert client.status == 200

    data = {
        'school_locations_id': 1,
        'TravelAllowance': '30232',
        'tax_rates_id': 1
    }

    client.post(url, data=data)
    assert client.status == 200

    row = web2py.db.teachers_payment_travel(1)
    assert row.TravelAllowance == float(data['TravelAllowance'])
    assert row.tax_rates_id == data['tax_rates_id']
    assert row.school_locations_id == 1


def test_payment_travel_edit(client, web2py):
    """
        Can we add travel allowance for a location?
    """
    prepare_classes(web2py)
    populate_auth_user_teachers_travel(web2py)

    url = '/teachers/payment_travel_edit?teID=2&tpfrtID=1'
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

    row = web2py.db.teachers_payment_travel(1)
    assert row.TravelAllowance == float(data['TravelAllowance'])
    assert row.tax_rates_id == data['tax_rates_id']
    assert row.school_locations_id == 1


def test_payment_travel_delete(client, web2py):
    """
        Can we delete a travel allowance for a location?
    """
    prepare_classes(web2py)
    populate_auth_user_teachers_travel(web2py)

    url = '/teachers/payment_travel_delete?teID=2&tpfrtID=1'
    client.get(url)
    assert client.status == 200

    query = (web2py.db.teachers_payment_travel.id > 0)
    assert web2py.db(query).count() == 0


def test_teacher_delete(client, web2py):
    """
        Can we remove the teacher status from a customer?
    """
    populate_customers(web2py)

    row = web2py.db.auth_user(1001)
    row.teacher = True
    row.update_record()

    web2py.db.commit()

    url = '/teachers/delete?uID=1001'
    client.get(url)
    assert client.status == 200

    row = web2py.db.auth_user(1001)
    assert row.teacher == False

