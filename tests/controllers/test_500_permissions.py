# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
    py.test test cases to test OpenStudio.
    These tests run based on webclient and need web2py server running.
"""

from gluon.contrib.populate import populate
from populate_os_tables import populate_workshops
from populate_os_tables import populate_workshops_products_customers
from populate_os_tables import populate_customers
from populate_os_tables import populate_customers_with_subscriptions
from populate_os_tables import populate_customers_with_classcards
from populate_os_tables import populate_school_subscriptions
from populate_os_tables import populate_postcode_groups
from populate_os_tables import prepare_classes
from populate_os_tables import prepare_shifts
from populate_os_tables import populate_customers_orders
from populate_os_tables import populate_customers_orders_items

from setup_permisison_tests import setup_permission_tests


# def test_logout(client, web2py):
#     """
#         This is not an actual test, but just logs out the user
#     """
#     print web2py.db().select(web2py.db.auth_user.ALL)
#
#     url = '/default/user/logout'
#     client.get(url)
#     assert client.status == 200


def test_login_nopriv_user(client, web2py):
    """
        Logs in with a user without any permissions by default
    """
    setup_permission_tests(web2py)

    data = dict(email='support@openstudioproject.com',
                password='password',
                _formname='login')
    client.post('/default/user/login', data=data)
    assert client.status == 200
    assert 'Home' in client.text


def test_customers_contact_info(client, web2py):
    """
        Check if the customers_info update permission works
    """
    setup_permission_tests(web2py)
    populate_customers(web2py, 1)

    url = '/customers/edit/1001'
    client.get(url)
    assert client.status == 200
    assert "Insufficient privileges" in client.text

    gid = 2

    web2py.auth.add_permission(200, 'read', 'auth_user', 0)
    web2py.auth.add_permission(200, 'update', 'auth_user', 0)
    web2py.db.commit()

    str_check = '<label>Telephone</label>'
    client.get(url)
    assert client.status == 200
    assert not str_check in client.text

    web2py.auth.add_permission(200, 'update', 'customers_contact', 0)
    web2py.db.commit()
    client.get(url)
    assert client.status == 200
    assert str_check in client.text


def test_customers_address_info(client, web2py):
    """
        Check if the customers_info update permission works
    """
    setup_permission_tests(web2py)
    populate_customers(web2py, 1)

    url = '/customers/edit/1'
    client.get(url)
    assert client.status == 200
    assert "Insufficient privileges" in client.text

    gid = 2

    web2py.auth.add_permission(200, 'read', 'auth_user', 0)
    web2py.auth.add_permission(200, 'update', 'auth_user', 0)
    web2py.db.commit()


    str_check = "<label>Country</label>"
    client.get(url)
    assert client.status == 200
    assert not str_check in client.text

    web2py.auth.add_permission(200, 'update', 'customers_address', 0)
    web2py.db.commit()
    client.get(url)
    assert client.status == 200
    assert str_check in client.text


def test_customers_edit_classcard_enddate(client, web2py):
    """
        Check if the permission to prevent editing the enddate of a subscription works
    """
    setup_permission_tests(web2py)

    populate_customers(web2py, 1)

    web2py.db.school_classcards.insert(
        Name           = 'Classcard',
        Description    = 'test',
        Price          = '125',
        ValidityMonths = 3,
        ValidityDays   = 0,
        Classes        = 10)

    web2py.db.customers_classcards.insert(
        school_classcards_id = 1,
        auth_customer_id     = 1001,
        Startdate = '2014-01-01')

    web2py.auth.add_permission(200, 'update', 'customers_classcards', 0)

    web2py.db.commit()

    url = '/customers/classcard_edit?ccdID=1&cuID=1001'
    client.get(url)
    assert client.status == 200

    assert not 'Expiration' in client.text

    # grant permission and check again
    web2py.auth.add_permission(200, 'update', 'customers_classcards_enddate', 0)
    web2py.db.commit()

    client.get(url)
    assert client.status == 200

    assert 'Expiration' in client.text


def test_customers_orders_delete(client, web2py):
    """
        Is the delete permission for customers_orders working?
    """
    setup_permission_tests(web2py)

    populate_customers_orders(web2py)
    populate_customers_orders_items(web2py)

    web2py.auth.add_permission(200, 'read', 'customers_orders', 0)
    web2py.db.commit()

    url = '/orders/index'
    client.get(url)
    assert client.status == 200

    assert not 'fa-times' in client.text

    # grant permission and check again
    web2py.auth.add_permission(200, 'delete', 'customers_orders', 0)
    web2py.db.commit()

    client.get(url)
    assert client.status == 200

    assert 'fa-times' in client.text


