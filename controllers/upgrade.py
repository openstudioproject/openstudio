# -*- coding: utf-8 -*-

from general_helpers import max_string_length
from general_helpers import get_ajax_loader

from openstudio import Invoice, WorkshopProduct

from os_upgrade import set_version


def index():
    """
        This function executes commands needed for upgrades to new versions
    """
    # first check if a version is set
    if not db.sys_properties(Property='Version'):
        db.sys_properties.insert(Property='Version',
                                 PropertyValue=0)
        db.sys_properties.insert(Property='VersionRelease',
                                 PropertyValue=0)

    # check if a version is set and get it
    if db.sys_properties(Property='Version'):
        version = float(db.sys_properties(Property='Version').PropertyValue)

        if version < 2.17:
            print version
            upgrade_to217()

            session.flash = T("Upgraded db to 2.17")

        if version < 3.00:
            print version
            upgrade_to300()

            session.flash = T("Upgraded db to 3.00")

        if version < 3.01:
            print version
            upgrade_to301()

            session.flash = T("Upgraded db to 3.01")

        if version < 3.02:
            print version
            upgrade_to302()

            session.flash = T("Upgraded db to 3.02")

        if version < 3.03:
            print version
            upgrade_to303()

            session.flash = T("Upgraded db to 3.03")

        if version < 3.04:
            print version
            upgrade_to304()

            session.flash = T("Upgraded db to 3.04")

        if version < 3.05:
            print version
            upgrade_to305()

            session.flash = T("Upgraded db to 3.05")

        if version < 3.06:
            print version
            upgrade_to306()
            session.flash = T("Upgraded db to 3.06")

        if version < 3.07:
            print version
            upgrade_to307()
            session.flash = T("Upgraded db to 3.07")
        else:
            session.flash = T("Already up to date")

        if version < 3.09:
            print version
            upgrade_to309()
            session.flash = T("Upgraded db to 3.09")
        else:
            session.flash = T("Already up to date")

        if version < 2017.0:
            print version
            upgrade_to20170()
            session.flash = T("Upgraded db to 2017")
        else:
            session.flash = T('Already up to date')

        if version < 2017.2:
            print version
            upgrade_to_20172()
            session.flash = T("Upgraded db to 2017.2")
        else:
            session.flash = T('Already up to date')

        if version < 2017.4:
            print version
            upgrade_to_20174()
            session.flash = T("Upgraded db to 2017.4")
        else:
            session.flash = T('Already up to date')

        if version < 2017.5:
            print version
            upgrade_to_20175()
            session.flash = T("Upgraded db to 2017.5")
        else:
            session.flash = T('Already up to date')

        if version < 2017.6:
            print version
            upgrade_to_20176()
            session.flash = T("Upgraded db to 2017.6")
        else:
            session.flash = T('Already up to date')

        if version < 2017.7:
            print version
            upgrade_to_20177()
            session.flash = T("Upgraded db to 2017.7")
        else:
            session.flash = T('Already up to date')

        if version < 2018.1:
            print version
            upgrade_to_20181()
            session.flash = T("Upgraded db to 2018.1")
        else:
            session.flash = T('Already up to date')

        # always renew permissions for admin group after update
        set_permissions_for_admin_group()

    set_version()

    # Clear system properties cache
    cache_clear_sys_properties()

    # Clear menu cache
    cache_clear_menu_backend()

    # Back to square one
    redirect(URL('default', 'user', args=['login']))


def upgrade_to217(var=None):
    '''
        Upgrade db to 2.17
    '''
    from general_helpers import string_to_int

    # Db changes for merges and set everyone as customer, except admin
    rows = db().select(db.auth_user.ALL)
    for row in rows:
        row.merged = False
        if row.id > 1:
            # except admin
            row.customer = True
        if row.employee == None:
            # migration for employees
            row.employee = False

        row.update_record()

    # Db changes for postcode groups (set postcode_asint field)
    query = (db.auth_user.postcode != '') & \
            (db.auth_user.postcode != None)
    rows = db(query).select(db.auth_user.ALL)

    for row in rows:
        row.postcode_asint = string_to_int(row.postcode)
        row.update_record()


