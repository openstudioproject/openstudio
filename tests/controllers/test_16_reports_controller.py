# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
    py.test test cases to test OpenStudio.
    These tests run based on webclient and need web2py server running.
"""

import datetime

from gluon.contrib.populate import populate

from populate_os_tables import populate_payment_methods
from populate_os_tables import populate_customers
from populate_os_tables import populate_customers_with_subscriptions
from populate_os_tables import populate_postcode_groups
from populate_os_tables import prepare_classes
from populate_os_tables import populate_classes
from populate_os_tables import populate_sys_organizations
from populate_os_tables import populate_reports_attendance_organizations



#def test_stats_customer_postcode_as_int(client, web2py):
    #"""
        #Check that the compute function for customers is working
    #"""
    #populate_customers(web2py)
    #populate_postcode_groups(web2py)

    #print web2py.db().select(web2py.db.auth_user.id,
                             #web2py.db.auth_user.postcode,
                             #web2py.db.auth_user.postcode_asint,
                             #)

    #url = '/default/user/login'
    #client.get(url)
    #assert client.status == 200

    #customer = web2py.db.auth_user(1001)
    #assert customer.postcode_asint == 190100110


def test_customers_inactive(client, web2py):
    """
        Can we list customers without activity after a given date?
    """
    populate_customers(web2py, created_on=datetime.date(2010, 1, 1))

    url = '/reports/customers_inactive'
    client.get(url)
    assert client.status == 200

    data = {
        'date':datetime.date.today()
    }
    client.post(url, data=data)
    assert client.status == 200

    assert web2py.db.auth_user(1001).first_name in client.text
    assert 'Found 10 customers without activity after' in client.text


def test_customers_inactive_dont_list_created_after_date(client, web2py):
    """
        Can we list customers without activity after a given date?
    """
    populate_customers(web2py, created_on=datetime.date(2010, 1, 1))

    url = '/reports/customers_inactive'
    client.get(url)
    assert client.status == 200

    data = {
        'date':datetime.date(2009, 1, 1)
    }
    client.post(url, data=data)
    assert client.status == 200

    assert web2py.db.auth_user(1001).first_name not in client.text


def test_customers_inactive_dont_list_with_subscription(client, web2py):
    """
        Customers with a subscription after given date
    """
    url = '/reports/customers_inactive'
    client.get(url)
    assert client.status == 200

    populate_customers_with_subscriptions(web2py,
                                          created_on=datetime.date(2014, 1, 1))
    data = {
        'date':datetime.date.today()
    }
    client.post(url, data=data)
    assert client.status == 200

    assert web2py.db.auth_user(1001).first_name not in client.text


def test_customers_inactive_dont_list_with_classcard(client, web2py):
    """
        Customers with a classcard after given date
    """
    from populate_os_tables import populate_customers_with_classcards

    url = '/reports/customers_inactive'
    client.get(url)
    assert client.status == 200

    populate_customers_with_classcards(web2py,
                                       created_on=datetime.date(2014, 1, 1))
    data = {
        'date':datetime.date(2014, 1, 1)
    }
    client.post(url, data=data)
    assert client.status == 200

    assert web2py.db.auth_user(1001).first_name not in client.text


def test_customers_inactive_dont_list_with_workshop_product(client, web2py):
    """
        Customers attending an event (workshop) on or after given date
    """
    from populate_os_tables import populate_workshops_products_customers

    url = '/reports/customers_inactive'
    client.get(url)
    assert client.status == 200

    populate_workshops_products_customers(web2py, created_on=datetime.date(2012,1,1))

    data = {
        'date':datetime.date(2014, 1, 1)
    }
    client.post(url, data=data)
    assert client.status == 200

    assert web2py.db.auth_user(1001).first_name not in client.text


