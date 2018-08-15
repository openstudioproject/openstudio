#!/usr/bin/env python

import datetime
from gluon.contrib.populate import populate

from setup_profile_tests import setup_profile_tests


def populate_sys_properties_school_info(web2py):
    """
        Insert school info into db.sys_properties
    """
    web2py.db.sys_properties.bulk_insert(
        [ { 'Property' : 'company_name',          'PropertyValue' : 'Banana republic' },
          { 'Property' : 'company_address',       'PropertyValue' : '#1 Big street' },
          { 'Property' : 'company_phone',         'PropertyValue' : '0123456789' },
          { 'Property' : 'company_email',         'PropertyValue' : 'company@openstudioproject.com' },
          { 'Property' : 'company_registration',  'PropertyValue' : 'KVK 123456' } ]
    )

    web2py.db.commit()


def populate_sys_notifications(web2py, with_email=True):
    """
    populate sys_notifications
    """
    web2py.db.sys_notifications.insert(
        Notification="order_created",
        NotificationTitle="Order created",
        NotificationMessage="Orders message"
    )

    if with_email:
        populate_sys_notifications_email(web2py)

    web2py.db.commit()


def populate_sys_notifications_email(web2py):
    """
    populate sys_notifications_email
    """
    web2py.db.sys_notifications_email.insert(
        sys_notifications_id=1,
        Email="admin@openstudioproject.com"
    )

    web2py.db.commit()


def populate_school_classcards(
        web2py,
        nr=1,
        trialcard=True,
        membership_required=False
    ):
    """
        Add 'nr' of cards to school_classcards
    """
    i = 0
    for i in range(i, nr):
        web2py.db.school_classcards.insert(
            PublicCard = True,
            MembershipRequired = membership_required,
            Name = 'Classcard_' + unicode(i),
            Description = 'General card ' + unicode(i),
            Price = 125,
            Validity = 3,
            ValidityUnit = 'months',
            Classes = 10,
            Trialcard = False)

    if trialcard:
        web2py.db.school_classcards.insert(
            PublicCard = True,
            MembershipRequired = membership_required,
            Name = 'Proefweek',
            Description = 'General trialcard',
            Price = 15,
            Validity = 7,
            ValidityUnit = 'days',
            Trialcard = True)

    web2py.db.commit()


def populate_school_classcards_groups(web2py, populate_classcards=True):
    """
        Populate subscriptions and add 2 groups each with 2 subscriptions
    """
    if populate_classcards:
        populate_school_classcards(web2py, 6)

    web2py.db.school_classcards_groups.insert(
        Name = 'Group1',
        Description = 'This is the first group'
    )

    web2py.db.school_classcards_groups.insert(
        Name = 'Group2',
        Description = 'This is the second group'
    )

    web2py.db.school_classcards_groups_classcards.insert(
        school_classcards_groups_id = 1,
        school_classcards_id = 1
    )
    web2py.db.school_classcards_groups_classcards.insert(
        school_classcards_groups_id = 1,
        school_classcards_id = 2
    )

    web2py.db.school_classcards_groups_classcards.insert(
        school_classcards_groups_id = 2,
        school_classcards_id = 3
    )
    web2py.db.school_classcards_groups_classcards.insert(
        school_classcards_groups_id = 2,
        school_classcards_id = 4
    )

    web2py.db.commit()


def populate_payment_methods(web2py):
    """
        This function adds the following to the paymentmethods table
        1. Cash
        2. Wire transfer
        3. Direct debit
    """
    methods = ['Cash', 'Wire transfer', 'Direct debit']
    i = 1
    for method in methods:
        row = web2py.db.payment_methods(1)
        if not row is None:
            query = (web2py.db.payment_methods.id == i)
            web2py.db(query).delete()
        web2py.db.payment_methods.insert(id=i,
                                  Name=method)
        i += 1


def populate_school_locations(web2py, nr=1):
    """
        Populate school_locations table 
    """
    for i in range(1, nr+1):
        web2py.db.school_locations.insert(
            Name = 'location_' + unicode(i),
            AllowAPI = True
        )


def populate_school_classtypes(web2py, nr=1):
    """
        Populate school_locations table 
    """
    for i in range(1, nr+1):
        web2py.db.school_classtypes.insert(
            Name = 'classtype_' + unicode(i),
            AllowAPI = True,
            Description = 'Description_classtype_' + unicode(i)
        )


def populate_customers(web2py,
                       nr_of_customers=10,
                       tax_rates=True,
                       employee=False,
                       teacher=False,
                       created_on=datetime.datetime.now()):
    if tax_rates:
        populate_tax_rates(web2py)

    populate(web2py.db.school_discovery, 3)
    populate_school_locations(web2py, 2)
    populate(web2py.db.school_levels, 3)
    populate(web2py.db.school_languages, 2)

    for i in range(1, nr_of_customers+1):
        if i < 6:
            school_locations_id = 1
        else:
            school_locations_id = 2

        cuID = i + 1000 # avoid conflict with teachers when populating

        web2py.db.auth_user.insert(
            id                  = cuID,
            archived            = False,
            first_name          = 'customer_' + unicode(i),
            last_name           =  unicode(i),
            email               = 'customer' + unicode(i) + '@email.nl',
            customer            = True,
            city                = 'city_' + unicode(i),
            postcode            = '190-' + unicode(cuID) + 'A',
            school_locations_id = school_locations_id,
            employee=employee,
            teacher=teacher,
            created_on=created_on)

    web2py.db.commit()


def populate_customers_payment_info(web2py, nr_of_customers):
    for i in range (1, nr_of_customers+1):
        web2py.db.customers_payment_info.insert(
            auth_customer_id        = i + 1000,
            payment_methods_id      = 3,
            AccountNumber           = "Account" + unicode(i),
            AccountHolder           = "HolderName" + unicode(i),
            BIC                     = "BIC" + unicode(i))

    web2py.db.commit()