def test_settings_access_group_delete(client, web2py):
    """
        Is the delete permission for a user group working?
    """
    setup_permission_tests(web2py)
    prepare_classes(web2py)
    web2py.auth.add_permission(200, 'read', 'settings', 0)

    web2py.db.commit()

    url = '/settings/access_groups'
    client.get(url)
    assert client.status == 200

    assert not 'fa-times' in client.text

    # grant permission and check again
    web2py.auth.add_permission(200, 'delete', 'auth_group', 0)
    web2py.db.commit()

    client.get(url)
    assert client.status == 200

    assert 'fa-times' in client.text


def test_settings_access_api_users_delete(client, web2py):
    """
        Is the delete permission for an api user working?
    """
    setup_permission_tests(web2py)
    web2py.db.sys_api_users.insert(
        Username='test',
        Description='test',
        APIKey='123456')

    web2py.auth.add_permission(200, 'read', 'settings', 0)

    web2py.db.commit()

    url = '/settings/access_api_users'
    client.get(url)
    assert client.status == 200

    assert not 'fa-times' in client.text

    # grant permission and check again
    web2py.auth.add_permission(200, 'delete', 'sys_api_users', 0)
    web2py.db.commit()

    client.get(url)
    assert client.status == 200

    assert 'fa-times' in client.text


def test_events_delete(client, web2py):
    """
        Is the delete permission for a workshop working?
    """
    setup_permission_tests(web2py)
    populate_workshops(web2py)
    web2py.auth.add_permission(200, 'read', 'workshops', 0)

    web2py.db.commit()

    url = '/events/index'
    client.get(url)
    assert client.status == 200

    assert not 'fa-times' in client.text

    # grant permission and check again
    web2py.auth.add_permission(200, 'delete', 'workshops', 0)
    web2py.db.commit()

    client.get(url)
    assert client.status == 200

    assert 'fa-times' in client.text


def test_events_tickets_delete(client, web2py):
    """
        Is the delete permission for a workshop product working?
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_workshops_products_customers(web2py)
    setup_permission_tests(web2py)
    web2py.auth.add_permission(200, 'read', 'workshops_products', 0)

    web2py.db.commit()

    url = '/events/tickets?wsID=1'
    client.get(url)
    assert client.status == 200

    assert not 'fa-times' in client.text

    # grant permission and check again
    web2py.auth.add_permission(200, 'delete', 'workshops_products', 0)
    web2py.db.commit()

    client.get(url)
    assert client.status == 200

    assert 'fa-times' in client.text


def test_events_tickets_customers_delete(client, web2py):
    """
        Is the delete permission for a workshop product customer working?
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    setup_permission_tests(web2py)
    populate_workshops_products_customers(web2py)
    web2py.auth.add_permission(200, 'read', 'workshops_products_customers', 0)

    web2py.db.commit()

    url = '/events/tickets_list_customers?wsID=1&wspID=2'
    client.get(url)
    assert client.status == 200

    assert not 'ticket_delete_customer' in client.text

    # grant permission and check again
    web2py.auth.add_permission(200, 'delete', 'workshops_products_customers', 0)
    web2py.db.commit()

    client.get(url)
    assert client.status == 200

    assert 'ticket_delete_customer' in client.text