def test_customers_inactive_dont_list_with_note(client, web2py):
    """
        Customers with note on or after given date
    """
    from populate_os_tables import populate_customers_notes

    url = '/reports/customers_inactive'
    client.get(url)
    assert client.status == 200

    populate_customers_notes(web2py, created_on=datetime.date(2012,1,1))

    data = {
        'date':datetime.date(2014, 1, 1)
    }
    client.post(url, data=data)
    assert client.status == 200

    assert web2py.db.auth_user(1001).first_name not in client.text


def test_customers_inactive_dont_list_with_class_attendance(client, web2py):
    """
        Customers attending a class after given date
    """
    from populate_os_tables import prepare_classes

    url = '/reports/customers_inactive'
    client.get(url)
    assert client.status == 200

    prepare_classes(web2py, created_on=datetime.date(2012,1,1))

    data = {
        'date':datetime.date(2014, 1, 1)
    }
    client.post(url, data=data)
    assert client.status == 200

    assert web2py.db.auth_user(1001).first_name not in client.text


def test_customers_inactive_dont_list_with_orders(client, web2py):
    """
        Customers with order after given date
    """
    from populate_os_tables import populate_customers_orders

    url = '/reports/customers_inactive'
    client.get(url)
    assert client.status == 200

    populate_customers(web2py, created_on=datetime.date(2012,1,1))
    populate_customers_orders(web2py)

    data = {
        'date':datetime.date(2014, 1, 1)
    }
    client.post(url, data=data)
    assert client.status == 200

    assert web2py.db.auth_user(1001).first_name not in client.text


def test_customers_inactive_dont_list_with_invoices(client, web2py):
    """
        Customers with invoice after given date
    """
    from populate_os_tables import populate_invoices

    url = '/reports/customers_inactive'
    client.get(url)
    assert client.status == 200

    populate_customers(web2py, created_on=datetime.date(2012,1,1))
    populate_invoices(web2py)

    data = {
        'date':datetime.date(2014, 1, 1)
    }
    client.post(url, data=data)
    assert client.status == 200

    assert web2py.db.auth_user(1001).first_name not in client.text


def test_customers_inactive_delete(client, web2py):
    """
        Are customers without activity after a given date actually deleted?
    """
    populate_customers(web2py, created_on=datetime.date(2010, 1, 1))

    url = '/reports/customers_inactive_delete'
    data = {
        'date':datetime.date.today()
    }
    client.post(url, data=data)
    assert client.status == 200

    count = web2py.db(web2py.db.auth_user.id > 1).count()
    assert count == 0 # Only admin user remaining
    assert 'Deleted 10 customers' in client.text


def test_reports_retention_dropoff_rate(client, web2py):
    """
        Is the retention rate calculated correctly?
    """
    # get random page to set up OpenStudio environment
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    prepare_classes(web2py)

    # check retention
    url = '/reports/retention_rate?p1_start=2014-01-01&p1_end=2014-01-31&p2_start=2014-02-01&p2_end=2014-02-28'
    client.get(url)
    assert client.status == 200
    assert '0.00%' in client.text

    # check drop off
    url = '/reports/dropoff_rate?p1_start=2014-01-01&p1_end=2014-01-31&p2_start=2014-02-01&p2_end=2014-02-28'
    client.get(url)
    assert client.status == 200
    assert '100.00%' in client.text

    # insert a class for February
    web2py.db.classes_attendance.insert(
        auth_customer_id        = 1001,
        classes_id              = 1,
        ClassDate               = '2014-02-03',
        AttendanceType          = 3,
        customers_classcards_id = 1
    )
    web2py.db.commit()

    # check retention
    url = '/reports/retention_rate?p1_start=2014-01-01&p1_end=2014-01-31&p2_start=2014-02-01&p2_end=2014-02-28'
    client.get(url)
    assert client.status == 200
    assert '100.00%' in client.text

    # check dropoff
    url = '/reports/dropoff_rate?p1_start=2014-01-01&p1_end=2014-01-31&p2_start=2014-02-01&p2_end=2014-02-28'
    client.get(url)
    assert client.status == 200
    assert '0.00%' in client.text


