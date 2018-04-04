#!/usr/bin/env python

'''py.test test cases to test OpenStudio.

These tests run based on webclient and need web2py server running.
'''

import datetime
import calendar
from gluon.contrib.populate import populate
from populate_os_tables import prepare_classes
from populate_os_tables import populate_classes
from populate_os_tables import populate_customers
from populate_os_tables import populate_customers_with_subscriptions
from populate_os_tables import populate_customers_with_classcards
from populate_os_tables import populate_customers_payment_info
from populate_os_tables import populate_workshops_products_customers
from populate_os_tables import populate_workshops_with_activity
from populate_os_tables import populate_school_subscriptions
from populate_os_tables import populate_school_classcards

def test_customers_add(client, web2py):
    '''
        Created a customer?
    '''
    client.get('/customers/add')
    assert 'name="first_name"' in client.text
    assert 'name="last_name"' in client.text
    data = dict(first_name='Edwin',
                last_name='van de Ven',
                email='test@openstudioproject.com',
                )
    client.post('/customers/add', data=data)
    assert client.status == 200
    assert 'Profile' in client.text # verify redirection to edit page

    client.get('/customers')
    assert client.status == 200
    assert data['first_name'] in client.text
    assert data['last_name'] in client.text
    assert not 'class="error"' in client.text # make sure the form validated

    assert web2py.db(web2py.db.auth_user).count() == 2 # customer we just created and admin user
    assert web2py.db(web2py.db.auth_user.first_name == data['first_name']).count() == 1


def test_customers_edit(client, web2py):
    '''
        Can we edit a customer
    '''
    populate_customers(web2py)
    assert web2py.db(web2py.db.auth_user).count() > 0

    url = '/customers/edit/1001'
    client.get(url)
    assert client.status == 200

    data = {
        'id'            : 1001,
        'first_name'    : 'gorilla',
        'last_name'     : 'monkey',
        'email'         : 'gorilla@monkey.nl'
    }

    client.post(url, data=data)
    assert client.status == 200

    customer = web2py.db.auth_user(1001)
    assert customer.first_name == data['first_name']



def test_customers_edit_teacher(client, web2py):
    ''''
        Is the edit teacher page accepting submitted data?
    '''
    populate_customers(web2py, 2)
    assert web2py.db(web2py.db.auth_user).count() > 0

    url = '/customers/edit_teacher?cuID=1001'
    client.get(url)
    assert client.status == 200

    data = {
        'id'                : 1001,
        'teacher_bio'       : 'bananas',
        'education'         : 'cherries',
        'teacher_bio_link'  : 'mangoes',
        'teacher_website'   : 'pineapple'
    }

    client.post(url, data=data)
    assert client.status == 200

    customer = web2py.db.auth_user(1001)

    assert customer.teacher_bio == data['teacher_bio']
    assert customer.teacher_website == data['teacher_website']


def test_customers_archive(client, web2py):
    '''
        Can we archive a customer?
    '''
    populate_customers(web2py, 1)
    assert web2py.db(web2py.db.auth_user).count() == 1

    # archive
    client.get('/customers/archive?uID=1001')
    assert client.status == 200

    query = (web2py.db.auth_user.trashed == True)
    assert web2py.db(query).count() == 1

    # move to current
    client.get('/customers/archive?uID=1001')
    assert client.status == 200

    query = (web2py.db.auth_user.trashed == True)
    assert web2py.db(query).count() == 0


def test_load_list_birthday_icon(client, web2py):
    '''
        Is the birthday icon showing in load_list
    '''
    populate_customers(web2py, 1)

    # make it the first customers' birthday today
    today = datetime.date.today()
    customer = web2py.db.auth_user(1001)
    customer.date_of_birth = today
    customer.birthday = datetime.date(1900, today.month, today.day)
    customer.update_record()

    web2py.db.commit()

    url = '/customers/load_list?list_type=customers_index&initial_list=True&archived=False&items_per_page=7'
    client.get(url)
    assert client.status == 200
    assert 'fa-birthday-cake' in client.text


