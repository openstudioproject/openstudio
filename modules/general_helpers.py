# -*- coding: utf-8 -*-
import datetime
import calendar
import string

from gluon import *

def classes_get_status(clsID, date):
    """
        Returns the status and status marker for a class, possible options:
        normal
        subteacher
        open
        cancelled
    """
    db = current.db

    status = 'normal'
    status_marker = DIV(_class='status_marker bg_green')
    cotc = db.classes_otc(classes_id=clsID, ClassDate=date)

    if cotc:
        if cotc.Status == 'cancelled':
            status = 'cancelled'
            status_marker = DIV(_class='status_marker bg_orange')
        elif cotc.Status == 'open':
            status = 'open'
            status_marker = DIV(_class='status_marker bg_red')
        elif cotc.teacher_role == 1 and cotc.auth_teacher_id:
            status = 'subteacher'
            status_marker = DIV(_class='status_marker bg_blue')

    return dict(status=status,
                status_marker=status_marker)


def class_get_teachers(clsID, class_date):
    """
        Returns the teachers for a class based on the classes_id and
        date of the class
    """
    os_gui = current.globalenv['os_gui']

    teachers_dict = current.globalenv['teachers_dict']
    teacher_id = None
    teacher_id2 = None
    teacher_role = ''
    teacher_role2 = ''
    status = 'normal'

    dba = current.db

    # check regular teachers
    query = (dba.classes_teachers.classes_id == clsID) & \
            (dba.classes_teachers.Startdate <= class_date) &\
            ((dba.classes_teachers.Enddate >= class_date) |
             (dba.classes_teachers.Enddate == None))
    row = dba(query).select(dba.classes_teachers.ALL,
                            orderby=dba.classes_teachers.Startdate).first()

    if row:
        try:
            teacher_id = int(row.auth_teacher_id)
            if row.teacher_role:
                teacher_role = row.teacher_role
        except:
            pass
        try:
            teacher_id2 = int(row.auth_teacher_id2)
            if row.teacher_role2:
                teacher_role2 = row.teacher_role2
        except:
            pass

    # check subteachers
    query = (dba.classes_subteachers.classes_id == clsID) & \
            (dba.classes_subteachers.ClassDate == class_date)
    row = dba(query).select(dba.classes_subteachers.ALL).first()
    if row:
        teacher_role = ''
        teacher_role2 = ''
        teacher_id = None
        teacher_id2 = None
        try:
            teacher_id = int(row.auth_teacher_id)
            if row.teacher_role:
                teacher_role = row.teacher_role
            status = 'subteacher'
        except:
            pass
        try:
            teacher_id2 = int(row.auth_teacher_id2)
            if row.teacher_role2:
                teacher_role2 = row.teacher_role2
            status = 'subteacher'
        except:
            pass

    teacher = max_string_length(teachers_dict.get(teacher_id, ''), 20)
    teacher2 = max_string_length(teachers_dict.get(teacher_id2, ''), 20)

    # set label for teacher role
    if teacher_role == 1: # sub
        teacher_role = SPAN(os_gui.get_os_label('blue', teacher),
                            _title=current.T('Sub teacher'))
    elif teacher_role == 2: # assist
        teacher_role = SPAN(os_gui.get_os_label('yellow', teacher),
                            _title=current.T("Assistant"))
    elif teacher_role == 3: # karma
        teacher_role = SPAN(os_gui.get_os_label('purple', teacher),
                            _title=current.T('Karma teacher'))
    else:
        teacher_role = teacher

    # set label for teacher role 2
    if teacher_role2 == 1: # sub
        teacher_role2 = SPAN(os_gui.get_os_label('blue', teacher2),
                             _title=current.T("Sub teacher"))
    elif teacher_role2 == 2: # assist
        teacher_role2 = SPAN(os_gui.get_os_label('yellow', teacher2),
                             _title=current.T("Assistant"))
    elif teacher_role2== 3: # karma
        teacher_role2 = SPAN(os_gui.get_os_label('purple', teacher2),
                             _title=current.T('Karma teacher'))
    else:
        teacher_role2 = teacher2

    return dict(teacher_id=teacher_id,
                teacher_id2=teacher_id2,
                teacher=teacher,
                teacher2=teacher2,
                teacher_role=teacher_role,
                teacher_role2=teacher_role2,
                status=status)



