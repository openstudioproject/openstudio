# -*- coding: utf-8 -*-
#!/usr/bin/env python

'''
    py.test test cases to test the schedule controller (schedule.py)
'''

from gluon.contrib.populate import populate
from populate_os_tables import prepare_shifts
from populate_os_tables import prepare_shifts_and_classes_with_holiday

def test_holidays_index(client, web2py):
    '''
        Is the index page showing?
    '''
    url = '/schedule/holidays'
    client.get(url)
    assert client.status == 200
    assert 'Holidays' in client.text

def test_holiday_add(client, web2py):
    '''
        Can we add a holiday?
    '''
    populate(web2py.db.school_locations, 2)

    url = '/schedule/holiday_add'
    client.get(url)
    assert client.status == 200
    assert 'New holiday' in client.text

    data = dict(Description='Kerstvakantie',
                Startdate='2014-12-20',
                Enddate='2014-12-25',
                Classes=True)
    client.post(url, data=data)
    assert client.status == 200

    assert 'To which locations does this holiday apply?' in client.text # verify redirection

    url = '/schedule/holiday_edit_locations?shID=1'
    client.get(url)

    loc_data = {'1':'on'}
    client.post(url, data=loc_data)
    assert client.status == 200

    assert 'Holidays' in client.text
    assert data['Description'] in client.text # verify redirection
    assert web2py.db(web2py.db.school_holidays).count() == 1
    assert web2py.db(web2py.db.school_holidays_locations).count() == 1


def test_holiday_edit(client, web2py):
    '''
        Can we edit a holiday?
    '''
    populate(web2py.db.school_locations, 2)
    web2py.db.school_holidays.insert(
        Description = 'test',
        Startdate = '2014-01-01',
        Enddate = '2014-12-12',
        Classes=True)
    web2py.db.commit()
    assert web2py.db(web2py.db.school_holidays).count() == 1

    url = '/schedule/holiday_edit/1'
    client.get(url)
    assert client.status == 200
    assert 'Edit holiday' in client.text

    data = dict(id=1,
                Description='Kerstvakantie',
                Startdate='2014-12-20',
                Enddate='2014-12-25',
                Classes=True)
    client.post(url, data=data)
    assert client.status == 200

    assert 'Holidays' in client.text # verify redirection
    assert data['Description'] in client.text

    assert web2py.db(web2py.db.school_holidays).count() > 0


def test_holiday_edit_locations_cancel_bookings_and_refund_credits(client, web2py):
    '''
        Are bookings cancelled and credits returned when editing a holiday?
    '''
    from populate_os_tables import prepare_classes

    url = '/user/login'
    client.get(url)
    assert client.status == 200

    prepare_classes(web2py, credits=True)

    populate(web2py.db.school_locations, 2)
    shID = web2py.db.school_holidays.insert(
        Description='test',
        Startdate='2014-01-01',
        Enddate='2014-12-31',
        Classes=True
    )

    web2py.db.commit()
    assert web2py.db(web2py.db.school_holidays).count() == 1

    url = '/schedule/holiday_edit_locations?shID=' + str(shID)
    client.get(url)
    assert client.status == 200
    assert 'Holiday locations' in client.text

    data = {'1':'on',
            '2':'on'}
    client.post(url, data=data)
    assert client.status == 200

    assert 'Holidays' in client.text  # verify redirection

    caID = 3
    # Check status
    clatt = web2py.db.classes_attendance(caID)
    assert clatt.BookingStatus == 'cancelled'

    # Check credit mutation removed
    query = (web2py.db.customers_subscriptions_credits.id > 0)
    assert web2py.db(query).count() == 1


def test_staff_holidays(client, web2py):
    '''
        Check if we get a  list of teacher holidays
    '''
    url = '/schedule/staff_holidays'
    client.get(url)
    assert client.status == 200
    assert 'Staff holidays' in client.text


def test_staff_holidays_add(client, web2py):
    '''
        Can we add a holiday?
    '''
    # call populate_classes so we have some teachers in the db
    prepare_shifts(web2py)
    url = '/schedule/staff_holiday_add'
    client.get(url)
    assert client.status == 200

    data = { 'teachers_id' : 1001,
             'Startdate'   : '2014-01-01',
             'Enddate'     : '2014-02-01',
             'Note'        : 'Watermelon' }
    client.post(url, data=data)
    assert client.status == 200
    assert 'Watermelon' in client.text


def test_staff_holidays_edit(client, web2py):
    '''
        Can we edit a holiday?
    '''
    # call prepare so we have some customers with employee boolean in the db
    prepare_shifts(web2py)

    web2py.db.teachers_holidays.insert(
        auth_teacher_id = 1001,
        Startdate = '2014-01-01',
        Enddate = '2014-01-31',
        Note = 'Pineapple')

    web2py.db.commit()

    url = '/schedule/staff_holiday_edit?sthID=1'
    client.get(url)
    assert client.status == 200

    data = { 'id'              : 1,
             'auth_teacher_id' : 2,
             'Startdate'       : '2014-01-01',
             'Enddate'         : '2014-02-01',
             'Note'            : 'Watermelon' }
    client.post(url, data=data)
    assert client.status == 200
    assert 'Watermelon' in client.text


#TODO: fix this test
def test_teacher_holidays_choose_status(client, web2py):
    '''
        Can we change the status of the classes in a holiday of a teacher?
    '''
    prepare_shifts_and_classes_with_holiday(web2py)

    url = '/schedule/staff_holidays_choose_status?sthID=1'
    client.get(url)
    assert client.status == 200

    data = {'status':'open'}
    client.post(url, data=data)
    assert client.status == 200
    assert web2py.db(web2py.db.classes_otc.Status == 'open').count() == 4

    client.get(url)
    assert client.status == 200

    data = {'status':'cancelled'}
    client.post(url, data=data)
    assert client.status == 200
    assert web2py.db(web2py.db.classes_otc.Status == 'cancelled').count() == 4

    client.get(url)
    assert client.status == 200

    data = {'status':'normal'}
    client.post(url, data=data)
    assert client.status == 200
    assert web2py.db(web2py.db.classes_otc.Status == 'open').count() == 0
    assert web2py.db(web2py.db.classes_otc.Status == 'cancelled').count() == 0