def populate_account_merge(client, web2py):
    '''
        Populates all tables with reference to auth_user for user 1002
        Also created user 1001 so we have an id to merge into
    '''
    # get a random url to initialize payment methods
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    merge_into_id = 1001
    merge_from_id = 1002

    prepare_classes(web2py, nr_of_customers=2, cuID=merge_from_id)
    # let's make merge_from_id a teacher as well
    user = web2py.db.auth_user(merge_from_id)
    user.teacher = True
    user.enabled = True
    user.update_record()

    populate_customers_payment_info(web2py, 2)

    # remove payment info for merge_into_id, so we're sure that the info from merge_from_id appears in the test data
    query = (web2py.db.customers_payment_info.auth_customer_id == merge_into_id)
    web2py.db(query).delete()

    populate_school_subscriptions(web2py)
    web2py.db.customers_subscriptions.insert(
        auth_customer_id        = merge_from_id,
        school_subscriptions_id = 1,
        Startdate               = '2014-01-01',
        payment_methods_id      = 3
        )

    populate_school_classcards(web2py)
    web2py.db.customers_classcards.insert(
        auth_customer_id      = merge_from_id,
        school_classcards_id  = 1,
        Startdate             = '2014-01-01',
        Enddate               = '2014-01-31'
        )

    web2py.db.customers_notes.insert(
        auth_customer_id = merge_from_id,
        auth_user_id     = merge_from_id, # to check if the task assignment also mergesz
        BackofficeNote   = True,
        NoteDate         = '2014-01-01',
        NoteTime         = '17:00',
        Note             = 'Test note',
        )

    web2py.db.tasks.insert(
        auth_customer_id = merge_from_id,
        Task             = 'Fix some bugs',
        Description      = 'Test',
        Duedate          = '2014-02-01',
        auth_user_id     = merge_from_id, # to check if the task assignment also merges
        )

    web2py.db.alternativepayments.insert(
        auth_customer_id    = merge_from_id,
        PaymentYear         = 2014,
        PaymentMonth        = 1,
        Amount              = 12.03,
        Description         = 'test'
        )

    iID = web2py.db.invoices.insert(
        invoices_groups_id      = 100,
        auth_customer_id        = merge_from_id,
        payment_methods_id      = 3,
        Status                  = 'sent',
        InvoiceID               = 'INV' + unicode(merge_from_id),
        DateCreated             = '2014-01-01',
        DateDue                 = '2014-01-31'
        )

    web2py.db.invoices_amounts.insert(invoices_id = iID)

    web2py.db.payment_batches.insert(
        BatchType     = 'collection',
        Name          = 'test',
        Description   = 'test',
        ColYear       = 2014,
        ColMonth      = 1,
        Exdate        = '2014-01-01'
        )
    web2py.db.payment_batches_items.insert(
        payment_batches_id    = 1,
        auth_customer_id      = merge_from_id,
        )

    web2py.db.customers_payments.insert(
        auth_customer_id    = merge_from_id,
        Amount              = 1434.12,
        PaymentDate         = '2014-01-01',
        payment_methods_id  = 3,
        )

    web2py.db.customers_documents.insert(
        auth_customer_id    = merge_from_id,
        Description         = 'test',
        DocumentFile        = 'DocumentFile.txt',
        )

    populate(web2py.db.messages, 1)
    web2py.db.customers_messages.insert(
        auth_customer_id    = merge_from_id,
        messages_id         = 1,
        Status              = 'fail',
        )

    populate_workshops_with_activity(web2py, teachers=False)
    web2py.db.workshops_products_customers.insert(
        auth_customer_id      = merge_from_id,
        workshops_products_id = 1
        )
    web2py.db.workshops_activities_customers.insert(
        auth_customer_id        = merge_from_id,
        workshops_activities_id = 1
        )

    # customer tables end

    # teacher tables begin

    web2py.db.teachers_holidays.insert(
        auth_teacher_id = merge_from_id,
        Startdate       = '2014-01-01',
        Enddate         = '2014-01-31',
        Note            = 'Winter holiday'
        )

    web2py.db.teachers_classtypes.insert(
        auth_user_id          = merge_from_id,
        school_classtypes_id = 1
        )

    cl_te = web2py.db.classes_teachers(1) # from prepare_classes
    cl_te.auth_teacher_id  = merge_from_id
    cl_te.auth_teacher_id2 = merge_from_id
    cl_te.update_record()

    web2py.db.classes_subteachers.insert(
        classes_id        = 1,
        ClassDate         = '2014-01-06',
        auth_teacher_id   = merge_from_id,
        auth_teacher_id2  = merge_from_id
        )

    workshop = web2py.db.workshops(1)
    workshop.auth_teacher_id  = merge_from_id
    workshop.auth_teacher_id2 = merge_from_id
    workshop.update_record()

    wsa = web2py.db.workshops_activities(1)
    wsa.auth_teacher_id  = merge_from_id
    wsa.auth_teacher_id2 = merge_from_id
    wsa.update_record()

    # teacher tables end

    # user tables begin

    web2py.db.payment_batches_exports.insert(
        auth_user_id       = merge_from_id,
        payment_batches_id = 1,
        )

    # user tables end

    web2py.db.commit()


def test_account_merge(client, web2py):
    '''
        Can we merge an account?
        We'll create 2 customers, attach all data to 2nd customer,
        then merge into first and check if we still have all data.
    '''
    def assert_count_customer(table, count):
        print 'Testing customer table: ' + unicode(table)
        query = (table.auth_customer_id == 1001)
        #print web2py.db().select(table.ALL)

        assert web2py.db(query).count() == count
        print 'OK'

    def assert_count_user(table, count):
        print 'Testing user table: ' + unicode(table)
        query = (table.auth_user_id == 1001)
        assert web2py.db(query).count() == count
        print 'OK'

    def assert_count_teacher(table, count):
        print 'Testing teacher table: ' + unicode(table)
        query = (table.auth_teacher_id == 1001)
        assert web2py.db(query).count() == count
        print 'OK'

    def assert_count_teacher2(table, count):
        print 'Testing teacher2 table: ' + unicode(table)
        query = (table.auth_teacher_id2 == 1001)
        assert web2py.db(query).count() == count
        print 'OK'

    populate_account_merge(client, web2py)

    # Execute the merge
    auth_merge_id = 1002
    url = '/customers/account_merge_execute?cuID=1001&auth_merge_id=' + unicode(auth_merge_id)
    client.get(url)
    assert client.status == 200

    ## check all tables in the DB [ nr_of_records, table ]
    customer_tables = [
        [ 1, web2py.db.alternativepayments ],
        [ 4, web2py.db.classes_attendance ],
        [ 3, web2py.db.classes_reservation ],
        [ 1, web2py.db.classes_waitinglist ],
        [ 3, web2py.db.customers_classcards ],
        [ 1, web2py.db.customers_documents ],
        [ 1, web2py.db.customers_messages ],
        [ 2, web2py.db.customers_payment_info ],
        [ 1, web2py.db.customers_payments ],
        [ 3, web2py.db.customers_subscriptions ],
        [ 1, web2py.db.customers_notes ],
        [ 1, web2py.db.invoices ],
        [ 1, web2py.db.payment_batches_items ],
        [ 1, web2py.db.tasks ],
        [ 1, web2py.db.workshops_activities_customers ],
        [ 1, web2py.db.workshops_products_customers ]
        ]

    for count, table in customer_tables:
        assert_count_customer(table, count)

    auth_user_tables = [
        [ 1, web2py.db.customers_notes ],
        [ 1, web2py.db.payment_batches_exports ],
        [ 1, web2py.db.tasks ],
        ]

    for count, table in auth_user_tables:
        assert_count_user(table, count)

    auth_teacher_tables = [
        [ 1, web2py.db.classes_teachers ],
        [ 1, web2py.db.classes_subteachers ],
        [ 1, web2py.db.teachers_holidays ],
        [ 1, web2py.db.workshops ],
        [ 1, web2py.db.workshops_activities ],
        ]

    for count, table in auth_teacher_tables:
        assert_count_teacher(table, count)

    auth_teacher2_tables = [
        [ 1, web2py.db.classes_teachers ],
        [ 1, web2py.db.classes_subteachers ],
        [ 1, web2py.db.workshops ],
        [ 1, web2py.db.workshops_activities ],
        ]

    for count, table in auth_teacher2_tables:
        assert_count_teacher2(table, count)


    # check if the user is a teacher now
    user = web2py.db.auth_user(1001)
    assert user.teacher == True
    assert user.enabled == True


    merged_user = web2py.db.auth_user(1002)
    assert merged_user.merged
    assert merged_user.merged_into == 1001
    assert not merged_user.merged_on is None

    # verify the flash message
    assert 'Merge success' in client.text