def test_events_activities_delete(client, web2py):
    """
        Is the delete permission for a workshop activity working?
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    setup_permission_tests(web2py)
    populate_workshops_products_customers(web2py)
    web2py.auth.add_permission(200, 'read', 'workshops_activities', 0)

    web2py.db.commit()

    url = '/events/activities?wsID=1'
    client.get(url)
    assert client.status == 200

    assert not 'fa-times' in client.text

    # grant permission and check again
    web2py.auth.add_permission(200, 'delete', 'workshops_activities', 0)
    web2py.db.commit()

    client.get(url)
    assert client.status == 200

    assert 'fa-times' in client.text


def test_classes_delete(client, web2py):
    """
        Is the delete permission for a class working?
        class_delete
    """
    setup_permission_tests(web2py)
    prepare_classes(web2py)
    web2py.auth.add_permission(200, 'read', 'classes', 0)

    web2py.db.commit()

    url = '/classes/schedule?year=2014&week=2'
    client.get(url)
    assert client.status == 200

    assert not 'class_delete' in client.text

    # grant permission and check again
    web2py.auth.add_permission(200, 'delete', 'classes', 0)
    web2py.db.commit()

    client.get(url)
    assert client.status == 200

    assert 'class_delete' in client.text


def test_classes_otc_delete(client, web2py):
    """
        Is the delete permission for classes_otc working?
    """
    setup_permission_tests(web2py)
    prepare_classes(web2py)

    web2py.db.classes_otc.insert(
        classes_id = 1,
        ClassDate = '2014-01-06',
        Status = 'open'
    )

    web2py.auth.add_permission(200, 'read', 'classes_otc', 0)

    web2py.db.commit()

    url = '/classes/class_edit_on_date_remove_changes?cotcID=1'
    client.get(url)
    assert client.status == 200

    assert 'Not authorized' in client.text
    assert web2py.db(web2py.db.classes_otc).count() == 1

    # grant permission and check again
    web2py.auth.add_permission(200, 'delete', 'classes_otc', 0)
    web2py.db.commit()

    client.get(url)
    assert client.status == 200

    assert web2py.db(web2py.db.classes_otc).count() == 0


def test_classes_teachers_delete(client, web2py):
    """
        Is the delete permission for a class teacher working?
    """
    setup_permission_tests(web2py)
    prepare_classes(web2py)
    web2py.auth.add_permission(200, 'update', 'classes', 0)

    web2py.db.commit()

    url = '/classes/class_teachers?clsID=1'
    client.get(url)
    assert client.status == 200

    assert not 'fa-times' in client.text

    # grant permission and check again
    web2py.auth.add_permission(200, 'delete', 'classes_teachers', 0)
    web2py.db.commit()

    client.get(url)
    assert client.status == 200

    assert 'fa-times' in client.text


def test_classes_prices_delete(client, web2py):
    """
        Is the delete permission for a class price working?
    """
    setup_permission_tests(web2py)
    prepare_classes(web2py)
    web2py.auth.add_permission(200, 'update', 'classes', 0)

    web2py.db.commit()

    url = '/classes/class_prices?clsID=1'
    client.get(url)
    assert client.status == 200

    assert not 'fa-times' in client.text

    # grant permission and check again
    web2py.auth.add_permission(200, 'delete', 'classes_price', 0)
    web2py.db.commit()

    client.get(url)
    assert client.status == 200

    assert 'fa-times' in client.text


def test_schedule_school_holidays_delete(client, web2py):
    """
        Is the delete permission for a school holiday working?
    """
    setup_permission_tests(web2py)
    populate(web2py.db.school_locations, 1)
    populate(web2py.db.school_holidays, 1)

    web2py.auth.add_permission(200, 'read', 'school_holidays', 0)

    web2py.db.commit()

    url = '/schedule/holidays'
    client.get(url)
    assert client.status == 200

    assert not 'fa-times' in client.text

    # grant permission and check again
    web2py.auth.add_permission(200, 'delete', 'school_holidays', 0)
    web2py.db.commit()

    client.get(url)
    assert client.status == 200

    assert 'fa-times' in client.text


def test_staff_holidays_delete(client, web2py):
    """
        Is the delete permission for a staf holiday working?
    """
    setup_permission_tests(web2py)
    prepare_classes(web2py)
    web2py.db.teachers_holidays.insert(
        auth_teacher_id = 2,
        Startdate       = '2014-01-01',
        Enddate         = '2014-01-31',
        Note            = 'Peaches')

    web2py.auth.add_permission(200, 'read', 'teacher_holidays', 0)

    web2py.db.commit()

    url = '/schedule/staff_holidays'
    client.get(url)
    assert client.status == 200

    assert not 'fa-times' in client.text

    # grant permission and check again
    web2py.auth.add_permission(200, 'delete', 'teacher_holidays', 0)
    web2py.db.commit()

    client.get(url)
    assert client.status == 200

    assert 'fa-times' in client.text


def test_shift_delete(client, web2py):
    """
        Is the delete permission for a shift working?
    """
    setup_permission_tests(web2py)
    prepare_shifts(web2py)

    web2py.auth.add_permission(200, 'read', 'shifts', 0)

    web2py.db.commit()

    url = '/staff/schedule'
    client.get(url)
    assert client.status == 200

    assert not 'fa-times' in client.text

    # grant permission and check again
    web2py.auth.add_permission(200, 'delete', 'shifts', 0)
    web2py.db.commit()

    client.get(url)
    assert client.status == 200

    assert 'fa-times' in client.text


def test_shift_staff_delete(client, web2py):
    """
        Is the delete permission for assigning employees to shifts working?
    """
    setup_permission_tests(web2py)
    prepare_shifts(web2py)

    web2py.auth.add_permission(200, 'read', 'shifts_staff', 0)

    web2py.db.commit()

    url = '/staff/shift_staff?shID=1&date=2014-01-06'
    client.get(url)
    assert client.status == 200

    assert not 'fa-times' in client.text

    # grant permission and check again
    web2py.auth.add_permission(200, 'delete', 'shifts_staff', 0)
    web2py.db.commit()

    client.get(url)
    assert client.status == 200

    assert 'fa-times' in client.text


def test_classes_attendance_complementary(client, web2py):
    """
        Is the complementary permission working?
    """
    setup_permission_tests(web2py)
    prepare_classes(web2py)

    web2py.auth.add_permission(200, 'read', 'classes_attendance', 0)
    web2py.auth.add_permission(200, 'update', 'classes_attendance', 0)
    web2py.db.commit()

    url = '/classes/attendance_booking_options?clsID=1&date=2014-01-13&cuID=1003'
    client.get(url)
    assert client.status == 200
    assert 'Complementary' not in client.text

    web2py.auth.add_permission(200, 'complementary', 'classes_attendance', 0)
    web2py.db.commit()

    client.get(url)
    assert client.status == 200
    assert 'Complementary' in client.text

#NOTE: new attendance page, there is no more delete check in the classes code
# def test_classes_attendance_delete(client, web2py):
#     """
#         Is the delete permission for an attendance registration working?
#     """
#     setup_permission_tests(web2py)
#     prepare_classes(web2py)
#
#     web2py.auth.add_permission(200, 'read', 'classes_attendance', 0)
#     web2py.auth.add_permission(200, 'update', 'classes_attendance', 0)
#
#     web2py.db.commit()
#
#     url = '/classes/attendance?clsID=1&date=2014-01-06'
#     client.get(url)
#     assert client.status == 200
#
#     assert not 'fa-times' in client.text
#
#     # grant permission and check again
#     web2py.auth.add_permission(200, 'delete', 'classes_attendance', 0)
#     web2py.db.commit()
#
#     client.get(url)
#     assert client.status == 200
#
#     assert 'fa-times' in client.text

