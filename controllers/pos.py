# -*- coding: utf-8 -*-

from general_helpers import set_form_id_and_get_submit_button
from general_helpers import datestr_to_python

# auth.settings.on_failed_authorization = URL('return_json_permissions_error')


def set_headers(var=None):
    # print request.env.HTTP_ORIGIN

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


def check_permission(permission="read", attribute="pos"):
    permission = (auth.has_membership(group_id='Admins') or
                  auth.has_permission('read', 'pos'))

    message = ""
    if not permission:
        message = T("Permission denied")

    return dict(permission=permission,
                message=message)


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
    print('return_json_login_error')
    print('cookies:')
    print(request.cookies)

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
    print('return_json_permissions_error')
    print('cookies:')
    print(request.cookies)

    try:
        # Dev
        location = request.env.HTTP_ORIGIN + '/#/permissions_error'
    except TypeError:
        # Live
        location = request.env.wsgi_url_scheme + '://' + request.env.http_host + '/pos#/permissions_error'
        print(location)

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

    print('cookies:')
    print(request.cookies)

    return auth.is_logged_in()


@auth.requires_login(otherwise=return_json_login_error)
def get_user():
    set_headers()

    # if not is_authorized(auth.has_permission('read', 'auth_user')):
    #     return return_json_permissions_error()
    # Permissions error

    # get group membership
    group_id = None
    membership = db.auth_membership(user_id=auth.user.id)
    if membership:
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


@auth.requires_login(otherwise=return_json_login_error)
def get_classes():
    """
    List upcoming classes for today
    :return:
    """
    set_headers()
    permission_result = check_permission()
    if not permission_result['permission']:
        return return_json_permissions_error()

    date_received = request.vars['date']
    date = datestr_to_python("%Y-%m-%d", date_received)


    from openstudio.os_class_schedule import ClassSchedule
    cs = ClassSchedule(
        date,
        # filter_starttime_from=time_from
    )

    return dict(classes=cs.get_day_list())


@auth.requires_login(otherwise=return_json_login_error)
def get_class_attendance():
    """
    List attendance for a class
    :return:
    """
    set_headers()
    permission_result = check_permission()
    if not permission_result['permission']:
        return return_json_permissions_error()


    from openstudio.os_attendance_helper import AttendanceHelper

    clsID = request.vars['clsID']
    date_received = request.vars['date']
    date = datestr_to_python("%Y-%m-%d", date_received)

    ah = AttendanceHelper()
    attendance = ah.get_attendance_rows(clsID, date).as_list()

    return dict(attendance=attendance)


@auth.requires_login(otherwise=return_json_login_error)
def get_class_revenue():
    """
    :return:
    """
    set_headers()
    permission_result = check_permission()
    if not permission_result['permission']:
        return return_json_permissions_error()

    from openstudio.os_reports import Reports

    clsID = request.vars['clsID']
    date_received = request.vars['date']
    date = datestr_to_python("%Y-%m-%d", date_received)

    reports = Reports()

    return dict(revenue=reports.get_class_revenue_summary(clsID, date))


@auth.requires_login(otherwise=return_json_login_error)
def get_class_teacher_payment():
    """
    :return:
    """
    set_headers()
    permission_result = check_permission()
    if not permission_result['permission']:
        return return_json_permissions_error()

    from openstudio.os_class import Class

    clsID = request.vars['clsID']
    date_received = request.vars['date']
    date = datestr_to_python("%Y-%m-%d", date_received)

    cls = Class(clsID, date)
    payment = cls.get_teacher_payment()
    print(payment)

    return dict(payment = payment)


@auth.requires_login(otherwise=return_json_login_error)
def verify_teacher_payment():
    """
    Set teacher payment attendance
    """
    set_headers()
    permission_result = check_permission()
    if not permission_result['permission']:
        return return_json_permissions_error()

    from openstudio.os_teachers_payment_class import TeachersPaymentClass

    tpcID = request.vars['tpcID']

    tpc = TeachersPaymentClass(tpcID)
    result = tpc.verify()

    if result:
        status = 'success'
    else:
        status = 'fail'

    return dict(result=status)