def populate_customers_with_subscriptions(web2py,
                                          nr_of_customers=4,
                                          invoices=False,
                                          credits=False,
                                          membership_required=False,
                                          created_on=datetime.date.today()):
    if nr_of_customers < 4:
        # Set minimum number of customers, at least one for each school subscription
        nr_of_customers = 4

    populate_tax_rates(web2py)
    populate_customers(web2py, nr_of_customers, created_on=created_on)
    populate_payment_methods(web2py)
    populate_customers_payment_info(web2py, nr_of_customers)
    populate_school_subscriptions(web2py, membership_required=membership_required)

    ss_one_price = web2py.db.school_subscriptions_price(1).Price

    for i in range (1, nr_of_customers - 2): # this generates nr_or_customers - 3
        aucID = i + 1000
        csID = web2py.db.customers_subscriptions.insert(
            auth_customer_id        = aucID,
            school_subscriptions_id = 1,
            Startdate               = '2014-01-01',
            Enddate                 = None,
            payment_methods_id      = 3) # 3 = direct debit


        # Add invoices?
        if invoices:
            iID = web2py.db.invoices.insert(
                invoices_groups_id = 100,
                customers_subscriptions_id = csID,
                SubscriptionMonth = 1,
                SubscriptionYear = 2014,
            )

            ciID = web2py.db.invoices_customers.insert(
                auth_customer_id = aucID,
                invoices_id = iID
            )

            cisID = web2py.db.invoices_customers_subscriptions.insert(
                customers_subscriptions_id = csID,
                invoices_id = iID
            )

            web2py.db.invoices_items.insert(
                invoices_id = iID,
                Sorting = 1,
                ProductName = 'Subscription',
                Description = 'csID',
                Quantity = 1,
                Price = ss_one_price,
                tax_rates_id = 1
            )

            # tax rates (1) = 21%
            TotalPrice = round(ss_one_price / 1.21, 2)
            VAT = round(ss_one_price - TotalPrice, 2)

            web2py.db.invoices_amounts.insert(
                invoices_id = iID,
                TotalPrice = TotalPrice,
                VAT = VAT,
                TotalPriceVAT = ss_one_price,

            )


    web2py.db.customers_subscriptions.insert(
        auth_customer_id        = i + 1 + 1000,
        school_subscriptions_id = 2,
        Startdate               = '2014-01-01',
        Enddate                 = None,
        payment_methods_id      = 3) # 3 = direct debit

    # ssu 3 monthly credits
    web2py.db.customers_subscriptions.insert(
        auth_customer_id        = i + 2 + 1000,
        school_subscriptions_id = 3,
        Startdate               = '2014-01-01',
        Enddate                 = None,
        payment_methods_id      = 3) # 3 = direct debit

    # ssu 4 no subscription unit defined
    web2py.db.customers_subscriptions.insert(
        auth_customer_id        = i + 2 + 1000,
        school_subscriptions_id = 4,
        Startdate               = '2014-01-01',
        Enddate                 = None,
        payment_methods_id      = 3) # 3 = direct debit
    # ssu 5 no classes defined
    web2py.db.customers_subscriptions.insert(
        auth_customer_id        = i + 3 + 1000, # last customer
        school_subscriptions_id = 5,
        Startdate               = '2014-01-01',
        Enddate                 = None,
        payment_methods_id      = 3) # 3 = direct debit



    # add alt. price for first subscription to check automatic creation of invoices
    web2py.db.customers_subscriptions_alt_prices.insert(
        customers_subscriptions_id      = 1,
        SubscriptionMonth               = 1,
        SubscriptionYear                = 2014,
        Amount                          = 12345,
        Description                     = 'Bananas',
        Note                            = 'Hi there, this is a test note',
    )

    # add pause to 2nd customer to be able to check if NO invoice is created
    web2py.db.customers_subscriptions_paused.insert(
        customers_subscriptions_id      = 2,
        Startdate                       = '2014-01-01',
        Enddate                         = '2014-01-31',
        Description                     = 'Cherries'
    )

    if credits:
        web2py.db.customers_subscriptions_credits.insert(
            customers_subscriptions_id=1,
            MutationType='add',
            MutationAmount='3456',
            MutationDateTime='2014-01-01 00:00:00',
            Description='Test mutation',
            SubscriptionYear='2014',
            SubscriptionMonth='1'
        )

    web2py.db.commit()


def populate_customers_with_classcards(web2py,
                                      nr_of_customers=10,
                                      nr_cards=1,
                                      trialcard=True,
                                      invoices=False,
                                      customers_populated=False,
                                      membership_required=False,
                                      created_on=datetime.date.today()):

    populate_school_classcards(
        web2py,
        nr_cards,
        trialcard = trialcard,
        membership_required = membership_required,
    )
    scd = web2py.db.school_classcards(1)

    if not customers_populated:
        populate_customers(web2py, nr_of_customers, created_on=created_on)

    trialcard_id = nr_cards + 1

    for i in range(1, nr_of_customers+1):
        aucID = i + 1000
        ccdID = web2py.db.customers_classcards.insert(
            auth_customer_id     = aucID,
            school_classcards_id = 1,
            Startdate            = '2014-01-01',
            Enddate              = '2014-01-31',
            Note                 = 'Cherries' )

        # Add invoices?
        if invoices:
            iID = web2py.db.invoices.insert(
                invoices_groups_id=100,
                SubscriptionMonth=1,
                SubscriptionYear=2014,
            )

            ciID = web2py.db.invoices_customers.insert(
                auth_customer_id = aucID,
                invoices_id = iID
            )

            web2py.db.invoices_items.insert(
                invoices_id=iID,
                Sorting=1,
                ProductName='Class card',
                Description='First card in school',
                Quantity=1,
                Price=scd.Price,
                tax_rates_id=1
            )

            # tax rates (1) = 21%
            TotalPrice = round(scd.Price / 1.21, 2)
            VAT = round(scd.Price - TotalPrice, 2)

            web2py.db.invoices_amounts.insert(
                invoices_id=iID,
                TotalPrice=TotalPrice,
                VAT=VAT,
                TotalPriceVAT=scd.Price,

            )

            web2py.db.invoices_customers_classcards.insert(
                invoices_id=iID,
                customers_classcards_id=ccdID
            )

    web2py.db.commit()


def populate_customers_with_memberships(web2py,
                                        nr_of_customers=10,
                                        nr_memberships=1,
                                        invoices=False,
                                        customers_populated=False,
                                        created_on=datetime.date.today()):

    populate_school_memberships(web2py)

    if not customers_populated:
        populate_customers(web2py, nr_of_customers, created_on=created_on)

    startdate = '2014-01-01'
    enddate = '2014-01-31'

    for i in range(1, nr_of_customers+1):
        aucID = i + 1000
        cmID = web2py.db.customers_memberships.insert(
            auth_customer_id = aucID,
            school_memberships_id = 1,
            Startdate = startdate,
            Enddate = enddate,
            Note = 'Cherries',
            payment_methods_id = 1,
        )

        # Add invoices?
        if invoices:
            smp = web2py.db.school_memberships_price(1)

            iID = web2py.db.invoices.insert(
                invoices_groups_id=100,
                InvoiceID="INV2018" + unicode(i),
                MembershipPeriodStart=startdate,
                MembershipPeriodEnd=enddate,
            )

            ciID = web2py.db.invoices_customers.insert(
                auth_customer_id = aucID,
                invoices_id = iID
            )

            web2py.db.invoices_items.insert(
                invoices_id=iID,
                Sorting=1,
                ProductName='Membership',
                Description='First membership in school',
                Quantity=1,
                Price=smp.Price,
                tax_rates_id=smp.tax_rates_id
            )

            # tax rates (1) = 21%
            TotalPrice = round(smp.Price / 1.21, 2)
            VAT = round(smp.Price - TotalPrice, 2)

            web2py.db.invoices_amounts.insert(
                invoices_id=iID,
                TotalPrice=TotalPrice,
                VAT=VAT,
                TotalPriceVAT=smp.Price,

            )

            web2py.db.invoices_customers_memberships.insert(
                invoices_id=iID,
                customers_memberships_id=cmID
            )

    web2py.db.commit()


def populate_auth_user_teachers(web2py,
                                teaches_classes=True,
                                teaches_workshops=True):
    """
        Adds 2 teachers to db.
        auth.user.ids 2 and 3
    """
    try:
        populate_tax_rates(web2py)
    except:
        print T('Tried to insert tax rates, but one or more already exists in db.tax_rates')

    try:
        web2py.db.auth_user.insert(
            id         = 2,
            first_name = 'first',
            last_name  = 'teacher',
            email      = 'teacher@openstudioproject.com',
            teacher    = True,
            teaches_classes = teaches_classes,
            teaches_workshops = teaches_workshops
        )

        web2py.db.auth_user.insert(
            id         = 3,
            first_name = 'second',
            last_name  = 'teacher',
            email      = 'teacher2@openstudioproject.com',
            teacher    = True,
            teaches_classes = teaches_classes,
            teaches_workshops = teaches_workshops
        )

        web2py.db.commit()


    except:
        print "Tried inserting teachers, but id 2 or 3 already exists in auth_user"