def upgrade_to300(var=None):
    '''
        Upgrade db to 3.00
    '''
    ## Set default values for new field MonthlyClasses in school_subscriptions
    query = (db.school_subscriptions.MonthlyClasses == None)
    db(query).update(MonthlyClasses=0)

    ## Use new Unlimited boolean to specify unlimited classes
    query = (db.school_subscriptions.NRofClasses == None)
    db(query).update(NRofClasses = 0, Unlimited=True)


    # Create default invoice group
    db.invoices_groups.insert(
        id=100,
        Archived=False,
        Name='Default',
        NextID=1,
        DueDays=30,
        InvoicePrefix='INV',
        PrefixYear=True,
    )

    # Set default invoice group as default for products
    product_types = get_invoices_groups_product_types()

    for product, name in product_types:
        db.invoices_groups_product_types.insert(
            ProductType = product,
            invoices_groups_id = 100
        )

    ## Create invoices for workshops_products_customers entries
    # create invoices group
    igID = db.invoices_groups.insert(
        Name          = 'Workshops Products Customers Migration',
        NextID        = 1,
        InvoicePrefix = 'OSWSM_INV',
        PrefixYear    = False,
        Archived      = True,
    )

    # get workshop products customers
    rows = db().select(db.workshops_products_customers.ALL)
    # create invoice for each sold workshop product
    for row in rows:
        cuID   = row.auth_customer_id
        wspID  = row.workshops_products_id
        wspcID = row.id
        product = WorkshopProduct(wspID)

        description = product.workshop_name + ' - ' + product.name
        delta = datetime.timedelta(days = 30)
        duedate = product.workshop.Startdate + delta

        iID = db.invoices.insert(
            invoices_groups_id              = igID,
            auth_customer_id                = cuID,
            workshops_products_customers_id = wspcID,
            Description                     = description,
            DateCreated                     = product.workshop.Startdate,
            DateDue                         = product.workshop.Startdate,
            Status                          = 'sent'
            )

        # create object to set Invoice# and due date
        invoice = Invoice(iID)
        next_sort_nr = invoice.get_item_next_sort_nr()

        tax_percentage = product.get_tax_rate_percentage()

        if tax_percentage:
            price = product.price / ((tax_percentage/100) + 1)
        else:
            price = product.price

        if not price:
            # catch None values and empty strings
            price = 0

        iiID = db.invoices_items.insert(
            invoices_id  = iID,
            ProductName  = T("Event"),
            Description  = description,
            Quantity     = 1,
            Price        = price,
            Sorting      = next_sort_nr,
            tax_rates_id = product.tax_rates_id,
        )

        invoice.set_amounts()

        ## check for payments
        query = (db.customers_payments.auth_customer_id == cuID) & \
                (db.customers_payments.workshops_products_id == wspID)

        prows = db(query).select(db.customers_payments.ALL)
        if len(prows) > 0:
            # we have a payment
            payment = prows.first()
            db.invoices_payments.insert(
                invoices_id        = iID,
                Amount             = payment.Amount,
                PaymentDate        = payment.PaymentDate,
                payment_methods_id = payment.payment_methods_id,
                Note               = payment.Note
            )

            invoice.set_status('paid')


    ## Migrate overdue payments to invoices
    # create invoices group
    igID = db.invoices_groups.insert(
        Name          = 'Overdue Payments Migration',
        NextID        = 1,
        InvoicePrefix = 'OSOP_INV',
        PrefixYear    = False,
        Archived      = True,
    )

    query = (db.overduepayments.id > 0)
    rows = db(query).select(db.overduepayments.ALL)

    for row in rows:
        cuID   = row.auth_customer_id

        description = row.Description
        delta = datetime.timedelta(days = 30)
        duedate = row.PaymentDate + delta

        iID = db.invoices.insert(
            invoices_groups_id              = igID,
            auth_customer_id                = cuID,
            Description                     = description,
            DateCreated                     = row.PaymentDate,
            DateDue                         = duedate,
            Status                          = 'sent'
            )

        # create object to set Invoice# and due date
        invoice = Invoice(iID)
        next_sort_nr = invoice.get_item_next_sort_nr()

        price = row.Amount

        if not price:
            # catch None values and empty strings
            price = 0

        iiID = db.invoices_items.insert(
            invoices_id  = iID,
            ProductName  = description,
            Description  = description,
            Quantity     = 1,
            Price        = price,
            Sorting      = next_sort_nr,
        )

        invoice.set_amounts()

        ## check for payments
        if row.Paid:
            # we have a payment
            db.invoices_payments.insert(
                invoices_id        = iID,
                Amount             = row.Amount,
                PaymentDate        = row.PaymentDate,
                payment_methods_id = 1,
            )

            invoice.set_status('paid')


    ## Fill full_name & display_name field in auth_user
    query = (db.auth_user.id > 0)
    rows = db(query).select(db.auth_user.ALL)
    for row in rows:
        row.full_name = row.first_name.strip() + ' ' + row.last_name.strip()
        row.display_name = row.first_name.strip() + ' ' + row.last_name.strip()
        row.update_record()


