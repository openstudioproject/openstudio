#!/usr/bin/env python

"""
    py.test test cases to test the Profile controller (profile.py)
"""

from gluon.contrib.populate import populate

from populate_os_tables import populate_payment_methods
from populate_os_tables import populate_invoices
from populate_os_tables import populate_customers_orders
from populate_os_tables import populate_customers_orders_items
from populate_os_tables import populate_classes
from populate_os_tables import prepare_classes
from populate_os_tables import populate_customers_with_classcards
from populate_os_tables import populate_customers_with_subscriptions
from populate_os_tables import populate_customers_with_memberships
from populate_os_tables import populate_workshops_products_customers
from populate_os_tables import populate_settings_shop_customers_profile_announcements
from setup_profile_tests import setup_profile_tests

import datetime

# Function to find next weekday after given date
def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)



def test_logout_for_profile(client, web2py):
    """
        This is not an actual test, but just logs out the user
    """
    url = '/default/user/logout'
    client.get(url)
    assert client.status == 200


def test_login_profile_user(client, web2py):
    """
        Logs in with a user without any permissions by default
    """
    setup_profile_tests(web2py)

    data = dict(email='profile@openstudioproject.com',
                password='password',
                _formname='login')
    client.post('/default/user/login', data=data)
    assert client.status == 200
    assert '<li class="header">Account</li>' in client.text


def test_index_announcements(client, web2py):
    """
        Are the announcements shown correctly?
    """
    populate_settings_shop_customers_profile_announcements(web2py)

    url = '/profile/index'
    client.get(url)
    assert client.status == 200

    cpa = web2py.db.customers_profile_announcements(1)
    assert cpa.Title in client.text
    assert cpa.Announcement in client.text


def test_me(client, web2py):
    """
        Is the profile edit page showing correctly?
    """
    setup_profile_tests(web2py)

    url = '/profile/me'
    client.get(url)
    assert client.status == 200

    assert "fa-user-secret" in client.text


def test_me_privacy_link_not_shown(client, web2py):
    """
        Is the profile edit page showing correctly?
    """
    setup_profile_tests(web2py)

    url = '/profile/me'
    client.get(url)
    assert client.status == 200

    features = web2py.db.customers_profile_features(1)
    features.Privacy = False
    features.update_record()
    web2py.db.commit()

    client.get(url)
    assert client.status == 200

    assert "fa-user-secret" not in client.text


def test_staff_payments_link_not_shown(client, web2py):
    """
        The staff payments link shouldn't show
    """
    setup_profile_tests(web2py)

    url = '/profile/index'
    client.get(url)
    assert client.status == 200

    assert "Payments not in client.text"


def test_staff_payments(client, web2py):
    """
        Is the staff payments page showing?
    """
    from populate_os_tables import populate_auth_user_teachers_payment_invoices

    setup_profile_tests(web2py)

    au = web2py.db.auth_user(300)
    au.teacher = True
    au.update_record()

    web2py.db.commit()

    populate_auth_user_teachers_payment_invoices(web2py)

    # log out and log back in again to make the profile user a teacher
    url = '/default/user/logout'
    client.get(url)
    assert client.status == 200

    data = dict(email='profile@openstudioproject.com',
                password='password',
                _formname='login')
    client.post('/default/user/login', data=data)
    assert client.status == 200

    # Check payments display
    url = '/profile/staff_payments'
    client.get(url)
    assert client.status == 200

    ic = web2py.db.invoices_customers(auth_customer_id=300)
    invoice = web2py.db.invoices(ic.invoices_id)
    assert invoice.InvoiceID in client.text



