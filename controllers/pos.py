# -*- coding: utf-8 -*-

from general_helpers import set_form_id_and_get_submit_button
from general_helpers import datestr_to_python

# auth.settings.on_failed_authorization = URL('return_json_permissions_error')


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

set_headers()

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
        'date_format': get_sys_property('DateFormat'),
        'date_mask': DATE_MASK
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
               auth.has_permission('create', 'classes_attendance'))
def customer_class_booking_create():
    """
    Check customer in to a class
    :return:
    """
    from openstudio.os_attendance_helper import AttendanceHelper

    # set_headers()
    type_id = request.vars['id']
    cuID = request.vars['cuID']
    clsID = request.vars['clsID']
    type = request.vars['Type']
    date = TODAY_LOCAL

    error = True
    message = T("Please make sure that the variables cuID, clsID and Type are included")
    if cuID and clsID and type:
        error = False
        message = ""

        ah = AttendanceHelper()

        if type == 'subscription':
            result = ah.attendance_sign_in_subscription(
                cuID,
                clsID,
                type_id,
                date,
                credits_hard_limit=True,
                booking_status='attending'
            )

        elif type == 'classcard':
            result = ah.attendance_sign_in_classcard(
                cuID,
                clsID,
                type_id,
                date,
                booking_status='attending'
            )

        # elif type == 'dropin':
        #     result = ah.attendance_sign_in_dropin(
        #         cuID,
        #         clsID,
        #         date,
        #         invoice=True,
        #         booking_status='attending'
        #     )
        #
        # elif type == 'trialclass':
        #     result = ah.attendance_sign_in_dropin(
        #         cuID,
        #         clsID,
        #         date,
        #         invoice=True,
        #         booking_status='attending'
        #     )

        if result['status'] == 'fail':
            error = True
            message = result['message']

        # elif type == 'trial':


    return dict(error=error,
                message=message)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('update', 'classes_attendance'))
