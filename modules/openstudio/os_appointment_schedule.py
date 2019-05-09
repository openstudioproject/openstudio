# -*- coding: utf-8 -*-

import datetime

from gluon import *

from general_helpers import max_string_length
from general_helpers import NRtoDay


class AppointmentSchedule:
    def __init__(self, date,
                       filter_id_school_appointment = None,
                       filter_id_school_location = None,
                       filter_id_teacher = None,
                       filter_public = False,
                       filter_starttime_from = None,
                       sorting = 'starttime'
                 ):

        self.date = date

        self.filter_id_school_appointment = filter_id_school_appointment
        self.filter_id_school_location = filter_id_school_location
        self.filter_id_teacher = filter_id_teacher
        self.filter_public = filter_public
        self.sorting = sorting

    #     self.bookings_open = self._get_bookings_open()
    #
    #
    # def _get_bookings_open(self):
    #     """
    #         Returns False if no booking limit is defines, otherwise it returns the date from which
    #         bookings for this class will be accepted.
    #     """
    #     get_sys_property = current.globalenv['get_sys_property']
    #
    #     bookings_open = False
    #     shop_classes_advance_booking_limit = get_sys_property('shop_classes_advance_booking_limit')
    #     if not shop_classes_advance_booking_limit is None:
    #         delta = datetime.timedelta(days=int(shop_classes_advance_booking_limit))
    #         bookings_open = self.date - delta
    #
    #     return bookings_open


    def _get_day_filter_query(self):
        """
            Returns the filter query for the schedule
        """
        where = ''

        if self.filter_id_teacher:
            where += 'AND ((CASE WHEN sotc.auth_teacher_id IS NULL \
                            THEN clt.auth_teacher_id  \
                            ELSE sotc.auth_teacher_id END) = '
            where += unicode(self.filter_id_teacher) + ' '
            where += 'OR (CASE WHEN sotc.auth_teacher_id2 IS NULL \
                          THEN clt.auth_teacher_id2  \
                          ELSE sotc.auth_teacher_id2 END) = '
            where += unicode(self.filter_id_teacher) + ') '
        if self.filter_id_school_appointment:
            where += 'AND (CASE WHEN sotc.school_appointments_id IS NULL \
                           THEN cla.school_appointments_id  \
                           ELSE sotc.school_appointments_id END) = '
            where += unicode(self.filter_id_school_appointment) + ' '
        if self.filter_id_school_location:
            where += 'AND (CASE WHEN sotc.school_locations_id IS NULL \
                           THEN cla.school_locations_id  \
                           ELSE sotc.school_locations_id END) = '
            where += unicode(self.filter_id_school_location) + ' '
        if self.filter_public:
            where += "AND s.AllowAPI = 'T' "
            where += "AND sl.AllowAPI = 'T' "
            where += "AND sct.AllowAPI = 'T' "

        return where


    def _get_day_row_status(self, row):
        """
            Return status for row
        """
        status = 'normal'
        status_marker = DIV(_class='status_marker bg_green')
        if row.schedule_otc.Status == 'cancelled' or row.school_holidays.id:
            status = 'cancelled'
            status_marker = DIV(_class='status_marker bg_orange')
        elif row.schedule_otc.Status == 'open':
            status = 'open'
            status_marker = DIV(_class='status_marker bg_red')
        elif row.classes_teachers.teacher_role == 1:
            status = 'subteacher'
            status_marker = DIV(_class='status_marker bg_blue')

        return dict(status=status, marker=status_marker)


    def _get_day_get_table_get_permissions(self):
        """
            :return: dict containing button permissions for a user
        """
        auth = current.auth
        permissions = {}

        if auth.has_membership(group_id='Admins') or \
           auth.has_permission('read', 'classes_reservation'):
            permissions['classes_reservation'] = True
        if auth.has_membership(group_id='Admins') or \
           auth.has_permission('read', 'classes_waitinglist'):
            permissions['classes_waitinglist'] = True
        if auth.has_membership(group_id='Admins') or \
           auth.has_permission('read', 'classes_notes'):
            permissions['classes_notes'] = True
        if auth.has_membership(group_id='Admins') or \
           auth.has_permission('read', 'classes_revenue'):
            permissions['classes_revenue'] = True
        if auth.has_membership(group_id='Admins') or \
           auth.has_permission('create', 'schedule_otc'):
            permissions['schedule_otc'] = True
        if auth.has_membership(group_id='Admins') or \
           auth.has_permission('update', 'classes'):
            permissions['classes'] = True
        if auth.has_membership(group_id='Admins') or \
           auth.has_permission('delete', 'appointments'):
            permissions['appointments_delete'] = True

        return permissions


    def _get_day_get_table_get_buttons(self, clsID, date_formatted, permissions):
        """
            Returns buttons for schedule
            - one button group for edit & attendance buttons
            - separate button for delete
        """
        os_gui = current.globalenv['os_gui']
        T = current.T
        buttons = DIV(_class='pull-right')

        vars = { 'clsID':clsID,
                 'date' :date_formatted }


        links = [['header', T('Class on') + ' ' + date_formatted]]
        # check Attendance permission
        if permissions.get('classes_attendance', False):
            links.append(A(os_gui.get_fa_icon('fa-check-square-o'), T('Attendance'),
                           _href=URL('attendance', vars=vars)))
        # check Reservations permission
        if permissions.get('classes_reservation', False):
            links.append(
                A(os_gui.get_fa_icon('fa-calendar-check-o'),  T('Enrollments'),
                 _href=URL('reservations', vars=vars)))
        # check Waitinglist permission
        if permissions.get('classes_waitinglist', False):
            links.append(
                A(os_gui.get_fa_icon('fa-calendar-o'), T('Waitinglist'),
                  _href=URL('waitinglist', vars=vars)))
        # check Notes permission
        if permissions.get('classes_notes', False):
            links.append(
                A(os_gui.get_fa_icon('fa-sticky-note-o'), T('Notes'),
                  _href=URL('notes', vars=vars)))
        # check Revenue permission
        if permissions.get('classes_revenue', False):
            links.append(
                A(os_gui.get_fa_icon('fa-usd'), T('Revenue'),
                  _href=URL('revenue', vars=vars)))
        # check permissions to change this class
        if permissions.get('schedule_otc', False):
            links.append(A(os_gui.get_fa_icon('fa-pencil'),
                           T('Edit'),
                           _href=URL('class_edit_on_date', vars=vars)))
        # Check permission to update weekly class
        if permissions.get('classes', False):
            links.append('divider')
            links.append(['header', T('All classes in series')])
            links.append(A(os_gui.get_fa_icon('fa-pencil'),
                           T('Edit'), ' ',
                           _href=URL('class_edit', vars=vars)))

        class_menu = os_gui.get_dropdown_menu(
            links=links,
            btn_text=T('Actions'),
            btn_size='btn-sm',
            btn_icon='actions',
            menu_class='btn-group pull-right')

        remove = ''
        if permissions.get('classes_delete'):
            onclick_remove = "return confirm('" + \
                             T('Do you really want to delete this class?') + \
                             "');"
            remove = os_gui.get_button('delete_notext',
                       URL('class_delete', args=[clsID]),
                       onclick=onclick_remove)

            buttons.append(remove)

        return DIV(buttons, class_menu, _class='pull-right schedule_buttons')


    def _get_day_get_table_get_reservations(self, clsID, date_formatted, row, permissions):
        """
            Returns tools for schedule
            - reservations
        """
        auth = current.auth
        T = current.T

        tools = DIV()

        # get bookings count
        res = row.classes_schedule_count.Attendance or 0

        filled = SPAN(res, '/', row.classes.Maxstudents)

        link_class = ''
        if res > row.classes.Maxstudents:
            link_class = 'red'

        reservations = A(SPAN(T('Bookings'), ' ', filled),
                         _href=URL('attendance',
                                   vars={'clsID' : clsID,
                                         'date'  : date_formatted}),
                         _class=link_class)

        if permissions.get('classes_attendance', False):
            tools.append(reservations)

        return tools


    def _get_day_table_get_class_messages(self, row, clsID, date_formatted):
        """
            Returns messages for a class
        """
        os_gui = current.globalenv['os_gui']
        auth = current.auth
        T = current.T

        class_messages = []

        if row.school_holidays.Description:
            class_messages.append(
                SPAN(SPAN(_class=os_gui.get_icon('education') + ' grey'), ' ',
                     T('Holiday'), ' (',
                     A(row.school_holidays.Description,
                       _href=URL('schedule', 'holiday_edit',
                                 vars={'shID': row.school_holidays.id})),
                     ')'))

        if row.classes_teachers.teacher_role == 1:
            class_messages.append(T('Subteacher'))

        if row.schedule_otc.Status == 'cancelled':
            class_messages.append(T('Cancelled'))

        if row.schedule_otc.Status == 'open':
            class_messages.append(T('Open'))

        schedule_otc_update_permission = auth.has_membership(group_id='Admins') or \
                                        auth.has_permission('update', 'schedule_otc')
        if row.schedule_otc.id and schedule_otc_update_permission:
            _class = os_gui.get_icon('pencil') + ' grey'
            class_messages.append(
                A(SPAN(SPAN(_class=_class), ' ', T('Edited')),
                  _href=URL('class_edit_on_date',
                            vars={'clsID': clsID,
                                  'date': date_formatted})))

            if row.schedule_otc.Description:
                class_messages.append(row.schedule_otc.Description)

        num_messages = len(class_messages)
        msgs = SPAN()
        append = msgs.append
        for i, msg in enumerate(class_messages):
            append(msg)
            if i + 1 < num_messages:
                append(' | ')

        return msgs


    def _get_day_list_booking_status(self, row):
        """
            :param row: ClassSchedule.get_day_rows() row
            :return: booking status
        """
        pytz = current.globalenv['pytz']
        TIMEZONE = current.TIMEZONE
        NOW_LOCAL = current.NOW_LOCAL
        TODAY_LOCAL = current.TODAY_LOCAL

        local_tz = pytz.timezone(TIMEZONE)

        dt_start = datetime.datetime(self.date.year,
                                     self.date.month,
                                     self.date.day,
                                     int(row.classes.Starttime.hour),
                                     int(row.classes.Starttime.minute))
        dt_start = local_tz.localize(dt_start)
        dt_end = datetime.datetime(self.date.year,
                                   self.date.month,
                                   self.date.day,
                                   int(row.classes.Endtime.hour),
                                   int(row.classes.Endtime.minute))
        dt_end = local_tz.localize(dt_end)

        status = 'finished'
        if row.schedule_otc.Status == 'cancelled' or row.school_holidays.id:
            status = 'cancelled'
        elif dt_start <= NOW_LOCAL and dt_end >= NOW_LOCAL:
            # check start time
            status = 'ongoing'
        elif dt_start >= NOW_LOCAL:
            if not self.bookings_open == False and TODAY_LOCAL < self.bookings_open:
                status = 'not_yet_open'
            else:
                # check spaces for online bookings
                spaces = self._get_day_list_booking_spaces(row)
                if spaces < 1:
                    status = 'full'
                else:
                    status = 'ok'

        return status


    def _get_day_list_booking_spaces(self, row):
        """
        :param row: :param row: ClassSchedule.get_day_rows() row
        :return: int - available online booking spaces for a class
        """
        enrollments = row.classes_schedule_count.Reservations or 0
        enrollment_spaces = row.classes.MaxReservationsRecurring or 0
        enrollment_spaces_left = enrollment_spaces - enrollments

        spaces = row.classes.MaxOnlineBooking or 0
        online_booking = row.classes_schedule_count.OnlineBooking or 0
        #attendance = row.classes_schedule_count.Attendance or 0

        available_spaces = (spaces + enrollment_spaces_left) - online_booking
        if available_spaces < 1:
            available_spaces = 0
        #
        # print '### clsID' + unicode(row.classes.id)
        # print spaces
        # print enrollment_spaces_left
        # print online_booking
        # print available_spaces

        return available_spaces


    def _get_day_rows(self):
        """
            Helper function that returns a dict containing a title for the weekday,
            a date for the class and
            a SQLFORM.grid for a selected day which is within 1 - 7 (ISO standard).
        """
        date = self.date
        DATE_FORMAT = current.DATE_FORMAT
        db = current.db
        weekday = date.isoweekday()

        date_formatted = date.strftime(DATE_FORMAT)

        if self.sorting == 'location':
            orderby_sql = 'location_name, Starttime'
        elif self.sorting == 'starttime':
            orderby_sql = 'Starttime, location_name'

        fields = [
            db.schedule.id,
            db.schedule_otc.Status,
            db.schedule_otc.Description,
            db.schedule.school_locations_id,
            db.school_locations.Name,
            db.schedule.Starttime,
            db.schedule.Endtime,
            db.schedule.Startdate,
            db.schedule.Enddate,
            db.schedule.AllowAPI,
            db.schedule_otc.id,
            db.school_holidays.id,
            db.school_holidays.Description,
        ]

        where_filter = self._get_day_filter_query()

        query = """
        SELECT s.id,
               CASE WHEN sotc.Status IS NOT NULL
                    THEN sotc.Status
                    ELSE 'normal'
                    END AS Status,
               sotc.Description,
               CASE WHEN sotc.school_locations_id IS NOT NULL
                    THEN sotc.school_locations_id
                    ELSE s.school_locations_id
                    END AS school_locations_id,
               CASE WHEN sotc.school_locations_id IS NOT NULL
                    THEN slsotc.Name
                    ELSE sl.Name
                    END AS location_name,
               CASE WHEN sotc.Starttime IS NOT NULL
                    THEN sotc.Starttime
                    ELSE s.Starttime
                    END AS Starttime,
               CASE WHEN sotc.Endtime IS NOT NULL
                    THEN sotc.Endtime
                    ELSE s.Endtime
                    END AS Endtime,
               s.Startdate,
               s.Enddate,           
               s.AllowAPI,
               sotc.id,
               sho.id,
               sho.Description
        FROM schedule s
        LEFT JOIN
            ( SELECT id,
                     schedule_id,
                     ScheduleDate,
                     Status,
                     Description,
                     school_locations_id,
                     Starttime,
                     Endtime
              FROM schedule_otc
              WHERE ScheduleDate = '{schedule_date}' ) sotc
            ON s.id = sotc.schedule_id
        LEFT JOIN school_locations sl
            ON sl.id = s.school_locations_id
		LEFT JOIN school_locations slsotc
			ON slsotc.id = sotc.school_locations_id
        LEFT JOIN
            ( SELECT sh.id, sh.Description, shl.school_locations_id
              FROM school_holidays sh
              LEFT JOIN
                school_holidays_locations shl
                ON shl.school_holidays_id = sh.id
              WHERE sh.Startdate <= '{schedule_date}' AND
                    sh.Enddate >= '{schedule_date}') sho
            ON sho.school_locations_id = s.school_locations_id
        WHERE s.ScheduleType = 'appointment' AND
              (
                (s.FrequencyType = 'weekly' AND 
                 s.FrequencyInterval = {weekday} AND
                 s.Startdate <= '{schedule_date}' AND
                 (s.Enddate >= '{schedule_date}' OR s.Enddate IS NULL)) OR
                (s.FrequencyType = 'specific' AND s.Startdate = '{schedule_date}')
              )
              {where_filter}
        ORDER BY {orderby_sql}
        """.format(schedule_date = date,
                   weekday = weekday,
                   orderby_sql = orderby_sql,
                   where_filter = where_filter)

        # print query

        rows = db.executesql(query, fields=fields)

        return rows


    def get_day_rows(self):
        """
            Get day rows with caching 
        """
        #web2pytest = current.globalenv['web2pytest']
        #request = current.request

        # # Don't cache when running tests
        # if web2pytest.is_running_under_test(request, request.application):
        #     rows = self._get_day_rows()
        # else:
        #     cache = current.cache
        #     DATE_FORMAT = current.DATE_FORMAT
        #     CACHE_LONG = current.globalenv['CACHE_LONG']
        #     cache_key = 'openstudio_classschedule_get_day_rows_' + self.date.strftime(DATE_FORMAT)
        #     rows = cache.ram(cache_key , lambda: self._get_day_rows(), time_expire=CACHE_LONG)

        rows = self._get_day_rows()

        return rows


    def _get_day_table(self):
        """
            Returns table for today
        """
        os_gui = current.globalenv['os_gui']
        DATE_FORMAT = current.DATE_FORMAT
        ORGANIZATIONS = current.globalenv['ORGANIZATIONS']
        T = current.T
        date_formatted = self.date.strftime(DATE_FORMAT)

        table = TABLE(TR(TH(' ', _class='td_status_marker'), # status marker
                         TH(T('Location'), _class='location'),
                         TH(T('Class type'), _class='classtype'),
                         TH(T('Time'), _class='time'),
                         TH(T('Teacher'), _class='teacher'),
                         TH(T('Level'), _class='level'),
                         TH(T('Public'), _class='api'),
                         TH(T('')),
                         _class='os-table_header'),
                      _class='os-schedule')

        rows = self.get_day_rows()

        if len(rows) == 0:
            table = DIV(T("No appointments found on this day"))
        else:
            # avoiding some dots in the loop
            get_status = self._get_day_row_status
            get_teacher_roles = self._get_day_row_teacher_roles
            get_buttons = self._get_day_get_table_get_buttons
            get_class_messages = self._get_day_table_get_class_messages

            button_permissions = self._get_day_get_table_get_permissions()

            multiple_organizations = len(ORGANIZATIONS) > 1
            filter_id_status = self.filter_id_status
            msg_no_teacher = SPAN(T('No teacher'), _class='red')

            # Generate list of classes
            for i, row in enumerate(rows):
                repr_row = list(rows[i:i+1].render())[0]
                clsID = row.classes.id

                status_result = get_status(row)
                status = status_result['status']
                status_marker = status_result['marker']

                if filter_id_status and status != filter_id_status:
                    continue

                result = get_teacher_roles(row, repr_row)
                teacher = result['teacher_role']
                teacher2 = result['teacher_role2']

                api = INPUT(value=row.classes.AllowAPI,
                            _type='checkbox',
                            _value='api',
                            _disabled='disabled')

                buttons = get_buttons(clsID, date_formatted, button_permissions)
                reservations = get_reservations(clsID, date_formatted, row, button_permissions)
                class_messages = get_class_messages(row, clsID, date_formatted)

                if multiple_organizations:
                    organization = DIV(repr_row.classes.sys_organizations_id or '',
                                       _class='small_font grey pull-right btn-margin')
                else:
                    organization = ''

                row_class = TR(
                    TD(status_marker),
                    TD(max_string_length(repr_row.classes.school_locations_id, 16)),
                    TD(max_string_length(repr_row.classes.school_appointments_id, 24)),
                    TD(SPAN(repr_row.classes.Starttime, ' - ', repr_row.classes.Endtime)),
                    TD(teacher if (not status == 'open' and
                                   not row.classes_teachers.auth_teacher_id is None) \
                               else msg_no_teacher),
                    TD(max_string_length(repr_row.classes.school_levels_id, 12)),
                    TD(api),
                    TD(buttons),
                   _class='os-schedule_class')
                row_tools = TR(
                    TD(' '),
                    TD(class_messages, _colspan=3, _class='grey'),
                    TD(teacher2 if not status == 'open' else ''),
                    TD(),
                    TD(),
                    TD(organization),
                    _class='os-schedule_links',
                    _id='class_' + unicode(clsID))

                table.append(row_class)
                table.append(row_tools)

        return dict(table=table,
                    weekday=NRtoDay(self.date.isoweekday()),
                    date=date_formatted)


    def get_day_table(self):
        """
            Get day table with caching
        """
        web2pytest = current.globalenv['web2pytest']
        request = current.request
        auth = current.auth

        # Don't cache when running tests
        if web2pytest.is_running_under_test(request, request.application):
            rows = self._get_day_table()
        else:
            cache = current.cache
            DATE_FORMAT = current.DATE_FORMAT
            CACHE_LONG = current.globalenv['CACHE_LONG']
            cache_key = 'openstudio_appointments_schedule_get_day_table_' + \
                        unicode(auth.user.id) + '_' + \
                        self.date.strftime(DATE_FORMAT) + '_' + \
                        unicode(self.filter_id_school_appointment) + '_' + \
                        unicode(self.filter_id_school_location) + '_' + \
                        unicode(self.filter_id_teacher) + '_' + \
                        unicode(self.filter_public) + '_' + \
                        self.sorting

            rows = cache.ram(cache_key , lambda: self._get_day_table(), time_expire=CACHE_LONG)

        return rows


    # def get_day_list(self):
    #     """
    #         Format rows as list
    #     """
    #     os_gui = current.globalenv['os_gui']
    #     DATE_FORMAT = current.DATE_FORMAT
    #     T = current.T
    #     date_formatted = self.date.strftime(DATE_FORMAT)
    #
    #     rows = self.get_day_rows()
    #
    #     get_status = self._get_day_row_status
    #
    #     classes = []
    #     for i, row in enumerate(rows):
    #         repr_row = list(rows[i:i+1].render())[0]
    #
    #         # get status
    #         status_result = get_status(row)
    #         status = status_result['status']
    #
    #         # get teachers
    #         teacher_id = row.classes_teachers.auth_teacher_id
    #         teacher_id2 = row.classes_teachers.auth_teacher_id2
    #         teacher = repr_row.classes_teachers.auth_teacher_id
    #         teacher2 = repr_row.classes_teachers.auth_teacher_id2
    #         teacher_role = row.classes_teachers.teacher_role
    #         teacher_role2 = row.classes_teachers.teacher_role2
    #
    #         # check filter for teachers
    #         if self.filter_id_teacher:
    #             teacher_filter_id = int(self.filter_id_teacher)
    #             filter_check = (teacher_filter_id == teacher_id or
    #                             teacher_filter_id == teacher_id2)
    #             if not filter_check:
    #                 # break loop if it's not the teacher searched for
    #                 continue
    #
    #         # set holidays
    #         holiday = False
    #         holiday_description = ''
    #         if row.school_holidays.id:
    #             holiday = True
    #             holiday_description = row.school_holidays.Description
    #
    #         cancelled = False
    #         cancelled_description = ''
    #         if status == 'cancelled':
    #             cancelled = True
    #             cancelled_description = row.schedule_otc.Description
    #
    #         subteacher = False
    #         if ( row.classes_teachers.teacher_role == 1 or
    #              row.classes_teachers.teacher_role2 == 1 ):
    #             subteacher = True
    #
    #         # shop url
    #         shop_url = URL('shop', 'classes_book_options', vars={'clsID': row.classes.id,
    #                                                              'date' : date_formatted},
    #                        scheme=True,
    #                        host=True,
    #                        extension='')
    #
    #         # populate class data
    #         data = dict()
    #         data['ClassesID'] = row.classes.id
    #         data['LocationID'] = row.classes.school_locations_id
    #         data['Location'] = repr_row.classes.school_locations_id
    #         data['Starttime'] = repr_row.classes.Starttime
    #         data['time_starttime'] = row.classes.Starttime
    #         data['Endtime'] = repr_row.classes.Endtime
    #         data['time_endtime'] = row.classes.Endtime
    #         data['ClassTypeID'] = row.classes.school_appointments_id
    #         data['ClassType'] = repr_row.classes.school_appointments_id
    #         data['TeacherID'] = teacher_id
    #         data['TeacherID2'] = teacher_id2
    #         data['Teacher'] = teacher
    #         data['Teacher2'] = teacher2
    #         data['LevelID'] = row.classes.school_levels_id
    #         data['Level'] = repr_row.classes.school_levels_id
    #         data['Subteacher'] = subteacher
    #         data['Cancelled'] = cancelled
    #         data['CancelledDescription'] = cancelled_description
    #         data['Holiday'] = holiday
    #         data['HolidayDescription'] = holiday_description
    #         data['MaxStudents'] = row.classes.Maxstudents or 0 # Spaces for a class
    #         data['CountAttendance'] = row.classes_schedule_count.Attendance or 0
    #         data['CountAttendanceOnlineBooking'] = row.classes_schedule_count.OnlineBooking or 0
    #         data['BookingSpacesAvailable'] = self._get_day_list_booking_spaces(row)
    #         data['BookingStatus'] = self._get_day_list_booking_status(row)
    #         data['BookingOpen'] = self.bookings_open
    #         data['LinkShop'] = shop_url
    #
    #         classes.append(data)
    #
    #     return classes
