# -*- coding: utf-8 -*-

from general_helpers import max_string_length
from general_helpers import datestr_to_python

from openstudio import AttendanceHelper, ClassSchedule, Customer, Class

import pytz

@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'selfcheckin'))
def index():
    '''
        Lists announcements
    '''
    response.title = T("Where are you now?")
    response.logout = get_logout()

    locations = index_get_locations()

    content = DIV(
        locations,
        _class='col-xs-12'
    )

    return dict(content=content)


def index_get_locations(var=None):
    '''
        Returns a list of all locations that aren't archived
    '''
    query = (db.school_locations.Archived == False)

    rows = db(query).select(db.school_locations.ALL,
                            orderby=db.school_locations.Name)

    locations = UL(_id='locations')
    for row in rows:
        location = LI(A(SPAN(_class='glyphicon glyphicon-home'), ' ',
                        row.Name,
                        _href=URL('classes', vars={'locID':row.id}),
                        _class='btn btn-default btn-lg full-width'))
        locations.append(location)

    return locations


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'classes'))
def classes():
    '''
        Function returns a list of classes today
    '''
    locID = request.vars['locID']

    # Set today while looking at configured timezone
    now = pytz.utc.localize(datetime.datetime.now())
    tz = pytz.timezone(TIMEZONE)
    local_dt = now.astimezone(tz)
    today = datetime.date(local_dt.year, local_dt.month, local_dt.day)

    date_formatted = today.strftime(DATE_FORMAT)
    date = datestr_to_python(DATE_FORMAT, date_formatted)
    pretty_date = date.strftime('%B %d, %Y')

    location = db.school_locations(locID)
    # go_back
    response.back = A(SPAN(_class='glyphicon glyphicon-chevron-left'),
                     _href=URL('index'),
                     _class='pull-right')
    response.title = location.Name
    response.subtitle = SPAN(T('Classes'), ' ',
                             ' ',
                             pretty_date)
    response.view = 'selfcheckin/default.html'
    response.logout = get_logout()

    cs = ClassSchedule(
        date,
        filter_id_school_location = locID
    )

    rows = cs.get_day_rows()

    header = THEAD(TR(TH(T('Time')),
                      TH(T('Class type')),
                      TH(),
                      ))
    table = TABLE(header, _class='table table-striped table-hover')

    for i, row in enumerate(rows):
        repr_row = list(rows[i:i+1].render())[0]

        time = repr_row.classes.Starttime + ' - ' + repr_row.classes.Endtime
        link = os_gui.get_button('noicon',
            URL('checkin', vars={'clsID':row.classes.id,
                                 'date' :date_formatted}),
            title=T("Go to check-in"),
            _class='pull-right'
            )

        tr = TR(TD(time),
                TD(repr_row.classes.school_classtypes_id),
                TD(link))


        table.append(tr)

    return dict(content=table, logout=get_logout())


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('update', 'classes_attendance'))
def checkin():
    '''
        Checkin page for self checkin
    '''
    clsID          = request.vars['clsID']
    date_formatted = request.vars['date']
    date = datestr_to_python(DATE_FORMAT, date_formatted)

    session.customers_load_list_search_name = None
    session.classes_attendance_signin_back  = 'self_checkin'

    cls = Class(clsID, date)
    starttime = cls.cls.Starttime.strftime(TIME_FORMAT)
    pretty_date = date.strftime('%B %d, %Y')
    classtype = db.school_classtypes(cls.cls.school_classtypes_id)
    location = db.school_locations(cls.cls.school_locations_id)

    response.title = T(classtype.Name)
    response.subtitle = SPAN(starttime, ' ', pretty_date)
    response.logout = A(SPAN(_class='glyphicon glyphicon-chevron-left'),
                     _href=URL('classes',
                               vars={'locID':cls.cls.school_locations_id}))

    #response.view = 'templates/selfcheckin/checkin.html'

    # Check if the class is full
    full = cls.get_full()

    message = ''
    if full:
        message = DIV(BR(), os_gui.get_alert('info',
            SPAN(B(T('Notice')), BR(),
            T("This class is full, it's no longer possible to check in")),
            dismissable=False))

    search_results = DIV(LOAD('customers', 'load_list.load',
                              target='attendance_list_customers_list',
                              content=os_gui.get_ajax_loader(message=T("Searching...")),
                              vars={'list_type':'selfcheckin_checkin',
                                    'items_per_page':10,
                                    'clsID':clsID,
                                    'date':date_formatted,
                                    'pictures':False},
                              ajax=True),
                         _id="attendance_list_customers_list",
                         _class="load_list_customers clear")

    name = ''


    show_subscriptions_prop = 'selfcheckin_show_subscriptions'
    show_subscriptions = get_sys_property(show_subscriptions_prop)
    if show_subscriptions:
        show_subscriptions = True
    else:
        show_subscriptions = False

    ah = AttendanceHelper()
    customers = ah.get_checkin_list_customers_booked(clsID,
                                                     date,
                                                     pictures=False,
                                                     invoices=False,
                                                     show_notes=False,
                                                     reservations=False,
                                                     manage_checkin=False,
                                                     show_booking_time=False,
                                                     show_subscriptions=show_subscriptions,
                                                     class_full=full)
    form = checkin_get_search_form(clsID, date, name, request.function)

    content = DIV(
        SPAN(location.Name, _class='grey'),
        message,
        customers,
    )

    if not full:
        content.append(DIV(H2(T("I'm not yet on the list...")),
                           form,
                            search_results))

    return dict(content = content)

