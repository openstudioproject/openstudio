#!/usr/bin/env python

'''
    py.test test cases to test the API controller (api.py)
'''

import urllib
import gluon.contrib.simplejson as sj
from gluon.contrib.populate import populate

from populate_os_tables import populate_workshops_for_api_tests
from populate_os_tables import populate_api_users
from populate_os_tables import populate_school_subscriptions
from populate_os_tables import populate_school_classcards


base_url = 'http://dev.openstudioproject.com:8000'

def populate_schedule(web2py):
    '''
        Sets up a class and API user to test with
    '''
    populate_api_users(web2py)

    web2py.db.auth_user.insert(id=2,
                               first_name='Edwin',
                               last_name='van de Ven',
                               email='edwin@openstudioproject.com',
                               teacher=True)
    web2py.db.auth_user.insert(first_name='Pietje',
                               last_name='Puk',
                               email='pietje@puk.nl',
                               teacher=True)
    web2py.db.auth_user.insert(first_name='Aimee',
                               last_name='Garcias',
                               email='aimee@ashtanga.sp',
                               teacher=True)
    web2py.db.school_classtypes.insert(Name='Mysore',
                                       Link='http://www.openstudioproject.com',
                                       Description='Description here',
                                       AllowAPI=True)
    web2py.db.school_classtypes.insert(Name='Led class',
                                       AllowAPI=True)
    web2py.db.school_classtypes.insert(Name='Private',
                                       AllowAPI=False)
    web2py.db.school_locations.insert(Name="Sittard",
                                      AllowAPI=True)
    web2py.db.school_locations.insert(Name="Maastricht",
                                      AllowAPI=False)
    web2py.db.school_levels.insert(Name='Level 1')
    # Monday class + teachers
    web2py.db.classes.insert(school_locations_id=1,
                             school_classtypes_id=1,
                             school_levels_id=1,
                             Week_day=1,
                             Starttime='06:00:00',
                             Endtime='09:00:00',
                             Startdate='2014-01-01',
                             Enddate='',
                             Maxstudents=20,
                             AllowAPI=True)
    web2py.db.classes_teachers.insert(classes_id=1,
                                      auth_teacher_id=2,
                                      auth_teacher_id2=3,
                                      Startdate='2014-01-01')
    # Tuesday class + teachers
    web2py.db.classes.insert(school_locations_id=2,
                             school_classtypes_id=2,
                             school_levels_id=1,
                             Week_day=2,
                             Starttime='06:00:00',
                             Endtime='09:00:00',
                             Startdate='2014-01-01',
                             Enddate='',
                             Maxstudents=20,
                             AllowAPI=True)
    web2py.db.classes_teachers.insert(classes_id=2,
                                      auth_teacher_id=2,
                                      auth_teacher_id2=3,
                                      Startdate='2014-01-01')
    web2py.db.classes_otc.insert(
        classes_id=1,
        ClassDate='2014-01-13',
        auth_teacher_id=4,
        teacher_role=1,
        auth_teacher_id2=3,
        teacher_role2=1
    )
    # web2py.db.classes_subteachers.insert(classes_id=1,
    #                                      ClassDate='2014-01-13',
    #                                      auth_teacher_id=4,
    #                                      auth_teacher_id2=3)
    web2py.db.classes_otc.insert(
        classes_id=1,
        ClassDate='2014-01-20',
        Status='cancelled'
    )
    # web2py.db.classes_cancelled.insert(classes_id=1,
    #                                    ClassDate='2014-01-20')
    web2py.db.school_holidays.insert(Description='Carnavals vakantie',
                                     Startdate='2014-01-27',
                                     Enddate='2014-01-30',
                                     Classes=True)
    web2py.db.school_holidays_locations.insert(
        school_holidays_id = 1,
        school_locations_id = 1 )
    web2py.db.commit()


def test_schedule_get_extension_error():
    '''
        Check whether we get a value error when a call is made without variables
    '''
    url = base_url + '/api/schedule_get'
    page = urllib.urlopen(url).read()
    assert "Extension error" in page


def test_schedule_get_days_extension_error():
    '''
        Check whether we get a value error when a call is made without variables
    '''
    url = base_url + '/api/schedule_get_days'
    page = urllib.urlopen(url).read()
    assert "Extension error" in page


def test_workshops_get_extension_error():
    '''
        Check whether we get a value error when a class is made without variabled
    '''
    url = base_url + '/api/workshops_get'
    page = urllib.urlopen(url).read()
    assert "Extension error" in page


def test_schedule_get_authentication_error():
    '''
        Check whether we get an authentication error when we don't supply
        a username and password or a wrong username and password
    '''
    url = base_url + \
        '/api/schedule_get.json?user=test&key=test&year=2014&week=1'
    page = urllib.urlopen(url).read()
    assert "Authentication error" in page