def customer_class_booking_manage():
    """
    Manage booking for a class
    :return:
    """

    return dict(error=error,
                message=message)


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
        db.school_classcards.school_memberships_id,
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
            'school_memberships_id': row.school_memberships_id
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
               sc.school_memberships_id,
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
            AND (scp.Price > 0 AND scp.Price IS NOT NULL)
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
        db.school_subscriptions.school_memberships_id,
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
            'school_memberships_id': row.school_subscriptions.school_memberships_id
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
               sm.Price
        FROM school_memberships sm
        WHERE sm.Archived = 'F'
        ORDER BY sm.Name
    """.format(today=TODAY_LOCAL)

    fields = [
        db.school_memberships.id,
        db.school_memberships.Name,
        db.school_memberships.Description,
        db.school_memberships.Validity,
        db.school_memberships.ValidityUnit,
        db.school_memberships.Price
    ]

    rows = db.executesql(query, fields=fields)

    data = []
    for row in rows:
        data.append({
            'id': row.id,
            'Name': row.Name,
            'Description': row.Description or '',
            'Validity': row.Validity,
            'ValidityUnit': row.ValidityUnit,
            'Price': row.Price or 0
        })

    return dict(data=data)


def get_customers_thumbnail_url(row_data):
    if not row_data:
        return URL(
            'static', 'images/person.png',
            scheme=True,
            host=True
        )
    else:
        return URL(
            'default', 'download', args=[row_data],
            extension='',
            host=True,
            scheme=True
        )


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
        db.auth_user.barcode_id,
    )

    customers = {}

    for row in rows:
        date_of_birth = None
        if row.date_of_birth:
            date_of_birth = row.date_of_birth.strftime(DATE_FORMAT)

        customers[row.id] = {
            'id': row.id,
            'first_name': row.first_name,
            'last_name': row.last_name,
            'display_name': row.display_name,
            'search_name': row.display_name.lower() if row.display_name else "",
            'email': row.email,
            'gender': row.gender,
            'date_of_birth': date_of_birth,
            'address': row.address,
            'postcode': row.postcode,
            'city': row.city,
            'country': row.country,
            'phone': row.phone,
            'mobile': row.mobile,
            'emergency': row.emergency,
            'company': row.company,
            'thumbsmall': get_customers_thumbnail_url(row.thumbsmall),
            'thumblarge': get_customers_thumbnail_url(row.thumblarge),
            'barcode_id': row.barcode_id
        }

    return customers


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'customers_memberships'))
def get_customers_memberships_today():
    """
    List customer memberships
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
    )

    memberships = {}
    for i, row in enumerate(rows):
        repr_row = list(rows[i:i + 1].render())[0]

        try:
            memberships[row.auth_customer_id]
        except KeyError:
            memberships[row.auth_customer_id] = []

        memberships[row.auth_customer_id].append({
            'id': row.id,
            'auth_customer_id': row.auth_customer_id,
            'name': repr_row.school_memberships_id,
            'school_memberships_id': row.school_memberships_id,
            'start': repr_row.Startdate,
            'end': repr_row.Enddate,
        })

    return memberships


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'customers_memberships'))
def get_customers_memberships():
    """
    List customer memberships, from the last 400 days
    """
    set_headers()

    date_from = TODAY_LOCAL - datetime.timedelta(days=400)

    query = (db.customers_memberships.Startdate >= date_from)

    rows = db(query).select(
        db.customers_memberships.id,
        db.customers_memberships.auth_customer_id,
        db.customers_memberships.school_memberships_id,
        db.customers_memberships.Startdate,
        db.customers_memberships.Enddate,
    )

    memberships = {}
    for i, row in enumerate(rows):
        repr_row = list(rows[i:i + 1].render())[0]

        try:
            memberships[row.auth_customer_id]
        except KeyError:
            memberships[row.auth_customer_id] = []

        memberships[row.auth_customer_id].append({
            'id': row.id,
            'auth_customer_id': row.auth_customer_id,
            'name': repr_row.school_memberships_id,
            'school_memberships_id': row.school_memberships_id,
            'start': repr_row.Startdate,
            'end': repr_row.Enddate,
        })

    return memberships


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'customers_classcards'))
def get_customers_classcards():
    """
    List customer subscriptions, excluding cards that ended more then 
    7 months ago
    """
    set_headers()

    dont_show_after = TODAY_LOCAL - datetime.timedelta(days=217)
    query = (db.customers_classcards.Startdate <= TODAY_LOCAL) &\
            ((db.customers_classcards.Enddate >= dont_show_after) |\
             (db.customers_classcards.Enddate == None))

    left = [
        db.school_classcards.on(
            db.customers_classcards.school_classcards_id ==
            db.school_classcards.id
        )
    ]

    rows = db(query).select(
        db.customers_classcards.id,
        db.customers_classcards.auth_customer_id,
        db.customers_classcards.school_classcards_id,
        db.customers_classcards.Startdate,
        db.customers_classcards.Enddate,
        db.customers_classcards.ClassesTaken,
        db.school_classcards.Name,
        db.school_classcards.Classes,
        db.school_classcards.Unlimited,
        left=left
    )

    classcards = {}
    for i, row in enumerate(rows):
        repr_row = list(rows[i:i + 1].render())[0]

        try:
            classcards[row.customers_classcards.auth_customer_id]
        except KeyError:
            classcards[row.customers_classcards.auth_customer_id] = []

        classcards[row.customers_classcards.auth_customer_id].append({
            'id': row.customers_classcards.id,
            'auth_customer_id': row.customers_classcards.auth_customer_id,
            'name': row.school_classcards.Name,
            'start': repr_row.customers_classcards.Startdate,
            'end': repr_row.customers_classcards.Enddate,
            'classes_remaining': row.school_classcards.Classes - row.customers_classcards.ClassesTaken,
            'classes': row.school_classcards.Classes,
            'classes_display': repr_row.school_classcards.Classes,
            'unlimited': row.school_classcards.Unlimited
        })

    return classcards


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'customers_subscriptions'))
def get_customers_subscriptions():
    """
    List customer subscriptions, excluding subscriptions that ended more then 
    7 months ago
    """
    set_headers()

    dont_show_after = TODAY_LOCAL - datetime.timedelta(days=217)
    query = (db.customers_subscriptions.Startdate <= TODAY_LOCAL) &\
            ((db.customers_subscriptions.Enddate >= dont_show_after) |\
             (db.customers_subscriptions.Enddate == None))


    rows = db(query).select(
        db.customers_subscriptions.id,
        db.customers_subscriptions.auth_customer_id,
        db.customers_subscriptions.school_subscriptions_id,
        db.customers_subscriptions.Startdate,
        db.customers_subscriptions.Enddate,
    )

    subscriptions = {}
    for i, row in enumerate(rows):
        repr_row = list(rows[i:i + 1].render())[0]

        try:
            subscriptions[row.auth_customer_id]
        except KeyError:
            subscriptions[row.auth_customer_id] = []

        subscriptions[row.auth_customer_id].append({
            'id': row.id,
            'auth_customer_id': row.auth_customer_id,
            'name': repr_row.school_subscriptions_id,
            'start': row.Startdate,
            'end': row.Enddate,
        })

    return subscriptions


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('update', 'classes_attendance'))
def update_class_attendance():
    """

    :return:
    """
    from openstudio.os_class_attendance import ClassAttendance

    set_headers()

    print request.vars
    clattID = request.vars['id']
    status = request.vars['status']

    ca = ClassAttendance(clattID)
    ca.set_status(status)

    return dict(clattID=clattID, status=status)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('delete', 'classes_attendance'))
