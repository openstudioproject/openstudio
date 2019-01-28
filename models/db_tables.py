# coding: utf8
import datetime
import pytz

from gluon.scheduler import Scheduler
from gluon import current

from smarthumb import SMARTHUMB

from general_helpers import NRtoDay
from general_helpers import NRtoMonth
from general_helpers import NRtoPriority
from general_helpers import get_months_list
from general_helpers import get_priorities
from general_helpers import get_last_day_month
from general_helpers import get_group_id
from general_helpers import get_payment_batches_statuses
from general_helpers import string_to_int

from general_helpers import create_teachers_dict
from general_helpers import create_employees_dict
from general_helpers import create_locations_dict
from general_helpers import create_classtypes_dict

from decimal import Decimal, ROUND_HALF_UP

# init scheduler
scheduler = Scheduler(
    db,
    tasks=scheduler_tasks,
    utc_time=True
)

# helper functions

# Set global variable to show how many organizations we have
def _get_organizations():
    """
        Get organizations
    """
    query = (db.sys_organizations.Archived == False)
    rows = db(query).select(db.sys_organizations.ALL)

    organizations = {}
    for row in rows:
        organization = {}
        for field in row:
            organization[field] = row[field]

        organizations[row.id] = organization

        if row.DefaultOrganization:
            organizations['default'] = row.id

    return organizations


def get_organizations():
    """
        Get organizations from cache
    """
    # Don't cache when running tests
    if web2pytest.is_running_under_test(request, request.application):
        organizations = _get_organizations()
    else:
        cache_key = 'openstudio_sys_organizations'

        organizations = cache.ram(cache_key, lambda: _get_organizations(), time_expire=CACHE_LONG)

    return organizations


def set_class_status():
    session.class_status = dict(subteacher = T('Subteacher'),
                                open_class = T('Open'),
                                cancelled  = T('Cancelled'),
                                normal     = T('Normal'))
def set_shift_status():
    return dict(sub        = T('Sub'),
                open       = T('Open'),
                cancelled  = T('Cancelled'))

def represent_user_thumbsmall(value, row):
    today = TODAY_LOCAL
    cls = 'customer_image'
    cls_img = ''
    active = True
    birthday = False
    display_name = ''

    if 'trashed' in row:
        display_name = row.display_name
        thumb = row.thumbsmall
        cu_id = row.id
        if row.trashed:
            active = False

        if row.birthday:
            birthday = row.birthday
    elif 'trashed' in row.auth_user:
        display_name = row.auth_user.display_name
        thumb = row.auth_user.thumbsmall
        cu_id = row.auth_user.id
        if row.auth_user.trashed:
            active = False

        if row.auth_user.birthday:
            birthday = row.auth_user.birthday

    if not active:
        cls_img += ' red_border'

    present = ''
    if birthday:
        if birthday.day == today.day and birthday.month == today.month:
            present = SPAN(os_gui.get_fa_icon('fa-birthday-cake'),
                        _class='pull-right orange vsmall_font',
                        _title=T('Today is ') + display_name + T("'s birthday!"))

    alt = display_name
    if thumb is None:
        return DIV(present,
                    A(IMG(_src=URL('static', 'images/person.png'),
                         _alt=alt,
                         _class=cls_img),
                   _href=URL('customers', 'edit', args=[cu_id],
                             extension='')),
                   _class=cls)
    else:
        return DIV(present,
                    A(IMG(_src=URL('default', 'download', args=value),
                         _alt=alt,
                         _class=cls_img),
                   _href=URL('customers', 'edit', args=[cu_id],
                             extension='')),
                   _class=cls)


def represent_workshops_thumbsmall(value, row):
    if 'Name' in row:
        name = row.Name
        thumb = row.thumbsmall
        wsID = row.id

    elif 'Name' in row.workshops:
        name = row.workshops.Name
        thumb = row.workshops.thumbsmall
        wsID = row.workshops.id

    vars = {'wsID':wsID}

    alt = 'Image'
    url = URL('events', 'event_edit', vars=vars, extension='')
    edit_permission  = (auth.has_membership(group_id='Admins') or
                   auth.has_permission('update', 'workshops'))
    if edit_permission:
        if thumb is None:
            return DIV(A(I(_class='fa fa-photo big_font'),
                         _href=url),
                       _class='workshop_image')
        else:
            return DIV(A(IMG(_src=URL('default', 'download', args=value),
                             _alt=alt),
                         _href=url),
                        _class='workshop_image')
    else:
        if thumb is None:
            return DIV(I(_class='fa fa-2x fa-photo'),_class='workshop_image')
        else:
            return DIV(IMG(_src=URL('default', 'download', args=value),
                           _alt=alt),
                        _class='workshop_image')


def represent_shop_products_thumbsmall(value, row):
    if 'Name' in row:
        name = row.Name
        thumb = row.thumbsmall
        spID = row.id

    elif 'Name' in row.shop_products:
        name = row.shop_products.Name
        thumb = row.shop_products.thumbsmall
        spID = row.shop_products.id

    vars = {'spID':spID}

    alt = 'Image'
    url = URL('shop_manage', 'product_edit', vars=vars, extension='')
    edit_permission  = (auth.has_membership(group_id='Admins') or
                   auth.has_permission('update', 'shop_products'))
    if edit_permission:
        if thumb is None:
            return DIV(A(I(_class='fa fa-photo big_font'),
                         _href=url),
                       _class='shop_product_image')
        else:
            return DIV(A(IMG(_src=URL('default', 'download', args=value),
                             _alt=alt),
                         _href=url),
                        _class='shop_product_image')
    else:
        if thumb is None:
            return DIV(I(_class='fa fa-2x fa-photo'),_class='shop_product_image')
        else:
            return DIV(IMG(_src=URL('default', 'download', args=value),
                           _alt=alt),
                        _class='shop_product_image')


def represent_shop_products_variants_thumbsmall(value, row):
    if 'Name' in row:
        name = row.Name
        thumb = row.thumbsmall
        spvID = row.id
        spID = row.shop_products_id
    elif 'Name' in row.shop_products_variants:
        name = row.shop_products_variants.Name
        thumb = row.shop_products_variants.thumbsmall
        spvID = row.shop_products_variants.id
        spID = row.shop_products_variants.shop_products_id

    vars = {'spvID':spvID, 'spID':spID}

    alt = 'Image'
    url = URL('shop_manage', 'product_variant_edit', vars=vars, extension='')
    edit_permission  = (auth.has_membership(group_id='Admins') or
                   auth.has_permission('update', 'shop_products_variants'))
    if edit_permission:
        if thumb is None:
            return DIV(A(I(_class='fa fa-photo big_font'),
                         _href=url),
                       _class='shop_product_image')
        else:
            return DIV(A(IMG(_src=URL('default', 'download', args=value),
                             _alt=alt),
                         _href=url),
                        _class='shop_product_image')
    else:
        if thumb is None:
            return DIV(I(_class='fa fa-2x fa-photo'),_class='shop_product_image')
        else:
            return DIV(IMG(_src=URL('default', 'download', args=value),
                           _alt=alt),
                        _class='shop_product_image')


def represent_classtype_thumbsmall(value, row):
    if 'Name' in row:
        name = row.Name
        thumb = row.thumbsmall
        ctID = row.id

    elif 'Name' in row.school_classtypes:
        name = row.school_classtypes.Name
        thumb = row.school_classtypes.thumbsmall
        ctID = row.school_classtypes.id


    alt = name
    if thumb is None:
        return DIV(A(I(_class='fa fa-photo big_font'),
                     _href=URL('school_properties', 'classtype_edit', args=ctID,
                             extension='')),
                   _class='workshop_image')
    else:
        return DIV(A(IMG(_src=URL('default', 'download', args=value),
                         _alt=alt),
                     _href=URL('school_properties', 'classtype_edit', args=ctID,
                             extension='')),
                    _class='workshop_image')


def represent_workshops_thumblarge(value, row):
    if 'Name' in row:
        name = row.Name
        thumb = row.thumblarge
        wsID = row.id

    elif 'Name' in row.workshops:
        name = row.workshops.Name
        thumb = row.workshops.thumblarge
        wsID = row.workshops.id

    vars = {'wsID':wsID}
    alt = name
    if thumb is None:
        return DIV(A(I(_class='fa fa-photo big_font'),
                     _href=URL('shop', 'event', vars=vars,
                             extension='')),
                   _class='workshop_image_large')
    else:
        return DIV(A(IMG(_src=URL('default', 'download', args=value),
                         _alt=alt),
                     _href=URL('shop', 'event', vars=vars,
                             extension='')),
                    _class='workshop_image_large')


def represent_shop_products_thumblarge(value, row):
    if 'Name' in row:
        name = row.Name
        thumb = row.thumblarge
        spID = row.id

    elif 'Name' in row.shop_products:
        name = row.shop_products.Name
        thumb = row.shop_products.thumblarge
        spID = row.shop_products.id

    vars = {'spID':spID}
    alt = name
    if thumb is None:
        return DIV(A(I(_class='fa fa-photo big_font'),
                     _href=URL('shop_manage', 'product_edit', vars=vars,
                             extension='')),
                   _class='shop_product_image_large')
    else:
        return DIV(A(IMG(_src=URL('default', 'download', args=value),
                         _alt=alt),
                     _href=URL('shop_manage', 'product_edit', vars=vars,
                             extension='')),
                    _class='shop_product_image_large')


def represent_shop_products_variants_thumblarge(value, row):
    if 'Name' in row:
        name = row.Name
        thumb = row.thumblarge
        spvID = row.id

    elif 'Name' in row.shop_products_variants:
        name = row.shop_products_variants.Name
        thumb = row.shop_products_variants.thumblarge
        spvID = row.shop_products_variants.id

    vars = {'spvID':spvID}
    alt = name
    if thumb is None:
        return DIV(A(I(_class='fa fa-photo big_font'),
                     _href=URL('shop_manage', 'product_variant_edit', vars=vars,
                             extension='')),
                   _class='shop_product_image_large')
    else:
        return DIV(A(IMG(_src=URL('default', 'download', args=value),
                         _alt=alt),
                     _href=URL('shop_manage', 'product_variant_edit', vars=vars,
                             extension='')),
                    _class='shop_product_image_large')


def represent_payment_batch_status(value, row):
    """
        Returns a label for the status
    """
    label = ''
    statuses = get_payment_batches_statuses()
    for s, sd in statuses:
        if s == value:
            if s == 'sent_to_bank':
                label = os_gui.get_label('primary', sd)
            if s == 'approved':
                label = os_gui.get_label('success', sd)
            if s == 'awaiting_approval':
                label = os_gui.get_label('warning', sd)
            if s == 'rejected':
                label = os_gui.get_label('danger', sd)

    return label


def represent_customer_subscription_as_name(value, row):
    subscription = db.customers_subscriptions(row.customers_subscriptions_id)
    id = subscription.school_subscriptions_id
    return db.school_subscriptions(id).Name


def represent_time(value, row):
    if value is None:
        return value
    else:
        return value.strftime(TIME_FORMAT)


def represent_birthday(value, row):
    if value is None:
        return value
    else:
        return value.strftime("%B %d")


def represent_float_as_amount(value, row=None):
    """
        Takes value and rounds it to a 2 decimal number.
    """
    if value is None or (not isinstance(value, float) and not isinstance(value, int)):
        return ''
    else:
        return SPAN(CURRSYM, ' ', format(value, '.2f'))


def represent_boolean_as_checkbox(value, row=None):
    """
    :return: disabled html checkbox
    """
    checkbox = INPUT(value=value,
                     _type='checkbox',
                     _value='api',
                     _disabled='disabled')

    return checkbox


def represent_classes_attendance_bookingstatus(value, row):
    """
        Returns representation of booking status for classes attendance table
    """
    return_value = ''
    for status in booking_statuses:
        if value == status[0]:
            if value == 'cancelled':
                return_value = os_gui.get_label('warning', status[1])
            elif value == 'attending':
                return_value = os_gui.get_label('success', status[1])
            else:
                return_value = os_gui.get_label('primary', status[1])
            break

    return return_value


def represent_message_status(value, row):
    """
        Represent status of sent mails
    """
    if value == 'sent':
        rvalue = os_gui.get_label('success', T("Sent"))
    elif value == 'fail':
        rvalue = os_gui.get_label('danger', T("Sending failed"))

    return rvalue


def represent_teacher_role(value, row):
    """
        returns teacher role
    """
    teacher_role = ''
    for terID, role in teachers_roles:
        if terID == value:
            teacher_role = role

    return teacher_role


def set_show_location():
    show_location=False
    sprop = get_sys_property('Customer_ShowLocation')
    if sprop:
        if sprop == "on":
            show_location=True
    session.show_location = show_location


def os_date_widget(field, value):
    return DIV(
        INPUT(_name=field.name,
                 _type='text',
                 _id="%s_%s" % (field._tablename, field.name),
                 _class='date-inputmask',
                 _value=value,
                 _autocomplete="off",
                 requires=field.requires,
                 **{'_data-inputmask': "'alias': '" + DATE_MASK + "'",
                    '_data-mask':''}),
        DIV(os_gui.get_fa_icon('fa-calendar'), _class='input-group-addon'),
        _class='input-group full-width')


def os_date_widget_small(field, value):
    return DIV(
        INPUT(_name=field.name,
                 _type='text',
                 _id="%s_%s" % (field._tablename, field.name),
                 _class='date-inputmask',
                 _value=value,
                 _autocomplete="off",
                 requires=field.requires,
                 **{'_data-inputmask': "'alias': '" + DATE_MASK + "'",
                    '_data-mask':''}),
        _class='full-width')


def os_datepicker_widget(field, value):
    return DIV(
        INPUT(_name=field.name,
                 _type='text',
                 _id="%s_%s" % (field._tablename, field.name),
                 _class='datepicker',
                 _value=value,
                 _autocomplete="off",
                 requires=field.requires),
        DIV(os_gui.get_fa_icon('fa-calendar'), _class='input-group-addon'),
        _class='input-group full-width')


def os_datepicker_widget_small(field, value):
    return DIV(
        INPUT(_name=field.name,
                 _type='text',
                 _id="%s_%s" % (field._tablename, field.name),
                 _class='datepicker',
                 _value=value,
                 _autocomplete="off",
                 requires=field.requires),
        _class='full-width')


# def os_time_widget(field, value):
#     return DIV(
#         INPUT(_name=field.name,
#               _class='timepicker',
#               _type='text',
#               _id="%s_%s" % (field._tablename, field.name),
#               _value=value,
#               _autocomplete="off",
#               requires=field.requires),
#             DIV(os_gui.get_fa_icon('fa-clock-o'), _class='input-group-addon'),
#         _class='input-group bootstrap-timepicker timepicker full-width')

def os_time_widget(field, value):
    return DIV(
        INPUT(_name=field.name,
              _class='time-inputmask',
              _type='text',
              _id="%s_%s" % (field._tablename, field.name),
              _value=value,
              _autocomplete="off",
              requires=field.requires,
              **{'_data-inputmask': "'alias': 'h:s'",
                 '_data-mask': ''}),
            DIV(os_gui.get_fa_icon('fa-clock-o'), _class='input-group-addon'),
        _class='input-group full-width')


# Represent dict caching settings
dict_caching = (cache.ram, 20)
if web2pytest.is_running_under_test(request, request.application):
    dict_caching = None


def create_languages_dict():
    rows = db().select(db.school_languages.id, db.school_languages.Name, cache=dict_caching)
    d = dict()
    for row in rows:
        d[row.id] = row.Name
    d[None] = ""
    return d


# def create_customers_dict():
#     rows = db().select(db.auth_user.id,
#                        db.auth_user.first_name,
#                        db.auth_user.last_name)
#     d = dict()
#     for row in rows:
#         d[row.id] = row.first_name + " " + row.last_name
#     d[None] = ""
#     return d


def create_discovery_dict():
    rows = db().select(db.school_discovery.id, db.school_discovery.Name, cache=dict_caching)
    d = dict()
    for row in rows:
        d[row.id] = row.Name
    d[None] = ""
    return d


def create_mstypes_dict():
    rows = db().select(db.school_subscriptions.id, db.school_subscriptions.Name, cache=dict_caching)
    d = dict()
    for row in rows:
        d[row.id] = row.Name
    d[None] = ""
    return d


def create_school_levels_dict():
    rows = db().select(db.school_levels.id, db.school_levels.Name, cache=dict_caching)
    d = dict()
    for row in rows:
        d[row.id] = row.Name
    d[None] = XML('&nbsp;')
    return d


def create_payment_categories_dict():
    rows = db().select(db.payment_categories.id,
                       db.payment_categories.Name, cache=dict_caching)
    d = dict()
    for row in rows:
        d[row.id] = row.Name
    d[None] = T("")
    return d


def create_payment_methods_dict():
    rows = db().select(db.payment_methods.id, db.payment_methods.Name, cache=dict_caching)
    d = dict()
    for row in rows:
        d[row.id] = row.Name
    d[None] = ""
    d[0] = ""
    return d


# def create_classes_dict():
#     rows = db().select(db.classes.id,
#                        db.classes.school_locations_id,
#                        db.classes.school_classtypes_id,
#                        db.classes.Starttime,
#                        db.classes.Week_day,
#                        cache=(cache.ram, 15))
#     d = dict()
#     for row in rows:
#         location = locations_dict.get(row.school_locations_id)
#         classtype = classtypes_dict.get(row.school_classtypes_id)
#
#         d[row.id] = location + " "  + \
#                     NRtoDay(row.Week_day) + " " + \
#                     row.Starttime.strftime('%H:%M') + " " + \
#                     classtype
#     d[None] = ""
#     return d
# def create_workshops_dict():
#     rows = db().select(db.workshops.id,
#                        db.workshops.Name,
#                        cache=(cache.ram, 15))
#     d = dict()
#     for row in rows:
#         d[row.id] = row.Name
#
#     d[None] = ''
#     d[0] = ''
#
#     return d
# def create_workshops_activities_dict():
#     rows = db().select(db.workshops_activities.id,
#                        db.workshops_activities.Activity,
#                        cache=(cache.ram, 15))
#     d = dict()
#     for row in rows:
#         d[row.id] = row.Activity
#     d[None] = T("Full workshop")
#     d[0] = T("Full workshop")
#
#     return d

# the tables below here need to be defined first because of dependencies

# set global values for tables

permissions = ['create', 'read', 'update', 'delete', 'select']

# end global values for tables


def define_sys_accounting():
    db.define_table('sys_accounting',
        Field('auth_user_id', db.auth_user),
        Field('table_name'),
        Field('record_id'),
        Field('record_data', 'text'),
        Field('action_name'),
        Field('action_time', 'datetime',
            readable=False,
            writable=False,
            default=TODAY_LOCAL),
    )

#TODO: log deletion of records

def define_sys_organizations():
    db.define_table('sys_organizations',
        Field('DefaultOrganization', 'boolean',
            readable=False,
            writable=False,
            default=False,
            label=T('Default')),
        Field('Archived', 'boolean',
            readable=False,
            writable=False,
            default=False),
        Field('Name',
            requires=IS_NOT_EMPTY(),
            label=T('Organization')),
        Field('Address', 'text',
            requires=IS_NOT_EMPTY(),
            label=T('Address')),
        Field('Phone',
            label=T('Phone')),
        Field('Email',
            requires=IS_EMPTY_OR(IS_EMAIL()),
            label=T('Email')),
        Field('Registration',
            label=T('Company Registration'),
            comment=T('Eg. Chamber of commerce: 12345')),
        Field('TaxRegistration',
            label=T('Tax Registration Number'),
            comment=T('Eg. VAT number')),
        Field('TermsConditionsURL',
            requires=IS_EMPTY_OR(IS_URL()),
            label=T('Link to Terms & Conditions')),
        Field('TermsConditionsVersion',
            label=T('Terms & Conditions version')),
        Field('PrivacyNoticeURL',
            requires=IS_EMPTY_OR(IS_URL()),
            label=T('Link to Privacy notice')),
        Field('PrivacyNoticeVersion',
            label=T('Privacy notice version')),
        Field('ReportsClassPrice', 'float',
            readable=False,
            writable=False,
            represent=represent_float_as_amount,
            label=T('Resolve class price'),
            comment=T('Class price used when a customer from another organization takes a class')),
        format='%(Name)s')


def define_sys_properties():
    db.define_table('sys_properties',
        Field('Property', required=True,
            requires=IS_NOT_EMPTY(),
            label=T("Property")),
        Field('PropertyValue', 'text', required=True,
            requires=IS_NOT_EMPTY(),
            label=T("Value")),
        format='%(Property)s')


def define_sys_email_templates():
    db.define_table('sys_email_templates',
        Field('Name',
              label=T('Name')),
        Field('Title',
              label=T('Title')),
        Field('Description',
              label=T('Description')),
        Field('TemplateContent',
              label=T('Content'))
    )


def define_sys_notifications():
    db.define_table("sys_notifications",
        Field("Notification",
              requires=IS_NOT_EMPTY(),
              label= T('Notification')),
        Field('NotificationTitle',
              requires=IS_NOT_EMPTY(),
              label= T("Notifications Title")),
        Field('NotificationTemplate',
              requires=IS_NOT_EMPTY(),
              label= T("Notifications Title")),
    )


def define_sys_notifications_email():
    db.define_table('sys_notifications_email',
        Field('sys_notifications_id',
              db.sys_notifications,
              readable=False,
              writable=False,
              requires=IS_NOT_EMPTY()
              ),
        Field('Email',
              requires= IS_EMAIL(),
              label= T('Email')))


def define_sys_api_users():
    db.define_table('sys_api_users',
        Field('ActiveUser', 'boolean', required=True,
            readable=False,
            writable=False,
            default=True,
            label=T("Active")),
        Field('Username', required=True,
            requires=IS_NOT_IN_DB(db, 'sys_api_users.Username'),
            label=T("Username")),
        Field('Description', required=True,
            requires=IS_NOT_EMPTY(),
            label=T("Description")),
        Field('APIKey', required=True,
            writable=False,
            requires=IS_NOT_EMPTY(),
            label=T("Key")),
        )


def represent_accounting_costcenter(value, row):
    """
        Returns name for a tax rate
    """
    name = ''
    if value:
        name = db.accounting_costcenters(value).Name

    return name


def define_accounting_costcenters():
    db.define_table('accounting_costcenters',
        Field('Archived', 'boolean',
            readable=False,
            writable=False,
            default=False,
            label=T("Archived")),
        Field('Name',
            requires=IS_NOT_EMPTY(),
            label=T("Name")),
        Field('AccountingCode',
            label=T("Accounting code"),
            represent=lambda value, row: value or '',
            comment=T("Cost center code in your accounting software")),
        format='%(Name)s')


def represent_accounting_glaccount(value, row):
    """
        Returns name for a tax rate
    """
    name = ''
    if value:
        name = db.accounting_glaccounts(value).Name

    return name


def define_accounting_glaccounts():
    db.define_table('accounting_glaccounts',
        Field('Archived', 'boolean',
            readable=False,
            writable=False,
            default=False,
            label=T("Archived")),
        Field('Name',
            requires=IS_NOT_EMPTY(),
            label=T("Name")),
        Field('AccountingCode',
            label=T("Accounting code"),
            represent=lambda value, row: value or '',
            comment=T("General ledger account code in your accounting software")),
        format='%(Name)s')


def define_accounting_cashbooks_cash_count():
    auth_user_query = (db.auth_user.id > 1) & \
                      (db.auth_user.trashed == False) & \
                      ((db.auth_user.teacher == True) |
                       (db.auth_user.employee == True))

    try:
        auth_user_id_default = auth.user.id
    except AttributeError:
        auth_user_id_default = None  # default to None when not signed in

    db.define_table('accounting_cashbooks_cash_count',
        Field('CountDate', 'date',
            readable=False,
            writable=False),
        Field('CountType',
            readable=False,
            writable=False,
            default='opening',
            requires=IS_IN_SET([
              ['opening', T("Opening balance")],
              ['closing', T("Closing balance")]
            ]),
            label=T("Balance type") ),
        Field('Amount', 'double',
            represent=represent_float_as_amount,
            default=0,
            label=T("Amount")),
        Field('Note', 'text',
            label=T("Note")),
        Field('auth_user_id', db.auth_user,
            readable=False,
            writable=False,
            default=auth_user_id_default,
            requires=IS_EMPTY_OR(IS_IN_DB(db(auth_user_query),
                                          'auth_user.id',
                                          '%(first_name)s %(last_name)s',
                                          zero=T("Unassigned")))),
        Field('CreatedOn', 'datetime',
              readable=False,
              writable=False,
              default=datetime.datetime.now()),
    )

#
# def define_accounting_cashbooks_additional_items():
#     db.define_table('accounting_cashbooks_additional_items',
#         Field('BookingDate', 'date',
#             readable=False,
#             writable=False,
#             represent=represent_date),
#         Field('BookingType',
#             readable=False,
#             writable=False,
#             requires=IS_IN_SET([
#               ['debit', T("Debit / In")],
#               ['credit', T("Credit / Out")]
#             ])),
#         Field('Amount', 'double',
#             represent=represent_float_as_amount,
#             default=0,
#             label=T("Amount")),
#         Field('Description',
#               requires=IS_NOT_EMPTY(),
#               label=T("Description")),
#     )


