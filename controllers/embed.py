# -*- coding: utf-8 -*-

from general_helpers import datestr_to_python

def index():
    """
    Embed index
    :return:
    """
    return "hello world"


def classes():
    """
        List classes in shop
    """
    response.view = 'embed/index.html'

    if 'date' in request.vars:
        start_date = datestr_to_python(DATE_FORMAT, request.vars['date'])
        if start_date < TODAY_LOCAL:
            start_date = TODAY_LOCAL
    else:
        start_date = TODAY_LOCAL

    # set up filter variables
    filter_id_school_location = ''
    filter_id_school_classtype = ''
    filter_id_school_level = ''
    filter_id_teacher = ''

    if 'location' in request.vars:
        filter_id_school_location = request.vars['location']
    if 'teacher' in request.vars:
        filter_id_teacher = request.vars['teacher']
    if 'classtype' in request.vars:
        filter_id_school_classtype = request.vars['classtype']

    filter = classes_get_filter(start_date,
                                filter_id_school_classtype=filter_id_school_classtype,
                                filter_id_school_location=filter_id_school_location,
                                filter_id_school_level='',
                                filter_id_teacher=filter_id_teacher)

    days = []
    for day in range(0, 7):
        date = start_date + datetime.timedelta(days=day)
        classes_list = classes_get_day(date,
                                       filter_id_school_classtype=filter_id_school_classtype,
                                       filter_id_school_location=filter_id_school_location,
                                       filter_id_school_level='',
                                       filter_id_teacher=filter_id_teacher)

        days.append(dict(date=date, weekday=date.isoweekday(), classes=classes_list))


    classes = DIV()
    for day in days:
        header = H3(NRtoDay(day['weekday']), ' ',
                    XML('<small>' + day['date'].strftime('%d %B %Y') + '</small>'))

        table_header = DIV(
            DIV(SPAN(T('Time')),
                _class='col-md-2'),
            DIV(SPAN(T('Location')),
                _class='col-md-2'),
            DIV(SPAN(T('Class')),
                _class='col-md-3'),
            DIV(SPAN(T('Teacher')),
                _class='col-md-2'),
            DIV(SPAN(T('Spaces')),
                _class='col-md-1'),
            DIV(' ',
                _class='col-md-2'), # Actions
            _class='row shop_classes_table_header bold hidden-xs hidden-sm'
        )

        table = DIV(table_header, _class='shop-classes')
        for c in day['classes']:
            time = SPAN(c['Starttime'], ' - ', c['Endtime'])

            sub = ''
            if c['Subteacher']:
                sub = ' (sub)'

            book = classes_get_button_book(c)

            table_row = DIV(
                DIV(time,
                    _class='col-md-2'),
                DIV(c['Location'],
                    _class='col-md-2'),
                DIV(c['ClassType'],
                    _class='col-md-3'),
                DIV(c['Teacher'], ' ', sub,
                    _class='col-md-2'),
                DIV('(', c['BookingSpacesAvailable'] , ')',
                    _class='col-md-1 grey'),
                DIV(DIV(book, _class='pull-right'),
                    _class='col-md-2'),  # Actions
                _class='row'
            )

            table.append(table_row)

        class_day = DIV(
            DIV(DIV(header, _class="col-md-12"), _class="row"),
            DIV(
                DIV(
                    DIV(table,
                        _class="box-body no-padding"
                    ),
                    _class="box box-solid"
                ),
                # _class="col-md-12"
            ),
            _class="row"
        )
        classes.append(class_day)

    return dict(content=DIV(filter, classes))


def classes_get_button_book(c):
    """
        :param  c: Class from openstudio.py.ClassSchedule.get_day_list
        :return: book class button (or text)
    """
    book = SPAN(T('Finished'), _class='grey small_font')
    if c['BookingStatus'] == 'ongoing':
        book = SPAN(T('In session...'), _class='grey small_font')
    elif c['BookingStatus'] == 'cancelled':
        book = SPAN(T('Cancelled'), _class='grey small_font')
    elif c['BookingStatus'] == 'not_yet_open':
        book = SPAN(T('Book from'), ' ', c['BookingOpen'].strftime(DATE_FORMAT), _class='grey small_font')
    elif c['BookingStatus'] == 'full':
        book = SPAN(T('Fully booked'), _class='grey small_font')
    elif c['BookingStatus'] == 'ok':
        book = A(SPAN(T('Book'), ' ', os_gui.get_fa_icon('fa-chevron-right')), _href=c['LinkShop'])

    return book