@auth.requires_login(otherwise=return_json_login_error)
def get_class_booking_options():
    """
    List booking options for a class for a given customer
    :return:
    """
    set_headers()
    permission_result = check_permission()
    if not permission_result['permission']:
        return return_json_permissions_error()

    from openstudio.os_attendance_helper import AttendanceHelper
    from openstudio.os_customer import Customer

    clsID = request.vars['clsID']
    cuID = request.vars['cuID']

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
        list_type='pos'
    )

    return dict(options = options)


@auth.requires_login(otherwise=return_json_login_error)
def customer_class_booking_create():
    """
    Check customer in to a class, drop-in and trial are handled through
    an order.
    :return:
    """
    set_headers()
    permission_result = check_permission()
    if not permission_result['permission']:
        return return_json_permissions_error()

    from openstudio.os_attendance_helper import AttendanceHelper

    # set_headers()
    type_id = request.vars['id']
    cuID = request.vars['cuID']
    clsID = request.vars['clsID']
    type = request.vars['Type']
    date = TODAY_LOCAL

    ah = AttendanceHelper()
    error = True
    message = T("Please make sure that the variables cuID, clsID and Type are included")
    if cuID and clsID and type:
        error = False
        message = ""

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

        elif type == "complementary":
            error = False
            result = ah.attendance_sign_in_complementary(
                cuID,
                clsID,
                date,
                booking_status='attending'
            )

        elif type == "reconcile_later":
            print("checking in")
            error = False
            result = ah.attendance_sign_in_reconcile_later(
                cuID,
                clsID,
                date,
                booking_status='attending'
            )

            print(result)


        if result['status'] == 'fail':
            error = True
            message = result['message']


    return dict(error=error,
                message=message)


@auth.requires_login(otherwise=return_json_login_error)
def customer_class_booking_manage():
    """
    Manage booking for a class
    :return:
    """
    set_headers()
    permission_result = check_permission()
    if not permission_result['permission']:
        return return_json_permissions_error()

    return dict(error=error,
                message=message)


@auth.requires_login(otherwise=return_json_login_error)
def get_school_classcards():
    """
    List of school not archived classcards
    Sorted by name
    :return:
    """
    set_headers()
    permission_result = check_permission()
    if not permission_result['permission']:
        return return_json_permissions_error()

    def get_validity(row):
        """
            takes a db.school_classcards() row as argument
        """
        validity = str(row.Validity) + ' '

        validity_in = represent_validity_units(row.ValidityUnit, row)
        if row.Validity == 1:  # Cut the last 's"
            validity_in = validity_in[:-1]

        return validity + validity_in

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


@auth.requires_login(otherwise=return_json_login_error)
def get_school_subscriptions():
    """
    List of not archived school classcards
    Sorted by Name
    """
    set_headers()
    permission_result = check_permission()
    if not permission_result['permission']:
        return return_json_permissions_error()

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


@auth.requires_login(otherwise=return_json_login_error)
def get_school_memberships():
    """
    List of not archived school classcards
    Sorted by Name
    """
    set_headers()
    permission_result = check_permission()
    if not permission_result['permission']:
        return return_json_permissions_error()

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


@auth.requires_login(otherwise=return_json_login_error)
def get_customer_notes():
    """
    Return notes for a given customer
    """
    set_headers()
    permission_result = check_permission()
    if not permission_result['permission']:
        return return_json_permissions_error()

    cuID = request.vars['id']

    print(cuID)

    query = (db.customers_notes.auth_customer_id == cuID) & \
            (db.customers_notes.TeacherNote == True)

    rows = db(query).select(
        db.customers_notes.id,
        db.customers_notes.auth_user_id,
        db.customers_notes.NoteDate,
        db.customers_notes.NoteTime,
        db.customers_notes.Note,
        db.customers_notes.Processed,
        orderby=~db.customers_notes.NoteDate|\
                ~db.customers_notes.NoteTime
    )

    # print rows

    notes = []
    for i, row in enumerate(rows):
        # print row
        repr_row = list(rows[i:i + 1].render())[0]

        date = row.NoteDate
        time = row.NoteTime
        note_dt = datetime.datetime(
            date.year,
            date.month,
            date.day,
            time.hour,
            time.minute
        )

        # print note_dt

        notes.append({
            "id": row.id,
            "Timestamp": note_dt.strftime(DATETIME_FORMAT),
            "Note": row.Note,
            "User": repr_row.auth_user_id,
            "Processed": row.Processed
        })

    # print notes

    return dict(data=notes)