def define_accounting_expenses():
    auth_user_query = (db.auth_user.id > 1) & \
                      (db.auth_user.trashed == False) & \
                      ((db.auth_user.teacher == True) |
                       (db.auth_user.employee == True))
    ac_query = (db.accounting_costcenters.Archived == False)
    ag_query = (db.accounting_glaccounts.Archived == False)

    try:
        auth_user_id_default = auth.user.id
    except AttributeError:
        auth_user_id_default = None  # default to None when not signed in

    db.define_table('accounting_expenses',
        Field('BookingDate', 'date',
              default=TODAY_LOCAL,
              requires=IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                        minimum=datetime.date(1900, 1, 1),
                                        maximum=datetime.date(2999, 1, 1)),
              represent=represent_date,
              label=T("Booking date")),
        Field('Amount', 'double',
              represent=represent_float_as_amount,
              default=0,
              label=T("Amount")),
        Field('tax_rates_id', db.tax_rates,
              represent=represent_tax_rate,
              label=T('Tax rate')),
        Field('YourReference',
              label=T("Your reference"),
              comment=T("eg. The invoice or receipt number of a delivery from your supplier")),
        Field('Description',
              requires=IS_NOT_EMPTY(),
              label=T("Description")),
        Field('accounting_glaccounts_id', db.accounting_glaccounts,
              requires=IS_EMPTY_OR(IS_IN_DB(db(ag_query),
                                            'accounting_glaccounts.id',
                                            '%(Name)s')),
              represent=represent_accounting_glaccount,
              label=T('G/L Account'),
              comment=T('General ledger account ID in your accounting software')),
        Field('accounting_costcenters_id', db.accounting_costcenters,
              requires=IS_EMPTY_OR(IS_IN_DB(db(ac_query),
                                            'accounting_costcenters.id',
                                            '%(Name)s')),
              represent=represent_accounting_costcenter,
              label=T("Cost center"),
              comment=T("Cost center code in your accounting software")),
        Field('Note', 'text',
              label=T("Note")),
        Field('auth_user_id', db.auth_user,
              readable=False,
              writable=False,
              default=auth_user_id_default,
              requires=IS_EMPTY_OR(IS_IN_DB(db(auth_user_query),
                                            'auth_user.id',
                                            '%(first_name)s %(last_name)s',
                                            zero=T("Unassigned")))),
        Field('CreatedOn', 'datetime',
              readable=False,
              writable=False,
              default=datetime.datetime.now()),
    )


def define_payment_methods():
    db.define_table('payment_methods',
        Field('Archived', 'boolean',
            readable=False,
            writable=False,
            default=False,
            label=T("Archived")),
        Field('SystemMethod', 'boolean',
            readable=False,
            writable=False,
            default=False,
            label=T('System method (OpenStudio defined)')),
        Field('Name',
            requires=IS_NOT_EMPTY(),
            label=T("Name")),
        Field('AccountingCode',
            represent=lambda value, row: value or '',
            label=T("Accounting code"),
            comment=T("Payment method/condition code in your accounting software.")),
        format='%(Name)s')


def define_announcements():
    priorities = get_priorities()

    db.define_table('announcements',
        Field('Visible', 'boolean', required=True,
            default=True,
            label=T("Display")),
        Field('Title', required=True,
            requires=IS_NOT_EMPTY(),
            label=T("Title")),
        Field('Note', 'text', required=True,
            requires=IS_NOT_EMPTY(),
            label=T("Message")),
        Field('Startdate', 'date', required=True,
            requires=IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                      minimum=datetime.date(1900,1,1),
                                      maximum=datetime.date(2999,1,1)),
            default=TODAY_LOCAL,
            label=T("Notification from"),
            widget=os_datepicker_widget),
        Field('Enddate', 'date', required=False,
            requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                      minimum=datetime.date(1900,1,1),
                                      maximum=datetime.date(2999,1,1))),
            represent=represent_date,
            label=T("Notification until"),
            widget = os_datepicker_widget),
        Field('Priority', 'integer',
            requires=IS_IN_SET(priorities, zero=None),
            default=2,
            represent=NRtoPriority,
            label=T("Priority")),
        )

def define_tasks():
    auth_user_query = (db.auth_user.id > 1) & \
                      (db.auth_user.trashed == False) & \
                      ((db.auth_user.teacher == True) |
                       (db.auth_user.employee == True))
    auth_cu_query = (db.auth_user.customer == True)
    priorities = get_priorities()

    try:
        auth_user_id_default = auth.user.id
    except AttributeError:
        auth_user_id_default = None # default to None when not signed in

    db.define_table('tasks',
        Field('auth_customer_id', db.auth_user, readable=False, writable=False,
            requires=IS_EMPTY_OR(
                IS_IN_DB(auth_cu_query,
                         'auth_user.id','%(first_name)s %(last_name)s')),
            label=T("Customer")),
        Field('workshops_id', db.workshops, readable=False, writable=False,
            #represent=lambda value, row: workshops_dict.get(value, ''),
            requires=IS_EMPTY_OR(IS_IN_DB(db,'workshops.id','%(Name)s'))),
        Field('Finished', 'boolean', required=True,
            readable=False,
            writable=False,
            default=False,
            label=T("Finished")),
        Field('Task', required=True,
            requires=IS_NOT_EMPTY(),
            label=T("Task")),
        Field('Description', 'text',
            label=T("Description")),
        Field('Duedate', 'date', required=False,
            default=TODAY_LOCAL,
            requires=IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                      minimum=datetime.date(1900,1,1),
                                      maximum=datetime.date(2999,1,1)),
            represent=represent_date,
            label=T("Due"),
            widget=os_datepicker_widget),
        Field('Priority', 'integer', readable=False,
            requires=IS_IN_SET(priorities, zero=None),
            default=2,
            represent=NRtoPriority,
            label=T("Priority")),
        Field('auth_user_id', db.auth_user,
            requires=IS_EMPTY_OR(IS_IN_DB(db(auth_user_query),
                                          'auth_user.id',
                                          '%(first_name)s %(last_name)s',
                                          zero=T("Unassigned"))),
            default=auth_user_id_default,
            represent=tasks_represent_user,
            label=T("Assign to"))
        )


def tasks_represent_user(value, row):
    """
        returns first_name last_name for user or "Unassigned" when no
        user id is assigned
    """
    auth_user = db.auth_user(value)
    if auth_user is None:
        return_value = os_gui.get_label('danger', T("Unassigned"))
    else:
        return_value = SPAN(auth_user.first_name, ' ', auth_user.last_name)

    return return_value


def define_school_languages():
    db.define_table('school_languages',
        Field('Archived', 'boolean',
            readable=False,
            writable=False,
            default=False,
            label=T("Archived")),
        Field('Name', required=True,
            requires=IS_NOT_EMPTY(),
            label=T("Name")),
        format='%(Name)s')


def define_school_classtypes():
    db.define_table('school_classtypes',
        Field('Archived', 'boolean',
            readable=False,
            writable=False,
            default=False,
            label=T("Archived")),
        Field('AllowAPI', 'boolean',
              default=True,
              required=True,
              label=T('Public')),
        Field('picture', 'upload', autodelete=True,
            requires=IS_EMPTY_OR([IS_IMAGE(extensions=('jpeg', 'jpg', 'png')),
                                           IS_LENGTH(maxsize=4194304)]),
            label=T("Image")),
        Field('thumbsmall', 'upload', # generate 50*50 for list view
            autodelete=True, writable=False,
            compute = lambda row: SMARTHUMB(row.picture,
                                            (50, 50),
                                             name="Small"),
            represent = represent_classtype_thumbsmall,
            label=T("Image")),
        Field('thumblarge', 'upload', # generate 400*400 for edit view
            autodelete=True, writable=False,
            compute = lambda row: SMARTHUMB(row.picture,
                                             (400, 400),
                                             name="Large")),
        Field('Name', required=True,
            requires=IS_NOT_EMPTY(),
            label=T("Name")),
        Field('Link',
            represent=lambda value, row: value or '',
            label=T("Link to Description"),
            comment=T("Link to description on your website. Start with 'http:// or https://'")),
        Field('Description', 'text',
            represent=lambda value, row: value or '',
            label=T("Description")),
        format='%(Name)s')


def define_school_shifts():
    db.define_table('school_shifts',
        Field('Archived', 'boolean',
            readable=False,
            writable=False,
            default=False,
            label=T("Archived")),
        Field('Name', required=True,
            requires=IS_NOT_EMPTY(),
            label=T("Name")),
        format='%(Name)s')


def define_school_discovery():
    db.define_table('school_discovery',
        Field('Archived', 'boolean',
            readable=False,
            writable=False,
            default=False,
            label=T("Archived")),
        Field('Name', required=True,
            requires=IS_NOT_EMPTY(),
            label=T("Name")),
        format='%(Name)s')


def define_school_locations():
    db.define_table('school_locations',
        Field('Archived', 'boolean',
            readable=False,
            writable=False,
            default=False,
            label=T("Archived")),
        Field('Name', required=True,
            requires=IS_NOT_EMPTY(),
            label=T("Name")),
        Field('AllowAPI', 'boolean', required=True,
            default=False,
            label=T("Public"),
            ## tooltip
            comment = T("When the API is in use, this checkbox defines whether a \
                    location is available over the API."),
                 ),
        format='%(Name)s'
    )


def define_school_classcards():
    ac_query = (db.accounting_costcenters.Archived == False)
    ag_query = (db.accounting_glaccounts.Archived == False)
    so_query = (db.sys_organizations.Archived == False)
    sm_query = (db.school_memberships.Archived == False)
    format = '%(Name)s'
    # if len(ORGANIZATIONS) > 2:
    #     format = '%(Name)s - %(sys_organizations_id)s'


    db.define_table('school_classcards',
        Field('Archived', 'boolean',
            readable=False,
            writable=False,
            default=False,
            label=T("Archived")),
        Field('PublicCard', 'boolean',
              default=True,
              required=True,
              label=T('Show in shop')),
        # Field('MembershipRequired', 'boolean',
        #       default=False,
        #       label=T('Requires membership')),
        Field('Trialcard', 'boolean',
              default=False,
              required=True,
              label=T('Trial card')),
        Field('sys_organizations_id', db.sys_organizations,
              readable=True if len(ORGANIZATIONS) > 2 else False,
              writable=True if len(ORGANIZATIONS) > 2 else False,
              requires=IS_EMPTY_OR(IS_IN_DB(db(so_query),
                                'sys_organizations.id',
                                '%(Name)s',
                                zero=T("All"))),
              # represent=lambda value, row: organizations_dict.get(value, T("No Organization")),
              label=T("Organization")),
        Field('Name', required=True,
            requires=[IS_NOT_EMPTY(), IS_LENGTH(minsize=1, maxsize=40)],
            label=T("Name")),
        Field('Description',
            represent=lambda value, row:  value or '',
            label=T('Description')),
        Field('Price', 'float', required=True,
            requires=IS_FLOAT_IN_RANGE(0,99999999, dot='.',
                error_message=T('Too small or too large')),
            #represent = lambda value, row: SPAN(CURRSYM , ' ', format(value, '.2f')),
            represent = represent_float_as_amount,
            label=T("Price incl. VAT")),
        Field('tax_rates_id', db.tax_rates,
            label=T('Tax rate')),
        Field('ValidityMonths', 'integer', # Legacy field
            readable=False,
            writable=False,
            default=0,
            requires=IS_INT_IN_RANGE(0,36,
                error_message=T("Please enter a value between 0 and 36.")),
            represent=lambda value, row:  value or '',
            label=T("Months valid")),
        Field('ValidityDays', 'integer', # Legacy field
            readable=False,
            writable=False,
            default=0,
            requires=IS_INT_IN_RANGE(0,365,
                error_message=T("Please enter a value between 0 and 365.")),
            represent=lambda value, row:  value or '',
            label=T("Days valid")),
        Field('Validity', 'integer',
            requires=IS_INT_IN_RANGE(1, 2000, error_message=T('Please enter a number between 0 and 2000')),
            label=T('Validity')),
        Field('ValidityUnit',
              requires=IS_IN_SET(VALIDITY_UNITS, zero=None),
              represent=represent_validity_units,
              label=T('Validity In')),
        Field('Classes', 'integer', required=False,
            represent=represent_school_classcards_classes,
            label=T("Classes")),
        Field('Unlimited', 'boolean',
            readable=False,
            default=False,
            label=T("Unlimited classes"),
            comment=T('For unlimited cards the number of classes entered is ignored')),
        Field('school_memberships_id', db.school_memberships,
              requires=IS_EMPTY_OR(IS_IN_DB(db(sm_query),
                                            'school_memberships.id',
                                            '%(Name)s',
                                            zero=T("Doesn't require membership"))),
              label=T("Requires membership"),
              comment=T(
                  "Set a required membership for this card. Without this memberships customers won't be able to buy this card or use it to attend classes.")),
        Field('QuickStatsAmount', 'double',
              label=T('Quick Stats Amount'),
              default=0,
              comment=T(
                  "Only used for unlimited cards. As it's impossible to know the exact revenue for each class until the end of the card. This amount will be used to create rough estimates of class revenue.")
              ),
        Field('accounting_glaccounts_id', db.accounting_glaccounts,
              requires=IS_EMPTY_OR(IS_IN_DB(db(ag_query),
                                            'accounting_glaccounts.id',
                                            '%(Name)s')),
              represent=represent_accounting_glaccount,
              label=T('G/L Account'),
              comment=T('General ledger account ID in your accounting software')),
        Field('accounting_costcenters_id', db.accounting_costcenters,
              requires=IS_EMPTY_OR(IS_IN_DB(db(ac_query),
                                            'accounting_costcenters.id',
                                            '%(Name)s')),
              represent=represent_accounting_costcenter,
              label=T("Cost center"),
              comment=T("Cost center code in your accounting software")),
        format=format)


def represent_school_classcards_classes(value, row):
    """
    :param value: db.school_classcards.Classes
    :param row: db.school_classcards
    :return: representation for db.school_classcards.Classes
    """
    if row.Unlimited:
        return T('Unlimited')
    elif not row.Unlimited and not row.Classes:
        return SPAN(T('Invalid'), _title=T("Invalid settings - no classes defined. A card should either have classes or be unlimited."))
    else:
        return value


def define_school_classcards_groups():
    """
        Table to hold classcard groups
    """
    db.define_table('school_classcards_groups',
        Field('Name',
              requires=IS_NOT_EMPTY(),
              label=T('Name')),
        Field('Description', 'text',
              label=T('Description')),
        format='%(Name)s',
    )


def define_school_classcards_groups_classcards():
    """
         Table to hold subscriptions in a subscriptions group
    """
    db.define_table('school_classcards_groups_classcards',
        Field('school_classcards_groups_id', db.school_classcards_groups,
            required=True,
            readable=False,
            writable=False,
            label=T('Class card group')),
        Field('school_classcards_id', db.school_classcards,
            required=True,
            label=T('Class card')),
    )


def define_school_memberships():
    ac_query = (db.accounting_costcenters.Archived == False)
    ag_query = (db.accounting_glaccounts.Archived == False)

    db.define_table('school_memberships',
        Field('Archived', 'boolean',
            readable=False,
            writable=False,
            default= False,
            label=T("Archived")),
        Field('PublicMembership', 'boolean',
              default=False,
              label=T('Show in shop')),
        Field('Name', required=True,
            requires= IS_NOT_EMPTY(),
            label= T("Name")),
        Field('Description',
             label=T('Description')),
        Field('Price', 'float', required=True,
              requires=IS_FLOAT_IN_RANGE(0, 99999999, dot='.',
                                         error_message=T('Too small or too large')),
              # represent = lambda value, row: SPAN(CURRSYM , ' ', format(value, '.2f')),
              represent=represent_float_as_amount,
              label=T("Price incl. VAT")),
        Field('tax_rates_id', db.tax_rates,
              represent=represent_tax_rate,
              label=T('Tax rate')),
        Field('Validity', 'integer',
              requires=IS_INT_IN_RANGE(1, 2000,
                                       error_message=T('Please enter a number between 0 and 2000')),
              label=T('Validity')),
        Field('ValidityUnit',
              requires=IS_IN_SET(VALIDITY_UNITS, zero=None),
              represent=represent_validity_units,
              label=T('Validity In')),
        Field('Terms', 'text',
              label=T('Terms & conditions')),
        Field('accounting_glaccounts_id', db.accounting_glaccounts,
              requires=IS_EMPTY_OR(IS_IN_DB(db(ag_query),
                                            'accounting_glaccounts.id',
                                            '%(Name)s')),
              represent=represent_accounting_glaccount,
              label=T('G/L Account'),
              comment=T('General ledger account ID in your accounting software')),
        Field('accounting_costcenters_id', db.accounting_costcenters,
              requires=IS_EMPTY_OR(IS_IN_DB(db(ac_query),
                                            'accounting_costcenters.id',
                                            '%(Name)s')),
              represent=represent_accounting_costcenter,
              label=T("Cost center"),
              comment=T("Cost center code in your accounting software")),
        format='%(Name)s'
        )


def define_school_subscriptions():
    so_query = (db.sys_organizations.Archived == False)
    sm_query = (db.school_memberships.Archived == False)
    format = '%(Name)s'
    # if len(ORGANIZATIONS) > 2:
    #     format = '%(Name)s - %(sys_organizations_id)s'

    db.define_table('school_subscriptions',
        Field('Archived', 'boolean',
            readable=False,
            writable=False,
            default=False,
            label=T("Archived")),
        Field('ShopSubscription', 'boolean',
            default=False,
            label=T('Show in shop'),
            comment=T("Show this subscription in the OpenStudio shop, allowing your customers to buy it online.")),
        Field('PublicSubscription', 'boolean',
            default=False,
            label=T('Show on website'),
            comment=T("Show on website when OpenStudio subscriptions are integrated in your website.")),
        Field('Name', required=True,
              requires=IS_NOT_EMPTY(),
              label=T("Name")),
        Field('Description',
              label=T('Description')),
        Field('SortOrder', 'integer',
            requires=IS_INT_IN_RANGE(0, 5001, error_message=T('Enter a number between 0 and 5000')),
            default=0,
            label=T('Sort order'),
            comment=T("Order in which subscriptions are shown in the OpenStudio shop. Higher is shown first. Subscriptions with the same sort order number are sorted by name."),
            ),
        Field('sys_organizations_id', db.sys_organizations,
              readable=True if len(ORGANIZATIONS) > 2 else False,
              writable=True if len(ORGANIZATIONS) > 2 else False,
              requires=IS_EMPTY_OR(IS_IN_DB(db(so_query),
                                'sys_organizations.id',
                                '%(Name)s',
                                zero=T("All"))),
              # represent=lambda value, row: organizations_dict.get(value, T("No Organization")),
              label=T("Organization")),
        Field('NRofClasses', 'integer', required=False, # legacy field
            readable=False,
            writable=False,
            default=0,
            #represent=lambda value, row:  value or T('Unlimited'),
            label=T("Weekly classes")),
        Field('MonthlyClasses', 'integer', required=False, # legacy field
            readable=False,
            writable=False,
            default=0,
            #represent=lambda value, row:  value or T('Unlimited'),
            label=T('Monthly Classes')),
        Field('MinDuration', 'integer',
            default=1,
            represent=represent_school_subscriptions_minduration,
            label=T("Minimum duration"),
            comment=T("Minimum duration of this subscription in months")),
        Field('Classes', 'integer', required=False,
            requires=IS_INT_IN_RANGE(1, 201, error_message=T("Please enter a number between 1 and 200")),
            represent=represent_school_subscriptions_classes, # return Unlimited instead of number if row.Unlimited
            label=T("Classes")),
        Field('SubscriptionUnit',
            requires=IS_IN_SET(SUBSCRIPTION_UNITS, zero=None),
            represent=represent_subscription_units,
            label=T('Classes per')),
        Field('ReconciliationClasses', 'integer',
            label=T('Reconciliation Classes'),
            default=0,
            requires=IS_INT_IN_RANGE(0, 101),
            comment=T("Number of classes a customer can take without credits on this subscription.")),
        Field('CreditValidity', 'integer',
            label=T('Credit validity (days)'),
            requires=IS_EMPTY_OR(IS_INT_IN_RANGE(0, 735)),
            comment=T("Subscription credit expiration, in days. Leave empty for unlimited validity.")),
        Field('Unlimited', 'boolean',
            default=False,
            readable=False,
            label=T('Unlimited classes')),
        Field('Terms', 'text',
            label=T('Terms & conditions')),
        Field('school_memberships_id', db.school_memberships,
              requires=IS_EMPTY_OR(IS_IN_DB(db(sm_query),
                                            'school_memberships.id',
                                            '%(Name)s',
                                            zero=T("Doesn't require membership"))),
              label=T("Requires membership"),
              comment=T(
                  "Set a required membership for this card. Without this memberships customers won't be able to get this subscription or use it to attend classes.")),
        Field('QuickStatsAmount', 'double',
              label=T('Quick Stats Amount'),
              default=0,
              comment=T("As for subscription it's impossible to know the exact revenue for each class until the end of the month. This amount will be used to create rough estimates of class revenue.")
              ),
        Field('RegistrationFee', 'double',
              label=T('Registration Fee'),
              default = 0,
              comment=T("This Amount will be added to the first invoice for this subscription. Set to 0 for no registration fee."),
              ),
        Field('CountSold', 'integer',
            # Field to hold count of grouped sold customer subscriptions
            # Workaround for not being able to have count = db.school_subscriptions.id.count() in
            # fields = [] when using execute sql
            readable=False,
            writable=False),
        format=format)


def represent_school_subscriptions_minduration(value, row):
    """
    :param value: db.school_subscriptions.MinDuration
    :param row: db.school_subscriptions record
    :return:
    """
    month_str = T("%s Months" % value)
    if value == 1:
        month_str = T("%s Month" % value)

    return month_str


def represent_school_subscriptions_classes(value, row):
    """
    :param value: db.school_classcards.Classes
    :param row: db.school_classcards
    :return: representation for db.school_classcards.Classes
    """
    if row.Unlimited:
        return T('Unlimited')
    else:
        return value


def define_school_subscriptions_groups():
    """
        Table to hold subscription groups
    """
    db.define_table('school_subscriptions_groups',
        Field('Name',
              requires=IS_NOT_EMPTY(),
              label=T('Name')),
        Field('Description', 'text',
              label=T('Description')),
        format='%(Name)s',
    )


def define_school_subscriptions_groups_subscriptions():
    """
         Table to hold subscriptions in a subscriptions group
    """
    db.define_table('school_subscriptions_groups_subscriptions',
        Field('school_subscriptions_groups_id', db.school_subscriptions_groups,
            required=True,
            readable=False,
            writable=False,
            label=T('Subscription group')),
        Field('school_subscriptions_id', db.school_subscriptions,
            required=True,
            label=T('Subscription')),
    )


def define_school_subscriptions_price():
    today = TODAY_LOCAL
    ac_query = (db.accounting_costcenters.Archived == False)
    ag_query = (db.accounting_glaccounts.Archived == False)

    db.define_table('school_subscriptions_price',
        Field('school_subscriptions_id', db.school_subscriptions,
            required=True,
            readable=False,
            writable=False),
        Field('Startdate', 'date', required=True,
            requires=IS_DATE_IN_RANGE(format=DATE_FORMAT,
                       minimum=datetime.date(2000,1,1),
                       maximum=datetime.date(2999,12,31)),
            represent=represent_date,
            default=datetime.date(today.year, today.month, 1),
            widget=os_datepicker_widget),
        Field('Enddate', 'date',
            requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format=DATE_FORMAT,
                       minimum=datetime.date(2000,1,1),
                       maximum=datetime.date(2999,12,31))),
            represent=represent_date,
            widget=os_datepicker_widget),
        Field('Price', 'float', required=True,
            requires=IS_FLOAT_IN_RANGE(0,99999999, dot='.',
                error_message=T('Too small or too large')),
            represent = represent_float_as_amount,
            label=T("Monthly Fee incl VAT")),
        Field('tax_rates_id', db.tax_rates,
            label=T('Tax rate')),
        Field('accounting_glaccounts_id', db.accounting_glaccounts,
              requires=IS_EMPTY_OR(IS_IN_DB(db(ag_query),
                                            'accounting_glaccounts.id',
                                            '%(Name)s')),
              represent=represent_accounting_glaccount,
              label=T('G/L Account'),
              comment=T('General ledger account ID in your accounting software')),
        Field('accounting_costcenters_id', db.accounting_costcenters,
              requires=IS_EMPTY_OR(IS_IN_DB(db(ac_query),
                                            'accounting_costcenters.id',
                                            '%(Name)s')),
              represent=represent_accounting_costcenter,
              label=T("Cost center"),
              comment=T("Cost center code in your accounting software")),
        )


def define_payment_categories():
    types_dict = {0:T("Collection"),1:T("Payment")}
    db.define_table('payment_categories',
        Field('Archived', 'boolean',
            readable=False,
            writable=False,
            default=False,
            label=T("Archived")),
        Field('Name', required=True,
            requires=IS_NOT_EMPTY(),
            label=T("Name")),
        Field('CategoryType', 'integer', required=True,
            requires=IS_IN_SET(types_dict, zero=T("Please select...")),
            represent=lambda value, row: types_dict.get(value, ""),
            label=T("Type")),
        format='%(Name)s')


def define_school_levels():
    db.define_table('school_levels',
        Field('Archived', 'boolean',
            readable=False,
            writable=False,
            default=False,
            label=T("Archived")),
        Field('Name', required=True, requires=IS_NOT_EMPTY(), label=T("Name")),
        format='%(Name)s')


def define_teachers_holidays():
    au_query = (db.auth_user.trashed == False) & \
               ((db.auth_user.teacher == True) |
                (db.auth_user.employee == True))

    db.define_table('teachers_holidays',
        Field('auth_teacher_id', db.auth_user,
            requires=IS_IN_DB(db(au_query),
                              'auth_user.id',
                              '%(first_name)s %(last_name)s',
                              zero=(T('Select employee...'))),
            #represent=lambda value, row: teachers_dict.get(value, None),
            #represent=lambda value, row: value or '',
            label=T("Employee")),
        Field('Startdate', 'date', required=True,
            requires=IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                      minimum=datetime.date(1900,1,1),
                                      maximum=datetime.date(2999,1,1)),
            represent=represent_date,
            label=T("Start date"),
            widget=os_datepicker_widget),
        Field('Enddate', 'date', required=False,
            requires=IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                  minimum=datetime.date(1900,1,1),
                                  maximum=datetime.date(2999,1,1)),
            represent=represent_date, label=T("End date"),
            widget=os_datepicker_widget),
        Field('Note', 'text', required=True,
            requires=IS_NOT_EMPTY()),
        Field('CreatedOn', 'datetime',
              readable=False,
              writable=False,
              default=datetime.datetime.now())
        )