def get_months_list():
    """
        This function returns a list of tuples [0] is the number of the month and [1] is the name in English
    """
    return [(1,current.T("January")),
            (2,current.T("February")),
            (3,current.T("March")),
            (4,current.T("April")),
            (5,current.T("May")),
            (6,current.T("June")),
            (7,current.T("July")),
            (8,current.T("August")),
            (9,current.T("September")),
            (10,current.T("October")),
            (11,current.T("November")),
            (12,current.T("December"))]


def get_number_weekdays_in_month(year, month, iso_weekday):
    """
    :param year: year
    :param month: month
    :param iso_weekday: day in range 1 - 7 where Monday is 1 and Sunday is 7
    :return: count of days in month
    """
    day = datetime.date(year, month, 1)
    delta = datetime.timedelta(days=1)

    count = 0
    while day.month == month:
        if day.isoweekday() == iso_weekday:
            count += 1
        day += delta

    return count


def get_last_day_month(date):
    """
        This function returns the last day of the month as a datetime.date object
    """
    return datetime.date(date.year,
                         date.month,
                         calendar.monthrange(date.year,date.month)[1])


def get_first_day_next_month(date):
    """
    Returns the first day of the next month
    :param date: datetime.date
    :return: datetime.date
    """
    return get_last_day_month(date) + datetime.timedelta(days=1)


def get_last_day_next_month(date):
    """
    Returns the last day of the next month
    :param date: datetime.date
    :return: datetime.date
    """
    return get_last_day_month(get_first_day_next_month(date))


def get_lastweek_year(year):
    """
        The 28th of December is always in the last week...
        The 31st might be in week 1 according to the iso calendar
    """
    lastday = datetime.date(year,12,28)
    return lastday.isocalendar()[1]


def get_weekday(date):
    """
        Returns day of week for given datetime.date object
    """
    return date.isocalendar()[2]


def get_paused_subscriptions(date):
    """
        This helper function returns the paused subscriptions the month of date
    """
    lastdaythismonth = get_last_day_month(date)
    firstdaythismonth = datetime.date(date.year, date.month, 1)

    dba = current.db
    query = (dba.customers_subscriptions_paused.Startdate <=
             lastdaythismonth) & \
            ((dba.customers_subscriptions_paused.Enddate >=
              firstdaythismonth) |
            (dba.customers_subscriptions_paused.Enddate == None))
    rows = dba(query).select(dba.customers_subscriptions_paused.ALL)
    paused_subscriptions = dict()
    for row in rows:
        paused_subscriptions[row.customers_subscriptions_id] = True

    return paused_subscriptions


def get_classname(clsID):
    dba = current.db
    record = dba.classes[clsID]
    location = dba.school_locations[record.school_locations_id].Name
    classtype = dba.school_classtypes[record.school_classtypes_id].Name
    Weekday = NRtoDay(record.Week_day)
    return Weekday + " " + \
           location + " " + \
           record.Starttime.strftime('%H:%M') + " " + \
           classtype

def get_submenu(pages,
                page,
                horizontal=False,
                htype='', # tabs or pills
                _id='',
                _class=''):
    """
        This function returns a submenu based on the list pages which
        is in the following format:
        [ page, title, url ]
        when page matches pages[n][0] the menu whill receive an extra tag to
        indicate it's active
    """
    submenu_class = "os-submenu"
    if horizontal:
        submenu_class = "os-submenu-horizontal"
        if htype == 'tabs':
            menu = UL(_class='nav nav-tabs')
        else:
            menu = UL(_class='nav nav-pills')
        for p in pages:
            active = ''
            if p[0] == page:
                active = 'active'
            menu.append(LI(A(p[1], _href=p[2]), _class=active))
    else:
        menu = []
        for p in pages:
            active = False
            if p[0] == page:
                active = True
            menu.append([p[1], active, p[2]])

        menu = MENU(menu, li_first='', li_last='', _class=submenu_class, _id=_id)
    return menu

def get_group_id():
    """
        This function returns the group id of the currently logged in user
    """
    dba = current.db
    w2p_auth = current.auth
    row = dba(dba.auth_membership.user_id == w2p_auth.user.id).select(dba.auth_membership.group_id).first()
    return row.group_id


