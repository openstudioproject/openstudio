# -*- coding: utf-8 -*-

"""
    py.test test cases to test OpenStudio.
    These tests run based on webclient and need web2py server running.
"""

import datetime

from gluon.contrib.populate import populate

from populate_os_tables import populate_customers
from populate_os_tables import populate_customers_payment_info
from populate_os_tables import populate_customers_with_subscriptions
from populate_os_tables import populate_customers_with_memberships
from populate_os_tables import prepare_classes
from populate_os_tables import populate_school_classcards
from populate_os_tables import populate_school_subscriptions
from populate_os_tables import populate_school_memberships
from populate_os_tables import populate_customers_shoppingcart
from populate_os_tables import populate_customers_orders
from populate_os_tables import populate_customers_orders_items
from populate_os_tables import populate_payment_methods
from populate_os_tables import populate_sys_organizations
from populate_os_tables import populate_workshops
from populate_os_tables import populate_workshops_for_api_tests
from populate_os_tables import populate_invoices
from populate_os_tables import populate_invoices_items
from populate_os_tables import populate_tax_rates


from setup_profile_tests import setup_profile_tests


def next_weekday(d, weekday):
    """
        Function to find next weekday after given date
    """
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)


def test_class_checkout(client, web2py):
    """
    Test class checkout
    """
    setup_profile_tests(web2py)
    prepare_classes(web2py)
    today = datetime.date.today()

    next_monday = next_weekday(today, 0)

    url = '/shop/class_checkout?clsID=1&dropin=true&date=' + str(next_monday)
    client.get(url)
    assert client.status == 200

    location = web2py.db.school_locations(1)
    classtype = web2py.db.school_classtypes(1)

    assert location.Name in client.text
    assert classtype.Name in client.text

    assert "Anything you'd like" in client.text


    # Test /shop/class_order, we should be redirected after submitting
    data = {
        'CustomerNote': "my message"
    }

    client.post(url, data=data)
    assert client.status == 200

    assert "Order summary" in client.text
    assert str(next_monday) in client.text
    assert "Pay now" in client.text
    assert data['CustomerNote'] in client.text

    assert web2py.db(web2py.db.customers_orders).count() > 0


def test_classcard(client, web2py):
    """
    Test classcard info page
    """
    setup_profile_tests(web2py)
    populate_school_memberships(web2py)
    populate_school_classcards(web2py, school_memberships_id=1)

    url = '/shop/classcard?scdID=1'
    client.get(url)
    assert client.status == 200

    scd = web2py.db.school_classcards(1)
    assert scd.Name in client.text
    ms = web2py.db.school_memberships(1)
    assert ms.Name in client.text

    # Test order
    data = {
        'CustomerNote': "my message"
    }

    client.post(url, data=data)
    assert client.status == 200

    assert "Order summary" in client.text
    assert "Pay now" in client.text
    assert data['CustomerNote'] in client.text

    assert web2py.db(web2py.db.customers_orders).count() > 0



def test_subscription(client, web2py):
    """
    Test classcard info page
    """
    setup_profile_tests(web2py)
    populate_school_memberships(web2py)
    populate_school_subscriptions(web2py, school_memberships_id=1)

    url = '/shop/subscription?ssuID=1'
    client.get(url)
    assert client.status == 200

    ssu = web2py.db.school_subscriptions(1)
    assert ssu.Name in client.text
    ms = web2py.db.school_memberships(1)
    assert ms.Name in client.text

    # Test order
    data = {
        'CustomerNote': "my message"
    }

    client.post(url, data=data)
    assert client.status == 200

    assert "Order summary" in client.text
    assert "Pay now" in client.text
    assert data['CustomerNote'] in client.text

    assert web2py.db(web2py.db.customers_orders).count() > 0


def test_membership(client, web2py):
    """
    Test classcard info page
    """
    setup_profile_tests(web2py)
    populate_school_memberships(web2py)

    url = '/shop/membership?smID=1'
    client.get(url)
    assert client.status == 200

    ms = web2py.db.school_memberships(1)
    assert ms.Name in client.text

    # Test order
    data = {
        'CustomerNote': "my message"
    }

    client.post(url, data=data)
    assert client.status == 200

    assert "Order summary" in client.text
    assert "Pay now" in client.text
    assert data['CustomerNote'] in client.text

    assert web2py.db(web2py.db.customers_orders).count() > 0


def test_event_ticket(client, web2py):
    """
    Test event ticket order creation page
    """
    setup_profile_tests(web2py)

    # populate workshops table
    populate_workshops(web2py)

    url = '/shop/event_ticket?wspID=1'
    client.get(url)
    assert client.status == 200

    wsp = web2py.db.workshops_products(1)
    ws = web2py.db.workshops(1)

    assert wsp.Name in client.text
    assert ws.Name in client.text

    # Test order
    data = {
        'CustomerNote': "my message"
    }

    client.post(url, data=data)
    assert client.status == 200

    assert "Order summary" in client.text
    assert "Pay now" in client.text
    assert data['CustomerNote'] in client.text

    assert web2py.db(web2py.db.customers_orders).count() > 0


def test_customers_shop_features(client, web2py):
    """
        Are the settings to control of which pages to show in the shop working?
    """
    setup_profile_tests(web2py)

    # get random url to setup OpenStudio environment
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    # Check classcards
    url = '/shop/classcards'
    client.get(url)
    assert client.status == 200
    assert not 'No cards available' in client.text

    # Check workshops
    url = '/shop/events'
    client.get(url)
    assert client.status == 200
    assert not 'No workshops available' in client.text

    # Check subscriptions
    url = '/shop/subscriptions'
    client.get(url)
    assert client.status == 200
    assert not 'No subscriptions available' in client.text

    # Check memberships
    url = '/shop/memberships'
    client.get(url)
    assert client.status == 200
    assert not 'No memberships available at this time' in client.text

    ## Change settings
    features = web2py.db.customers_shop_features(1)
    features.Classcards = False
    features.Workshops = False
    features.Subscriptions = False
    features.Memberships = False
    features.update_record()
    web2py.db.commit()
    # and check again

    # Check classcards
    url = '/shop/classcards'
    client.get(url)
    assert client.status == 200
    assert 'No cards available' in client.text

    url = '/shop/classcard'
    client.get(url)
    assert client.status == 200
    assert 'This feature is disabled' in client.text

    url = '/shop/classcard_order'
    client.get(url)
    assert client.status == 200
    assert 'This feature is disabled' in client.text

    # Check workshops
    url = '/shop/events'
    client.get(url)
    assert client.status == 200
    assert 'No workshops available' in client.text

    url = '/shop/event_ticket_order'
    client.get(url)
    assert client.status == 200
    assert 'This feature is disabled' in client.text

    # Check subscriptions
    url = '/shop/subscription'
    client.get(url)
    assert client.status == 200
    assert 'This feature is disabled' in client.text

    # Check memberships
    url = '/shop/memberships'
    client.get(url)
    assert client.status == 200
    assert 'No memberships available at this time' in client.text

    url = '/shop/membership'
    client.get(url)
    assert client.status == 200
    assert 'This feature is disabled' in client.text