def upgrade_to301(var=None):
    '''
        Upgrade operations for 3.00 --> 3.01
    '''
    # migrate school holidays locations
    query = (db.school_holidays.id > 0)
    rows = db(query).select(db.school_holidays.ALL)
    for row in rows:
        # set Shifts to True
        row.Shifts = True
        row.update_record()
        # migrate locations
        shID = row.id
        loc_ids = row.school_locations_ids
        try:
            for locID in loc_ids:
                db.school_holidays_locations.insert(
                    school_holidays_id = shID,
                    school_locations_id = locID
                )
        except TypeError:
            # None type is not iterable
            pass


def upgrade_to302(var=None):
    '''
        Upgrade operations for 3.01 --> 3.02
    '''
    # set all teachers to teach classes
    query = (db.auth_user.teacher == True)
    rows = db(query).select(db.auth_user.ALL)
    for row in rows:
        row.teaches_classes = True
        row.update_record()

    ## Set default login destination for all users
    # Find all accounts that are no customer, employee or teacher and make them an employee
    query = ((db.auth_user.employee == False) |
             (db.auth_user.employee == None)) & \
            ((db.auth_user.teacher == False) |
             (db.auth_user.teacher == None)) & \
            ((db.auth_user.customer == False) |
             (db.auth_user.customer == None))
    db(query).update(employee = True)

    # Find all customers without a login destination
    query = (db.auth_user.customer == True) & \
            (db.auth_user.login_start == None)
    db(query).update(login_start='profile')

    # Find all teachers & employees without a login destination
    query = ((db.auth_user.teacher == True) |
             (db.auth_user.employee == True))
    db(query).update(login_start='backend')


    ## Migrate status tables to classes_otc

    # Subteachers
    rows = db().select(db.classes_subteachers.ALL)
    for row in rows:
        db.classes_otc.insert(
            classes_id       = row.classes_id,
            ClassDate        = row.ClassDate,
            auth_teacher_id  = row.auth_teacher_id,
            teacher_role     = row.teacher_role,
            auth_teacher_id2 = row.auth_teacher_id2,
            teacher_role2    = row.teacher_role2
        )

    # Classes Open
    rows = db().select(db.classes_open.ALL)
    for row in rows:
        check_row = db.classes_otc(classes_id = row.classes_id,
                                   ClassDate  = row.ClassDate)
        if check_row:
            check_row.Status = 'open'
        else:
            db.classes_otc.insert(
                classes_id = row.classes_id,
                ClassDate  = row.ClassDate,
                Status     = 'open'
            )


    # Classes Cancelled
    rows = db().select(db.classes_cancelled.ALL)
    for row in rows:
        check_row = db.classes_otc(classes_id = row.classes_id,
                                   ClassDate  = row.ClassDate)
        if check_row:
            check_row.Status = 'cancelled'
        else:
            db.classes_otc.insert(
                classes_id = row.classes_id,
                ClassDate  = row.ClassDate,
                Status     = 'cancelled'
            )

    ## Migrate invoice links to separate tables ( for one to many links ) and set amounts
    # Also update all invoice items to recalculate amounts
    rows = db(db.invoices_items.TotalPriceVAT == None).select(db.invoices_items.ALL)
    for row in rows:
        if row.VAT:
            row.TotalPriceVAT = row.TotalPrice + row.VAT
        else:
            row.TotalPriceVAT = row.TotalPrice
        row.update_record()


    rows = db().select(db.invoices.ALL)
    for row in rows:
        if row.customers_classcards_id:
            db.invoices_customers_classcards.insert(
                invoices_id = row.id,
                customers_classcards_id = row.customers_classcards_id
            )

        if row.classes_attendance_id:
            db.invoices_classes_attendance.insert(
                invoices_id = row.id,
                classes_attendance_id = row.classes_attendance_id
            )

        if row.workshops_products_customers_id:
            db.invoices_workshops_products_customers.insert(
                invoices_id = row.id,
                workshops_products_customers_id = row.workshops_products_customers_id
            )

        from os_invoices import Invoice

        invoice = Invoice(row.id)
        invoice.set_amounts()


