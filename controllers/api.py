# -*- coding: utf-8 -*-

import datetime

from general_helpers import iso_to_gregorian
from general_helpers import NRtoDay

from openstudio.openstudio import ClassSchedule, WorkshopSchedule, Workshop

cache_15_min = 99


def do_auth(user, key):
    """
        Checks if a user exists and if so if the supplied key is correct
    """
    query = (db.sys_api_users.Username == user)
    row = db(query).select(db.sys_api_users.ALL).first()
    authenticated = False
    message = ''
    message_fail = "Authentication error: please check user and key."
    if row is None:
        # Non existing user specified
        message = message_fail
    else:
        if not row.ActiveUser or not row.APIKey == key:
            # Inactive user or wrong key
            message = message_fail
        else:
            authenticated = True

    return dict(authenticated=authenticated,
                message=message)


def call_check_extension(var=None):
    '''
        check extension
    '''
    error = False
    error_msg = ''
    msg_extension_fail = T("Extension error: please call with a .json or \
                            .xml extension. Example: /api/schedule_get.json")
    if request.extension == 'xml':
        view = 'generic.xml'
    elif request.extension == 'json':
        view = 'generic.json'
    else:
        error = True
        error_msg = msg_extension_fail
        view = ''

    return dict(view=view, error=error, error_msg=error_msg)


def _schedule_get(year, week, sorting, TeacherID, ClassTypeID, LocationID, LevelID):
    # classes
    data = dict()
    data['classes'] = dict()
    for day in range(1, 8):
        date = iso_to_gregorian(int(year), int(week), int(day))

        class_schedule = ClassSchedule(
            date,
            filter_id_school_classtype=ClassTypeID,
            filter_id_school_location=LocationID,
            filter_id_school_level=LevelID,
            filter_id_teacher=TeacherID,
            filter_public=True,
            sorting=sorting
        )

        key = unicode(NRtoDay(day))

        class_data = dict(classes=class_schedule.get_day_list(),
                          date=date)

        data['classes'][key] = class_data

    # Teachers and classtypes this week
    teacher_ids_this_week = []
    classtype_ids_this_week = []
    location_ids_this_week = []
    weekdays = [T('Monday'), T('Tuesday'), T('Wednesday'), T('Thursday'), T('Friday'), T('Saturday'), T('Sunday')]
    for weekday in weekdays:
        for cls in data['classes'][weekday]['classes']:
            # check teachers
            if 'TeacherID' in cls and cls['TeacherID'] not in teacher_ids_this_week:
                teacher_ids_this_week.append(cls['TeacherID'])
            if 'TeacherID2' in cls and cls['TeacherID2'] not in teacher_ids_this_week:
                teacher_ids_this_week.append(cls['TeacherID2'])
            # check classtypes
            if 'ClassTypeID' in cls and cls['ClassTypeID'] not in classtype_ids_this_week:
                classtype_ids_this_week.append(cls['ClassTypeID'])
            # check locations
            if 'LocationID' in cls and cls['LocationID'] not in location_ids_this_week:
                location_ids_this_week.append(cls['LocationID'])


    # Define caching
    caching = (cache.ram, 120)
    if web2pytest.is_running_under_test(request, request.application):
        caching = None

    # ClassTypes
    classtypes = []
    query = (db.school_classtypes.Archived == False) & \
            (db.school_classtypes.AllowAPI == True) & \
            (db.school_classtypes.id.belongs(classtype_ids_this_week))
    rows = db(query).select(db.school_classtypes.id,
                            db.school_classtypes.Name,
                            db.school_classtypes.Link,
                            db.school_classtypes.Description,
                            db.school_classtypes.thumbsmall,
                            db.school_classtypes.thumblarge,
                            orderby=db.school_classtypes.Name,
                            cache=caching)

    for row in rows:

        thumblarge_url = ''
        thumbsmall_url = ''

        if row.thumblarge:
            thumblarge_url = '%s://%s%s' % (request.env.wsgi_url_scheme,
                                            request.env.http_host,
                                            URL('default', 'download', args=row.thumblarge,
                                                extension=''))
        if row.thumbsmall:
            thumbsmall_url = '%s://%s%s' % (request.env.wsgi_url_scheme,
                                            request.env.http_host,
                                            URL('default', 'download', args=row.thumbsmall,
                                                extension=''))

        classtypes.append(dict(id=row.id,
                               Name=row.Name,
                               Link=row.Link,
                               LinkThumbSmall=thumbsmall_url,
                               LinkThumbLarge=thumblarge_url,
                               Description=row.Description,
                               ))

    data['classtypes'] = classtypes

    # Teachers
    query = (db.auth_user.trashed == False) & \
            (db.auth_user.teacher == True) & \
            (db.auth_user.id.belongs(teacher_ids_this_week))
    teachers = []
    rows = db(query).select(db.auth_user.id,
                            db.auth_user.full_name,
                            db.auth_user.teacher_role,
                            db.auth_user.teacher_bio,
                            db.auth_user.teacher_bio_link,
                            db.auth_user.teacher_website,
                            db.auth_user.thumbsmall,
                            db.auth_user.thumblarge,
                            orderby=db.auth_user.full_name,
                            cache=caching)
    for row in rows:
        name = row.full_name

        thumblarge_url = ''
        thumbsmall_url = ''

        if row.thumblarge:
            thumblarge_url = '%s://%s%s' % (request.env.wsgi_url_scheme,
                                            request.env.http_host,
                                            URL('default', 'download', args=row.thumblarge,
                                                extension=''))

        if row.thumbsmall:
            thumbsmall_url = '%s://%s%s' % (request.env.wsgi_url_scheme,
                                            request.env.http_host,
                                            URL('default', 'download', args=row.thumbsmall,
                                                extension=''))

        teachers.append(dict(id=row.id,
                             name=name,  # for legacy purposes. Was the only one with name.
                             Role=row.teacher_role,
                             LinkToBio=row.teacher_bio_link,
                             Bio=row.teacher_bio,
                             Website=row.teacher_website,
                             LinkThumbLarge=thumblarge_url,
                             LinkThumbSmall=thumbsmall_url,
                             Name=name))

    data['teachers'] = teachers

    # Locations
    query = (db.school_locations.AllowAPI == True) & \
            (db.school_locations.Archived == False) & \
            (db.school_locations.id.belongs(location_ids_this_week))
    rows = db(query).select(db.school_locations.id,
                            db.school_locations.Name,
                            cache=caching).as_list()
    data['locations'] = rows

    # Practice levels
    query = (db.school_levels.Archived == False)
    rows = db(query).select(db.school_levels.id,
                            db.school_levels.Name,
                            cache=caching).as_list()
    data['levels'] = rows

    return data