def delete_class_attendance():
    """

    :return:
    """
    from openstudio.os_class_attendance import ClassAttendance

    set_headers()

    print request.vars
    clattID = request.vars['id']

    query = (db.classes_attendance.id == clattID)
    db(query).delete()

    return dict(clattID=clattID, error=False)


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

    customer_data = ''
    error = False
    if result.errors:
        error = True

    if not error:
        row = db.auth_user(result['id'])

        dob = ''
        if row.date_of_birth:
            dob = row.date_of_birth.strftime(DATE_FORMAT)

        customer_data = {
            'id': row.id,
            'first_name': row.first_name,
            'last_name': row.last_name,
            'display_name': row.display_name,
            'search_name': row.display_name.lower(),
            'barcode_id': row.barcode_id,
            'email': row.email,
            'gender': row.gender,
            'date_of_birth': dob,
            'address': row.address,
            'postcode': row.postcode,
            'city': row.city,
            'country': row.country,
            'phone': row.phone,
            'mobile': row.mobile,
            'emergency': row.emergency,
            'company': row.company,
            'thumbsmall': get_customers_thumbnail_url(row.thumbsmall),
            'thumblarge': get_customers_thumbnail_url(row.thumblarge)
        }

    return dict(result=result,
                customer_data=customer_data,
                error=error)


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
        error = False
        if result.errors:
            error = True

        if not error:
            row = db.auth_user(cuID)

            dob = ''
            if row.date_of_birth:
                dob = row.date_of_birth.strftime(DATE_FORMAT)

            customer_data = {
                'id': row.id,
                'first_name': row.first_name,
                'last_name': row.last_name,
                'display_name': row.display_name,
                'search_name': row.display_name.lower(),
                'barcode_id': row.barcode_id,
                'email': row.email,
                'gender': row.gender,
                'date_of_birth': dob,
                'address': row.address,
                'postcode': row.postcode,
                'city': row.city,
                'country': row.country,
                'phone': row.phone,
                'mobile': row.mobile,
                'emergency': row.emergency,
                'company': row.company,
                'thumbsmall': get_customers_thumbnail_url(row.thumbsmall),
                'thumblarge': get_customers_thumbnail_url(row.thumblarge)
            }

        return dict(result=result,
                    error=error,
                    customer_data=customer_data,
                    id=cuID)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('update', 'auth_user'))