def upgrade_to303():
    '''
        Upgrade operations for 3.02 --> 3.03
    '''
    ## correct birthdays
    query = (db.auth_user.date_of_birth != None)
    rows = db(query).select(db.auth_user.ALL)
    for row in rows:
        if row.date_of_birth.month == 2 and row.date_of_birth.day == 29:
            day = 28
        else:
            day = row.date_of_birth.day
        row.birthday = datetime.date(1900, row.date_of_birth.month, day)
        row.update_record()


def upgrade_to304():
    '''
        Upgrade operations for 3.03 --> 3.04
    '''
    ## Payment methods migrations
    # payment methods maintenance for 3.04
    db(db.payment_methods).update(SystemMethod=False)

    query = (db.payment_methods.id <= 3)
    db(query).update(SystemMethod=True)

    # insert payment method for Mollie
    db.payment_methods.insert(id=100,
                              Name=T('Mollie'),
                              Archived=False,
                              SystemMethod=True)

    ## Customer profile features
    # insert features row for customers profiles
    db.customers_profile_features.insert(
        id=1,
        Classes=True,
        Classcards=True,
        Subscriptions=True,
        Workshops=True,
        Orders=True,
        Invoices=True
    )

    ## Class card changes
    # Set unlimited boolean for class cards
    query = (db.school_classcards.Classes == 0) | \
            (db.school_classcards.Classes == '') | \
            (db.school_classcards.Classes == None)
    db(query).update(Unlimited=True)

    # set public for classcards
    query = (db.school_classcards.PublicCard == None)
    db(query).update(PublicCard = True)

    # Set new format validity
    query = (db.school_classcards.ValidityDays > 0)
    rows = db(query).select(db.school_classcards.ALL)
    for row in rows:
        row.Validity = row.ValidityDays
        row.ValidityUnit = 'days'
        row.update_record()

    query = (db.school_classcards.ValidityMonths > 0)
    rows = db(query).select(db.school_classcards.ALL)
    for row in rows:
        row.Validity = row.ValidityMonths
        row.ValidityUnit = 'months'
        row.update_record()

    ## School classtype changes
    # Set AllowAPI for school_classtypes to True to prevent any changes in schedule after update
    query = (db.school_classtypes.AllowAPI == None)
    db(query).update(AllowAPI=True)


def upgrade_to305():
    '''
        Upgrade operations 3.04 --> 3.05
    '''
    query = (db.workshops_products.PublicProduct == None)
    db(query).update(PublicProduct = True)


def upgrade_to306():
    '''
        Upgrade operations 3.05 --> 3.06
    '''
    templates = [
        ['email_template_invoice_created',
         '''<h3>A new invoice has been added to your account</h3>
<p>&nbsp;</p>
<p>{invoice_items}</p>
<p>&nbsp;</p>
<p>To view your invoices, please click <a href="{link_profile_invoices}">here</a>.</p>
<p>&nbsp;</p>'''],
        ['email_template_order_received',
         '''<h3>We have received your order with number #{order_id} on {order_date}</h3>
<p>&nbsp;</p>
<p>{order_items}</p>
<p>&nbsp;</p>
<p>To view your orders, please click <a href="{link_profile_orders}">here</a>.</p>'''],
        ['email_template_order_delivered',
         '''<h3>Your order&nbsp;with number #{order_id} has been delivered</h3>
<p>All items listed below have been added to your account</p>
<p>&nbsp;</p>
<p>{order_items}</p>
<p>&nbsp;</p>
<p>To view your orders, please click <a href="{link_profile_orders}">here</a>.</p>'''],
        ['email_template_payment_received',
         '''<h3>Payment received for invoice #{invoice_id}</h3>
<p>&nbsp;</p>
<p>On {payment_date} we have received a payment of {payment_amount} for invoice #{invoice_id}</p>
<p>&nbsp;</p>
<p>To view your invoices, please click <a href="{link_profile_invoices}">here</a>.</p>''']
    ]

    for template, template_content in templates:
        db.sys_properties.insert(
            Property=template,
            PropertyValue=template_content
        )