def test_classes(client, web2py):
    """
        Is the page listing classes for a week working? 
    """
    prepare_classes(web2py)

    url = '/shop/classes'
    client.get(url)
    assert client.status == 200

    # check display of class name, teacher name, time and location name
    location = web2py.db.school_locations(1)
    classtype = web2py.db.school_classtypes(1)
    teacher = web2py.db.auth_user(2)
    cls = web2py.db.classes(1)
    time = cls.Starttime.strftime("%H:%M") + ' - ' + cls.Endtime.strftime("%H:%M")

    assert location.Name.split(' ')[0] in client.text
    assert classtype.Name.split(' ')[0] in client.text
    assert teacher.display_name in client.text
    assert time in client.text


def test_classes_booking_status_cancelled(client, web2py):
    """
        Check if we can book a class when it's not yet finished
        Check if we can't book a class if it's cancelled or in the past
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    next_monday = next_weekday(datetime.date.today(), 0)

    prepare_classes(web2py)
    web2py.db.classes_otc.insert(
        classes_id = 1,
        ClassDate = next_monday,
        Status = 'cancelled'
    )

    web2py.db.commit()

    # check past & cancelled classes
    url = '/shop/classes?date=' + str(next_monday)
    client.get(url)
    assert client.status == 200

    assert str(datetime.date.today().day) in client.text
    assert 'Cancelled' in client.text


def test_classes_booking_status_ok(client, web2py):
    """
        Check if we can book a class when it's not yet finished
        Check if we can't book a class if it's cancelled or in the past
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    next_monday = next_weekday(datetime.date.today(), 0)
    prepare_classes(web2py)

    # check bookable classes
    url = '/shop/classes?date=2099-12-23'
    client.get(url)
    assert client.status == 200

    # is the link to book a class on the page?
    assert '/shop/classes_book_options' in client.text