#TODO rework test to check access to 'all' pages from home
# def test_profile_features(client, web2py):
#     """
#         Are the profile menu items showing when enabled/disabled in settings
#     """
#     # get random url to setup OpenStudio environment
#     url = '/default/user/login'
#     client.get(url)
#     assert client.status == 200
#
#     setup_profile_tests(web2py)
#
#     url = '/profile'
#     client.get(url)
#     assert client.status == 200
#
#     # check Classes
#     assert '<span>Classes</span>' in client.text
#     # check Class cards
#     assert '<span>Class cards</span>' in client.text
#     # check Subscriptions
#     assert '<span>Subscriptions</span>' in client.text
#     # check Workshops
#     assert '<span>Workshops</span>' in client.text
#     # check Orders
#     assert '<span>Orders</span>' in client.text
#     # check Invoices
#     assert '<span>Invoices</span>' in client.text
#
#     features = web2py.db.customers_profile_features(1)
#     features.Classes = False
#     features.Classcards = False
#     features.Subscriptions = False
#     features.Workshops = False
#     features.Orders = False
#     features.Invoices = False
#     features.update_record()
#
#     web2py.db.commit()
#
#     url = '/profile/index'
#     client.get(url)
#     assert client.status == 200
#
#     # check Classes
#     assert not '<span>Classes</span>' in client.text
#     # check Class cards
#     assert not '<span>Class cards</span>' in client.text
#     # check Subscriptions
#     assert not '<span>Subscriptions</span>' in client.text
#     # check Workshops
#     assert not '<span>Workshops</span>' in client.text
#     # check Orders
#     assert not '<span>Orders</span>' in client.text
#     # check Invoices
#     assert not '<span>Invoices</span>' in client.text

#NOTE: depricated - shop and profile have been merged so no more need for links to shop from profile
# def test_shop_links_features(client, web2py):
#     """
#         Are the shop links showing when features are enabled in settings
#     """
#     # get random url to setup OpenStudio environment
#     url = '/default/user/login'
#     client.get(url)
#     assert client.status == 200
#
#     setup_profile_tests(web2py)
#
#     # Check classcards
#     url = '/profile/classcards'
#     client.get(url)
#     assert client.status == 200
#     assert 'New card' in client.text
#
#     # Check workshops
#     url = '/profile/workshops'
#     client.get(url)
#     assert client.status == 200
#     assert 'Book workshop' in client.text
#
#     # Check subscriptions
#     url = '/profile/subscriptions'
#     client.get(url)
#     assert client.status == 200
#     assert 'Get a subscription' in client.text
#
#     ## Change settings
#     features = web2py.db.customers_shop_features(1)
#     features.Classcards = False
#     features.Workshops = False
#     features.Subscriptions = False
#     features.update_record()
#     web2py.db.commit()
#     # and check again
#
#     # Check classcards
#     url = '/profile/classcards'
#     client.get(url)
#     assert client.status == 200
#     assert not 'New card' in client.text
#
#     # Check workshops
#     url = '/profile/workshops'
#     client.get(url)
#     assert client.status == 200
#     assert not 'Book workshop' in client.text
#
#     # Check subscriptions
#     url = '/profile/subscriptions'
#     client.get(url)
#     assert client.status == 200
#     assert not 'Get a subscription' in client.text


# Depricated for now (2017-04-06)
# def test_index_reservations(client, web2py):
#     """
#         Are the reservations showing properly on the index controller
#     """
#     setup_profile_tests(web2py)
#     populate_classes(web2py)
#
#     today = datetime.date.today()
#     next_monday = next_weekday(today, 0) # 0 is Monday
#
#     web2py.db.classes_otc.insert(
#         classes_id=1,
#         ClassDate=next_monday,
#         school_locations_id=2,
#         school_classtypes_id=2,
#     )
#
#     web2py.db.classes_reservation.insert(
#         classes_id = 1,
#         auth_customer_id = 300,
#         Startdate = '2014-01-01'
#     )
#
#     web2py.db.commit()
#
#     url = '/profile/index'
#     client.get(url)
#     assert client.status == 200
#
#     # check normal classes
#     location = web2py.db.school_locations(1)
#     location_name = location.Name.split(' ')[0]
#     assert location_name in client.text
#
#     # check otc classes
#     location = web2py.db.school_locations(2)
#     location_name = location.Name.split(' ')[0]
#     assert location_name in client.text