def upgrade_to307():
    '''
        Upgrade operations 3.06 --> 3.07
    '''
    # Set PublicSubscription field for all school_subscriptions to False
    query = (db.school_subscriptions.PublicSubscription == None)
    db(query).update(PublicSubscription = False)

    # Set new format validity for db.school_subscriptions
    query = (db.school_subscriptions.NRofClasses > 0)
    rows = db(query).select(db.school_subscriptions.ALL)
    for row in rows:
        row.Classes = row.NRofClasses
        row.SubscriptionUnit = 'week'
        row.update_record()

    query = (db.school_subscriptions.MonthlyClasses > 0)
    rows = db(query).select(db.school_subscriptions.ALL)
    for row in rows:
        row.Classes = row.MonthlyClasses
        row.SubscriptionUnit = 'month'
        row.update_record()

    # New email templates for password reset and verify email
    templates = [
        ['email_template_sys_reset_password',
         '''<h3>Reset password</h3>
<p>Please click on the <a href="%(link)s">link</a> to reset your password</p>'''],
        ['email_template_sys_verify_email',
         '''<h3>Verify email</h3>
<p>Welcome %(first_name)s!</p>
<p>Please click on the <a href="%(link)s">link</a> to verify your email</p>'''],
        ['email_template_payment_recurring_failed',
         '''<h3>Recurring payment failed</h3>
<p>&nbsp;</p>
<p>One or more recurring payments failed, please log in to your profile and pay any open invoices before the due date.</p>
<p>&nbsp;</p>
<p>To view your invoices, please click <a href="{link_profile_invoices}">here</a>.</p>'''],
        ['email_template_sys_footer',
         ''' '''],
    ]

    for template, template_content in templates:
        db.sys_properties.insert(
            Property=template,
            PropertyValue=template_content
        )

    # Set daily task
    from openstudio import OsScheduler
    oss = OsScheduler()
    oss.set_tasks()

    # insert features row for customers shop
    db.customers_shop_features.insert(
        id=1,
        Classcards=True,
        Subscriptions=True,
        Workshops=True
    )

    ## Migration for shifts_otc
    # Define tables
    define_shifts_sub()
    define_shifts_open()
    define_shifts_cancelled()

    # Shifts Sub
    rows = db().select(db.shifts_sub.ALL)
    for row in rows:
        db.shifts_otc.insert(
            shifts_id         = row.shifts_id,
            ShiftDate         = row.ShiftDate,
            auth_employee_id  = row.auth_employee_id,
            auth_employee_id2 = row.auth_employee_id2,
        )

    # Shifts Open
    rows = db().select(db.shifts_open.ALL)
    for row in rows:
        check_row = db.shifts_otc(shifts_id = row.shifts_id,
                                  ShiftDate = row.ShiftDate)
        if check_row:
            check_row.Status = 'open'
            check_row.update_record()
        else:
            db.shifts_otc.insert(
                shifts_id = row.shifts_id,
                ShiftDate = row.ShiftDate,
                Status    = 'open'
            )

    # Shifts Cancelled
    rows = db().select(db.shifts_cancelled.ALL)
    for row in rows:
        check_row = db.shifts_otc(shifts_id = row.shifts_id,
                                  ShiftDate = row.ShiftDate)
        if check_row:
            check_row.Status = 'cancelled'
            check_row.update_record()
        else:
            db.shifts_otc.insert(
                shifts_id = row.shifts_id,
                ShiftDate = row.ShiftDate,
                Status    = 'cancelled'
            )


def upgrade_to309():
    '''
        Upgrade operations 3.07 | 3.08 --> 3.09
    '''
    ## Set dates & times for all workshops based on activities
    from openstudio import Workshop
    rows = db().select(db.workshops.id)
    for row in rows:
        workshop = Workshop(row.id)
        workshop.update_dates_times()


def upgrade_to20170():
    '''
        Upgrade operations 3.09 --> 2017.0
    '''
    ## Update all invoice amounts to include paid and balance in amounts
    rows = db(db.invoices).select(db.invoices.id)
    for row in rows:
        invoice = Invoice(row.id)
        invoice.set_amounts()


def upgrade_to_20172():
    '''
        Upgrade operations 2017.0 & 2017.1 > 2017.2
    '''
    # This keeps the default behaviour the same for existing users
    db.sys_properties.insert(
        Property='online_payment_provider',
        PropertyValue='mollie',
    )


def upgrade_to_20173():
    '''
        Upgrade operations to 2017.3
    '''
    # clear menu cache to allow shop menu to appear
    cache_clear_menu_backend()

    # clear cache for schedule
    cache_clear_classschedule()