def test_schedule_get_days_authentication_error():
    '''
        Check whether we get an authentication error when we don't supply
        a username and password or a wrong username and password
    '''
    url = base_url + \
        '/api/schedule_get_days.json?user=test&key=test&date_start=2014-01-01&date_end=2014-01-06'
    page = urllib.urlopen(url).read()
    assert "Authentication error" in page


def test_workshops_get_authentication_error():
    '''
        Check whether we get an authentication error when we don't supply
        a username and password or a wrong username and password
    '''
    url = base_url + \
        '/api/workshops_get.json?user=test&key=test'
    page = urllib.urlopen(url).read()
    assert "Authentication error" in page


def test_schedule_get_value_error():
    '''
        Check whether we specify a string for year and week
    '''
    url = base_url + \
        '/api/schedule_get.json?user=test&key=test&year=bla&week=bla'
    page = urllib.urlopen(url).read()
    assert "Value error" in page


def test_schedule_get_days_value_error():
    '''
        Check whether we specify a string for year and week
    '''
    url = base_url + \
        '/api/schedule_get_days.json?user=test&key=test&date_start=2000&date_end=2014-01-06'
    page = urllib.urlopen(url).read()
    assert "Missing value" in page


def test_schedule_get_missing_value():
    '''
        Check whether we specify a string for year and week
    '''
    url = base_url + \
        '/api/schedule_get.json'
    page = urllib.urlopen(url).read()
    assert "Missing value" in page


def test_schedule_get_days_missing_value():
    '''
        Check whether we specify a string for year and week
    '''
    url = base_url + \
        '/api/schedule_get_days.json'
    page = urllib.urlopen(url).read()
    assert "Missing value" in page


def test_schedule_get_json(client, web2py):
    '''
        Check whether we can get the information in the database through the api
        using the JSON interface.
    '''
    populate_schedule(web2py)

    url = base_url + \
        '/api/schedule_get.json?user=test&key=test&year=2014&week=2'
    page = urllib.urlopen(url).read()

    json = sj.loads(page)

    ## check locations info
    assert json['data']['locations'][0]['id'] == 1
    assert json['data']['locations'][0]['Name']== 'Sittard'
    # Check that only the location with "AllowAPI = True" is shown
    assert len(json['data']['locations']) == 1

    ## check classtypes info, sorted alphabetically
    assert json['data']['classtypes'][0]['Name']== 'Mysore'
    assert json['data']['classtypes'][0]['Link'] == 'http://www.openstudioproject.com'
    assert json['data']['classtypes'][0]['Description'] == 'Description here'
    # Check that only the location with "AllowAPI = True" is shown and that only classtypes listed in classes are shown
    assert len(json['data']['classtypes']) == 1

    # check teachers info, sorted alphabetically - listing only those currently in the classes list for this week
    assert json['data']['teachers'][0]['name'] == 'Edwin van de Ven'

    # check classes info
    assert json['data']['classes']['Monday']['date'] == '2014-01-06'
    assert not json['data']['classes']['Monday']['classes'][0]['Holiday']
    assert json['data']['classes']['Monday']['classes'][0]['LocationID'] == 1
    assert json['data']['classes']['Monday']['classes'][0]['Location'] == 'Sittard'
    assert json['data']['classes']['Monday']['classes'][0]['ClassTypeID'] == 1
    assert json['data']['classes']['Monday']['classes'][0]['ClassType'] == 'Mysore'
    assert json['data']['classes']['Monday']['classes'][0]['Starttime'] == '06:00'
    assert json['data']['classes']['Monday']['classes'][0]['Endtime'] == '09:00'
    assert json['data']['classes']['Monday']['classes'][0]['TeacherID'] == 2
    assert json['data']['classes']['Monday']['classes'][0]['Teacher'] == 'Edwin van de Ven'
    assert json['data']['classes']['Monday']['classes'][0]['TeacherID2'] == 3
    assert json['data']['classes']['Monday']['classes'][0]['LevelID'] == 1
    assert json['data']['classes']['Monday']['classes'][0]['Level'] == 'Level 1'
    assert not json['data']['classes']['Monday']['classes'][0]['Subteacher']
    assert not json['data']['classes']['Monday']['classes'][0]['Cancelled']

    assert json['data']['classes']['Monday']['classes'][0]['BookingStatus'] == 'finished'
    assert json['data']['classes']['Monday']['classes'][0]['LinkShop'] == \
           'http://dev.openstudioproject.com:8000/shop/classes_book_options?clsID=1&date=2014-01-06'

    # check classes_subteachers
    url = base_url + \
        '/api/schedule_get.json?user=test&key=test&year=2014&week=3'
    page = urllib.urlopen(url).read()

    json = sj.loads(page)

    assert json['data']['classes']['Monday']['date'] == '2014-01-13'


    assert not json['data']['classes']['Monday']['classes'][0]['Holiday']
    assert json['data']['classes']['Monday']['classes'][0]['TeacherID'] == 4
    assert json['data']['classes']['Monday']['classes'][0]['Teacher'] == \
        'Aimee Garcias'
    assert json['data']['classes']['Monday']['classes'][0]['TeacherID2'] == 3
    assert json['data']['classes']['Monday']['classes'][0]['Teacher2'] == \
        'Pietje Puk'
    assert json['data']['classes']['Monday']['classes'][0]['Subteacher']
    assert not json['data']['classes']['Monday']['classes'][0]['Cancelled']

    # check cancelled
    url = base_url + \
        '/api/schedule_get.json?user=test&key=test&year=2014&week=4'
    page = urllib.urlopen(url).read()

    json = sj.loads(page)

    assert json['data']['classes']['Monday']['date'] == '2014-01-20'
    assert json['data']['classes']['Monday']['classes'][0]['Cancelled']
    assert not json['data']['classes']['Monday']['classes'][0]['Holiday']

    # check holiday
    url = base_url + \
        '/api/schedule_get.json?user=test&key=test&year=2014&week=5'
    page = urllib.urlopen(url).read()

    json = sj.loads(page)

    assert json['data']['classes']['Monday']['date'] == '2014-01-27'
    assert json['data']['classes']['Monday']['classes'][0]['Holiday']

    # Check TeacherID parameter
    teID = 2
    url = base_url + \
        '/api/schedule_get.json?user=test&key=test&year=2014&week=2&TeacherID=' + unicode(teID)
    page = urllib.urlopen(url).read()

    json = sj.loads(page)

    assert json['data']['classes']['Monday']['date']  == '2014-01-06'
    assert json['data']['classes']['Monday']['classes'][0]['TeacherID'] == teID
    assert json['data']['classes']['Monday']['classes'][0]['Teacher'] == \
        'Edwin van de Ven'