# def test_classes_attendance_list_delete(client, web2py):
#     """
#         Is the delete permission for an attendance list registration working?
#     """
#     setup_permission_tests(web2py)
#     prepare_classes(web2py)
#
#     web2py.auth.add_permission(200, 'read', 'classes_attendance', 0)
#     web2py.auth.add_permission(200, 'update', 'classes_attendance', 0)
#
#     web2py.db.commit()
#
#     url = '/classes/attendance_list?clsID=1&date=2014-01-06'
#     client.get(url)
#     assert client.status == 200
#
#     assert not 'fa-times' in client.text
#
#     # grant permission and check again
#     web2py.auth.add_permission(200, 'delete', 'classes_attendance', 0)
#     web2py.db.commit()
#
#     client.get(url)
#     assert client.status == 200
#
#     assert 'fa-times' in client.text


def test_classes_reservations_delete(client, web2py):
    """
        Is the delete permission for an a reservation working?
    """
    setup_permission_tests(web2py)
    prepare_classes(web2py)

    web2py.auth.add_permission(200, 'read', 'classes_reservation', 0)
    web2py.auth.add_permission(200, 'update', 'classes_reservation', 0)

    web2py.db.commit()

    url = '/classes/reservations?clsID=1&date=2014-01-06'
    client.get(url)
    assert client.status == 200

    assert not 'fa-times' in client.text

    # grant permission and check again
    web2py.auth.add_permission(200, 'delete', 'classes_reservation', 0)
    web2py.db.commit()

    client.get(url)
    assert client.status == 200

    assert 'fa-times' in client.text