def schedule_get():
    '''
        Returns the schedule as XML or JSON depending on the extension used
        Variables required:
        - user: OpenStudio API user
        - key: Key for OpenStudio API user
        - year: Choose year to return schedule for
        - week: Chose week to return schedule for
    '''
    # forget session
    session.forget(response)
    # check extension
    result = call_check_extension()
    if result['error']:
        return result['error_msg']
    else:
        response.view = result['view']

    if ( 'user' in request.vars and
         'key' in request.vars and
         'year' in request.vars and
         'week' in request.vars ):
        try:
            user = request.vars['user']
            key = request.vars['key']
            year = int(request.vars['year'])
            week = int(request.vars['week'])

            # check auth
            auth_result = do_auth(user, key)
            if not auth_result['authenticated']:
                return dict(data=auth_result['message'])

            sorting = 'location'
            if 'SortBy' in request.vars:
                if request.vars['SortBy'] == 'time':
                    sorting = 'starttime'

            # check for TeacherID
            TeacherID = None
            if 'TeacherID' in request.vars:
                TeacherID = int(request.vars['TeacherID'])

            # check for ClassTypeID
            ClassTypeID = None
            if 'ClassTypeID' in request.vars:
                ClassTypeID = int(request.vars['ClassTypeID'])

            # check for LocationID
            LocationID = None
            if 'LocationID' in request.vars:
                LocationID = int(request.vars['LocationID'])

            # check for LevelID
            LevelID = None
            if 'LevelID' in request.vars:
                LevelID = int(request.vars['LevelID'])


            # Don't cache when running tests
            if web2pytest.is_running_under_test(request, request.application):
                data = _schedule_get(year, week, sorting, TeacherID, ClassTypeID, LocationID, LevelID)
            else:
                cache_key = 'openstudio_api_schedule_get_' + unicode(year) + '_' + \
                            'week_' + unicode(week) + '_' + \
                            'sorting_' + sorting + '_' + \
                            'TeacherID_' + unicode(TeacherID) + '_' + \
                            'ClassTypeID_' + unicode(ClassTypeID) + '_' + \
                            'LocationID_' + unicode(LocationID) + '_' + \
                            'LevelID_' + unicode(LevelID)
                data = cache.ram(cache_key,
                                 lambda: _schedule_get(year, week, sorting, TeacherID, ClassTypeID, LocationID, LevelID),
                                 time_expire=cache_15_min)

        except ValueError:
            data = T("Value error")
    else:
        data = T("Missing value: user, key, year and week are required values, \
                  one or more was missing in your request.")

    ## allow all domains to request this resource
    ## Only enable when you really need it, server side implementation is recommended.
    response.headers["Access-Control-Allow-Origin"] = "*"


    return dict(data=data)