def test_reports_teacher_classes(client, web2py):
    """
        Does the page list the classes for the teacher (incl. sub classes correctly)
        Does the page list the revenue correctly?
    """
    # get random page to set up OpenStudio environment
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    prepare_classes(web2py, with_subscriptions=True, with_classcards=True, invoices=True)

    url = '/reports/teacher_classes?month=1&year=2014&teachers_id=2'
    client.get(url)
    assert client.status == 200

    # check listing of Trial amount
    assert '10.00' in client.text
    # check listing of Drop in amount
    assert '18.00' in client.text
    # check listing of subscription amount
    assert '40.00' in client.text
    # check listing of class card amount
    assert '12.50' in client.text


def test_reports_teacher_classes_class_revenue(client, web2py):
    """
        Does the page list the revenue breakdown correctly for this class
    """
    # get random page to set up OpenStudio environment
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    prepare_classes(web2py, with_subscriptions=True, with_classcards=True, invoices=True)

    # Check trial class
    url = '/reports/teacher_classes_class_revenue?clsID=1&date=2014-01-06'
    client.get(url)
    assert client.status == 200
    assert '10.00' in client.text
    # Check drop in class
    url = '/reports/teacher_classes_class_revenue?clsID=1&date=2014-01-13'
    client.get(url)
    assert client.status == 200
    assert '18.00' in client.text
    # Check subscription
    url = '/reports/teacher_classes_class_revenue?clsID=1&date=2014-01-20'
    client.get(url)
    assert client.status == 200
    assert '40.00' in client.text
    # Check class card
    url = '/reports/teacher_classes_class_revenue?clsID=1&date=2014-01-27'
    client.get(url)
    assert client.status == 200
    assert '12.50' in client.text


def test_reports_classcards(client, web2py):
    """
        Is the page showing?
    """
    pass
    #TODO: write test


def test_reports_classcards_current(client, web2py):
    """
        Is the page showing?
    """
    pass
    #TODO: write test


def test_reports_dropinclasses(client, web2py):
    """
        Is the page listing drop in classes for a month working?
    """
    populate_customers(web2py)
    populate_classes(web2py, with_otc=True)

    web2py.db.classes_attendance.insert(
        classes_id = 1,
        ClassDate = '2014-01-06',
        auth_customer_id = 1001,
        AttendanceType = 2,
    )

    web2py.db.commit()

    url = '/reports/dropinclasses?year=2014&month=1'
    client.get(url)
    assert client.status == 200

    location = web2py.db.school_locations(2).Name.split(' ')[0]
    assert location in client.text

    classtype = web2py.db.school_classtypes(2).Name.split(' ')[0]
    assert classtype in client.text


def test_reports_trialclasses(client, web2py):
    """
        Is the page listing drop in classes for a month working?
    """
    populate_customers(web2py)
    populate_classes(web2py, with_otc=True)

    web2py.db.classes_attendance.insert(
        classes_id = 1,
        ClassDate = '2014-01-06',
        auth_customer_id = 1001,
        AttendanceType = 1,
    )

    web2py.db.commit()

    url = '/reports/trialclasses?year=2014&month=1'
    client.get(url)
    assert client.status == 200

    location = web2py.db.school_locations(2).Name.split(' ')[0]
    assert location in client.text

    classtype = web2py.db.school_classtypes(2).Name.split(' ')[0]
    assert classtype in client.text



def test_reports_postcodes_groups_list(client, web2py):
    """
        Is the page that lists postcode groups working?
    """
    url = '/reports/postcodes_groups_list'
    client.get(url)
    assert client.status == 200