def test_classes_booking_status_full(client, web2py):
    """
        Check if we can book a class when it's not yet finished
        Check if we can't book a class if it's cancelled or in the past
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    next_monday = next_weekday(datetime.date.today(), 0)
    prepare_classes(web2py)

    # check current classes
    url = '/shop/classes?date=' + str(next_monday)
    client.get(url)
    assert client.status == 200

    # Check fully booked
    cls = web2py.db.classes(1)
    cls.MaxOnlineBooking = 1
    cls.update_record()

    web2py.db.classes_attendance.insert(
        auth_customer_id = 1001,
        classes_id = 1,
        ClassDate = next_monday,
        AttendanceType = None,
        customers_subscriptions_id = 1,
        online_booking = True
    )

    web2py.db.commit()

    client.get(url)
    assert client.status == 200

    # is the fully booked message showing
    assert 'Fully booked' in client.text


def test_classes_week_chooser(client, web2py):
    """
        Is the page listing classes for a week working? 
    """
    prepare_classes(web2py)

    url = '/shop/classes?date=' + str(datetime.date.today())
    client.get(url)
    assert client.status == 200

    # Check previous week link (& becomes &amp; because of client)
    assert 'href="#"' in client.text
    # Check next week link
    assert '/shop/classes?date=' + str(datetime.date.today() + datetime.timedelta(days=7)) in client.text


def test_classes_filter(client, web2py):
    """
        Is the page listing classes for a week working? 
    """
    prepare_classes(web2py)
    # Check location filter
    url = '/shop/classes?year=2014&week=2'
    client.get(url)
    assert client.status == 200


    # Check location filter
    url = '/shop/classes?year=2014&week=2&location=2'
    client.get(url)
    assert client.status == 200

    location_1 = web2py.db.school_locations(1)
    location_2 = web2py.db.school_locations(2)
    assert '<div class="col-md-2">' + location_1.Name + '</div>' not in client.text
    assert '<div class="col-md-2">' + location_2.Name in client.text


    # Check classtypes filter
    url = '/shop/classes?year=2014&week=2&classtype=2'
    client.get(url)
    assert client.status == 200

    ct_1 = web2py.db.school_classtypes(1)
    ct_2 = web2py.db.school_classtypes(2)
    assert '<div class="col-md-3">' + ct_1.Name not in client.text
    assert '<div class="col-md-3">' + ct_2.Name in client.text

    # Check teacher filter
    url = '/shop/classes?year=2014&week=2&teacher=3'
    client.get(url)
    assert client.status == 200

    te_2 = web2py.db.auth_user(2)
    te_3 = web2py.db.auth_user(3)
    assert '<div class="col-md-2">' + te_2.display_name not in client.text
    assert '<div class="col-md-2">' + te_3.display_name in client.text


def test_classes_book_options(client, web2py):
    """
        Is the page listing the booking options showing everything? 
    """
    url = '/user/login'
    client.get(url)
    assert client.status == 200

    setup_profile_tests(web2py)
    prepare_classes(web2py, credits=True)
    populate_school_subscriptions(web2py)
    populate_school_classcards(web2py, nr=2)

    csID = web2py.db.customers_subscriptions.insert(
        auth_customer_id = 300,
        school_subscriptions_id = 1,
        Startdate = '2014-01-01',
        payment_methods_id = 1)

    web2py.db.customers_subscriptions_credits.insert(
        customers_subscriptions_id = csID,
        MutationDateTime = '2014-01-01 00:00:00',
        MutationType = 'add',
        MutationAmount = '20',
        Description = 'test',
        SubscriptionYear = '2014',
        SubscriptionMonth = '1',
    )

    web2py.db.customers_classcards.insert(
        auth_customer_id = 300,
        school_classcards_id = 1,
        Startdate = '2014-01-01',
        Enddate = '2099-12-31'
    )

    trial_message = '82374238947239sddjshfk'
    web2py.db.sys_properties.insert(
        Property = 'shop_classes_trial_message',
        PropertyValue = trial_message
    )

    dropin_message = '823742sadtdfgd39sddjsh'
    web2py.db.sys_properties.insert(
        Property = 'shop_classes_dropin_message',
        PropertyValue = dropin_message
    )

    web2py.db.commit()

    next_monday = next_weekday(datetime.date.today(), 0)
    client.get('/shop/classes_book_options?clsID=1&date=' + str(next_monday))
    assert client.status == 200

    assert '<div class="col-md-3 bold">Subscription</div>' in client.text
    assert '<div class="col-md-3 bold">Class card</div>' in client.text
    assert '<div class="col-md-3 bold">Drop in</div>' in client.text
    assert '<div class="col-md-3 bold">Trial</div>' in client.text
    assert dropin_message in client.text
    assert trial_message in client.text

    # check drop in and trial price listing
    class_prices = web2py.db.classes_price(1)
    assert str(class_prices.Dropin) in client.text
    assert str(class_prices.Trial) in client.text

    # Check request review check-in option not available
    assert 'Request review' not in client.text


def test_classes_book_options_trial_disabled_from_system_settings(client, web2py):
    """
        Is the trial option disabled?
    """
    url = '/user/login'
    client.get(url)
    assert client.status == 200

    setup_profile_tests(web2py)
    prepare_classes(web2py, credits=True)

    sprop = web2py.db.sys_properties(Property='system_enable_class_checkin_trialclass')
    sprop.PropertyValue = ''
    sprop.update_record()

    web2py.db.commit()

    next_monday = next_weekday(datetime.date.today(), 0)
    client.get('/shop/classes_book_options?clsID=1&date=' + str(next_monday))
    assert client.status == 200

    assert '<div class="col-md-3 bold">Drop in</div>' in client.text
    assert '<div class="col-md-3 bold">Trial</div>' not in client.text

    # check drop in and trial price listing
    class_prices = web2py.db.classes_price(1)
    assert str(class_prices.Dropin) in client.text
    assert str(class_prices.Trial) not in client.text

    # Check request review check-in option not available
    assert 'Request review' not in client.text


def test_classes_book_options_subscription_blocked(client, web2py):
    """
        Is the page listing the booking options showing a blocked
        message for a blocked subscription
    """
    url = '/user/login'
    client.get(url)
    assert client.status == 200

    setup_profile_tests(web2py)
    prepare_classes(web2py, credits=True)
    populate_school_subscriptions(web2py)
    populate_school_classcards(web2py, nr=2)

    csID = web2py.db.customers_subscriptions.insert(
        auth_customer_id = 300,
        school_subscriptions_id = 1,
        Startdate = '2014-01-01',
        payment_methods_id = 1
    )

    web2py.db.customers_subscriptions_credits.insert(
        customers_subscriptions_id = csID,
        MutationDateTime = '2014-01-01 00:00:00',
        MutationType = 'add',
        MutationAmount = '20',
        Description = 'test',
        SubscriptionYear = '2014',
        SubscriptionMonth = '1',
    )

    web2py.db.customers_subscriptions_blocked.insert(
        customers_subscriptions_id = csID,
        Startdate = '2014-01-01',
        Enddate = '2099-12-31',
        Description = 'Test'
    )

    web2py.db.commit()

    next_monday = next_weekday(datetime.date.today(), 0)
    client.get('/shop/classes_book_options?clsID=1&date=' + str(next_monday))
    assert client.status == 200

    assert 'Blocked' in client.text

    # Check request review check-in option not available
    assert 'Request review' not in client.text


def test_classes_book_options_dropin_trial_membership_prices(client, web2py):
    """
        Is the page listing the booking options showing everything?
    """
    url = '/user/login'
    client.get(url)
    assert client.status == 200

    setup_profile_tests(web2py)
    prepare_classes(web2py, credits=True)
    populate_customers_with_memberships(web2py, customers_populated=True)

    cm = web2py.db.customers_memberships(1)
    cm.auth_customer_id = 300
    cm.Enddate = None
    cm.update_record()

    web2py.db.commit()

    next_monday = next_weekday(datetime.date.today(), 0)
    client.get('/shop/classes_book_options?clsID=1&date=' + str(next_monday))
    assert client.status == 200

    # check drop in and trial price listing
    class_prices = web2py.db.classes_price(1)
    assert str(class_prices.DropinMembership) in client.text
    assert str(class_prices.TrialMembership) in client.text


def test_classes_book_options_not_yet_open(client, web2py):
    """
        Is the not yet open for bookings message displayed?
    """
    url = '/user/login'
    client.get(url)
    assert client.status == 200

    setup_profile_tests(web2py)
    prepare_classes(web2py)
    populate_school_subscriptions(web2py)
    populate_school_classcards(web2py, nr=2)

    web2py.db.customers_subscriptions.insert(
        auth_customer_id = 300,
        school_subscriptions_id = 1,
        Startdate = '2014-01-01',
        payment_methods_id = 1)

    web2py.db.customers_classcards.insert(
        auth_customer_id = 300,
        school_classcards_id = 1,
        Startdate = '2014-01-01',
        Enddate = '2999-12-31'
    )

    web2py.db.sys_properties.insert(
        Property='shop_classes_advance_booking_limit',
        PropertyValue='7'
    )

    web2py.db.commit()

    # get the url again
    client.get('/shop/classes_book_options?clsID=1&date=2999-08-01')
    assert client.status == 200

    assert 'Bookings for this class are accepted from' in client.text

    # Also check for shop/classes
    client.get('/shop/classes?date=' + str(datetime.date.today() + datetime.timedelta(days=21)))
    assert client.status == 200
    assert 'Book from' in client.text


def test_classes_book_options_already_booked(client, web2py):
    """
        Is the already booked message displayed?
    """
    url = '/user/login'
    client.get(url)
    assert client.status == 200

    setup_profile_tests(web2py)
    prepare_classes(web2py)
    populate_school_subscriptions(web2py)
    populate_school_classcards(web2py, nr=2)

    cuID = 300
    csID = web2py.db.customers_subscriptions.insert(
        auth_customer_id = cuID,
        school_subscriptions_id = 1,
        Startdate = '2014-01-01',
        payment_methods_id = 1)

    next_monday = next_weekday(datetime.date.today(), 0)

    web2py.db.classes_attendance.insert(
        auth_customer_id=cuID,
        classes_id=1,
        ClassDate=next_monday,
        AttendanceType=None,
        customers_subscriptions_id=csID)

    web2py.db.commit()

    # get the url again
    client.get('/shop/classes_book_options?clsID=1&date=' + str(next_monday))
    assert client.status == 200
    assert "You've already booked this class" in client.text


def test_classes_book_options_no_past_class_bookings(client, web2py):
    """
         Are we redirected to the next class that's actually happening when we're trying to book a class in the past?
    """
    setup_profile_tests(web2py)
    prepare_classes(web2py)

    today = datetime.date.today()
    two_weeks_ago = today - datetime.timedelta(days=14)

    url = '/shop/classes_book_options?clsID=1&date=' + str(two_weeks_ago)
    client.get(url)
    assert client.status == 200

    assert 'Unable to show booking options for this class.' in client.text


def test_classes_book_options_no_class_bookings_on_wrong_weekday(client, web2py):
    """
         Are we redirected to the next class that's actually happening when we're trying to book a class in the past?
    """
    setup_profile_tests(web2py)
    prepare_classes(web2py)

    today = datetime.date.today()
    next_tuesday = next_weekday(today, 1)

    url = '/shop/classes_book_options?clsID=1&date=' + str(next_tuesday)
    client.get(url)
    assert client.status == 200

    assert 'Unable to show booking options for this class.' in client.text


def test_classes_book_options_no_cancelled_class_bookings(client, web2py):
    """
         Are we redirected to the next class that's actually happening when we're trying to book a cancelled class?
    """
    setup_profile_tests(web2py)
    prepare_classes(web2py)

    today = datetime.date.today()
    next_monday = next_weekday(today, 0)

    web2py.db.classes_otc.insert(
        classes_id = 1,
        ClassDate = next_monday,
        Status = 'cancelled'
    )

    web2py.db.commit()

    url = '/shop/classes_book_options?clsID=1&date=' + str(next_monday)
    client.get(url)
    assert client.status == 200

    assert 'Unable to show booking options for this class.' in client.text


def test_classes_book_options_no_bookings_during_holidays(client, web2py):
    """
         Are we redirected to the next class that's actually happening when we're trying to book a class
         during a holiday?
    """
    setup_profile_tests(web2py)
    prepare_classes(web2py)

    today = datetime.date.today()
    next_monday = next_weekday(today, 0)

    web2py.db.school_holidays.insert(
        Description='Test',
        Startdate='2010-01-01',
        Enddate='2999-31-21',
        Classes=True
    )

    web2py.db.school_holidays_locations.insert(
        school_holidays_id = 1,
        school_locations_id = 1
    )

    web2py.db.commit()

    url = '/shop/classes_book_options?clsID=1&date=' + str(next_monday)
    client.get(url)
    assert client.status == 200

    assert 'Unable to show booking options for this class.' in client.text


def test_classes_book_options_enroll_show(client, web2py):
    """
         Is the enroll option showing?
    """
    url = '/user/login'
    client.get(url)
    assert client.status == 200

    today = datetime.date.today()
    next_monday = next_weekday(today, 0)

    setup_profile_tests(web2py)
    prepare_classes(web2py)
    populate_school_subscriptions(web2py)
    populate_school_classcards(web2py, nr=2)

    web2py.db.customers_subscriptions.insert(
        auth_customer_id = 300,
        school_subscriptions_id = 1,
        Startdate = '2014-01-01',
        payment_methods_id = 1)

    web2py.db.commit()

    url = '/shop/classes_book_options?clsID=1&date=' + str(next_monday)
    client.get(url)
    assert client.status == 200


    ssu = web2py.db.school_subscriptions(1)
    assert "Enroll" in client.text
    assert 'In case you would like to join this class every week' in client.text


def test_classes_book_options_enroll_not_allowed_message(client, web2py):
    """
         Is the enroll option showing?
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    setup_profile_tests(web2py)
    prepare_classes(web2py)

    today = datetime.date.today()
    next_monday = next_weekday(today, 0)

    query = (web2py.db.classes_school_subscriptions_groups.id > 0)
    web2py.db(query).delete()

    web2py.db.customers_subscriptions.insert(
        auth_customer_id = 300,
        school_subscriptions_id = 1,
        Startdate = '2014-01-01',
        payment_methods_id = 1)

    web2py.db.commit()

    url = '/shop/classes_book_options?clsID=1&date=' + str(next_monday)
    client.get(url)
    assert client.status == 200

    assert "Enrollment in this class is not possible using your current subscription(s)." in client.text