def test_classes(client, web2py):
    """
        Is the list of classes showing?
    """
    setup_profile_tests(web2py)
    populate_classes(web2py)

    d = datetime.date.today()
    next_monday = next_weekday(d, 0)

    # Insert changed location into classes_otc for next Monday
    web2py.db.classes_otc.insert(
        classes_id=1,
        ClassDate=next_monday,
        school_locations_id=2,
        school_classtypes_id=2,
    )

    web2py.db.classes_attendance.insert(
        classes_id = 1,
        ClassDate = '2014-01-06',
        auth_customer_id = 300,
        AttendanceType = 1
    )

    web2py.db.commit()

    url = '/profile/classes'
    client.get(url)
    assert client.status == 200

    # check regular class listing
    location = web2py.db.school_locations(1)
    location_name = location.Name.split(' ')[0]
    assert location_name in client.text

    # check otc class listing
    location = web2py.db.school_locations(1)
    location_name = location.Name.split(' ')[0]
    assert location_name in client.text


def test_classes_show_cancel_link(client, web2py):
    """
        Is the cancel link shown when it should?
    """
    setup_profile_tests(web2py)
    populate_classes(web2py)

    d = datetime.date.today()
    next_next_monday = next_weekday(d, 0) + datetime.timedelta(days=7)

    clattID = web2py.db.classes_attendance.insert(
        classes_id = 1,
        ClassDate = next_next_monday,
        auth_customer_id = 300,
        AttendanceType = 1
    )

    # Allow cancellation 24 hours or more in advance
    web2py.db.sys_properties.insert(
        Property = 'shop_classes_cancellation_limit',
        PropertyValue = '24'
    )

    web2py.db.commit()

    # check profile/classes
    url = '/profile/classes'
    client.get(url)
    assert client.status == 200

    assert "/profile/class_cancel_confirm" in client.text

    # # check profile home
    # url = '/profile/index'
    # client.get(url)
    # assert client.status == 200
    #
    # assert "/profile/class_cancel_confirm" in client.text


def test_classes_hide_cancel_link(client, web2py):
    """
        Is the cancel link hidden when it should?
    """
    setup_profile_tests(web2py)
    populate_classes(web2py)

    d = datetime.date.today()
    next_next_monday = next_weekday(d, 0) + datetime.timedelta(days=7)

    clattID = web2py.db.classes_attendance.insert(
        classes_id = 1,
        ClassDate = next_next_monday,
        auth_customer_id = 300,
        AttendanceType = 1
    )

    # Allow cancellation 24 hours or more in advance
    web2py.db.sys_properties.insert(
        Property = 'shop_classes_cancellation_limit',
        PropertyValue = '744' # roughly month from now
    )

    web2py.db.commit()

    # check profile/classes
    url = '/profile/classes'
    client.get(url)
    assert client.status == 200

    assert not "/profile/class_cancel_confirm" in client.text

    # check profile home
    url = '/profile/index'
    client.get(url)
    assert client.status == 200

    assert not "/profile/class_cancel_confirm" in client.text


def test_class_cancel_confirmation(client, web2py):
    """
         Is the cancel conformation page showing?
    """
    setup_profile_tests(web2py)
    populate_classes(web2py)

    d = datetime.date.today()
    next_next_monday = next_weekday(d, 0) + datetime.timedelta(days=7)

    clattID = web2py.db.classes_attendance.insert(
        classes_id = 1,
        ClassDate = next_next_monday,
        auth_customer_id = 300,
        AttendanceType = 1
    )

    # Allow cancellation 24 hours or more in advance
    web2py.db.sys_properties.insert(
        Property = 'shop_classes_cancellation_limit',
        PropertyValue = '24'
    )

    web2py.db.commit()

    url = '/profile/class_cancel_confirm?clattID=' + unicode(clattID)
    client.get(url)
    assert client.status == 200

    assert "Are you sure you want to cancel" in client.text