def classes_get_filter(date,
                       filter_id_school_classtype='',
                       filter_id_school_location='',
                       filter_id_school_level='',
                       filter_id_teacher=''):
    """
        :param filter_id_school_classtype: db.school_classtypes.id
        :param filter_id_school_location: db.school_locations.id
        :param filter_id_school_level: db.school_levels.id
        :param filter_id_teacher: db.auth_user.id (teacher = True)
        :return: div containing filter form for shop classes
    """
    date_formatted = date.strftime(DATE_FORMAT)

    au_query = (db.auth_user.teacher == True) & \
               (db.auth_user.trashed == False)

    sl_query = (db.school_locations.Archived == False) & \
               (db.school_locations.AllowAPI == True)

    ct_query = (db.school_classtypes.Archived == False) & \
               (db.school_classtypes.AllowAPI == True)

    sle_query = (db.school_levels.Archived == False)

    form = SQLFORM.factory(
        Field('location',
            requires=IS_IN_DB(db(sl_query),'school_locations.id', '%(Name)s',
                              zero=T('All locations')),
            default=filter_id_school_location,
            label=""),
        Field('teacher',
            requires=IS_IN_DB(db(au_query),'auth_user.id',
                              '%(full_name)s',
                              zero=T('All teachers')),
            default=filter_id_teacher,
            label=""),
        Field('classtype',
            requires=IS_IN_DB(db(ct_query),'school_classtypes.id', '%(Name)s',
                              zero=T('All classtypes')),
            default=filter_id_school_classtype,
            label=""),
        # Field('level',
        #     requires=IS_IN_DB(db(sle_query),'school_levels.id', '%(Name)s',
        #                       zero=T('All levels')),
        #     default=filter_id_school_level,
        #     label=""),
        submit_button=T('Go'),
        formstyle='divs',
        )

    # submit form on change
    selects = form.elements('select')
    for select in selects:
        select.attributes['_onchange'] = "this.form.submit();"

    box = DIV(
        DIV(
            DIV(
                DIV(form.custom.begin,
                    DIV(form.custom.widget.location,
                        _class='col-md-3'),
                    DIV(form.custom.widget.teacher,
                        _class='col-md-3'),
                    DIV(form.custom.widget.classtype,
                        _class='col-md-3'),
                    # form.custom.widget.level,
                    DIV(classes_get_week_browser(date),
                        _class='col-md-3'),
                    form.custom.end,
                    _class="box-body"
                ),
                _class="box box-solid"
            ),
        ),
        _class='row'
    )

    return box


def classes_get_week_browser(date):
    """
        :param week: int week
        :param year: int year
        :return: buttons to browse through weeks
    """
    one_week = datetime.timedelta(days=7)
    date_prev = (date - one_week).strftime(DATE_FORMAT)
    date_next = (date + one_week).strftime(DATE_FORMAT)


    url_prev = URL('classes', vars={ 'date': date_prev })
    if date <= TODAY_LOCAL:
        url_prev = '#'
    url_next = URL('classes', vars={ 'date': date_next })

    previous = A(I(_class='fa fa-angle-left'),
                 _href=url_prev,
                 _class='btn btn-default')

    if date <= TODAY_LOCAL:
        previous['_disabled'] = 'disabled'

    nxt = A(I(_class='fa fa-angle-right'),
            _href=url_next,
            _class='btn btn-default')

    today = ''
    if date > TODAY_LOCAL:
        today = os_gui.get_button(
            'noicon',
            URL('embed', 'classes',
                vars={'date': TODAY_LOCAL.strftime(DATE_FORMAT)}),
            title=T('Today'),
            btn_size='',
            _class="pull-right"
        )

    buttons = DIV(previous, nxt, _class='btn-group pull-right')

    return DIV(buttons, ' ', today, _class='shop-classes-week-chooser')


def classes_get_day(date,
                    filter_id_school_classtype,
                    filter_id_school_location,
                    filter_id_school_level,
                    filter_id_teacher):
    """
        :param weekday: ISO weekday (1-7)
        :return: List of classes for day
    """
    from openstudio.os_class_schedule import ClassSchedule

    cs = ClassSchedule(
        date,
        filter_id_school_classtype = filter_id_school_classtype,
        filter_id_school_location = filter_id_school_location,
        filter_id_school_level = filter_id_school_level,
        filter_id_teacher = filter_id_teacher,
        filter_public = True,
        sorting = 'starttime' )

    return cs.get_day_list()