def define_teachers_payment_fixed_rate_default():
    db.define_table('teachers_payment_fixed_rate_default',
        Field('auth_teacher_id', db.auth_user,
              readable=False,
              writable=False),
        Field('ClassRate', 'double',
              requires=IS_FLOAT_IN_RANGE(0, 99999999, dot='.',
                                         error_message=T('Too small or too large')),
              represent=represent_float_as_amount,
              label=T("Class Rate excl. VAT")),
        Field('tax_rates_id', db.tax_rates,
            label=T('Tax rate')),
    )


def define_teachers_payment_fixed_rate_class():
    db.define_table('teachers_payment_fixed_rate_class',
        Field('auth_teacher_id', db.auth_user,
              readable=False,
              writable=False),
        Field('classes_id', db.classes,
              readable=False,
              writable=False),
        Field('ClassRate', 'double',
              requires=IS_FLOAT_IN_RANGE(0, 99999999, dot='.',
                                         error_message=T('Too small or too large')),
              represent=represent_float_as_amount,
              label=T("Class Rate excl. VAT")),
        Field('tax_rates_id', db.tax_rates,
            label=T('Tax rate')),
    )


def define_teachers_payment_fixed_rate_travel():
    loc_query = (db.school_locations.Archived == False)

    db.define_table('teachers_payment_fixed_rate_travel',
        Field('auth_teacher_id', db.auth_user,
              readable=False,
              writable=False),
        Field('school_locations_id', db.school_locations, required=True,
              requires=IS_IN_DB(db(loc_query),
                                'school_locations.id',
                                '%(Name)s',
                                zero=T("Please select...")),
              represent=lambda value, row: locations_dict.get(value, T("No location")),
              label=T("Location")),
        Field('TravelAllowance', 'double',
              requires=IS_FLOAT_IN_RANGE(0, 99999999, dot='.',
                                         error_message=T('Too small or too large')),
              represent=represent_float_as_amount,
              label=T("Travel Allowance excl. VAT")),
        Field('tax_rates_id', db.tax_rates,
            label=T('Tax rate')),
    )


def define_teachers_payment_travel():
    loc_query = (db.school_locations.Archived == False)

    db.define_table('teachers_payment_travel',
        Field('auth_teacher_id', db.auth_user,
              readable=False,
              writable=False),
        Field('school_locations_id', db.school_locations, required=True,
              requires=IS_IN_DB(db(loc_query),
                                'school_locations.id',
                                '%(Name)s',
                                zero=T("Please select...")),
              represent=lambda value, row: locations_dict.get(value, T("No location")),
              label=T("Location")),
        Field('TravelAllowance', 'double',
              requires=IS_FLOAT_IN_RANGE(0, 99999999, dot='.',
                                         error_message=T('Too small or too large')),
              represent=represent_float_as_amount,
              label=T("Travel Allowance excl. VAT")),
        Field('tax_rates_id', db.tax_rates,
            label=T('Tax rate')),

    )


def define_teachers_payment_attendance_lists():
    db.define_table('teachers_payment_attendance_lists',
        Field('Archived', 'boolean',
              readable=False,
              writable=False,
              default=False,
              label=T("Archived")),
        Field('Name',
              required=True,
              requires=IS_NOT_EMPTY(),
              label=T("Name")),
        Field('tax_rates_id', db.tax_rates,
              label=T('Tax rate'),
              comment=T("Tax rate applied to items in this list")),
        format='%(Name)s')


def define_teachers_payment_attendance_lists_rates():
    db.define_table('teachers_payment_attendance_lists_rates',
        Field('teachers_payment_attendance_lists_id',
              db.teachers_payment_attendance_lists,
              readable=False,
              writable=False,
              requires=IS_NOT_EMPTY()
              ),
        Field('AttendanceCount', 'integer',
              requires=IS_INT_IN_RANGE(0, 999999),
               label = T("Attendance Number"),
              writable=False
            ),
        Field('Rate','double',
              requires=IS_FLOAT_IN_RANGE(0, 99999999, dot='.',
                                         error_message=T('Too small or too large')),
              label=T("Attendance List Rate excl. VAT"),
              ),
        )


def define_teachers_payment_attendance_lists_school_classtypes():
    db.define_table('teachers_payment_attendance_lists_school_classtypes',
        Field('teachers_payment_attendance_lists_id',
              db.teachers_payment_attendance_lists,
              readable=False,
              writable=False,
              requires=IS_NOT_EMPTY()),
        Field('school_classtypes_id',
              db.school_classtypes)
    )


def define_teachers_payment_classes():
    """

    """
    au_query = (db.auth_user.trashed == False) & \
               (db.auth_user.teacher == True) & \
               (db.auth_user.teaches_classes == True)

    db.define_table('teachers_payment_classes',
        Field('classes_id', db.classes),
        Field('ClassDate', 'date'),
        Field('Status',
              represent=represent_teachers_payment_classes_status,
              requires=IS_IN_SET(teacher_payment_classes_statuses)),
        Field('AttendanceCount', 'integer'),
        Field('auth_teacher_id', db.auth_user,
            requires=IS_IN_DB(db(au_query),
                              'auth_user.id',
                              '%(first_name)s %(last_name)s',
                              zero=(T('Select teacher...'))),
            represent=lambda value, row: teachers_dict.get(value, None),
            #represent=lambda value, row: value or '', # when this is enabled it the schedule returns id's instead of names
            label=T("Teacher")),
        Field('auth_teacher_id2', db.auth_user,
            requires=IS_EMPTY_OR(IS_IN_DB(db(au_query),
                                          'auth_user.id',
                                          '%(first_name)s %(last_name)s')),
            represent=lambda value, row: teachers_dict.get(value, None),
            #represent=lambda value, row: value or '',
            label=T("Teacher 2")),
        Field('ClassRate', 'double',
              represent=represent_float_as_amount),
        Field('RateType',
              readable=False,
              writable=False,
              requires=IS_IN_SET(teacher_payment_classes_rate_types),
              represent=represent_teachers_payment_classes_rate_type,
              label=T("RateType")),
        Field('teachers_payment_attendance_list_id', db.teachers_payment_attendance_lists,
              readable=False,
              writable=False),
        Field('tax_rates_id', db.tax_rates,
              readable=False,
              writable=False),
        Field('TravelAllowance', 'double',
              represent=represent_float_as_amount),
        Field('tax_rates_id_travel_allowance', db.tax_rates),
        Field('VerifiedBy', db.auth_user,
              readable=False,
              writable=False),
        Field('VerifiedOn', 'datetime',
              readable=False,
              writable=False),
        Field('UpdatedOn', 'datetime',
              readable=False,
              writable=False,
              compute=lambda row: datetime.datetime.now()),
        Field('CreatedOn', 'datetime',
              readable=False,
              writable=False,
              default=datetime.datetime.now())
    )


def define_customers_notes():
    db.define_table('customers_notes',
        Field('auth_customer_id', db.auth_user, # to link note to customer
              readable=False,
              writable=False),
        Field('auth_user_id', db.auth_user, # who made the note
              readable=False,
              writable=False),
        Field('BackofficeNote', 'boolean',
              readable=False,
              writable=False,
              default=False),
        Field('TeacherNote', 'boolean',
              readable=False,
              writable=False,
              default=False),
        Field('NoteDate', 'date', required=True,
              readable=False,
              writable=False,
              default=TODAY_LOCAL,
              requires=IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                      minimum=datetime.date(1900,1,1),
                                      maximum=datetime.date(2999,1,1)),
              represent=represent_date, label=T("Date"),
              widget=os_datepicker_widget),
        Field('NoteTime', 'time', required=True,
              readable=False,
              writable=False,
              default=datetime.datetime.now().time(),
              requires=IS_TIME(error_message='must be HH:MM:SS'),
              represent=lambda value, row: value.strftime('%H:%M')),
        Field('Note', 'text', required=True,
              requires=IS_NOT_EMPTY()),
        Field('Injury', 'boolean',
              default=False,
              label=T('This note describes an injury')),
        )


def define_alternativepayments():
    months = get_months_list()
    pc_query = (db.payment_categories.Archived == False)

    db.define_table('alternativepayments',
        Field('auth_customer_id', db.auth_user,
            readable=False,
            writable=False,
            label=T('CustomerID')),
        Field('PaymentYear', 'integer', required=True,
            default=TODAY_LOCAL.year,
            requires=IS_NOT_EMPTY(),
            label=T("Year")),
        Field('PaymentMonth', 'integer', required=True,
            requires=IS_IN_SET(months, zero=T("Please select...")),
            default=TODAY_LOCAL.month,
            represent=NRtoMonth,
            label=T("Month")),
        Field('Amount', 'double', required=True,
            requires=IS_NOT_EMPTY(),
            represent = lambda value, row: format(value, '.2f'),
            label=T("Amount")),
        Field('payment_categories_id', db.payment_categories,
            requires=IS_EMPTY_OR(IS_IN_DB(db(pc_query),
                                          'payment_categories.id',
                                          '%(Name)s',
                                          '%(CategoryType)s',
                                          zero=None)),
            represent=lambda value, row: paycat_dict.get(value, ""),
            label=T("Category")),
        Field('Description', 'text',
            requires=IS_NOT_EMPTY(),
            label=T("Description")),
        Field('CreatedOn', 'datetime',
              readable=False,
              writable=False,
              default=datetime.datetime.now()),
        singular=T("Alternative payment"), plural=T("Alternative payments")
        )


def define_classes_notes():
    db.define_table('classes_notes',
        Field('classes_id', db.classes, # to link note to a class
              readable=False,
              writable=False),
        Field('ClassDate', 'date', required=True,
              readable=False,
              writable=False,
              requires=IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                        minimum=datetime.date(1900,1,1),
                                        maximum=datetime.date(2999,1,1)),
              represent=represent_date,
              label=T("Class date"),
              widget=os_datepicker_widget),
        Field('auth_user_id', db.auth_user, # who made the note
              readable=False,
              writable=False),
        Field('BackofficeNote', 'boolean',
              readable=False,
              writable=False,
              default=False),
        Field('TeacherNote', 'boolean',
              readable=False,
              writable=False,
              default=False),
        Field('Note', 'text', required=True,
              requires=IS_NOT_EMPTY()),
        )


def define_employee_claims():
    db.define_table('employee_claims',
        Field('auth_user_id', db.auth_user,  # Employee that does the expenses
              required= True,
              readable=False,
              writable=False,
              label=T('Employee/Teacher')),
        Field('Amount', 'double',
              default=0,
              represent=represent_float_as_amount,
              label=T("Amount (incl. VAT)")),
        Field('Quantity', 'double',
              default=1,
              # represent=represent_float_as_amount,
              label=T("Quantity")),
        Field('tax_rates_id', db.tax_rates,
              label= T('Tax Rate')),
        Field('ClaimDate', 'datetime',
              default=NOW_LOCAL,
              readable= False,
              writable= False,
              represent=represent_datetime,
              label=T('Date')),
        Field('Description',
              label=T('Description')),
        Field('Attachment', 'upload', autodelete=True,
              requires=IS_EMPTY_OR([IS_IMAGE(extensions=('jpeg', 'jpg', 'png')),
                                    IS_LENGTH(maxsize=665600,
                                              error_message=T('650KB or less'))]),  # 650KB
              label=T("Attachment (Max 650KB)")),
        Field('Status',
              readable=False,
              writable=False,
              requires=IS_IN_SET(employee_expenses_statuses),
              represent=represent_employee_expenses_status,
              label=T("Status")),
        Field('VerifiedBy', db.auth_user,
              readable=False,
              writable=False),
        Field('VerifiedOn', 'datetime',
              readable=False,
              writable=False),
        )


def define_classes():
    weekdays = [('1',T('Monday')),
                ('2',T('Tuesday')),
                ('3',T('Wednesday')),
                ('4',T('Thursday')),
                ('5',T('Friday')),
                ('6',T('Saturday')),
                ('7',T('Sunday'))]

    loc_query = (db.school_locations.Archived == False)
    ct_query = (db.school_classtypes.Archived == False)
    sl_query = (db.school_levels.Archived == False)
    so_query = (db.sys_organizations.Archived == False)

    db.define_table('classes',
        Field('sys_organizations_id', db.sys_organizations,
              readable=True if len(ORGANIZATIONS) > 2 else False,
              writable=True if len(ORGANIZATIONS) > 2 else False,
              requires=IS_IN_DB(db(so_query),
                                'sys_organizations.id',
                                '%(Name)s',
                                zero=T("Please select...")),
              #represent=lambda value, row: organizations_dict.get(value, T("No Organization")),
              label=T("Organization")),
        Field('school_locations_id', db.school_locations, required=True,
            requires=IS_IN_DB(db(loc_query),
                              'school_locations.id',
                              '%(Name)s',
                              zero=T("Please select...")),
            represent=lambda value, row: locations_dict.get(value, T("No location")),
            label=T("Location")),
        Field('school_classtypes_id', db.school_classtypes, required=True,
            requires=IS_IN_DB(db(ct_query),
                              'school_classtypes.id',
                              '%(Name)s',
                              zero=T("Please select...")),
            represent=lambda value, row: classtypes_dict.get(value, T("No classtype")),
            label=T("Type")),
        Field('school_levels_id', db.school_levels, required=False,
            requires=IS_EMPTY_OR(IS_IN_DB(db(sl_query),
                                 'school_levels.id',
                                 '%(Name)s')),
            represent=lambda value, row: levels_dict.get(value, T("No level")),
            label=T("Level")),
        Field('Week_day', 'integer', required=True,
            requires=IS_IN_SET(weekdays),
            represent=NRtoDay,
            label=T("Weekday")),
        Field('Starttime', 'time', required=True,
            requires=IS_TIME(error_message='must be HH:MM'),
            represent=lambda value, row: value.strftime('%H:%M') if value else '',
            #widget=os_gui.get_widget_time,
            label=T("Start"),
            widget=os_time_widget),
        Field('Endtime', 'time', required=True,
            requires=IS_TIME(error_message='must be HH:MM'),
            represent=lambda value, row: value.strftime('%H:%M') if value else '',
            widget=os_time_widget,
            label=T("End")),
        Field('Startdate', 'date', required=True,
            requires=IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                      minimum=datetime.date(1900,1,1),
                                      maximum=datetime.date(2999,1,1)),
            represent=represent_date,
            label=T("Start date"),
            widget=os_datepicker_widget),
        Field('Enddate', 'date', required=False,
            requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                  minimum=datetime.date(1900,1,1),
                                  maximum=datetime.date(2999,1,1))),
            represent=represent_date,
            label=T("End date"),
            widget=os_datepicker_widget),
        Field('Maxstudents', 'integer', required=True,
            requires=IS_INT_IN_RANGE(0, 500),
            label=T("Spaces"),
            comment=T("Total spaces for this class. Should be greater then online booking and enrollment spaces added up.")),
        Field('MaxOnlineBooking', 'integer',
            requires=IS_INT_IN_RANGE(0, 500),
            label=T('Online booking spaces'),
            comment=T("Maximum number of online bookings accepted for this class")),
        Field('MaxReservationsRecurring', 'integer', # Used to set max. enrollments
            requires=IS_INT_IN_RANGE(0,500),
            default=0,
            label=T('Enrollment spaces'),
            comment=T("Maximum number of enrollments for this class")),
        Field('MaxReservationsDT', 'integer', # Depricated from 2017.3
            readable=False,
            writable=False,
            requires=IS_INT_IN_RANGE(0,500),
            default=0,
            label=T('Max. reservations - drop in / trial')),
        Field('AllowAPI', 'boolean', required=True,
            default=False,
            label=T("Public"),
            comment=T("When the API is in use, this checkbox defines whether \
                a class is passed to the website.")),
        Field('AllowShopTrial', 'boolean',
            default=False,
            label=T("Trial class in shop"),
            comment=T("Show trial class booking option in shop.")),
        Field('CreatedOn', 'datetime',
              readable=False,
              writable=False,
              default=datetime.datetime.now()),
        Field('CreatedBy', db.auth_user,
              readable=False,
              writable=False)
        )

    try:
        db.classes.CreatedBy.default = auth.user.id
    except AttributeError:
        pass


def define_classes_otc():
    """
        Define one time change table for classes
    """
    loc_query = (db.school_locations.Archived == False)
    ct_query = (db.school_classtypes.Archived == False)
    sl_query = (db.school_levels.Archived == False)
    au_query = (db.auth_user.trashed == False) & \
               (db.auth_user.teacher == True) & \
               (db.auth_user.teaches_classes == True)

    statuses = [['normal', T('Normal')],
                ['open', T('Open / Sub teacher required')],
                ['cancelled', T('Cancelled')]]

    db.define_table('classes_otc',
        Field('classes_id', db.classes, required=True,
            readable=False,
            writable=False),
        Field('ClassDate', 'date', required=True,
            readable=False,
            writable=False,
            requires=IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                      minimum=datetime.date(1900, 1, 1),
                                      maximum=datetime.date(2999, 1, 1)),
            represent=represent_date,
            label=T("Class date"),
            widget=os_datepicker_widget),
        Field('Status',
            requires=IS_EMPTY_OR(IS_IN_SET(statuses)),
            label=T('Status')),
        Field('Description',
            label=T('Description')),
        Field('school_locations_id', db.school_locations,
            requires=IS_EMPTY_OR(
                IS_IN_DB(db(loc_query),
                         'school_locations.id',
                         '%(Name)s',
                         zero=T(""))),
            represent=lambda value, row: locations_dict.get(value, T("No location")),
            label=T("Location")),
        Field('school_classtypes_id', db.school_classtypes,
            requires=IS_EMPTY_OR(
                IS_IN_DB(db(ct_query),
                         'school_classtypes.id',
                         '%(Name)s',
                         zero=T(""))),
            represent=lambda value, row: classtypes_dict.get(value, T("No classtype")),
            label=T("Type")),
        Field('Starttime', 'time',
            requires=IS_EMPTY_OR(IS_TIME(error_message='please insert as HH:MM')),
            represent=lambda value, row: value.strftime('%H:%M') if value else '',
            widget=os_time_widget,
            label=T("Start")),
        Field('Endtime', 'time',
            requires=IS_EMPTY_OR(IS_TIME(error_message='please insert as HH:MM')),
            represent=lambda value, row: value.strftime('%H:%M') if value else '',
            widget=os_time_widget,
            label=T("End")),
        Field('auth_teacher_id', db.auth_user,
              requires=IS_EMPTY_OR(IS_IN_DB(db(au_query),
                                   'auth_user.id',
                                   '%(first_name)s %(last_name)s',
                                   zero=(T('')))),
              represent=lambda value, row: teachers_dict.get(value,
                                                             None),
              # represent=lambda value, row: value or '',
              label=T("Sub teacher")),
        Field('teacher_role', 'integer',
              requires=IS_EMPTY_OR(IS_IN_SET(teachers_roles)),
              represent=represent_teacher_role,
              default=1,
              label=T('Sub teacher role')),
        Field('auth_teacher_id2', db.auth_user,
              requires=IS_EMPTY_OR(IS_IN_DB(db(au_query),
                                            'auth_user.id',
                                            '%(first_name)s %(last_name)s')),
              represent=lambda value, row: teachers_dict.get(value,
                                                             None),
              # represent=lambda value, row: value or '',
              label=T("Sub teacher 2")),
        Field('teacher_role2', 'integer',
              requires=IS_EMPTY_OR(IS_IN_SET(teachers_roles)),
              represent=represent_teacher_role,
              label=T('Sub teacher 2 role')),
        Field('Maxstudents', 'integer',
              requires=IS_EMPTY_OR(IS_INT_IN_RANGE(0, 500)),
              label=T("Spaces"),
              comment=os_gui.get_info_icon(
                  title=T("Total spaces for this class"),
                  btn_icon='info')),
        Field('MaxOnlineBooking', 'integer',
              requires=IS_EMPTY_OR(IS_INT_IN_RANGE(0, 500)),
              label=T('Online booking spaces'),
              comment=os_gui.get_info_icon(
                  title=T("Maximum number of online bookings accepted for this class"),
                  btn_icon='info')),
    )

def define_classes_otc_sub_avail():
    """
        Table to store the available requests for a class open to substitution
    """
    db.define_table('classes_otc_sub_avail',
        Field('classes_otc_id', db.classes_otc,
              label=T('Classes_OTC')),
        Field('auth_teacher_id', db.auth_user,
              label=T('Teacher')),
        Field('Accepted', 'boolean',
              label=T('Accepted'))
    )


def define_classes_school_subscriptions_groups():
    """
        Table to store which subscriptions have which access to a class
    """
    #TODO: Smart query for school_subscriptions_id, to check if it isn't in set classes_id + school_subscriptions_id for this table

    """
    something like this in the controller:
        db.classes_subscriptions.school_subscriptions_id.requires = IS_NOT_IN_DB(records)

    """
    db.define_table('classes_school_subscriptions_groups',
        Field('classes_id', db.classes,
              readable=False,
              writable=False),
        Field('school_subscriptions_groups_id', db.school_subscriptions_groups,
              label=T('Subscription group')),
        Field('Enroll', 'boolean',
              default=False,
              represent=represent_classes_subscriptions_group_boolean,
              label=T('Enrollment')),
        Field('ShopBook', 'boolean',
              default=False,
              represent=represent_classes_subscriptions_group_boolean,
              label=T('Book in advance'),
              comment=T('From the OpenStudio shop')),
        Field('Attend', 'boolean',
              default=True,
              represent=represent_classes_subscriptions_group_boolean,
              label=T('Attend')),
    )


def define_classes_school_classcards_groups():
    """
        Table to store which classcards have which access to a class
    """
    #TODO: Smart query for school_classcards_id, to check if it isn't in set classes_id + school_classcards_id for this table

    """
    something like this in the controller:
        db.classes_classcards.school_classcards_id.requires = IS_NOT_IN_DB(records)

    """
    db.define_table('classes_school_classcards_groups',
        Field('classes_id', db.classes,
              readable=False,
              writable=False),
        Field('school_classcards_groups_id', db.school_classcards_groups,
              label=T('classcard group')),
        Field('Enroll', 'boolean',
              readable=False,
              writable=False,
              default=False,
              represent=represent_classes_subscriptions_group_boolean,
              label=T('Enrollment')),
        Field('ShopBook', 'boolean',
              default=False,
              represent=represent_classes_subscriptions_group_boolean,
              label=T('Book in advance'),
              comment=T('From the OpenStudio shop')),
        Field('Attend', 'boolean',
              default=True,
              represent=represent_classes_subscriptions_group_boolean,
              label=T('Attend')),
    )


def represent_classes_subscriptions_group_boolean(value, row):
    return INPUT(value=value,
                 _type='checkbox',
                 _value='not_defined',
                 _disabled='disabled')


def define_classes_price():
    """
        Define prices for a class
    """
    ac_query = (db.accounting_costcenters.Archived == False)
    ag_query = (db.accounting_glaccounts.Archived == False)

    db.define_table('classes_price',
        Field('classes_id', db.classes, required=True,
            readable=False,
            writable=False),
        Field('Startdate', 'date', required=True,
            requires=IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                      minimum=datetime.date(1900,1,1),
                                      maximum=datetime.date(2999,1,1)),
            represent=represent_date,
            label=T("Start date"),
            widget=os_datepicker_widget),
        Field('Enddate', 'date', required=False,
            requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                 minimum=datetime.date(1900,1,1),
                                 maximum=datetime.date(2999,1,1))),
            represent=represent_date,
            label=T("End date"),
            widget=os_datepicker_widget),
        Field('Dropin', 'double', required=False,
            represent=represent_float_as_amount,
            default=0,
            label=T("Drop-in incl. VAT")),
        Field('tax_rates_id_dropin', db.tax_rates,
            label=T('Drop-in tax rate')),
        Field('DropinMembership', 'double', required=False,
              represent=represent_float_as_amount,
              default=0,
              label=T("Drop-in membership price incl. VAT")),
        Field('tax_rates_id_dropin_membership', db.tax_rates,
              label=T('Drop-in tax rate membership')),
        Field('accounting_glaccounts_id_dropin', db.accounting_glaccounts,
              requires=IS_EMPTY_OR(IS_IN_DB(db(ag_query),
                                            'accounting_glaccounts.id',
                                            '%(Name)s')),
              represent=represent_accounting_glaccount,
              label=T('Drop-in G/L Account'),
              comment=T('General ledger account ID in your accounting software')),
        Field('accounting_costcenters_id_dropin', db.accounting_costcenters,
              requires=IS_EMPTY_OR(IS_IN_DB(db(ac_query),
                                            'accounting_costcenters.id',
                                            '%(Name)s')),
              represent=represent_accounting_costcenter,
              label=T("Drop-in Cost center"),
              comment=T("Cost center code in your accounting software")),
        Field('Trial', 'double', required=False,
            represent=represent_float_as_amount,
            default=0,
            label=T("Trial incl. VAT")),
        Field('tax_rates_id_trial', db.tax_rates,
            label=T('Trial tax rate')),
        Field('TrialMembership', 'double', required=False,
            represent=represent_float_as_amount,
            default=0,
            label=T("Trial membership price incl. VAT")),
        Field('tax_rates_id_trial_membership', db.tax_rates,
            label=T('Trial tax rate membership')),
        Field('accounting_glaccounts_id_trial', db.accounting_glaccounts,
              requires=IS_EMPTY_OR(IS_IN_DB(db(ag_query),
                                            'accounting_glaccounts.id',
                                            '%(Name)s')),
              represent=represent_accounting_glaccount,
              label=T('Trial G/L Account'),
              comment=T('General ledger account ID in your accounting software')),
        Field('accounting_costcenters_id_trial', db.accounting_costcenters,
              requires=IS_EMPTY_OR(IS_IN_DB(db(ac_query),
                                            'accounting_costcenters.id',
                                            '%(Name)s')),
              represent=represent_accounting_costcenter,
              label=T("Trial cost center"),
              comment=T("Cost center code in your accounting software")),
        )


