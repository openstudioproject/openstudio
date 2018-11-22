# -*- coding: utf-8 -*-

from general_helpers import set_form_id_and_get_submit_button
from general_helpers import datestr_to_python

# auth.settings.on_failed_authorization = URL('return_json_permissions_error')


# print request.env
#
# if request.env.http_origin:
#     response.headers['Access-Control-Allow-Origin'] = request.env.http_origin;
#     response.headers['Access-Control-Allow-Methods'] = "POST,GET,OPTIONS";
#     response.headers['Access-Control-Allow-Credentials'] = "true";
#     response.headers['Access-Control-Allow-Headers'] = "Accept, Authorization, Content-Type, If-Match, If-Modified-Since, If-None-Match, If-Unmodified-Since, Accept-Encoding";
#     response.headers['Access-Control-Allow-Content-Type'] = 'application/json'
#     # response.headers['Access-Control-Allow-Origin'] = "*"

@auth.requires_login()
def index():
    # print auth.user

    return dict()


def set_headers(var=None):
    if request.env.HTTP_ORIGIN == 'http://dev.openstudioproject.com:8080':
        response.headers["Access-Control-Allow-Origin"] = request.env.HTTP_ORIGIN

    # response.headers["Access-Control-Allow-Credentials"] = "true"
    # response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, POST, DELETE, OPTIONS"
    # response.headers["Access-Control-Allow-Headers"] = "*"
    # response.headers["Access-Control-Allow-Origin"] = '*'
    response.headers['Access-Control-Max-Age'] = 86400
    # response.headers['Access-Control-Allow-Headers'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept'
    response.headers['Access-Control-Allow-Methods'] = '*'
    response.headers['Access-Control-Allow-Content-Type'] = 'application/json'
    response.headers['Access-Control-Allow-Credentials'] = 'true'



def return_json_login_error(var=None):
    print 'return_json_login_error'
    print 'cookies:'
    print request.cookies

    set_headers()

    return dict(
        error=401,
        error_message=T("User is not logged in and needs to provide credentials"),
        location=URL('default', 'user',
                     args='login',
                     vars={'_next':"/pos"},
                     scheme=True,
                     host=True,
                     extension='')
        # location='http://dev.openstudioproject.com:8000/user/login?_next=/pos'
    )


def return_json_permissions_error():
    set_headers()
    print 'return_json_permissions_error'
    print 'cookies:'
    print request.cookies

    try:
        # Dev
        location = request.env.HTTP_ORIGIN + '/#/permissions_error'
    except TypeError:
        # Live
        location = request.env.wsgi_url_scheme + '://' + request.env.http_host + '/pos#/permissions_error'
        print location

    return dict(
        error=403,
        error_message=T("You don't have the permissions required to perform this action"),
        location=location

    )


def is_authorized(permission):
    """
    :param permission: in form auth.has_permission('read', 'permission')
    :return: None
    """
    return (auth.has_membership(group_id="Admins") or
            permission)


@auth.requires_login(otherwise=return_json_login_error)
def get_logged_in():
    set_headers()

    print 'cookies:'
    print request.cookies

    return auth.is_logged_in()


@auth.requires_login(otherwise=return_json_login_error)
def get_user():
    set_headers()

    # if not is_authorized(auth.has_permission('read', 'auth_user')):
    #     return return_json_permissions_error()
    # Permissions error

    # get group membership
    membership = db.auth_membership(user_id=auth.user.id)
    group_id = membership.group_id

    # get group permissions
    query = (db.auth_permission.group_id == group_id) & \
            (db.auth_permission.record_id == 0)
    rows = db(query).select(db.auth_permission.name,
                            db.auth_permission.table_name)
    permissions = {}
    for row in rows:
        if row.table_name in permissions:
            permissions[row.table_name].append(row.name)
        else:
            permissions[row.table_name] = [row.name]


    return dict(profile=auth.user,
                permissions=permissions)