def populate_teachers_payment_classes(web2py, status='not_verified'):
    """

    """
    populate_tax_rates(web2py)
    prepare_classes(web2py)
    populate_auth_user_teachers_fixed_rate_default(web2py)

    web2py.db.commit()

    rate = web2py.db.teachers_payment_fixed_rate_default(1).ClassRate

    dates = [
        '2014-01-06',
        '2014-01-13',
        '2014-01-20',
        '2014-01-27',
    ]

    for date in dates:
        web2py.db.teachers_payment_classes.insert(
            classes_id = 1,
            ClassDate = date,
            AttendanceCount = 1,
            auth_teacher_id = 2,
            ClassRate = 25,
            tax_rates_id = 1,
            Status = status
        )

    web2py.db.commit()


def populate_teachers_payment_attendance_lists(web2py, with_rates=True):
    """
        Insert dummy list
    """
    populate_tax_rates(web2py)

    web2py.db.teachers_payment_attendance_lists.insert(
        Name = "Test list",
        tax_rates_id = 1,
    )

    web2py.db.commit()

    if with_rates:
        populate_teachers_payment_attendance_lists_rates(web2py)


def populate_teachers_payment_attendance_lists_rates(web2py):
    """
    Insert dummy date into list rates
    """
    for i in range(1, 11):
        web2py.db.teachers_payment_attendance_lists_rates.insert(
            teachers_payment_attendance_lists_id = 1,
            AttendanceCount = i,
            Rate = i * 1011
        )

    web2py.db.commit()


def populate_teachers_payment_attendance_lists_school_classtypes(web2py):
    """
    Dummy data for teachers_payment_attendance_lists_classtypes
    """
    populate_teachers_payment_attendance_lists(web2py)
    populate_school_classtypes(web2py, 3)

    for i in range(1, 4):
        web2py.db.teachers_payment_attendance_lists_school_classtypes.insert(
            teachers_payment_attendance_lists_id = 1,
            school_classtypes_id = i
        )

    web2py.db.commit()


def populate_auth_user_teachers_fixed_rate_default(web2py):
    """
        Insert dummy data for teachers_payment_fixed_rate_default
    """
    query = (web2py.db.auth_user.teacher == True)
    rows = web2py.db(query).select(web2py.db.auth_user.ALL)
    for row in rows:
        web2py.db.teachers_payment_fixed_rate_default.insert(
            auth_teacher_id = row.id,
            ClassRate = 10343,
            tax_rates_id = 1
        )

    web2py.db.commit()


def populate_auth_user_teachers_fixed_rate_class_1(web2py):
    """
        Insert dummy data for teachers_payment_fixed_rate_class
    """
    web2py.db.teachers_payment_fixed_rate_class.insert(
        auth_teacher_id = 2,
        classes_id = 1,
        ClassRate = 645570,
        tax_rates_id = 1
    )

    web2py.db.commit()


def populate_auth_user_teachers_fixed_rate_travel(web2py):
    """
        Insert dummy data for teachers_payment_fixed_rate_travel
    """
    web2py.db.teachers_payment_fixed_rate_travel.insert(
        auth_teacher_id = 2,
        school_locations_id = 1,
        TravelAllowance = 304753,
        tax_rates_id = 1
    )

    web2py.db.commit()


def populate_auth_user_teachers_payment_invoices(web2py):
    """
        Insert teacher payment invoices for all teachers
    """
    query = (web2py.db.auth_user.teacher == True)
    rows = web2py.db(query).select(web2py.db.auth_user.ALL)

    today = datetime.date.today()

    for row in rows:
        iID = web2py.db.invoices.insert(
            TeacherPayment = True,
            TeacherPaymentMonth = today.month,
            TeacherPaymentYear = today.year,
            CustomerName = row.display_name,
            Status = 'sent',
            InvoiceID = 'INV00' + unicode(row.id),
            Description = 'Payment test',
            DateCreated = today,
            DateDue = today + datetime.timedelta(days=31),
        )

        icID = web2py.db.invoices_customers.insert(
            auth_customer_id=row.id,
            invoices_id=iID
        )

        web2py.db.invoices_amounts.insert(invoices_id=iID)

    web2py.db.commit()

    populate_invoices_items(web2py, credit_items=True)


def populate_classes(web2py, with_otc=False):
    """
        This function creates a class and populates the required tables for that.
        To test classdate, '2014-01-06' can be used. This is a Monday.
    """
    populate(web2py.db.school_locations, 2)
    populate(web2py.db.school_classtypes, 3)
    populate(web2py.db.school_levels, 3)
    populate(web2py.db.tax_rates, 1)

    populate_auth_user_teachers(web2py)

    web2py.db.classes.insert(school_locations_id='1',
                             school_classtypes_id='1',
                             Week_day='1',
                             Starttime='06:00:00',
                             Endtime='09:00:00',
                             Startdate='2014-01-01',
                             Enddate='2090-01-01',
                             Maxstudents='20',
                             AllowAPI=True,
                             )

    web2py.db.classes_teachers.insert(classes_id=1,
                                      auth_teacher_id=2,
                                      auth_teacher_id2=3,
                                      teacher_role2=1, # subteacher
                                      Startdate='2014-01-01',
                                      Enddate='2090-01-01',
                                      )

    web2py.db.classes_price.insert(classes_id = 1,
                                   Dropin     = 17.5,
                                   tax_rates_id_dropin = 1,
                                   Trial      = 12.5,
                                   tax_rates_id_trial = 1,
                                   DropinMembership = 15,
                                   tax_rates_id_dropin_membership = 1,
                                   TrialMembership = 15,
                                   tax_rates_id_trial_membership = 1,
                                   Startdate  = '2014-01-01')


    if with_otc:
        web2py.db.classes_otc.insert(
            classes_id = 1,
            ClassDate  = '2014-01-06',
            school_locations_id = 2,
            school_classtypes_id = 2,
        )


    web2py.db.commit()