def test_customers_subscription_add(client, web2py):
    '''
        Can we add a customers_subscription?
    '''
    populate_school_subscriptions(web2py)
    populate_customers(web2py)
    assert web2py.db(web2py.db.school_subscriptions).count() > 0
    assert web2py.db(web2py.db.auth_user).count() > 0

    url = '/customers/subscription_add/?cuID=1'

    client.get(url)
    assert client.status == 200

    data = dict(school_subscriptions_id='1',
                Startdate='2014-01-01',
                )
    client.post(url, data=data)
    assert client.status == 200
    assert web2py.db(web2py.db.customers_subscriptions).count() == 1

    mstype_name = web2py.db.school_subscriptions(1).Name

    client.get('/customers/subscriptions?cuID=1')
    assert client.status == 200
    assert mstype_name in client.text


def populate_customer_subscriptions(client, web2py):
    # get random url to initialize payment methods in db
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_school_subscriptions(web2py)
    populate_customers(web2py)
    web2py.db.customers_subscriptions.insert(
        auth_customer_id        = 1001,
        school_subscriptions_id = 1,
        Startdate               = '2014-01-01',
        payment_methods_id      = 3,
        Note                    = "Hello world!")

    web2py.db.commit()

    assert web2py.db(web2py.db.school_subscriptions).count() > 0
    assert web2py.db(web2py.db.auth_user).count() > 0
    assert web2py.db(web2py.db.customers_subscriptions).count() > 0


def populate_customer_subscriptions_paused(client, web2py):
    '''
        Adds pause to subcription starting from 2014-01-01
    '''
    populate_customer_subscriptions(client, web2py)

    web2py.db.customers_subscriptions_paused.insert(
        customers_subscriptions_id = 1,
        Startdate                  = '2014-01-01',
        Enddate                    = '2014-01-31',
        Description                = 'Bananas')

    web2py.db.commit()


def test_customers_subscription_edit(client, web2py):
    '''
        can we edit a subscription?
    '''
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    prepare_classes(web2py)

    clattID = web2py.db.classes_attendance.insert(
        auth_customer_id = 1001,
        classes_id = 1,
        customers_subscriptions_id = 1,
        ClassDate = '2099-10-11',
        AttendanceType = None,
    )

    web2py.db.commit()

    url = '/customers/subscription_edit?cuID=1001&csID=1'
    client.get(url)
    assert client.status == 200

    data = dict(id=1,
                school_subscriptions_id = '1',
                Startdate               = '2013-01-01',
                Enddate                 = '2013-12-31'
                )
    client.post(url, data=data)
    assert client.status == 200

    assert 'Subscriptions' in client.text # verify redirection to customers/subscriptions
    assert data['Startdate'] in client.text

    # Check that the onaccept function for edit has changed the booking status,
    # as it's after today and after the subscription enddate
    clatt = web2py.db.classes_attendance(clattID)
    assert clatt.BookingStatus == 'cancelled'


def test_customers_subscription_delete(client, web2py):
    '''
        Is the custom delete function for customer subscriptions working?
    '''
    # get random url to initialize payment methods
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_customers_with_subscriptions(web2py, 2)

    # insert invoice and check that the subscription isn't deletable anymore
    web2py.db.invoices.insert(
        invoices_groups_id          = 100,
        auth_customer_id            = 1001,
        customers_subscriptions_id  = 1,
        SubscriptionMonth           = 1,
        SubscriptionYear            = 2014,
        Status                      = 'sent',
        DateCreated                 = '2014-01-01',
        DateDue                     = '2014-01-31',
    )

    web2py.db.commit()

    url = '/customers/subscription_delete?cuID=1001&csID=1'
    client.get(url)
    assert client.status == 200

    assert 'Unable to delete' in client.text

    # now remove invoices and try again
    web2py.db(web2py.db.invoices.id > 0).delete()
    web2py.db.commit()

    url = '/customers/subscription_delete?cuID=1001&csID=1'
    client.get(url)
    assert client.status == 200

    assert 'Deleted subscription' in client.text


def test_customers_subscriptions_list_recent_pauses(client, web2py):
    '''
        Is the list of paused subscriptions showing?
    '''
    # get random url to initialize payment methods in db
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_customer_subscriptions_paused(client, web2py)

    assert web2py.db(web2py.db.customers_subscriptions).count() == 1

    client.get('/customers/subscriptions?cuID=1001')
    assert client.status == 200
    assert 'Pauses' in client.text

    # check recent pauses
    assert '2014-01-01 - 2014-01-31' in client.text


