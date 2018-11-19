#!/usr/bin/env python

"""py.test test cases to test OpenStudio.

These tests run based on webclient and need web2py server running.
"""

import datetime
import gluon.contrib.simplejson as sj
from gluon.contrib.populate import populate
from populate_os_tables import prepare_classes
from populate_os_tables import populate_classes
from populate_os_tables import populate_customers
from populate_os_tables import populate_customers_with_classcards
from populate_os_tables import populate_customers_with_subscriptions
from populate_os_tables import populate_customers_with_memberships
from populate_os_tables import populate_school_classcards
from populate_os_tables import populate_school_classcards_groups
from populate_os_tables import populate_workshop_activity_overlapping_class
from populate_os_tables import populate_school_subscriptions_groups
from populate_os_tables import populate_customers_notes
from populate_os_tables import populate_auth_user_teachers_fixed_rate_default
from populate_os_tables import prepare_classes_otc_subs_avail


def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)


def test_class_add(client, web2py):
    """
        Can we add a class?
    """
    populate(web2py.db.school_locations, 1)
    populate(web2py.db.school_classtypes, 1)

    url = '/classes/class_add'
    client.get(url)
    assert client.status == 200
    data = dict(school_locations_id='1',
                school_classtypes_id='1',
                Week_day='1',
                Starttime='06:00:00',
                Endtime='08:00:00',
                Startdate='2014-01-01',
                Maxstudents='123',
                MaxOnlineBooking='110',
                MaxReservationsRecurring='10',
                )
    client.post(url, data=data)
    assert client.status == 200

    assert "Add teacher" in client.text # check redirection to add teacher page


    # move to schedule page and check display of input
    url = '/classes/schedule'
    client.get(url)
    assert client.status == 200

    assert web2py.db(web2py.db.classes).count() == 1
    assert data['Maxstudents'] in client.text
    query = web2py.db.classes.Maxstudents == data['Maxstudents']
    assert web2py.db(query).count() == 1


def test_class_edit(client, web2py):
    """
        Can we edit a class?
    """
    populate_classes(web2py)
    assert web2py.db(web2py.db.classes).count() == 1

    url = '/classes/class_edit/?clsID=1'
    client.get(url)
    assert client.status == 200
    data = dict(id=1,
                school_locations_id='1',
                school_classtypes_id='1',
                Week_day='1', # Monday
                Starttime='06:00:00',
                Endtime='08:00:00',
                Startdate='2014-01-01',
                Maxstudents='499',
                MaxOnlineBooking='200',
                MaxReservationsRecurring='10'
                )
    client.post(url, data=data)
    assert client.status == 200
    assert "Schedule" in client.text # check redirection to schedule

    assert data['Maxstudents'] in client.text
    assert web2py.db(web2py.db.classes.Maxstudents == data['Maxstudents']).count() == 1


def test_revenue(client, web2py):
    """
    Check core data on /classes/revenue
    """
    prepare_classes(web2py)
    populate_auth_user_teachers_fixed_rate_default(web2py)

    url = '/classes/revenue?clsID=1&date=2014-01-06'
    client.get(url)
    assert client.status == 200

    prices = web2py.db.classes_price(1)
    assert format(prices.Trial, '.2f') in client.text

    tp = web2py.db.teachers_payment_fixed_rate_default(1)
    assert format(tp.ClassRate, '.2f') in client.text


def test_revenue_export_preview(client, web2py):
    """
    Check core data on /classes/revenue_export_preview
    """
    prepare_classes(web2py)
    populate_auth_user_teachers_fixed_rate_default(web2py)

    url = '/classes/revenue_export_preview?clsID=1&date=2014-01-06'
    client.get(url)
    assert client.status == 200

    prices = web2py.db.classes_price(1)
    assert format(prices.Trial, '.2f') in client.text

    tp = web2py.db.teachers_payment_fixed_rate_default(1)
    assert format(tp.ClassRate, '.2f') in client.text


def test_revenue_export(client, web2py):
    """
    Check core data on /classes/revenue
    """
    prepare_classes(web2py)
    populate_auth_user_teachers_fixed_rate_default(web2py)

    url = '/classes/revenue_export?clsID=1&date=2014-01-06'
    client.get(url)
    assert client.status == 200


def test_schedule(client, web2py):
    """
        Is the schedule showing all things as it should?
    """
    populate_classes(web2py)
    assert web2py.db(web2py.db.classes).count() == 1

    url = '/classes/schedule'
    client.get(url)
    assert client.status == 200
    assert 'Schedule' in client.text

    url = '/classes/schedule?year=2014&week=2' # we need the second week because the class is on a monday and the in week 1 monday is in december 2013.
    client.get(url)
    assert client.status == 200
    assert 'fa-user' in client.text
    assert 'Enrollments' in client.text
    assert 'fa-pencil' in client.text
    assert 'fa-times' in client.text
    location_check = web2py.db.school_locations(1).Name.split(' ')[1]
    assert location_check in client.text

    # check if the label for subteacher is applied
    assert '<span class="os_label bg_light_blue">' in client.text


def test_schedule_classes_otc(client, web2py):
    """
        Is a change from classes_otc showing in the schedule?
    """
    populate_classes(web2py, with_otc=True)

    url = '/classes/schedule?year=2014&week=2'
    client.get(url)
    assert client.status == 200

    location = web2py.db.school_locations(2).Name.split(' ')[0]
    assert location in client.text

    classtype = web2py.db.school_classtypes(2).Name.split(' ')[0]
    assert classtype in client.text


def test_class_edit_on_date(client, web2py):
    """
        Is the page to edit a single class working?
    """
    prepare_classes(web2py)

    url = '/classes/class_edit_on_date?clsID=1&date=2014-01-06'
    client.get(url)
    assert client.status == 200

    data = {'Status':'open'}
    client.post(url, data=data)
    assert client.status == 200

    assert web2py.db(web2py.db.classes_otc).count() == 1

    client.get(url)
    assert client.status == 200
    assert '<option selected="selected" value="open">' in client.text


def test_class_edit_on_date_remove_changes(client, web2py):
    """
        Can we remove the changes in classes_otc
    """
    prepare_classes(web2py)

    web2py.db.classes_otc.insert(
        classes_id=1,
        ClassDate='2014-01-06',
        Status='cancelled' )

    web2py.db.commit()

    url = '/classes/class_edit_on_date_remove_changes?cotcID=1&clsID=1&date=2014-01-06'
    client.get(url)
    assert client.status == 200
    assert web2py.db(web2py.db.classes_otc).count() == 0


def test_class_edit_on_date_cancel_class(client, web2py):
    """
        Are credits returned to all customers and booking cancelled when a class is cancelled
    """
    url = '/user/login'
    client.get(url)
    assert client.status == 200

    prepare_classes(web2py, credits=True)

    url = '/classes/class_edit_on_date?clsID=1&date=2014-01-20'
    client.get(url)
    assert client.status == 200

    data = {'Status':'cancelled'}
    client.post(url, data=data)
    assert client.status == 200

    assert web2py.db(web2py.db.classes_otc).count() == 1

    client.get(url)
    assert client.status == 200
    assert '<option selected="selected" value="cancelled">' in client.text

    caID = 3 # This is the ID of the class on 20-01-2014
    # Check status
    clatt = web2py.db.classes_attendance(caID)
    assert clatt.BookingStatus == 'cancelled'

    # Check credit mutation removed
    query = (web2py.db.customers_subscriptions_credits.id > 0)
    assert web2py.db(query).count() == 1