def define_classes_teachers():
    au_query = (db.auth_user.trashed == False) & \
               (db.auth_user.teacher == True) & \
               (db.auth_user.teaches_classes == True)

    db.define_table('classes_teachers',
        Field('classes_id', db.classes, required=True,
            readable=False,
            writable=False),
        Field('auth_teacher_id', db.auth_user,
            requires=IS_IN_DB(db(au_query),
                              'auth_user.id',
                              '%(first_name)s %(last_name)s',
                              zero=(T('Select teacher...'))),
            represent=lambda value, row: teachers_dict.get(value, None),
            #represent=lambda value, row: value or '', # when this is enabled it the schedule returns id's instead of names
            label=T("Teacher")),
        Field('teacher_role', 'integer',
            requires=IS_EMPTY_OR(IS_IN_SET(teachers_roles)),
            represent=represent_teacher_role,
            default=0,
            label=T('Teacher role')),
        Field('auth_teacher_id2', db.auth_user,
            requires=IS_EMPTY_OR(IS_IN_DB(db(au_query),
                                          'auth_user.id',
                                          '%(first_name)s %(last_name)s')),
            represent=lambda value, row: teachers_dict.get(value, None),
            #represent=lambda value, row: value or '',
            label=T("Teacher 2")),
        Field('teacher_role2', 'integer',
            requires=IS_EMPTY_OR(IS_IN_SET(teachers_roles)),
            represent=represent_teacher_role,
            label=T('Teacher role 2')),
        Field('Startdate', 'date', required=True,
            requires=IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                      minimum=datetime.date(1900,1,1),
                                      maximum=datetime.date(2999,1,1)),
            represent=represent_date,
            label=T("Start date"),
            widget=os_datepicker_widget),
        Field('Enddate', 'date', required=False,
            requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                 minimum=datetime.date(1900,1,1),
                                 maximum=datetime.date(2999,1,1))),
            represent=represent_date,
            label=T("End date"),
            widget=os_datepicker_widget),
        )


def define_classes_open():
    db.define_table('classes_open',
        Field('classes_id', db.classes, required=True),
        Field('ClassDate', 'date', required=True,
            requires=IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                      minimum=datetime.date(1900,1,1),
                                      maximum=datetime.date(2999,1,1)))
        )

def define_classes_cancelled():
    db.define_table('classes_cancelled',
        Field('classes_id', db.classes, required=True),
        Field('ClassDate', 'date', required=True,
            requires=IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                      minimum=datetime.date(1900,1,1),
                                      maximum=datetime.date(2999,1,1)))
        )

def define_classes_schedule_counts():
    """
        This table won't hold any actual data. It's used as a way to get the
        result of custom query for the class schedule into a web2py DAL row.
    """
    db.define_table('classes_schedule_count',
        Field('classes_id', db.classes, required=True),
        Field('Reservations', 'integer'),
        Field('ReservationsCancelled', 'integer'),
        Field('Attendance', 'integer'), # Attendance for this class
        Field('OnlineBooking', 'integer'),
        Field('Attendance4WeeksAgo', 'integer'),
        Field('Attendance8WeeksAgo', 'integer'),
        Field('NRClasses4WeeksAgo', 'integer'),
        Field('NRClasses8WeeksAgo', 'integer'),
        )


def define_customers_classcards():
    scd_query = (db.school_classcards.Archived == False)
    school_classcards_format = '%(Name)s'

    db.define_table('customers_classcards',
        Field('auth_customer_id', db.auth_user, required=True,
            readable=False,
            writable=False,
            label=T('CustomerID')),
        Field('school_classcards_id', db.school_classcards,
            requires=IS_IN_DB(db(scd_query),
                              'school_classcards.id',
                              school_classcards_format,
                              zero=(T('Please select...'))),
            label=T('Class card')),
        Field('Startdate', 'date', required=True,
            default=TODAY_LOCAL,
            requires=IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                      minimum=datetime.date(1900,1,1),
                                      maximum=datetime.date(2999,1,1)),
            represent=represent_date,
            label=T("Start"),
            widget=os_datepicker_widget),
        Field('Enddate', 'date', required=False,
            requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                      minimum=datetime.date(1900,1,1),
                                      maximum=datetime.date(2999,1,1))),
            represent=represent_date,
            label=T("Expiration"),
            widget=os_datepicker_widget),
        Field('Note', 'text',
            represent=lambda value, row: value or "",
            label=T("Any notes?")),
        Field('ClassesTaken', 'integer',
            readable=False,
            writable=False,
            default=0),
        Field('CreatedOn', 'datetime',
              readable=False,
              writable=False,
              default=datetime.datetime.now()),
        format='%(school_classcards_id)s',
        singular=T("Classcard"), plural=T("Classcards")
        )


def define_classes_attendance():
    types = [
        (1,T("Trial class")),
        (2,T("Drop In")),
        (3,T("Class card")),
        (4,T("Complementary")),
        (5,T("To be reviewed")),
    ]
    # None = subscription
    session.att_types_dict = {
        None: T("Subscription"),
        1: T("Trial class"),
        2: T("Drop In"),
        3: T("Class card"),
        4: T("Complementary"),
        5: T("To be reviewed")
    }
    db.define_table('classes_attendance',
        Field('auth_customer_id', db.auth_user, required=True,
            label=T('CustomerID')),
        Field('CustomerMembership', 'boolean', # Set to true if customer has membership when checking in
            readable=False,
            writable=False,
            default=False),
        Field('classes_id', db.classes, required=True,
            #represent=lambda value, row: classes_dict.get(value, None),
            represent=lambda value, row: value or '',
            label=T("Class")),
        Field('ClassDate', 'date', required=True,
            requires=IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                      minimum=datetime.date(1900,1,1),
                                      maximum=datetime.date(2999,1,1)),
            represent=represent_date,
            label=T("Class date"),
            widget=os_datepicker_widget),
        Field('AttendanceType', 'integer', required=True,
            requires=IS_IN_SET(types),
            represent=lambda value, row: session.att_types_dict.get(value, ""),
            label=T("Type")),
        Field('customers_subscriptions_id', db.customers_subscriptions,
            represent=represent_customer_subscription,
            label=T('Subscription')),
        Field('customers_classcards_id', db.customers_classcards,
            represent=lambda value, row: value or "",
            label=T("Card")),
        Field('online_booking', 'boolean',
            readable=False,
            writable=False,
            default=False,
            label=T('Online')),
        Field('BookingStatus',
            requires=IS_IN_SET(booking_statuses),
            default='booked',
            readable=False,
            writable=False,
            represent = represent_classes_attendance_bookingstatus,
            label=T('BookingStatus')),
        Field('CreatedOn', 'datetime',
            readable=False,
            writable=False,
            represent=represent_datetime,
            default=datetime.datetime.now()),
        Field('CreatedBy', db.auth_user,
            readable=False,
            writable=False)
        )

    try:
        db.classes_attendance.CreatedBy.default = auth.user.id
    except AttributeError:
        pass


def represent_customer_subscription(value, row):
    """
        Returns name of subscription with startdate
    """
    return_value = ''

    if value:
        subscription = db.customers_subscriptions(value)
        ssuID = subscription.school_subscriptions_id
        school_subscription = db.school_subscriptions(ssuID)
        startdate = subscription.Startdate.strftime(DATE_FORMAT)
        title = T('From') + ' ' + startdate + ' [' + unicode(value) + ']'
        return_value = SPAN(school_subscription.Name, _title=title)

    return return_value


def define_classes_attendance_override():
    db.define_table('classes_attendance_override',
        Field('classes_id', db.classes, required=True,
            readable=False,
            writable=False,
            label=T("ClassID")),
        Field('ClassDate', 'date', required=True,
            readable=False,
            writable=False,
                        requires=IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                      minimum=datetime.date(1900,1,1),
                                      maximum=datetime.date(2999,1,1)),
            label=T("Class date"),
            widget=os_datepicker_widget),
        Field('Amount', 'integer', required=True,
            label=T("")),
        )

def define_customers_payment_info():
    db.define_table('customers_payment_info',
        Field('auth_customer_id', db.auth_user, required=True,
            readable=False,
            writable=False,
            label=T('CustomerID')),
        Field('payment_methods_id', db.payment_methods,
            requires=IS_EMPTY_OR(IS_IN_DB(db,'payment_methods.id','%(Name)s',
                                          zero=T("Please select..."))),
            represent=lambda value, row: payment_methods_dict.get(value),
            label=T("Default payment method")),
        Field('AccountNumber',
            requires=[
                IS_NOT_EMPTY(error_message=T("Account number is required")),
                IS_IBAN()
            ],
            represent=lambda value, row: value or "",
            label=T("Account number")),
        Field('AccountHolder',
            requires=IS_NOT_EMPTY(
                error_message=T("Account holder is required")
            ),
            represent=lambda value, row: value or "",
            label=T("Account holder")),
        Field('BIC',
            represent=lambda value, row: value or "",
            label=T("BIC")),
        Field('MandateSignatureDate', 'date', # Deprecated from 2018.82 do NOT use. Store in payment_info_mandates
            readable=False,
            writable=False,
            requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                      minimum=datetime.date(1900,1,1),
                                      maximum=datetime.date(2999,1,1))),
            represent=represent_date,
            label=T("Mandate signature date"),
            widget=os_datepicker_widget),
        Field('BankName',
            represent=lambda value, row: value or "",
            label=T("Bank name")),
        Field('BankLocation',
            represent=lambda value, row: value or "",
            label=T("Bank location")),
        Field('exact_online_bankaccount_id',
            readable=False,
            writable=False),
        singular=T("Bank details"), plural=T("Bank details")
        )

    # sorted_payment_methods = [dict(id=None, Name=T("Please select..."))]
    # payment_methods = db(db.payment_methods).select(orderby=db.payment_methods.id)
    # for method in payment_methods:
    #     sorted_payment_methods.append(dict(Name=method.Name, id=method.id))
    #
    # db.customers_payment_info.payment_methods_id.widget = lambda f, v: \
    #     SELECT([OPTION(i['Name'],
    #         _value=i['id']) for i in sorted_payment_methods],
    #         _name=f.name, _id="%s_%s" % (f._tablename, f.name),
    #         _value=v,
    #         value=v)


def define_customers_payment_info_mandates():
    """
        Table to hold mandates for bank accounts
    """
    import uuid

    db.define_table('customers_payment_info_mandates',
        Field('customers_payment_info_id', db.customers_payment_info,
              readable=False,
              writable=False,
              label=T('Payment Info')),
        Field('MandateReference',
              requires=IS_NOT_EMPTY(),
              default=str(uuid.uuid4()),
              label=T("Mandate reference"),
              comment=T("OpenStudio automatically generates a unique reference for each mandate, but you're free to enter something else.")),
        Field('MandateText', 'text',
              writable=False,
              represent=lambda value, row: value or ''),
        Field('MandateSignatureDate', 'date',
              requires=IS_EMPTY_OR(
                  IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                   minimum=datetime.date(1900, 1, 1),
                                   maximum=datetime.date(2999, 1, 1))
              ),
              default=TODAY_LOCAL ,
              represent=represent_date,
              label=T("Mandate signature date"),
              widget=os_datepicker_widget),
        Field("CreatedOn", 'datetime',
              readable=False,
              writable=False,
              represent=represent_datetime,
              default=datetime.datetime.now()),
        Field('exact_online_directdebitmandates_id',
              readable=False,
              writable=False)
    )


def define_customers_memberships():
    ms_query = (db.school_memberships.Archived == False)
    pm_query = (db.payment_methods.Archived == False)

    school_memberships_format = '%(Name)s'

    db.define_table('customers_memberships',
        Field('auth_customer_id', db.auth_user, required=True,
              readable=False,
              writable=False,
              label=T('CustomerID')),
        Field('school_memberships_id', db.school_memberships,
              requires=IS_IN_DB(db(ms_query),
                                'school_memberships.id', school_memberships_format,
                                zero=T("Please select...")),
              label=T("Membership")),
        Field('Startdate', 'date', required=True,
              requires=IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                        minimum=datetime.date(1900, 1, 1),
                                        maximum=datetime.date(2999, 1, 1)),
              represent=represent_date,
              default=TODAY_LOCAL,
              label=T("Start"),
              widget=os_datepicker_widget),
        Field('Enddate', 'date', required=False,
              requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                                    minimum=datetime.date(1900, 1, 1),
                                                    maximum=datetime.date(2999, 1, 1))),
              represent=represent_date,
              label=T("End"),
              widget=os_datepicker_widget),
        Field('payment_methods_id', db.payment_methods, required=True,
              requires=IS_EMPTY_OR(IS_IN_DB(db(pm_query), 'payment_methods.id', '%(Name)s',
                                            zero=T("Please select..."))),
              represent=lambda value, row: payment_methods_dict.get(value),
              label=T("Payment method")),
        Field('Note', 'text',
              represent=lambda value, row: value or '',
              label=T("Note")),
        singular=T("Membership"), plural=T("Memberships")
        )


def define_customers_subscriptions():
    subscriptions_query = (db.school_subscriptions.Archived == False)
    pm_query = (db.payment_methods.Archived == False)

    school_subscription_format = '%(Name)s'

    db.define_table('customers_subscriptions',
        Field('auth_customer_id', db.auth_user, required=True,
            readable=False,
            writable=False,
            label=T('CustomerID')),
        Field('school_subscriptions_id', db.school_subscriptions,
            requires = IS_IN_DB(db(subscriptions_query),
                'school_subscriptions.id', school_subscription_format,
                zero=T("Please select...")),
            #represent=lambda value, row: mstypes_dict.get(value, None),
            #represent=lambda value, row: value or '',
            label=T("Subscription")),
        Field('Startdate', 'date', required=True,
            requires=IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                      minimum=datetime.date(1900,1,1),
                                      maximum=datetime.date(2999,1,1)),
            represent=represent_date,
            default=TODAY_LOCAL,
            label=T("Start"),
            widget=os_datepicker_widget),
        Field('Enddate', 'date', required=False,
            requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                      minimum=datetime.date(1900,1,1),
                                      maximum=datetime.date(2999,1,1))),
            represent=represent_date,
            label=T("End"),
            widget=os_datepicker_widget),
        Field('payment_methods_id', db.payment_methods, required=True,
            requires=IS_EMPTY_OR(IS_IN_DB(db(pm_query),'payment_methods.id','%(Name)s',
                                          zero=T("Please select..."))),
            represent=lambda value, row: payment_methods_dict.get(value),
            label=T("Payment method")),
        Field('Note', 'text',
            represent=lambda value, row: value or '',
            label=T("Note")),
        Field('CreditsRemaining', 'float',
            readable=False,
            writable=False), # no actual data is stored, but used to map raw sql into DAL
        Field('PeriodCreditsAdded', 'float',
            readable=False,
            writable=False), # no actual data is stored, but used to map raw sql into DAL
        Field('CreatedOn', 'datetime',
              readable=False,
              writable=False,
              default=datetime.datetime.now()),
        Field('RegistrationFeePaid','boolean',
              readable=False,
              writable=False,
              default=False
              ),
        singular=T("Subscription"), plural=T("Subscriptions"))


def define_customers_subscriptions_credits():
    """
        Table to hold credit transactions for subscriptions
    """
    months = get_months_list()
    mutation_types = [ ['add', T('Add')],
                       ['sub', T('Subtract')] ]

    db.define_table('customers_subscriptions_credits',
        Field('customers_subscriptions_id', db.customers_subscriptions, required=True,
            readable=False,
            writable=False,
            represent=represent_customer_subscription_as_name,
            label=T("Subscription")),
        Field('classes_attendance_id', db.classes_attendance,
            readable=False,
            writable=False,
            requires=IS_EMPTY_OR(IS_IN_DB(db.classes_attendance,
                                          'classes_attendance.id',
                                          '%(id)s'))),
        Field('MutationDateTime', 'datetime',
              readable=False,
              writable=False,
              default=TODAY_LOCAL,
              represent=represent_datetime,
              label=T('Mutation Time')),
        Field('MutationType',
            requires=IS_IN_SET(mutation_types, zero=None), # Add or Sub(tract)
            represent=represent_customers_subscriptions_credits_MutationType,
            label=T('Mutation')),
        Field('MutationAmount', 'float',
            label=T('Credits')), # Number of credits
        Field('Description', 'text'),
        Field('SubscriptionYear', 'integer',
            readable=False,
            writable=False,
            default=TODAY_LOCAL.year,
            requires=IS_EMPTY_OR(IS_INT_IN_RANGE(1900, 2999)),
            label=T("Year")),
        Field('SubscriptionMonth', 'integer',
            readable=False,
            writable=False,
            requires=IS_EMPTY_OR(IS_IN_SET(months, zero=T("Please select..."))),
            default=TODAY_LOCAL.month,
            represent=NRtoMonth,
            label=T("Month")),
        Field('Expiration', 'boolean',
            readable=False,
            writable=False,
            default=False,
            label=T('Expired'))
    )


def represent_customers_subscriptions_credits_MutationType(value, row):
    """
        Represent mutation type
    """
    if value == 'add':
        mtype = os_gui.get_label('success', B(T('+')))
    else:
        mtype = os_gui.get_label('default', B(T('-')))

    return mtype


def define_customers_subscriptions_paused():
    today = TODAY_LOCAL
    startdate_default = datetime.date(today.year, today.month, 1)
    enddate_default = get_last_day_month(startdate_default)

    db.define_table('customers_subscriptions_paused',
        Field('customers_subscriptions_id', db.customers_subscriptions, required=True,
              readable=False,
              writable=False,
              represent=represent_customer_subscription_as_name,
              label=T("Subscription")),
        Field('Startdate', 'date', required=True,
            requires=IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                      minimum=datetime.date(1900,1,1),
                                      maximum=datetime.date(2999,1,1)),
            default=startdate_default,
            label=T("Paused from"),
            widget=os_datepicker_widget),
        Field('Enddate', 'date', required=True,
            requires=IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                      minimum=datetime.date(1900,1,1),
                                      maximum=datetime.date(2999,1,1)),
            default=enddate_default,
            label=T("Paused until"),
            widget=os_datepicker_widget),
        Field('Description',
            represent=lambda value, row: value or "",
            label=T("Description")),
        )


def define_customers_subscriptions_alt_prices():
    months = get_months_list()

    db.define_table('customers_subscriptions_alt_prices',
        Field('customers_subscriptions_id', db.customers_subscriptions,
            required=True,
            readable=False,
            writable=False,
            label=T("Subscription")),
        Field('SubscriptionMonth', 'integer',
            requires=IS_IN_SET(months, zero=T('Please select...')),
            represent=NRtoMonth,
            default=TODAY_LOCAL.month,
            label=T('Month')),
        Field('SubscriptionYear', 'integer',
            default=TODAY_LOCAL.year,
            label=T('Year')),
        Field('Amount', 'double', required=True,
            requires=IS_NOT_EMPTY(),
            represent = represent_float_as_amount,
            label=T("Amount")),
        Field('Description',
            represent=lambda value, row: value or "",
            label=T("Description"),
            comment = os_gui.get_info_icon(
                title=T("This will appear on invoice as the description."),
                btn_icon='info')),
        Field('Note', 'text',
            represent=lambda value, row: value or "",
            label=T("Note"),
            comment = os_gui.get_info_icon(
                title=T("Private notes field, not visible for customers."),
                btn_icon='info')),
        )


def define_customers_documents():
    db.define_table('customers_documents',
        Field('auth_customer_id', db.auth_user, required=True,
            readable=False,
            writable=False,
            label=T('CustomerID')),
        Field('Description', required=False,
            requires=IS_NOT_EMPTY(),
            label=T("Description")),
        Field('DocumentFile', 'upload', autodelete=True,
            requires=IS_LENGTH(maxsize=4153344,
                error_message=T("Maximum size is 4MB")),
            represent=lambda value, row: A(T("Download"),
                _href=URL('default', 'download', args=value)),
            label=T("File (max 4MB)")),
        Field('UploadDateTime', 'datetime', required=True,
            readable=False,
            writable=False,
            default=datetime.datetime.now(),
            represent=represent_datetime,
            label=T("Uploaded on")),
        )


def define_log_customers_accepted_documents():
    db.define_table('log_customers_accepted_documents',
        Field('auth_customer_id', db.auth_user,
              readable=False,
              writable=False,
              label="CustomerID"),
        Field('DocumentName',
              label=T("Document")),
        Field('DocumentDescription',
              represent=lambda value, row: value or '',
              label=T("Description")),
        Field('DocumentVersion',
              represent=lambda value, row: value or '',
              label=T("Document version")),
        Field('DocumentURL',
              requires=IS_URL(),
              label=T('Document accepted on URL')),
        Field('OpenStudioVersion',
              represent=lambda value, row: value or '',
              label=T('OpenStudio version')),
        Field('CreatedOn', 'datetime',
              readable=False,
              writable=False,
              default=datetime.datetime.now(),
              represent=represent_datetime,
              label=T('Accepted on'))
    )


def define_teachers_classtypes():
    db.define_table('teachers_classtypes',
        Field('auth_user_id', db.auth_user,
            label=T('Teacher')),
        Field('school_classtypes_id', db.school_classtypes, required=True,
            label=T("Class type")),
        )


def define_classes_subteachers():
    au_query = (db.auth_user.trashed == False) & \
               (db.auth_user.teacher == True) & \
               (db.auth_user.teaches_classes == True)

    db.define_table('classes_subteachers',
        Field('classes_id', db.classes, required=True,
            readable=False,
            writable=False,
            label=T("ClassID")),
        Field('ClassDate', 'date', required=True,
            readable=False,
            writable=False,
            requires=IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                      minimum=datetime.date(1900,1,1),
                                      maximum=datetime.date(2999,1,1)),
            label=T("Class date"),
            widget=os_datepicker_widget),
        Field('auth_teacher_id', db.auth_user,
            requires=IS_IN_DB(db(au_query),
                              'auth_user.id',
                              '%(first_name)s %(last_name)s',
                              zero=(T('Select teacher...'))),
            represent=lambda value, row: teachers_dict.get(value, None),
            #represent=lambda value, row: value or '',
            label=T("Teacher")),
        Field('teacher_role', 'integer',
            requires=IS_EMPTY_OR(IS_IN_SET(teachers_roles)),
            represent=represent_teacher_role,
            default=1,
            label=T('Teacher role')),
        Field('auth_teacher_id2', db.auth_user,
            requires=IS_EMPTY_OR(IS_IN_DB(db(au_query),
                                          'auth_user.id',
                                          '%(first_name)s %(last_name)s')),
            represent=lambda value, row: teachers_dict.get(value, None),
            #represent=lambda value, row: value or '',
            label=T("Teacher")),
        Field('teacher_role2', 'integer',
            requires=IS_EMPTY_OR(IS_IN_SET(teachers_roles)),
            represent=represent_teacher_role,
            label=T('Teacher role 2')),
        )

def define_classes_reservation():
    db.define_table('classes_reservation',
        Field('auth_customer_id', db.auth_user, required=True,
            readable=False,
            writable=False,
            label=T('CustomerID')),
        Field('classes_id', db.classes,
            readable=False,
            writable=False,
            #represent=lambda value, row: classes_dict.get(value, None),
            represent=lambda value, row: value or '',
            label=T("Class")),
        Field('customers_subscriptions_id', db.customers_subscriptions,
            readable=False,
            writable=False,
            label=T("Subscription")),
        Field('Startdate', 'date', required=True,
            requires=IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                      minimum=datetime.date(1900,1,1),
                                      maximum=datetime.date(2999,1,1)),
            represent=represent_date,
            label=T("Start date"),
            widget=os_datepicker_widget),
        Field('Enddate', 'date', required=False,
            requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                  minimum=datetime.date(1900,1,1),
                                  maximum=datetime.date(2999,1,1))),
            represent=represent_date,
            label=T("End date"),
            comment=T("If an enddate is not set, the enrollment is considered indefinite and can be ended later by setting an end date."),
            widget=os_datepicker_widget),
        Field('SingleClass', 'boolean',
            readable=False,
            writable=False,
            default=False,
            represent=represent_classes_reservation_single_class),
        Field('TrialClass', 'boolean',
            readable=False,
            writable=False,
            default=False),
        Field('ResType',
            readable=False,
            writable=False,
            compute=compute_classes_reservation_restype,
            represent=represent_classes_reservation_restype),
        )


def compute_classes_reservation_restype(row):
    """
        Returns reservation type based on data in row
    """
    restype = 'recurring'
    if row.SingleClass == True and row.TrialClass == False:
        restype = 'single'
    elif row.SingleClass == True and row.TrialClass == True:
        restype = 'trial'

    return restype


def represent_classes_reservation_restype(value, row):
    """
        Returns reservation type for a class
    """
    repr_val = ''
    if value == 'single':
        repr_val = os_gui.get_label('primary', T("Drop in"))
    elif value == 'trial':
        repr_val = os_gui.get_label('success', T("Trial"))
    elif value == 'recurring':
        repr_val = os_gui.get_label('default', T("Enrolled"))

    return repr_val


def represent_classes_reservation_single_class(value, row):
    """
        returns 'Single class' when row.SingleClass == True
        returns 'Recurring' when row.SingleClass != True
    """
    return_value = SPAN(T("Enrolled from "), row.Startdate)
    if row.Enddate:
        return_value.append(T(' until '))
        return_value.append(row.Enddate)

    if value:
        if row.TrialClass:
            return_value = T("Trial class on") + ' ' + row.Startdate
        else: # regular single reservation
            return_value = T("Drop in class on") + ' ' + row.Startdate

    return return_value