def test_customers_subscriptions_pauses(client, web2py):
    '''
        Is the list of pauzed showing?
    '''
    # get random url to initialize payment methods in db
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_customer_subscriptions_paused(client, web2py)

    assert web2py.db(web2py.db.customers_subscriptions).count() == 1

    client.get('/customers/subscription_pauses?csID=1&cuID=1001')
    assert client.status == 200
    assert 'Pauses' in client.text

    # check listing
    pause = web2py.db.customers_subscriptions_paused(1)
    assert pause.Description in client.text


def test_customers_subscriptions_pause_add(client, web2py):
    '''
        Test adding of a pause
    '''
    # get random url to initialize payment methods in db
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_customer_subscriptions(client, web2py)

    url = '/customers/subscription_pause_add?csID=1'
    client.get(url)
    assert client.status == 200

    data = {'from_month'   : '1',
            'from_year'    : '2014',
            'until_month'  : '2',
            'until_year'   : '2',
            'description'  : 'Custard apple'}
    client.post(url, data=data)
    assert client.status == 200

    # verify redirection
    assert 'Subscriptions' in client.text

    # verify display
    assert data['description'] in client.text

    # verify database
    assert web2py.db(web2py.db.customers_subscriptions_paused).count() == 1


def test_customers_subscriptions_alt_prices_repeat(client, web2py):
    '''
        Test repeating of alt prices
    '''
    # get random url to initialize payment methods in db
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_customers_with_subscriptions(web2py)

    url = '/customers/subscription_alt_price_repeat?csapID=1'
    client.get(url)
    assert client.status == 200

    assert web2py.db(web2py.db.customers_subscriptions_alt_prices.id > 0).count() == 2


def test_customer_subscription_credits_month(client, web2py):
    '''
        Is the page listing added subscription credits showing?
    '''
    # get a random url to initialize the OS environment
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    prepare_classes(web2py, credits=True)

    url = '/customers/subscription_credits_month?year=2014&month=1'
    client.get(url)
    assert client.status == 200

    csc = web2py.db.customers_subscriptions_credits(1)
    assert str(round(csc.MutationAmount, 1)) in client.text


def test_customers_subscription_credits_month_add_confirm(client, web2py):
    '''
        Is the confirmation page to add credits showing?
    '''
    url = '/customers/subscription_credits_month_add_confirm'
    client.get(url)
    assert client.status == 200

    assert "Add confirmation" in client.text


def test_customers_subscription_credits_month_add(client, web2py):
    '''
        Are credits batch-added correctly?
    '''
    import calendar

    # get a random url to initialize the OS environment
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    prepare_classes(web2py, credits=True)

    # Set session variables
    url = '/customers/subscription_credits_month?year=2014&month=1'
    client.get(url)
    assert client.status == 200

    # Add credits
    url = '/customers/subscription_credits_month_add'
    client.get(url)
    assert client.status == 200

    # Check skipping of subscriptions that already got credits
    # count customers_subscriptions_id where mutationtype = add should be 1
    query = (web2py.db.customers_subscriptions_credits.MutationType=="add") & \
            (web2py.db.customers_subscriptions_credits.customers_subscriptions_id == 1)
    assert web2py.db(query).count() == 1

    # Check skipping of paused subscriptions
    # Customers_subscription 2 is paused in januari 2014
    query = (web2py.db.customers_subscriptions_credits.MutationType=="add") & \
            (web2py.db.customers_subscriptions_credits.customers_subscriptions_id == 2)
    assert web2py.db(query).count() == 0

    # Check skipping of school subscriptions where number of classes is None or == 0
    # Check skipping of school subscriptions where subscription unit is not defined
    query = (web2py.db.customers_subscriptions_credits.customers_subscriptions_id == 10) | \
            (web2py.db.customers_subscriptions_credits.customers_subscriptions_id == 11)
    assert web2py.db(query).count() == 0

    # Check calculation of amount of credits given for month
    # SSU 3
    assert web2py.db.customers_subscriptions_credits(8).MutationAmount == 1

    # Check calculation of amount of credits given for week
    first_day = datetime.date(2014, 1, 1)
    last_day =  datetime.date(first_day.year,
                              first_day.month,
                              calendar.monthrange(first_day.year,first_day.month)[1])

    t_days = (last_day - first_day) + datetime.timedelta(days=1)
    percent = 1 # (full  month of january should be calculated correctly

    ssu = web2py.db.school_subscriptions(1)
    subscription_unit = ssu.SubscriptionUnit
    classes = ssu.Classes
    if subscription_unit == 'month':
        credits = round(classes * percent, 1)
    else:
        weeks_in_month = round(t_days.days / float(7), 1)
        credits = round((weeks_in_month * classes) * percent, 1)

    assert web2py.db.customers_subscriptions_credits(3).MutationAmount == credits


def test_customers_subscription_credits_month_add_book_classes_for_recurring_reservations(client, web2py):
    '''
        Are classes for recurring reservations booked?
    '''
    ##
    # Check if classes for recurring reservations are booked
    ##
    import calendar

    # get a random url to initialize the OS environment
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    prepare_classes(web2py, credits=True)

    ##
    # Cancel a class
    ##
    web2py.db.classes_otc.insert(
        classes_id = 1,
        ClassDate = '2099-01-05', # First Monday for 2099
        Status = 'cancelled'
    )

    ##
    # Add a holiday so the second monday of month will be cancelled
    ##
    shID = web2py.db.school_holidays.insert(
        Description = 'test',
        Startdate = '2099-01-06',
        Enddate = '2099-01-13',
        Classes = True
    )

    web2py.db.school_holidays_locations.insert(
        school_holidays_id = shID,
        school_locations_id = 1,
    )

    web2py.db.commit()

    # Set session variables
    url = '/customers/subscription_credits_month?year=2099&month=1'
    client.get(url)
    assert client.status == 200

    # Add credits
    url = '/customers/subscription_credits_month_add'
    client.get(url)
    assert client.status == 200


    query = (web2py.db.classes_attendance.ClassDate >= '2099-01-01')
    assert web2py.db(query).count() == 2