def get_badge(badge_type, value):
    """
        Returns a span with a badge class
    """
    _class = 'badge'
    if badge_type == 'default':
        pass
    elif badge_type == 'success':
        _class += ' badge-success'
    elif badge_type == 'warning':
        _class += ' badge-warning'
    elif badge_type == 'important':
        _class += ' badge-important'
    elif badge_type == 'info':
        _class += ' badge-info'
    elif badge_type == 'inverse':
        _class += ' badge-inverse'

    return SPAN(value, _class=_class)


def get_label(label_type, value):
    """
        Returns a span with a badge class
    """
    _class = 'label'
    if label_type == 'default':
        _class += ' label-default'
    elif label_type == 'primary':
        _class += ' label-primary'
    elif label_type == 'success':
        _class += ' label-success'
    elif label_type == 'warning':
        _class += ' label-warning'
    elif label_type == 'important':
        _class += ' label-important'
    elif label_type == 'info':
        _class += ' label-info'

    return SPAN(value, _class=_class)


def get_priorities():
    """
    This function returns the priorities list of tuples.
    """
    return [(1, current.T("High")),
            (2, current.T("Normal")),
            (3, current.T("Low"))]

def get_input_search(_class='', _id=''):
    """
        Returns an input with Search... as placeholder
    """
    return INPUT(_name='search',
                 _placeholder=current.T('Search...'),
                 _autocomplete='off',
                 _class='search form-control ' + _class,
                 _id=_id)


def workshops_get_full_workshop_product_id(wsID):
    """
        Return id of full workshop product
    """
    dba = current.db
    query = (dba.workshops_products.workshops_id == wsID) & \
            (dba.workshops_products.FullWorkshop == True)
    return dba(query).select().first().id


# date related functions

def datestr_to_python(date_format, datestr):
    """
    This function takes date string and converts it into a python datetime.date object
    first argument: date_format
    second argument: date string
    """
    if date_format == '%d-%m-%Y':
        day = int(datestr.split("-")[0])
        month = int(datestr.split("-")[1])
        year = int(datestr.split("-")[2])
    elif date_format == '%m-%d-%Y':
        month = int(datestr.split("-")[0])
        day = int(datestr.split("-")[1])
        year = int(datestr.split("-")[2])
    elif date_format == '%Y-%m-%d':
        year = int(datestr.split("-")[0])
        month = int(datestr.split("-")[1])
        day = int(datestr.split("-")[2])

    return datetime.date(year, month, day)


def next_weekday(date, isoweekday):
    """
         Return next weekday after given date
    """
    days_ahead = isoweekday - date.isoweekday()
    if days_ahead <= 1: # Target day already happened this week
        days_ahead += 7
    return date + datetime.timedelta(days_ahead)


def NRtoDay(value, row=None):
    """
    This function takes a value and row as arguments and converts the value (that's within 1 and 7) to a week day.
    The row value is ignored, but present so it can be used within web2py's database represent function for Field definitions.
    """
    value = int(value)
    if value == 1:
        day = "Monday"
    elif value == 2:
        day = "Tuesday"
    elif value == 3:
        day = "Wednesday"
    elif value == 4:
        day = "Thursday"
    elif value == 5:
        day = "Friday"
    elif value == 6:
        day = "Saturday"
    elif value == 7:
        day = "Sunday"
    return current.T(day)


def NRtoMonth(value, row=None):
    month = ''
    if not value is None:
        value = int(value)
        months = get_months_list()
        for m in months:
            if m[0] == value:
                month = m[1]

    return month


def iso_year_start(iso_year):
    "The gregorian calendar date of the first day of the given ISO year"
    fourth_jan = datetime.date(iso_year, 1, 4)
    delta = datetime.timedelta(fourth_jan.isoweekday()-1)
    return fourth_jan - delta


def iso_to_gregorian(iso_year, iso_week, iso_day):
    "Gregorian calendar date for the given ISO year, week and day"
    iso_year = int(iso_year)
    iso_week = int(iso_week)
    year_start = iso_year_start(iso_year)
    return year_start + datetime.timedelta(days=iso_day-1, weeks=iso_week-1)


# date functions end