def define_classes_reservation_cancelled():
    db.define_table('classes_reservation_cancelled',
        Field('classes_reservation_id', db.classes_reservation,
            label=T("Reservation")),
        Field('ClassDate', 'date', required=True,
            requires=IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                      minimum=datetime.date(1900,1,1),
                                      maximum=datetime.date(2999,1,1)),
            widget=os_datepicker_widget),
        )


def define_classes_waitinglist():
    db.define_table('classes_waitinglist',
        Field('auth_customer_id', db.auth_user, required=True,
            readable=False,
            writable=False,
            label=T('CustomerID')),
        Field('classes_id', db.classes,
            writable=False,
            #represent=lambda value, row: classes_dict.get(value, None),
            represent=lambda value, row: value or '',
            label=T("Class")),
        )


def define_workshops():
    au_query = (db.auth_user.trashed == False) & \
               (db.auth_user.teacher == True) & \
               (db.auth_user.teaches_workshops == True)

    sl_query = (db.school_levels.Archived == False)
    loc_query = (db.school_locations.Archived == False)

    db.define_table('workshops',
        Field('Archived', 'boolean',
            readable=False,
            writable=False,
            default=False,
            label=T("Archived")),
        Field('PublicWorkshop', 'boolean',
            default=False,
            label=T('Show in shop')),
        Field('AutoSendInfoMail', 'boolean',
            default=True,
            label=T('Auto send info mail'),
            comment=T("Automatically send info mail to all customers added to this workshop.")),
        Field('Name',
            requires=IS_NOT_EMPTY(),
            label=T("Name")),
        Field('Tagline',
              represent=lambda value, row: value or "",
              label=T('Tagline'),
              comment=T('If asked to describe this event in a short sentence, it would be...')),
        Field('school_levels_id', db.school_levels, required=False,
            requires=IS_EMPTY_OR(IS_IN_DB(db(sl_query),
                                 'school_levels.id',
                                 '%(Name)s')),
            represent=lambda value, row: levels_dict.get(value, T("")),
            label=T("Level")),
        Field('Startdate', 'date',
            writable=False,
            requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                 minimum=datetime.date(1900,1,1),
                                 maximum=datetime.date(2999,1,1))),
            represent=represent_date,
            label=T("Start date"),
            widget=os_datepicker_widget),
        Field('Enddate', 'date',
            readable=False,
            writable=False,
            requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                 minimum=datetime.date(1900,1,1),
                                 maximum=datetime.date(2999,1,1))),
            represent=represent_date,
            label=T("End date"),
            widget=os_datepicker_widget),
        Field('Starttime', 'time',
            readable=False,
            writable=False,
            requires=IS_TIME(error_message='must be HH:MM'),
            represent=lambda value, row: value.strftime('%H:%M') if value else '',
            widget=os_time_widget,
            label=T("Start")),
        Field('Endtime', 'time',
            readable=False,
            writable=False,
            requires=IS_TIME(error_message='must be HH:MM'),
            represent=lambda value, row: value.strftime('%H:%M') if value else '',
            widget=os_time_widget,
            label=T("End")),
        Field('Teacher', # legacy field, but keep it for now
            readable=False,
            writable=False,
            represent=lambda value, row: value or "",
            label=T("External Teacher")),
        Field('TeacherEmail', # legacy field, but keep it for now
            readable=False,
            writable=False,
            requires=IS_EMPTY_OR(IS_EMAIL()),
            label=T("External Teacher email")),
        Field('Teacher2', # legacy field, but keep it for now
            readable=False,
            writable=False,
            represent=lambda value, row: value or "",
            label=T("External Teacher 2")),
        Field('Teacher2Email', # legacy field, but keep it for now
            readable=False,
            writable=False,
            requires=IS_EMPTY_OR(IS_EMAIL()),
            label=T("External Teacher2 email")),
        Field('auth_teacher_id', db.auth_user,
            requires=IS_EMPTY_OR(IS_IN_DB(db(au_query),
                              'auth_user.id',
                              '%(first_name)s %(last_name)s',
                              zero=(T('Select teacher...')))),
            represent=lambda value, row: teachers_dict.get(value, None),
            #represent=lambda value, row: value or '',
            label=T("Teacher"),
            comment=T("Default teacher(s) for activities and this teacher will be shown in the OpenStudio shop.")),
        Field('auth_teacher_id2', db.auth_user,
            requires=IS_EMPTY_OR(IS_IN_DB(db(au_query),
                                          'auth_user.id',
                                          '%(first_name)s %(last_name)s')),
            represent=lambda value, row: teachers_dict.get(value, None),
            #represent=lambda value, row: value or '',
            label=T("Teacher 2")),
        Field('Preview', 'text',
            label=T('Preview'),
            comment=T('A short introduction about this event')),
        Field('Description', 'text',
            label=T('Description'),
            comment=T("Full event description")),
        Field('school_locations_id', db.school_locations, required=True,
              requires=IS_IN_DB(db(loc_query),
                                'school_locations.id',
                                '%(Name)s',
                                zero=T("Please select...")),
              represent=lambda value, row: locations_dict.get(value, T("No location set")),
              label=T("Location")),
        Field('picture', 'upload', autodelete=True,
            requires=IS_EMPTY_OR([IS_IMAGE(extensions=('jpeg', 'jpg', 'png')),
                                           IS_LENGTH(maxsize=665600,
                                                     error_message=T('650KB or less'))]), # 650KB
            label=T("Image (Max 650KB)")),
        Field('thumbsmall', 'upload', # generate 50*50 for list view
            autodelete=True, writable=False,
            compute = lambda row: SMARTHUMB(row.picture,
                                            (50, 50),
                                             name="Small"),
            represent = represent_workshops_thumbsmall,
            label=T("Image")),
        Field('thumblarge', 'upload', # generate 400*400 for edit view
            autodelete=True, writable=False,
            compute = lambda row: SMARTHUMB(row.picture,
                                             (400, 400),
                                             name="Large"),
            represent = represent_workshops_thumblarge),
        Field('picture_2', 'upload', autodelete=True,
            requires=IS_EMPTY_OR([IS_IMAGE(extensions=('jpeg', 'jpg', 'png')),
                                           IS_LENGTH(maxsize=665600,
                                                     error_message=T('650KB or less'))]), # 650KB
            label=T("Image (Max 650KB)")),
        Field('thumbsmall_2', 'upload', # generate 50*50 for list view
            autodelete=True, writable=False,
            compute = lambda row: SMARTHUMB(row.picture_2,
                                            (50, 50),
                                             name="Small"),
            represent = represent_workshops_thumbsmall,
            label=T("Image")),
        Field('thumblarge_2', 'upload', # generate 400*400 for edit view
            autodelete=True, writable=False,
            compute = lambda row: SMARTHUMB(row.picture_2,
                                             (400, 400),
                                             name="Large"),
            represent = represent_workshops_thumblarge),
        Field('picture_3', 'upload', autodelete=True,
            requires=IS_EMPTY_OR([IS_IMAGE(extensions=('jpeg', 'jpg', 'png')),
                                           IS_LENGTH(maxsize=665600,
                                                     error_message=T('650KB or less'))]), # 650KB
            label=T("Image (Max 650KB)")),
        Field('thumbsmall_3', 'upload', # generate 50*50 for list view
            autodelete=True, writable=False,
            compute = lambda row: SMARTHUMB(row.picture_3,
                                            (50, 50),
                                             name="Small"),
            represent = represent_workshops_thumbsmall,
            label=T("Image")),
        Field('thumblarge_3', 'upload', # generate 400*400 for edit view
            autodelete=True, writable=False,
            compute = lambda row: SMARTHUMB(row.picture_3,
                                             (400, 400),
                                             name="Large"),
            represent = represent_workshops_thumblarge),
        Field('picture_4', 'upload', autodelete=True,
            requires=IS_EMPTY_OR([IS_IMAGE(extensions=('jpeg', 'jpg', 'png')),
                                           IS_LENGTH(maxsize=665600,
                                                     error_message=T('650KB or less'))]), # 650KB
            label=T("Image (Max 650KB)")),
        Field('thumbsmall_4', 'upload', # generate 50*50 for list view
            autodelete=True, writable=False,
            compute = lambda row: SMARTHUMB(row.picture_4,
                                            (50, 50),
                                             name="Small"),
            represent = represent_workshops_thumbsmall,
            label=T("Image")),
        Field('thumblarge_4', 'upload', # generate 400*400 for edit view
            autodelete=True, writable=False,
            compute = lambda row: SMARTHUMB(row.picture_4,
                                             (400, 400),
                                             name="Large"),
            represent = represent_workshops_thumblarge),
        Field('picture_5', 'upload', autodelete=True,
            requires=IS_EMPTY_OR([IS_IMAGE(extensions=('jpeg', 'jpg', 'png')),
                                           IS_LENGTH(maxsize=665600,
                                                     error_message=T('650KB or less'))]), # 650KB
            label=T("Image (Max 650KB)")),
        Field('thumbsmall_5', 'upload', # generate 50*50 for list view
            autodelete=True, writable=False,
            compute = lambda row: SMARTHUMB(row.picture_5,
                                            (50, 50),
                                             name="Small"),
            represent = represent_workshops_thumbsmall,
            label=T("Image")),
        Field('thumblarge_5', 'upload', # generate 400*400 for edit view
            autodelete=True, writable=False,
            compute = lambda row: SMARTHUMB(row.picture_5,
                                             (400, 400),
                                             name="Large"),
            represent = represent_workshops_thumblarge),
        format='%(Name)s')


def define_workshops_mail():
    """
        Table to hold workshops_information_mails
    """
    db.define_table('workshops_mail',
        Field('workshops_id', db.workshops,
              readable=False,
              writable=False,
              label=T("Event")),
        Field('MailContent', 'text',
              label=T("Mail content"))
    )


def define_workshops_activities():
    loc_query = (db.school_locations.Archived == False)
    au_query = (db.auth_user.trashed == False) & \
               (db.auth_user.teacher == True) & \
               (db.auth_user.teaches_workshops == True)

    db.define_table('workshops_activities',
        Field('workshops_id', db.workshops, readable=False, writable=False,
            label=T("Event")),
        Field('Activity',
            requires=IS_NOT_EMPTY(),
            label=T("Name")),
        Field('Activitydate', 'date', required=True,
            requires=IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                      minimum=datetime.date(1900,1,1),
                                      maximum=datetime.date(2999,1,1)),
            represent=represent_date,
            label=T("Date"),
            widget=os_datepicker_widget),
        Field('school_locations_id', db.school_locations,
            requires=IS_EMPTY_OR(IS_IN_DB(db(loc_query),
                                          'school_locations.id',
                                          '%(Name)s')),
            represent=lambda value, row: locations_dict.get(value, None),
            label=T("Location")),
        Field('LocationExternal', # Deprecated
            readable=False,
            writable=False,
            represent=lambda value, row: value or '',
            label=T("External location")),
        Field('Starttime', 'time', required=True,
            requires=IS_TIME(error_message='must be HH:MM'),
            represent=lambda value, row: value.strftime('%H:%M'),
            widget=os_time_widget,
            label=T("Start")),
        Field('Endtime', 'time', required=True,
            readable=False,
            requires=IS_TIME(error_message='must be HH:MM'),
            represent=lambda value, row: value.strftime('%H:%M'),
            widget=os_time_widget,
            label=T("End")),
        Field('Spaces', 'integer',
            requires=IS_NOT_EMPTY(),
            label=T("Spaces")),
        Field('Teacher', # Deprecated
            readable=False,
            writable=False,
            represent=lambda value, row: value or "",
            label=T("External Teacher")),
        Field('TeacherEmail', # Deprecated
            readable=False,
            writable=False,
            requires=IS_EMPTY_OR(IS_EMAIL()),
            label=T("External Teacher email")),
        Field('Teacher2', # Deprecated
            readable=False,
            writable=False,
            represent=lambda value, row: value or "",
            label=T("External Teacher 2")),
        Field('Teacher2Email', # Deprecated
            readable=False,
            writable=False,
            requires=IS_EMPTY_OR(IS_EMAIL()),
            label=T("External Teacher2 email")),
        Field('auth_teacher_id', db.auth_user,
            requires=IS_EMPTY_OR(IS_IN_DB(db(au_query),
                                 'auth_user.id',
                                 '%(first_name)s %(last_name)s',
                                 zero=(T('Select teacher...')))),
            represent=lambda value, row: teachers_dict.get(value, None),
            #represent=lambda value, row: value or '',
            label=T("Teacher")),
        Field('auth_teacher_id2', db.auth_user,
            requires=IS_EMPTY_OR(IS_IN_DB(db(au_query),
                                          'auth_user.id',
                                          '%(first_name)s %(last_name)s')),
            represent=lambda value, row: teachers_dict.get(value, None),
            #represent=lambda value, row: value or '',
            label=T("Teacher 2")),
        )


def define_workshops_products():
    ac_query = (db.accounting_costcenters.Archived == False)
    ag_query = (db.accounting_glaccounts.Archived == False)

    db.define_table('workshops_products',
        Field('workshops_id', db.workshops,
            readable=False,
            writable=False,
            label=T("WorkshopID")),
        Field('FullWorkshop', 'boolean', required=True,
            readable=False,
            writable=False,
            default=False),
        Field('Deletable', 'boolean', required=True,
            readable=False,
            writable=False,
            default=True),
        Field('PublicProduct', 'boolean',
            default=True,
            label=T('Show in shop')),
        Field('Name',
            requires=IS_NOT_EMPTY(),
            label=T('Name')),
        Field('Price', 'double', required=True,
            requires=IS_FLOAT_IN_RANGE(0,99999999, dot='.',
                error_message=T('Too small or too large')),
            represent=represent_float_as_amount,
            label=T("Price incl. VAT")),
        Field('PriceSubscription', 'double',
            requires=IS_EMPTY_OR(IS_FLOAT_IN_RANGE(0,99999999, dot='.',
                error_message=T('Too small or too large'))),
            represent=represent_float_as_amount,
            label=T("Subscription price incl. VAT"),
            comment=T("This price will be applied when a customer has a subscription")),
        Field('PriceEarlybird', 'double',
            requires=IS_EMPTY_OR(IS_FLOAT_IN_RANGE(0,99999999, dot='.',
                error_message=T('Too small or too large'))),
            represent=represent_float_as_amount,
            label=T("Earlybird price incl. VAT")),
        Field('PriceSubscriptionEarlybird', 'double',
            requires=IS_EMPTY_OR(IS_FLOAT_IN_RANGE(0,99999999, dot='.',
                error_message=T('Too small or too large'))),
            represent=represent_float_as_amount,
            label=T("Earlybird price incl. VAT for customers with a subscription")),
        Field('EarlybirdUntil', 'date',
              requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                                    minimum=datetime.date(1900, 1, 1),
                                                    maximum=datetime.date(2999, 1, 1))),
              label=T("Earlybird price until"),
              comment=T("Earlybird price will be applied until the date above"),
              widget=os_datepicker_widget,),
        Field('tax_rates_id', db.tax_rates,
            requires=IS_IN_DB(db,
                              'tax_rates.id',
                              '%(Name)s',
                              zero=T("Please select..."),
                              error_message=T("Please select a tax rate")),
            label=T('Tax rate'),
            comment=T('Tax rate for prices')),
        Field('Description', 'text', required=False),
        Field('ExternalShopURL',
            label=T("Link external shop"),
            comment=T(
                    "Add an url here starting with 'http://, https:// or mailto:' to change the link of the 'add to cart' button " + \
                    "for this poduct")),
        Field('AddToCartText',
            label=T("Add to cart text"),
            default=T('Add to cart'),
            comment=T("Change the text for the 'Add to cart' button. Shows 'Add to cart' when left empty.")),
        Field('Donation', 'boolean',
            label=T("Donation based"),
            default=False,
            comment=T("Shows 'Donation based' instead of the price in the shop.")),
        Field('accounting_glaccounts_id', db.accounting_glaccounts,
              requires=IS_EMPTY_OR(IS_IN_DB(db(ag_query),
                                            'accounting_glaccounts.id',
                                            '%(Name)s')),
              represent=represent_accounting_glaccount,
              label=T('G/L Account'),
              comment=T('General ledger account ID in your accounting software')),
        Field('accounting_costcenters_id', db.accounting_costcenters,
              requires=IS_EMPTY_OR(IS_IN_DB(db(ac_query),
                                            'accounting_costcenters.id',
                                            '%(Name)s')),
              represent=represent_accounting_costcenter,
              label=T("Cost center"),
              comment=T("Cost center code in your accounting software")),
        format='%(Name)s')


def define_workshops_products_activities():
    db.define_table('workshops_products_activities',
        Field('workshops_products_id', db.workshops_products,
            label=T("Product")),
        Field('workshops_activities_id', db.workshops_activities,
            label=T("Activity")))


def define_workshops_products_customers():
    db.define_table('workshops_products_customers',
        Field('workshops_products_id', db.workshops_products,
            label=T('Product')),
        Field('auth_customer_id', db.auth_user, required=True,
            label=T('CustomerID')),
        Field('Cancelled', 'boolean',
            required=True,
            default=False,
            label=T('Cancelled')),
        Field('PaymentConfirmation', 'boolean',
            default=False,
            label=T("Payment confirmation")),
        Field('WorkshopInfo', 'boolean',
            default=False,
            label=T("Event information")),
        Field('Waitinglist', 'boolean',
            default=False,
            label=T('Waitinglist')),
        Field('CreatedOn', 'datetime',
              readable=False,
              writable=False,
              default=datetime.datetime.now()),
        )


def define_workshops_activities_customers():
    """
        Table used to store attendance for a workshop activity
    """
    db.define_table('workshops_activities_customers',
        Field('workshops_activities_id', db.workshops_activities,
            requires=IS_EMPTY_OR(IS_IN_DB(db, 'workshops_activities.id',
                                          '%(Activity)s')),
            #represent = lambda value, row: \
                #workshops_activities_dict.get(value, T("Not Found")),
            represent=lambda value, row: value or '',
            label=T("Workshop Activity")),
        Field('auth_customer_id', db.auth_user, required=True,
            label=T('CustomerID')),
        )


def define_school_holidays():
    db.define_table('school_holidays',
        Field('Description', required=True,
            requires=IS_NOT_EMPTY(),
            label=T('Description')),
        Field('Startdate', 'date', required=True,
            requires=IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                      minimum=datetime.date(1900,1,1),
                                      maximum=datetime.date(2999,1,1)),
            represent=represent_date,
            label=T("Start date"),
            widget=os_datepicker_widget),
        Field('Enddate', 'date', required=True,
            requires=IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                 minimum=datetime.date(1900,1,1),
                                 maximum=datetime.date(2999,1,1)),
            represent=represent_date,
            label=T("End date"),
            widget=os_datepicker_widget),
        Field('school_locations_ids', 'list:reference school_locations', #NOTE: field depricated from 3.02
              readable=False,
              writable=False,
              represent=represent_school_locations_ids,
              label = T('Locations'),
              widget = SQLFORM.widgets.checkboxes.widget,
              #requires=IS_IN_DB(db, 'school_locations.id', '%(Name)s', multiple=True),
              ),
        Field('Classes', 'boolean', required=True,
            label=T('Classes')),
        Field('Shifts', 'boolean',
            readable=False,
            writable=False,
            default=True ))


def define_school_holidays_locations():
    db.define_table('school_holidays_locations',
        Field('school_holidays_id', db.school_holidays),
        Field('school_locations_id', db.school_locations))


def represent_school_locations_ids(value, row):
    """
        Represent school_locations_ids
    """
    if value is None:
        r_value = ''
    else:
        r_value = SPAN()
        for location in value:
            location = locations_dict.get(location, '')
            r_value.append(os_gui.get_label('info', location))
            r_value.append(' ')

    return r_value


def define_schedule_classes_status():
    statuses = [ ["",      T("Open") ],
                 ["final", T("Final")] ]

    db.define_table('schedule_classes_status',
        Field('ScheduleYear', 'integer', required=True,
            requires=IS_NOT_EMPTY()),
        Field('ScheduleWeek', 'integer', required=True,
            requires=IS_NOT_EMPTY()),
        Field('Status', required=True,
            requires=IS_IN_SET(statuses, zero=None))
        )


def define_schedule_staff_status():
    statuses = [ ["",      T("Open") ],
                 ["final", T("Final")] ]

    db.define_table('schedule_staff_status',
        Field('ScheduleYear', 'integer', required=True,
            requires=IS_NOT_EMPTY()),
        Field('ScheduleWeek', 'integer', required=True,
            requires=IS_NOT_EMPTY()),
        Field('Status', required=True,
            requires=IS_IN_SET(statuses, zero=None))
        )


def define_messages():
    db.define_table('messages',
        Field('created_at', 'datetime',
            default=datetime.datetime.now()),
        Field('msg_subject'),
        Field('msg_content', 'text'),
        )


def define_customers_messages():
    db.define_table('customers_messages',
        Field('auth_customer_id', db.auth_user, required=True,
            readable=False,
            writable=False,
            label=T('CustomerID')),
        Field('messages_id', db.messages,
              readable=False,
              writable=False),
        Field('Status',
              requires=IS_IN_SET(message_statuses),
              represent=represent_message_status),
        Field('CreatedOn', 'datetime',
              readable=False,
              writable=False,
              default=datetime.datetime.now(),
              represent=represent_datetime),
        )


def define_payment_batches():
    loc_query = (db.school_locations.Archived == False)
    pc_query = (db.payment_categories.Archived == False)


    pcID_requires = IS_IN_DB(db(pc_query),
                             'payment_categories.id',
                             '%(Name)s',
                             zero=T("Please select..."))

    #if not request.is_scheduler and not request.is_shell:
    if 'export' in request.vars:
        if request.vars['export'] == 'collection':
            pc_query &= (db.payment_categories.CategoryType == 0)
            pcID_requires= IS_IN_DB(db(pc_query),
                                    'payment_categories.id',
                                    '%(Name)s',
                                    zero=None)
            payment_categories_id_zero = None
        elif request.vars['export'] == 'payment':
            pc_query &= (db.payment_categories.CategoryType == 1)
            pcID_requires= IS_IN_DB(db(pc_query),
                                    'payment_categories.id',
                                    '%(Name)s',
                                    zero=None)
            payment_categories_id_zero = None

    statuses = get_payment_batches_statuses()
    db.define_table('payment_batches',
        Field('BatchType',
            readable=False,
            writable=False,
            requires=IS_IN_SET([['collection', T('Collection')],
                                ['payment', T('Payment') ]])),
        Field('Status',
            requires=IS_IN_SET(statuses),
            represent=represent_payment_batch_status),
        Field('Name',
            requires=IS_NOT_EMPTY(),
            label=T("Batch Name")),
        Field('BatchTypeDescription',
              # readable=False,
              writable=False,
              requires=IS_EMPTY_OR(IS_IN_SET(payment_batchtypes)),
              represent=represent_payment_batchtypes,
              label=T('Batch Type')),
        Field('payment_categories_id', db.payment_categories,
            requires=pcID_requires,
            represent=lambda value, row: paycat_dict.get(value, ""),
            label=T("Category")),
        Field('Description',
            readable=False,
            writable=False,
            requires=IS_NOT_EMPTY(),
            label=T("Bank statement description")),
        Field('ColYear', 'integer',
            requires=IS_INT_IN_RANGE(1000,9999,
                error_message=T("Please enter a year.")),
            default=TODAY_LOCAL.year,
            represent=lambda value, row: value or '',
            label=T("Year")),
        Field('ColMonth', 'integer',
            requires=IS_IN_SET(get_months_list()),
            represent=NRtoMonth,
            default=TODAY_LOCAL.month,
            label=T("Month")),
        Field('Exdate', 'date',
            requires=IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                      minimum=datetime.date(1900,1,1),
                                      maximum=datetime.date(2999,1,1)),
            represent=represent_date,
            label=T("Execution date"),
            widget=os_datepicker_widget),
        Field('IncludeZero', 'boolean',
            default=False,
            label=T('Include lines with amount 0')),
        Field('school_locations_id', db.school_locations,
            readable=False,
            writable=False,
            requires=IS_EMPTY_OR(IS_IN_DB(db(loc_query),
                                          'school_locations.id',
                                          '%(Name)s',
                                          zero=T('All'))),
            represent=lambda value, row: locations_dict.get(value, T('All')),
            label=T("Location")),
        Field('Note', 'text'),
        Field('Created_at', 'datetime',
            readable=False,
            writable=False,
            default=datetime.datetime.now(),
            represent=represent_datetime),
        )


def define_payment_batches_items():
    db.define_table('payment_batches_items',
        Field('payment_batches_id', db.payment_batches),
        Field('auth_customer_id', db.auth_user,
            label=T('CustomerID')),
        Field('customers_subscriptions_id', db.customers_subscriptions,
            represent = lambda value, row: value or '',
            label=T("Subscriptions ID")),
        Field('invoices_id', db.invoices,
            represent = lambda value, row: value or '',
            label=T("Invoices ID")),
        Field('AccountHolder',
            represent=lambda value, row: value or "",
            label=T("Account holder")),
        Field('BIC',
            represent=lambda value, row: value or "",
            label=T("BIC")),
        Field('AccountNumber',
            represent=lambda value, row: value or "",
            label=T("Account number")),
        Field('MandateSignatureDate', 'date',
            requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                      minimum=datetime.date(1900,1,1),
                                      maximum=datetime.date(2999,1,1))),
            label=T("Mandate signature date"),
            widget=os_datepicker_widget),
        Field('MandateReference',
            represent=lambda value, row: value or SPAN(T("Not set"), _class='text-red'),
            label=T("Mandate reference")),
        Field('Amount', 'float',
            requires=IS_EMPTY_OR(IS_FLOAT_IN_RANGE(0,99999999, dot='.',
                                 error_message=T('Too small or too large'))),
            represent=represent_float_as_amount,
            label=T("Amount")),
        Field('Currency',
            requires=IS_NOT_EMPTY()),
        Field('Description',
            requires=IS_NOT_EMPTY()),
        Field('BankName',
            represent=lambda value, row: value or "",
            label=T("Bank name")),
        Field('BankLocation',
            represent=lambda value, row: value or "",
            label=T("Bank location"))
    )