@auth.requires_login(otherwise=return_json_login_error)
def create_customer_note():
    """
    :return: dict containing data of new note
    """
    set_headers()
    permission_result = check_permission()
    if not permission_result['permission']:
        return return_json_permissions_error()

    print(request.vars)

    # Set some default values
    db.customers_notes.auth_user_id.default = auth.user.id
    db.customers_notes.auth_customer_id.default = request.vars['cuID']
    db.customers_notes.TeacherNote.default = True

    result = db.customers_notes.validate_and_insert(**request.vars)
    print(result)

    error = False
    if result.errors:
        error = True

    # if not error:
    #     row = db.customers_notes(result['id'])

    return dict(result=result,
                error=error)


@auth.requires_login(otherwise=return_json_login_error)
def update_customer_note():
    """
    :return: dict containing data of new note
    """
    set_headers()
    permission_result = check_permission()
    if not permission_result['permission']:
        return return_json_permissions_error()

    print(request.vars)

    cnID = request.vars['id']

    print(cnID)
    cn = db.customers_notes(cnID)
    cn.Note = request.vars['Note']
    record = cn.update_record()

    # error = False
    # if result.errors:
    #     error = True

    # if not error:
    #     row = db.customers_notes(result['id'])

    return dict(error=False)


@auth.requires_login(otherwise=return_json_login_error)
def update_customer_note_status():
    """
    :return: dict containing data of new note
    """
    set_headers()
    permission_result = check_permission()
    if not permission_result['permission']:
        return return_json_permissions_error()

    print(request.vars)

    cnID = request.vars['id']

    print(cnID)
    cn = db.customers_notes(cnID)
    cn.Processed = not cn.Processed
    record = cn.update_record()

    # error = False
    # if result.errors:
    #     error = True

    # if not error:
    #     row = db.customers_notes(result['id'])

    return dict(error=False)


@auth.requires_login(otherwise=return_json_login_error)
def delete_customer_note():
    """

    :return:
    """
    set_headers()
    permission_result = check_permission()
    if not permission_result['permission']:
        return return_json_permissions_error()

    print(request.vars)
    cnID = request.vars['id']

    query = (db.customers_notes.id == cnID)
    error = db(query).delete()

    return dict(id=cnID, error=error)


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


@auth.requires_login(otherwise=return_json_login_error)
def get_customers():
    """
    Get non trashed customers from cache
    """
    # forget session
    set_headers()
    permission_result = check_permission()
    if not permission_result['permission']:
        return return_json_permissions_error()

    session.forget(response)

    # Don't cache when running tests
    if web2pytest.is_running_under_test(request, request.application):
        data = _get_customers()
    else:
        cache_key = 'openstudio_pos_get_customers'
        data = cache.ram(cache_key,
                         lambda: _get_customers(),
                         time_expire=600)

    return data


def _get_customers(var=None):
    """
    List not trashed customers
    """
    query = (db.auth_user.customer == True) & \
            (db.auth_user.trashed == False)

    rows = db(query).select(
        db.auth_user.id,
        db.auth_user.first_name,
        db.auth_user.last_name,
        db.auth_user.display_name,
        db.auth_user.email,
        # db.auth_user.gender,
        db.auth_user.date_of_birth,
        # db.auth_user.address,
        # db.auth_user.postcode,
        # db.auth_user.city,
        # db.auth_user.country,
        # db.auth_user.phone,
        db.auth_user.mobile,
        # db.auth_user.emergency,
        # db.auth_user.company,
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
            # 'gender': row.gender,
            'date_of_birth': date_of_birth,
            # 'address': row.address,
            # 'postcode': row.postcode,
            # 'city': row.city,
            # 'country': row.country,
            # 'phone': row.phone,
            'mobile': row.mobile,
            # 'emergency': row.emergency,
            # 'company': row.company,
            'thumbsmall': get_customers_thumbnail_url(row.thumbsmall),
            'thumblarge': get_customers_thumbnail_url(row.thumblarge),
            'barcode_id': row.barcode_id
        }

    return customers