def test_customers_subscription_credits_in_customers_list(client, web2py):
    '''
        Test listing of credits in customers list
    '''
    # get random url to initialize payment methods in db
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_customers_with_subscriptions(web2py, 4, credits=True)

    url = '/customers/load_list.load?list_type=customers-index&items_per_page=20&initial_list=True&archived=False&show_location=True&show_email=True'
    client.get(url)
    assert client.status == 200

    # check balance and listing
    assert '3456.0' in client.text


def test_customers_subscription_credits(client, web2py):
    '''
        Test listing of credits
    '''
    # get random url to initialize payment methods in db
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_customers_with_subscriptions(web2py, credits=True)

    url = '/customers/subscription_credits?cuID=1001&csID=1'
    client.get(url)
    assert client.status == 200

    # check balance and listing
    csc = web2py.db.customers_subscriptions_credits(1)
    assert csc.Description in client.text
    assert unicode(round(csc.MutationAmount, 1)) in client.text


def test_customers_subscription_credits_add(client, web2py):
    '''
        Can we add credits to a subscription?
    '''
    # get random url to initialize payment methods in db
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_customers_with_subscriptions(web2py, credits=False)

    url = '/customers/subscription_credits_add?cuID=1001&csID=1'
    client.get(url)
    assert client.status == 200

    data = {
        'MutationType':'add',
        'MutationAmount':123,
        'Description':'A coconut on a sunny beach would be nice...'
    }

    client.post(url, data=data)
    assert client.status == 200

    assert web2py.db(web2py.db.customers_subscriptions_credits.id > 0).count() == 1


def test_customers_subscription_credits_edit(client, web2py):
    '''
        Can we edit a credit mutation?
    '''
    # get random url to initialize payment methods in db
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_customers_with_subscriptions(web2py, credits=True)

    url = '/customers/subscription_credits_edit?cuID=1001&csID=1&cscID=1'
    client.get(url)
    assert client.status == 200

    data = {
        'id':1,
        'MutationType':'add',
        'MutationAmount':123,
        'Description':'A coconut on a sunny beach would be nice...'
    }

    client.post(url, data=data)
    assert client.status == 200

    csc = web2py.db.customers_subscriptions_credits(1)
    assert csc.Description == data['Description']


def test_customers_subscription_credits_delete(client, web2py):
    '''
        Can we delete a subscription credits mutation?
    '''
    # get random url to initialize payment methods in db
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_customers_with_subscriptions(web2py, credits=True)

    url = '/customers/subscription_credits_delete?cuID=1001&csID=1&cscID=1'
    client.get(url)
    assert client.status == 200

    assert web2py.db(web2py.db.customers_subscriptions_credits.id > 0).count() == 0


def test_customers_subscription_credits_month_expired(client, web2py):
    '''
        Is the display of expired credits working?
    '''
    # get random url to initialize payment methods in db
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_customers_with_subscriptions(web2py, credits=True)

    amount = 1234567
    web2py.db.customers_subscriptions_credits.insert(
        customers_subscriptions_id = 1,
        MutationDateTime = '2014-01-31 00:00:00',
        MutationType = 'sub',
        MutationAmount = amount,
        Description = 'Expiration January 2014',
        Expiration = True
    )

    web2py.db.commit()

    url = '/customers/subscription_credits_month_expired?year=2014&month=1'
    client.get(url)
    assert client.status == 200

    assert str(amount) in client.text


def test_customers_subscription_credits_month_expire_credits(client, web2py):
    '''
        Are credits being expired like they should
    '''
    # get random url to initialize payment methods in db
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_customers_with_subscriptions(web2py, credits=True)

    url = '/customers/subscription_credits_month_expire_credits'
    client.get(url)
    assert client.status == 200

    query = (web2py.db.customers_subscriptions_credits.Expiration == True)
    assert web2py.db(query).count() == 1


def test_classcard_add_classic(client, web2py):
    '''
        Add a classcard using a drop down menu
    '''
    populate_school_classcards(web2py, 8, trialcard = True)
    populate_customers(web2py, 1)

    # check redirection of add_classcard
    url = '/customers/classcard_add?cuID=1'
    client.get(url)
    assert client.status == 200
    assert not 'panel-primary' in client.text

    # check automatic calculating of enddate
    url = '/customers/classcard_add_classic?cuID=1'
    data = {'school_classcards_id' :  1,
            'Startdate'            : '2014-01-01',
            'Note'                 : 'Bananas'}
    client.post(url, data=data)
    assert client.status == 200

    # check db
    assert web2py.db(web2py.db.customers_classcards).count() == 1
    # check automatich adding of enddate
    assert web2py.db.customers_classcards(1).Enddate == datetime.date(2014, 3, 31)

    # check classcard invoice
    check_classcard_invoice(web2py)


def check_classcard_invoice(web2py):
    '''
        Check if an invoice is created correctly after adding a classcard
        to a customer
    '''
    assert web2py.db(web2py.db.invoices).count() == 1
    invoice = web2py.db.invoices(1)
    assert invoice.invoices_groups_id == 100

    iccd = web2py.db.invoices_customers_classcards(1)
    assert iccd.customers_classcards_id == 1

    price = web2py.db.school_classcards(1).Price
    invoice_amount = web2py.db.invoices_amounts(1).TotalPriceVAT

    assert price == invoice_amount