def test_classes_waitinglist_delete(client, web2py):
    """
        Is the delete permission for a waitinglist entry working?
    """
    setup_permission_tests(web2py)
    prepare_classes(web2py)

    web2py.auth.add_permission(200, 'read', 'classes_waitinglist', 0)
    web2py.auth.add_permission(200, 'update', 'classes_waitinglist', 0)

    web2py.db.commit()

    url = '/classes/waitinglist_edit?clsID=1&date=2014-01-06'
    client.get(url)
    assert client.status == 200

    assert not 'fa-times' in client.text

    # grant permission and check again
    web2py.auth.add_permission(200, 'delete', 'classes_waitinglist', 0)
    web2py.db.commit()

    client.get(url)
    assert client.status == 200

    assert 'fa-times' in client.text


def test_classes_class_subscriptions_delete(client, web2py):
    """
        Is the delete permission for classes_school_subscriptions_groups working correctly?
    """
    setup_permission_tests(web2py)
    prepare_classes(web2py)

    web2py.auth.add_permission(200, 'read', 'classes_school_subscriptions_groups', 0)
    web2py.auth.add_permission(200, 'update', 'classes_school_subscriptions_groups', 0)

    web2py.db.commit()

    url = '/classes/class_subscriptions?clsID=1'
    client.get(url)
    assert client.status == 200

    assert not 'fa-times' in client.text

    # grant permission and check again
    web2py.auth.add_permission(200, 'delete', 'classes_school_subscriptions_groups', 0)
    web2py.db.commit()

    client.get(url)
    assert client.status == 200

    assert 'fa-times' in client.text


def test_classes_class_classcards_delete(client, web2py):
    """
        Is the delete permission for classes_school_subscriptions_groups working correctly?
    """
    setup_permission_tests(web2py)
    prepare_classes(web2py)

    web2py.auth.add_permission(200, 'read', 'classes_school_classcards_groups', 0)
    web2py.auth.add_permission(200, 'update', 'classes_school_classcards_groups', 0)

    web2py.db.commit()

    url = '/classes/class_classcards?clsID=1'
    client.get(url)
    assert client.status == 200

    assert not 'fa-times' in client.text

    # grant permission and check again
    web2py.auth.add_permission(200, 'delete', 'classes_school_classcards_groups', 0)
    web2py.db.commit()

    client.get(url)
    assert client.status == 200

    assert 'fa-times' in client.text


def test_school_subscriptions_groups_delete(client, web2py):
    """
        Is the delete permission for classes_school_subscriptions_groups working correctly?
    """
    setup_permission_tests(web2py)
    prepare_classes(web2py)

    web2py.auth.add_permission(200, 'read', 'school_subscriptions_groups', 0)
    web2py.auth.add_permission(200, 'update', 'school_subscriptions_groups', 0)

    web2py.db.commit()

    url = '/school_properties/subscriptions_groups'
    client.get(url)
    assert client.status == 200

    assert not 'fa-times' in client.text

    # grant permission and check again
    web2py.auth.add_permission(200, 'delete', 'school_subscriptions_groups', 0)
    web2py.db.commit()

    client.get(url)
    assert client.status == 200

    assert 'fa-times' in client.text


def test_school_subscriptions_group_subscriptions_delete(client, web2py):
    """
        Is the delete permission for classes_school_subscriptions_groups working correctly?
    """
    setup_permission_tests(web2py)
    prepare_classes(web2py)

    web2py.auth.add_permission(200, 'read', 'school_subscriptions_groups_subscriptions', 0)
    web2py.auth.add_permission(200, 'update', 'school_subscriptions_groups_subscriptions', 0)

    web2py.db.commit()

    url = '/school_properties/subscriptions_group_subscriptions?ssgID=1'
    client.get(url)
    assert client.status == 200

    assert not 'fa-times' in client.text

    # grant permission and check again
    web2py.auth.add_permission(200, 'delete', 'school_subscriptions_groups_subscriptions', 0)
    web2py.db.commit()

    client.get(url)
    assert client.status == 200

    assert 'fa-times' in client.text


def test_school_classcards_groups_delete(client, web2py):
    """
        Is the delete permission for school_classcards_groups working correctly?
    """
    setup_permission_tests(web2py)
    prepare_classes(web2py)

    web2py.auth.add_permission(200, 'read', 'school_classcards_groups', 0)
    web2py.auth.add_permission(200, 'update', 'school_classcards_groups', 0)

    web2py.db.commit()

    url = '/school_properties/classcards_groups'
    client.get(url)
    assert client.status == 200

    assert not 'fa-times' in client.text

    # grant permission and check again
    web2py.auth.add_permission(200, 'delete', 'school_classcards_groups', 0)
    web2py.db.commit()

    client.get(url)
    assert client.status == 200

    assert 'fa-times' in client.text
    