@auth.requires_login(otherwise=return_json_login_error)
def get_customer_memberships_today():
    """
    List customer memberships
    """
    set_headers()
    permission_result = check_permission()
    if not permission_result['permission']:
        return return_json_permissions_error()

    cuID = request.vars['id']

    query = (db.customers_memberships.Startdate <= TODAY_LOCAL) & \
            ((db.customers_memberships.Enddate >= TODAY_LOCAL) |
             (db.customers_memberships.Enddate == None)) & \
            (db.customers_memberships.auth_customer_id == cuID)

    rows = db(query).select(
        db.customers_memberships.id,
        db.customers_memberships.auth_customer_id,
        db.customers_memberships.school_memberships_id,
        db.customers_memberships.Startdate,
        db.customers_memberships.Enddate,
    )

    memberships = []
    for i, row in enumerate(rows):
        repr_row = list(rows[i:i + 1].render())[0]

        memberships.append({
            'id': row.id,
            'auth_customer_id': row.auth_customer_id,
            'name': repr_row.school_memberships_id,
            'school_memberships_id': row.school_memberships_id,
            'start': repr_row.Startdate,
            'end': repr_row.Enddate,
        })

    return dict(data=memberships)


@auth.requires_login(otherwise=return_json_login_error)
def get_customer_memberships():
    """
    List customer memberships, from the last 400 days
    """
    set_headers()
    permission_result = check_permission()
    if not permission_result['permission']:
        return return_json_permissions_error()

    cuID = request.vars['id']

    date_from = TODAY_LOCAL - datetime.timedelta(days=400)

    query = (db.customers_memberships.Startdate >= date_from) & \
            (db.customers_memberships.auth_customer_id == cuID)
    left = [
        db.school_memberships.on(
            db.customers_memberships.school_memberships_id ==
            db.school_memberships.id
        )
    ]

    rows = db(query).select(
        db.customers_memberships.id,
        db.customers_memberships.auth_customer_id,
        db.customers_memberships.Startdate,
        db.customers_memberships.Enddate,
        db.school_memberships.id,
        db.school_memberships.Name,
        left=left
    )

    memberships = []
    for i, row in enumerate(rows):

        memberships.append({
            'id': row.customers_memberships.id,
            'auth_customer_id': row.customers_memberships.auth_customer_id,
            'name': row.school_memberships.Name,
            'school_memberships_id': row.school_memberships.id,
            'start': row.customers_memberships.Startdate.strftime(DATE_FORMAT),
            'end': row.customers_memberships.Enddate.strftime(DATE_FORMAT),
        })

    return dict(data=memberships)


@auth.requires_login(otherwise=return_json_login_error)
def get_customer_classcards():
    """
    List customer subscriptions, excluding cards that ended more then 
    7 months ago
    """
    set_headers()
    permission_result = check_permission()
    if not permission_result['permission']:
        return return_json_permissions_error()

    cuID = request.vars['id']

    dont_show_after = TODAY_LOCAL - datetime.timedelta(days=217)
    query = (db.customers_classcards.Startdate <= TODAY_LOCAL) &\
            ((db.customers_classcards.Enddate >= dont_show_after) |
             (db.customers_classcards.Enddate == None)) & \
            (db.customers_classcards.auth_customer_id == cuID)

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

    classcards = []
    for i, row in enumerate(rows):
        repr_row = list(rows[i:i + 1].render())[0]

        classes_taken = row.customers_classcards.ClassesTaken or 0

        classcards.append({
            'id': row.customers_classcards.id,
            'auth_customer_id': row.customers_classcards.auth_customer_id,
            'name': row.school_classcards.Name,
            'start': repr_row.customers_classcards.Startdate,
            'end': repr_row.customers_classcards.Enddate,
            'classes_remaining': row.school_classcards.Classes - classes_taken,
            'classes': row.school_classcards.Classes,
            'classes_display': repr_row.school_classcards.Classes,
            'unlimited': row.school_classcards.Unlimited
        })

    return dict(data=classcards)


@auth.requires_login(otherwise=return_json_login_error)
def get_customer_payment_info_known():
    """
    Return true when payment info is known (records exists and AccountNumber != None, else false
    :return:
    """
    set_headers()
    permission_result = check_permission()
    if not permission_result['permission']:
        return return_json_permissions_error()

    cuID = request.vars['id']
    print(request.vars)
    print(auth.has_membership(group_id='Admins'))
    print(auth.has_permission('read', 'customers_payment_info'))

    query = (db.customers_payment_info.auth_customer_id == cuID) & \
            (db.customers_payment_info.AccountNumber != None)
    count = db(query).count()

    if count:
        return dict(payment_info_known=True)
    else:
        return dict(payment_info_known=False)