def test_reports_postcode_group_add(client, web2py):
    """
        Can we add a new postcode group?
    """
    url = '/reports/postcode_group_add'
    client.get(url)
    assert client.status == 200

    data = {'Name'            : 'Banana',
            'PostcodeStart'   : '190-1001A',
            'PostcodeEnd'     : '190-1005Z'}

    client.post(url, data=data)
    assert client.status == 200
    assert 'Edit postcode groups' in client.text # verify redirection
    assert 'Banana' in client.text

    # verify db
    query = (web2py.db.postcode_groups.id > 0)
    assert web2py.db(query).count() == 1


def test_reports_postcode_group_edit(client, web2py):
    """
        Can we edit a postcode group?
    """
    populate_postcode_groups(web2py)

    url = '/reports/postcode_group_edit?pgID=1'
    client.get(url)
    assert client.status == 200

    data = {'id'              : 1,
            'Name'            : 'Banana',
            'PostcodeStart'   : '190-1001A',
            'PostcodeEnd'     : '190-1005Z'}

    client.post(url, data=data)
    assert client.status == 200
    assert 'Edit postcode groups' in client.text # verify redirection
    assert 'Banana' in client.text

    # verify db
    query = (web2py.db.postcode_groups.id > 0)
    assert web2py.db(query).count() == 1


def test_reports_postcode_group_archive(client, web2py):
    """
        Test if a group can be (un)archived
    """
    populate_postcode_groups(web2py)

    url = '/reports/postcode_groups_archive?pgID=1'
    client.get(url)
    assert client.status == 200

    # check that there's one group that's archived
    query = (web2py.db.postcode_groups.Archived == True)
    count = web2py.db(query).count()
    assert count == 1

    url = '/reports/postcode_groups_archive?pgID=1'
    client.get(url)
    assert client.status == 200

    # check that there's one group that's not archived now
    query = (web2py.db.postcode_groups.Archived == False)
    count = web2py.db(query).count()
    assert count == 1


def test_reports_postcodes(client, web2py):
    """
        Is the stats page counting correct?
    """
    populate_customers(web2py)
    populate_postcode_groups(web2py)

    url = '/reports/postcodes'
    client.get(url)
    assert client.status == 200

    # check that count of groups postcodes is in the page data
    group = web2py.db.postcode_groups(1)
    query = (web2py.db.auth_user.postcode_asint >= group.PostcodeStart_AsInt) & \
            (web2py.db.auth_user.postcode_asint <= group.PostcodeEnd_AsInt)
    count = web2py.db(query).count()

    assert '<td>' + str(count) + '</td>' in client.text


def test_reports_attendance_review_requested(client, web2py):
    """
    Are check-ins listed as they should?
    """
    prepare_classes(web2py)

    url = '/reports/attendance_review_requested'
    client.get(url)
    assert client.status == 200

    assert '<td>customer_1 1</td>' in client.text
    assert '/classes/attendance_booking_options?clsID=1&amp;cuID=1001&amp;date=2014-02-03' in client.text


def test_reports_attendance_classtypes(client, web2py):
    """
        Is the attendance classtypes page counting correctly?
    """
    prepare_classes(web2py)

    url = '/reports/attendance_set_month?year=2014&month=1&back=/attendance_classtypes'
    client.get(url)
    assert client.status == 200

    url = '/reports/attendance_classtypes'
    client.get(url)
    assert client.status == 200
    assert 'January' in client.text

    assert '<td>3</td>' in client.text


def test_attendance_organizations(client, web2py):
    """
        Is the report showing correctly?
    """
    populate_reports_attendance_organizations(web2py)

    url = '/reports/attendance_organizations?year=2014&month=1'
    client.get(url)
    assert client.status == 200

    assert 'Resolve class price</div><div class="col-md-5"><span>€ 10.00' in client.text
    assert 'Classes taught</div><div class="col-md-5">8' in client.text
    assert 'Total attendance</div><div class="col-md-5"><a href="/reports/attendance_organizations_list_attendance?month=1&amp;soID=1&amp;year=2014">3</a>' in client.text
    assert 'Attendance from Organization_1</div><div class="col-md-5">1' in client.text

    # check resolve
    assert 'Organization_1 owes Organization_0</div><div class="col-md-5"><span>€ 10.00</span>' in client.text