def test_classes_otc_subteacher(client, web2py):
    """
        Can we add substitute teachers for a class?
    """
    populate_classes(web2py)
    assert web2py.db(web2py.db.classes).count() == 1

    classes_id = '1'
    classdate = '2014-01-06'

    url = '/classes/class_edit_on_date?clsID=' + classes_id + '&date=' + classdate
    client.get(url)
    assert client.status == 200

    teachers_id = 2
    data = dict(auth_teacher_id=teachers_id,
                auth_teacher_id2='',
                teacher_role=1,
                teacher_role2='')
    client.post(url, data=data)
    assert client.status == 200

    query = (web2py.db.classes_otc.auth_teacher_id == teachers_id)
    assert web2py.db(query).count() == 1


def test_attendance_list_add_customer(client, web2py):
    """
        Add a customer from the attendance list
    """
    prepare_classes(web2py)

    rvars = 'clsID=1&date=2014-01-06'

    url = '/classes/attendance?' + rvars
    client.get(url)
    assert client.status == 200

    # now pretend we clicked the button and go to customers/add
    url = '/customers/add?' + rvars
    client.get(url)
    assert client.status == 200

    data = {'first_name' : "One Punch",
            'last_name'  : "Man",
            'email'      : 'Saitama_opm@yahoo.co.jp' }
    client.post(url, data=data)
    assert client.status == 200

    # verify redirection back to attendance_list
    assert 'Attendance' in client.text

    # verify DB
    query = (web2py.db.auth_user.first_name == data['first_name'])
    assert web2py.db(query).count() == 1


# def test_expected_attendance_reservations(client, web2py):
#     """
#         Does the expected attendance page show?
#     """
#     populate_classes(web2py)
#     populate_customers(web2py, 1)
#     web2py.db.classes_reservation.insert(classes_id='1',
#                                          auth_customer_id=1001,
#                                          Startdate='2014-01-01')
#     web2py.db.commit()
#
#     assert web2py.db(web2py.db.auth_user).count() > 1
#     assert web2py.db(web2py.db.classes).count() == 1
#     assert web2py.db(web2py.db.classes_reservation).count() == 1
#
#     url = '/classes/attendance?clsID=1&date=2014-01-06'
#     client.get(url)
#     assert client.status == 200
#     assert web2py.db.auth_user(1001).first_name in client.text



# def test_expected_attendance_from_previous_attendance_classcard(client, web2py):
#     """
#         Does the expected attendance page show customers without reservations
#         who attended using a class card or subscription in the past month?
#     """
#     # get random url to init payment methods
#     url = '/default/user/login'
#     client.get(url)
#     assert client.status == 200
#
#     populate_classes(web2py)
#     populate_customers_with_classcards(web2py)
#
#     web2py.db.classes_attendance.insert(
#         classes_id                 = 1,
#         auth_customer_id           = 1001,
#         customers_classcards_id    = 1,
#         ClassDate                  = '2014-01-06',
#         AttendanceType             = 3 )
#
#     web2py.db.commit()
#
#     url = '/classes/attendance?clsID=1&date=2014-01-20'
#     client.get(url)
#     assert client.status == 200
#
#     assert web2py.db.auth_user(1001).first_name in client.text


# def test_attendance_sign_in_trialclass(client, web2py):
#     """
#         Can we check in a customer for a trial class?
#         Check using auth_user.id 1002
#     """
#     classdate = '2014-01-06'
#     prepare_classes(web2py)
#
#     url = '/classes/attendance_sign_in_trialclass?cuID=1002&clsID=1&date=2014-01-06'
#     client.get(url)
#     assert client.status == 200
#
#     # check we have count 2 for attendance in db
#     query = (web2py.db.classes_attendance.id > 0)
#     count = web2py.db(query).count()
#     assert count == 4
#
#     assert web2py.db(web2py.db.invoices).count() == 1
#     invoice = web2py.db.invoices(1)
#     assert invoice.invoices_groups_id == 100
#
#     inv_clatt = web2py.db.invoices_classes_attendance(1)
#     assert inv_clatt.classes_attendance_id == 5
#
#     price = web2py.db.classes_price(1).Trial
#     invoice_amount = web2py.db.invoices_amounts(1).TotalPriceVAT
#
#     assert price == invoice_amount


# def test_attendance_sign_in_dropin(client, web2py):
#     """
#         Can we check in a customer for a drop in class?
#         Check using auth_user.id 1002
#     """
#     classdate = '2014-01-06'
#     prepare_classes(web2py)
#
#     url = '/classes/attendance_sign_in_dropin?cuID=1002&clsID=1&date=2014-01-06'
#     client.get(url)
#     assert client.status == 200
#
#     # check we have count 2 for attendance in db
#     query = (web2py.db.classes_attendance.id > 0)
#     count = web2py.db(query).count()
#     assert count == 4
#
#     assert web2py.db(web2py.db.invoices).count() == 1
#     invoice = web2py.db.invoices(1)
#     assert invoice.invoices_groups_id == 100
#
#     inv_clatt = web2py.db.invoices_classes_attendance(1)
#     assert inv_clatt.classes_attendance_id == 5
#
#     price = web2py.db.classes_price(1).Dropin
#     invoice_amount = web2py.db.invoices_amounts(1).TotalPriceVAT
#
#     assert price == invoice_amount


# def test_attendance_sign_in_subscription(client, web2py):
#     """
#         Can we check in a customer for a class using a subscription?
#         Check using auth_user.id 1001
#     """
#     # get random url to init payment methods for subscription
#     client.get('/default/user/login')
#     assert client.status == 200
#
#     populate_customers_with_subscriptions(web2py, credits=True)
#
#     populate(web2py.db.school_locations, 2)
#     populate(web2py.db.school_classtypes, 3)
#     populate(web2py.db.school_levels, 3)
#     web2py.db.classes.insert(school_locations_id=1,
#                              school_classtypes_id=1,
#                              Week_day=1,
#                              Starttime='06:00:00',
#                              Endtime='09:00:00',
#                              Startdate='2014-01-01',
#                              Enddate='2999-01-01',
#                              Maxstudents=20,
#                              )
#
#     web2py.db.commit()
#
#     url = '/classes/attendance_sign_in_subscription?cuID=1001&csID=1&clsID=1&date=2015-01-05'
#     client.get(url)
#     assert client.status == 200
#
#     # check we have count 1 for attendance in db
#     query = (web2py.db.classes_attendance.id > 0)
#     count = web2py.db(query).count()
#     assert count == 1
#
#     # check we have 2 counts in db.customers_subscriptions_credits
#     # one for initial add of credits from populate table and 1 from subtracting a credit for this class
#     query = (web2py.db.customers_subscriptions_credits.id > 0)
#     assert web2py.db(query).count() == 2
#
#
# def test_attendance_sign_in_subscription_check_paused(client, web2py):
#     """
#         Can we check in a customer for a class using a subscription
#         does it show a message when the subscription is paused'?
#         Check using auth_user.id 1001
#     """
#     # get random url to init payment methods for subscription
#     client.get('/default/user/login')
#     assert client.status == 200
#
#     populate_customers_with_subscriptions(web2py)
#
#     populate(web2py.db.school_locations, 2)
#     populate(web2py.db.school_classtypes, 3)
#     populate(web2py.db.school_levels, 3)
#     web2py.db.classes.insert(school_locations_id=1,
#                              school_classtypes_id=1,
#                              Week_day=1,
#                              Starttime='06:00:00',
#                              Endtime='09:00:00',
#                              Startdate='2014-01-01',
#                              Enddate='2999-01-01',
#                              Maxstudents=20,
#                              )
#
#     web2py.db.customers_subscriptions_paused.insert(
#         customers_subscriptions_id = 1,
#         Startdate                  = '2014-01-01',
#         Enddate                    = '2014-12-31',
#         Description                = 'for testing')
#
#     web2py.db.commit()
#
#     url = '/classes/attendance_sign_in_subscription?cuID=1001&csID=1&clsID=1&date=2014-01-06'
#     client.get(url)
#     assert client.status == 200
#
#     # check we have count 1 for attendance in db
#     query = (web2py.db.classes_attendance.id > 0)
#     count = web2py.db(query).count()
#     assert count == 1
#     assert 'Subscription is paused on this date' in client.text