def prepare_classes(web2py,
                    nr_of_customers = 10,
                    cuID = 1001,
                    attendance=True,
                    with_subscriptions=True,
                    with_classcards=True,
                    with_reservations=True,
                    invoices=False,
                    credits=False,
                    created_on=datetime.date.today()):

    populate_customers_with_subscriptions(web2py,
                                          nr_of_customers,
                                          invoices=invoices,
                                          credits=credits,
                                          created_on=created_on)
    populate_customers_with_classcards(web2py,
                                       nr_of_customers=nr_of_customers,
                                       nr_cards=4,
                                       trialcard=False,
                                       invoices=invoices,
                                       customers_populated=True)
    populate_auth_user_teachers(web2py)
    populate_school_classtypes(web2py, 3)
    populate_school_subscriptions_groups(web2py, populate_subscriptions=False)
    populate_school_classcards_groups(web2py, populate_classcards=False)


    # Monday class
    web2py.db.classes.insert(school_locations_id=1,
                             school_classtypes_id=1,
                             Week_day=1,
                             Starttime='06:00:00',
                             Endtime='09:00:00',
                             Startdate='2014-01-01',
                             Enddate='2999-01-01',
                             Maxstudents=20,
                             MaxReservationsRecurring=2,
                             MaxReservationsDT=2,
                             MaxOnlineBooking=15,
                             AllowAPI=True,
                             AllowShopTrial=True
                             )

    # Monday class 2
    web2py.db.classes.insert(school_locations_id=1,
                             school_classtypes_id=1,
                             Week_day=1,
                             Starttime='09:15:00',
                             Endtime='10:45:00',
                             Startdate='2014-01-01',
                             Enddate='2999-01-01',
                             Maxstudents=20,
                             MaxReservationsRecurring=2,
                             MaxReservationsDT=2,
                             MaxOnlineBooking=15,
                             AllowAPI=True,
                             AllowShopTrial=True
                             )

    # Tuesday class
    web2py.db.classes.insert(school_locations_id=2,
                             school_classtypes_id=2,
                             Week_day=2,
                             Starttime='06:00:00',
                             Endtime='09:00:00',
                             Startdate='2014-01-01',
                             Enddate='2999-01-01',
                             Maxstudents=20,
                             MaxReservationsRecurring=2,
                             MaxReservationsDT=2,
                             MaxOnlineBooking=15,
                             AllowAPI=True,
                             AllowShopTrial=True
                             )

    # Add Monday class to the first subscriptions & classcard group
    web2py.db.classes_school_subscriptions_groups.insert(
        classes_id=1,
        school_subscriptions_groups_id=1,
        Enroll=True,
        ShopBook=True,
        Attend=True
    )

    web2py.db.classes_school_classcards_groups.insert(
        classes_id=1,
        school_classcards_groups_id=1,
        Enroll=True,
        ShopBook=True,
        Attend=True
    )

    ## Add stuff to Monday's class
    if with_reservations:
        # recurring class reservation
        web2py.db.classes_reservation.insert(auth_customer_id=cuID,
                                             classes_id='1',
                                             Startdate='2014-01-01',
                                             SingleClass=False,
                                             TrialClass=False)
        # dropin class reservation
        web2py.db.classes_reservation.insert(auth_customer_id=cuID,
                                             classes_id='1',
                                             Startdate='2014-01-06',
                                             SingleClass=True,
                                             TrialClass=False)
        # trial class reservation
        web2py.db.classes_reservation.insert(auth_customer_id=cuID,
                                             classes_id='1',
                                             Startdate='2014-01-06',
                                             SingleClass=True,
                                             TrialClass=True)

    web2py.db.classes_waitinglist.insert(auth_customer_id=cuID,
                                         classes_id='1')
    web2py.db.classes_teachers.insert(classes_id=1,
                                      auth_teacher_id=2,
                                      Startdate='2014-01-01')
    web2py.db.classes_teachers.insert(classes_id=2,
                                      auth_teacher_id=2,
                                      Startdate='2014-01-01')
    web2py.db.classes_teachers.insert(classes_id=3,
                                      auth_teacher_id=3,
                                      Startdate='2014-01-01')

    trial_price = 10
    dropin_price = 18
    trial_price_membership = 8
    dropin_price_membership = 15
    web2py.db.classes_price.insert(classes_id = 1,
                                   Dropin = dropin_price,
                                   tax_rates_id_dropin = 1,
                                   DropinMembership = dropin_price_membership,
                                   tax_rates_id_dropin_membership = 1,
                                   Trial = trial_price,
                                   tax_rates_id_trial = 1,
                                   TrialMembership=trial_price_membership,
                                   tax_rates_id_trial_membership=1,
                                   Startdate  = '2014-01-01')
    if attendance:
        # Trial class
        clattID = web2py.db.classes_attendance.insert(
            auth_customer_id=cuID,
            classes_id='1',
            ClassDate='2014-01-06', # this is a Monday ( week_day for the class defined above = 1 )
            AttendanceType='1')

        # Add invoices?
        if invoices:
            iID = web2py.db.invoices.insert(
                invoices_groups_id=100,
            )

            ciID = web2py.db.invoices_customers.insert(
                auth_customer_id = cuID,
                invoices_id = iID
            )

            web2py.db.invoices_items.insert(
                invoices_id=iID,
                Sorting=1,
                ProductName='Trial class',
                Description='',
                Quantity=1,
                Price=trial_price,
                tax_rates_id=1
            )

            # tax rates (1) = 21%
            TotalPrice = round(trial_price / 1.21, 2)
            VAT = round(trial_price - TotalPrice, 2)

            web2py.db.invoices_amounts.insert(
                invoices_id=iID,
                TotalPrice=TotalPrice,
                VAT=VAT,
                TotalPriceVAT=trial_price,
            )

            web2py.db.invoices_classes_attendance.insert(
                classes_attendance_id = clattID,
                invoices_id = iID
            )

            web2py.db.commit()

        # Drop in class
        clattID = web2py.db.classes_attendance.insert(auth_customer_id=cuID,
                                            classes_id='1',
                                            ClassDate='2014-01-13', # this is a Monday ( week_day for the class defined above = 1 )
                                            AttendanceType='2')

        # Add invoices?
        if invoices:
            iID = web2py.db.invoices.insert(
                invoices_groups_id=100,
            )

            ciID = web2py.db.invoices_customers.insert(
                auth_customer_id = cuID,
                invoices_id = iID
            )

            web2py.db.invoices_items.insert(
                invoices_id=iID,
                Sorting=1,
                ProductName='Drop in class',
                Description='',
                Quantity=1,
                Price=dropin_price,
                tax_rates_id=1
            )

            # tax rates (1) = 21%
            TotalPrice = round(dropin_price / 1.21, 2)
            VAT = round(dropin_price - TotalPrice, 2)

            web2py.db.invoices_amounts.insert(
                invoices_id=iID,
                TotalPrice=TotalPrice,
                VAT=VAT,
                TotalPriceVAT=dropin_price,
            )

            web2py.db.invoices_classes_attendance.insert(
                classes_attendance_id = clattID,
                invoices_id = iID
            )
            web2py.db.commit()

        # Subscription
        clattID = web2py.db.classes_attendance.insert(auth_customer_id=cuID,
                                            classes_id=1,
                                            ClassDate='2014-01-20',
                                            AttendanceType=None,
                                            customers_subscriptions_id=1)
        web2py.db.customers_subscriptions_credits.insert(
            customers_subscriptions_id = 1,
            classes_attendance_id = clattID,
            MutationDateTime = '2014-01-20 00:00:00',
            MutationType = 'sub',
            MutationAmount = 1,
            Description = 'Class on 2014-01-20 test',
        )

        # Class card
        web2py.db.classes_attendance.insert(auth_customer_id=cuID,
                                            classes_id=1,
                                            ClassDate='2014-01-27',
                                            AttendanceType=3,
                                            customers_classcards_id=1)

    # Class notes
    web2py.db.classes_notes.insert(
        classes_id = 1,
        auth_user_id = 1001,
        ClassDate = '2014-01-06',
        TeacherNote = True,
        Note = 'Avocado')


    web2py.db.commit()