def update_customer_picture():
    """
    :return: dict containing data of new auth_user
    """
    import cStringIO

    set_headers()

    status = 'fail'
    data = {}

    cuID = request.vars['cuID']
    picture = request.vars['picture'].split(',')[1] # Remove description from b64 encoded image

    if cuID:
        # start decode into image
        import base64
        png_image = base64.b64decode(picture)
        # Create file stream
        stream = cStringIO.StringIO(png_image)

        # Update picture & generate new thumbnails
        query = (db.auth_user.id == cuID)
        result = db(query).update(picture=db.auth_user.picture.store(
            stream, # file stream
            'picture_%s.png' % cuID # filename
        ))

        # Generate return values
        row = db.auth_user(cuID)
        data = {
            'id': cuID,
            'thumbsmall': get_customers_thumbnail_url(row.thumbsmall),
            'thumblarge': get_customers_thumbnail_url(row.thumblarge)
        }

        status = 'success'


    return dict(result=status,
                data=data)


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
               auth.has_permission('read', 'payment_methods'))
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


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'tax_rates'))
def get_tax_rates():
    """

    :return: dict containing payment methods sorted by name
    """
    set_headers()

    query = (db.tax_rates.Archived == False)

    rows = db(query).select(
        db.tax_rates.ALL,
        orderby=~db.tax_rates.Name
    )

    return dict(data=rows.as_list())


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'shop_categories'))
def get_product_categories():
    """

    :return: dict containing payment methods sorted by name
    """
    set_headers()

    query = (db.shop_categories.Archived == False)

    rows = db(query).select(
        db.shop_categories.id,
        db.shop_categories.Name,
        orderby=db.shop_categories.Name
    )

    return dict(data=rows.as_dict())


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
    receipt_link = None
    receipt_items = None
    receipt_amounts = None
    receipt_pmID = None


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

    # Verify items
    if not items:
        error = True
        message = T("No items were submitted for processing")

    if not error and not pmID:
        error = True
        message = T("No payment method was selected")

    # Verify customer doesn't already have subscription or membership
    if cuID and not error:
        from openstudio.os_customer import Customer
        customer = Customer(cuID)
        for item in items:
            if item['item_type'] == 'subscription':
                subscription_ids = customer.get_school_subscriptions_ids_on_date(TODAY_LOCAL)
                print 'validating subscriptions'
                print subscription_ids
                if item['data']['id'] in subscription_ids:
                    error = True
                    message = T("This customer already has this subscription")
                        
            if item['item_type'] == 'membership':
                membership_ids = customer.get_school_memberships_ids_on_date(TODAY_LOCAL)
                print 'validating memberhsips'
                print membership_ids
                if item['data']['id'] in membership_ids:
                    error = True
                    message = T("This customer already has this membership")
    ## IMPORTANT: Get Item price & VAT info from server DB, not from Stuff submitted by Javascript.
    # JS can be manipulated.
    if not error:
        # IF customerID; add order; deliver
        invoice = None
        invoices_payment_id = None
        invoice_created = False
        if cuID:
            print 'create order'
            invoice = validate_cart_create_order(cuID, pmID, items)
            invoice_created = True


        # Always create payment receipt
        print 'create receipt'
        receipt = validate_cart_create_receipt(
            invoice_created,
            invoice,
            pmID,
            items,
        )

        receipt_link = URL(
            'finance', 'receipt',
            vars={'rID':receipt.receipts_id},
            extension='',
            scheme=True,
            host=True
        )

        receipt_items = receipt.get_receipt_items_rows()
        print receipt_items
        receipt_amounts = receipt.get_amounts()
        receipt_pmID = receipt.row.payment_methods_id


    return dict(
        error=error,
        message=message,
        receipt_link=receipt_link,
        receipt_items=receipt_items,
        receipt_amounts=receipt_amounts,
        receipt_payment_methods_id=receipt_pmID
    )


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
        elif item['item_type'] == 'class_dropin':
            order.order_item_add_class(
                item['data']['clsID'],
                TODAY_LOCAL,
                2 # Attendance Type 2 = drop-in
            )
        elif item['item_type'] == 'class_trial':
            order.order_item_add_class(
                item['data']['clsID'],
                TODAY_LOCAL,
                1 # Attendance Type 1 = trial
            )
        elif item['item_type'] == 'custom':
            order.order_item_add_custom(
                product_name = item['data']['product'],
                description = item['data']['description'],
                quantity = item['quantity'],
                price = item['data']['price'],
                tax_rates_id = item['data']['tax_rates_id']
            )

    # update order status
    order.set_status_awaiting_payment()

    # mail order to customer
#    order_received_mail_customer(coID)

    # check if this order needs to be paid or it's free and can be added to the customers' account straight away
    amounts = order.get_amounts()

    # Deliver order, add stuff to customer's account
    result = order.deliver(
        class_online_booking=False,
        class_booking_status='attending'
    )
    invoice = result['invoice']

    # Add payment
    ipID = invoice.payment_add(
        amounts.TotalPriceVAT,
        TODAY_LOCAL,
        payment_methods_id=pmID,
    )

    return invoice