# def test_attendance_sign_in_subscription_weekly_classes_check(client, web2py):
#     """
#         Can we check in a customer for a class using a subscription?
#         Check using auth_user.id 1001
#     """
#     # get random url to init payment methods for subscription
#     client.get('/default/user/login')
#     assert client.status == 200
#
#     populate_customers_with_subscriptions(web2py)
#
#     populate(web2py.db.school_locations, 2)
#     populate(web2py.db.school_classtypes, 3)
#     populate(web2py.db.school_levels, 3)
#     web2py.db.classes.insert(school_locations_id=1,
#                              school_classtypes_id=1,
#                              Week_day=1,
#                              Starttime='06:00:00',
#                              Endtime='09:00:00',
#                              Startdate='2014-01-01',
#                              Enddate='2999-01-01',
#                              Maxstudents=20,
#                              )
#     web2py.db.classes.insert(school_locations_id=1,
#                              school_classtypes_id=1,
#                              Week_day=2,
#                              Starttime='06:00:00',
#                              Endtime='09:00:00',
#                              Startdate='2014-01-01',
#                              Enddate='2999-01-01',
#                              Maxstudents=20,
#                              )
#
#     web2py.db.commit()
#
#     # Check in to a class
#     url = '/classes/attendance_sign_in_subscription?cuID=1001&csID=1&clsID=1&date=2015-01-05'
#     client.get(url)
#     assert client.status == 200
#
#     # Check in to another class
#     url = '/classes/attendance_sign_in_subscription?cuID=1001&csID=1&clsID=2&date=2015-01-05'
#     client.get(url)
#     assert client.status == 200
#     # now we should be over the limit
#     assert 'exceeded' in client.text
#
#     # check we have count 2 for attendance in db
#     query = (web2py.db.classes_attendance.id > 0)
#     count = web2py.db(query).count()
#     assert count == 2
#
#
# def test_attendance_sign_in_subscription_monthly_classes_check(client, web2py):
#     """
#         Can we check in a customer for a class using a subscription?
#         Check using auth_user.id 1001
#     """
#     # get random url to init payment methods for subscription
#     client.get('/default/user/login')
#     assert client.status == 200
#
#     populate_customers_with_subscriptions(web2py)
#
#     # change first customer subscription to monthly one school_subscriptions_id = 3
#     cs = web2py.db.customers_subscriptions(1)
#     cs.school_subscriptions_id = 3
#     cs.update_record()
#
#     populate(web2py.db.school_locations, 2)
#     populate(web2py.db.school_classtypes, 3)
#     populate(web2py.db.school_levels, 3)
#     web2py.db.classes.insert(school_locations_id=1,
#                              school_classtypes_id=1,
#                              Week_day=1,
#                              Starttime='06:00:00',
#                              Endtime='09:00:00',
#                              Startdate='2014-01-01',
#                              Enddate='2999-01-01',
#                              Maxstudents=20,
#                              )
#     web2py.db.classes.insert(school_locations_id=1,
#                              school_classtypes_id=1,
#                              Week_day=2,
#                              Starttime='06:00:00',
#                              Endtime='09:00:00',
#                              Startdate='2014-01-01',
#                              Enddate='2999-01-01',
#                              Maxstudents=20,
#                              )
#
#     web2py.db.commit()
#
#     url = '/classes/attendance_sign_in_subscription?cuID=1001&csID=3&clsID=1&date=2015-01-05'
#     client.get(url)
#     assert client.status == 200
#
#     url = '/classes/attendance_sign_in_subscription?cuID=1001&csID=3&clsID=2&date=2015-01-05'
#     client.get(url)
#     assert client.status == 200
#     assert 'exceeded' in client.text
#
#     # check we have count 2 for attendance in db
#     query = (web2py.db.classes_attendance.id > 0)
#     count = web2py.db(query).count()
#     assert count == 2


# def test_attendance_sign_in_classcard(client, web2py):
#     """
#         Can we check in a customer for a class using a class card?
#         Check using auth_user.id 1002
#     """
#     classdate = '2014-01-06'
#     populate_customers_with_classcards(web2py)
#
#     populate(web2py.db.school_locations, 2)
#     populate(web2py.db.school_classtypes, 3)
#     populate(web2py.db.school_levels, 3)
#     web2py.db.classes.insert(school_locations_id=1,
#                              school_classtypes_id=1,
#                              Week_day=1,
#                              Starttime='06:00:00',
#                              Endtime='09:00:00',
#                              Startdate='2014-01-01',
#                              Enddate='2999-01-01',
#                              Maxstudents=20,
#                              )
#     web2py.db.commit()
#
#     url = '/classes/attendance_sign_in_classcard?cuID=1002&ccdID=2&clsID=1&date=2015-01-05'
#     client.get(url)
#     assert client.status == 200
#
#     # check we have count 1 for attendance in db
#     query = (web2py.db.classes_attendance.id > 0)
#     assert web2py.db(query).count() == 1
#
#     # check classes remaining count; should be total classes on card - 1
#     scd = web2py.db.school_classcards(1)
#     card_total = scd.Classes
#
#     url = '/customers/classcards?cuID=1002'
#     client.get(url)
#     assert client.status == 200
#     assert unicode(card_total - 1) + ' Classes remaining' in client.text
#
#     # check again after cancelling booking (manually); should be equal to total classes available on card
#     row = web2py.db.classes_attendance(1)
#     row.BookingStatus = 'cancelled'
#     row.update_record()
#
#     web2py.db.commit()
#
#     url = '/customers/classcards?cuID=1002'
#     client.get(url)
#     assert client.status == 200
#     assert unicode(card_total) + ' Classes remaining' in client.text

def test_class_book_subscription(client, web2py):
    """
        Can we book a class on a subscription?
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    classdate = '2014-01-06'
    prepare_classes(web2py, attendance=False, credits=True)

    assert web2py.db(web2py.db.classes_attendance).count() == 0

    url = '/classes/class_book?csID=1&date=2014-01-06&cuID=1001&clsID=1'
    client.get(url)
    assert client.status == 200

    clatt = web2py.db.classes_attendance(1)
    assert clatt.ClassDate == datetime.date(2014, 1, 6)
    assert clatt.classes_id == 1
    assert clatt.auth_customer_id == 1001
    assert clatt.customers_subscriptions_id == 1
    assert clatt.AttendanceType is None


def test_class_book_classcard(client, web2py):
    """
        Can we book a class on a card?
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    classdate = '2014-01-06'
    prepare_classes(web2py, attendance=False)

    assert web2py.db(web2py.db.classes_attendance).count() == 0

    url = '/classes/class_book?ccdID=1&date=2014-01-06&cuID=1001&clsID=1'
    client.get(url)
    assert client.status == 200

    clatt = web2py.db.classes_attendance(1)
    assert clatt.ClassDate == datetime.date(2014, 1, 6)
    assert clatt.classes_id == 1
    assert clatt.auth_customer_id == 1001
    assert clatt.customers_classcards_id == 1
    assert clatt.AttendanceType == 3