def define_payment_batches_exports():
    try:
        auth_user_id_default = auth.user.id
    except AttributeError:
        auth_user_id_default = 1 # default to admin when not signed in

    db.define_table('payment_batches_exports',
        Field('payment_batches_id', db.payment_batches),
        Field('auth_user_id', db.auth_user,
            default=auth_user_id_default),
        Field('FirstCustomers', 'boolean',
            default=False),
        Field('RecurringCustomers', 'boolean',
            default=False),
        Field('Created_at', 'datetime',
            readable=False,
            writable=False,
            default=datetime.datetime.now(),
            represent=represent_datetime )
    )


# Deprecated from 2019.02.x
def define_invoices_workshops_products_customers():
    """
        Table to link workshop products to invoices
    """
    db.define_table('invoices_workshops_products_customers',
        Field('invoices_id', db.invoices,
            readable=False,
            writable=False),
        Field('workshops_products_customers_id', db.workshops_products_customers,
            readable=False,
            writable=False))


def define_invoices_items_workshops_products_customers():
    """
        Table to link workshop products to invoices
    """
    db.define_table('invoices_items_workshops_products_customers',
        Field('invoices_items_id', db.invoices_items,
            readable=False,
            writable=False),
        Field('workshops_products_customers_id', db.workshops_products_customers,
            readable=False,
            writable=False))


def define_invoices_customers():
    """
        Table to link customers to invoices
    """
    db.define_table('invoices_customers',
        Field('invoices_id', db.invoices,
            readable=False,
            writable=False),
        Field('auth_customer_id', db.auth_user,
              writable=False,
              label=T('Customer')))


# Deprecated from 2019.02.x
def define_invoices_customers_memberships():
    """
        Table to link customer memberships to invoices
    """
    db.define_table('invoices_customers_memberships',
        Field('invoices_id', db.invoices,
            readable=False,
            writable=False),
        Field('customers_memberships_id', db.customers_memberships,
            readable=False,
            writable=False))


def define_invoices_items_customers_memberships():
    """
        Table to link customer memberships to invoice items
    """
    db.define_table('invoices_items_customers_memberships',
        Field('invoices_items_id', db.invoices_items,
            readable=False,
            writable=False),
        Field('customers_memberships_id', db.customers_memberships,
            readable=False,
            writable=False))


# Deprecated from 2019.02.x
def define_invoices_customers_subscriptions():
    """
        Table to link customer subscriptions to invoices
    """
    db.define_table('invoices_customers_subscriptions',
        Field('invoices_id', db.invoices,
            readable=False,
            writable=False),
        Field('customers_subscriptions_id', db.customers_subscriptions,
            readable=False,
            writable=False))


def define_invoices_items_customers_subscriptions():
    """
        Table to link customer subscriptions to invoices
    """
    db.define_table('invoices_items_customers_subscriptions',
        Field('invoices_items_id', db.invoices_items,
            readable=False,
            writable=False),
        Field('customers_subscriptions_id', db.customers_subscriptions,
            readable=False,
            writable=False))


# Deprecated from 2019.02.x
def define_invoices_customers_classcards():
    """
        Table to link customer classcards to invoices
    """
    db.define_table('invoices_customers_classcards',
        Field('invoices_id', db.invoices,
            readable=False,
            writable=False),
        Field('customers_classcards_id', db.customers_classcards,
            readable=False,
            writable=False))


def define_invoices_items_customers_classcards():
    """
        Table to link customer classcards to invoice items
    """
    db.define_table('invoices_items_customers_classcards',
        Field('invoices_items_id', db.invoices_items,
            readable=False,
            writable=False),
        Field('customers_classcards_id', db.customers_classcards,
            readable=False,
            writable=False))


# Deprecated from 2019.02.x
def define_invoices_employee_claims():
    """
        Table to link employee claims to invoices
    """
    db.define_table('invoices_employee_claims',
        Field('invoices_id', db.invoices,
              readable=False,
              writable=False),
        Field('employee_claims_id', db.employee_claims,
              readable= False,
              writable = False,
              label=T('Employee Expense'))
    )


def define_invoices_items_employee_claims():
    """
        Table to link employee claims to invoices items
    """
    db.define_table('invoices_items_employee_claims',
        Field('invoices_items_id', db.invoices_items,
              readable=False,
              writable=False),
        Field('employee_claims_id', db.employee_claims,
              readable= False,
              writable = False,
              label=T('Employee Expense'))
    )


# Deprecated from 2019.02.x
def define_invoices_teachers_payment_classes():
    """
        Table to link teacher payment classes to invoices
    """
    db.define_table('invoices_teachers_payment_classes',
        Field('invoices_id', db.invoices,
            readable=False,
            writable=False),
        Field('teachers_payment_classes_id', db.teachers_payment_classes,
              readable= False,
              writable = False,
              label=T('Teacher payment class')
              )
    )


def define_invoices_items_teachers_payment_classes():
    """
        Table to link teacher payment classes to invoice items
    """
    db.define_table('invoices_items_teachers_payment_classes',
        Field('invoices_items_id', db.invoices_items,
            readable=False,
            writable=False),
        Field('teachers_payment_classes_id', db.teachers_payment_classes,
              readable= False,
              writable = False,
              label=T('Teacher payment class')
              )
    )


def define_invoices_customers_orders():
    """
        Table to link customers_orders to invoices
    """
    db.define_table('invoices_customers_orders',
        Field('invoices_id', db.invoices,
            readable=False,
            writable=False),
        Field('customers_orders_id', db.customers_orders,
            readable=False,
            writable=False))


def define_invoices_classes_attendance():
    """
        Table to link invoices to class attendance
    """
    db.define_table('invoices_classes_attendance',
        Field('invoices_id', db.invoices,
              readable=False,
              writable=False),
        Field('classes_attendance_id', db.classes_attendance,
            readable=False,
            writable=False))


def define_invoices_groups():
    db.define_table('invoices_groups',
        Field('Archived', 'boolean',
            readable=False,
            writable=False,
            default=False,
            label=T("Archived")),
        Field('PublicGroup', 'boolean',
              default=True,
              label=T('Public'),
              comment=T("Show this group in customer profiles")),
        Field('Name',
            requires=IS_NOT_EMPTY(),
            label=T('Group name')),
        Field('NextID', 'integer',
            default=1,
            label=T("Next invoice #")),
        Field('DueDays', 'integer',
            default=30,
            requires=IS_INT_IN_RANGE(1, 366,
                                     error_message=T('Please enter a number')),
            label=T('Invoices due after (days)')),
        Field('InvoicePrefix',
            default='INV',
            label=T('Invoice prefix')),
        Field('PrefixYear', 'boolean',
            default=True,
            label=T('Prefix year'),
            comment=T("Prefix the year to an invoice number eg. INV20181")),
        Field('AutoResetPrefixYear', 'boolean',
            default=True,
            label=T('Auto reset numbering'),
            comment=T("Automatically reset invoice numbering to 1 when creating the first invoice of a new year. This setting only takes effect when Prefix year is enabled.")),
        Field('Terms', 'text',
              label=T("Terms")),
        Field('Footer', 'text',
              label=T("Footer")),
        Field('JournalID',
              represent=lambda value, row: value or '',
              label=T("Journal ID"),
              comment=T(
                  "Journal ID / Code in your accounting software. All invoices in this group will be mapped to this journal.")),
        format='%(Name)s')


def define_invoices_groups_product_types():
    """
        Table to hold default invoice group assignments to certain categories
        of products
    """
    product_types = get_invoices_groups_product_types()
    group_query = (db.invoices_groups.Archived == False)

    db.define_table('invoices_groups_product_types',
        Field('ProductType',
            readable=False,
            writable=False,
            requires=IS_IN_SET(product_types),
            label=T("Type of product")),
        Field('invoices_groups_id', db.invoices_groups,
            requires=IS_IN_DB(db(group_query),
                              'invoices_groups.id',
                              '%(Name)s',
                              zero=T("Please select...")),
            label=T('Invoice group')),
        )


def define_invoices():
    months = get_months_list()

    group_query = (db.invoices_groups.Archived == False)

    db.define_table('invoices',
        Field('invoices_groups_id', db.invoices_groups,
            readable=False,
            writable=False,
            requires=IS_IN_DB(db(group_query),
                              'invoices_groups.id',
                              '%(Name)s',
                              zero=T("Please select...")),
            label=T('Invoice group')),
        Field('payment_methods_id', db.payment_methods,
            requires=IS_EMPTY_OR(
                     IS_IN_DB(db,'payment_methods.id','%(Name)s',
                              error_message=T("Please select a payment method"),
                              zero=T("Not set"))),
            represent=lambda value, row: payment_methods_dict.get(value),
            label=T("Payment method")),
        Field('SubscriptionMonth', 'integer',
            readable=False,
            writable=False,
            requires=IS_IN_SET(months, zero=T('Please select...')),
            represent=NRtoMonth,
            default=TODAY_LOCAL.month,
            label=T('Month')),
        Field('SubscriptionYear', 'integer',
            readable=False,
            writable=False,
            default=TODAY_LOCAL.year,
            label=T('Year')),
        Field('TeacherPayment', 'boolean',
            readable=False,
            writable=False,
            default=False),
        Field('EmployeeClaim', 'boolean',
            readable=False,
            writable=False,
            default=False),
        Field('CustomerCompany',
              label=T('Company')),
        Field('CustomerCompanyRegistration',
            label=T("Company Registration")),
        Field('CustomerCompanyTaxRegistration',
            label=T("Company Tax Registration")),
        Field('CustomerName',
              represent=lambda value, row: value or '',
              label=T('Name')),
        Field('CustomerListName',
              compute=compute_invoices_CustomerListName,
              represent=lambda value, row: value or '',
              label=T('To')),
        Field('CustomerAddress', 'text',
              label=T('Address')),
        Field('Status',
            default='draft',
            requires=IS_IN_SET(invoice_statuses, zero=None),
            represent=represent_invoice_status,
            label=T("Status")),
        Field('InvoiceID',
            represent=represent_invoices_invoiceid,
            label=T("Invoice #")),
        Field('Description',
            label=T('Summary')),
        Field('DateCreated', 'date',
            default=TODAY_LOCAL,
            requires=IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                      minimum=datetime.date(1900,1,1),
                                      maximum=datetime.date(2999,1,1)),
            represent=represent_date,
            label = T("Date"),
            widget=os_datepicker_widget),
        Field('DateDue', 'date', required=False,
            default=TODAY_LOCAL,
            requires=IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                      minimum=datetime.date(1900,1,1),
                                      maximum=datetime.date(2999,1,1)),
            represent=represent_invoices_datedue,
            label=T("Due"),
            widget=os_datepicker_widget),
        Field('Terms', 'text',
            label=T("Terms")),
        Field('Footer', 'text',
            label=T("Footer")),
        Field('Note', 'text',
            label=T("Note")),
        Field('ExactOnlineSalesEntryID',
            readable=False,
            writable=False),
        Field('Created_at', 'datetime',
            readable=False,
            writable=False,
            default=datetime.datetime.now(),
            represent=represent_datetime ),
        Field('Updated_at', 'datetime',
            readable=False,
            writable=False,
            default=datetime.datetime.now(),
            represent=represent_datetime ),
        Field('credit_invoice_for', 'integer', # db.invoices.id this invoice is a credit invoice for
            readable=False,
            writable=False)
        )


def compute_invoices_CustomerListName(row):
    if row.CustomerCompany:
        return row.CustomerCompany

    return row.CustomerName

    # sorted_payment_methods = [dict(id='', Name=T("Not set"))]
    # payment_methods = db(db.payment_methods).select(orderby=db.payment_methods.id)
    # for method in payment_methods:
    #     sorted_payment_methods.append(dict(Name=method.Name, id=method.id))
    #
    # db.invoices.payment_methods_id.widget = lambda f, v: \
    #     SELECT([OPTION(i['Name'],
    #         _value=i['id']) for i in sorted_payment_methods],
    #         _name=f.name, _id="%s_%s" % (f._tablename, f.name),
    #         _value=v,
    #         value=v)


def represent_invoices_invoiceid(value, row):
    """
    :param value: db.invoices.InvoiceID
    :param row: gluon.dal.row
    :return: link to invoice
    """
    if not value:
        return ''

    if request.controller == 'profile' or request.controller == 'shop':
        return value
    else:
        try:
            iID = row.invoices.id
        except:
            iID = row.id


        return A(value,
                 _href=URL('invoices', 'edit', vars={'iID':iID}, extension=''))



def represent_invoices_datedue(date, row):
    """
        Try to set a represent date, but if the supplied row doesn't have
        the required fields, just don't do anything. We won't need this field
        anyway in that case.
    """
    try:
        if date is None:
            return ""
        else:
            today = TODAY_LOCAL
            try:
                status = row.Status
            except AttributeError:
                status = row.invoices.Status
            if date < today and status == 'sent':
                return SPAN(date.strftime(DATE_FORMAT), _class='bold red')
            else:
                return SPAN(date.strftime(DATE_FORMAT))

    except AttributeError:
        pass


def define_invoices_payments():
    db.define_table('invoices_payments',
        Field('invoices_id', db.invoices,
            readable=False,
            writable=False),
        Field('Amount', 'float',
            requires=IS_EMPTY_OR(IS_FLOAT_IN_RANGE(-999999999, 999999999, dot='.',
                                          error_message=T('Please enter an amount'))),
            represent=represent_float_as_amount,
            default=0,
            label=T("Amount")),
        Field('PaymentDate', 'date', required=True,
            default=TODAY_LOCAL,
            requires=IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                      minimum=datetime.date(1900,1,1),
                                      maximum=datetime.date(2999,1,1)),
            represent=represent_date,
            label=T("Payment date"),
            widget=os_datepicker_widget),
        Field('payment_methods_id', db.payment_methods, required=True,
            requires=IS_IN_DB(db,'payment_methods.id','%(Name)s',
                              error_message=T("Please select a payment method"),
                              zero=T("Please select...")),
            represent=lambda value, row: payment_methods_dict.get(value),
            label=T("Payment method")),
        Field('Note', 'text',
            represent=lambda value, row: value or '',
            label=T("Note")),
        Field('mollie_payment_id',
            readable=False,
            writable=False)
        )

    # sorted_payment_methods = [dict(id='', Name=T("Please select..."))]
    # payment_methods = db(db.payment_methods).select(orderby=db.payment_methods.id)
    # for method in payment_methods:
    #     sorted_payment_methods.append(dict(Name=method.Name, id=method.id))
    #
    # db.invoices_payments.payment_methods_id.widget = lambda f, v: \
    #     SELECT([OPTION(i['Name'],
    #         _value=i['id']) for i in sorted_payment_methods],
    #         _name=f.name, _id="%s_%s" % (f._tablename, f.name),
    #         _value=v,
    #         value=v)


def define_invoices_mollie_payment_ids():
    db.define_table('invoices_mollie_payment_ids',
        Field('invoices_id', db.invoices,
            label=T('Invoices_id')),
        Field('mollie_payment_id',
            label=T('Mollie payment id')),
        Field('RecurringType',
            readable=False,
            writable=False),
        Field('WebhookURL',
            readable=False,
            writable=False),
        Field('CreatedOn', 'datetime',
            readable=False,
            writable=False,
            default=datetime.datetime.now(),
            represent=represent_datetime)
    )


def represent_invoice_status(value, row):
    """
        Returns label for invoice status
    """
    label = ''

    if value == 'draft':
        label_class = 'default'
    if value == 'sent':
        label_class = 'primary'
    if value == 'paid':
        label_class = 'success'
    if value == 'cancelled':
        label_class = 'warning'

    for status, text in invoice_statuses:
        if status == value:
            label = os_gui.get_label(label_class, text)

    return label


def define_invoices_items():
    ac_query = (db.accounting_costcenters.Archived == False)
    ag_query = (db.accounting_glaccounts.Archived == False)

    db.define_table('invoices_items',
        Field('invoices_id', db.invoices,
            readable=False,
            writable=False),
        Field('Sorting', 'integer',
            readable=False,
            writable=False),
        Field('ProductName',
            requires=IS_NOT_EMPTY(error_message = T("Enter product name")),
            label   =T("Product Name")),
        Field('Description', 'text',
            label=T("Description")),
        Field('Quantity', 'double',
            requires=IS_FLOAT_IN_RANGE(-100000, 1000000, dot=".",
                     error_message=T("Enter a number, decimals use '.'")),
            default=1,
            label=T("Quantity")),
        Field('Price', 'double',
            represent=represent_float_as_amount,
            default=0,
            label=T("Price")),
        Field('tax_rates_id', db.tax_rates,
            requires=IS_EMPTY_OR(IS_IN_DB(db(),
                                  'tax_rates.id',
                                  '%(Name)s')),
            represent=represent_tax_rate,
            label=T("Tax rate")),
        Field('TotalPriceVAT', 'double',
            compute=lambda row: row.Price * row.Quantity,
            represent=represent_float_as_amount),
        Field('VAT', 'double',
            compute=compute_invoice_item_vat,
            represent=represent_float_as_amount),
        Field('TotalPrice', 'double',
            compute=compute_invoice_item_total_price,
            represent=represent_float_as_amount),
        Field('accounting_glaccounts_id', db.accounting_glaccounts,
              requires=IS_EMPTY_OR(IS_IN_DB(db(ag_query),
                                            'accounting_glaccounts.id',
                                            '%(Name)s')),
              represent=represent_accounting_glaccount,
              label=T('G/L Account'),
              comment=T('General ledger account ID in your accounting software')),
        Field('accounting_costcenters_id', db.accounting_costcenters,
            requires=IS_EMPTY_OR(IS_IN_DB(db(ac_query),
                                          'accounting_costcenters.id',
                                          '%(Name)s')),
            represent=represent_accounting_costcenter,
            label=T("Cost center")),
        Field('ExactOnlineSalesEntryLineID',
            readable=False,
            writable=False),
    )


def compute_invoice_item_total_price(row):
    """
        Returns the total price for an invoice item
    """
    total_price_vat = Decimal(row.TotalPriceVAT)

    total = Decimal(Decimal(total_price_vat - row.VAT).quantize(Decimal('.01'),
                                                                rounding=ROUND_HALF_UP))
    return total


def compute_invoice_item_vat(row):
    """
        Returns the vat for an invoice item
    """
    tID = row.tax_rates_id
    if not tID:
        vat = 0
    else:
        vat_rate = db.tax_rates(tID).Percentage / 100

        total_price_vat = float(row.TotalPriceVAT)
        vat = total_price_vat - (total_price_vat / (1 + vat_rate))

        vat = Decimal(Decimal(vat).quantize(Decimal('.01'),
                                            rounding=ROUND_HALF_UP))

    return vat


def define_invoices_amounts():
    db.define_table('invoices_amounts',
        Field('invoices_id', db.invoices),
        Field('TotalPrice', 'double',
            default=0,
            represent=represent_float_as_amount,
            label=T("Subtotal")),
        Field('VAT', 'double',
            default=0,
            represent=represent_float_as_amount,
            label=T("VAT")),
        Field('TotalPriceVAT', 'double',
            default=0,
            represent=represent_float_as_amount,
            label=T("Total")),
        Field('Paid', 'double',
            default=0,
            represent=represent_float_as_amount,
            ),
        Field('Balance', 'double',
            compute=compute_invoices_amounts_balance,
            default=0,
            represent=represent_float_as_amount)
        )


def compute_invoices_amounts_balance(row):
    """
        Calculates the balance for an invoice amounts row
    """
    return row.TotalPriceVAT - row.Paid



def define_receipts():
    db.define_table('receipts',
        Field('payment_methods_id', db.payment_methods,
            requires=IS_EMPTY_OR(
                     IS_IN_DB(db,'payment_methods.id','%(Name)s',
                              error_message=T("Please select a payment method"),
                              zero=T("Not set"))),
            represent=lambda value, row: payment_methods_dict.get(value),
            label=T("Payment method")),
        Field('CreatedBy', db.auth_user,
            writable=False,
            label=T("Employee")),
        Field('CreatedOn', 'datetime',
            writable=False,
            default=datetime.datetime.now(),
            represent=represent_datetime,
            label=T("Time")),
        Field('UpdatedOn', 'datetime',
            readable=False,
            writable=False,
            default=datetime.datetime.now(),
            represent=represent_datetime ),
        )

    try:
        db.receipts.CreatedBy.default = auth.user.id
    except AttributeError:
        pass


def define_receipts_items():
    ac_query = (db.accounting_costcenters.Archived == False)
    ag_query = (db.accounting_glaccounts.Archived == False)

    db.define_table('receipts_items',
        Field('receipts_id', db.receipts,
            readable=False,
            writable=False),
        Field('Sorting', 'integer',
            readable=False,
            writable=False),
        Field('ProductName',
            requires=IS_NOT_EMPTY(error_message = T("Enter product name")),
            label   =T("Product Name")),
        Field('Description', 'text',
            label=T("Description")),
        Field('Quantity', 'double',
            requires=IS_FLOAT_IN_RANGE(-100000, 1000000, dot=".",
                     error_message=T("Enter a number, decimals use '.'")),
            default=1,
            label=T("Quantity")),
        Field('Price', 'double',
            represent=represent_float_as_amount,
            default=0,
            label=T("Price")),
        Field('tax_rates_id', db.tax_rates,
            requires=IS_EMPTY_OR(IS_IN_DB(db(),
                                  'tax_rates.id',
                                  '%(Name)s')),
            represent=represent_tax_rate,
            label=T("Tax rate")),
        Field('TotalPriceVAT', 'double',
            compute=lambda row: row.Price * row.Quantity,
            represent=represent_float_as_amount),
        Field('VAT', 'double',
            compute=compute_receipt_item_vat,
            represent=represent_float_as_amount),
        Field('TotalPrice', 'double',
            compute=compute_receipt_item_total_price,
            represent=represent_float_as_amount),
        Field('accounting_glaccounts_id', db.accounting_glaccounts,
              requires=IS_EMPTY_OR(IS_IN_DB(db(ag_query),
                                            'accounting_glaccounts.id',
                                            '%(Name)s')),
              represent=represent_accounting_glaccount,
              label=T('G/L Account'),
              comment=T('General ledger account ID in your accounting software')),
        Field('accounting_costcenters_id', db.accounting_costcenters,
              requires=IS_EMPTY_OR(IS_IN_DB(db(ac_query),
                                            'accounting_costcenters.id',
                                            '%(Name)s')),
              represent=represent_accounting_costcenter,
              label=T("Cost center"),
              comment=T("Cost center code in your accounting software")),
        # How are receipts processed in Exact Online?
    )


def compute_receipt_item_total_price(row):
    """
        Returns the total price for an receipt item
    """
    total_price_vat = Decimal(row.TotalPriceVAT)

    total = Decimal(Decimal(total_price_vat - row.VAT).quantize(Decimal('.01'),
                                                                rounding=ROUND_HALF_UP))
    return total


def compute_receipt_item_vat(row):
    """
        Returns the vat for an receipt item
    """
    tID = row.tax_rates_id
    if not tID:
        vat = 0
    else:
        vat_rate = db.tax_rates(tID).Percentage / 100

        total_price_vat = float(row.TotalPriceVAT)
        vat = total_price_vat - (total_price_vat / (1 + vat_rate))

        vat = Decimal(Decimal(vat).quantize(Decimal('.01'),
                                            rounding=ROUND_HALF_UP))

    return vat


def define_receipts_amounts():
    db.define_table('receipts_amounts',
        Field('receipts_id', db.invoices),
        Field('TotalPrice', 'double',
            default=0,
            represent=represent_float_as_amount,
            label=T("Subtotal")),
        Field('VAT', 'double',
            default=0,
            represent=represent_float_as_amount,
            label=T("VAT")),
        Field('TotalPriceVAT', 'double',
            default=0,
            represent=represent_float_as_amount,
            label=T("Total")),
        Field('Paid', 'double',
            default=0,
            represent=represent_float_as_amount,
            ),
        )


def compute_receipts_amounts_balance(row):
    """
        Calculates the balance for an receipts amounts row
    """
    return row.TotalPriceVAT - row.Paid


def define_receipts_items_shop_sales():
    db.define_table('receipts_items_shop_sales',
        Field('shop_sales_id', db.shop_sales,
              readable=False,
              writable=False),
        Field('receipts_items_id', db.receipts_items,
              readable=False,
              writable=False)
    )


def represent_tax_rate(value, row):
    """
        Returns name for a tax rate
    """
    name = ''
    if value:
        name = db.tax_rates(value).Name

    return name


def define_tax_rates():
    float_error = T('Please enter a value between 0 and 100')

    db.define_table('tax_rates',
        Field('Archived', 'boolean',
            readable=False,
            writable=False,
            default=False,
            label=T("Archived")),
        Field('Name',
            requires=IS_NOT_EMPTY(),
            label=T('Name')),
        Field('Percentage', 'float',
            requires=IS_FLOAT_IN_RANGE(0,100, dot='.',
                                       error_message=float_error),
            comment='A percentage as numbers only is expected (without %). Use " . " for decimals.',
            label=T('Percentage')),
        Field('VATCodeID',
            represent=lambda value, row: value or '',
            label=T("VAT Code ID"),
            comment=T("VAT Code in your accounting software.")),
        format='%(Name)s'
    )


def define_postcode_groups():
    """
        Create groups for postcodes
    """
    db.define_table('postcode_groups',
        Field('Archived', 'boolean',
            readable=False,
            writable=False,
            default=False,
            label=T("Archived")),
        Field('Name',
            requires=IS_NOT_EMPTY(),
            label=T('Name')),
        Field('PostcodeStart',
            requires=[IS_NOT_EMPTY(), IS_UPPER()],
            label=T('From postcode')),
        Field('PostcodeStart_AsInt', 'integer',
            readable=False,
            writable=False,
            compute=lambda row: string_to_int(row.PostcodeStart),
            label=T('From postcode as int')),
        Field('PostcodeEnd',
            requires=[IS_NOT_EMPTY(), IS_UPPER()],
            label=T('Until postcode')),
        Field('PostcodeEnd_AsInt', 'integer',
            readable=False,
            writable=False,
            compute=lambda row: string_to_int(row.PostcodeEnd),
            label=T('Until postcode as int')),
        format='%(Name)s'
    )