def test_school_classcards_group_classcards_delete(client, web2py):
    """
        Is the delete permission for school_classcards_groups_classcards working correctly?
    """
    setup_permission_tests(web2py)
    prepare_classes(web2py)

    web2py.auth.add_permission(200, 'read', 'school_classcards_groups_classcards', 0)
    web2py.auth.add_permission(200, 'update', 'school_classcards_groups_classcards', 0)

    web2py.db.commit()

    url = '/school_properties/classcards_group_classcards?scgID=1'
    client.get(url)
    assert client.status == 200

    assert not 'fa-times' in client.text

    # grant permission and check again
    web2py.auth.add_permission(200, 'delete', 'school_classcards_groups_classcards', 0)
    web2py.db.commit()

    client.get(url)
    assert client.status == 200

    assert 'fa-times' in client.text


def test_paymentbatches_delete(client, web2py):
    """
        Is the delete payment batch button working?
    """
    setup_permission_tests(web2py)
    web2py.db.payment_batches.insert(
        BatchType   = 'collection',
        Status      = 'approved',
        Description = 'test',
        ColYear     = 2014,
        ColMonth    = 1,
        Exdate      = '2013-12-31')

    web2py.auth.add_permission(200, 'read', 'payment_batches', 0)

    web2py.db.commit()

    url = '/finance/batches_index/?export=collection'
    client.get(url)
    assert client.status == 200

    assert not 'fa-times' in client.text

    # grant permission and check again
    web2py.auth.add_permission(200, 'delete', 'payment_batches', 0)
    web2py.db.commit()

    client.get(url)
    assert client.status == 200

    assert 'fa-times' in client.text


def test_customer_delete(client, web2py):
    """
        Is the delete permission for a customer working?
    """
    setup_permission_tests(web2py)
    populate_customers(web2py, 1)
    web2py.auth.add_permission(200, 'read', 'auth_user', 0)

    web2py.db.commit()

    url = '/customers/load_list.load?list_type=customers_index&items_per_page=7&initial_list=True&archived=False'
    client.get(url)
    assert client.status == 200

    assert not 'fa-times' in client.text

    # grant permission and check again
    web2py.auth.add_permission(200, 'delete', 'auth_user', 0)
    web2py.db.commit()

    client.get(url)
    assert client.status == 200

    assert 'fa-times' in client.text


def test_customer_subscription_delete(client, web2py):
    """
        Is the delete permission for a customer subscription working?
    """
    # get random url to init payment methods in db
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    setup_permission_tests(web2py)
    populate_customers_with_subscriptions(web2py, 2)

    web2py.auth.add_permission(200, 'read', 'customers_subscriptions', 0)

    web2py.db.commit()

    url = '/customers/subscriptions?cuID=1001'
    client.get(url)
    assert client.status == 200

    assert not 'fa-times' in client.text

    # grant permission and check again
    web2py.auth.add_permission(200, 'delete', 'customers_subscriptions', 0)
    web2py.db.commit()

    client.get(url)
    assert client.status == 200

    assert 'fa-times' in client.text


def test_customers_subscription_credits_delete(client, web2py):
    """
        Is the delete permission working for subscription credits?
    """
    # get random url to init payment methods in db
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    setup_permission_tests(web2py)
    populate_customers_with_subscriptions(web2py, 2, credits=True)

    web2py.auth.add_permission(200, 'read', 'customers_subscriptions_credits', 0)

    web2py.db.commit()

    url = '/customers/subscription_credits?cuID=1001&csID=1'
    client.get(url)
    assert client.status == 200

    assert not 'fa-times' in client.text

    # grant permission and check again
    web2py.auth.add_permission(200, 'delete', 'customers_subscriptions_credits', 0)
    web2py.db.commit()

    client.get(url)
    assert client.status == 200

    assert 'fa-times' in client.text