def prepare_shifts(web2py, nr_of_customers = 10, cuID = 1001, with_otc = False):
    populate_customers(web2py, nr_of_customers, employee=True)
    populate(web2py.db.school_shifts, 3)

    web2py.db.shifts.insert(school_locations_id=1,
                            school_shifts_id=1,
                            Week_day=1,
                            Starttime='06:00:00',
                            Endtime='09:00:00',
                            Startdate='2014-01-01',
                            Enddate='2999-01-01' )

    web2py.db.shifts_staff.insert(shifts_id=1,
                                  auth_employee_id=1001,
                                  Startdate='2014-01-01')


    if with_otc:
        web2py.db.shifts_otc.insert(
            shifts_id=1,
            ShiftDate='2014-01-06',
            school_locations_id=2,
            school_shifts_id=2,
        )

    web2py.db.commit()


def prepare_shifts_and_classes_with_holiday(web2py):
    populate_customers(web2py, 2, employee=True, teacher=True)
    populate(web2py.db.school_shifts, 3)
    populate(web2py.db.school_classtypes, 3)

    web2py.db.shifts.insert(school_locations_id=1,
                            school_shifts_id=1,
                            Week_day=1,
                            Starttime='06:00:00',
                            Endtime='09:00:00',
                            Startdate='2014-01-01',
                            Enddate='2999-01-01' )

    web2py.db.shifts_staff.insert(shifts_id=1,
                                  auth_employee_id=1001,
                                  Startdate='2014-01-01')

    web2py.db.classes.insert(school_locations_id=1,
                             school_classtypes_id=1,
                             Week_day=1,
                             Starttime='06:00:00',
                             Endtime='09:00:00',
                             Startdate='2014-01-01',
                             Enddate='2999-01-01',
                             Maxstudents=20,
                             MaxReservationsRecurring=2,
                             MaxReservationsDT=2
                             )

    web2py.db.classes_teachers.insert(auth_teacher_id=1001,
                                      classes_id=1,
                                      Startdate='2014-01-01')

    web2py.db.teachers_holidays.insert(auth_teacher_id=1001,
                                       Startdate='2014-01-01',
                                       Enddate='2014-01-31',
                                       Note='Applejuice')

    web2py.db.commit()


def populate_workshops(web2py, teachers=True):
    """
        Adds some data to tables used for workshops
    """
    if teachers:
        populate_auth_user_teachers(web2py)

    populate(web2py.db.school_locations, 1)

    web2py.db.workshops.insert(
        Archived            = False,
        PublicWorkshop      = True,
        Name                = 'Introduction course',
        Startdate           = '2014-01-01',
        Enddate             = '2014-01-31',
        auth_teacher_id     = 2,
        auth_teacher_id2    = 3,
        school_locations_id = 1,
        Description         = 'Banana mango smoothie'
    )

    wsID = 1
    web2py.db.workshops_products.insert(
         workshops_id=wsID,
         FullWorkshop=True,
         PublicProduct=True,
         Deletable=False,
         Name='Full event',
         Price=100,
         PriceSubscription=81,
         PriceEarlybird=75,
         PriceSubscriptionEarlybird=70,
         EarlybirdUntil='2013-12-31',
         Description='Full event')

    web2py.db.commit()


def populate_sys_api_users(web2py):
    """
        Populate API users
    """
    web2py.db.sys_api_users.insert(ActiveUser=True,
                                   Username='test',
                                   APIKey='test',
                                   Description='test user')

    web2py.db.commit()


def populate_workshops_for_api_tests(web2py, teachers=True, auth_customer_id=1001):
    """
        Adds some data to tables used for workshops
    """
    populate_sys_api_users(web2py)
    populate_customers(web2py, 2)

    if teachers:
        populate_auth_user_teachers(web2py)

    populate(web2py.db.school_locations, 1)

    startdate = datetime.date.today()
    enddate = startdate + datetime.timedelta(days=14)

    auth_teacher_id = 2
    auth_teacher_id2 = 3

    wsID = web2py.db.workshops.insert(
        PublicWorkshop      = True,
        Archived            = False,
        Name                = 'Introduction course',
        Startdate           = startdate,
        Enddate             = enddate,
        Starttime           = '06:00',
        Endtime             = '09:00',
        auth_teacher_id     = auth_teacher_id,
        auth_teacher_id2    = auth_teacher_id2,
        school_locations_id = 1,
        Description         = 'Mango'
    )

    web2py.db.workshops_activities.insert(
        workshops_id=wsID,
        Activity='Activity Name',
        Activitydate=startdate,
        school_locations_id=1,
        Starttime='06:00',
        Endtime='15:00',
        Spaces=1,
        auth_teacher_id=auth_teacher_id,
        auth_teacher_id2=auth_teacher_id2
    )

    web2py.db.workshops_activities.insert(
        workshops_id=wsID,
        Activity='Activity End name',
        Activitydate=enddate,
        school_locations_id=1,
        Starttime='06:00',
        Endtime='09:00',
        Spaces=1,
        auth_teacher_id=auth_teacher_id,
        auth_teacher_id2=auth_teacher_id2
    )

    web2py.db.workshops_products.insert(
         workshops_id=wsID,
         FullWorkshop=True,
         Deletable=False,
         Name='Full event',
         Price=100,
         Description='Full event')

    web2py.db.workshops_products.insert(
         workshops_id=wsID,
         FullWorkshop=True,
         Deletable=False,
         Name='ExternalShopURL test',
         Price=200,
         Description='ExternalShopURL test',
         ExternalShopURL='http://www.jsdflkjsal.com/shop',
         AddToCartText='MangoSmoothie')

    web2py.db.workshops_products_customers.insert(
        workshops_products_id = wsID,
        auth_customer_id = auth_customer_id
    )

    web2py.db.commit()


def populate_workshops_with_activity(web2py, teachers=True):
    """
        Calls populate workshops and adds an activity
    """
    populate_tax_rates(web2py)
    populate_workshops(web2py, teachers=teachers)
    workshop = web2py.db.workshops(1)
    web2py.db.workshops_activities.insert(
        workshops_id = 1,
        Activity = 'Activity Name',
        Activitydate = '2014-01-06',
        school_locations_id = 1,
        Starttime = '06:00',
        Endtime = '09:00',
        Spaces = 1,
        auth_teacher_id = workshop.auth_teacher_id,
        auth_teacher_id2 = workshop.auth_teacher_id2
        )

    web2py.db.commit()


def populate_workshop_activity_overlapping_class(web2py):
    """
        Adds a workshop activity on 2014-01-06 (Monday),
        this overlaps with the class from populate_classes.
    """
    prepare_classes(web2py)
    # print 'classes ok'
    populate_workshops(web2py, teachers=False) # teachers are already populated by prepare_classes
    # print 'workshops ok'
    workshop = web2py.db.workshops(1)

    # print web2py.db().select(web2py.db.workshops.ALL)
    # print web2py.db().select(web2py.db.workshops_products.ALL)
    # print web2py.db().select(web2py.db.school_locations.ALL)
    # print web2py.db().select(web2py.db.auth_user.id, web2py.db.auth_user.first_name)

    web2py.db.workshops_activities.insert(
        workshops_id = 1,
        Activity = 'Activity Name',
        Activitydate = '2014-01-06',
        school_locations_id = 1,
        Starttime = '06:00',
        Endtime = '09:00',
        Spaces = 1,
        auth_teacher_id = workshop.auth_teacher_id,
        auth_teacher_id2 = workshop.auth_teacher_id2
        )
    web2py.db.commit()