def test_classes_book_options_enroll_no_subscription_message(client, web2py):
    """
         Is the enroll option showing?
    """
    setup_profile_tests(web2py)
    prepare_classes(web2py)

    today = datetime.date.today()
    next_monday = next_weekday(today, 0)

    web2py.db.commit()

    url = '/shop/classes_book_options?clsID=1&date=' + str(next_monday)
    client.get(url)
    assert client.status == 200

    assert 'A subscription is required to enroll' in client.text


def test_classes_book_options_enroll_already_enrolled_message(client, web2py):
    """
         Is the enroll option showing?
    """
    setup_profile_tests(web2py)
    prepare_classes(web2py)

    today = datetime.date.today()
    next_monday = next_weekday(today, 0)

    web2py.db.classes_reservation.insert(
        classes_id = 1,
        auth_customer_id = 300,
        Startdate = '2014-01-01',
    )

    web2py.db.commit()

    url = '/shop/classes_book_options?clsID=1&date=' + str(next_monday)
    client.get(url)
    assert client.status == 200

    assert "You're enrolled in this class." in client.text


def test_classes_book_options_enroll_no_spaces_message(client, web2py):
    """
         Is the enroll option showing?
    """
    setup_profile_tests(web2py)
    prepare_classes(web2py)

    today = datetime.date.today()
    next_monday = next_weekday(today, 0)

    cls = web2py.db.classes(1)
    cls.MaxReservationsRecurring = 1
    cls.update_record()

    web2py.db.classes_reservation.insert(
        classes_id = 1,
        auth_customer_id = 1001,
        Startdate = '2014-01-01',
    )

    web2py.db.commit()

    url = '/shop/classes_book_options?clsID=1&date=' + str(next_monday)
    client.get(url)
    assert client.status == 200

    assert 'All spaces for enrollments are currently filled. ' in client.text


def test_class_book_subscription(client, web2py):
    """
        Can we actually book a class? 
    """
    url = '/user/login'
    client.get(url)
    assert client.status == 200

    setup_profile_tests(web2py)
    prepare_classes(web2py)
    populate_school_subscriptions(web2py)

    csID = web2py.db.customers_subscriptions.insert(
        auth_customer_id = 300,
        school_subscriptions_id = 1,
        Startdate = '2014-01-01',
        payment_methods_id = 1)

    web2py.db.customers_subscriptions_credits.insert(
        customers_subscriptions_id = csID,
        MutationDateTime = datetime.datetime.now(),
        MutationType = 'add',
        MutationAmount = '200',
        Description = 'Plenty of credits to book a class'
    )

    web2py.db.commit()

    next_monday = next_weekday(datetime.date.today(), 0)

    # check subscription booking
    url = '/shop/class_book?clsID=1&date=' + str(next_monday) + '&csID=' + str(csID)
    client.get(url)
    assert client.status == 200

    query = (web2py.db.classes_attendance.auth_customer_id == 300)
    assert web2py.db(query).count() == 1

    web2py.db(web2py.db.classes_attendance.id > 0).delete()
    web2py.db.commit()


def test_class_book_subscription_no_credits(client, web2py):
    """
        Is a message shown to the customer when there are no classes remaining
    """
    url = '/user/login'
    client.get(url)
    assert client.status == 200

    setup_profile_tests(web2py)
    prepare_classes(web2py)
    populate_school_subscriptions(web2py)
    populate_school_classcards(web2py, nr=2)

    csID = web2py.db.customers_subscriptions.insert(
        auth_customer_id = 300,
        school_subscriptions_id = 1,
        Startdate = '2014-01-01',
        payment_methods_id = 1)

    web2py.db.customers_subscriptions_credits.insert(
        customers_subscriptions_id = csID,
        MutationDateTime = datetime.datetime.now(),
        MutationType = 'sub',
        MutationAmount = '2000',
        Description = 'Definitely not booking a class anytime soon'
    )

    web2py.db.commit()

    next_monday = next_weekday(datetime.date.today(), 0)

    # check subscription booking
    url = '/shop/class_book?clsID=1&date=' + str(next_monday) + '&csID=' + str(csID)
    client.get(url)
    assert client.status == 200

    query = (web2py.db.classes_attendance.auth_customer_id == 300)
    assert web2py.db(query).count() == 0

    assert "No credits remaining on this subscription" in client.text


def test_class_book_subscription_no_shopbook_permission(client, web2py):
    """
        We should be redirected back to the booking options page
    """
    url = '/user/login'
    client.get(url)
    assert client.status == 200

    setup_profile_tests(web2py)
    prepare_classes(web2py)

    query = (web2py.db.classes_school_subscriptions_groups.id > 0)
    web2py.db(query).delete()

    csID = web2py.db.customers_subscriptions.insert(
        auth_customer_id = 300,
        school_subscriptions_id = 1,
        Startdate = '2014-01-01',
        payment_methods_id = 1
    )

    web2py.db.commit()

    next_monday = next_weekday(datetime.date.today(), 0)

    url = '/shop/class_book?csID=' + str(csID) + '&clsID=1&date=' + str(next_monday)
    client.get(url)
    assert client.status == 200

    # We should be redirected back to booking options page
    assert "Booking options for this class" in client.text