def define_shifts():
    weekdays = [('1',T('Monday')),
                ('2',T('Tuesday')),
                ('3',T('Wednesday')),
                ('4',T('Thursday')),
                ('5',T('Friday')),
                ('6',T('Saturday')),
                ('7',T('Sunday'))]

    loc_query = (db.school_locations.Archived == False)
    ss_query = (db.school_shifts.Archived == False)

    db.define_table('shifts',
        Field('school_locations_id', db.school_locations, required=True,
            requires=IS_IN_DB(db(loc_query),
                              'school_locations.id',
                              '%(Name)s',
                              zero=T("Please select...")),
            #represent=lambda value, row: locations_dict.get(value, T("No location")),
            label=T("Location")),
        Field('school_shifts_id', db.school_shifts, required=True,
            requires=IS_IN_DB(db(ss_query),
                              'school_shifts.id',
                              '%(Name)s',
                              zero=T("Please select...")),
            #represent=lambda value, row: s_dict.get(value, T("No classtype")),
            label=T("Shift")),
        Field('Week_day', 'integer', required=True,
            requires=IS_IN_SET(weekdays),
            represent=NRtoDay,
            label=T("Weekday")),
        Field('Starttime', 'time', required=True,
            requires=IS_TIME(error_message='must be HH:MM'),
            represent=lambda value, row: value.strftime('%H:%M'),
            widget=os_time_widget,
            label=T("Start")),
        Field('Endtime', 'time', required=True,
            requires=IS_TIME(error_message='must be HH:MM'),
            represent=lambda value, row: value.strftime('%H:%M'),
            widget=os_time_widget,
            label=T("End")),
        Field('Startdate', 'date', required=True,
            requires=IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                      minimum=datetime.date(1900,1,1),
                                      maximum=datetime.date(2999,1,1)),
            represent=represent_date,
            label=T("Start date"),
            widget=os_datepicker_widget),
        Field('Enddate', 'date', required=False,
            requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                  minimum=datetime.date(1900,1,1),
                                  maximum=datetime.date(2999,1,1))),
            represent=represent_date,
            label=T("End date"),
            widget=os_datepicker_widget),
        )


def define_shifts_otc():
    """
        Define one time change table for classes
    """
    loc_query = (db.school_locations.Archived == False)
    ss_query = (db.school_shifts.Archived == False)
    sl_query = (db.school_levels.Archived == False)
    au_query = (db.auth_user.trashed == False) & \
               (db.auth_user.employee == True)

    statuses = [['normal', T('Normal')],
                ['open', T('Open')],
                ['cancelled', T('Cancelled')]]

    db.define_table('shifts_otc',
        Field('shifts_id', db.shifts, required=True,
            readable=False,
            writable=False),
        Field('ShiftDate', 'date', required=True,
            readable=False,
            writable=False,
            requires=IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                      minimum=datetime.date(1900, 1, 1),
                                      maximum=datetime.date(2999, 1, 1)),
            represent=represent_date,
            label=T("Shift date"),
            widget=os_datepicker_widget),
        Field('Status',
            requires=IS_EMPTY_OR(IS_IN_SET(statuses)),
            label=T('Status')),
        Field('Description',
            label=T('Description')),
        Field('school_locations_id', db.school_locations,
            requires=IS_EMPTY_OR(
                IS_IN_DB(db(loc_query),
                         'school_locations.id',
                         '%(Name)s',
                         zero=T(""))),
            represent=lambda value, row: locations_dict.get(value, T("No location")),
            label=T("Location")),
        Field('school_shifts_id', db.school_shifts,
            requires=IS_EMPTY_OR(IS_IN_DB(db(ss_query),
                                          'school_shifts.id',
                                          '%(Name)s',
                                          zero=T(""))),
            label=T("Shift")),
        Field('Starttime', 'time',
            requires=IS_EMPTY_OR(IS_TIME(error_message='please insert as HH:MM')),
            represent=lambda value, row: value.strftime('%H:%M'),
            widget=os_time_widget,
            label=T("Start")),
        Field('Endtime', 'time',
            requires=IS_EMPTY_OR(IS_TIME(error_message='please insert as HH:MM')),
            represent=lambda value, row: value.strftime('%H:%M'),
            widget=os_time_widget,
            label=T("End")),
        Field('auth_employee_id', db.auth_user,
              requires=IS_EMPTY_OR(IS_IN_DB(db(au_query),
                                   'auth_user.id',
                                   '%(first_name)s %(last_name)s',
                                   zero=(T('')))),
              represent=lambda value, row: employees_dict.get(value,
                                                             None),
              # represent=lambda value, row: value or '',
              label=T("Sub Employee")),
        Field('auth_employee_id2', db.auth_user,
              requires=IS_EMPTY_OR(IS_IN_DB(db(au_query),
                                            'auth_user.id',
                                            '%(first_name)s %(last_name)s')),
              represent=lambda value, row: employees_dict.get(value,
                                                             None),
              # represent=lambda value, row: value or '',
              label=T("Sub Employee 2")),
    )


# Legacy table, depricated from 3.08
def define_shifts_sub():
    au_query = (db.auth_user.trashed == False) & \
               (db.auth_user.employee == True)

    db.define_table('shifts_sub',
        Field('shifts_id', db.shifts, required=True,
            readable=False,
            writable=False,
            label=T("ShiftsID")),
        Field('ShiftDate', 'date', required=True,
            readable=False,
            writable=False,
            requires=IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                      minimum=datetime.date(1900,1,1),
                                      maximum=datetime.date(2999,1,1)),
            label=T("Shift date"),
            widget=os_datepicker_widget),
        Field('auth_employee_id', db.auth_user,
            requires=IS_IN_DB(db(au_query),
                              'auth_user.id',
                              '%(first_name)s %(last_name)s',
                              zero=(T('Select employee...'))),
            #represent=lambda value, row: teachers_dict.get(value, None),
            #represent=lambda value, row: value or '',
            label=T("Employee")),
        Field('auth_employee_id2', db.auth_user,
            requires=IS_EMPTY_OR(IS_IN_DB(db(au_query),
                                          'auth_user.id',
                                          '%(first_name)s %(last_name)s')),
            #represent=lambda value, row: teachers_dict.get(value, None),
            #represent=lambda value, row: value or '',
            label=T("Employee 2")),
        )



def define_shifts_staff():
    au_query = (db.auth_user.trashed == False) & \
               (db.auth_user.employee == True)

    db.define_table('shifts_staff',
        Field('shifts_id', db.shifts, required=True,
            readable=False,
            writable=False),
        Field('auth_employee_id', db.auth_user,
            requires=IS_IN_DB(db(au_query),
                              'auth_user.id',
                              '%(first_name)s %(last_name)s',
                              zero=(T('Select employee...'))),
            #represent=lambda value, row: teachers_dict.get(value, None),
            #represent=lambda value, row: value or '', # when this is enabled it the schedule returns id's instead of names
            label=T("Employee")),
        Field('auth_employee_id2', db.auth_user,
            requires=IS_EMPTY_OR(IS_IN_DB(db(au_query),
                                          'auth_user.id',
                                          '%(first_name)s %(last_name)s')),
            #represent=lambda value, row: teachers_dict.get(value, None),
            #represent=lambda value, row: value or '',
            label=T("Employee 2")),
        Field('Startdate', 'date', required=True,
            requires=IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                      minimum=datetime.date(1900,1,1),
                                      maximum=datetime.date(2999,1,1)),
            represent=represent_date,
            label=T("Start date"),
            widget=os_datepicker_widget),
        Field('Enddate', 'date', required=False,
            requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                 minimum=datetime.date(1900,1,1),
                                 maximum=datetime.date(2999,1,1))),
            represent=represent_date,
            label=T("End date"),
            widget=os_datepicker_widget),
        )

# Legacy table, depricated from 3.08
def define_shifts_open():
    db.define_table('shifts_open',
        Field('shifts_id', db.shifts, required=True),
        Field('ShiftDate', 'date', required=True,
            requires=IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                      minimum=datetime.date(1900,1,1),
                                      maximum=datetime.date(2999,1,1)))
        )

# Legacy table, depricated from 3.08
def define_shifts_cancelled():
    db.define_table('shifts_cancelled',
        Field('shifts_id', db.shifts, required=True),
        Field('ShiftDate', 'date', required=True,
            requires=IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                      minimum=datetime.date(1900,1,1),
                                      maximum=datetime.date(2999,1,1)))
        )


def define_customers_shoppingcart():
    """
        Table to hold shopping cart entries
    """
    types = [ (1,T("Trial class")),
              (2,T("Drop In")) ]

    db.define_table('customers_shoppingcart',
        Field('auth_customer_id', db.auth_user, required=True,
            readable=False,
            writable=False,
            label=T('CustomerID')),
        Field('workshops_products_id', db.workshops_products,
            label=T('Workshop Product')),
        Field('school_classcards_id', db.school_classcards,
            label=T('Class card')),
        Field('classes_id', db.classes,
            label=T('Class')),
        Field('ClassDate', 'date',
            readable=False,
            writable=False,
            requires=IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                      minimum=datetime.date(1900, 1, 1),
                                      maximum=datetime.date(2999, 1, 1)),
            represent=represent_date,
            label=T("Class date"),
            widget=os_datepicker_widget),
        Field('AttendanceType', 'integer',
            requires=IS_IN_SET(types),
            represent=lambda value, row: session.att_types_dict.get(value, ""),
            label=T("Type")),
        Field('CreatedOn', 'datetime',
              readable=False,
              writable=False,
              default=datetime.datetime.now(),
              represent=represent_datetime)
        )


def define_customers_orders():
    """
        Table to hold orders made through online shop for a customer
    """
    db.define_table('customers_orders',
        Field('auth_customer_id', db.auth_user, required=True,
            readable=False,
            writable=False,
            label=T('Customer')),
        Field('Donation', 'boolean',
            readable=False,
            writable=False),
        Field('Status',
            requires=IS_IN_SET(order_statuses),
            represent=represent_customers_orders_status,
            default='received',
            label=T('Status')),
        Field('CustomerNote', 'text',
            label=T("Anything you'd like to tell us about this order?")),
        Field('Origin',
            requires=IS_IN_SET(customers_orders_origins),
            represent=represent_customers_orders_origin,
            label=T("Order origin"),
        ),
        Field('DateCreated', 'datetime',
              #readable=False,
              writable=False,
              represent=represent_datetime,
              default=datetime.datetime.now(),
              label=T("Order date")),
    )


def define_shop_categories():
    """
        Define shop categories
    """
    db.define_table('shop_categories',
        Field('Archived', 'boolean',
              readable=False,
              writable=False,
              default=False),
        Field('Name',
              label=T('Name')),
        Field('Description', 'text',
              label=T("Description")),
    )


def define_shop_categories_products():
    """
        Define shop categories products
    """
    db.define_table('shop_categories_products',
        Field('shop_categories_id', db.shop_categories),
        Field('shop_products_id', db.shop_products),
    )


def define_shop_products():
    """
        Define products
    """
    ac_query = (db.accounting_costcenters.Archived == False)
    ag_query = (db.accounting_glaccounts.Archived == False)

    visibility = [
        ['always', T('Always visible')],
        ['hidden', T('Hidden')],
        ['in_stock', T('Show when in stock')],
    ]

    db.define_table('shop_products',
        Field('picture', 'upload', autodelete=True,
              requires=IS_EMPTY_OR([IS_IMAGE(extensions=('jpeg', 'jpg', 'png')),
                                    IS_LENGTH(maxsize=665600,
                                              error_message=T('650KB or less'))]),  # 650KB
              label=T("Image (Max 650KB)")),
        Field('thumbsmall', 'upload',  # generate 50*50 for list view
              autodelete=True,
              readable=False,
              writable=False,
              compute=lambda row: SMARTHUMB(row.picture,
                                            (50, 50),
                                            name="Small"),
              represent=represent_shop_products_thumbsmall,
              label=T("Image")),
        Field('thumblarge', 'upload',  # generate 400*400 for edit view
              autodelete=True,
              readable=False,
              writable=False,
              compute=lambda row: SMARTHUMB(row.picture,
                                            (400, 400),
                                            name="Large"),
              represent=represent_shop_products_thumblarge),
        Field('Name',
              requires=IS_NOT_EMPTY(),
              label=T("Name")),
        Field('Description', 'text',
              label=T("Description")),
        Field('DescriptionShop', 'text',
              label=T("Descripion in shop"),
              comment=T("This is the description customers will see")),
        Field('Visibility',
              requires=IS_IN_SET(visibility, zero=None),
              default='in_stock',
              label=T('Shop visibility')),
        Field('shop_brands_id', db.shop_brands,
              requires=IS_EMPTY_OR(IS_IN_DB(db(),
                                            'shop_brands.id',
                                            '%(Name)s')),
              label=T('Brand')),
        Field('shop_suppliers_id', db.shop_suppliers,
              requires=IS_EMPTY_OR(IS_IN_DB(db(),
                                            'shop_suppliers.id',
                                            '%(Name)s')),
              label=T('Supplier')),
        Field('shop_products_sets_id', db.shop_products_sets,
              requires=IS_EMPTY_OR(IS_IN_DB(db(),
                                            'shop_products_sets.id',
                                            '%(Name)s')),
              label=T('Product set')),
        Field('accounting_glaccounts_id', db.accounting_glaccounts,
              requires=IS_EMPTY_OR(IS_IN_DB(db(ag_query),
                                            'accounting_glaccounts.id',
                                            '%(Name)s')),
              represent=represent_accounting_glaccount,
              label=T('G/L Account'),
              comment=T('General ledger account ID in your accounting software')),
        Field('accounting_costcenters_id', db.accounting_costcenters,
              requires=IS_EMPTY_OR(IS_IN_DB(db(ac_query),
                                            'accounting_costcenters.id',
                                            '%(Name)s')),
              represent=represent_accounting_costcenter,
              label=T("Cost center"),
              comment=T("Cost center code in your accounting software")),
    )


def define_shop_products_variants():
    """
        Define product variants
    """
    db.define_table('shop_products_variants',
        Field('shop_products_id', db.shop_products,
              readable=False,
              writable=False),
        Field('Enabled', 'boolean',
              readable=False,
              writable=False,
              default=True),
        Field('picture', 'upload', autodelete=True,
              requires=IS_EMPTY_OR([IS_IMAGE(extensions=('jpeg', 'jpg', 'png')),
                                    IS_LENGTH(maxsize=665600,
                                              error_message=T('650KB or less'))]),  # 650KB
              label=T("Image (Max 650KB)")),
        Field('thumbsmall', 'upload',  # generate 50*50 for list view
              autodelete=True,
              readable=False,
              writable=False,
              compute=lambda row: SMARTHUMB(row.picture,
                                            (50, 50),
                                            name="Small"),
              represent=represent_shop_products_variants_thumbsmall,
              label=T("Image")),
        Field('thumblarge', 'upload',  # generate 400*400 for edit view
              autodelete=True,
              readable=False,
              writable=False,
              compute=lambda row: SMARTHUMB(row.picture,
                                            (400, 400),
                                            name="Large"),
              represent=represent_shop_products_variants_thumblarge),
        Field('Name',
              requires=IS_NOT_EMPTY()),
        Field('Price', 'double',
              default=0,
              represent=represent_float_as_amount,
              label=T("Price incl. VAT")),
        Field('tax_rates_id', db.tax_rates,
              label=T('Tax rate')),
        Field('PurchasePrice', 'double',
              default=0,
              represent=represent_float_as_amount,
              label=T("Purchace price")),
        Field('ArticleCode',
              represent=lambda value, row: value or "",
              label=T('Article code')),
        Field('Barcode',
              label=T('Barcode'),
              comment=T("The barcode that should be linked to this product variant (For EU countries; this is where you enter the EAN)")),
        Field('SKU',
              label=T('SKU'),
              comment=T("Stock Keeping Unit")),
        Field('KeepStock', 'boolean',
              default=True,
              represent=represent_boolean_as_checkbox,
              label=T('Keep stock'),
              comment=T('Keep track of stock changes for this variant')),
        Field('StockShop', 'integer',
              default=0,
              label=T('Stock shop')),
        Field('StockWarehouse', 'integer',
              default=0,
              label=T('Stock warehouse')),
        Field('DefaultVariant', 'boolean',
              readable=False,
              writable=False,
              label=T('Default variant for a product')),
        Field('VariantCode',
              readable=False,
              writable=False),
    )


def define_shop_sales():
    """
    Define shop products sales
    :return:
    """
    db.define_table('shop_sales',
        Field('CreatedOn', 'datetime',
              writable=False,
              default=NOW_UTC,
              represent=represent_datetime,
              label=T("Time")),
        Field('ProductName',
              label=T("Product")),
        Field('VariantName',
              label=T("Variant")),
        Field('Quantity',
              label=T("Quantity")),
        Field('ArticleCode',
              represent=lambda value, row: value or '',
              label=T("Article code")),
        Field('Barcode',
              represent=lambda value, row: value or '',
              label=T("Barcode")),
    )


def define_shop_sales_products_variants():
    db.define_table('shop_sales_products_variants',
        Field('shop_sales_id', db.shop_sales,
              readable=False,
              writable=False),
        Field('shop_products_variants_id', db.shop_products_variants,
              readable=False,
              writable=False),
    )


def define_shop_products_sets():
    """
        Define products sets; sets of options that can be linked to a product
    """
    db.define_table('shop_products_sets',
        Field('Name',
              requires=IS_NOT_EMPTY(),
              label=T('Name')),
        Field('Description', 'text',
              label=T('Description'))
    )


def define_shop_products_sets_options():
    """
        Define products options
        eg. color, size, etc.
    """
    db.define_table('shop_products_sets_options',
        Field('shop_products_sets_id',
              readable=False,
              writable=False),
        Field('Name',
              requires=IS_NOT_EMPTY(),
              label=T('Name')),
    )


def define_shop_products_sets_options_values():
    """
        Define shop products options values
        eg. red, blue, etc.
    """
    db.define_table('shop_products_sets_options_values',
        Field('shop_products_sets_options_id', db.shop_products_sets_options,
              readable=False,
              writable=False
              ),
        Field('Name',
              requires=IS_NOT_EMPTY(),
              label=T('Name')),
    )


def define_shop_brands():
    """
        Define shop brands
    """
    db.define_table('shop_brands',
        Field('Archived', 'boolean',
              readable=False,
              writable=False,
              default=False),
        Field('Name',
              requires=IS_NOT_EMPTY(),
              label=T('Name')),
        Field('Description', 'text',
              label=T('Description'))
    )


def define_shop_suppliers():
    """
        Define shop suppliers
    """
    db.define_table('shop_suppliers',
        Field('Archived', 'boolean',
              readable=False,
              writable=False,
              default=False),
        Field('Name',
              requires=IS_NOT_EMPTY(),
              label=T('Name')),
        Field('Description',
              label=T('Description')),
        Field('ContactName',
              label=T('Contact name')),
        Field('ContactPhone',
              label=T('Contact phone')),
        Field('ContactEmail',
              requires=IS_EMPTY_OR(IS_EMAIL()),
              label=T('Contact email')),
        Field('CompanyAddress',
              label=T('Company address')),
        Field('CompanyCity',
              label=T('Company city')),
        Field('CompanyPostCode',
              label=T('Company postcode')),
        Field('CompanyCountry',
              label=T('Company country')),
        Field('Notes', 'text',
              label=T('Notes')),
    )


def define_shop_links():
    """
        Hold additional links in shop
    """
    db.define_table('shop_links',
        Field('Name',
              label=T('Name')),
        Field('URL',
              requires=IS_URL(),
              label=T('URL')),
    )


def represent_customers_orders_status(value, row):
    """
        Returns label for order status
    """
    label = ''

    if value == 'received':
        label_class = 'default'
    if value == 'awaiting_payment':
        label_class = 'primary'
    if value == 'paid' or value == 'processing' or value == 'delivered':
        label_class = 'success'
    if value == 'cancelled':
        label_class = 'warning'

    for status, text in order_statuses:
        if status == value:
            label = os_gui.get_label(label_class, text)

    return label


def define_customers_orders_amounts():
    db.define_table('customers_orders_amounts',
        Field('customers_orders_id', db.customers_orders),
        Field('TotalPrice', 'double',
            default=0,
            represent=represent_float_as_amount,
            label=T("Subtotal")),
        Field('VAT', 'double',
            default=0,
            represent=represent_float_as_amount,
            label=T("VAT")),
        Field('TotalPriceVAT', 'double',
            default=0,
            represent=represent_float_as_amount,
            label=T("Total")),
        Field('Paid', 'double',
            default=0,
            represent=represent_float_as_amount,
            ),
        Field('Balance', 'double',
            compute=compute_invoices_amounts_balance,
            default=0,
            represent=represent_float_as_amount)
        )


def define_customers_orders_items():
    """
        Table to hold customers_orders items
    """
    ac_query = (db.accounting_costcenters.Archived == False)
    ag_query = (db.accounting_glaccounts.Archived == False)

    types = [ (1,T("Trial class")),
              (2,T("Drop In")) ]

    db.define_table('customers_orders_items',
        Field('customers_orders_id', db.customers_orders,
            readable=False,
            writable=False),
        Field('Donation', 'boolean',
            readable=False,
            writable=False),
        Field('ProductVariant', 'boolean',
            readable=False,
            writable=False,
            default=False),
        Field('school_classcards_id', db.school_classcards,
            readable=False,
            writable=False),
        Field('school_subscriptions_id', db.school_subscriptions,
            readable=False,
            writable=False),
        Field('school_memberships_id', db.school_memberships,
            readable=False,
            writable=False),
        Field('workshops_products_id', db.workshops_products,
            readable=False,
            writable=False),
        Field('classes_id', db.classes,
            readable=False,
            writable=False),
        Field('ClassDate', 'date',
            readable=False,
            writable=False,
            requires=IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                      minimum=datetime.date(1900, 1, 1),
                                      maximum=datetime.date(2999, 1, 1)),
            represent=represent_date,
            label=T("Class date"),
            widget=os_datepicker_widget),
        Field('AttendanceType', 'integer',
            requires=IS_IN_SET(types),
            represent=lambda value, row: session.att_types_dict.get(value, ""),
            label=T("Type")),
        Field('ProductName',
              requires=IS_NOT_EMPTY(error_message=T("Enter product name")),
              label=T("Product Name")),
        Field('Description', 'text',
              label=T("Description")),
        Field('Quantity', 'double',
            requires=IS_FLOAT_IN_RANGE(-100000, 1000000,
                     error_message=T("Enter a number, decimals use '.'")),
            default=1,
            label=T("Quantity")),
        Field('Price', 'double',
              represent=represent_float_as_amount,
              default=0,
              label=T("Price")),
        Field('tax_rates_id', db.tax_rates,
              requires=IS_EMPTY_OR(IS_IN_DB(db(),
                                            'tax_rates.id',
                                            '%(Name)s')),
              represent=represent_tax_rate,
              label=T("Tax rate")),
        Field('TotalPriceVAT', 'double',
              compute=lambda row: row.Price or 0 * row.Quantity,
              represent=represent_float_as_amount),
        Field('VAT', 'double',
              compute=compute_invoice_item_vat,
              represent=represent_float_as_amount),
        Field('TotalPrice', 'double',
              compute=compute_invoice_item_total_price,
              represent=represent_float_as_amount),
        Field('accounting_glaccounts_id', db.accounting_glaccounts,
              requires=IS_EMPTY_OR(IS_IN_DB(db(ag_query),
                                            'accounting_glaccounts.id',
                                            '%(Name)s')),
              represent=represent_accounting_glaccount,
              label=T('G/L Account'),
              comment=T('General ledger account ID in your accounting software')),
        Field('accounting_costcenters_id', db.accounting_costcenters,
              requires=IS_EMPTY_OR(IS_IN_DB(db(ac_query),
                                            'accounting_costcenters.id',
                                            '%(Name)s')),
              represent=represent_accounting_costcenter,
              label=T("Cost center"),
              comment=T("Cost center code in your accounting software")),
        )


def define_customers_orders_items_shop_products_variants():
    """
    Added addition table to allow deleting of product and product variants. Adding a link to the orders_items table
    would cause all order items with that product variant to be deleted when that product variant is deleted.
    A full history of orders is always nice to have!
    """
    db.define_table('customers_orders_items_shop_products_variants',
        Field('customers_orders_items_id', db.customers_orders_items),
        Field('shop_products_variants_id', db.shop_products_variants)
    )


def define_customers_orders_mollie_payment_ids():
    db.define_table('customers_orders_mollie_payment_ids',
        Field('customers_orders_id', db.customers_orders,
            label=T('Customers_orders_id')),
        Field('mollie_payment_id',
            label=T('Mollie payment id')))


def define_mollie_log_webhook():
    db.define_table('mollie_log_webhook',
        Field('ReceivedOn', 'datetime',
            default=datetime.datetime.now()),
        Field('mollie_payment_id'),
        Field('mollie_payment', 'text'))


def define_integration_exact_online_log():
    db.define_table('integration_exact_online_log',
        Field('ActionName'),
        Field('ObjectName'),
        Field('ObjectID'),
        Field('ActionResult', 'text'),
        Field('Status',
            requires=IS_IN_SET(
                ['success', T("Success")],
                ['fail', T("Fail")],
            )),
        Field('CreatedOn', 'datetime',
            default=datetime.datetime.now())
    )