def populate_workshops_products(web2py, workshops_id=1, nr_products=1):
    """
        Populate workshop products
    """
    for i in range(1, nr_products + 1):
        web2py.db.workshops_products.insert(
            workshops_id=workshops_id,
            Name="Product_" + unicode(i),
            PublicProduct=True,
            Price=100,
            PriceSubscription=90,
            PriceEarlybird=80,
            PriceSubscriptionEarlybird=70,
            EarlybirdUntil='2014-01-01',
            tax_rates_id=1
        )

    web2py.db.commit()


def populate_workshops_products_customers(web2py, created_on=datetime.date.today()):
    """
        Populate db tables so we have 2 products, one activity
        and 2 customers, 1 attending the full ws product and the other
        the other product
    """
    populate_payment_methods(web2py)
    populate_tax_rates(web2py)
    populate_workshops_with_activity(web2py)
    populate_customers(web2py, 2, created_on=created_on) # produces ids 1001 and 1002 in db.auth_user
    populate_workshops_products(web2py)

    wspID = 2
    web2py.db.workshops_products_activities.insert(workshops_products_id = wspID,
                                                   workshops_activities_id = 1)

    wspcID = web2py.db.workshops_products_customers.insert(workshops_products_id = wspID,
                                                           auth_customer_id = 1001)
    wspcID2 = web2py.db.workshops_products_customers.insert(workshops_products_id = 1,
                                                            auth_customer_id = 1002)

    iID = web2py.db.invoices.insert(
        invoices_groups_id=100,
        payment_methods_id=1,
        Status='sent',
        InvoiceID='INV' + unicode(1001),
        DateCreated='2014-01-01',
        DateDue='2014-01-15'
    )

    ciID = web2py.db.invoices_customers.insert(
        auth_customer_id=1001,
        invoices_id=iID
    )

    web2py.db.invoices_amounts.insert(
        invoices_id = iID,
        TotalPriceVAT = web2py.db.workshops_products(2).Price
    )

    iID2 = web2py.db.invoices.insert(
        invoices_groups_id=100,
        payment_methods_id=1,
        Status='sent',
        InvoiceID='INV' + unicode(1002),
        DateCreated='2014-01-01',
        DateDue='2014-01-15'
    )

    web2py.db.invoices_amounts.insert(
        invoices_id = iID2,
        TotalPriceVAT = web2py.db.workshops_products(1).Price
    )

    ciID2 = web2py.db.invoices_customers.insert(
        auth_customer_id=1002,
        invoices_id=iID
    )

    web2py.db.invoices_workshops_products_customers.insert(
        invoices_id = iID,
        workshops_products_customers_id = wspcID
    )

    web2py.db.invoices_workshops_products_customers.insert(
        invoices_id = iID2,
        workshops_products_customers_id = wspcID2
    )

    web2py.db.commit()


def populate_workshops_messages(web2py):
    """
        Populates db tables so we have a workshop, as in
        populate_workshops_products_customers

        Then adds a few messages
    """
    populate_workshops_products_customers(web2py)
    populate_messages(web2py, 1)

    web2py.db.workshops_messages.insert(workshops_id = 1,
                                        messages_id  = 1)

    web2py.db.commit()


def populate_messages(web2py, nr_messages=1):
    """
        Populates the messages table with a message
    """
    populate(web2py.db.messages, nr_messages)


def populate_tasks(web2py):
    """
        Populate tasks
    """
    populate_customers(web2py, 1)
    populate_workshops(web2py)

    one_day = datetime.timedelta(days=1)
    today = datetime.date.today()
    yesterday = today - one_day
    tomorrow = today + one_day

    # no customer, no workshop
    web2py.db.tasks.insert(
        Finished     = False,
        Task         = 'Eat delicious grapes',
        Description  = 'The red ones',
        Duedate      = datetime.date.today(),
        Priority     = 2,
        auth_user_id = 1,
        )

    # no customer, no workshop Finished
    web2py.db.tasks.insert(
        Finished     = True,
        Task         = 'Eat bananas',
        Description  = 'The yellow ones with black spots',
        Duedate      = datetime.date.today(),
        Priority     = 2,
        auth_user_id = 1,
        )

    # linked to customer
    web2py.db.tasks.insert(
        auth_customer_id = 1,
        Finished         = False,
        Task             = 'Make smoothie',
        Description      = 'Something with chocolate',
        Duedate          = yesterday,
        Priority         = 2,
        auth_user_id     = 1,
        )

    # linked to workshop
    web2py.db.tasks.insert(
        workshops_id = 1,
        Finished     = False,
        Task         = 'Eat pineapples',
        Description  = 'The yellow ones',
        Duedate      = tomorrow,
        Priority     = 2,
        auth_user_id = 1,
        )

    web2py.db.commit()


def populate_announcements(web2py, nr=10):
    """
        populates the announcements table
    """
    populate(web2py.db.announcements, nr)


def populate_school_memberships(web2py, price=True):
    """
        Add a membership with a price
    """
    populate_tax_rates(web2py)

    web2py.db.school_memberships.insert(
        Archived = False,
        Name = 'Premium membership',
        Description = 'premium membership',
        Terms = "Mango season",
        Validity = 1,
        ValidityUnit = 'months'
       )

    if price:
        web2py.db.school_memberships_price.insert(
            school_memberships_id = 1,
            Startdate = '1900-01-01',
            Price = 40,
            tax_rates_id=1
        )

    web2py.db.commit()


def populate_school_subscriptions(web2py, membership_required=False):
    """
        Add a few subscriptions with some prices
    """
    # 1
    web2py.db.school_subscriptions.insert(
        Archived    = False,
        PublicSubscription = True,
        MembershipRequired = membership_required,
        Name = 'one class a week',
        Classes = 1,
        SubscriptionUnit = 'week',
        CreditValidity=28, # 4 weeks
        Terms = 'Subscription terms go here and I want to eat a watermelon',
        SortOrder=0)

    # 2
    web2py.db.school_subscriptions.insert(
        Archived    = False,
        MembershipRequired=membership_required,
        Name        = 'Unlimited for free',
        Classes     = 0,
        CreditValidity=28,  # 4 weeks
        Unlimited   = True,
        SortOrder=0)

    # 3
    web2py.db.school_subscriptions.insert(
        Archived           = False,
        MembershipRequired=membership_required,
        Name               = 'one class a month',
        Classes            = 1,
        CreditValidity=28,  # 4 weeks
        SubscriptionUnit   = 'month',
        SortOrder=0
    )

    # 4
    web2py.db.school_subscriptions.insert(
        Archived=False,
        MembershipRequired=membership_required,
        Name='Unit not defined',
        Classes=1,
        CreditValidity=28,  # 4 weeks
        SubscriptionUnit=None,
        SortOrder=0
    )

    # 5
    web2py.db.school_subscriptions.insert(
        Archived = False,
        MembershipRequired=membership_required,
        Name = 'Classes not defined',
        Classes = None,
        CreditValidity=28,  # 4 weeks
        SubscriptionUnit = 'month',
        SortOrder=0
    )

    ss_one_price = 40
    web2py.db.school_subscriptions_price.insert(
        school_subscriptions_id = 1,
        Startdate = '1900-01-01',
        Price     = ss_one_price)

    web2py.db.school_subscriptions_price.insert(
        school_subscriptions_id = 2,
        Startdate = '1900-01-01',
        Price     = 0)

    web2py.db.commit()