def test_class_cancel_confirmation_cannot_be_cancelled(client, web2py):
    """
        Is the message showing notifying the customer that the class can't be cancelled anymore
    """
    setup_profile_tests(web2py)
    populate_classes(web2py)

    d = datetime.date.today()
    next_monday = next_weekday(d, 0)

    clattID = web2py.db.classes_attendance.insert(
        classes_id = 1,
        ClassDate = next_monday,
        auth_customer_id = 300,
        AttendanceType = 1
    )

    # Allow cancellation 24 hours or more in advance
    web2py.db.sys_properties.insert(
        Property = 'shop_classes_cancellation_limit',
        PropertyValue = '744'
    )

    web2py.db.commit()

    url = '/profile/class_cancel_confirm?clattID=' + unicode(clattID)
    client.get(url)
    assert client.status == 200

    assert "We're sorry to inform" in client.text


def test_class_cancel(client, web2py):
    """
        Can a customer cancel a class?
    """
    setup_profile_tests(web2py)
    populate_classes(web2py)

    d = datetime.date.today()
    next_monday = next_weekday(d, 0)

    clattID = web2py.db.classes_attendance.insert(
        classes_id = 1,
        ClassDate = next_monday,
        auth_customer_id = 300,
        AttendanceType = 1
    )

    # Allow cancellation 1 hours or more in advance
    web2py.db.sys_properties.insert(
        Property = 'shop_classes_cancellation_limit',
        PropertyValue = '1'
    )

    web2py.db.commit()

    url = '/profile/class_cancel?clattID=' + unicode(clattID)
    client.get(url)
    assert client.status == 200

    clatt = web2py.db.classes_attendance(clattID)
    assert clatt.BookingStatus == 'cancelled'


def test_classcards(client, web2py):
    """
        Is the list of class cards showing?
    """
    setup_profile_tests(web2py)

    populate_customers_with_classcards(web2py)

    ccd = web2py.db.customers_classcards(1)
    ccd.auth_customer_id = 300
    ccd.update_record()

    web2py.db.commit()

    url = '/profile/classcards'
    client.get(url)
    assert client.status == 200

    scd = web2py.db.school_classcards(1)
    scd_name = scd.Name.split(' ')[0]

    assert scd_name in client.text
    assert '2014-01-01' in client.text


def test_classcard_info(client, web2py):
    """
        Is the classcard info page showing correctly?
    """
    setup_profile_tests(web2py)
    prepare_classes(web2py)

    ccdID = web2py.db.customers_classcards.insert(
        auth_customer_id = 300,
        school_classcards_id = 1,
        Startdate = '2014-01-01',
        Enddate = '2999-12-31'
    )

    web2py.db.classes_school_classcards_groups.insert(
        classes_id = 1,
        school_classcards_groups_id = 1,
        ShopBook = True,
        Attend = True
    )

    web2py.db.commit()


    url = '/profile/classcard_info?ccdID=' + unicode(ccdID)
    client.get(url)
    assert client.status == 200

    assert client.text.count('<span class="text-green"><i class="fa fa-check">') == 2
    
    
def test_memberships(client, web2py):
    """
        Is the list of memberships showing? 
    """
    url = '/profile/memberships'
    client.get(url)
    assert client.status == 200

    setup_profile_tests(web2py)
    
    populate_customers_with_memberships(web2py)

    cm = web2py.db.customers_memberships(1)
    cm.auth_customer_id = 300
    cm.update_record()
    
    web2py.db.commit()

    client.get(url)
    assert client.status == 200

    sm = web2py.db.school_memberships(1)
    assert sm.Name in client.text
    assert unicode(cm.Startdate) in client.text
    

def test_subscriptions(client, web2py):
    """
        Is the list of subscriptions showing?
    """
    # get the url, for some reason the customers_subscriptions table is empty if not when asserting
    url = '/profile/subscriptions'
    client.get(url)
    assert client.status == 200

    setup_profile_tests(web2py)

    populate_customers_with_subscriptions(web2py, credits=True)

    cs = web2py.db.customers_subscriptions(1)
    cs.auth_customer_id = 300
    cs.update_record()

    web2py.db.commit()

    url = '/profile/subscriptions'
    client.get(url)
    assert client.status == 200

    ss = web2py.db.school_subscriptions(1)
    assert ss.Name in client.text
    assert unicode(cs.Startdate) in client.text
    assert unicode(3456.0) in client.text  # check if number of credits is displayed