def test_class_book_classcard(client, web2py):
    """
        Can we book a class on a class card from the shop?
    """
    url = '/user/login'
    client.get(url)
    assert client.status == 200

    setup_profile_tests(web2py)
    prepare_classes(web2py)
    populate_school_classcards(web2py, nr=2)

    web2py.db.classes_school_classcards_groups.insert(
        classes_id = 1,
        school_classcards_group = 1,
        Enroll = True,
        ShopBook = True,
        Attend = True
    )

    ccdID = web2py.db.customers_classcards.insert(
        auth_customer_id = 300,
        school_classcards_id = 1,
        Startdate = '2014-01-01',
        Enddate = '2099-12-31'
    )

    web2py.db.commit()

    next_monday = next_weekday(datetime.date.today(), 0)
    # check class card booking
    url = '/shop/class_book?clsID=1&date=' + str(next_monday) + '&ccdID=' + str(ccdID)
    client.get(url)
    assert client.status == 200

    query = (web2py.db.classes_attendance.auth_customer_id == 300)
    assert web2py.db(query).count() == 1

    assert 'Recur booking until' in client.text # Check redirection after booking a class using a card


def test_class_book_classcard_no_shopbook_permission(client, web2py):
    """
        We should be redirected back to the booking options page
    """
    url = '/user/login'
    client.get(url)
    assert client.status == 200

    setup_profile_tests(web2py)
    prepare_classes(web2py)

    query = (web2py.db.classes_school_classcards_groups.id > 0)
    web2py.db(query).delete()

    ccdID = web2py.db.customers_classcards.insert(
        auth_customer_id = 300,
        school_classcards_id = 1,
        Startdate = '2014-01-01',
        Enddate = '2999-12-31'
    )

    web2py.db.commit()

    next_monday = next_weekday(datetime.date.today(), 0)

    url = '/shop/class_book?ccdID=' + str(ccdID) + '&clsID=1&date=' + str(next_monday)
    client.get(url)
    assert client.status == 200

    # We should be redirected back to booking options page
    assert "Booking options for this class" in client.text


def test_class_book_classcard_recurring_class_cancelled(client, web2py):
    """
        Recurring booking not possible when class is cancelled
    """
    url = '/user/login'
    client.get(url)
    assert client.status == 200

    setup_profile_tests(web2py)
    prepare_classes(web2py)
    populate_school_classcards(web2py, nr=2)

    ccdID = web2py.db.customers_classcards.insert(
        auth_customer_id = 300,
        school_classcards_id = 1,
        Startdate = '2014-01-01',
        Enddate = '2099-12-31'
    )

    next_monday = next_weekday(datetime.date.today(), 0)

    web2py.db.classes_otc.insert(
        classes_id = 1,
        ClassDate = next_monday,
        Status = 'cancelled'
    )

    query = (web2py.db.classes_attendance.id > 0)
    web2py.db(query).delete()

    web2py.db.commit()

    url = "/shop/class_book_classcard_recurring?ccdID=" + str(ccdID) + '&clsID=1&date=' + str(next_monday)
    client.get(url)
    assert client.status == 200

    data = {
        'recur_until':str(next_monday + datetime.timedelta(days=2))
    }

    client.post(url, data=data)
    assert client.status == 200
    assert "Booked 0 classes" in client.text # Check message to user

    # Make sure no class was booked
    assert web2py.db(web2py.db.classes_attendance).count() == 0


def test_class_book_classcard_recurring_class_during_holiday(client, web2py):
    """
        Recurring booking not possible when class is in a holiday
    """
    url = '/user/login'
    client.get(url)
    assert client.status == 200

    setup_profile_tests(web2py)
    prepare_classes(web2py)
    populate_school_classcards(web2py, nr=2)

    ccdID = web2py.db.customers_classcards.insert(
        auth_customer_id = 300,
        school_classcards_id = 1,
        Startdate = '2014-01-01',
        Enddate = '2099-12-31'
    )

    next_monday = next_weekday(datetime.date.today(), 0)

    shID = web2py.db.school_holidays.insert(
        Description = "Holiday",
        Startdate = next_monday - datetime.timedelta(days=7),
        Enddate = next_monday + datetime.timedelta(days=35),
        Classes = True
    )

    web2py.db.school_holidays_locations.insert(
        school_holidays_id = shID,
        school_locations_id = 1,
    )

    query = (web2py.db.classes_attendance.id > 0)
    web2py.db(query).delete()

    web2py.db.commit()

    url = "/shop/class_book_classcard_recurring?ccdID=" + str(ccdID) + '&clsID=1&date=' + str(next_monday)
    client.get(url)
    assert client.status == 200

    data = {
        'recur_until':str(next_monday + datetime.timedelta(days=32))
    }

    client.post(url, data=data)
    assert client.status == 200
    assert "Booked 0 classes" in client.text # Check message to user

    # Make sure no class was booked
    assert web2py.db(web2py.db.classes_attendance).count() == 0


def test_class_book_classcard_recurring_class_full(client, web2py):
    """
        Recurring booking not possible when OnlineBooking spaces for a class are full
    """
    url = '/user/login'
    client.get(url)
    assert client.status == 200

    setup_profile_tests(web2py)
    prepare_classes(web2py)
    populate_school_classcards(web2py, nr=2)

    ccdID = web2py.db.customers_classcards.insert(
        auth_customer_id = 300,
        school_classcards_id = 1,
        Startdate = '2014-01-01',
        Enddate = '2099-12-31'
    )

    next_monday = next_weekday(datetime.date.today(), 0)

    query = (web2py.db.classes_attendance.id > 0)
    web2py.db(query).delete()

    # Remove online booking spaces to simulate a full class
    cls = web2py.db.classes(1)
    cls.MaxOnlineBooking = 0
    cls.update_record()

    web2py.db.commit()

    url = "/shop/class_book_classcard_recurring?ccdID=" + str(ccdID) + '&clsID=1&date=' + str(next_monday)
    client.get(url)
    assert client.status == 200

    data = {
        'recur_until':str(next_monday + datetime.timedelta(days=3))
    }

    client.post(url, data=data)
    assert client.status == 200

    assert "Booked 0 classes" in client.text # Check message to user

    # Make sure no class was booked
    assert web2py.db(web2py.db.classes_attendance).count() == 0


def test_class_book_classcard_recurring_no_classcard_classes_remaining(client, web2py):
    """
        It should not be possible to recur a booking on a class card without remaining classes
    """
    url = '/user/login'
    client.get(url)
    assert client.status == 200

    setup_profile_tests(web2py)
    prepare_classes(web2py)
    populate_school_classcards(web2py, nr=2)

    ccdID = web2py.db.customers_classcards.insert(
        auth_customer_id = 300,
        school_classcards_id = 1,
        Startdate = '2014-01-01',
        Enddate = '2099-12-31'
    )

    next_monday = next_weekday(datetime.date.today(), 0)

    query = (web2py.db.classes_attendance.id > 0)
    web2py.db(query).delete()

    # Remove classes from school card to simulate no classes remaining on card
    scd = web2py.db.school_classcards(1)
    scd.Classes = 0
    scd.update_record()

    web2py.db.commit()

    url = "/shop/class_book_classcard_recurring?ccdID=" + str(ccdID) + '&clsID=1&date=' + str(next_monday)
    client.get(url)
    assert client.status == 200

    data = {
        'recur_until':str(next_monday + datetime.timedelta(days=3))
    }

    client.post(url, data=data)
    assert client.status == 200
    assert "Booked 0 classes" in client.text # Check message to user

    # Make sure no class was booked
    assert web2py.db(web2py.db.classes_attendance).count() == 0