def test_class_book_dropin(client, web2py):
    """
        Can we book a class as drop in?
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    classdate = '2014-01-06'
    prepare_classes(web2py, attendance=False)

    assert web2py.db(web2py.db.classes_attendance).count() == 0

    url = '/classes/class_book?dropin=true&date=2014-01-06&cuID=1001&clsID=1'
    client.get(url)
    assert client.status == 200

    clatt = web2py.db.classes_attendance(1)
    assert clatt.ClassDate == datetime.date(2014, 1, 6)
    assert clatt.classes_id == 1
    assert clatt.auth_customer_id == 1001
    assert clatt.AttendanceType == 2

    # Invoice created?
    query = (web2py.db.invoices.id > 0)
    assert web2py.db(query).count() == 1

    invoice = web2py.db.invoices(1)
    ig_100 = web2py.db.invoices_groups(100)
    assert ig_100.Terms == invoice.Terms
    assert ig_100.Footer == invoice.Footer


def test_class_book_dropin_membership_invoice_amounts(client, web2py):
    """
        Are membership prices put on the invoice for drop in classes?
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    classdate = '2014-01-06'
    prepare_classes(web2py, attendance=False)
    populate_customers_with_memberships(web2py, customers_populated=True)

    assert web2py.db(web2py.db.classes_attendance).count() == 0

    url = '/classes/class_book?dropin=true&date=2014-01-06&cuID=1001&clsID=1'
    client.get(url)
    assert client.status == 200

    # Invoice created?
    query = (web2py.db.invoices.id > 0)
    assert web2py.db(query).count() == 1

    # Invoice item amounts?
    prices = web2py.db.classes_price(1)
    item = web2py.db.invoices_items(1)
    assert item.TotalPriceVAT == prices.DropinMembership
    assert item.tax_rates_id == prices.tax_rates_id_dropin_membership


def test_class_book_trial(client, web2py):
    """
        Can we book a class as trial class?
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    classdate = '2014-01-06'
    prepare_classes(web2py, attendance=False)

    assert web2py.db(web2py.db.classes_attendance).count() == 0

    url = '/classes/class_book?trial=true&date=2014-01-06&cuID=1001&clsID=1'
    client.get(url)
    assert client.status == 200

    clatt = web2py.db.classes_attendance(1)
    assert clatt.ClassDate == datetime.date(2014, 1, 6)
    assert clatt.classes_id == 1
    assert clatt.auth_customer_id == 1001
    assert clatt.AttendanceType == 1

    # Invoice created?
    query = (web2py.db.invoices.id > 0)
    assert web2py.db(query).count() == 1

    invoice = web2py.db.invoices(1)
    ig_100 = web2py.db.invoices_groups(100)
    assert ig_100.Terms == invoice.Terms
    assert ig_100.Footer == invoice.Footer


def test_class_book_trial_membership_invoice_amounts(client, web2py):
    """
        Are membership prices put on the invoice for trial classes?
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    classdate = '2014-01-06'
    prepare_classes(web2py, attendance=False)
    populate_customers_with_memberships(web2py, customers_populated=True)

    assert web2py.db(web2py.db.classes_attendance).count() == 0

    url = '/classes/class_book?trial=true&date=2014-01-06&cuID=1001&clsID=1'
    client.get(url)
    assert client.status == 200

    # Invoice created?
    query = (web2py.db.invoices.id > 0)
    assert web2py.db(query).count() == 1

    # Invoice item amounts?
    prices = web2py.db.classes_price(1)
    item = web2py.db.invoices_items(1)
    assert item.TotalPriceVAT == prices.TrialMembership
    assert item.tax_rates_id == prices.tax_rates_id_trial_membership


def test_class_book_complementary(client, web2py):
    """
        Can we book a class as complementary?
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    classdate = '2014-01-06'
    prepare_classes(web2py, attendance=False)

    assert web2py.db(web2py.db.classes_attendance).count() == 0

    url = '/classes/class_book?complementary=true&date=2014-01-06&cuID=1001&clsID=1'
    client.get(url)
    assert client.status == 200

    clatt = web2py.db.classes_attendance(1)
    assert clatt.ClassDate == datetime.date(2014, 1, 6)
    assert clatt.classes_id == 1
    assert clatt.auth_customer_id == 1001
    assert clatt.AttendanceType == 4


def test_attendance_set_status_attending(client, web2py):
    """
        Can we change the status of an attendance record?
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    classdate = '2014-01-06'
    prepare_classes(web2py)
    assert web2py.db(web2py.db.classes_attendance).count() == 4

    url = '/classes/attendance_set_status?clattID=1&status=attending'
    client.get(url)
    assert client.status == 200

    clatt = web2py.db.classes_attendance(1)
    assert clatt.BookingStatus == 'attending'


def test_attendance_remove(client, web2py):
    """
        Can we remove attendance using JSON after adding it?
    """
    classdate = '2014-01-06'
    prepare_classes(web2py)
    assert web2py.db(web2py.db.classes_attendance).count() == 4

    # first visit the attendance page to set the session var used to determine where to redirect
    url = '/classes/attendance?clsID=1&date=' + classdate
    client.get(url)
    assert client.status == 200

    # now try to remove a customer from the attendance list
    url = '/classes/attendance_remove?clattID=1'
    client.get(url)
    assert client.status == 200

    # check redirect back to attendance
    assert 'Attendance' in client.text

    assert web2py.db(web2py.db.classes_attendance).count() == 2


def test_attendance_remove_cancel_invoice(client, web2py):
    """
        Test cancelling of invoice after removing attendance for drop in classes
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    classdate = '2014-01-06'
    prepare_classes(web2py, invoices=True)
    assert web2py.db(web2py.db.classes_attendance).count() == 4

    # first visit the attendance page to set the session var used to determine where to redirect
    url = '/classes/attendance?clsID=1&date=' + classdate
    client.get(url)
    assert client.status == 200


    # now try to remove a customer from the attendance list
    url = '/classes/attendance_remove?clattID=2'
    client.get(url)
    assert client.status == 200

    # check redirect back to attendance
    assert 'Attendance' in client.text

    assert web2py.db(web2py.db.invoices.Status == 'cancelled').count() == 1


def test_attendance_booking_options_request_review(client, web2py):
    """
        Is the subscription not allowed message shown to customers like it should?
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    prepare_classes(web2py)

    url = '/classes/attendance_booking_options?clsID=1&cuID=1001&date=2014-01-06'
    client.get(url)
    assert client.status == 200

    assert "Request review" in client.text


def test_attendance_booking_options_subscription_not_allowed(client, web2py):
    """
        Is the subscription not allowed message shown to customers like it should?
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    prepare_classes(web2py)

    query = (web2py.db.classes_school_subscriptions_groups.id > 0)
    web2py.db(query).delete()

    query = (web2py.db.customers_classcards.id > 0)
    web2py.db(query).delete()
    web2py.db.commit()


    url = '/classes/attendance_booking_options?clsID=1&cuID=1001&date=2014-01-06'
    client.get(url)
    assert client.status == 200

    assert "Not allowed for this class" in client.text


def test_attendance_booking_options_classcard_not_allowed(client, web2py):
    """
        Is the subscription not allowed message shown to customers like it should?
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    prepare_classes(web2py)

    query = (web2py.db.classes_school_classcards_groups.id > 0)
    web2py.db(query).delete()

    query = (web2py.db.customers_subscriptions.id > 0)
    web2py.db(query).delete()
    web2py.db.commit()

    url = '/classes/attendance_booking_options?clsID=1&cuID=1001&date=2014-01-06'
    client.get(url)
    assert client.status == 200

    assert "Not allowed for this class" in client.text