def test_customer_classcard_delete(client, web2py):
    """
        Is the delete permission for a customer classcard working?
    """
    setup_permission_tests(web2py)
    populate_customers_with_classcards(web2py, 1)
    web2py.auth.add_permission(200, 'read', 'customers_classcards', 0)
    web2py.db.commit()

    url = '/customers/classcards?cuID=1001'
    client.get(url)
    assert client.status == 200

    assert not 'fa-times' in client.text

    # grant permission and check again
    web2py.auth.add_permission(200, 'delete', 'customers_classcards', 0)
    web2py.db.commit()

    client.get(url)
    assert client.status == 200

    assert 'fa-times' in client.text


def test_customer_classes_reservations_delete(client, web2py):
    """
        Is the delete permission for a reservation under customers working?
    """
    setup_permission_tests(web2py)
    prepare_classes(web2py)
    web2py.auth.add_permission(200, 'read', 'classes_reservation', 0)
    web2py.db.commit()

    url = '/customers/classes_reservations?cuID=1001'
    client.get(url)
    assert client.status == 200

    assert not 'fa-times' in client.text

    # grant permission and check again
    web2py.auth.add_permission(200, 'delete', 'classes_reservation', 0)
    web2py.db.commit()

    client.get(url)
    assert client.status == 200

    assert 'fa-times' in client.text


def test_customer_classes_waitinglist_delete(client, web2py):
    """
        Is the delete permission for waitinglist under customers working?
    """
    setup_permission_tests(web2py)
    prepare_classes(web2py)
    web2py.auth.add_permission(200, 'read', 'classes_waitinglist', 0)
    web2py.db.commit()

    url = '/customers/classes_waitinglist?cuID=1001'
    client.get(url)
    assert client.status == 200

    assert not 'fa-times' in client.text

    # grant permission and check again
    web2py.auth.add_permission(200, 'delete', 'classes_waitinglist', 0)
    web2py.db.commit()

    client.get(url)
    assert client.status == 200

    assert 'fa-times' in client.text


def test_customer_classes_attendance_delete(client, web2py):
    """
        Is the delete permission for attendance under customers working?
    """
    setup_permission_tests(web2py)
    prepare_classes(web2py)
    web2py.auth.add_permission(200, 'read', 'classes_attendance', 0)
    web2py.db.commit()

    url = '/customers/classes_attendance?cuID=1001'
    client.get(url)
    assert client.status == 200

    assert not 'fa-times' in client.text

    # grant permission and check again
    web2py.auth.add_permission(200, 'delete', 'classes_attendance', 0)
    web2py.db.commit()

    client.get(url)
    assert client.status == 200

    assert 'fa-times' in client.text


def test_customer_payments_payment_info_delete(client, web2py):
    """
        Is the delete permission for payment info under customers working?
    """
    # get random url to init payment methods in db
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    setup_permission_tests(web2py)
    populate_customers(web2py, 1)
    web2py.db.customers_payment_info.insert(
        auth_customer_id   = 1001,
        AccountNumber      ='123456',
        payment_methods_id = 1)

    web2py.auth.add_permission(200, 'read', 'customers_payment_info', 0)
    web2py.auth.add_permission(200, 'read', 'customers_payments', 0)
    web2py.db.commit()

    url = '/customers/payments?cuID=1001'
    client.get(url)
    assert client.status == 200

    assert not 'fa-times' in client.text

    # grant permission and check again
    web2py.auth.add_permission(200, 'delete', 'customers_payment_info', 0)
    web2py.db.commit()

    client.get(url)
    assert client.status == 200

    assert 'fa-times' in client.text


def test_customer_payments_alternativepayments_delete(client, web2py):
    """
        Is the delete permission for alternative under customers working?
    """
    setup_permission_tests(web2py)
    populate_customers(web2py, 1)
    web2py.db.alternativepayments.insert(
        auth_customer_id   = 1001,
        PaymentYear        = 2014,
        PaymentMonth       = 1,
        Amount             = 100,
        Description        = 'test')

    web2py.auth.add_permission(200, 'read', 'customers_payments', 0)
    web2py.auth.add_permission(200, 'read', 'alternativepayments', 0)
    web2py.db.commit()

    url = '/customers/payments?cuID=1001'
    client.get(url)
    assert client.status == 200

    assert not 'fa-times' in client.text

    # grant permission and check again
    web2py.auth.add_permission(200, 'delete', 'alternativepayments', 0)
    web2py.db.commit()

    client.get(url)
    assert client.status == 200

    assert 'fa-times' in client.text