def test_class_book_classcard_recurring_past_advance_booking_limit(client, web2py):
    """
        Recurring booking not possible when OnlineBooking spaces for a class are full
    """
    url = '/user/login'
    client.get(url)
    assert client.status == 200

    setup_profile_tests(web2py)
    prepare_classes(web2py)
    populate_school_classcards(web2py, nr=2)

    ccdID = web2py.db.customers_classcards.insert(
        auth_customer_id = 300,
        school_classcards_id = 1,
        Startdate = '2014-01-01',
        Enddate = '2099-12-31'
    )

    next_monday = next_weekday(datetime.date.today(), 0) + datetime.timedelta(days=7)

    query = (web2py.db.classes_attendance.id > 0)
    web2py.db(query).delete()

    # Set advance booking limit to 3 day to simulate class going past advance booking limit
    web2py.db.sys_properties.insert(
        Property = 'shop_classes_advance_booking_limit',
        PropertyValue = '3'
    )

    web2py.db.commit()

    url = "/shop/class_book_classcard_recurring?ccdID=" + str(ccdID) + '&clsID=1&date=' + str(next_monday)
    client.get(url)
    assert client.status == 200

    data = {
        'recur_until':str(next_monday + datetime.timedelta(days=14))
    }

    client.post(url, data=data)
    assert client.status == 200

    assert "Enter date in range" in client.text # Check message to user

    # Make sure no class was booked
    assert web2py.db(web2py.db.classes_attendance).count() == 0


def test_class_book_classcard_recurring_class_past_classcard_enddate(client, web2py):
    """
        Recurring class not booked when after classcard enddate
    """
    url = '/user/login'
    client.get(url)
    assert client.status == 200

    setup_profile_tests(web2py)
    prepare_classes(web2py)
    populate_school_classcards(web2py, nr=2)

    ccdID = web2py.db.customers_classcards.insert(
        auth_customer_id = 300,
        school_classcards_id = 1,
        Startdate = '2014-01-01',
        Enddate = '2014-12-31'
    )

    next_monday = next_weekday(datetime.date.today(), 0) + datetime.timedelta(days=7)

    query = (web2py.db.classes_attendance.id > 0)
    web2py.db(query).delete()

    web2py.db.commit()

    url = "/shop/class_book_classcard_recurring?ccdID=" + str(ccdID) + '&clsID=1&date=' + str(next_monday)
    client.get(url)
    assert client.status == 200

    data = {
        'recur_until':str(next_monday + datetime.timedelta(days=10))
    }

    client.post(url, data=data)
    assert client.status == 200
    assert "Enter date in range" in client.text # Check message to user

    # Make sure no class was booked
    assert web2py.db(web2py.db.classes_attendance).count() == 0


def test_class_book_classcard_recurring(client, web2py):
    """
        Are recurring classes booked?
    """
    url = '/user/login'
    client.get(url)
    assert client.status == 200

    setup_profile_tests(web2py)
    prepare_classes(web2py)
    populate_school_classcards(web2py, nr=2)

    ccdID = web2py.db.customers_classcards.insert(
        auth_customer_id = 300,
        school_classcards_id = 1,
        Startdate = '2014-01-01',
        Enddate = '2099-12-31'
    )

    next_monday = next_weekday(datetime.date.today(), 0)

    query = (web2py.db.classes_attendance.id > 0)
    web2py.db(query).delete()

    web2py.db.commit()

    url = "/shop/class_book_classcard_recurring?ccdID=" + str(ccdID) + '&clsID=1&date=' + str(next_monday)
    client.get(url)
    assert client.status == 200

    data = {
        'recur_until':str(next_monday + datetime.timedelta(days=22))
    }

    client.post(url, data=data)
    assert client.status == 200

    assert "Booked 4 classes" in client.text # Check message to user

    # Make sure 4 classes were booked
    assert web2py.db(web2py.db.classes_attendance).count() == 4


def test_class_enroll(client, web2py):
    """
        Can we add enrollments?
    """
    from populate_os_tables import populate_classes

    setup_profile_tests(web2py)

    url = '/profile/index'
    client.get(url)
    assert client.status == 200

    populate_classes(web2py)
    populate_customers_with_subscriptions(web2py, credits=True)

    cs = web2py.db.customers_subscriptions(1)
    cs.auth_customer_id = 300
    cs.update_record()

    web2py.db.commit()

    url = '/shop/class_enroll?csID=1&clsID=1&date=2014-01-06'
    client.get(url)
    assert client.status == 200

    data = {
        'Startdate': '2014-01-06'
    }

    client.post(url, data=data)
    assert client.status == 200

    assert 'Enrollment added' in client.text # check user message

    query = (web2py.db.classes_reservation.ResType == 'recurring')
    assert web2py.db(query).count() == 1


    # Check classes booked
    query = (web2py.db.classes_attendance.ClassDate == datetime.date(2014, 1, 6)) & \
            (web2py.db.classes_attendance.auth_customer_id == 300) & \
            (web2py.db.classes_attendance.BookingStatus == 'booked') & \
            (web2py.db.classes_attendance.classes_id == 1)
    assert web2py.db(query).count() == 1


def test_class_add_to_cart_requires_complete_profile(client, web2py):
    """
        Can we add a drop in class to the shopping cart?
    """
    url = '/user/login'
    client.get(url)
    assert client.status == 200

    setup_profile_tests(web2py)
    prepare_classes(web2py)
    populate_school_subscriptions(web2py)
    populate_school_classcards(web2py, nr=2)

    web2py.db.sys_properties.insert(
        Property="shop_requires_complete_profile_classes",
        PropertyValue="on"
    )
    web2py.db.commit()

    # check drop in booking
    future_monday = next_weekday(datetime.date(2999, 1, 1), 0)
    url = '/shop/class_book?clsID=1&date=' + str(future_monday) + '&dropin=true'
    client.get(url)
    assert client.status == 200

    assert "best service possible" in client.text


def test_classcards(client, web2py):
    """
        Is the page that lists class cards working?
    """
    setup_profile_tests(web2py)

    # populate a regular card and a trial card
    populate_school_classcards(web2py, 1)

    url = '/shop/classcards'
    client.get(url)
    assert client.status == 200

    ## check regular card
    scd = web2py.db.school_classcards(1)
    # Panel type
    assert 'box-widget' in client.text
    # Name
    assert scd.Name in client.text
    # Validity
    assert '3 Months' in client.text
    # Price
    assert '€ 125.00' in client.text
    # Add to cart link
    assert '/shop/classcard?scdID=1' in client.text

    ## check trial card
    scd = web2py.db.school_classcards(2)
    # Name
    assert scd.Name in client.text
    # Validity
    assert '7 Days' in client.text
    # Price
    assert '€ 15.00' in client.text
    # Add to cart link
    assert '/shop/classcard?scdID=2' in client.text