def test_attendance_teacher_notes(client, web2py):
    """
        Are the notes shown correctly?
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    prepare_classes(web2py)
    populate_customers_notes(web2py, customers=False)

    url = '/classes/attendance_teacher_notes?clsID=1&cuID=1001&date=2014-01-06'
    client.get(url)
    assert client.status == 200

    note_1 = web2py.db.customers_notes(1)
    note_2 = web2py.db.customers_notes(2)

    # Check backoffice notes aren't displayed
    assert not note_1.Note in client.text
    # Check teacher notes are displayed
    assert note_2.Note in client.text
    # Check injuries get a red label
    assert 'text-red' in client.text


def test_attendance_teacher_notes_add(client, web2py):
    """
        Can we add teacher notes?
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    prepare_classes(web2py)

    url = '/classes/attendance_teacher_notes?clsID=1&cuID=1001&date=2014-01-06'
    client.get(url)
    assert client.status == 200

    data = {
        'Note':'Bananas',
        'Injury':'on'
    }

    client.post(url, data=data)
    assert client.status == 200

    assert web2py.db(web2py.db.customers_notes).count() == 1


def test_attendance_teacher_notes_edit(client, web2py):
    """
        Can we edit teacher notes?
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    prepare_classes(web2py)
    populate_customers_notes(web2py, customers=False)

    url = '/classes/attendance_teacher_note_edit?clsID=1&cuID=1001&date=2014-01-06&cnID=2'
    client.get(url)
    assert client.status == 200
    assert 'Edit note' in client.text # Check the notification for the user to let them know we're editing is showing

    data = {
        'id':2,
        'Note':'Bananas',
        'Injury':'on'
    }

    client.post(url, data=data)
    assert client.status == 200

    assert web2py.db.customers_notes(2).Note == data['Note']


def test_attendance_teacher_notes_delete(client, web2py):
    """
        Can we delete teacher notes?
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    prepare_classes(web2py)
    populate_customers_notes(web2py, customers=False)

    query = (web2py.db.customers_notes.TeacherNote == True)
    notes_count_before = web2py.db(query).count()

    url = '/classes/attendance_teacher_note_delete?clsID=1&cuID=1001&date=2014-01-06&cnID=2'
    client.get(url)
    assert client.status == 200

    assert (notes_count_before - 1) == web2py.db(query).count()


def test_attendance_teacher_notes_recent_and_injury(client, web2py):
    """
        Are recent notes (made within the last 3 months) shown in the classes/attendance page
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    prepare_classes(web2py, attendance=True)
    populate_customers_notes(web2py, customers=False)

    clattID = web2py.db.classes_attendance.insert(
        auth_customer_id=1001,
        classes_id='1',
        ClassDate='2015-01-05',  # this is a Monday ( week_day for the class defined above = 1 )
        AttendanceType='1')

    web2py.db.commit()

    url = '/classes/attendance?clsID=1&date=2015-01-05'
    client.get(url)
    assert client.status == 200

    assert '1 Recent note' in client.text
    assert '1 Injury' in client.text


def test_attendance_teacher_notes_injury_status(client, web2py):
    """
        Can we update the injury status for a note?
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    prepare_classes(web2py, attendance=True)
    populate_customers_notes(web2py, customers=False)

    url = '/classes/attendance_teacher_notes_injury_status?clsID=1&cnID=2&date=2014-01-06'
    client.get(url)
    assert client.status == 200

    assert web2py.db.customers_notes(2).Injury == False

#TODO: Update this test for class_book classes taken
# def test_attendance_classcard_class_count_classestaken(client, web2py):
#     """
#         Is the class count increased when a class is added to a customer?
#     """
#     populate_classes(web2py)
#
#     nr_cards = 1
#     populate_school_classcards(web2py, nr_cards, trialcard = True)
#     populate_customers(web2py, 1)
#
#     web2py.db.customers_classcards.insert(
#         school_classcards_id = 1,
#         auth_customer_id     = 1001,
#         Startdate            = '2014-01-01')
#     web2py.db.commit()
#
#     # test adding class and check count
#     url = '/classes/attendance_sign_in_classcard?cuID=1001&clsID=1&ccdID=1&date=2014-01-06'
#     client.get(url)
#     assert client.status == 200
#
#     assert web2py.db(web2py.db.classes_attendance).count() == 1
#     assert web2py.db.classes_attendance(1).customers_classcards_id == 1
#
#     classcard = web2py.db.customers_classcards(1)
#     assert classcard.ClassesTaken == 1
#
#     # test count after removing
#     url = '/classes/attendance_remove?cuID=1001&clsID=1&date=2014-01-06'
#     client.get(url)
#     assert client.status == 200
#
#     classcard = web2py.db.customers_classcards(1)
#     assert classcard.ClassesTaken == 0


def test_classes_override_attendance(client, web2py):
    """
        Does the override attendance page work?
    """
    populate_classes(web2py)
    assert web2py.db(web2py.db.classes).count() == 1

    url = '/classes/attendance_override?clsID=1&date=2014-01-06'
    client.get(url)
    assert client.status == 200

    data = dict(Amount='123456')
    client.post(url, data=data)
    assert client.status == 200
    assert 'Saved' in client.text # check redirection to same page
    query = (web2py.db.classes_attendance_override.Amount ==
             data['Amount'])
    assert web2py.db(query).count() == 1

    # now can we edit it

    client.get(url)
    assert client.status == 200
    assert data['Amount'] in client.text

    update_data = dict(id=1,
                       Amount='987654')
    client.post(url, data=update_data)
    assert client.status == 200
    assert 'Saved' in client.text # check redirection to same page
    query = (web2py.db.classes_attendance_override.Amount ==
             update_data['Amount'])
    assert web2py.db(query).count() == 1


def test_classes_otc_status_cancelled(client, web2py):
    """
        Does the cancel status work?
    """
    populate_classes(web2py)
    assert web2py.db(web2py.db.classes).count() == 1

    classes_id = '1'
    classdate = '2014-01-06'

    # check cancelling class
    url = '/classes/class_edit_on_date?clsID=' + classes_id + '&date=' + classdate
    client.get(url)
    assert client.status == 200

    data = {
        'Status':'cancelled'
    }

    client.post(url, data=data)
    assert client.status == 200
    assert 'Saved' in client.text

    cotc = web2py.db.classes_otc(1)
    assert cotc.Status == data['Status']


def test_classes_otc_status_open(client, web2py):
    """
        Does the cancel status work?
    """
    populate_classes(web2py)
    assert web2py.db(web2py.db.classes).count() == 1

    classes_id = '1'
    classdate = '2014-01-06'

    # check cancelling class
    url = '/classes/class_edit_on_date?clsID=' + classes_id + '&date=' + classdate
    client.get(url)
    assert client.status == 200

    data = {
        'Status':'open'
    }

    client.post(url, data=data)
    assert client.status == 200
    assert 'Saved' in client.text

    cotc = web2py.db.classes_otc(1)
    assert cotc.Status == data['Status']