@auth.requires_login(otherwise=return_json_login_error)
def get_settings():
    """
    Pos Relevant settings
    """
    set_headers()

    settings = {
        'currency_symbol': CURRSYM,
        'currency': get_sys_property('Currency'),
        'customers_barcodes': get_sys_property('pos_customers_barcodes')
    }

    return dict(data = settings)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'classes'))
def get_classes():
    """
    List upcoming classes for today
    :return:
    """
    date_received = request.vars['date']
    date = datestr_to_python("%Y-%m-%d", date_received)

    set_headers()

    from openstudio.os_class_schedule import ClassSchedule


    cs = ClassSchedule(
        date,
        # filter_starttime_from=time_from
    )

    return dict(classes=cs.get_day_list())


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'classes_attendance'))
def get_class_attendance():
    """
    List attendance for a class
    :return:
    """
    from openstudio.os_attendance_helper import AttendanceHelper

    clsID = request.vars['clsID']
    date_received = request.vars['date']
    date = datestr_to_python("%Y-%m-%d", date_received)

    set_headers()

    ah = AttendanceHelper()
    attendance = ah.get_attendance_rows(clsID, date).as_list()

    return dict(attendance=attendance)


#TODO: Change for right permission
@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'classes_attendance'))
def get_class_revenue():
    """
    :return:
    """
    from openstudio.os_reports import Reports

    set_headers()

    clsID = request.vars['clsID']
    date_received = request.vars['date']
    date = datestr_to_python("%Y-%m-%d", date_received)

    reports = Reports()

    return dict(revenue=reports.get_class_revenue_summary(clsID, date))


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('update', 'teachers_payment_attendance'))
def get_class_teacher_payment():
    """

    :return:
    """
    from openstudio.os_class import Class

    set_headers()

    clsID = request.vars['clsID']
    date_received = request.vars['date']
    date = datestr_to_python("%Y-%m-%d", date_received)

    cls = Class(clsID, date)

    return dict(payment = cls.get_teacher_payment())


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('update', 'teachers_payment_attendance'))
def verify_teacher_payment():
    """
    Set teacher payment attendance
    """
    from openstudio.os_teachers_payment_class import TeachersPaymentClass

    set_headers()

    tpcID = request.vars['tpcID']

    tpc = TeachersPaymentClass(tpcID)
    result = tpc.verify()

    if result:
        status = 'success'
    else:
        status = 'fail'

    return dict(result=status)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('create', 'classes_attendance'))
def get_class_booking_options():
    """
    List booking options for a class for a given customer
    :return:
    """
    from openstudio.os_attendance_helper import AttendanceHelper
    from openstudio.os_customer import Customer

    clsID = request.vars['clsID']
    cuID = request.vars['cuID']

    set_headers()

    customer = Customer(cuID)
    complementary_permission = (auth.has_membership(group_id='Admins') or
                                auth.has_permission('complementary', 'classes_attendance'))

    ah = AttendanceHelper()
    options = ah.get_customer_class_booking_options(
        clsID,
        TODAY_LOCAL,
        customer,
        trial=True,
        complementary=complementary_permission,
        list_type='attendance'
    )

    return dict(options = options)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'school_classcards'))
def get_school_classcards():
    """
    List of school not archived classcards
    Sorted by name
    :return:
    """
    def get_validity(row):
        """
            takes a db.school_classcards() row as argument
        """
        validity = unicode(row.Validity) + ' '

        validity_in = represent_validity_units(row.ValidityUnit, row)
        if row.Validity == 1:  # Cut the last 's"
            validity_in = validity_in[:-1]

        return validity + validity_in

    set_headers()

    #TODO order by Trial card and then name
    query = (db.school_classcards.Archived == False)
    rows = db(query).select(
        db.school_classcards.id,
        db.school_classcards.Name,
        db.school_classcards.Description,
        db.school_classcards.Price,
        db.school_classcards.Validity,
        db.school_classcards.ValidityUnit,
        db.school_classcards.Classes,
        db.school_classcards.Unlimited,
        db.school_classcards.Trialcard,
        db.school_classcards.MembershipRequired,
        orderby=db.school_classcards.Name
    )

    data_rows = []
    for row in rows:
        item = {
            'id': row.id,
            'Name': row.Name,
            'Description': row.Description,
            'Price': row.Price,
            'Validity': row.Validity,
            'ValidityUnit': row.ValidityUnit,
            'ValidityDisplay': get_validity(row),
            'Classes': row.Classes,
            'Unlimited': row.Unlimited,
            'Trialcard': row.Trialcard,
            'MembershipRequired': row.MembershipRequired
        }

        data_rows.append(item)

    return dict(data=data_rows)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'school_subscriptions'))