def test_classcards_shop_allow_trial_cards_for_existing_customers(client, web2py):
    """
    If the sys property 'shop_allow_trial_cards_for_existing_customers' is not
    'on' and the customer has or had a card or subscription, it shouldn't show
    trial cards in the list.
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    setup_profile_tests(web2py)

    # populate a regular card and a trial card
    populate_school_classcards(web2py, 1)
    populate_customers_with_subscriptions(web2py)
    subscription = web2py.db.customers_subscriptions(1)
    subscription.auth_customer_id = 300
    subscription.update_record()

    web2py.db.commit()

    url = '/shop/classcards'
    client.get(url)
    assert client.status == 200

    ## check regular card
    scd = web2py.db.school_classcards(1)
    # Panel type
    assert 'box-widget' in client.text
    # Name
    assert scd.Name in client.text
    # Validity
    assert '3 Months' in client.text
    # Price
    assert '€ 125.00' in client.text
    # Add to cart link
    assert '/shop/classcard?scdID=1' in client.text

    ## check trial card (this shouldn't be in the client text
    scd = web2py.db.school_classcards(2)
    # Name
    assert scd.Name not in client.text
    # Add to cart link
    assert '/shop/classcard?scdID=2' not in client.text


def test_classcards_display_message_trial_over_times_bought(client, web2py):
    """
        Is the message telling a customer they've reached the max nr of times
        they can buy a trial card showing?
    """
    setup_profile_tests(web2py)


    web2py.db.sys_properties.insert(
        Property='shop_allow_trial_cards_for_existing_customers',
        PropertyValue='on'
    )
    web2py.db.commit()

    # populate a regular card and a trial card
    populate_school_classcards(web2py, 1)

    web2py.db.customers_classcards.insert(
        auth_customer_id = 300,
        school_classcards_id = 2, # this is the trial card
        Startdate = datetime.date.today(),
        Enddate = datetime.date.today() + datetime.timedelta(days=31)
    )
    web2py.db.commit()

    url = '/shop/classcards'
    client.get(url)
    assert client.status == 200

    assert "You've reached the maximum number of times you can purchase this card." in client.text


def test_classcard_membership_required_message(client, web2py):
    """
    Is the Membership required link showing like it should?
    """
    setup_profile_tests(web2py)
    web2py.db.commit()

    # populate a regular card and a trial card
    populate_school_memberships(web2py)
    populate_school_classcards(web2py, school_memberships_id=1)

    url = '/shop/classcard?scdID=1'
    client.get(url)
    assert client.status == 200

    sm = web2py.db.school_memberships(1)
    assert sm.Name in client.text


def test_classcard_add_to_cart_requires_complete_profile(client, web2py):
    """
        Are classcards added to the shopping cart as expected?
    """
    setup_profile_tests(web2py)
    web2py.db.sys_properties.insert(
        Property="shop_requires_complete_profile_classcards",
        PropertyValue="on"
    )
    web2py.db.commit()

    # populate a regular card and a trial card
    populate_school_classcards(web2py, 1)

    url = '/shop/classcard?scdID=1'
    client.get(url)
    assert client.status == 200

    # Verify redirection
    assert 'best service possible' in client.text


def test_complete(client, web2py):
    """
        Is the order/payment complete page showing correctly?
    """
    setup_profile_tests(web2py)
    populate_customers(web2py)
    populate_customers_orders(web2py)
    populate_customers_orders_items(web2py)

    url = '/shop/complete?coID=2'
    client.get(url)
    assert client.status == 200
    assert "Unable" in client.text # this is part of a string that says something like "Unable to show order"

    url = '/shop/complete?coID=1'
    client.get(url)
    assert client.status == 200

    assert 'No payment received' in client.text

    # Change status and check message
    order = web2py.db.customers_orders(1)
    order.Status = 'delivered'
    order.update_record()
    web2py.db.commit()

    client.get(url)
    assert client.status == 200

    assert 'Payment received' in client.text

    # check link to continue
    assert '/profile' in client.text


def test_contact(client, web2py):
    """
        Is the contact page showing all info?
    """
    populate_sys_organizations(web2py)

    url = '/shop/contact'
    client.get(url)
    assert client.status == 200

    properties = [
        'Name',
        'Address',
        'Phone',
        'Email',
        'Registration'
    ]

    print('\n')

    org = web2py.db.sys_organizations(1)

    for p in properties:
        print(p)
        assert org[p] in client.text


def test_event_price(client, web2py):
    """
        Is the regular price applied?
        No earlybird discount() & no subscription discount
    """
    setup_profile_tests(web2py)

    # populate workshops table
    populate_workshops(web2py)

    url = '/shop/event?wsID=1'
    client.get(url)
    assert client.status == 200

    # Verify regular price
    wsp = web2py.db.workshops_products(1)
    assert str(wsp.Price) + '</span>' in client.text


def test_event_price_earlybird(client, web2py):
    """
        Is the earlybird price applied?
    """
    setup_profile_tests(web2py)

    # populate workshops table
    populate_workshops(web2py)

    wsp = web2py.db.workshops_products(1)
    wsp.EarlybirdUntil = '2999-12-31'
    wsp.update_record()

    web2py.db.commit()

    url = '/shop/event?wsID=1'
    client.get(url)
    assert client.status == 200

    # Verify regular price
    wsp = web2py.db.workshops_products(1)
    assert str(wsp.PriceEarlybird) + '</span>' in client.text


def test_event_price_subscription(client, web2py):
    """
        Is the subscription price applied?
    """
    setup_profile_tests(web2py)

    client.get('/default/user/login')
    assert client.status == 200

    # populate workshops table
    populate_workshops(web2py)
    populate_customers_with_subscriptions(web2py)

    cs = web2py.db.customers_subscriptions(1)
    cs.auth_customer_id = 300
    cs.update_record()

    web2py.db.commit()

    url = '/shop/event?wsID=1'
    client.get(url)
    assert client.status == 200

    # Verify regular price
    wsp = web2py.db.workshops_products(1)
    assert str(wsp.PriceSubscription) + '</span>' in client.text


def test_event_price_subscription_earlybird(client, web2py):
    """
        Is the earlybird price for customers with a subscription applied?
    """
    setup_profile_tests(web2py)

    client.get('/default/user/login')
    assert client.status == 200

    # populate workshops table
    populate_workshops(web2py)
    populate_customers_with_subscriptions(web2py)

    wsp = web2py.db.workshops_products(1)
    wsp.EarlybirdUntil = '2999-12-31'
    wsp.update_record()

    cs = web2py.db.customers_subscriptions(1)
    cs.auth_customer_id = 300
    cs.update_record()

    web2py.db.commit()

    url = '/shop/event?wsID=1'
    client.get(url)
    assert client.status == 200

    # Verify regular price
    wsp = web2py.db.workshops_products(1)
    assert str(wsp.PriceSubscriptionEarlybird) + '</span>' in client.text


def test_event_ticket_requires_complete_profile(client, web2py):
    """
        Is the required profile check working for workshops?
    """
    setup_profile_tests(web2py)

    # populate workshops table
    populate_workshops(web2py)

    web2py.db.sys_properties.insert(
        Property="shop_requires_complete_profile_events",
        PropertyValue="on"
    )
    web2py.db.commit()

    url = '/shop/event_ticket?wspID=1'
    client.get(url)
    assert client.status == 200

    # Verify redirection
    assert 'best service possible' in client.text


def test_event_sold_out(client, web2py):
    """
        Is the 'sold out' text showing correctly for sold out workshops
    """
    setup_profile_tests(web2py)
    
    populate_workshops_for_api_tests(web2py)

    url = '/shop/event?wsID=1'
    client.get(url)
    assert client.status == 200

    assert '<div class="workshop_price fullws_price" id="wsp_price_1" style="display: none;">Sold out</div>' in client.text


def test_event_product_price_donation(client, web2py):
    """
        Is the text "Donation based" showing when the "Donation" checkbox is enabled for a workshop product?
    """
    setup_profile_tests(web2py)
    populate_workshops_for_api_tests(web2py)

    # Set donation based for the second product
    wsp = web2py.db.workshops_products(2)
    wsp.Donation = True
    wsp.PublicProduct = True
    wsp.update_record()

    web2py.db.commit()

    url = '/shop/event?wsID=1'
    client.get(url)
    assert client.status == 200

    assert "Donation based" in client.text


def test_event_product_external_shop_url_and_alt_btn_text(client, web2py):
    """
        Are the fields to link to an external shop from the workshops page working? 
    """
    setup_profile_tests(web2py)
    populate_workshops_for_api_tests(web2py, auth_customer_id=300)

    url = '/shop/event?wsID=1'
    client.get(url)
    assert client.status == 200

    wsp = web2py.db.workshops_products(2)
    assert wsp.ExternalShopURL in client.text
    assert wsp.AddToCartText in client.text


def test_subscriptions_membership_required_message(client, web2py):
    """
    Is the Membership required link showing like it should?
    """
    setup_profile_tests(web2py)
    web2py.db.commit()

    # populate a regular card and a trial card
    populate_school_memberships(web2py)
    populate_school_subscriptions(web2py, school_memberships_id=1)

    url = '/shop/subscription?ssuID=1'
    client.get(url)
    assert client.status == 200

    sm = web2py.db.school_memberships(1)
    assert sm.Name in client.text


def test_subscription(client, web2py):
    """
        Are the terms for a subscription showing correctly?
         ( First the general terms defined in settings and below the specific terms from the subscription in school )
    """
    setup_profile_tests(web2py)

    # get random url to init OpenStudio env
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_school_subscriptions(web2py)

    terms = 'GeneralTerms'
    web2py.db.sys_properties.insert(
        Property = 'shop_subscriptions_terms',
        PropertyValue = terms
    )

    web2py.db.commit()

    url = '/shop/subscription?ssuID=1'
    client.get(url)
    assert client.status == 200

    # Check general terms
    assert terms in client.text
    # Check subscription specific terms
    ssu = web2py.db.school_subscriptions(1)
    assert ssu.Terms in client.text


def test_subscription_requires_complete_profile(client, web2py):
    """
        Are the terms for a subscription showing correctly?
         ( First the general terms defined in settings and below the specific terms from the subscription in school )
    """
    setup_profile_tests(web2py)

    # get random url to init OpenStudio env
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_school_subscriptions(web2py)
    web2py.db.sys_properties.insert(
        Property="shop_requires_complete_profile_subscriptions",
        PropertyValue="on"
    )

    terms = 'GeneralTerms'
    web2py.db.sys_properties.insert(
        Property = 'shop_subscription',
        PropertyValue = terms
    )

    web2py.db.commit()

    url = '/shop/subscription?ssuID=1'
    client.get(url)
    assert client.status == 200

    # Check general terms
    assert "best service possible" in client.text


def test_subscription_direct_debit_log_terms(client, web2py):
    """
        Are accepted terms logged for a subscription
    """
    url = "/default/user/login"
    client.get(url)
    assert client.status == 200

    setup_profile_tests(web2py)
    populate_school_subscriptions(web2py)
    populate_payment_methods(web2py)

    web2py.db.customers_payment_info.insert(
        auth_customer_id=300,
        payment_methods_id=3,
        AccountNumber="Account300",
        AccountHolder="HolderName300",
        BIC="BIC300")
    web2py.db.commit()

    url = '/shop/subscription_direct_debit?ssuID=1'
    client.get(url)
    assert client.status == 200

    cs = web2py.db.customers_subscriptions(1)
    assert cs.auth_customer_id == 300
    assert cs.Startdate == datetime.date.today()
    assert cs.school_subscriptions_id == 1

    query = (web2py.db.log_customers_accepted_documents.id > 0)
    assert web2py.db(query).count() > 0


def test_membership_terms(client, web2py):
    """
        Are the terms for a membership showing correctly?
         ( First the general terms defined in settings and below the specific terms from the membership in school )
    """
    setup_profile_tests(web2py)

    # get random url to init OpenStudio env
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_school_memberships(web2py)

    terms = 'GeneralTerms'
    web2py.db.sys_properties.insert(
        Property = 'shop_memberships_terms',
        PropertyValue = terms
    )

    web2py.db.commit()

    url = '/shop/membership?smID=1'
    client.get(url)
    assert client.status == 200

    # Check general terms
    assert terms in client.text
    # Check subscription specific terms
    sm = web2py.db.school_memberships(1)
    assert sm.Terms in client.text


def test_membership_requires_complete_profile(client, web2py):
    """
        Are the terms for a membership showing correctly?
         ( First the general terms defined in settings and below the specific terms from the membership in school )
    """
    setup_profile_tests(web2py)

    # get random url to init OpenStudio env
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_school_memberships(web2py)
    web2py.db.sys_properties.insert(
        Property="shop_requires_complete_profile_memberships",
        PropertyValue="on"
    )

    terms = 'GeneralTerms'
    web2py.db.sys_properties.insert(
        Property = 'shop_memberships_terms',
        PropertyValue = terms
    )

    web2py.db.commit()

    url = '/shop/membership?smID=1'
    client.get(url)
    assert client.status == 200

    # Check general terms
    assert "best service possible" in client.text


def test_donate(client, web2py):
    """
        Is an order created with the right amount when a donation is made?
        
        ( Invoice creation for donations is tested in test_order_paid_delivery_invoice ) 
    """
    url = '/shop/donate'
    client.get(url)
    assert client.status == 200

    setup_profile_tests(web2py)
    populate_tax_rates(web2py)

    web2py.db.sys_properties.insert(
        Property='shop_donations_tax_rates_id',
        PropertyValue='1'
    )

    web2py.db.commit()

    data = {'amount':'100',
            'description':'test'}
    client.post(url, data=data)
    assert client.status == 200

    donation_item = web2py.db.customers_orders_items(1)
    assert donation_item.ProductName == 'Donation'
    assert donation_item.Price == float(data['amount'])
    assert donation_item.Description == data['description']
    assert donation_item.Quantity == 1