@auth.requires_login(otherwise=return_json_login_error)
def get_customer_subscriptions():
    """
    List customer subscriptions, excluding subscriptions that ended more then 
    7 months ago
    """
    set_headers()
    permission_result = check_permission()
    if not permission_result['permission']:
        return return_json_permissions_error()

    cuID = request.vars['id']

    dont_show_after = TODAY_LOCAL - datetime.timedelta(days=217)
    query = (db.customers_subscriptions.Startdate <= TODAY_LOCAL) &\
            ((db.customers_subscriptions.Enddate >= dont_show_after) |
             (db.customers_subscriptions.Enddate == None)) & \
            (db.customers_subscriptions.auth_customer_id == cuID)


    rows = db(query).select(
        db.customers_subscriptions.id,
        db.customers_subscriptions.auth_customer_id,
        db.customers_subscriptions.school_subscriptions_id,
        db.customers_subscriptions.Startdate,
        db.customers_subscriptions.Enddate,
        db.customers_subscriptions.MinEnddate,
    )

    subscriptions = []
    for i, row in enumerate(rows):
        repr_row = list(rows[i:i + 1].render())[0]

        end_date = None
        min_end = None
        if row.Enddate:
            end_date = row.Enddate.strftime(DATE_FORMAT)

        if row.MinEnddate:
            min_end = row.MinEnddate.strftime(DATE_FORMAT)


        subscriptions.append({
            'id': row.id,
            'auth_customer_id': row.auth_customer_id,
            'name': repr_row.school_subscriptions_id,
            'start': row.Startdate.strftime(DATE_FORMAT),
            'end': end_date,
            'min_end': min_end
        })

    return dict(data=subscriptions)


@auth.requires_login(otherwise=return_json_login_error)
def get_customer_reconcile_later_classes():
    """
    List customer reconcile later classes

    :return:
    """
    set_headers()
    permission_result = check_permission()
    if not permission_result['permission']:
        return return_json_permissions_error()

    from openstudio.os_attendance_helper import AttendanceHelper

    cuID = request.vars['id']

    left = [
        db.classes.on(
            db.classes_attendance.classes_id ==
            db.classes.id
        ),
        db.school_classtypes.on(
            db.classes.school_classtypes_id ==
            db.school_classtypes.id,
        ),
        db.school_locations.on(
            db.classes.school_locations_id ==
            db.school_locations.id
        )
    ]

    # Type 6 = reconcile later
    query = (db.classes_attendance.AttendanceType == 6) & \
            (db.classes_attendance.auth_customer_id == cuID)
    rows = db(query).select(
        db.classes_attendance.ALL,
        db.classes.ALL,
        db.school_locations.Name,
        db.school_classtypes.Name,
        left=left,
        orderby = db.classes_attendance.ClassDate
    )

    ah = AttendanceHelper()
    reconcile_later_classes = []
    for row in rows:

        price = ah._attendance_sign_in_get_dropin_trial_price(
            row.classes_attendance.auth_customer_id,
            row.classes_attendance.classes_id,
            row.classes_attendance.ClassDate,
            'dropin'
        )
        reconcile_later_classes.append({
            'id': row.classes_attendance.id,
            'auth_customer_id': row.classes_attendance.auth_customer_id,
            'class_id': row.classes_attendance.classes_id,
            'class_date': row.classes_attendance.ClassDate.strftime(DATE_FORMAT),
            'has_membership': row.classes_attendance.CustomerMembership,
            'school_location': row.school_locations.Name,
            'school_classtype': row.school_classtypes.Name,
            'time_start': row.classes.Starttime.strftime(TIME_FORMAT),
            'time_end': row.classes.Endtime.strftime(TIME_FORMAT),
            'price': price
        })

    return dict(data=reconcile_later_classes)


@auth.requires_login(otherwise=return_json_login_error)
def get_customer_school_info():
    """
    List customer information
    - subscriptions
    - memberships
    - classcards
    - reconcile later classes
    :return:
    """
    set_headers()
    permission_result = check_permission()
    if not permission_result['permission']:
        return return_json_permissions_error()

    cuID = request.vars['id']

    subscriptions = get_customer_subscriptions()['data']
    classcards = get_customer_classcards()['data']
    memberships = get_customer_memberships()['data']
    reconcile_later_classes = get_customer_reconcile_later_classes()['data']

    return dict(
        subscriptions=subscriptions,
        classcards=classcards,
        memberships=memberships,
        reconcile_later_classes=reconcile_later_classes
    )