def get_school_subscriptions():
    """
    List of not archived school classcards
    Sorted by Name
    """
    set_headers()

    query = """
        SELECT sc.id,
               sc.Name,
               sc.SortOrder,
               sc.Description,
               sc.Classes,
               sc.SubscriptionUnit,
               sc.Unlimited,
               sc.RegistrationFee,
               sc.MembershipRequired,
               scp.Price
        FROM school_subscriptions sc
        LEFT JOIN
        ( SELECT school_subscriptions_id, 
                 Price
          FROM school_subscriptions_price
          WHERE Startdate <= '{today}' AND
                (Enddate >= '{today}' OR Enddate IS NULL) 
        ) scp ON sc.id = scp.school_subscriptions_id
        WHERE sc.Archived = 'F'
        ORDER BY sc.Name
    """.format(today=TODAY_LOCAL)

    fields = [
        db.school_subscriptions.id,
        db.school_subscriptions.Name,
        db.school_subscriptions.SortOrder,
        db.school_subscriptions.Description,
        db.school_subscriptions.Classes,
        db.school_subscriptions.SubscriptionUnit,
        db.school_subscriptions.Unlimited,
        db.school_subscriptions.RegistrationFee,
        db.school_subscriptions.MembershipRequired,
        db.school_subscriptions_price.Price,
    ]

    rows = db.executesql(query, fields=fields)

    data = []
    for row in rows:
        data.append({
            'id': row.school_subscriptions.id,
            'Name': row.school_subscriptions.Name,
            'SortOrder': row.school_subscriptions.SortOrder,
            'Description': row.school_subscriptions.Description or '',
            'Classes': row.school_subscriptions.Classes,
            'SubscriptionUnit': row.school_subscriptions.SubscriptionUnit,
            'Unlimited': row.school_subscriptions.Unlimited,
            'Price': row.school_subscriptions_price.Price or 0,
            'RegistrationFee': row.school_subscriptions.RegistrationFee or 0,
            'MembershipRequired': row.school_subscriptions.MembershipRequired,
        })

    return dict(data=data)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'school_memberships'))
def get_school_memberships():
    """
    List of not archived school classcards
    Sorted by Name
    """
    set_headers()

    query = """
        SELECT sm.id,
               sm.Name,
               sm.Description,
               sm.Validity,
               sm.ValidityUnit,
               smp.Price
        FROM school_memberships sm
        LEFT JOIN
        ( SELECT school_memberships_id, 
                 Price
          FROM school_memberships_price
          WHERE Startdate <= '{today}' AND
                (Enddate >= '{today}' OR Enddate IS NULL) 
        ) smp ON sm.id = smp.school_memberships_id
        WHERE sm.Archived = 'F'
        ORDER BY sm.Name
    """.format(today=TODAY_LOCAL)

    fields = [
        db.school_memberships.id,
        db.school_memberships.Name,
        db.school_memberships.Description,
        db.school_memberships.Validity,
        db.school_memberships.ValidityUnit,
        db.school_memberships_price.Price
    ]

    rows = db.executesql(query, fields=fields)

    data = []
    for row in rows:
        data.append({
            'id': row.school_memberships.id,
            'Name': row.school_memberships.Name,
            'Description': row.school_memberships.Description or '',
            'Validity': row.school_memberships.Validity,
            'ValidityUnit': row.school_memberships.ValidityUnit,
            'Price': row.school_memberships_price.Price or 0
        })

    return dict(data=data)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'auth_user'))