def test_subscriptions_display_credits_unlimited(client, web2py):
    """
        Is the list of subscriptions showing?
    """
    # get the url, for some reason the customers_subscriptions table is empty if not when asserting
    url = '/profile/subscriptions'
    client.get(url)
    assert client.status == 200

    setup_profile_tests(web2py)

    populate_customers_with_subscriptions(web2py, credits=True)

    ssu = web2py.db.school_subscriptions(1)
    ssu.Unlimited = True
    ssu.update_record()

    cs = web2py.db.customers_subscriptions(1)
    cs.auth_customer_id = 300
    cs.update_record()

    web2py.db.commit()

    url = '/profile/subscriptions'
    client.get(url)
    assert client.status == 200

    ss = web2py.db.school_subscriptions(1)
    assert ss.Name in client.text
    assert unicode(cs.Startdate) in client.text
    assert 'Unlimited' in client.text  # check if number of credits is displayed


def test_subscription_credits_profile_home(client, web2py):
    """
        Check if subscription credits are displayed on the home page of a profile
    """
    # get the url, for some reason the customers_subscriptions table is empty if not when asserting
    url = '/profile/index'
    client.get(url)
    assert client.status == 200

    setup_profile_tests(web2py)

    populate_customers_with_subscriptions(web2py, credits=True)

    cs = web2py.db.customers_subscriptions(1)
    cs.auth_customer_id = 300
    cs.update_record()

    web2py.db.commit()

    client.get(url)
    assert client.status == 200

    assert unicode(3456.0) in client.text # check if number of credits is displayed


def test_subscription_unlimited_credits_profile_home(client, web2py):
    """
        Check if subscription credits are displayed on the home page of a profile
    """
    # get the url, for some reason the customers_subscriptions table is empty if not when asserting
    url = '/profile/index'
    client.get(url)
    assert client.status == 200

    setup_profile_tests(web2py)

    populate_customers_with_subscriptions(web2py, credits=True)

    ssu = web2py.db.school_subscriptions(1)
    ssu.Unlimited = True
    ssu.update_record()

    cs = web2py.db.customers_subscriptions(1)
    cs.auth_customer_id = 300
    cs.update_record()

    web2py.db.commit()

    client.get(url)
    assert client.status == 200

    assert 'Unlimited' in client.text # check if number of credits is displayed


def test_subscription_info(client, web2py):
    """
        Is the subscription info page showing correctly?
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    setup_profile_tests(web2py)
    prepare_classes(web2py)

    csID = web2py.db.customers_subscriptions.insert(
        auth_customer_id = 300,
        school_subscriptions_id = 1,
        Startdate = '2014-01-01',
        Enddate = '2999-12-31',
        payment_methods_id = 1
    )

    web2py.db.classes_school_subscriptions_groups.insert(
        classes_id = 1,
        school_subscriptions_groups_id = 1,
        Enroll = True,
        ShopBook = True,
        Attend = True
    )

    web2py.db.commit()

    url = '/profile/subscription_info?csID=' + unicode(csID)
    client.get(url)
    assert client.status == 200

    assert client.text.count('<span class="text-green"><i class="fa fa-check">') == 3


def test_events(client, web2py):
    """
        Is the list of workshops showing?
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    setup_profile_tests(web2py)
    populate_workshops_products_customers(web2py)

    wspc = web2py.db.workshops_products_customers(1)
    wspc.auth_customer_id = 300
    wspc.update_record()

    web2py.db.commit()

    url = '/profile/events'
    client.get(url)
    assert client.status == 200

    # check name of workshop on page

    wsp = web2py.db.workshops_products(wspc.workshops_products_id)
    ws  = web2py.db.workshops(wsp.workshops_id)

    assert wsp.Name in client.text
    assert ws.Name in client.text
    assert unicode(ws.Startdate) in client.text