@auth.requires_login(otherwise=return_json_login_error)
def update_class_attendance():
    """

    :return:
    """
    set_headers()
    permission_result = check_permission()
    if not permission_result['permission']:
        return return_json_permissions_error()

    from openstudio.os_class_attendance import ClassAttendance


    print(request.vars)
    clattID = request.vars['id']
    status = request.vars['status']

    ca = ClassAttendance(clattID)
    ca.set_status(status)

    return dict(clattID=clattID, status=status)


@auth.requires_login(otherwise=return_json_login_error)
def delete_class_attendance():
    """

    :return:
    """
    set_headers()
    permission_result = check_permission()
    if not permission_result['permission']:
        return return_json_permissions_error()

    from openstudio.os_classcards_helper import ClasscardsHelper
    from openstudio.os_class_attendance import ClassAttendance

    clattID = request.vars['id']

    clatt = db.classes_attendance(clattID)
    cuID = clatt.auth_customer_id
    clsID = clatt.classes_id
    date_formatted = clatt.ClassDate.strftime(DATE_FORMAT)

    ##
    # Change invoice status to cancelled (if any)
    ##
    query = (db.invoices_items_classes_attendance.classes_attendance_id == clattID)
    left = [
        db.invoices_items.on(
            db.invoices_items_classes_attendance.invoices_items_id ==
            db.invoices_items.id
        )
    ]
    rows = db(query).select(
        db.invoices_items.ALL,
        left=left,
    )
    for row in rows:
        invoice = Invoice(row.invoices_id)
        invoice.set_status('cancelled')

    ##
    # Delete attendance record
    ##
    query = (db.classes_attendance.id == clattID)
    db(query).delete()

    # Clear cache to refresh subscription credit count
    cache_clear_customers_subscriptions(cuID)

    # Clear cache to refresh classes taken count
    cache_clear_customers_classcards(cuID)

    # Clear api cache to refresh available spaces
    cache_clear_classschedule_api()


    if clatt.customers_classcards_id:
        # update class count on classcard
        ccdh = ClasscardsHelper()
        ccdh.set_classes_taken(clatt.customers_classcards_id)

    return dict(clattID=clattID, error=False)


@auth.requires_login(otherwise=return_json_login_error)
def create_customer():
    """
    :return: dict containing data of new auth_user
    """
    set_headers()
    permission_result = check_permission()
    if not permission_result['permission']:
        return return_json_permissions_error()

    from openstudio.os_cache_manager import OsCacheManager

    ocm = OsCacheManager()


    db.auth_user.password.requires = None
    print(request.vars)

    result = db.auth_user.validate_and_insert(**request.vars)
    print(result)
    ocm.clear_customers()

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


@auth.requires_login(otherwise=return_json_login_error)
def update_customer():
    """
    :return: dict containing data of new auth_user
    """
    set_headers()
    permission_result = check_permission()
    if not permission_result['permission']:
        return return_json_permissions_error()

    from openstudio.os_cache_manager import OsCacheManager

    ocm = OsCacheManager()

    db.auth_user.password.requires = None
    print(request.vars)

    cuID = request.vars.pop('id', None)

    print(cuID)
    print(request.vars)

    print(db.auth_user.email.requires)

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
        ocm.clear_customers()
        print(result)
        error = False
        if result.errors:
            error = True
            customer_data = {}

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


@auth.requires_login(otherwise=return_json_login_error)
def update_customer_picture():
    """
    :return: dict containing data of new auth_user
    """
    set_headers()
    permission_result = check_permission()
    if not permission_result['permission']:
        return return_json_permissions_error()

    import io

    status = 'fail'
    data = {}

    cuID = request.vars['cuID']
    picture = request.vars['picture'].split(',')[1] # Remove description from b64 encoded image

    if cuID:
        # start decode into image
        import base64
        png_image = base64.b64decode(picture)
        # Create file stream
        stream = io.BytesIO(png_image)

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