def set_form_id_and_get_submit_button(form, form_id):
    """
    :param form: html form
    :param form_id: form id to be set
    :return: form with id and submit button
    """
    form_element = form.element('form')
    form['_id'] = form_id

    elements = form.elements('input, select, textarea')
    for element in elements:
        element['_form'] = form_id

    submit = form.element('input[type=submit]')

    return dict(form=form, submit=submit)


def NRtoPriority(value, row=None):
    value = int(value)
    priorities = get_priorities()
    for p in priorities:
        if p[0] == value:
            return p[1]


def create_teachers_dict():
    db = current.db
    query = db.auth_user.teacher == True
    rows = db(query).select(db.auth_user.id,
                       db.auth_user.full_name)
    d = dict()
    for row in rows:
        d[row.id] = row.full_name
    d[None] = ""

    return d


def create_employees_dict():
    db = current.db
    query = db.auth_user.employee == True
    rows = db(query).select(db.auth_user.id,
                            db.auth_user.full_name)
    d = dict()
    for row in rows:
        d[row.id] = row.full_name
    d[None] = ""

    return d


def create_locations_dict():
    dba = current.db
    rows = dba().select(dba.school_locations.id, dba.school_locations.Name)
    d = dict()
    for row in rows:
        d[row.id] = row.Name
    d[None] = ""
    return d


def create_classtypes_dict():
    dba = current.db
    rows = dba().select(dba.school_classtypes.id, dba.school_classtypes.Name)
    d = dict()
    for row in rows:
        d[row.id] = row.Name
    d[None] = ""
    return d

def highlight_submenu(menu_link_title):
    """
    This function is used to make menu items bold
    """
    return (SPAN(menu_link_title, _style="font-weight:900;"))

def get_ajax_loader(msg='', big=False):
    """
        This function returns a div with a message and a loading gif
    """
    if big:
        loader = IMG(_src=URL('static', 'plugin_os-layout/images/ajax-loader-big.gif'))
    else:
        loader = IMG(_src=URL('static', 'plugin_os-layout/images/ajax-loader.gif'))
    return DIV(msg, BR(), loader)

class User_helpers():
    def __init__(self):
        self.auth = current.auth
        self.dba = current.db
    # def on_user_create(self, form):
    #     """
    #         This function creates a new group for a user. We're using this function
    #         because we're manually adding users and the web2py auth functions
    #         aren't called at those times.
    #     """
    #     user_id = form.vars.id
    #     group_name = "user_{0}".format(user_id)
    #     group_id = self.auth.add_group(group_name, group_name)
    #     self.auth.add_membership(group_id, user_id)
    #
    #     row = self.dba.auth_user(user_id)
    #
    # def on_user_delete(self, table, record_id):
    #     """
    #         This function creates a removed the group created for user and
    #         removes the membership form the group.
    #     """
    #     user_id = record_id
    #     group_name = "user_{0}".format(user_id)
    #     group_id = self.auth.id_group(group_name)
    #     self.auth.del_membership(group_id, user_id)
    #     self.auth.del_group(group_id)

    def check_read_permission(self, item, user_id):
        """
            This function checks the permission for a menu link
        """
        if self.auth.has_permission('read', item, 0, user_id) or self.auth.has_membership(1, user_id):
            return True
        else:
            return False