def test_customer_documents_delete(client, web2py):
    """
        Is the delete permission for documents under customers working?
    """
    setup_permission_tests(web2py)
    populate_customers(web2py, 1)
    web2py.db.customers_documents.insert(
        auth_customer_id = 1001,
        Description      = 'test',
        DocumentFile     = 'file.txt')

    web2py.auth.add_permission(200, 'read', 'customers_documents', 0)
    web2py.db.commit()

    url = '/customers/documents?cuID=1001'
    client.get(url)
    assert client.status == 200

    assert not 'fa-times' in client.text

    # grant permission and check again
    web2py.auth.add_permission(200, 'delete', 'customers_documents', 0)
    web2py.db.commit()

    client.get(url)
    assert client.status == 200

    assert 'fa-times' in client.text


def test_customer_notes_delete(client, web2py):
    """
        Is the delete permission for notes under customers working?
    """
    # get random url to populate db.auth_user with admin
    client.get('/default/user/login')
    assert client.status == 200

    setup_permission_tests(web2py)
    populate_customers(web2py, 1)
    web2py.db.customers_notes.insert(
        auth_customer_id = 1001,
        auth_user_id     = 1,
        BackofficeNote   = True,
        NoteDate         = '2014-01-01',
        NoteTime         = "12:00",
        Note             = 'Strawberry')

    web2py.auth.add_permission(200, 'read', 'customers_notes', 0)
    web2py.auth.add_permission(200, 'read', 'customers_notes_backoffice', 0)
    web2py.db.commit()

    url = '/customers/notes?cuID=1001'
    client.get(url)
    assert client.status == 200

    assert not 'fa-times' in client.text

    # grant permission and check again
    web2py.auth.add_permission(200, 'delete', 'customers_notes', 0)
    web2py.db.commit()

    client.get(url)
    assert client.status == 200

    assert 'fa-times' in client.text



def test_task_delete(client, web2py):
    """
        Is the delete permission for a task working?
    """
    setup_permission_tests(web2py)
    web2py.db.tasks.insert(
        Finished     = False,
        Task         = 'Bananas',
        Description  = 'papaya',
        Duedate      = '2014-01-01',
        Priority     = 2,
        auth_user_id = 200)
    web2py.auth.add_permission(200, 'read', 'tasks', 0)

    web2py.db.commit()

    url = '/tasks/index'
    client.get(url)
    assert client.status == 200

    assert not 'fa-times' in client.text

    # grant permission and check again
    web2py.auth.add_permission(200, 'delete', 'tasks', 0)
    web2py.db.commit()

    client.get(url)
    assert client.status == 200

    assert 'fa-times' in client.text


def test_announcement_delete(client, web2py):
    """
        Is the delete permission for an announcement working?
    """
    setup_permission_tests(web2py)
    populate(web2py.db.announcements, 1)
    web2py.auth.add_permission(200, 'read', 'announcements', 0)

    web2py.db.commit()

    url = '/announcements/index'
    client.get(url)
    assert client.status == 200

    assert not 'fa-times' in client.text

    # grant permission and check again
    web2py.auth.add_permission(200, 'delete', 'announcements', 0)
    web2py.db.commit()

    client.get(url)
    assert client.status == 200

    assert 'fa-times' in client.text


def test_reports_postcode_group_delete(client, web2py):
    """
        Is the delete permission for a postcode group working?
    """
    setup_permission_tests(web2py)
    populate_postcode_groups(web2py)
    web2py.auth.add_permission(200, 'read', 'postcode_groups', 0)

    web2py.db.commit()

    url = '/reports/postcodes_groups_list'
    client.get(url)
    assert client.status == 200

    assert not 'fa-times' in client.text

    # grant permission and check again
    web2py.auth.add_permission(200, 'delete', 'postcode_groups', 0)
    web2py.db.commit()

    client.get(url)
    assert client.status == 200

    assert 'fa-times' in client.text


def test_reports_customers_inactive_delete(client, web2py):
    """
        Is the delete function protected?
    """
    setup_permission_tests(web2py)

    url = '/reports/customers_inactive_delete?date=2018-01-1'
    client.get(url)
    assert client.status == 200
    assert "Insufficient privileges" in client.text

    web2py.auth.add_permission(200, 'read', 'reports_customers', 0)
    web2py.auth.add_permission(200, 'delete', 'auth_user', 0)
    web2py.db.commit()

    client.get(url)
    assert client.status == 200

    assert 'Run report' in client.text