def test_orders(client, web2py):
    """
        Is the list of orders showing?
    """
    url = '/profile/orders'
    client.get(url)
    assert client.status == 200

    setup_profile_tests(web2py)
    populate_customers_orders(web2py)
    populate_customers_orders_items(web2py)

    client.get(url)
    assert client.status == 200

    # check all invoices link
    assert 'All invoices' in client.text

    order = web2py.db.customers_orders(2)

    # Check display of ID
    assert str(order.id) in client.text

    # check display of status
    assert 'Awaiting payment' in client.text

    # check time
    import pytz
    dc = pytz.utc.localize(order.DateCreated)
    tz = pytz.timezone('Europe/Amsterdam')
    local_dc = dc.astimezone(tz)
    assert unicode(local_dc)[:-9] in client.text.decode('utf-8') #[:-3] removes seconds, they are not displayed by default

    # check items display
    query = (web2py.db.customers_orders_items.customers_orders_id == 2)
    rows = web2py.db(query).select(web2py.db.customers_orders_items.ALL)
    for row in rows:
        assert row.Description in client.text

    # Check total amount
    ord_amounts = web2py.db.customers_orders_amounts(2)
    assert format(ord_amounts.TotalPriceVAT, '.2f') in client.text

    # check cancel button display
    assert 'Cancel' in client.text
    assert '/profile/order_cancel?coID=2' in client.text

    # check payment button
    assert 'Pay now' in client.text
    assert '/mollie/order_pay?coID=2' in client.text

    # add payment and reload page


def test_order_cancel(client, web2py):
    """
        Can we actually cancel an order?
    """
    url = '/profile/orders'
    client.get(url)
    assert client.status == 200

    setup_profile_tests(web2py)
    populate_customers_orders(web2py)
    populate_customers_orders_items(web2py)

    url = '/profile/order_cancel?coID=2'
    client.get(url)
    assert client.status == 200
    assert 'Orders' in client.text # Verify redirection to orders page

    order = web2py.db.customers_orders(2)
    assert order.Status == 'cancelled'



def test_invoices(client, web2py):
    """
        Is the list of invoices showing?
    """
    url = '/profile/invoices'
    client.get(url)
    assert client.status == 200

    setup_profile_tests(web2py)
    populate_invoices(web2py)

    client.get(url)
    assert client.status == 200

    invoice = web2py.db.invoices(2)

    assert invoice.InvoiceID in client.text
    assert unicode(invoice.DateCreated) in client.text.decode('utf-8')
    assert invoice.Status in client.text.lower()

    inv_amounts = web2py.db.invoices_amounts(2)
    assert format(inv_amounts.TotalPriceVAT, '.2f') in client.text


    # check payment button
    assert 'Pay now' in client.text
    assert '/mollie/invoice_pay?iID=2' in client.text


def test_enrollments(client, web2py):
    """
        Are class enrollments listed correctly?
    """
    # get the url, for some reason the customers_subscriptions table is empty if we don't get this first
    url = '/profile/index'
    client.get(url)
    assert client.status == 200

    setup_profile_tests(web2py)
    populate_classes(web2py)

    web2py.db.classes_reservation.insert(
        classes_id = 1,
        auth_customer_id = 300,
        Startdate = '2014-01-01',
    )

    web2py.db.commit()

    url = '/profile/enrollments'
    client.get(url)
    assert client.status == 200

    assert '2014-01-01' in client.text
    assert 'End enrollment' in client.text # Check end link display


def test_enrollment_end(client, web2py):
    """
        Are class enrollments listed correctly?
    """
    # get the url, for some reason the customers_subscriptions table is empty if we don't get this first
    url = '/profile/index'
    client.get(url)
    assert client.status == 200

    setup_profile_tests(web2py)
    populate_classes(web2py)

    clrID = web2py.db.classes_reservation.insert(
        classes_id = 1,
        auth_customer_id = 300,
        Startdate = '2014-01-01',
    )

    web2py.db.commit()

    url = '/profile/enrollment_end/' + unicode(clrID)
    client.get(url)
    assert client.status == 200

    data = {
        'id': clrID,
        'Enddate':'2017-12-31'
    }

    url = '/profile/enrollment_end/' + unicode(clrID)
    client.post(url, data=data)
    assert client.status == 200

    clr = web2py.db.classes_reservation(clrID)
    assert clr.Enddate == datetime.date(2017, 12, 31)