def test_classes_open(client, web2py):
    """
        Check if classes appear on the classes_open list
    """
    populate_classes(web2py)
    assert web2py.db(web2py.db.classes).count() == 1

    # get 2 mondays later than today
    delta = datetime.timedelta(days=7)
    today = datetime.date.today()
    next_monday = next_weekday(today, 0) # 0 = Monday, 1=Tuesday, 2=Wednesday...
    monday_after_that = next_monday + delta

    web2py.db.classes_otc.insert(
        Status = 'open',
        classes_id = 1,
        ClassDate = next_monday )
    web2py.db.classes_otc.insert(
        Status = 'open',
        classes_id = 1,
        ClassDate = monday_after_that,
        school_locations_id = 2,
        school_classtypes_id = 2)
    web2py.db.classes_otc.insert(
        Status = 'open',
        classes_id = 1,
        ClassDate = '2014-01-06' )

    web2py.db.commit()

    assert web2py.db(web2py.db.classes_otc.Status == 'open').count() == 3

    # get the page
    url = '/classes/classes_open'
    client.get(url)
    assert client.status == 200

    # past open classes shouldn't be shown
    assert '2014-01-06' not in client.text
    # future ones should be shown
    assert unicode(next_monday) in client.text
    assert unicode(monday_after_that) in client.text

    # check location & classtype from classes_otc
    location = web2py.db.school_locations(2).Name.split(' ')[0]
    assert location in client.text
    classtype = web2py.db.school_classtypes(2).Name.split(' ')[0]
    assert classtype in client.text


def test_overlapping_workshops(client, web2py):
    """
        Test if the overlapping workshop activities show up
    """
    populate_workshop_activity_overlapping_class(web2py)

    # test overlapping page
    url = '/classes/overlapping_workshops?year=2014&week=2'
    client.get(url)
    assert client.status == 200
    activity = web2py.db.workshops_activities(1)
    assert activity.Activity.split(' ')[0] in client.text