def test_shedule_get_days_json(client, web2py):
    '''
        test schedule_get_days API endpoint
    '''
    populate_schedule(web2py)


    # check normal class
    url = base_url + \
        '/api/schedule_get_days.json?user=test&key=test&date_start=2014-01-06&date_end=2014-01-06'
    page = urllib.urlopen(url).read()
    json = sj.loads(page)


    assert json['data'][0]['date'] == '2014-01-06'
    assert not json['data'][0]['classes'][0]['Holiday']
    assert json['data'][0]['classes'][0]['LocationID'] == 1
    assert json['data'][0]['classes'][0]['Location'] == 'Sittard'
    assert json['data'][0]['classes'][0]['ClassTypeID'] == 1
    assert json['data'][0]['classes'][0]['ClassType'] == 'Mysore'
    assert json['data'][0]['classes'][0]['Starttime'] == '06:00'
    assert json['data'][0]['classes'][0]['Endtime'] == '09:00'
    assert json['data'][0]['classes'][0]['TeacherID'] == 2
    assert json['data'][0]['classes'][0]['Teacher'] == 'Edwin van de Ven'
    assert json['data'][0]['classes'][0]['TeacherID2'] == 3
    assert json['data'][0]['classes'][0]['LevelID'] == 1
    assert json['data'][0]['classes'][0]['Level'] == 'Level 1'
    assert not json['data'][0]['classes'][0]['Subteacher']
    assert not json['data'][0]['classes'][0]['Cancelled']

    # check subteachers class
    url = base_url + \
        '/api/schedule_get_days.json?user=test&key=test&date_start=2014-01-13&date_end=2014-01-13'
    page = urllib.urlopen(url).read()
    json = sj.loads(page)

    assert json['data'][0]['date'] == '2014-01-13'
    assert not json['data'][0]['classes'][0]['Holiday']
    assert json['data'][0]['classes'][0]['TeacherID'] == 4
    assert json['data'][0]['classes'][0]['Teacher'] == \
        'Aimee Garcias'
    assert json['data'][0]['classes'][0]['TeacherID2'] == 3
    assert json['data'][0]['classes'][0]['Teacher2'] == \
        'Pietje Puk'
    assert json['data'][0]['classes'][0]['Subteacher']
    assert not json['data'][0]['classes'][0]['Cancelled']


    # check cancelled
    url = base_url + \
        '/api/schedule_get_days.json?user=test&key=test&date_start=2014-01-20&date_end=2014-01-20'
    page = urllib.urlopen(url).read()
    json = sj.loads(page)

    assert json['data'][0]['date'] == '2014-01-20'
    assert json['data'][0]['classes'][0]['Cancelled']
    assert not json['data'][0]['classes'][0]['Holiday']

    # check holiday
    url = base_url + \
        '/api/schedule_get_days.json?user=test&key=test&date_start=2014-01-27&date_end=2014-01-27'
    page = urllib.urlopen(url).read()
    json = sj.loads(page)

    assert json['data'][0]['date'] == '2014-01-27'
    assert json['data'][0]['classes'][0]['Holiday']