def schedule_get_day_get_teachers(class_date):
    '''
        Function returns teachers for a selected day
    '''
    query = (db.classes_teachers.Startdate <= class_date) &\
            ((db.classes_teachers.Enddate >= class_date) |
             (db.classes_teachers.Enddate == None))

    d = dict()
    rows = db(query).select(db.classes_teachers.ALL)
    for row in rows:
        d[row.classes_id] = dict(teacher_id=row.auth_teacher_id,
                                 teacher_id2=row.auth_teacher_id2)

    return d


def schedule_get_days():
    '''

    '''
    # forget session
    session.forget(response)
    # check extension
    result = call_check_extension()
    if result['error']:
        return result['error_msg']
    else:
        response.view = result['view']

    # check vars
    try:
        date_format = '%Y-%m-%d'
        user = request.vars['user']
        key = request.vars['key']
        date_start = request.vars['date_start']
        date_start = datetime.datetime.strptime(date_start, date_format)
        date_start = datetime.date(date_start.year,
                                   date_start.month,
                                   date_start.day)
        date_end = request.vars['date_end']
        date_end = datetime.datetime.strptime(date_end, date_format)
        date_end = datetime.date(date_end.year,
                                 date_end.month,
                                 date_end.day)
    except:
        return T("Missing value: user, key, date_start and date_end are \
                  required values, one or more was missing in your request. \
                  (Date format: yyyy-mm-dd)")

    # check auth
    auth_result = do_auth(user, key)
    if not auth_result['authenticated']:
        return auth_result['message']

    # check for TeacherID
    TeacherID = None
    if 'TeacherID' in request.vars:
        TeacherID = int(request.vars['TeacherID'])

    # check for ClassTypeID
    ClassTypeID = None
    if 'ClassTypeID' in request.vars:
        ClassTypeID = int(request.vars['ClassTypeID'])

    # check for LocationID
    LocationID = None
    if 'LocationID' in request.vars:
        LocationID = int(request.vars['LocationID'])

    # check for LevelID
    LevelID = None
    if 'LevelID' in request.vars:
        LevelID = int(request.vars['LevelID'])

    # check for SortBy
    sorting = 'location'
    if 'SortBy' in request.vars:
        if request.vars['SortBy'] == 'time':
            sorting = 'starttime'

    current_date = date_start
    delta = datetime.timedelta(days=1)
    data = []
    while current_date <= date_end:
        today = {}
        class_schedule = ClassSchedule(
            current_date,
            filter_id_school_classtype = ClassTypeID,
            filter_id_school_location = LocationID,
            filter_id_school_level = LevelID,
            filter_id_teacher = TeacherID,
            filter_public = True,
            sorting=sorting,
        )

        today['classes'] = class_schedule.get_day_list()

        today['date'] = current_date
        data.append(today)

        current_date += delta


    ## allow all domains to request this resource
    ## Only enable when you really need it, server side implementation is recommended.
    # response.headers["Access-Control-Allow-Origin"] = "*"


    return dict(data=data)


def _workshops_get(var=None):
    '''
        Returns upcoming workshops as XML or JSON depending on the extension used
        Variables required:
        - user: OpenStudio API user
        - key: Key for OpenStudio API user
    '''
    ws = WorkshopSchedule(TODAY_LOCAL,
                          filter_only_public=True)
    rows = ws.get_workshops_rows()

    workshops = []
    for i, row in enumerate(rows):
        repr_row = list(rows[i:i + 1].render())[0]

        thumblarge_url = _get_url_thumbnail(row.workshops.thumblarge)
        thumbsmall_url = _get_url_thumbnail(row.workshops.thumbsmall)

        teacher = _workshop_get_teacher(row.workshops.auth_teacher_id)
        teacher2 = _workshop_get_teacher(row.workshops.auth_teacher_id2)

        workshop = {
            'id': row.workshops.id,
            'Name': row.workshops.Name,
            'Tagline': row.workshops.Tagline,
            'Startdate': row.workshops.Startdate,
            'Enddate': row.workshops.Enddate,
            'Starttime': row.workshops.Starttime,
            'Endtime': row.workshops.Endtime,
            'LocationID': row.workshops.school_locations_id,
            'Location': repr_row.workshops.school_locations_id,
            'Teacher': teacher,
            'Teacher2': teacher2,
            'Preview': repr_row.workshops.Preview,
            'Description': repr_row.workshops.Description,
            'Price': row.workshops_products.Price,
            'LinkThumbLarge': thumblarge_url,
            'LinkThumbSmall': thumbsmall_url,
            'LinkShop': workshop_get_url_shop(row.workshops.id)
        }

        workshops.append(workshop)


    return dict(data=workshops)


