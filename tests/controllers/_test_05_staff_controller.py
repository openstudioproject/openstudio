# -*- coding: utf-8 -*-
'''
    py.test test cases to test the staff controller (staff.py)
'''

from gluon.contrib.populate import populate
from populate_os_tables import populate_customers
from populate_os_tables import prepare_shifts

def test_shift_add(client, web2py):
    '''
        Can we add a shift?
    '''
    populate_customers(web2py, nr_of_customers=2, employee=True)
    populate(web2py.db.school_locations, 1)
    populate(web2py.db.school_shifts, 1)

    url = '/staff/shift_add'
    client.get(url)
    assert client.status == 200
    data = dict(school_locations_id='1',
                school_shifts_id='1',
                Week_day='1',
                Starttime='06:00:00',
                Endtime='08:00:00',
                Startdate='2014-01-01',
                )
    client.post(url, data=data)
    assert client.status == 200
    assert "Assign employees" in client.text # check redirection to assign employees page

    url = '/staff/shift_employees_add?shID=1'
    client.get(url)
    assert client.status == 200

    emp_data = {'shifts_id':1,
                'Startdate':data['Startdate'],
                'auth_employee_id':1001}

    client.post(url, data=emp_data)
    assert client.status == 200
    assert 'Edit shift' in client.text # verify redirection

    # move to schedule page and check display of input
    url = '/staff/schedule'
    client.get(url)
    assert client.status == 200

    assert web2py.db(web2py.db.shifts).count() == 1
    location = web2py.db.school_locations(1).Name[:10]
    assert location in client.text


def test_shift_edit(client, web2py):
    '''
        Can we edit a shift?
    '''
    prepare_shifts(web2py)
    assert web2py.db(web2py.db.shifts).count() == 1

    url = '/staff/shift_edit/?shID=1'
    client.get(url)
    assert client.status == 200
    data = dict(id=1,
                school_locations_id='1',
                school_shifts_id='1',
                Week_day='1', # Monday
                Starttime='06:00:00',
                Endtime='12:12:00',
                Startdate='2014-01-01',
                )
    client.post(url, data=data)
    assert client.status == 200
    assert "Edit shift" in client.text

    url = '/staff/schedule'
    client.get(url)
    assert client.status == 200
    assert '12:12' in client.text


def test_shift_employees_add(client, web2py):
    '''
        Can we add employees to a shift?
    '''
    prepare_shifts(web2py)

    url = '/staff/shift_employees_add?shID=1'
    client.get(url)
    assert client.status == 200

    data = {'shifts_id':1,
            'auth_employee_id':1002,
            'Startdate':'2014-01-01'}
    client.post(url, data=data)
    assert client.status == 200

    assert web2py.db(web2py.db.shifts_staff).count() == 2


def test_shift_employees_edit(client, web2py):
    '''
        Can we edit employees assigned to a shift?
    '''
    prepare_shifts(web2py)

    url = '/staff/shift_employees_edit?shsID=1&shID=1&date=2014-01-01'
    client.get(url)
    assert client.status == 200

    data = {'id':1,
            'auth_employee_id':1002,
            'Startdate':'2014-01-01'}
    client.post(url, data=data)
    assert client.status == 200

    query = (web2py.db.shifts_staff.auth_employee_id==data['auth_employee_id'])
    assert web2py.db(query).count() == 1


def test_schedule(client, web2py):
    '''
        Is the schedule showing all things as it should?
    '''
    prepare_shifts(web2py)
    assert web2py.db(web2py.db.shifts).count() == 1

    url = '/staff/schedule'
    client.get(url)
    assert client.status == 200
    assert 'Schedule' in client.text

    url = '/staff/schedule?year=2014&week=2' # we need the second week because the class is on a monday and the in week 1 monday is in december 2013.
    client.get(url)
    assert client.status == 200
    assert 'fa-pencil' in client.text
    assert 'fa-times' in client.text
    location_check = web2py.db.school_locations(1).Name[:10]
    assert location_check in client.text


def test_schedule_otc(client, web2py):
    '''
        Is a change from classes_otc showing in the schedule?
    '''
    prepare_shifts(web2py, with_otc=True)

    url = '/staff/schedule?year=2014&week=2'
    client.get(url)
    assert client.status == 200

    location = web2py.db.school_locations(2).Name.split(' ')[0]
    assert location in client.text

    shift = web2py.db.school_shifts(2).Name.split(' ')[0]
    assert shift in client.text


def test_status_set_open(client, web2py):
    '''
        Can we set the status to open for a shift?
    '''
    prepare_shifts(web2py)

    url = '/staff/shift_edit_on_date?shID=1&date=2014-01-06'
    client.get(url)
    assert client.status == 200

    data = {'Status':'open'}
    client.post(url, data=data)
    assert client.status == 200

    assert web2py.db(web2py.db.shifts_otc).count() == 1

    client.get(url)
    assert client.status == 200
    assert '<option selected="selected" value="open">' in client.text


def test_status_set_cancelled(client, web2py):
    '''
        Can we set the status to cancelled for a shift?
    '''
    prepare_shifts(web2py)

    url = '/staff/shift_edit_on_date?shID=1&date=2014-01-06'
    client.get(url)
    assert client.status == 200

    data = {'Status':'cancelled'}
    client.post(url, data=data)
    assert client.status == 200

    assert web2py.db(web2py.db.shifts_otc).count() == 1

    client.get(url)
    assert client.status == 200
    assert '<option selected="selected" value="cancelled">' in client.text


def test_status_set_sub(client, web2py):
    '''
        Can we add substitute employee for a shift?
    '''
    prepare_shifts(web2py)
    assert web2py.db(web2py.db.shifts).count() == 1

    shID = '1'
    shiftdate = '2014-01-06'
    aueID = 1001

    url = '/staff/shift_edit_on_date?shID=1&date=2014-01-06'
    client.get(url)
    assert client.status == 200

    data = {'auth_employee_id':aueID}
    client.post(url, data=data)
    assert client.status == 200

    assert web2py.db(web2py.db.shifts_otc).count() == 1

    client.get(url)
    assert client.status == 200
    assert '<option selected="selected" value="1001">' in client.text


def test_schedule_weekly_status(client, web2py):
    '''
        Can we set the status of the schedule to 'final' and back to 'open'
    '''
    url = '/staff/schedule?year=2014&week=1'
    client.get(url)
    assert client.status == 200
    assert '<span class="bold">Open</span>' in client.text

    url = '/staff/schedule_set_week_status?status=final'
    client.get(url)
    assert client.status == 200
    assert '<span class="green bold">Final</span>' in client.text

    url = '/staff/schedule_set_week_status?status='
    client.get(url)
    assert client.status == 200
    assert '<span class="bold">Open</span>' in client.text