def validate_cart_create_receipt(
        invoice_created,
        invoice,
        pmID,
        items
    ):
    """
    :param pmID: db.payment_methods.id
    :param invoices_payment_id: db.invoices_payments.id
    :param items: PoS items
    :return: int - receipt_id
    """
    from openstudio.os_receipt import Receipt
    from openstudio.os_shop_products_variant import ShopProductsVariant

    rID = db.receipts.insert(
        payment_methods_id = pmID,
    )

    receipt = Receipt(rID)

    # Add items
    for item in items:
        if item['item_type'] == 'product':
            pvID = item['data']['id']
            quantity = item['quantity']
            riID = receipt.item_add_product_variant(pvID, quantity)

            variant = ShopProductsVariant(pvID)
            product = db.shop_products(variant.row.shop_products_id)
            ssaID = db.shop_sales.insert(
                ProductName=product.Name,
                VariantName=variant.row.Name,
                ArticleCode=variant.row.ArticleCode,
                Barcode=variant.row.Barcode,
                Quantity=quantity
            )

            db.shop_sales_products_variants.insert(
                shop_sales_id = ssaID,
                shop_products_variants_id = pvID
            )

            db.receipts_items_shop_sales.insert(
                shop_sales_id = ssaID,
                receipts_items_id = riID
            )

            # Update stock
            variant.stock_reduce(quantity)
        elif item['item_type'] == 'custom' and not invoice_created:
            """
                Only add custom items to receipt here if no if no invoice is created
                otherwise, get data from invoice
            """
            data = item['data']

            riID = receipt.item_add_custom(
                product_name = data['product'],
                description = data['description'],
                quantity = item['quantity'],
                price = data['price'],
                tax_rates_id = data['tax_rates_id']
            )


    if invoice_created:
        invoice_items = invoice.get_invoice_items_rows()
        for item in invoice_items:
            receipt.item_add_from_invoice_item(item)

    return receipt


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'accounting_expenses'))
def get_expenses():
    """
    :return: List of expenses
    """
    set_headers()

    query = (db.accounting_expenses.BookingDate == TODAY_LOCAL)

    rows = db(query).select(
        db.accounting_expenses.id,
        db.accounting_expenses.BookingDate,
        db.accounting_expenses.Amount,
        db.accounting_expenses.tax_rates_id,
        db.accounting_expenses.YourReference,
        db.accounting_expenses.Description,
        db.accounting_expenses.Note,
    )

    expenses = {}

    for row in rows:
        expenses[row.id] = {
            'id': row.id,
            'booking_date': row.BookingDate,
            'amount': row.Amount,
            'tax_rates_id': row.tax_rates_id,
            'your_reference': row.YourReference,
            'description': row.Description,
            'note': row.Note
        }

    return expenses

@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'accounting_expenses'))
def get_cash_counts():
    """
    :return: List of expenses
    """
    set_headers()

    opening_row = db.accounting_cashbooks_cash_count(
        CountDate = TODAY_LOCAL,
        CountType = 'opening'
    )

    closing_row = db.accounting_cashbooks_cash_count(
        CountDate = TODAY_LOCAL,
        CountType = 'closing'
    )


    cash_counts = {
        'opening': {
            'Amount': opening_row.Amount if opening_row else 0
        },
        'closing': {
            'Amount': closing_row.Amount if closing_row else 0
        }
    }


    return cash_counts


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('update', 'accounting_cashbooks_cash_count'))
def set_cash_count():
    set_headers()

    # Clean up input of amount
    if 'amount' in request.vars:
        if ',' in request.vars['amount']:
            request.vars['amount'] = request.vars['amount'].replace(',', '.')

    row = db.accounting_cashbooks_cash_count(
        CountDate = TODAY_LOCAL,
        CountType = request.vars['type']
    )

    if not row:
        result = db.accounting_cashbooks_cash_count.validate_and_insert(
            CountDate = TODAY_LOCAL,
            CountType = request.vars['type'],
            Amount = request.vars['amount'],
        )
    else:
        query = (db.accounting_cashbooks_cash_count.id == row.id)
        result = db(query).validate_and_update(
            id = row.id,
            CountDate = TODAY_LOCAL,
            CountType = request.vars['type'],
            Amount = request.vars['amount']
        )

    error = False
    if result.errors:
        error = True


    return dict(result=result,
                cash_counts_data=get_cash_counts(),
                error=error)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('create', 'accounting_expenses'))
def create_expense():
    """
    :return: dict containing data of new auth_user
    """
    set_headers()

    print request.vars

    # Clean up input of amount
    if 'Amount' in request.vars:
        if ',' in request.vars['Amount']:
            request.vars['Amount'] = request.vars['Amount'].replace(',', '.')


    result = db.accounting_expenses.validate_and_insert(**request.vars)
    print result

    expense_data = ''
    error = False
    if result.errors:
        error = True

    if not error:
        row = db.accounting_expenses(result['id'])

        expense_data = row.as_dict()
        # expense_data = {
        #     'id': row.id,
        #     'first_name': row.first_name,
        #     'last_name': row.last_name,
        #     'display_name': row.display_name,
        #     'search_name': row.display_name.lower(),
        #     'barcode_id': row.barcode_id,
        #     'email': row.email,
        #     'gender': row.gender,
        #     'date_of_birth': dob,
        #     'address': row.address,
        #     'postcode': row.postcode,
        #     'city': row.city,
        #     'country': row.country,
        #     'phone': row.phone,
        #     'mobile': row.mobile,
        #     'emergency': row.emergency,
        #     'company': row.company,
        #     'thumbsmall': get_customers_thumbnail_url(row.thumbsmall),
        #     'thumblarge': get_customers_thumbnail_url(row.thumblarge)
        # }

    return dict(result=result,
                expense_data=expense_data,
                error=error)