def workshops_get():
    '''
        Cache workshops list for API
    '''
    # forget session
    session.forget(response)

    # check extension
    result = call_check_extension()
    if result['error']:
        return result['error_msg']
    else:
        response.view = result['view']

    # check vars
    try:
        user = request.vars['user']
        key = request.vars['key']
    except:
        return T("Missing value: user and key are required values, one or more was missing in your request. ")

    # check auth
    auth_result = do_auth(user, key)
    if not auth_result['authenticated']:
        return auth_result['message']


    # Don't cache when running tests
    if web2pytest.is_running_under_test(request, request.application):
        data = _workshops_get()
    else:
        cache_key = 'openstudio_workshops_api_workshops_get'
        data = cache.ram(cache_key,
                         lambda: _workshops_get(),
                         time_expire=CACHE_LONG)

    return data


def workshop_get():
    """
        Returns workshop as XML or JSON depending on the extension used
        Variables required:
        - user: OpenStudio API user
        - key: Key for OpenStudio API user
        - id: Workshops id
    """
    # forget session
    session.forget(response)

    # check extension
    result = call_check_extension()
    if result['error']:
        return result['error_msg']
    else:
        response.view = result['view']

    # check vars
    try:
        user = request.vars['user']
        key = request.vars['key']
    except:
        return T("Missing value: user and key are required values, one or more was missing in your request. ")

    # check auth
    auth_result = do_auth(user, key)
    if not auth_result['authenticated']:
        return auth_result['message']

    wsID = request.vars['id']
    workshop = Workshop(wsID)

    # Check if the workshop is allowed over the API / in the shop
    if not workshop.PublicWorkshop:
        return 'Not found'

    # Ok, return stuff
    shop_url = workshop_get_url_shop(wsID)
    thumblarge_url = _get_url_thumbnail(workshop.thumblarge)
    thumbsmall_url = _get_url_thumbnail(workshop.thumbsmall)

    activities = []
    rows = workshop.get_activities()
    for i, row in enumerate(rows):
        repr_row = list(rows[i:i + 1].render())[0]

        activity = {
            'Name': row.Activity,
            'Date': row.Activitydate,
            'LocationID': row.school_locations_id,
            'Location': repr_row.school_locations_id,
            'Starttime': repr_row.Starttime,
            'Endtime': repr_row.Endtime,
            'TeacherID': row.auth_teacher_id,
            'Teacher': repr_row.auth_teacher_id,
            'TeacherID2': row.auth_teacher_id2,
            'Teacher2': repr_row.auth_teacher_id2,
        }

        activities.append(activity)

    teacher = _workshop_get_teacher(row.auth_teacher_id)
    teacher2 = _workshop_get_teacher(row.auth_teacher_id2)

    workshop = {
        'id': workshop.wsID,
        'Name': workshop.Name,
        'Tagline': workshop.Tagline,
        'Startdate': workshop.Startdate,
        'Enddate': workshop.Enddate,
        'Starttime': workshop.Starttime,
        'Endtime': workshop.Endtime,
        'LocationID': workshop.school_locations_id,
        'Location': workshop.school_location,
        'Teacher': teacher,
        'Teacher2': teacher2,
        'Preview': workshop.Preview,
        'Description': workshop.Description,
        'Price': workshop.get_full_workshop_price(),
        'LinkThumbLarge': thumblarge_url,
        'LinkThumbSmall': thumbsmall_url,
        'LinkShop': workshop_get_url_shop(workshop.wsID),
        'Activities': activities,
    }

    return dict(data=workshop)


def workshop_get_url_shop(wsID):
    """
        :param wsID: db.workshops.id
        :return: Link to OpenStudio shop
    """
    shop_url = URL('shop', 'event', vars={'wsID': wsID},
                   scheme=True,
                   host=True,
                   extension='')

    return shop_url