def test_overlapping_workshops_count(client, web2py):
    """
        Test if the count shows up correctly for overlapping workshops
        in the shedule
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_workshop_activity_overlapping_class(web2py)

    # set schedule session vars first
    url = '/classes/schedule?schedule_year=2014&schedule_week=2'
    client.get(url)
    assert client.status == 200

    url = '/classes/schedule_get_overlapping_workshops.load'
    client.get(url)
    assert client.status == 200

    # check badge on the schedule page
    assert '<span class="badge">1</span>' in client.text


def test_class_teachers(client, web2py):
    """
        Test if we can get a list of teachers for a class
    """
    populate_classes(web2py)
    assert web2py.db(web2py.db.classes).count() == 1

    url = '/classes/class_teachers?clsID=1'
    client.get(url)
    assert client.status == 200

    teacher = web2py.db.auth_user(2)

    assert teacher.first_name in client.text


def test_class_teacher_add(client, web2py):
    """
        Test if we can add a teacher
    """
    populate_classes(web2py)
    assert web2py.db(web2py.db.classes).count() == 1

    url = '/classes/class_teacher_add?clsID=1'
    client.get(url)
    assert client.status == 200

    data = dict(auth_teacher_id=2,
                Startdate='2014-01-01',
                Enddate='2014-02-01')
    client.post(url, data=data)
    assert client.status == 200

    assert web2py.db(web2py.db.classes_teachers).count() == 2
    teacher = web2py.db.auth_user(2)

    assert teacher.first_name in client.text

def test_class_teacher_edit(client, web2py):
    """
        Test if we can edit a teacher
    """
    populate_classes(web2py)
    assert web2py.db(web2py.db.classes).count() == 1

    url = '/classes/class_teacher_edit?clsID=1&cltID=1'
    client.get(url)
    assert client.status == 200

    data = dict(id=1,
                classes_id=1,
                auth_teacher_id=3,
                Startdate='2014-01-01',
                Enddate='2014-02-01')
    client.post(url, data=data)
    assert client.status == 200

    teacher = web2py.db.auth_user(3)
    assert teacher.first_name in client.text


def test_class_prices(client, web2py):
    """
        Test if we can get a list of prices for a class
    """
    populate_classes(web2py)
    assert web2py.db(web2py.db.classes).count() == 1

    url = '/classes/class_teachers?clsID=1'
    client.get(url)
    assert client.status == 200

    class_price = web2py.db.classes_price(1)

    assert unicode(class_price.Startdate) in client.text


def test_class_price_add(client, web2py):
    """
        Test if we can add a price
    """
    populate_classes(web2py)
    assert web2py.db(web2py.db.classes).count() == 1

    url = '/classes/class_price_add?clsID=1'
    client.get(url)
    assert client.status == 200

    data = dict(Dropin=254098303,
                tax_rates_id_dropin=1,
                Trial=1324243,
                tax_rates_id_trial=1,
                DropinMembership=1230987,
                tax_rates_id_dropin_membership=1,
                TrialMembership=934579,
                tax_rates_id_trial_membership=1,
                Startdate='2014-01-01',
                Enddate='2014-02-01')
    client.post(url, data=data)
    assert client.status == 200

    assert web2py.db(web2py.db.classes_price).count() == 2
    price = format(web2py.db.classes_price(2).Dropin, '.2f')

    assert price in client.text


def test_class_price_edit(client, web2py):
    """
        Test if we can edit a teacher
    """
    populate_classes(web2py)
    assert web2py.db(web2py.db.classes).count() == 1

    url = '/classes/class_price_edit?clsID=1&clpID=1'
    client.get(url)
    assert client.status == 200

    data = dict(
        id = 1,
        Dropin=254098303,
        tax_rates_id_dropin=1,
        Trial=1324243,
        tax_rates_id_trial=1,
        DropinMembership=1230987,
        tax_rates_id_dropin_membership=1,
        TrialMembership=934579,
        tax_rates_id_trial_membership=1,
        Startdate='2014-01-01',
        Enddate='2014-02-01'
    )
    client.post(url, data=data)
    assert client.status == 200

    assert web2py.db(web2py.db.classes_price).count() == 1

    price = format(web2py.db.classes_price(1).Dropin, '.2f')

    assert price in client.text


def test_class_teacher_display_schedule(client, web2py):
    """
        Test whether a teacher shows up currectly in the schedule
    """
    populate_classes(web2py)
    assert web2py.db(web2py.db.classes).count() == 1

    url = '/classes/schedule'
    client.get(url)
    assert client.status == 200

    teacher = web2py.db.auth_user(2)
    assert teacher.first_name in client.text


def test_class_edit_notification_no_subscription_or_classcard_group(client, web2py):
    """
        Is a notification shown to the user when no subscription or class card groups are assigned to a class
    """
    prepare_classes(web2py)

    web2py.db(web2py.db.classes_school_subscriptions_groups.id > 0).delete()
    web2py.db(web2py.db.classes_school_classcards_groups.id > 0).delete()

    web2py.db.commit()

    url = '/classes/class_edit?clsID=1'
    client.get(url)
    assert client.status == 200

    assert 'No subscription groups or class card groups have been' in client.text


def test_class_subscriptions(client, web2py):
    """
        Are school_subscription_groups listed correctly
    """
    # get random url to initialize web2py environnment
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    prepare_classes(web2py)
    populate_school_subscriptions_groups(web2py)

    web2py.db.classes_school_subscriptions_groups.insert(
        classes_id = 1,
        school_subscriptions_groups_id = 1,
        Enroll = True,
        ShopBook = True,
        Attend = True
    )

    web2py.db.commit()

    url = '/classes/class_subscriptions?clsID=1'
    client.get(url)
    assert client.status == 200

    ssg = web2py.db.school_subscriptions_groups(1)
    assert ssg.Name in client.text


def test_class_subscription_group_add(client, web2py):
    """
        Can we add a subscription group to a class
    """
    # get random url to initialize web2py environnment
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    prepare_classes(web2py)

    query = (web2py.db.classes_school_subscriptions_groups.id > 0)
    web2py.db(query).delete()
    web2py.db.commit()

    url = '/classes/class_subscription_group_add?clsID=1'
    client.get(url)
    assert client.status == 200

    ssgID = 1

    data = {
        'school_subscriptions_groups_id':ssgID,
        'Enroll':'on'
    }

    client.post(url, data=data)
    assert client.status == 200

    ssg = web2py.db.school_subscriptions_groups(ssgID)
    assert ssg.Name in client.text

    # Is there something in the db now?
    query = (web2py.db.classes_school_subscriptions_groups.classes_id == 1)
    assert web2py.db(query).count() == 1

    # Is the Attend field set when setting enroll like it should?
    cssg = web2py.db.classes_school_subscriptions_groups(2)
    assert cssg.Attend == True

    # Check that we can't add the same group twice
    client.get(url)
    assert client.status == 200

    assert ssg.Name not in client.text


def test_class_subscription_group_edit(client, web2py):
    """
        Can we add a subscription group to a class
    """
    # get random url to initialize web2py environnment
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    prepare_classes(web2py)

    cssgID = web2py.db.classes_school_subscriptions_groups.insert(
        classes_id = 1,
        school_subscriptions_groups_id = 1,
        Enroll = True,
        ShopBook = True,
        Attend = True
    )

    web2py.db.commit()

    url = '/classes/class_subscription_group_edit?clsID=1&cssgID=' + unicode(cssgID)
    client.get(url)
    assert client.status == 200

    data = {
        'id':cssgID,
        'Enroll':'on',
        'ShopBook':'',
        'Attend':'',

    }

    client.post(url, data=data)
    assert client.status == 200

    assert web2py.db.classes_school_subscriptions_groups(1).Enroll == True
    assert web2py.db.classes_school_subscriptions_groups(1).Attend == True


def test_class_subscription_group_delete(client, web2py):
    """
        Can we delete a subscription group?
    """
    # get random url to initialize web2py environnment
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    prepare_classes(web2py)
    populate_school_subscriptions_groups(web2py)


    url = '/classes/class_subscription_group_delete?clsID=1&cssgID=' + unicode(1)
    client.get(url)
    assert client.status == 200

    query = (web2py.db.classes_school_subscriptions_groups.id > 0)
    assert web2py.db(query).count() == 0


def test_class_copy_subscription_classcards(client, web2py):
    """
        Is the page to list other classes to copy subscription and classcard setting from working?
    """
    # get random url to initialize web2py environnment
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    prepare_classes(web2py)

    url = '/classes/class_copy_subscriptions_classcards?clsID=2'
    client.get(url)
    assert client.status == 200

    next_monday = next_weekday(datetime.date.today(), 0)

    data = {'class_date':next_monday}

    client.post(url, data=data)
    assert client.status == 200

    # verify listing of class 1
    cls = web2py.db.classes(1)
    location = web2py.db.school_locations(cls.school_locations_id)
    assert location.Name in client.text


def test_class_copy_subscription_classcards_execute(client, web2py):
    """
        Can we copy subscription and classcards settings from another class?
    """
    # get random url to initialize web2py environnment
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    prepare_classes(web2py)

    url = '/classes/class_copy_subscriptions_classcards_execute?clsID_from=1&clsID_to=2'
    client.get(url)
    assert client.status == 200

    cssg = web2py.db.classes_school_subscriptions_groups(1)
    cscg = web2py.db.classes_school_classcards_groups(1)
    cssg2 = web2py.db.classes_school_subscriptions_groups(2)
    cscg2 = web2py.db.classes_school_classcards_groups(2)

    assert cssg.Enroll == cssg2.Enroll
    assert cssg.ShopBook == cssg2.ShopBook
    assert cssg.Attend == cssg2.Attend
    
    assert cscg.Enroll == cscg2.Enroll
    assert cscg.ShopBook == cscg2.ShopBook
    assert cscg.Attend == cscg2.Attend
    
    
def test_class_classcards(client, web2py):
    """
        Are school_classcard_groups listed correctly
    """
    # get random url to initialize web2py environnment
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    prepare_classes(web2py)
    populate_school_classcards_groups(web2py)

    web2py.db.classes_school_classcards_groups.insert(
        classes_id = 1,
        school_classcards_groups_id = 1,
        Enroll = True,
        ShopBook = True,
        Attend = True
    )

    web2py.db.commit()

    url = '/classes/class_classcards?clsID=1'
    client.get(url)
    assert client.status == 200

    ssg = web2py.db.school_classcards_groups(1)
    assert ssg.Name in client.text


def test_class_classcard_group_add(client, web2py):
    """
        Can we add a classcard group to a class
    """
    # get random url to initialize web2py environnment
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    prepare_classes(web2py)

    query = (web2py.db.classes_school_classcards_groups.id > 0)
    web2py.db(query).delete()
    web2py.db.commit()


    url = '/classes/class_classcard_group_add?clsID=1'
    client.get(url)
    assert client.status == 200

    ssgID = 1

    data = {
        'school_classcards_groups_id':ssgID,
        'ShopBook':'on'
    }

    client.post(url, data=data)
    assert client.status == 200

    ssg = web2py.db.school_classcards_groups(ssgID)
    assert ssg.Name in client.text

    # Is there something in the db now?
    query = (web2py.db.classes_school_classcards_groups.classes_id == 1)
    assert web2py.db(query).count() == 1

    # Is the Attend field set when setting enroll like it should?
    cscg = web2py.db.classes_school_classcards_groups(2)
    assert cscg.Attend == True

    # Check that we can't add the same group twice
    client.get(url)
    assert ssg.Name not in client.text


def test_class_classcard_group_edit(client, web2py):
    """
        Can we add a classcard group to a class
    """
    # get random url to initialize web2py environnment
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    prepare_classes(web2py)


    cscgID = 1
    url = '/classes/class_classcard_group_edit?clsID=1&cssgID=' + unicode(cscgID)
    client.get(url)
    assert client.status == 200

    data = {
        'id':cscgID,
        'Enroll':'on',
        'ShopBook':'',
        'Attend':'',

    }

    client.post(url, data=data)
    assert client.status == 200

    assert web2py.db.classes_school_classcards_groups(cscgID).Enroll == True
    assert web2py.db.classes_school_classcards_groups(cscgID).Attend == True


def test_class_classcard_group_delete(client, web2py):
    """
        Can we delete a classcard group?
    """
    # get random url to initialize web2py environnment
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    prepare_classes(web2py)

    cscgID = 1
    url = '/classes/class_classcard_group_delete?clsID=1&cssgID=' + unicode(cscgID)
    client.get(url)
    assert client.status == 200

    query = (web2py.db.classes_school_classcards_groups)
    assert web2py.db(query).count() == 0



#TODO: move this test to reports
# def test_teacher_classes(client, web2py):
#     """
#         Test if classes are listed for a teacher
#     """
#     populate_classes(web2py)
#
#     url = '/classes/teacher_classes?teachers_id=2&year=2014&month=1'
#     client.get(url)
#     assert client.status == 200
#
#     location = web2py.db.school_locations(1).Name.split(' ')[0]
#     assert location in client.text

#TODO: move this test to reports
# def test_teacher_classes_role_display(client, web2py):
#     """
#         Test if the role for teacher 2 is displayed correctly
#     """
#     populate_classes(web2py)
#
#     url = '/classes/teacher_classes?teachers_id=2&year=2014&month=1'
#     client.get(url)
#     assert client.status == 200
#
#     # check if the label for subteacher is applied
#     assert '<span class="os_label bg_light_blue">' in client.text