def test_classcard_add_classic_trialcard_removed_after_getting_one(client, web2py):
    '''
        Check that the trialcard options are no longer listed
    '''
    nr_cards = 10
    populate_school_classcards(web2py, nr_cards, trialcard = True)
    populate_customers(web2py, 1)

    trialcard_id = nr_cards + 1

    web2py.db.customers_classcards.insert(
        auth_customer_id = 1001,
        school_classcards_id = trialcard_id,
        Startdate = '2014-01-01',
        Enddate = '2014-01-31',
        Note = 'Cherries' )

    web2py.db.commit()
    # check db
    assert web2py.db(web2py.db.customers_classcards).count() == 1

    # check automatic calculating of enddate
    url = '/customers/classcard_add_classic?cuID=1001'
    client.get(url)
    assert client.status == 200
    assert web2py.db.school_classcards(trialcard_id).Name not in client.text


def test_classcard_add_modern(client, web2py):
    '''
        Add a classcard using fancy layout
    '''
    populate_school_classcards(web2py, 6, trialcard = True)
    populate_customers(web2py, 1)

    # check redirection of add_classcard
    url = '/customers/classcard_add?cuID=1'
    client.get(url)
    assert client.status == 200
    assert 'panel-primary' in client.text # now we're on the modern one
    # check automatic calculating of enddate

    # check automatic calculating of enddate
    url = '/customers/classcard_add_modern_add_card?cuID=1&scdID=1'
    data = {'school_classcards_id' :  1,
            'Startdate'            : '2014-01-01',
            'Note'                 : 'Bananas'}
    client.post(url, data=data)
    assert client.status == 200

    # check db
    assert web2py.db(web2py.db.customers_classcards).count() == 1
    # check automatich adding of enddate
    assert web2py.db.customers_classcards(1).Enddate == datetime.date(2014, 3, 31)

    # check classcard invoice
    check_classcard_invoice(web2py)


def test_classcard_add_modern_trialcard_removed_after_getting_one(client, web2py):
    '''
        Check that the trialcard options are no longer listed
    '''
    nr_cards = 5
    populate_school_classcards(web2py, nr_cards, trialcard = True)
    populate_customers(web2py, 1)

    trialcard_id = nr_cards + 1

    web2py.db.customers_classcards.insert(
        auth_customer_id = 1001,
        school_classcards_id = trialcard_id,
        Startdate = '2014-01-01',
        Enddate = '2014-01-31',
        Note = 'Cherries' )

    web2py.db.commit()
    # check db
    assert web2py.db(web2py.db.customers_classcards).count() == 1

    # check that the trialcard isn't listed
    url = '/customers/classcard_add_modern?cuID=1001'
    client.get(url)
    assert client.status == 200
    assert not web2py.db.school_classcards(trialcard_id).Name in client.text


def test_classcard_edit(client, web2py):
    '''
        can we edit a classcard?
    '''
    nr_cards = 1
    populate_school_classcards(web2py, nr_cards, trialcard = True)
    populate_customers(web2py, 1)

    trialcard_id = nr_cards + 1

    web2py.db.customers_classcards.insert(
        auth_customer_id = 1001,
        school_classcards_id = 1,
        Startdate = '2014-01-01',
        Enddate = '2014-01-31',
        Note = 'Cherries' )

    web2py.db.commit()

    assert web2py.db(web2py.db.auth_user).count() > 0
    assert web2py.db(web2py.db.customers_classcards).count() > 0

    url = '/customers/classcard_edit?cuID=1001&ccdID=1'
    client.get(url)
    assert client.status == 200

    data = dict(id=1,
                Startdate='2016-01-01',
                Enddate='2016-02-01',
                Note='Mango smoothie')
    client.post(url, data=data)
    assert client.status == 200

    assert 'Class cards' in client.text # check redirection
    assert data['Startdate'] in client.text # check form submission
    assert data['Enddate'] in client.text


def test_classcard_classes_taken(client, web2py):
    '''
        Is the list of classes taken on a class card working?
        Is classes_otc applied to this list?
    '''
    populate_classes(web2py, with_otc=True)
    populate_customers_with_classcards(web2py)

    web2py.db.classes_attendance.insert(
        classes_id = 1,
        ClassDate = '2014-01-06',
        auth_customer_id = 1001,
        customers_classcards_id = 1,
        AttendanceType = 3
    )

    web2py.db.commit()

    url = '/customers/classcard_classes?ccdID=1'
    client.get(url)
    assert client.status == 200

    # check classes_otc application
    location = web2py.db.school_locations(2).Name.split(' ')[0]
    assert location in client.text

    classtype = web2py.db.school_classtypes(2).Name.split(' ')[0]
    assert classtype in client.text


def test_classes_reservations_recurring(client, web2py):
    '''
        List reservations for a customer (this is the default)
    '''
    prepare_classes(web2py)

    url = '/customers/classes_reservations?cuID=1001'
    client.get(url)
    assert client.status == 200

    location_name = web2py.db.school_locations(1).Name.split(' ')[0]
    # make sure one reservation is showing
    assert client.text.count(location_name) == 1


def test_classes_reservations_filter_single(client, web2py):
    '''
        Check filter for single classes
    '''
    prepare_classes(web2py)

    url = '/customers/classes_reservations?cuID=1001&filter=single'
    client.get(url)
    assert client.status == 200

    location_name = web2py.db.school_locations(1).Name.split(' ')[0]
    # make sure one reservation is showing
    assert client.text.count(location_name) == 1