def _get_url_thumbnail(download_url):
    '''
        :param rel_url: db.workshops.thumblarge
        :return: formatted url
    '''
    url = ''
    if download_url:
        url = URL('default', 'download', args=download_url,
                  scheme=True,
                  host=True,
                  extension='')
    return url


def _workshop_get_teacher(teID):
    """
        :param teID: db.auth_user.id
        :return: dict containing teacher info
    """
    row = db.auth_user(teID)
    if row is None:
        return ''

    thumblarge_url = _get_url_thumbnail(row.thumblarge)
    thumbsmall_url = _get_url_thumbnail(row.thumbsmall)

    return dict(id=row.id,
                Name=row.full_name,
                Role=row.teacher_role,
                LinkToBio=row.teacher_bio_link,
                Bio=row.teacher_bio,
                Website=row.teacher_website,
                LinkThumbLarge=thumblarge_url,
                LinkThumbSmall=thumbsmall_url)


def _school_subscriptions_get(var=None):
    """
        Get school subscriptions from the database and return as list sorted by name
    """
    query = '''
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
        ORDER BY sc.SortOrder DESC, sc.Name
    '''.format(today=TODAY_LOCAL)

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

    return data


def school_subscriptions_get():
    '''
        Returns public subscriptions as XML or JSON depending on the extension used
        Variables required:
        - user: OpenStudio API user
        - key: Key for OpenStudio API user
    '''
    # forget session
    session.forget(response)

    # check extension
    result = call_check_extension()
    if result['error']:
        return result['error_msg']
    else:
        response.view = result['view']

    # check vars
    try:
        user = request.vars['user']
        key = request.vars['key']
    except:
        return T("Missing value: user and key are required values, one or more was missing in your request. ")

    # check auth
    auth_result = do_auth(user, key)
    if not auth_result['authenticated']:
        return auth_result['message']

    # Don't cache when running tests
    if web2pytest.is_running_under_test(request, request.application):
        data = _school_subscriptions_get()
    else:
        cache_key = 'openstudio_school_subcriptions_api_get'
        data = cache.ram(cache_key,
                         lambda: _school_subscriptions_get(),
                         time_expire=CACHE_LONG)

    return {'data':data}


def _school_classcards_get(var=None):
    '''
        Get public school classcards
    '''
    query = (db.school_classcards.PublicCard == True) & \
            (db.school_classcards.Archived == False)
    rows = db(query).select(db.school_classcards.Name,
                            db.school_classcards.Description,
                            db.school_classcards.Price,
                            db.school_classcards.Validity,
                            db.school_classcards.ValidityUnit,
                            db.school_classcards.Classes,
                            db.school_classcards.Unlimited,
                            db.school_classcards.Trialcard,
                            orderby=db.school_classcards.Name)

    return rows.as_list()


def school_classcards_get():
    '''
        Returns public subscriptions as XML or JSON depending on the extension used
        Variables required:
        - user: OpenStudio API user
        - key: Key for OpenStudio API user
    '''
    # forget session
    session.forget(response)

    # check extension
    result = call_check_extension()
    if result['error']:
        return result['error_msg']
    else:
        response.view = result['view']

    # check vars
    try:
        user = request.vars['user']
        key = request.vars['key']
    except:
        return T("Missing value: user and key are required values, one or more was missing in your request. ")

    # check auth
    auth_result = do_auth(user, key)
    if not auth_result['authenticated']:
        return auth_result['message']

    # Don't cache when running tests
    if web2pytest.is_running_under_test(request, request.application):
        data = _school_classcards_get()
    else:
        cache_key = 'openstudio_school_classcards_api_get'
        data = cache.ram(cache_key,
                         lambda: _school_classcards_get(),
                         time_expire=CACHE_LONG)

    return {'data':data}


def _school_teachers_get_classtypes(teID):
    '''
        Return dict of classtypes for a teacher
    '''
    query = (db.teachers_classtypes.auth_user_id == teID) & \
            (db.school_classtypes.AllowAPI == True) & \
            (db.school_classtypes.Archived == False)

    left = [ db.school_classtypes.on(db.teachers_classtypes.school_classtypes_id == db.school_classtypes.id)]

    data = []
    rows = db(query).select(
        db.school_classtypes.id,
        db.school_classtypes.Name,
        left=left,
        orderby=db.school_classtypes.Name
    )

    for row in rows:
        data.append({'id':row.id, 'Name':row.Name})

    return data