def test_workshops_get_json(client, web2py):
    '''
        test workshops_get API endpoint
    '''
    populate_workshops_for_api_tests(web2py)

    # Check if workshop is in the list
    url = base_url + '/api/workshops_get.json?user=test&key=test'
    page = urllib.urlopen(url).read()
    json = sj.loads(page)

    workshop = web2py.db.workshops(1)
    fws_wsp = web2py.db.workshops_products(1)
    location = web2py.db.school_locations(1)
    teacher = web2py.db.auth_user(workshop.auth_teacher_id)
    teacher2 = web2py.db.auth_user(workshop.auth_teacher_id2)

    assert json['data'][0]['Startdate'] == str(workshop.Startdate)
    assert json['data'][0]['Enddate'] == str(workshop.Enddate)
    assert json['data'][0]['Name'] == workshop.Name
    assert json['data'][0]['Teacher']['id'] == workshop.auth_teacher_id
    assert json['data'][0]['Teacher']['Name'] == teacher.display_name
    assert json['data'][0]['Teacher2']['id'] == workshop.auth_teacher_id2
    assert json['data'][0]['Teacher2']['Name'] == teacher2.display_name
    assert json['data'][0]['LocationID'] == workshop.school_locations_id
    assert json['data'][0]['Location'] == location.Name
    assert json['data'][0]['Description'] == workshop.Description


def test_workshop_get_json(client, web2py):
    '''
        test workshop_get API endpoint
    '''
    populate_workshops_for_api_tests(web2py)

    # Check if workshop is in the list
    url = base_url + '/api/workshop_get.json?user=test&key=test&id=1'
    page = urllib.urlopen(url).read()
    json = sj.loads(page)

    workshop = web2py.db.workshops(1)
    fws_wsp = web2py.db.workshops_products(1)
    location = web2py.db.school_locations(1)
    teacher = web2py.db.auth_user(workshop.auth_teacher_id)
    teacher2 = web2py.db.auth_user(workshop.auth_teacher_id2)

    assert json['data']['Startdate'] == str(workshop.Startdate)
    assert json['data']['Enddate'] == str(workshop.Enddate)
    assert json['data']['Name'] == workshop.Name
    assert json['data']['Teacher']['id'] == workshop.auth_teacher_id
    assert json['data']['Teacher']['Name'] == teacher.display_name
    assert json['data']['Teacher2']['id'] == workshop.auth_teacher_id2
    assert json['data']['Teacher2']['Name'] == teacher2.display_name
    assert json['data']['LocationID'] == workshop.school_locations_id
    assert json['data']['Location'] == location.Name
    assert json['data']['Description'] == workshop.Description


def workshop_get_dates(activities):
    '''
        :param workshop: Workshop object
        :param activities: workshop activities rows
    '''
    date_until = ''
    if len(activities) > 0:
        date_from = activities[0].Activitydate

    if len(activities) > 1:
        date_until = activities[len(activities) - 1].Activitydate

    if len(activities) == 0: # no activities
        date_from = T("No activities found...")
        date_until = T("No activities found...")

    return dict(date_from=date_from,
                date_until=date_until)


def test_school_subscriptions_get_json(client, web2py):
    '''
        Are the subscriptions returned correctly?
    '''
    populate_api_users(web2py)

    populate_school_subscriptions(web2py)

    url = base_url + '/api/school_subscriptions_get.json?user=test&key=test'
    page = urllib.urlopen(url).read()
    json = sj.loads(page)

    subscription = web2py.db.school_subscriptions(1)
    subscription_price = web2py.db.school_subscriptions_price(1)
    assert json['data'][0]['Name'] == subscription.Name
    assert json['data'][0]['Price'] == subscription_price.Price


def test_school_classcards_get_json(client, web2py):
    '''
        Are the class cards returned correctly?
    '''
    populate_api_users(web2py)

    populate_school_classcards(web2py, 2)

    url = base_url + '/api/school_classcards_get.json?user=test&key=test'
    page = urllib.urlopen(url).read()
    json = sj.loads(page)

    classcard = web2py.db.school_classcards(1)
    assert json['data'][0]['Name'] == classcard.Name


def test_school_teachers_get_json(client, web2py):
    '''
        Are the teachers returned correctly?
    '''
    from populate_os_tables import populate_auth_user_teachers

    populate_api_users(web2py)

    populate_auth_user_teachers(web2py)

    url = base_url + '/api/school_teachers_get.json?user=test&key=test'
    page = urllib.urlopen(url).read()
    json = sj.loads(page)

    teacher = web2py.db.auth_user(2)
    assert json['data'][0]['Name'] == teacher.full_name