def test_school_holiday_display_schedule(client, web2py):
    """
        Is a holiday displayed properly in the schedule?
    """
    populate_classes(web2py)
    description = 'fslkdfjlkrjlkdf'
    web2py.db.school_holidays.insert(Description=description,
                                     Startdate='2014-01-01',
                                     Enddate='2014-01-30',
                                     Classes=True)
    web2py.db.school_holidays_locations.insert(
        school_locations_id = 1,
        school_holidays_id = 1)
    web2py.db.commit()

    url = '/classes/schedule?year=2014&week=2'
    client.get(url)
    assert client.status == 200

    assert description in client.text


def test_reservations(client, web2py):
    """
        Test list of reservations
    """
    prepare_classes(web2py)

    url = '/classes/reservations?filter=this&clsID=1&date=2014-01-06'
    client.get(url)
    assert client.status == 200

    assert client.text.count('Enrolled from 2014-01-01') == 1
    assert client.text.count('Drop in class on 2014-01-06') == 1
    assert client.text.count('Trial class on 2014-01-06') == 1


def test_reservation_maxreservations_recurring_reached(client, web2py):
    """
        Does a warning message show on the reservations page when the
        reservations count exceeds the Maxstudents for a class?
    """
    prepare_classes(web2py)

    # lower number of available spaces to get a warning
    cls = web2py.db.classes(1)
    cls.MaxReservationsRecurring = 1
    cls.update_record()

    # another recurring class reservation
    web2py.db.classes_reservation.insert(auth_customer_id=1002,
                                         classes_id='1',
                                         Startdate='2014-01-01',
                                         SingleClass=False,
                                         TrialClass=False)

    web2py.db.commit()

    url = '/classes/reservations?clsID=1&date=2014-01-06'
    client.get(url)
    assert client.status == 200

    assert 'Warning' in client.text


def test_reservation_choose(client, web2py):
    """
    Are allowed subscriptions listed?
    """
    url = '/user/login'
    client.get(url)
    assert client.status == 200

    prepare_classes(web2py)

    url = '/classes/reservation_add_choose?clsID=1&cuID=1001&date=2014-01-01'
    client.get(url)
    assert client.status == 200

    ssu = web2py.db.school_subscriptions(1)
    assert ssu.Name in client.text


def test_reservation_add(client, web2py):
    """
    Can we add a reservation?
    """
    url = '/user/login'
    client.get(url)
    assert client.status == 200

    prepare_classes(web2py, with_reservations=False)

    url = '/classes/class_enroll?clsID=1&csID=1&cuID=1001&date=2014-01-06'
    client.get(url)
    assert client.status == 200

    data = {
        'Startdate': '2014-01-01',
        'Enddate': '2014-01-31'
    }

    client.post(url, data=data)
    assert client.status == 200

    clr = web2py.db.classes_reservation(1)
    assert clr.Startdate == datetime.date(2014, 1, 1)
    assert clr.Enddate == datetime.date(2014, 1, 31)

    # Check classes booked
    query = (web2py.db.classes_attendance.ClassDate == datetime.date(2014, 1, 6)) & \
            (web2py.db.classes_attendance.auth_customer_id == 1001) & \
            (web2py.db.classes_attendance.BookingStatus == 'booked') & \
            (web2py.db.classes_attendance.classes_id == 1)
    assert web2py.db(query).count() == 1


def test_reservation_edit(client, web2py):
    """
    Can we edit a reservation?
    """
    url = '/user/login'
    client.get(url)
    assert client.status == 200

    prepare_classes(web2py)

    url = '/classes/reservation_edit?clsID=1&crID=1&date=2014-01-06'
    client.get(url)
    assert client.status == 200

    data = {
        'id': 1,
        'Startdate': '2014-01-21',
        'Enddate': '2014-01-31'
    }

    client.post(url, data=data)
    assert client.status == 200

    clr = web2py.db.classes_reservation(1)
    assert clr.Startdate == datetime.date(2014, 1, 21)
    assert clr.Enddate == datetime.date(2014, 1, 31)


def test_reservations_recurring(client, web2py):
    """
        List reservations for a customer (this is the default)
    """
    prepare_classes(web2py)

    url = '/classes/reservations?filter=recurring&clsID=1&date=2014-01-06'
    client.get(url)
    assert client.status == 200

    assert client.text.count('Enrolled from 2014-01-01') == 1


def test_notes(client, web2py):
    """
        Test list of class notes
    """
    prepare_classes(web2py)

    note = web2py.db.classes_notes(1)

    url = '/classes/notes?clsID=1&date=2014-01-06'
    client.get(url)
    assert client.status == 200

    assert note['Note'] in client.text


def test_notes_add(client, web2py):
    """
        Can we add a note?
    """
    prepare_classes(web2py)

    url = '/classes/notes?clsID=1&date=2014-01-06'
    client.get(url)
    assert client.status == 200

    data = {'classes_id' : 1,
            'ClassDate' : '2014-01-06',
            'auth_user' : 1002,
            'TeacherNote' : True,
            'Note' : 'Cherries'}

    client.post(url, data=data)
    assert client.status == 200

    assert data['Note'] in client.text
    assert web2py.db(web2py.db.classes_notes).count() == 2


def test_notes_edit(client, web2py):
    """
        Can we edit a note?
    """
    prepare_classes(web2py)

    url = '/classes/note_edit?clsID=1&date=2014-01-06&cnID=1'
    client.get(url)
    assert client.status == 200

    data = {'id' : 1,
            'classes_id' : 1,
            'ClassDate' : '2014-01-06',
            'auth_user' : 1002,
            'TeacherNote' : True,
            'Note' : 'Cherries'}

    client.post(url, data=data)
    assert client.status == 200

    assert data['Note'] in client.text
    assert web2py.db(web2py.db.classes_notes).count() == 1


def test_notes_delete(client, web2py):
    """
        Can we delete a note?
    """
    prepare_classes(web2py)

    url = '/classes/note_delete?clsID=1&date=2014-01-06&cnID=1'
    client.get(url)
    assert client.status == 200

    assert web2py.db(web2py.db.classes_notes).count() == 0


def test_subs_manage_pending(client, web2py):
    """
    Manage sub requests
    """
    prepare_classes_otc_subs_avail(web2py, accepted=None)

    url = '/classes/subs_manage'
    client.get(url)
    assert client.status == 200

    cotcsa = web2py.db.classes_otc_sub_avail(1)
    cotc = web2py.db.classes_otc(cotcsa.classes_otc_id)

    assert unicode(cotc.ClassDate) in client.text


def test_subs_manage_processed(client, web2py):
    """
    Manage sub requests
    """
    prepare_classes_otc_subs_avail(web2py, accepted=True)

    url = '/classes/subs_manage?Status=processed'
    client.get(url)
    assert client.status == 200

    cotcsa = web2py.db.classes_otc_sub_avail(1)
    cotc = web2py.db.classes_otc(cotcsa.classes_otc_id)

    assert unicode(cotc.ClassDate) in client.text


def test_sub_avail_accept(client, web2py):
    """
    Are cotcsa rows accepted correctly?
    """
    prepare_classes_otc_subs_avail(web2py, accepted=None)

    url = '/classes/sub_avail_accept?cotcsaID=1'
    client.get(url)
    assert client.status == 200

    cotcsa = web2py.db.classes_otc_sub_avail(1)
    assert cotcsa.Accepted == True


def test_sub_avail_decline(client, web2py):
    """
    Are cotcsa rows declined correctly?
    """
    prepare_classes_otc_subs_avail(web2py, accepted=None)

    url = '/classes/sub_avail_decline?cotcsaID=1'
    client.get(url)
    assert client.status == 200

    cotcsa = web2py.db.classes_otc_sub_avail(1)
    assert cotcsa.Accepted == False