def define_customers_profile_features():
    """
        Define table to hold which features are enabled for customer logins
    """
    db.define_table('customers_profile_features',
        Field('Memberships', 'boolean',
              default=True,
              label=T('Memberships')),
        Field('Subscriptions', 'boolean',
              default=True,
              label=T('Subscriptions')),
        Field('Classes', 'boolean',
            default=True,
            label=T('Classes')),
        Field('Classcards', 'boolean',
            default=True,
            label=T('Class cards')),
        Field('Workshops', 'boolean',
            default=True,
            label=T('Events')),
        Field('Orders', 'boolean',
            default=True,
            label=T('Orders')),
        Field('Invoices', 'boolean',
            default=True,
            label=T('Invoices')),
        Field('Mail', 'boolean',
            default=True,
            label=T('Mailing lists')),
        Field('Privacy', 'boolean',
            default=True,
            label=T('Privacy'),
            comment=T('Page where users can download all data linked to their account')),
    )


def define_customers_profile_announcements():
    """
        Define table to hold announcements shown on customer profiles
    """
    db.define_table('customers_profile_announcements',
        Field('PublicAnnouncement', 'boolean', required=True,
            default=True,
            label=T("Published")),
        Field('Sticky', 'boolean', required=True,
            default=False,
            label=T("Sticky")),
        Field('Title', required=True,
            requires=IS_NOT_EMPTY(),
            label=T("Title")),
        Field('Announcement', 'text', required=True,
            requires=IS_NOT_EMPTY(),
            represent=lambda value, row: XML(value),
            label=T("Message")),
        Field('Startdate', 'date', required=True,
            requires=IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                      minimum=datetime.date(1900,1,1),
                                      maximum=datetime.date(2999,1,1)),
            default=TODAY_LOCAL,
            label=T("Show from"),
            widget=os_datepicker_widget),
        Field('Enddate', 'date', required=False,
            requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                      minimum=datetime.date(1900,1,1),
                                      maximum=datetime.date(2999,1,1))),
            represent=represent_date,
            label=T("Show until until"),
            widget = os_datepicker_widget),
        )


def define_customers_shop_features():
    """
        Define table to hold which features are enabled in the shop
    """
    db.define_table('customers_shop_features',
        Field('Memberships', 'boolean',
              default=True,
              label=T('Memberships')),
        Field('Subscriptions', 'boolean',
              default=True,
              label=T('Subscriptions')),
        Field('Classes', 'boolean',
              default=True,
              label=T('Classes')),
        Field('Classcards', 'boolean',
              default=True,
              label=T('Class cards')),
        Field('Workshops', 'boolean',
              default=True,
              label=T('Events')),
        Field('Donations', 'boolean',
              default=True,
              label=T('Donations'))
    )


def define_sys_files():
    """
        System file uploads
    """
    db.define_table('sys_files',
        Field('Name',
            readable=False,
            writable=False),
        Field('SysFile', 'upload', autodelete=True,
            label=T("File")),
        format='%(Name)s'
    )


def define_mailing_lists():
    """
        Define mailing lists table
    """
    db.define_table('mailing_lists',
        Field('Name',
              requires=IS_NOT_EMPTY(),
              label=T('Name')),
        Field('Description', 'text',
              requires=IS_NOT_EMPTY(),
              label=T('Description')),
        Field('Frequency',
              label=T('Frequency'),
              comment=T('eg. Once a month, twice a year, etc.')),
        Field('MailChimpListID',
              label=T('MailChimp List ID'),
              comment=T('Please refer to the MailChimp knowledge base on how to find the list ID for a list.'))
    )


# def define_integration_exact_online_storage():
#     """
#     Settings for exact online
#     """
#     db.define_table('integration_exact_online_storage',
#         Field('ConfigSection'),
#         Field('ConfigOption'),
#         Field('ConfigValue'),
#     )
#

def set_static_payment_methods():
    """
        This function adds the following to the paymentmethods table
        1. Cash
        2. Wire transfer
        3. Direct debit
    """
    methods = [T('Cash'), T('Wire transfer'), T('Direct debit')]
    i = 1
    for method in methods:
        row = db.payment_methods(1)
        if not row is None:
            query = (db.payment_methods.id == i)
            db(query).delete()
        db.payment_methods.insert(id=i,
                                  Name=method,
                                  Archived=False,
                                  SystemMethod=True)
        i += 1

    db.payment_methods.insert(id=100,
                              Name=T('Mollie'),
                              Archived=False,
                              SystemMethod=True)


def set_default_storage_space():
    """
        Sets 5GB (5000MB) as default storage space
    """
    allowed_space = '5000' # In MB
    db.sys_properties.insert(Property='storage_allowed_space',
                             PropertyValue=allowed_space)

    cache_clear_sys_properties()


def set_preferences_permissions():
    """
        Set the additional required permissions for the groups with the read
        permission for preferences.
        Currently create, read, update, delete and select will be set for
        payment_methods and payment_categories.
    """
    if not auth.user is None:
        user_id = auth.user.id
        check = auth.has_permission('read', 'preferences', 0, user_id)
        if check:
            tables = ['payment_categories', 'payment_methods']
            group_id = get_group_id()
            for table in tables:
                for permission in permissions:
                    auth.add_permission(group_id, permission, table, 0)


def create_admin_user_and_group():
    row = db.auth_user(1)
    if row is None:
        password = db.auth_user.password.validate('OSAdmin1#')[0]
        db.auth_user.insert(id=1,
                            enabled=True,
                            first_name='admin',
                            last_name='admin',
                            email='admin@openstudioproject.com',
                            password=password,
                            login_start='backend')
    row = db.auth_group(1)
    if row is None:
        db.auth_group.insert(id=1,
                             role='Admins',
                             description='This group has full access')
        auth.add_membership(1, 1) # add the admin user to the admins group
        set_permissions_for_admin_group()


def set_permissions_for_admin_group():
    for table in db.tables:
        for permission in permissions:
            auth.add_permission(1, permission, table, 0)


def setup_create_invoice_group():
    """
        Create default invoice group
    """
    terms = None
    footer = None
    if web2pytest.is_running_under_test(request, request.application):
        terms = 'Terms go there'
        footer = 'Footer goes here'


    db.invoices_groups.insert(
        id=100,
        Archived=False,
        Name='Default',
        NextID=1,
        DueDays=30,
        InvoicePrefix='INV',
        PrefixYear=True,
        Terms=terms,
        Footer=footer
    )


def setup_create_invoice_group_defaults():
    """
        Set default invoice group as default for products
    """
    product_types = get_invoices_groups_product_types()

    for product, name in product_types:
        db.invoices_groups_product_types.insert(
            ProductType = product,
            invoices_groups_id = 100
        )


def setup_set_customers_profile_features():
    """
        Enable all profile features for customers by default
    """
    db.customers_profile_features.insert(
        id=1,
        Classes=True,
        Classcards=True,
        Subscriptions=True,
        Workshops=True,
        Orders=True,
        Invoices=True
    )


def setup_set_customers_shop_features():
    """
        Enable all profile features for customers by default
    """
    db.customers_shop_features.insert(
        id=1,
        Classcards=True,
        Subscriptions=True,
        Workshops=True
    )


def setup_set_email_templates():
    """
        Insert default email templates
    """
    templates = [
        [
            'sys_email_footer',
            'Email Footer',
             """ """
        ],
        [
            'sys_reset_password',
            'Reset Password',
            """<h3>Reset password</h3>
            <p>Please click on the <a href="%(link)s">link</a> to reset your password</p>"""
        ],
        [
            'sys_verify_email',
            'Verify Email',
            """<h3>Verify email</h3>
            <p>Welcome %(first_name)s!</p>
            <p>Please click on the <a href="%(link)s">link</a> to verify your email</p>"""
        ],
        [
            'order_received',
            'Order received',
            """<h3>We have received your order with number #{order_id} on {order_date}</h3>
            <p>&nbsp;</p>
            <p>{order_items}</p>
            <p>&nbsp;</p>
            <p>To view your orders, please click <a href="{link_profile_orders}">here</a>.</p>"""
        ],
        [
            'order_delivered',
            'Order delivered',
            """<h3>Your order&nbsp;with number #{order_id} has been delivered</h3>
            <p>All items listed below have been added to your account</p>
            <p>&nbsp;</p>
            <p>{order_items}</p>
            <p>&nbsp;</p>
            <p>To view your orders, please click <a href="{link_profile_orders}">here</a>.</p>
            <p>To view your invoices, please click <a href="{link_profile_invoices}">here</a>.</p>"""
        ],
        [
            'payment_recurring_failed',
            'Recurring payment failed',
            """<h3>Recurring payment failed</h3>
            <p>&nbsp;</p>
            <p>One or more recurring payments failed, please log in to your account and pay any open invoices before the due date.</p>
            <p>&nbsp;</p>
            <p>To view your invoices, please click <a href="{link_profile_invoices}">here</a>.</p>"""
        ],
    ]
    for name, title, template_content in templates:
        db.sys_email_templates.insert(
            Name = name,
            Title = title,
            TemplateContent = template_content
        )


def setup():
    """
        This function runs when running OpenStudio for the first time.
        To check whether setup has run, use the Property "setup_complete" in
        the sys_properties table. If the value is "T", it has run.
    """
    setup_complete = 'F'
    row = db.sys_properties(Property="setup_complete")
    if not row is None:
        setup_complete = row.PropertyValue

    if setup_complete != 'T':
        from os_upgrade import set_version
        set_version()

        from openstudio.os_scheduler import OsScheduler
        oss = OsScheduler()
        oss.set_tasks()

        set_static_payment_methods()
        set_default_storage_space()
        setup_create_invoice_group()
        setup_set_email_templates()
        create_admin_user_and_group()
        setup_create_invoice_group_defaults()
        setup_set_customers_profile_features()
        setup_set_customers_shop_features()
        set_permissions_for_admin_group()

        from openstudio.os_setup import OsSetup
        os_setup = OsSetup()
        os_setup.setup()

        db.sys_properties.insert(Property="setup_complete",
                                 PropertyValue="T")

        cache_clear_sys_properties()
        # go to upgrade to set version & release in DB
        #redirect(URL('upgrade', 'index'))



## call the define table functions
# define system table
define_sys_properties()

#  set date and time formats
def set_dateformats():
    return [('%Y-%m-%d','yyyy-mm-dd'),
            ('%m-%d-%Y','mm-dd-yyyy'),
            ('%d-%m-%Y','dd-mm-yyyy')]


def set_dateformat():
    sprop_dateformat = get_sys_property('DateFormat')
    if sprop_dateformat:
        date_format = sprop_dateformat
    else:
        date_format = None
    if date_format is None:
        date_format = '%Y-%m-%d'

    return date_format


def set_datemask(date_format):
    """
        :return: datemask for inputs based on date format
    """
    if date_format == '%d-%m-%Y':
        mask = 'dd-mm-yyyy'
    elif date_format == '%m-%d-%Y':
        mask = 'mm-dd-yyyy'
    else:
        mask = 'yyyy-mm-dd'

    return mask


def set_timeformat():
    return '%H:%M'


def set_datetimeformat():
    return DATE_FORMAT + ' ' + TIME_FORMAT


DATE_FORMATS = set_dateformats()
DATE_FORMAT = set_dateformat()
DATE_FORMAT_ISO8601 = '%Y-%m-%d'
DATE_MASK = set_datemask(DATE_FORMAT)
TIME_FORMAT = set_timeformat()
DATETIME_FORMAT = set_datetimeformat()

# set timezone
TIMEZONE = get_sys_property('TimeZone') or 'Europe/Amsterdam'

NOW_UTC = pytz.utc.localize(datetime.datetime.now())
TODAY_UTC = datetime.date.today()

NOW_LOCAL = NOW_UTC.astimezone(pytz.timezone(TIMEZONE))
TODAY_LOCAL = datetime.date(NOW_LOCAL.year, NOW_LOCAL.month, NOW_LOCAL.day)


current.DATE_FORMATS = DATE_FORMATS
current.DATE_FORMAT = DATE_FORMAT
current.DATE_FORMAT_ISO8601 = DATE_FORMAT_ISO8601
current.TIME_FORMAT = TIME_FORMAT
current.DATETIME_FORMAT = DATETIME_FORMAT
current.TIMEZONE = TIMEZONE
current.NOW_LOCAL = NOW_LOCAL
current.TODAY_LOCAL = TODAY_LOCAL


def represent_date(date, row=None):
    if date is None:
        return ""
    else:
        return date.strftime(DATE_FORMAT)


def represent_datetime(datetime, row=None):
    if datetime is None:
        return ""
    else:
        dt = pytz.utc.localize(datetime)
        tz = pytz.timezone(TIMEZONE)
        local_dt = dt.astimezone(tz)
        return local_dt.strftime(DATETIME_FORMAT)


## Set datetime format for scheduler tables
db.scheduler_task.start_time.requires=IS_DATETIME(format=DATETIME_FORMAT)
db.scheduler_task.stop_time.requires=IS_DATETIME(format=DATETIME_FORMAT)
db.scheduler_task.next_run_time.requires=IS_DATETIME(format=DATETIME_FORMAT)
db.scheduler_task.last_run_time.requires=IS_DATETIME(format=DATETIME_FORMAT)


## create all tables needed by auth if not custom tables
define_school_languages()
languages_dict = create_languages_dict()
define_school_classtypes()
classtypes_dict = create_classtypes_dict()
define_school_discovery()
discovery_dict = create_discovery_dict()
define_school_locations()
locations_dict = create_locations_dict()
define_school_levels()
levels_dict = create_school_levels_dict()

dis_query = (db.school_discovery.Archived == False)
lev_query = (db.school_levels.Archived    == False)
loc_query = (db.school_locations.Archived == False)
lan_query = (db.school_languages.Archived == False)

auth.settings.extra_fields['auth_user'] = [
    Field('archived', 'boolean', # This field can be removed in > 2018.2
          readable=False,
          writable=False,
          default=False,
          label=T("Archived")),
    Field('trashed', 'boolean',
        readable=False,
        writable=False,
        default=False,
        label=T('Deleted')),
    Field('enabled', 'boolean',
        readable=False,
        writable=False,
        default=True,
        label=T("Allow login")),
    Field('customer', 'boolean',
        readable=False,
        writable=False,
        default=True,
        label=T('Customer')),
    Field('teacher', 'boolean',
        readable=False,
        writable=False,
        default=False,
        label=T('Teacher')),
    Field('teaches_classes', 'boolean',
        readable=False,
        writable=False,
        default=False,
        label=T('Teaches classes')),
    Field('teaches_workshops', 'boolean',
        readable=False,
        writable=False,
        default=False,
        label=T('Teaches events')),
    Field('employee', 'boolean',
        readable=False,
        writable=False,
        default=False,
        label=T('Employee')),
    Field('business', 'boolean',
        readable=False,
        writable=False,
        default=False,
        label=T('Business'),
        comment = os_gui.get_info_icon(
            title=T("Show company name instead of first & last name in lists."),
            btn_icon='info')),
    Field('login_start',
        readable=False,
        writable=False,
        requires=IS_IN_SET([ ['backend', T('Backend')],
                             ['selfcheckin', T("Self Check-in")],
                             ['ep', T("Employee portal")],
                             ['profile', T('Customer profile')]
                           ]),
        default='profile',
        label=T("After login go to")),
    Field('last_login', 'datetime',
        readable=False,
        writable=False),
    Field('barcode_id', 'integer',
        represent=lambda value, row: value or "",
        label=T("Barcode")),
    Field('barcode', 'upload', autodelete=True,
          readable=False,
          writable=False,
          represent=lambda value, row: A(T("Download"),
                                         _href=URL('default', 'download', args=value)),
          label=T("Barcode")),
    Field('gender',
        requires=IS_EMPTY_OR(IS_IN_SET(GENDERS)),
        represent=represent_gender,
        label=T("Gender")),
    Field('date_of_birth', 'date', required=False,
        requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format=DATE_FORMAT,
                             minimum=datetime.date(1900,1,1),
                             maximum=datetime.date(2999,12,31))),
        represent=represent_date, label=T("Date of birth"),
        widget=os_date_widget),
    Field('birthday', 'date',
        readable=False,
        writable=False,
        compute=compute_birthday,
        requires=IS_EMPTY_OR(IS_DATE(format=DATE_FORMAT))),
        #represent=lambda value, row: value.strftime("%B %d") if value else ''),
    Field('address',
        required=False,
        label=T("Address")),
    Field('postcode',
        required=False,
        label=T("Postcode")),
    Field('postcode_asint', 'integer',
        required=False,
        readable=False,
        writable=False,
        compute=lambda row: string_to_int(row.postcode)),
    Field('city',
        required=False,
        represent=lambda value, row:  value or "",
        label=T("City")),
    Field('country',
        required=False,
        requires=IS_EMPTY_OR(IS_IN_SET(country_codes)),
        represent=lambda value, row:  value or "",
        label=T("Country")),
    Field('phone',
        required=False,
        represent=lambda value, row:  value or "",
        label=T("Telephone")),
    Field('mobile',
        required=False,
        represent=lambda value, row:  value or "",
        label=T("Mobile")),
    Field('emergency',
        required=False,
        represent=lambda value, row:  value or "",
        label=T("Emergency contact")),
    Field('keynr', required=False,
        represent=lambda value, row: value or "",
        label=T("Key Number")),
    Field('newsletter', 'boolean',
        default=False,
        label=T("Newsletter")),
    Field('company',
        label=T("Company")),
    Field('company_registration',
        label=T("Registration")),
    Field('company_tax_registration',
        label=T("Tax Registration")),
    Field('school_discovery_id', db.school_discovery,
        requires=IS_EMPTY_OR(IS_IN_DB(db(dis_query),
                                      'school_discovery.id',
                                      '%(Name)s')),
        represent=lambda value, row: discovery_dict.get(value, None),
        label=T("Discovery")),
    Field('school_levels_id', db.school_levels,
        requires=IS_EMPTY_OR(IS_IN_DB(db(lev_query),'school_levels.id','%(Name)s')),
        represent=lambda value, row: levels_dict.get(value, None),
        label=T("Level")),
    Field('school_locations_id', db.school_locations,
        requires=IS_EMPTY_OR(IS_IN_DB(db(loc_query),
                                      'school_locations.id',
                                      '%(Name)s')),
        represent=lambda value, row: locations_dict.get(value, None),
        label=T("Primary location")),
    Field('school_languages_id', db.school_languages,
        requires=IS_EMPTY_OR(IS_IN_DB(db(lan_query),
                                      'school_languages.id',
                                      '%(Name)s')),
        represent=lambda value, row: languages_dict.get(value, None),
        label=T("Language")),
    Field('picture', 'upload', autodelete=True,
        requires=IS_EMPTY_OR([IS_IMAGE(extensions=('jpeg', 'jpg', 'png')),
                                       IS_LENGTH(maxsize=4194304)]),
        label=T("Customer")),
    Field('thumbsmall', 'upload', # generate 50*50 for list view
        autodelete=True, writable=False,
        compute = lambda row: SMARTHUMB(row.picture,
                                        (50, 50),
                                         name="Small"),
        represent = represent_user_thumbsmall,
        label=T("Customer")),
    Field('thumblarge', 'upload', # generate 400*400 for edit view
        autodelete=True, writable=False,
        compute = lambda row: SMARTHUMB(row.picture,
                                         (400, 400),
                                         name="Large")),
    Field('teacher_role',
          readable=False,
          writable=False,
          label=T('Teacher role')),
    Field('teacher_bio', 'text',
        label=T("Biography")),
    Field('education', 'text',
        required=False,
        label=T("Education")),
    Field('teacher_bio_link',
        label=T("Link to bio")),
    Field('teacher_website',
        label=T("Website")),
    Field('full_name',
        readable=False,
        writable=False,
        compute=lambda row:row.first_name.strip() + ' ' + \
                           row.last_name.strip()),
    Field('display_name',
        writable=False,
        compute=lambda row: row.company if (row.business and row.company) else row.full_name,
        label=T("Customer")),
    Field('mollie_customer_id',
        readable=False,
        writable=False,
        label=T("Mollie customer id")),
    Field('exact_online_relation_id',
        readable=False,
        writable=False,
        label=T("Exact online customer ID")),
    Field('merged', 'boolean',
        readable=False,
        writable=False,
        default=False),
    Field('merged_into', 'integer',
        readable=False,
        writable=False),
    Field('merged_on', 'datetime',
        readable=False,
        writable=False,
        represent=represent_datetime),
    Field('teacher_notes_count', 'integer', # empty field that can be used to map values into from raw queries
        readable=False,
        writable=False),
    Field('teacher_notes_count_injuries', 'integer', # empty field that can be used to map values into from raw queries
        readable=False,
        writable=False),
    Field('created_on', 'datetime',
          readable=False,
          writable=False,
          default=datetime.datetime.now(),
          represent=represent_datetime)
    ]


auth.define_tables(username=False, signature=False)

# Set format for auth_user.id
db.auth_user._format = '%(display_name)s'

# set up email
MAIL = mail

# setup currency symbol
CURRSYM = get_sys_property('CurrencySymbol')
if not CURRSYM:
    CURRSYM = u'€'
# setup currency
CURRENCY = get_sys_property('Currency')
if not CURRENCY:
    CURRENCY = 'EUR'


### Sys properties and auth tables end

# Now continue with the rest of the DAL

define_sys_organizations()
define_sys_api_users()
define_sys_files()
define_sys_accounting()
define_sys_email_templates()
define_sys_notifications()
define_sys_notifications_email()
set_show_location()
set_dateformat()
set_class_status()
SHIFT_STATUSES = set_shift_status()
ORGANIZATIONS = get_organizations()
define_payment_methods()
payment_methods_dict = create_payment_methods_dict()

define_mailing_lists()
define_integration_exact_online_log()
define_postcode_groups()
define_tax_rates()
define_accounting_costcenters()
define_accounting_glaccounts()
define_accounting_expenses()
define_accounting_cashbooks_cash_count()

define_school_memberships()
define_school_subscriptions()
#mstypes_dict = create_mstypes_dict()
define_school_subscriptions_price()
define_school_subscriptions_groups()
define_school_subscriptions_groups_subscriptions()
define_school_classcards()
define_school_classcards_groups()
define_school_classcards_groups_classcards()
define_payment_categories()
paycat_dict = create_payment_categories_dict()
define_teachers_holidays()
teachers_dict = create_teachers_dict()
employees_dict = create_employees_dict()

define_messages()

define_workshops()
#workshops_dict = create_workshops_dict()
define_workshops_activities()
#workshops_activities_dict = create_workshops_activities_dict()
define_workshops_products()
define_workshops_products_activities()
define_workshops_mail()

#customers_dict = create_customers_dict()
define_customers_documents()
define_customers_notes()
define_customers_payment_info()
define_customers_payment_info_mandates()
define_customers_messages()
define_customers_memberships()
define_customers_subscriptions()
define_customers_subscriptions_paused()
define_customers_subscriptions_alt_prices()
define_customers_profile_features()
define_customers_profile_announcements()
define_customers_shop_features()

define_alternativepayments()

define_workshops_products_customers()
define_workshops_activities_customers()
define_classes()

define_customers_shoppingcart()
#classes_dict = create_classes_dict()
define_classes_otc()
define_classes_otc_sub_avail()
define_classes_price()
define_classes_teachers()
define_classes_open()
define_classes_cancelled()
define_customers_classcards()
define_classes_reservation()
define_classes_reservation_cancelled()
define_classes_waitinglist()
define_classes_attendance()
define_classes_attendance_override()
define_teachers_classtypes()
define_classes_subteachers()
define_classes_notes()
define_classes_schedule_counts()
define_classes_school_subscriptions_groups()
define_classes_school_classcards_groups()
define_tasks()
define_announcements()
define_school_holidays()
define_school_holidays_locations()
define_schedule_classes_status()

# teacher payment definitions (depend on classes and auth_user)
define_teachers_payment_fixed_rate_default()
define_teachers_payment_fixed_rate_class()
define_teachers_payment_travel()
define_teachers_payment_attendance_lists()
define_teachers_payment_attendance_lists_rates()
define_teachers_payment_attendance_lists_school_classtypes()
define_teachers_payment_classes()

define_customers_subscriptions_credits()
define_log_customers_accepted_documents()

# order definitions
define_customers_orders()
define_customers_orders_items()
define_customers_orders_amounts()
define_customers_orders_mollie_payment_ids()

# shop tables
define_shop_links()
define_shop_brands()
define_shop_suppliers()
define_shop_products_sets()
define_shop_products_sets_options()
define_shop_products_sets_options_values()
define_shop_products()
define_shop_products_variants()
define_shop_categories()
define_shop_categories_products()
define_customers_orders_items_shop_products_variants()

# employee claims definitions
define_employee_claims()

# shop sales
define_shop_sales()
define_shop_sales_products_variants()

# invoice definitions
define_invoices_groups()
define_invoices_groups_product_types()
define_invoices()
define_invoices_amounts()
define_invoices_items()
define_invoices_items_customers_classcards()
define_invoices_items_employee_claims()
define_invoices_items_customers_memberships()
define_invoices_items_customers_subscriptions()
define_invoices_items_teachers_payment_classes()
define_invoices_items_workshops_products_customers()
define_invoices_payments()
define_invoices_classes_attendance()
define_invoices_customers()
define_invoices_customers_orders()
define_invoices_mollie_payment_ids()
# define_invoices_customers_memberships()
# define_invoices_customers_subscriptions()
# define_invoices_workshops_products_customers()
# define_invoices_customers_classcards()
# define_invoices_employee_claims()
# define_invoices_teachers_payment_classes()


# receipts definitions
define_receipts()
define_receipts_items()
define_receipts_items_shop_sales()
define_receipts_amounts()

# payment batches definitions
define_payment_batches()
define_payment_batches_items()
define_payment_batches_exports()

# shifts definitions
define_school_shifts()
define_shifts()
define_shifts_staff()
define_shifts_otc()
define_schedule_staff_status()

# mollie tables
define_mollie_log_webhook()

set_preferences_permissions()

# some system maintendance
create_admin_user_and_group()
setup()