@auth.requires_login(otherwise=return_json_login_error)
def update_customer_payment_information():
    """
    :return: dict containing data of new note
    """
    set_headers()
    permission_result = check_permission()
    if not permission_result['permission']:
        return return_json_permissions_error()

    print('payment info endpoint here:')
    print(request.vars)

    cuID = request.vars['id']
    account_number = request.vars['AccountNumber']
    account_holder = request.vars['AccountHolder']

    # Fetch existing payment info for customer, if any
    query = (db.customers_payment_info.auth_customer_id == cuID)
    rows = db(query).select(db.customers_payment_info.ALL)

    if not rows:
        # Insert
        result = db.customers_payment_info.validate_and_insert(
            auth_customer_id = cuID,
            AccountNumber = account_number,
            AccountHolder = account_holder
        )

    else:
        # Update
        row = rows.first()
        query = (db.customers_payment_info.id == row.id)
        result = db(query).validate_and_update(
            id = row.id,
            AccountNumber = account_number,
            AccountHolder = account_holder
        )

    error = False
    if result.errors:
        error = True

    return dict(result=result,
                error=error)


@auth.requires_login(otherwise=return_json_login_error)
def get_products():
    """

    :return: dict containing products sorted by category
    """
    set_headers()
    permission_result = check_permission()
    if not permission_result['permission']:
        return return_json_permissions_error()

    from openstudio.os_shop_products_variants import ShopProductsVariants
    # from openstudio.os_shop_category import ShopCategory

    import pprint

    pp = pprint.PrettyPrinter(depth=6)

    spv = ShopProductsVariants()

    data = spv.list_pos()
    # pp.pprint(data)

    return dict(data=data)


@auth.requires_login(otherwise=return_json_login_error)
def get_payment_methods():
    """

    :return: dict containing payment methods sorted by name
    """
    set_headers()
    permission_result = check_permission()
    if not permission_result['permission']:
        return return_json_permissions_error()

    not_pos_methods = [2, 3, 100]
    query = (db.payment_methods.Archived == False) & \
            ~(db.payment_methods.id.belongs(not_pos_methods))

    rows = db(query).select(
        db.payment_methods.ALL,
        orderby=~db.payment_methods.SystemMethod|db.payment_methods.Name
    )

    return dict(data=rows.as_list())


@auth.requires_login(otherwise=return_json_login_error)
def get_tax_rates():
    """

    :return: dict containing payment methods sorted by name
    """
    set_headers()
    permission_result = check_permission()
    if not permission_result['permission']:
        return return_json_permissions_error()

    query = (db.tax_rates.Archived == False)

    rows = db(query).select(
        db.tax_rates.ALL,
        orderby=~db.tax_rates.Name
    )

    return dict(data=rows.as_list())


@auth.requires_login(otherwise=return_json_login_error)
def get_product_categories():
    """

    :return: dict containing payment methods sorted by name
    """
    set_headers()
    permission_result = check_permission()
    if not permission_result['permission']:
        return return_json_permissions_error()

    query = (db.shop_categories.Archived == False)

    rows = db(query).select(
        db.shop_categories.id,
        db.shop_categories.Name,
        orderby=db.shop_categories.Name
    )

    return dict(data=rows.as_dict())


@auth.requires_login(otherwise=return_json_login_error)
def validate_cart():
    """
    Process shopping cart
    :return:
    """
    # print request.env
    set_headers()
    permission_result = check_permission()
    if not permission_result['permission']:
        return return_json_permissions_error()


    print("POS read permissions")
    print(auth.has_membership(group_id='Admins') or
          auth.has_permission('read', 'pos'))

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

    print('customerID')
    print(type(cuID))
    print(cuID)

    print('validate_cart_items:')
    print(items)

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
                print('validating subscriptions')
                print(subscription_ids)
                if item['data']['id'] in subscription_ids:
                    error = True
                    message = T("This customer already has this subscription")
                        
            if item['item_type'] == 'membership':
                membership_ids = customer.get_school_memberships_ids_on_date(TODAY_LOCAL)
                print('validating memberhsips')
                print(membership_ids)
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
            # Use order to create receipts
            print('create order')
            result = validate_cart_create_order(cuID, pmID, items)
            invoice = result['invoice']
            receipt = result['receipt']
        else:
            # Create receipt for products and custom items manually
            print('create receipt directly')
            receipt = validate_cart_create_receipt(
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
        print(receipt_items)
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
                item['data']['id']
            )
        elif item['item_type'] == 'membership':
            order.order_item_add_membership(
                item['data']['id'],
                TODAY_LOCAL
            )
        elif item['item_type'] == 'class_reconcile_later':
            datestr = item['data']['class_date']
            class_date = datestr_to_python(DATE_FORMAT, datestr)

            query = (db.classes_attendance.id == item['data']['id'])
            db(query).delete()

            order.order_item_add_class(
                item['data']['class_id'],
                class_date,
                2 # Attendance Type 2 = drop-in
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
        class_booking_status='attending',
        payment_methods_id=pmID
    )

    invoice = result['invoice']

    # Add payment
    ipID = invoice.payment_add(
        amounts.TotalPriceVAT,
        TODAY_LOCAL,
        payment_methods_id=pmID,
    )

    return result