def get_customers():
    """
    List not trashed customers
    """
    set_headers()

    query = (db.auth_user.customer == True) & \
            (db.auth_user.trashed == False)

    rows = db(query).select(
        db.auth_user.id,
        db.auth_user.first_name,
        db.auth_user.last_name,
        db.auth_user.display_name,
        db.auth_user.email,
        db.auth_user.gender,
        db.auth_user.date_of_birth,
        db.auth_user.address,
        db.auth_user.postcode,
        db.auth_user.city,
        db.auth_user.country,
        db.auth_user.phone,
        db.auth_user.mobile,
        db.auth_user.emergency,
        db.auth_user.company,
        db.auth_user.thumbsmall,
        db.auth_user.thumblarge,
    )

    customers = {}

    for row in rows:
        customers[row.id] = {
            'id': row.id,
            'first_name': row.first_name,
            'last_name': row.last_name,
            'display_name': row.display_name,
            'search_name': row.display_name.lower(),
            'email': row.email,
            'gender': row.gender,
            'date_of_birth': row.date_of_birth,
            'address': row.address,
            'postcode': row.postcode,
            'city': row.city,
            'country': row.country,
            'phone': row.phone,
            'mobile': row.mobile,
            'emergency': row.emergency,
            'company': row.company,
            'thumbsmall': URL(
                'default', 'download', args=[row.thumbsmall],
                extension='',
                host=True,
                scheme=True
            ),
            'thumblarge': URL(
                'default', 'download', args=[row.thumblarge],
                extension='',
                host=True,
                scheme=True
            ),
        }

    return customers


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'customers_memberships'))
def get_customers_memberships():
    """
    List not trashed customers
    """
    set_headers()

    query = (db.customers_memberships.Startdate <= TODAY_LOCAL) & \
            ((db.customers_memberships.Enddate >= TODAY_LOCAL) |\
             (db.customers_memberships.Enddate == None))

    rows = db(query).select(
        db.customers_memberships.id,
        db.customers_memberships.auth_customer_id,
        db.customers_memberships.school_memberships_id,
        db.customers_memberships.Startdate,
        db.customers_memberships.Enddate,
        db.customers_memberships.DateID
    )

    memberships = {}
    for i, row in enumerate(rows):
        repr_row = list(rows[i:i + 1].render())[0]

        memberships[row.id] = {
            'auth_customer_id': row.auth_customer_id,
            'name': repr_row.school_memberships_id,
            'start': row.Startdate,
            'end': row.Enddate,
            'date_id': row.DateID
        }

    return memberships


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('create', 'auth_user'))
def create_customer():
    """
    :return: dict containing data of new auth_user
    """
    set_headers()


    db.auth_user.password.requires = None
    print request.vars

    result = db.auth_user.validate_and_insert(**request.vars)
    print result

    return dict(result=result)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('update', 'auth_user'))
def update_customer():
    """
    :return: dict containing data of new auth_user
    """
    set_headers()

    db.auth_user.password.requires = None
    print request.vars

    cuID = request.vars.pop('id', None)

    print cuID
    print request.vars

    print db.auth_user.email.requires

    # The default validator returns an error in this case
    # It says an account already exists for this email
    # when trying to update the users' own/current email.
    # This validator works around that.
    ##
    query = (db.auth_user.id != cuID)

    db.auth_user.email.requires = [
        IS_EMAIL(),
        IS_LOWER(),
        IS_NOT_IN_DB(
            db(query),
            'auth_user.email',
            error_message=T("This email already has an account")
        )
    ]

    if cuID:
        query = (db.auth_user.id == cuID)


        result = db(query).validate_and_update(**request.vars)
        print result

        return dict(result=result,
                    id=cuID)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'shop_products'))
def get_products():
    """

    :return: dict containing products sorted by category
    """
    from openstudio.os_shop_products_variants import ShopProductsVariants
    # from openstudio.os_shop_category import ShopCategory

    import pprint

    pp = pprint.PrettyPrinter(depth=6)
    set_headers()


    spv = ShopProductsVariants()

    data = spv.list_pos()
    # pp.pprint(data)

    return dict(data=data)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'shop_products'))