def upgrade_to_20174():
    '''
        Upgrade operations to 2017.4
    '''
    # migrate system company info to sys_organizations and set a default organization
    company_name = get_sys_property('company_name')
    company_address = get_sys_property('company_address')
    company_email = get_sys_property('company_email')
    company_phone = get_sys_property('company_phone')
    company_registration = get_sys_property('company_registration')
    company_terms_conditions_url = get_sys_property('company_terms_conditions_url')

    db.sys_organizations.insert(
        Name = company_name,
        Address = company_address,
        Email = company_email,
        Phone = company_phone,
        Registration = company_registration,
        TermsConditionsURL = company_terms_conditions_url
    )

    # clean old system settings of company info
    query = ((db.sys_properties.Property == 'company_name') |
             (db.sys_properties.Property == 'company_address') |
             (db.sys_properties.Property == 'company_email') |
             (db.sys_properties.Property == 'company_phone') |
             (db.sys_properties.Property == 'company_registration') |
             (db.sys_properties.Property == 'company_terms_conditions_url'))
    db(query).delete()


def upgrade_to_20175():
    '''
        Upgrade operations to 2017.5
    '''
    # Remove all "user_" groups from auth_group
    query = db.auth_group.role.like('user_%')
    db(query).delete()

    ##
    # set Booking status to attending for all historical data in classes_attendance
    ##
    query = (db.classes_attendance.BookingStatus == None)
    db(query).update(BookingStatus = 'attending')


def upgrade_to_20176():
    '''
        Upgrade operations to 2017.6
    '''
    # Set default value for ReconciliationClasses field in school_subscriptions
    query = (db.school_subscriptions.ReconciliationClasses == None)
    db(query).update(ReconciliationClasses = 0)


    # Clear menu cache to reload for all users
    cache_clear_menu_backend()


    ##
    # set Booking status to attending for all historical data in classes_attendance
    ##
    query = (db.classes_attendance.BookingStatus == None)
    db(query).update(BookingStatus = 'attending')


def upgrade_to_20177():
    '''
        Upgrade operations to 2017.7
    '''
    ##
    # Set default value for auth_user.trashed for all users
    ##
    query = (db.auth_user.trashed == None)
    db(query).update(trashed = False)

    ##
    # clear menu cache to show new links and icons
    ##
    cache_clear_menu_backend()

    ##
    # set Booking status to attending for all historical data in classes_attendance
    ##
    query = (db.classes_attendance.BookingStatus == None)
    db(query).update(BookingStatus='attending')


def upgrade_to_20181():
    """
        Upgrade operations to 2018.1
    """
    ##
    # clear cache
    ##
    cache.ram.clear(regex='.*')

    ##
    # Set sorting order for subscriptions
    ##
    query = (db.school_subscriptions.SortOrder == None)
    db(query).update(SortOrder = 0)

    ##
    # Create default subscription group, add all subscriptions to it and give the group full permissions for each class
    # to maintain similar behaviour compared to before the update
    ##

    # Subscriptions
    ssgID = db.school_subscriptions_groups.insert(
        Name = 'All subscriptions',
        Description = 'All subscriptions',
    )

    query = (db.school_subscriptions.Archived == False)
    rows = db(query).select(db.school_subscriptions.ALL)
    for row in rows:
        db.school_subscriptions_groups_subscriptions.insert(
            school_subscriptions_id = row.id,
            school_subscriptions_groups_id = ssgID
        )

    # Class cards
    scgID = db.school_classcards_groups.insert(
        Name = 'All class cards',
        Description = 'All class cards'
    )

    query = (db.school_classcards.Archived == False)
    rows = db(query).select(db.school_classcards.ALL)
    for row in rows:
        db.school_classcards_groups_classcards.insert(
            school_classcards_id = row.id,
            school_classcards_groups_id = scgID
        )

    # Link subscription & class card groups to classes and give permissions
    rows = db(db.classes).select(db.classes.ALL)
    for row in rows:
        db.classes_school_subscriptions_groups.insert(
            classes_id = row.id,
            school_subscriptions_groups_id = ssgID,
            Enroll = True,
            ShopBook = True,
            Attend = True
        )

        db.classes_school_classcards_groups.insert(
            classes_id = row.id,
            school_classcards_groups_id = scgID,
            Enroll = True,
            ShopBook = True,
            Attend = True
        )

    ##
    # set Booking status to attending for all historical data in classes_attendance
    ##
    query = (db.classes_attendance.BookingStatus == None)
    db(query).update(BookingStatus='attending')
    # TODO: repeat the 2 lines above for all coming upgrades