def populate_school_subscriptions_groups(web2py, populate_subscriptions=True):
    """
        Populate subscriptions and add 2 groups each with 2 subscriptions
    """
    if populate_subscriptions:
        populate_school_subscriptions(web2py)

    web2py.db.school_subscriptions_groups.insert(
        Name = 'Group1',
        Description = 'This is the first group'
    )

    web2py.db.school_subscriptions_groups.insert(
        Name = 'Group2',
        Description = 'This is the second group'
    )

    web2py.db.school_subscriptions_groups_subscriptions.insert(
        school_subscriptions_groups_id = 1,
        school_subscriptions_id = 1
    )
    web2py.db.school_subscriptions_groups_subscriptions.insert(
        school_subscriptions_groups_id = 1,
        school_subscriptions_id = 2
    )

    web2py.db.school_subscriptions_groups_subscriptions.insert(
        school_subscriptions_groups_id = 2,
        school_subscriptions_id = 3
    )
    web2py.db.school_subscriptions_groups_subscriptions.insert(
        school_subscriptions_groups_id = 2,
        school_subscriptions_id = 4
    )

    web2py.db.commit()



def populate_postcode_groups(web2py):
    """
        Populate db.postcode_groups
    """
    web2py.db.postcode_groups.insert(
        Name          = 'group1',
        PostcodeStart = '190-1001A',
        PostcodeEnd   = '190-1005Z')

    web2py.db.commit()



def populate_tax_rates(web2py):
    """
        Populates tax rates table with some dummy data
    """
    web2py.db.tax_rates.insert(
        Name = 'BTW 21%',
        Percentage = 21
    )

    web2py.db.tax_rates.insert(
        Name = 'BTW 6%',
        Percentage = 6
    )

    web2py.db.commit()


# def populate_invoices_groups(web2py):
#     """
#         Populate invoices_groups
#     """
#     terms = 'Invoice Terms here'
#     footer = 'Invoice Footer here'
#
#     web2py.db.invoices_groups.insert(
#         id=100,
#         PublicGroup = True,
#         Name = 'Default',
#         NextID = 1,
#         PrefixYear = True,
#         Terms = terms,
#         Footer = footer
#     )
#
#     web2py.db.commit()

def populate_invoices(web2py, teacher_fixed_price_invoices=False):
    """
        Adds one invoice for each user found
    """
    populate_payment_methods(web2py)

    today = datetime.date.today()
    delta = datetime.timedelta(days = 14)

    teacher_payment = False,
    teacher_payment_month = None
    teacher_payment_year = None

    if teacher_fixed_price_invoices:
        teacher_payment = True
        teacher_payment_month = datetime.date.today().month
        teacher_payment_year = datetime.date.today().year

    rows = web2py.db().select(web2py.db.auth_user.ALL)
    for row in rows:
        cuID = row.id

        iID = web2py.db.invoices.insert(
            invoices_groups_id = 100,
            payment_methods_id = 3,
            TeacherPayment=teacher_payment,
            TeacherPaymentMonth=teacher_payment_month,
            TeacherPaymentYear=teacher_payment_year,
            CustomerName=row.display_name,
            Status = 'sent',
            InvoiceID = 'INV' + unicode(cuID),
            DateCreated = today,
            DateDue = today + delta
        )

        icID = web2py.db.invoices_customers.insert(
            auth_customer_id = cuID,
            invoices_id = iID
        )

        web2py.db.invoices_amounts.insert(invoices_id = iID)

    web2py.db.commit()


def populate_invoices_items(web2py, credit_items=False):
    """
        Adds an item for each invoice found
    """
    quantity = 10
    price = 12

    if credit_items:
        quantity = quantity * -1
        price = price * -1

    rows = web2py.db().select(web2py.db.invoices.ALL)
    for row in rows:
        iID = row.id

        web2py.db.invoices_items.insert(
            invoices_id         = iID,
            ProductName         = 'Fruits',
            Description         = 'Bananas',
            Quantity            = quantity,
            Price               = price
        )

        amounts = web2py.db.invoices_amounts(iID)
        amounts.TotalPriceVAT += (quantity * price)
        amounts.update_record()

    web2py.db.commit()


def populate_customers_orders(web2py):
    """
        Adds one invoice for each user found
    """
    populate_payment_methods(web2py)

    today = datetime.date.today()
    delta = datetime.timedelta(days = 14)

    rows = web2py.db().select(web2py.db.auth_user.ALL)
    for row in rows:
        cuID = row.id

        coID = web2py.db.customers_orders.insert(
            auth_customer_id = cuID,
            Status = 'awaiting_payment',
            CustomerNote = 'Order_note_for_' + unicode(cuID)
        )

        web2py.db.customers_orders_amounts.insert(customers_orders_id = coID)

    web2py.db.commit()


def populate_customers_orders_items(web2py,
                                    classcards=False,
                                    workshops_products=False,
                                    classes=False,
                                    donation=False):
    """
        Adds an item for each invoice found
    """
    Price = 12
    Quantity = 10
    Donation = False

    if classes:
        populate_classes(web2py)
        cls_price = web2py.db.classes_price(1)
        Price = cls_price.Dropin
        Quantity = 1
    if classcards:
        populate_school_classcards(web2py, 1, False)
        scd = web2py.db.school_classcards(1)
        Price = scd.Price
        Quantity = 1
    if workshops_products:
        populate_workshops_with_activity(web2py)
        populate_workshops_products(web2py, 1)
        wsp = web2py.db.workshops_products(1)
        Price = wsp.Price
        Quantity = 1
    if donation:
        Donation = True
        Price = 100
        Quantity = 1

    rows = web2py.db().select(web2py.db.customers_orders.ALL)
    for row in rows:
        coID = row.id

        school_classcards_id = None
        if classcards:
            school_classcards_id = 1

        workshops_products_id = None
        if workshops_products:
            workshops_products_id = 1

        classes_id = None
        class_date = None
        attendance_type = None
        if classes:
            classes_id = 1
            class_date = '2099-01-01'
            attendance_type = 2

        web2py.db.customers_orders_items.insert(
            customers_orders_id   = coID,
            Donation              = Donation,
            ProductName           = 'Fruits',
            Description           = 'Bananas',
            Quantity              = Quantity,
            Price                 = Price,
            school_classcards_id  = school_classcards_id,
            workshops_products_id = workshops_products_id,
            classes_id            = classes_id,
            ClassDate             = class_date,
            AttendanceType        = attendance_type
        )

        amounts = web2py.db.customers_orders_amounts(customers_orders_id = coID)
        amounts.TotalPriceVAT += Price
        amounts.update_record()

    web2py.db.commit()


def populate_customers_orders_amounts(web2py):
    """
        Set the TotalPriceVAT field to the total of items for each order
    """
    sum = web2py.db.customers_orders_items.TotalPriceVAT.sum()
    rows = web2py.db().select(
        web2py.db.customers_orders_items.customers_orders_id,
        sum,
        groupby=web2py.db.customers_orders_items.customers_orders_id,
    )

    for row in rows:
        web2py.db.customers_orders_amounts.insert(
            customers_orders_id = row.customers_orders_items.customers_orders_id,
            TotalPriceVAT = row[sum]
        )

    web2py.db.commit()