def validate_cart_create_receipt(
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
        elif item['item_type'] == 'custom':
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

    return receipt


@auth.requires_login(otherwise=return_json_login_error)
def get_expenses():
    """
    :return: List of expenses
    """
    set_headers()
    permission_result = check_permission()
    if not permission_result['permission']:
        return return_json_permissions_error()

    query = (db.accounting_expenses.BookingDate == TODAY_LOCAL)

    rows = db(query).select(
        db.accounting_expenses.id,
        db.accounting_expenses.BookingDate,
        db.accounting_expenses.Amount,
        db.accounting_expenses.tax_rates_id,
        db.accounting_expenses.YourReference,
        db.accounting_expenses.Description,
        db.accounting_expenses.Note,
        orderby=db.accounting_expenses.Description
    )

    expenses = {}

    for row in rows:
        expenses[row.id] = row.as_dict()

    return expenses


@auth.requires_login(otherwise=return_json_login_error)
def get_cash_counts():
    """
    :return: List of expenses
    """
    set_headers()
    permission_result = check_permission()
    if not permission_result['permission']:
        return return_json_permissions_error()

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


@auth.requires_login(otherwise=return_json_login_error)
def set_cash_count():
    set_headers()
    permission_result = check_permission()
    if not permission_result['permission']:
        return return_json_permissions_error()

    print(request.vars)

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


@auth.requires_login(otherwise=return_json_login_error)
def create_expense():
    """
    :return: dict containing data of new auth_user
    """
    set_headers()
    permission_result = check_permission()
    if not permission_result['permission']:
        return return_json_permissions_error()

    print(request.vars)

    # Clean up input of amount
    if 'Amount' in request.vars:
        if ',' in request.vars['Amount']:
            request.vars['Amount'] = request.vars['Amount'].replace(',', '.')


    result = db.accounting_expenses.validate_and_insert(**request.vars)
    print(result)

    expense_data = ''
    error = False
    if result.errors:
        error = True

    if not error:
        row = db.accounting_expenses(result['id'])

        expense_data = row.as_dict()

    return dict(result=result,
                expense_data=expense_data,
                error=error)


@auth.requires_login(otherwise=return_json_login_error)
def update_expense():
    """
    :return: dict containing data of new auth_user
    """
    set_headers()
    permission_result = check_permission()
    if not permission_result['permission']:
        return return_json_permissions_error()

    print(request.vars)
    aeID = request.vars.pop('id', None)
    print(aeID)

    # Clean up input of amount
    if 'Amount' in request.vars:
        if ',' in request.vars['Amount']:
            request.vars['Amount'] = request.vars['Amount'].replace(',', '.')

    query = (db.accounting_expenses.id == aeID)
    result = db(query).validate_and_update(**request.vars)
    # print result

    expense_data = ''
    error = False
    if result.errors:
        error = True

    if not error:
        row = db.accounting_expenses(aeID)
        expense_data = row.as_dict()

    return dict(result=result,
                expense_data=expense_data,
                error=error,
                id=aeID)


@auth.requires_login(otherwise=return_json_login_error)
def delete_expense():
    """

    :return:
    """
    set_headers()
    permission_result = check_permission()
    if not permission_result['permission']:
        return return_json_permissions_error()

    print(request.vars)
    aeID = request.vars['id']

    query = (db.accounting_expenses.id == aeID)
    db(query).delete()

    return dict(id=aeID, error=False)