def test_attendance_organizations_list_attendance(client, web2py):
    """
        test customers list for an organization
    """
    populate_reports_attendance_organizations(web2py)

    url = '/reports/attendance_organizations_list_attendance?year=2014&month=1&soID=1'
    client.get(url)
    assert client.status == 200

    # Check display of attendance from other organizations
    assert '2014-01-06' in client.text
    assert '2014-01-13' in client.text
    assert '2014-01-27' in client.text
    assert 'customer_1' in client.text
    assert '<span class="orange bold">Classcard_0</span>' in client.text


def test_reports_attendance_organizations_res_prices(client, web2py):
    """
        Is the page to list organizations with resolve prices showing?
    """
    populate_sys_organizations(web2py)

    url = '/reports/attendance_organizations_res_prices'
    client.get(url)
    assert client.status == 200

    so = web2py.db.sys_organizations(1)
    assert so.Name in client.text


def test_reports_attendance_organizations_res_price_edit(client, web2py):
    """
        Is the page to edit resolve prices for an organization showing?
    """
    populate_sys_organizations(web2py)

    url = '/reports/attendance_organizations_res_price_edit?soID=1'
    client.get(url)
    assert client.status == 200

    data = {
        'id':'1',
        'ReportsClassPrice':'123456'
    }

    client.post(url, data=data)
    assert client.status == 200
    assert data['ReportsClassPrice'] in client.text


def test_reports_subscriptions_alt_prices(client, web2py):
    """
        Is the list of alt. prices for subscriptions being shown correctly?
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_customers_with_subscriptions(web2py, 2)

    today = datetime.date.today()

    description = 'Red grapes'

    web2py.db.customers_subscriptions_alt_prices.insert(
        customers_subscriptions_id = 1,
        SubscriptionMonth          = today.month,
        SubscriptionYear           = today.year,
        Amount                     = 200,
        Description                = description,
    )

    web2py.db.commit()

    url = '/reports/subscriptions_alt_prices'
    client.get(url)
    assert client.status == 200
    assert description in client.text



def test_reports_subscriptions_overview_customers_location_filter(client, web2py):
    """
        Does the filter actually ... filter?
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_customers_with_subscriptions(web2py, 10)

    web2py.db.sys_properties.insert(
        Property='Customer_ShowLocation',
        PropertyValue='on'
    )

    web2py.db.commit()

    url = '/reports/subscriptions_overview_customers?school_locations_id=2&ssuID=1&year=2014&month=1'
    client.get(url)
    assert client.status == 200

    customer_2 = web2py.db.auth_user(1002)
    assert customer_2.display_name not in client.text

    customer_7 = web2py.db.auth_user(1007)
    assert customer_7.display_name in client.text


def test_reports_subscriptions_online(client, web2py):
    """
    Test listing of new online subscriptions
    """
    url = "/default/user/login"
    client.get(url)
    assert client.status == 200

    populate_payment_methods(web2py)
    populate_customers_with_subscriptions(web2py, nr_of_customers=2)

    today = datetime.date.today()

    cs = web2py.db.customers_subscriptions(1)
    cs.Startdate = today
    cs.payment_methods_id = 3
    cs.Origin = "SHOP"
    cs.Verified = True
    cs.update_record()
    web2py.db.commit()

    url = "/reports/subscriptions_online?year=%s&month=%s" % (today.year, today.month)
    client.get(url)
    assert client.status == 200

    # Check label display
    assert "Verified" in client.text

    # Check subscription name display
    ssu = web2py.db.school_subscriptions(cs.school_subscriptions_id)
    assert ssu.Name in client.text
