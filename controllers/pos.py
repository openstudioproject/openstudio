# -*- coding: utf-8 -*-

from general_helpers import set_form_id_and_get_submit_button
from general_helpers import datestr_to_python

# auth.settings.on_failed_authorization = URL('return_json_permissions_error')


@auth.requires_login()
def index():
    # print auth.user

    return dict()


def set_headers(var=None):
    if request.env.HTTP_ORIGIN == 'http://localhost:8080':
        response.headers["Access-Control-Allow-Origin"] = request.env.HTTP_ORIGIN
    response.headers["Access-Control-Allow-Credentials"] = "true"


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
        'checkin_barcodes': get_sys_property('pos_barcodes_checkin')
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
    rows = db(query).select(db.school_classcards.Name,
                            db.school_classcards.Description,
                            db.school_classcards.Price,
                            db.school_classcards.Validity,
                            db.school_classcards.ValidityUnit,
                            db.school_classcards.Classes,
                            db.school_classcards.Unlimited,
                            db.school_classcards.Trialcard,
                            orderby=db.school_classcards.Name)

    data_rows = []
    for row in rows:
        item = {
            'Name': row.Name,
            'Description': row.Description,
            'Price': row.Price,
            'Validity': row.Validity,
            'ValidityUnit': row.ValidityUnit,
            'ValidityDisplay': get_validity(row),
            'Classes': row.Classes,
            'Unlimited': row.Unlimited,
            'Trialcard': row.Trialcard
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
        SELECT sc.Name,
               sc.SortOrder,
               sc.Description,
               sc.Classes,
               sc.SubscriptionUnit,
               sc.Unlimited,
               scp.Price
        FROM school_subscriptions sc
        LEFT JOIN
        ( SELECT school_subscriptions_id, 
                 Price
          FROM school_subscriptions_price
          WHERE Startdate <= '{today}' AND
                (Enddate >= '{today}' OR Enddate IS NULL) 
        ) scp ON sc.id = scp.school_subscriptions_id
        WHERE sc.PublicSubscription = 'T' AND sc.Archived = 'F'
        ORDER BY sc.Name
    """.format(today=TODAY_LOCAL)

    fields = [ db.school_subscriptions.Name,
               db.school_subscriptions.SortOrder,
               db.school_subscriptions.Description,
               db.school_subscriptions.Classes,
               db.school_subscriptions.SubscriptionUnit,
               db.school_subscriptions.Unlimited,
               db.school_subscriptions_price.Price ]

    rows = db.executesql(query, fields=fields)

    data = []
    for row in rows:
        data.append({
            'Name': row.school_subscriptions.Name,
            'SortOrder': row.school_subscriptions.SortOrder,
            'Description': row.school_subscriptions.Description or '',
            'Classes': row.school_subscriptions.Classes,
            'SubscriptionUnit': row.school_subscriptions.SubscriptionUnit,
            'Unlimited': row.school_subscriptions.Unlimited,
            'Price': row.school_subscriptions_price.Price
        })

    return dict(data=data)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'school_memberships'))
def get_school_subscriptions():
    """
    List of not archived school classcards
    Sorted by Name
    """
    set_headers()

    query = """
        SELECT sm.Name,
               sm.SortOrder,
               sm.Description,
               sm.Classes,
               sm.SubscriptionUnit,
               sm.Unlimited,
               smp.Price
        FROM school_memberships sm
        LEFT JOIN
        ( SELECT school_memberships_id, 
                 Price
          FROM school_shool_memberships_price
          WHERE Startdate <= '{today}' AND
                (Enddate >= '{today}' OR Enddate IS NULL) 
        ) smp ON sm.id = smp.school_memberships_id
        WHERE sm.PublicMembership = 'T' AND sm.Archived = 'F'
        ORDER BY sm.Name
    """.format(today=TODAY_LOCAL)

    fields = [ db.school_memberships.Name,
               db.school_memberships.Description,
               db.school_memberships.Validity,
               db.school_memberships.ValidityUnit,
               db.school_memberships_price.Price ]

    rows = db.executesql(query, fields=fields)

    data = []
    for row in rows:
        data.append({
            'Name': row.school_memberships.Name,
            'Description': row.school_memberships.Description or '',
            'Validity': row.school_memberships.Validity,
            'ValidityUnit': row.school_memberships.ValidityUnit,
            'Price': row.school_memberships_price.Price
        })

    return dict(data=data)