def test_classes_reservations_filter_trial(client, web2py):
    '''
        Check filter for trialclasses
    '''
    prepare_classes(web2py)

    url = '/customers/classes_reservations?cuID=1001&filter=trial'
    client.get(url)
    assert client.status == 200

    location_name = web2py.db.school_locations(1).Name.split(' ')[0]
    # make sure one reservation is showing
    assert client.text.count(location_name) == 1


def test_classes_reservation_add_list_classes_for_date(client, web2py):
    '''
        Does the listing of classes for a specified date work?
    '''
    prepare_classes(web2py)
    # we'll have to use a Monday ^ the function above only adds a class on Monday
    url = '/customers/classes_reservation_add?cuID=1001&date=2014-01-06'
    client.get(url)
    assert client.status == 200

    # check if we have a location and an add button
    assert 'Add' in client.text
    location_name = web2py.db.school_locations(1).Name.split(' ')[0]
    assert client.text.count(location_name) == 1


####
    '''
        Reservation add and edit are tested in the classes controller
    '''
####


def test_classes_waitinglist(client, web2py):
    '''
        Waitinglist for a customer
    '''
    prepare_classes(web2py)

    url = '/customers/classes_waitinglist?cuID=1001'
    client.get(url)
    assert client.status == 200

    #print web2py.db().select(web2py.db.classes_waitinglist.ALL)

    location_name = web2py.db.school_locations(1).Name.split(' ')[0]
    # make sure one reservation is showing
    assert client.text.count(location_name) == 1


def test_classes_attendance(client, web2py):
    '''
        Attendance for a customer
    '''
    prepare_classes(web2py)

    url = '/customers/classes_attendance?cuID=1001'
    client.get(url)
    assert client.status == 200

    location_name = web2py.db.school_locations(1).Name.split(' ')[0]
    # make sure one reservation is showing
    assert client.text.count(location_name) == 3


def test_classes_attendance_cancel_booking_and_refund_credits(client, web2py):
    '''
        Check if a booking is cancelled and credits are returned to a customer
    '''
    url = '/user/login'
    client.get(url)
    assert client.status == 200

    prepare_classes(web2py, credits=True)

    caID = 3

    url = '/customers/classes_attendance_cancel?caID=' + unicode(caID)
    client.get(url)
    assert client.status == 200

    # Check status
    clatt = web2py.db.classes_attendance(caID)
    assert clatt.BookingStatus == 'cancelled'

    # Check credit mutation removed
    query = (web2py.db.customers_subscriptions_credits.id > 0)
    assert web2py.db(query).count() == 1


def test_payments_info_add(client, web2py):
    """
        Can we add info for a customer?
    """
    populate_customers(web2py)
    assert web2py.db(web2py.db.auth_user).count() > 0

    url = '/customers/payment_info_add/1001'
    client.get(url)
    assert client.status == 200

    data = dict(payments_methods_id='3',
                AccountNumber='123456',
                AccountHolder='Hello',
                BIC="NLBIC123",
                MandateSignatureDate='2014-01-01',
                BankName='ING',
                BankLocation='NL'
                )
    client.post(url, data=data)
    assert client.status == 200
    assert "info" in client.text # check redirection
    assert data['AccountNumber'] in client.text

    client.get(url) # check if we can add only once
    assert client.status == 200
    assert 'already' in client.text

def test_payments_info_edit(client, web2py):
    """
        Can we edit info for a customer?
    """
    populate_customers(web2py, 1)

    # get a random url to make sure the setup function runs to populate the
    # payment_methods table
    url = '/customers/index'
    client.get(url)
    assert client.status == 200

    web2py.db.customers_payment_info.insert(auth_customer_id   = 1001,
                                            payment_methods_id = 3)
    web2py.db.commit()
    assert web2py.db(web2py.db.auth_user).count() > 0
    assert web2py.db(web2py.db.customers_payment_info).count() == 1

    url = '/customers/payment_info_edit/1001/1'

    client.get(url)
    assert client.status == 200

    data = dict(id                 = 1,
                auth_customer_id   = 1001,
                payment_methods_id='3',
                AccountNumber='123456',
                AccountHolder='Hello',
                BIC="NLBIC123",
                MandateSignatureDate='2014-01-01',
                BankName='ING',
                BankLocation='NL'
                )
    client.post(url, data=data)
    assert client.status == 200
    assert "info" in client.text # check redirection
    assert data['AccountNumber'] in client.text


def test_payments_ap_add(client, web2py):
    """
        Can we add an alternative payment?
    """
    today = datetime.date.today()
    populate_customers(web2py, 1)
    assert web2py.db(web2py.db.auth_user).count() == 1

    url = '/customers/alternativepayment_add/1001'
    client.get(url)
    assert client.status == 200

    assert 'value="' + unicode(today.year) + '"' in client.text # check default year value
    assert 'selected="selected" value="' + unicode(today.month) + '"' in client.text # check default month value

    data = dict(PaymentYear=today.year,
                PaymentMonth=today.month,
                Amount='99999',
                )
    client.post(url, data=data)
    assert client.status == 200
    assert "info" in client.text # check redirection
    assert data['Amount'] in client.text

def test_payments_ap_edit(client, web2py):
    """
        Can we edit an alternative payment?
    """
    populate_customers(web2py, 1)
    populate(web2py.db.payment_categories, 4)
    populate(web2py.db.alternativepayments, 1)
    assert web2py.db(web2py.db.auth_user).count() == 1
    assert web2py.db(web2py.db.alternativepayments).count() > 0

    url = '/customers/alternativepayment_edit/1001/1'
    client.get(url)
    assert client.status == 200

    data = dict(PaymentYear='2015',
                PaymentMonth='1',
                Amount='99999',
                )
    client.post(url, data=data)
    assert client.status == 200
    assert "info" in client.text # check redirection
    assert data['Amount'] in client.text


