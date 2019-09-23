#!/usr/bin/env python

'''
    py.test test cases to test OpenStudio.
    These tests run based on webclient and need web2py server running.
'''

import datetime

from gluon.contrib.populate import populate

from populate_os_tables import populate_customers
from populate_os_tables import populate_customers_with_subscriptions
from populate_os_tables import prepare_classes


def test_selfcheckin_index(client, web2py):
    '''
        Is the page that lists locations working?
    '''
    populate(web2py.db.school_locations, 1)

    url = '/selfcheckin/index'
    client.get(url)
    assert client.status == 200

    location = web2py.db.school_locations(1)
    assert location.Name in client.text

def test_selfcheckin_classes(client, web2py):
    '''
        Is the page listing classes working?
    '''
    # This gives a class on Monday
    prepare_classes(web2py)

    # For the other days of the week
    for i in range(2, 8):
        web2py.db.classes.insert(school_locations_id=1,
                                 school_classtypes_id=1,
                                 Week_day=i,
                                 Starttime='06:00:00',
                                 Endtime='09:00:00',
                                 Startdate='2014-01-01',
                                 Enddate='2999-01-01',
                                 Maxstudents=20
                                 )
    web2py.db.commit()

    url = '/selfcheckin/classes?locID=1'
    client.get(url)
    assert client.status == 200

    classtype = web2py.db.school_classtypes(1)
    assert classtype.Name in client.text

def test_selfcheckin_checkin_impossible_when_full(client, web2py):
    '''
        Test to verify a full message is displayed & check-in buttons are
        disabled when a class has no more spaces
    '''
    # This gives a class on Monday
    prepare_classes(web2py)

    today = datetime.date.today()
    # For the other days of the week
    for i in range(2, 8):
        clsID = web2py.db.classes.insert(school_locations_id=1,
                                         school_classtypes_id=1,
                                         Week_day=i,
                                         Starttime='06:00:00',
                                         Endtime='09:00:00',
                                         Startdate='2014-01-01',
                                         Enddate='2999-01-01',
                                         Maxstudents=1
                                         )

        web2py.db.classes_attendance.insert(auth_customer_id=1001,
                                            classes_id=clsID,
                                            ClassDate=today,
                                            AttendanceType='1')

    # make sure there's only one space for all classes
    cls = web2py.db.classes(1)
    cls.Maxstudents = 1
    cls.update_record()

    web2py.db.commit()

    url = '/selfcheckin/checkin/?clsID=' + str(clsID) + \
          '&date=' + str(today)
    client.get(url)
    assert client.status == 200

    assert 'This class is full' in client.text
    assert not 'Check in</button>' in client.text