def _school_teachers_get_by_classtype(ctID):
    '''
        Get school teachers
    '''
    left = None

    query = (db.auth_user.teacher == True) & \
            (db.auth_user.trashed == False)

    if ctID:
        # build query to select only teachers marked for a specific class type
        query &= (db.teachers_classtypes.school_classtypes_id == ctID)
        left = [db.teachers_classtypes.on(db.teachers_classtypes.auth_user_id == db.auth_user.id)]

    rows = db(query).select(
        db.auth_user.id,
        db.auth_user.full_name,
        db.auth_user.teacher_role,
        db.auth_user.teacher_bio_link,
        db.auth_user.teacher_bio,
        db.auth_user.teacher_website,
        db.auth_user.thumbsmall,
        db.auth_user.thumblarge,
        left=left,
        orderby = db.auth_user.full_name
    )

    # add classtypes for teacher

    teachers = []
    for row in rows:
        teachers.append({
            'id': row.id,
            'Name': row.full_name,
            'Role': row.teacher_role,
            'LinkToBio': row.teacher_bio_link,
            'Bio': row.teacher_bio,
            'Website': row.teacher_website,
            'LinkThumbSmall': _get_url_thumbnail(row.thumbsmall),
            'LinkThumbLarge': _get_url_thumbnail(row.thumblarge),
            'ClassTypes': _school_teachers_get_classtypes(row.id)
        })

    return teachers


def school_teachers_get():
    '''
        Returns list of teachers as XML or JSON depending on the extension used
        Variables required:
        - user: OpenStudio API user
        - key: Key for OpenStudio API user
    '''
    # forget session
    session.forget(response)

    # check extension
    result = call_check_extension()
    if result['error']:
        return result['error_msg']
    else:
        response.view = result['view']

    # check vars
    try:
        user = request.vars['user']
        key = request.vars['key']
    except:
        return T("Missing value: user and key are required values, one or more was missing in your request. ")

    # check auth
    auth_result = do_auth(user, key)
    if not auth_result['authenticated']:
        return auth_result['message']

    # Don't cache when running tests
    if web2pytest.is_running_under_test(request, request.application):
        data = _school_teachers_get_by_classtype(request.vars['ctID'])
    else:
        if 'ClassTypeID' in request.vars:
            ctID = request.vars['ClassTypeID']
            cache_key = 'openstudio_school_teachers_api_get_ClassTypeID_' + ctID
        else:
            ctID = None
            cache_key = 'openstudio_school_teachers_api_get_all'

        data = cache.ram(cache_key,
                         lambda: _school_teachers_get_by_classtype(ctID),
                         time_expire=CACHE_LONG)

    return {'data':data}


def _school_classtypes_get(var=None):
    '''
        Get school class types
    '''
    # ClassTypes
    classtypes = []
    query = (db.school_classtypes.Archived == False) & \
            (db.school_classtypes.AllowAPI == True)
    rows = db(query).select(db.school_classtypes.id,
                            db.school_classtypes.Name,
                            db.school_classtypes.Link,
                            db.school_classtypes.Description,
                            db.school_classtypes.thumbsmall,
                            db.school_classtypes.thumblarge,
                            orderby=db.school_classtypes.Name)

    for row in rows:
        classtypes.append(dict(id=row.id,
                               Name=row.Name,
                               Link=row.Link,
                               LinkThumbSmall=_get_url_thumbnail(row.thumbsmall),
                               LinkThumbLarge=_get_url_thumbnail(row.thumblarge),
                               Description=row.Description,
                               ))

    return classtypes


def school_classtypes_get():
    '''
        Returns list of teachers as XML or JSON depending on the extension used
        Variables required:
        - user: OpenStudio API user
        - key: Key for OpenStudio API user
    '''
    # forget session
    session.forget(response)

    # check extension
    result = call_check_extension()
    if result['error']:
        return result['error_msg']
    else:
        response.view = result['view']

    # check vars
    try:
        user = request.vars['user']
        key = request.vars['key']
    except:
        return T("Missing value: user and key are required values, one or more was missing in your request. ")

    # check auth
    auth_result = do_auth(user, key)
    if not auth_result['authenticated']:
        return auth_result['message']

    # Don't cache when running tests
    if web2pytest.is_running_under_test(request, request.application):
        data = _school_classtypes_get()
    else:
        cache_key = 'openstudio_school_classtypes_api_get_all'

        data = cache.ram(cache_key,
                         lambda: _school_classtypes_get(),
                         time_expire=CACHE_LONG)

    return {'data':data}