def test_documents(client, web2py):
    '''
        Can we get a list of the documents available?
    '''
    populate_customers(web2py, 1)
    assert web2py.db(web2py.db.auth_user).count() == 1

    url = '/customers/documents?cuID=1001'
    client.get(url)
    assert client.status == 200
    assert "Documents" in client.text


def test_notes(client, web2py):
    '''
        Can we get a list of notes and add a new note?
    '''
    populate_customers(web2py, 1)
    assert web2py.db(web2py.db.auth_user).count() == 1

    # check list
    url = '/customers/notes?cuID=1001'
    client.get(url)
    assert client.status == 200

    # check add
    data = dict(Note='Bananas',
                Alert='on')
    client.post(url, data=data)
    assert client.status == 200
    assert "Add a new note" in client.text # check if we're at the notes page
    assert data['Note'] in client.text

    # check delete
    url = '/customers/note_delete.json'

    data = dict(id='1')
    client.post(url, data=data)
    assert client.status == 200

    assert web2py.db(web2py.db.customers_notes).count() == 0


def test_events(client, web2py):
    '''
        Test display of workshops
    '''
    # get random url to initialize web2py environnment
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_workshops_products_customers(web2py)

    url = '/customers/events?cuID=1001'
    client.get(url)
    assert client.status == 200

    workshop = web2py.db.workshops(1)
    assert workshop.Name.split(' ')[0] in client.text
    # check label (product 2 is defined for cuID 1 in populate function)
    product = web2py.db.workshops_products(2)
    assert product.Name.split(' ')[0] in client.text
    # check payment and info form
    assert 'Event Info' in client.text


def test_event_add(client, web2py):
    '''
        Is the list of workshops showing?
    '''
    # get random url to initialize web2py environnment
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_workshops_products_customers(web2py)

    url = '/customers/event_add?cuID=1001'
    client.get(url)
    assert client.status == 200

    # check that the workshop is listed
    workshop = web2py.db.workshops(1)
    assert workshop.Name.split(' ')[0] in client.text
    # assert that the products button is showing
    assert 'Products' in client.text


def test_workshop_add_list_products(client, web2py):
    '''
        Is the list of workshop products showing from a customer?
    '''
    # get random url to initialize web2py environnment
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_workshops_products_customers(web2py)

    url = '/customers/events_add_list_tickets?cuID=1001&wsID=1'
    client.get(url)
    assert client.status == 200

    # check if the name of the workshop is showing
    workshop = web2py.db.workshops(1)
    assert workshop.Name.split(' ')[0] in client.text

    # check if the add button is showing
    assert 'Add' in client.text
    assert 'waitinglist' in client.text


# def test_load_list_sell_workshop_product(client, web2py):
#     '''
#         Test if the list shows
#     '''
#     populate_workshops_products_customers(web2py)
#
#     url = '/customers/load_list?list_type=workshops_products_sell&wsID=1&wspID=1'
#     client.get(url)
#     assert client.status == 200
#
#     customer = web2py.db.auth_user(1001)
#     assert customer.first_name in client.text


def test_payment_info_dutch_iban_validator_length_fail(client, web2py):
    '''
        Checks if the validator fails when the length of the number is too short
    '''
    # by getting some page the payment methods get initialized
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_customers(web2py, 1)
    populate_customers_payment_info(web2py, 1)

    url = '/customers/payment_info_edit/1001/1'
    client.get(url)
    assert client.status == 200

    data = {'id'            : 1,
            'AccountNumber' : 'NL21INGB012345678'} # 1 digit too short for valid Dutch IBAN
    client.post(url, data=data)
    assert client.status == 200

    assert 'Dutch IBAN should be 18 characters' in client.text


def test_payment_info_dutch_iban_validator_validation_fail(client, web2py):
    '''
        Checks if the validator fails when the IBAN isn't valid
    '''
    # by getting some page the payment methods get initialized
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_customers(web2py, 1)
    populate_customers_payment_info(web2py, 1)

    url = '/customers/payment_info_edit/1001/1'
    client.get(url)
    assert client.status == 200

    data = {'id'            : 1,
            'AccountNumber' : 'NL21INGB0123456789'} # Invalid Dutch IBAN
    client.post(url, data=data)
    assert client.status == 200

    assert 'IBAN validation failed' in client.text


def test_payment_info_dutch_iban_validator_pass(client, web2py):
    '''
        Checks if the validator passes on a correct number
    '''
    # by getting some page the payment methods get initialized
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_customers(web2py, 1)
    populate_customers_payment_info(web2py, 1)

    url = '/customers/payment_info_edit/1001/1'
    client.get(url)
    assert client.status == 200

    data = {'id'            : 1,
            'AccountNumber' : 'NL89TRIO0390502103'} # Valid Dutch IBAN
    client.post(url, data=data)
    assert client.status == 200

    # verify redirection
    assert 'Payment info' in client.text

    # verify database
    row = web2py.db.customers_payment_info(1)
    assert row.AccountNumber == data['AccountNumber']


def test_payment_info_not_iban_pass(client, web2py):
    '''
        Checks if the validator passes when something other than a dutch IBAN nr is added
    '''
    # by getting some page the payment methods get initialized
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_customers(web2py, 1)
    populate_customers_payment_info(web2py, 1)

    url = '/customers/payment_info_edit/1001/1'
    client.get(url)
    assert client.status == 200

    data = {'id'            : 1,
            'AccountNumber' : '12445565ef39i65'} # Random stuff
    client.post(url, data=data)
    assert client.status == 200

    # verify redirection
    assert 'Payment info' in client.text

    # verify database
    row = web2py.db.customers_payment_info(1)
    assert row.AccountNumber == data['AccountNumber'].upper()