# memo functions begin
class Memo_links():
    def memo_link_visible(self, row):
        visible = False
        try:
            visible = row.Visible
            row_id = row.id
        except:
            try:
                visible = row.memos.Visible
                row_id = row.memos.id
            except:
                pass

        if visible:
            icon = 'glyphicon glyphicon-ok'
        else:
            icon = 'glyphicon glyphicon-remove'

        vars = {'memoID':row_id}
        try:
            vars['wsID'] = row.workshops_id
        except:
            pass
        return A(SPAN(_class=icon),
                 current.T(""),
                 _class="btn btn-default btn-sm",
                _href=URL('memo_change_visibility',
                    vars=vars),
                _title=current.T("Show/Hide this memo"))

    def memo_link_announcement(self, row):
        announcement = False
        try:
            announcement = row.Announcement
            row_id = row.id
        except:
            try:
                announcement = row.memos.Announcement
                row_id = row.memos.id
            except:
                pass

        if announcement:
            icon = 'glyphicon glyphicon-ok'
        else:
            icon = 'glyphicon glyphicon-remove'

        vars = {'memoID':row_id}
        try:
            vars['wsID'] = row.workshops_id
        except:
            pass
        return A(SPAN(_class=icon),
                 current.T(""),
                 _class="btn btn-default btn-sm",
                _href=URL('memo_change_announcement',
                    vars=vars),
                _title=current.T("Show at top"))

    def memo_link_priority(self, row):
        priority = None
        try:
            priority = row.Priority
            row_id = row.id
        except:
            try:
                priority = row.memos.Priority
                row_id = row.memos.id
            except:
                pass

        vars = {'memoID':row_id}
        try:
            vars['wsID'] = row.workshops_id
        except:
            pass

        if priority:
            if priority == 1:
                title = current.T("High")
            elif priority == 2:
                title = current.T("Normal")
            else:
                title = current.T("Low")
            return A(title, _href=URL('memo_change_priority',
                vars=vars),
                _title=current.T("Change the priority of this memo"))
        else:
            return current.T("Error fetching priority")

# memo funcions end

def max_string_length(string, length):
    """
        Cuts string to desired length, if longer, cuts and replaces last 3
        characters with "..."
    """
    if string is None:
        return_value = ''
    elif len(string) > length:
        return_value = string[:length-3] + "..."
    else:
        return_value = string

    return return_value


def string_to_int(str_in):
    """
        Translates string to integer where A=10 & Z=35
    """
    if not (isinstance(str_in, str) or isinstance(str_in, str)) or len(str_in) == 0:
        return None
    # format the string
    str_in = str_in.upper()
    # remove punctuation
    for char in string.punctuation:
        str_in = str_in.replace(char, '')
    # remove whitespace
    for char in string.whitespace:
        str_in = str_in.replace(char, '')

    # create replace map
    replace_map = {}
    for i, letter in enumerate(list(string.ascii_uppercase)):
        replace_map[letter] = str(i + 10)

    for k, v in replace_map.items():
        str_in = str_in.replace(k, v)

    return int(str_in)


def get_payment_batches_statuses():
    """
        Returns statuses for use with payment batches
    """
    statuses = [ [ 'sent_to_bank', current.T('Sent to Bank') ],
                 [ 'approved', current.T('Approved') ],
                 [ 'awaiting_approval', current.T("Awaiting approval") ],
                 [ 'rejected', current.T('Rejected') ] ]

    return statuses


def represent_validity_units(value, row=None):
    """
        Function to represent validity units
    """
    VALIDITY_UNITS = current.globalenv['VALIDITY_UNITS']

    return_value = ''
    for unit in VALIDITY_UNITS:
        if value == unit[0]:
            return_value = unit[1]
            # if row.Validity == 1:
            #     # Cut the 's' at the end
            #     return_value = return_value[:-1]
            break

    return return_value


def represent_subscription_units(value, row):
    """
        Function to represent validity units
    """
    SUBSCRIPTION_UNITS = current.globalenv['SUBSCRIPTION_UNITS']

    return_value = ''
    for unit in SUBSCRIPTION_UNITS:
        if value == unit[0]:
            return_value = unit[1]
            # if row.Validity == 1:
            #     # Cut the 's' at the end
            #     return_value = return_value[:-1]
            break

    return return_value

def represent_subscription_cancellation_period_units(value, row):
    """
        Function to represent validity units
    """
    SUBSCRIPTION_CANCELLATION_PERIOD_UNITS = current.globalenv['SUBSCRIPTION_CANCELLATION_PERIOD_UNITS']

    return_value = ''
    for unit in SUBSCRIPTION_CANCELLATION_PERIOD_UNITS:
        if value == unit[0]:
            return_value = unit[1]
            # if row.Validity == 1:
            #     # Cut the 's' at the end
            #     return_value = return_value[:-1]
            break

    return return_value


def get_download_url(db_upload_field_value):
    """
        :param rel_url: db.workshops.thumblarge
        :return: formatted url
    """
    url = ''
    if db_upload_field_value:
        url = URL('default', 'download', args=db_upload_field_value,
                  scheme=True,
                  host=True,
                  extension='')
    return url