@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('update', 'classes_attendance'))
def checkin_booking_options():
    '''
        List booking options for a customer
    '''
    cuID = request.vars['cuID']
    clsID = request.vars['clsID']
    date_formatted = request.vars['date']
    date = datestr_to_python(DATE_FORMAT, date_formatted)

    customer = Customer(cuID)
    cls = Class(clsID, date)
    starttime = cls.cls.Starttime.strftime(TIME_FORMAT)
    pretty_date = date.strftime('%B %d, %Y')
    classtype = db.school_classtypes(cls.cls.school_classtypes_id)
    location = db.school_locations(cls.cls.school_locations_id)

    response.title = T(classtype.Name)
    response.subtitle = SPAN(starttime, ' ', pretty_date)
    response.view = 'selfcheckin/checkin.html'


    return_url = URL('selfcheckin', 'checkin', vars={'clsID':clsID,
                                                     'date':date_formatted})

    cls = Class(clsID, date)

    ah = AttendanceHelper()
    options = ah.get_customer_class_booking_options(clsID,
                                                    date,
                                                    customer,
                                                    trial=True,
                                                    list_type='attendance',
                                                    controller='classes')
    cancel = os_gui.get_button('noicon',
                               return_url,
                               title=T('Cancel'),
                               btn_size='')

    content = DIV(
        H3(T('Booking options for'), ' ', customer.row.display_name, _class='center'), BR(),
        options,
        DIV(BR(), cancel, _class="col-md-12 center"),
        _class="row"
    )

    back = os_gui.get_button('back', return_url)

    return dict(content=content,
                back=back)



def checkin_get_search_form(clsID, date, name, function):
    '''
        Form to search for customers
    '''
    date_formatted = date.strftime(DATE_FORMAT)
    form = SQLFORM.factory(
        Field('name', default=name, label=T("")),
        submit_button='Search',
        )
    form.element('input[name=name]')['_placeholder'] = \
        'Please enter your first name or your last name...'
    form.element('input[name=name]')['_autocomplete'] = 'off'

    form = DIV(form.custom.begin,
               DIV(form.custom.widget.name,
                   SPAN(form.custom.submit, _class="input-group-btn"),
                   _class="input-group"),
               form.custom.end,
               BR())

    return form


@auth.requires_login()
def get_logout(var=None):
    '''
        Returns logout button
    '''
    logout = A(SPAN(_class='glyphicon glyphicon-off'), ' ',
                   T('Log Out'),
                   _href=URL('default', 'user', args=['logout']))

    return logout


def get_logo(var=None):
    '''
        Returns logo for self check-in
    '''
    branding_logo = os.path.join(request.folder,
                                 'static',
                                 'plugin_os-branding',
                                 'logos',
                                 'branding_logo_selfcheckin.png')
    if os.path.isfile(branding_logo):
        logo_img = IMG(_src=URL('static',
                       'plugin_os-branding/logos/branding_logo_selfcheckin.png'))
    else:
        logo_img = ''

    return logo_img
