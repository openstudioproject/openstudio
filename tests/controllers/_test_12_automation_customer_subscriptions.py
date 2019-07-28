# -*- coding: utf-8 -*-

import datetime
from populate_os_tables import populate_customers_with_subscriptions
from populate_os_tables import prepare_classes


def test_create_monthly_invoices_inv_date_today(client, web2py):
    """
        Can we create subscription invoices for a month?
    """
    # Get random url to initialize OpenStudio environment
    url = '/default/user/login'

    client.get(url)
    assert client.status == 200

    populate_customers_with_subscriptions(web2py, 10)


    url = '/test_automation_customer_subscriptions/' + \
          'test_create_invoices' + \
          '?month=1&year=2014&description=Subscription_Jan&invoice_date=today'
    client.get(url)
    assert client.status == 200


    # print web2py.db().select(web2py.db.invoices_items.ALL)
    # print web2py.db().select(web2py.db.invoices_items_customers_subscriptions.ALL)


    # check the created invoices
    ig_100 = web2py.db.invoices_groups(100)
    invoice = web2py.db.invoices(1)
    assert invoice.DateCreated == datetime.date.today()
    assert invoice.Status == 'sent'
    assert invoice.InvoiceID == 'INV' + str(datetime.date.today().year) + '1'
    assert ig_100.Terms == invoice.Terms
    assert ig_100.Footer == invoice.Footer

    iics = web2py.db.invoices_items_customers_subscriptions(1)
    assert iics.invoices_items_id == 1
    assert iics.customers_subscriptions_id == 1

    # Check that an invoice is created for the paused subscription
    iics = web2py.db.invoices_items_customers_subscriptions(2)
    print(iics)
    assert iics.invoices_items_id == 2
    assert iics.customers_subscriptions_id == 2


    ## check created invoice items
    ssup = web2py.db.school_subscriptions_price(1)
    # alt. Price subscription item (first subscription gets a different price)
    altp = web2py.db.customers_subscriptions_alt_prices(1)
    item = web2py.db.invoices_items(1)
    assert altp.Amount == item.Price
    assert altp.Description == item.Description

    # paused item
    item = web2py.db.invoices_items(2)
    assert item.Price < ssup.Price

    # regular item
    item = web2py.db.invoices_items(3)
    assert item.Price == ssup.Price


def test_create_monthly_invoices_inv_date_first_of_month(client, web2py):
    """
        Can we create subscription invoices for a month?
    """
    # Get random url to initialize OpenStudio environment
    url = '/default/user/login'

    client.get(url)
    assert client.status == 200

    populate_customers_with_subscriptions(web2py, 10)


    url = '/test_automation_customer_subscriptions/' + \
          'test_create_invoices' + \
          '?month=1&year=2014&description=Subscription_Jan&invoice_date=first_of_month'
    client.get(url)
    assert client.status == 200


    # print web2py.db().select(web2py.db.invoices_items.ALL)
    # print web2py.db().select(web2py.db.invoices_items_customers_subscriptions.ALL)

    # check the created invoices
    ig_100 = web2py.db.invoices_groups(100)
    invoice = web2py.db.invoices(1)
    assert invoice.DateCreated == datetime.date(2014, 1, 1)


def test_add_subscription_credits_for_month(client, web2py):
    """
        Are credits batch-added correctly?
    """
    import calendar

    # get a random url to initialize the OS environment
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    prepare_classes(web2py, credits=True)

    # Add credits
    url = '/test_automation_customer_subscriptions/test_add_subscription_credits_for_month?year=2014&month=1'
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


def test_subscription_credits_month_add_book_classes_for_recurring_reservations(client, web2py):
    """
        Are classes for recurring reservations booked?
    """
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

    # Add credits
    url = '/test_automation_customer_subscriptions/test_add_subscription_credits_for_month?year=2099&month=1'
    client.get(url)
    assert client.status == 200


    query = (web2py.db.classes_attendance.ClassDate >= '2099-01-01')
    assert web2py.db(query).count() == 2