def get_payment_methods():
    """

    :return: dict containing payment methods sorted by name
    """
    set_headers()

    not_pos_methods = [2, 3, 100]
    query = (db.payment_methods.Archived == False) & \
            ~(db.payment_methods.id.belongs(not_pos_methods))

    rows = db(query).select(
        db.payment_methods.ALL,
        orderby=~db.payment_methods.SystemMethod|db.payment_methods.Name
    )

    return dict(data=rows.as_list())


#TODO make read PoS permission
# @auth.requires(auth.has_membership(group_id='Admins'))
               # auth.has_permission('read', 'shop_products'))
def validate_cart():
    """
    Process shopping cart
    :return:
    """
    # print request.env

    set_headers()

    error = False
    message = ''


    #If no customerID; just make receipt and update stock
    #if customerID; Make order, deliver order, add payment to invoice created by deliver order

    items = request.vars['items']
    pmID = request.vars['payment_methodID']
    cuID = request.vars['customerID']

    print 'customerID'
    print type(cuID)
    print cuID

    print 'validate_cart_items:'
    print items

    if not items:
        error = True
        message = T("No items were submitted for processing")



    ## IMPORTANT: Get Item price & VAT info from server DB, not from Stuff submitted by Javascript.
    # JS can be manipulated.
    if not error:
        # IF customerID; add order; deliver
        invoices_payment_id = None
        if cuID:
            print 'create order'
            invoices_payment_id = validate_cart_create_order(cuID, pmID, items)


        # Always create payment receipt
        print 'create receipt'
        validate_cart_create_receipt(
            pmID,
            invoices_payment_id,
            items,
        )




    return dict(error=error, message=message)


def validate_cart_create_order(cuID, pmID, items):
    """
    :param cuID: db.auth_user.id
    :param items:
    :return:
    """
    from openstudio.os_order import Order

    coID = db.customers_orders.insert(
        auth_customer_id = cuID,
        Status = 'order_received',
        Origin = 'pos',
    )
    order = Order(coID)

    # Add items
    for item in items:
        if item['item_type'] == 'product':
            order.order_item_add_product_variant(item['data']['id'], item['quantity'])
        elif item['item_type'] == 'classcard':
             order.order_item_add_classcard(item['data']['id'])
        elif item['item_type'] == 'subscription':
            order.order_item_add_subscription(
                item['data']['id'],
                TODAY_LOCAL
            )
        elif item['item_type'] == 'membership':
            order.order_item_add_membership(
                item['data']['id'],
                TODAY_LOCAL
            )

    # update order status
    order.set_status_awaiting_payment()

    # mail order to customer
#    order_received_mail_customer(coID)

    # check if this order needs to be paid or it's free and can be added to the customers' account straight away
    amounts = order.get_amounts()

    # Deliver order, add stuff to customer's account
    result = order.deliver()
    invoice = result['invoice']

    # Add payment
    ipID = invoice.payment_add(
        amounts.TotalPriceVAT,
        TODAY_LOCAL,
        payment_methods_id=pmID,
    )


def validate_cart_create_receipt(pmID, invoices_payment_id, items):
    """
    :param pmID: db.payment_methods.id
    :param invoices_payment_id: db.invoices_payments.id
    :param items: PoS items
    :return: int - receipt_id
    """
    from openstudio.os_receipt import Receipt

    rID = db.receipts.insert(
        payment_methods_id = pmID,
    )

    receipt = Receipt(rID)

    # Add items
    print 'create_receipt_items:'
    print items
    for item in items:
        if item['item_type'] == 'product':
            receipt.item_add_product_variant(item['data']['id'], item['quantity'])
        elif item['item_type'] == 'classcard':
             receipt.item_add_classcard(item['data']['id'])
        # elif item['item_type'] == 'subscription':
        #     order.order_item_add_subscription(
        #         item['data']['id'],
        #         TODAY_LOCAL
        #     )
        # elif item['item_type'] == 'membership':
        #     order.order_item_add_membership(
        #         item['data']['id'],
        #         TODAY_LOCAL
        #     )