def populate_customers_shoppingcart(web2py):
    """
        Adds items to shoppingcart
    """
    setup_profile_tests(web2py)
    prepare_classes(web2py)
    populate_school_classcards(web2py, 1)

    web2py.db.customers_shoppingcart.insert(
        auth_customer_id=300,
        school_classcards_id=1
    )

    web2py.db.customers_shoppingcart.insert(
        auth_customer_id=300,
        classes_id=1,
        ClassDate='2099-01-01',
        AttendanceType=2
    )

    web2py.db.customers_shoppingcart.insert(
        auth_customer_id=300,
        classes_id=1,
        ClassDate='2099-01-01',
        AttendanceType=1
    )

    web2py.db.commit()


def populate_customers_notes(web2py,
                             customers=True,
                             created_on=datetime.date.today()):
    """
        Populate customers_notes table
    """
    if customers:
        populate_customers(web2py, 2, created_on=created_on)

    web2py.db.customers_notes.insert(
        auth_customer_id = 1001,
        auth_user_id = 1,
        BackofficeNote = True,
        NoteDate = '2014-01-01',
        NoteTime = '00:00:00',
        Note = 'Backoffice note content'
    )

    web2py.db.customers_notes.insert(
        auth_customer_id = 1001,
        auth_user_id = 1,
        TeacherNote = True,
        NoteDate = '2014-01-01',
        NoteTime = '00:00:00',
        Note = "I'm describing an injury here",
        Injury = True
    )

    web2py.db.customers_notes.insert(
        auth_customer_id = 1001,
        auth_user_id = 1,
        TeacherNote = True,
        NoteDate = datetime.date.today,
        NoteTime = '00:00:00',
        Note = "I'm a regular note",
        Injury = False
    )

    web2py.db.commit()




def populate_settings_shop_links(web2py):
    """
        Add a link for the shop
    """
    web2py.db.shop_links.insert(Name='Tweakers',
                                URL='http://www.tweakers.net')

    web2py.db.commit()


def populate_settings_shop_customers_profile_announcements(web2py):
    """
        Add an announcement
    """
    web2py.db.customers_profile_announcements.insert(
        PublicAnnouncement = True,
        Sticky = False,
        Title = 'Bananas',
        Announcement = 'Make a great, if not awesome, ingredient for smoothies',
        Startdate = '2014-01-01',
    )

    web2py.db.commit()

# def populate_reports_teacher_classes(web2py):
#     """
#         Populate all fields required to be able to test reports.py/teacher_classes
#     """
#     prepare_classes(web2py, with_subscriptions=True)
#     # teachers
#
#     # classes
#
#     # prices for classes
#
#     # Customers
#
#     # attendance


def populate_sys_organizations(web2py, nr_organizations=1):
    """
        Add an organization to sys_organizations
    """
    for i in range(0, nr_organizations):
        soID = unicode(i)

        default = True if i == 0 else False

        web2py.db.sys_organizations.insert(
            DefaultOrganization = default,
            Archived = False,
            Name = 'Organization_' + soID,
            Address = 'Address ' + soID,
            Phone = '123456' + soID,
            Email = 'info@organization' + soID + '.nl',
            Registration = 'reg_' + soID,
            TaxRegistration = 'reg_tax_' + soID,
            TermsConditionsURL = 'https://www.google.nl',
            TermsConditionsVersion = '2.12',
            PrivacyNoticeURL = 'https://www.google.nl',
            PrivacyNoticeVersion = '8.12',
            ReportsClassPrice = 10 * (i + 1)
        )

    web2py.db.commit()


def populate_reports_attendance_organizations(web2py):
    """
        Populate tables for reports_attendance_organizations
    """
    populate_sys_organizations(web2py, 2)
    prepare_classes(web2py)

    for i in range (1, 3):
        cls = web2py.db.classes(i)
        cls.sys_organizations_id = 1
        cls.update_record()

    school_subscr = web2py.db.school_subscriptions(1)
    school_subscr.sys_organizations_id = 2
    school_subscr.update_record()

    school_cc = web2py.db.school_classcards(1)
    school_cc.sys_organizations_id = 2
    school_cc.update_record()


    web2py.db.commit()


def populate_api_users(web2py):
    """
        Populate api users table
    """
    web2py.db.sys_api_users.insert(ActiveUser=True,
                                   Username='test',
                                   APIKey='test',
                                   Description='test user')

    web2py.db.commit()


def populate_mailing_lists(web2py):
    """
        Populate mailing lists
    """
    web2py.db.mailing_lists.insert(
        Name='Newsletter',
        Description='Newsletter for this studio',
        Frequency='Twice a year',
        MailChimpListID='mcID12345',
    )

    web2py.db.commit()


def populate_shop_products(web2py):
    """
        Populate shop_products
    """
    web2py.db.shop_products.insert(
        Name = "Coffee",
        Description = "Coffee",
        DescriptionShop = "Coffee shop description"
    )

    web2py.db.commit()


def populate_shop_products_variants(web2py,
                                    populate_products=True,
                                    populate_products_sets=False):
    """
        Populate shop_products_variants
    """
    if populate_products:
        populate_shop_products(web2py)
    populate_tax_rates(web2py)

    if populate_products_sets:
        populate_shop_products_sets(web2py,
                                    options=True,
                                    values=True)
        product = web2py.db.shop_products(1)
        product.shop_products_sets_id = 1
        product.update_record()

    web2py.db.shop_products_variants.insert(
        shop_products_id = 1,
        Name = 'Black',
        Price = '10',
        tax_rates_id = 1,
        DefaultVariant = True,
    )

    web2py.db.shop_products_variants.insert(
        shop_products_id = 1,
        Name = 'Latte',
        Price = '12',
        tax_rates_id = 1,
        DefaultVariant = False,
    )

    web2py.db.commit()
    

def populate_shop_products_sets(web2py,
                                options=False,
                                values=False):
    """
        Populate shop products_sets
    """
    spsID = web2py.db.shop_products_sets.insert(
        Archived = False,
        Name = "Size and color",
        Description = "Set size and color for options"
    )

    if values:
        options = True

    if options:
        spsoID = web2py.db.shop_products_sets_options.insert(
            shop_products_sets_id = spsID,
            Name = 'Color'
        )

        if values:
            web2py.db.shop_products_sets_options_values.insert(
                shop_products_sets_options_id = spsoID,
                Name = 'Red'
            )
            web2py.db.shop_products_sets_options_values.insert(
                shop_products_sets_options_id = spsoID,
                Name = 'Blue'
            )

    web2py.db.commit()


def populate_shop_brands(web2py):
    """
        Populate shop brands
    """
    web2py.db.shop_brands.insert(
        Archived = False,
        Name = "Dell",
        Description = "Cool laptops!"
    )

    web2py.db.commit()


def populate_shop_suppliers(web2py):
    """
        Populate shop suppliers
    """
    web2py.db.shop_suppliers.insert(
        Archived = False,
        Name = "FruitTraders",
        Description = "Great pineapples!"
    )

    web2py.db.commit()


def populate_shop_categories(web2py):
    """
        Populate shop categories
    """
    web2py.db.shop_categories.insert(
        Archived = False,
        Name = "FruitTraders",
        Description = "Great pineapples!"
    )

    web2py.db.commit()