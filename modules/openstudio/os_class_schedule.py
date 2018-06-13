# -*- coding: utf-8 -*-

import datetime

from gluon import *


class ClassSchedule:
    def __init__(self, date,
                       filter_id_sys_organization = None,
                       filter_id_school_classtype = None,
                       filter_id_school_location = None,
                       filter_id_school_level = None,
                       filter_id_teacher = None,
                       filter_id_status = None,
                       filter_public = False,
                       sorting = 'starttime',
                       trend_medium = None,
                       trend_high = None):

        self.date = date

        self.filter_id_sys_organization = filter_id_sys_organization
        self.filter_id_school_classtype = filter_id_school_classtype
        self.filter_id_school_location = filter_id_school_location
        self.filter_id_teacher = filter_id_teacher
        self.filter_id_school_level = filter_id_school_level
        self.filter_id_status = filter_id_status
        self.filter_public = filter_public
        self.sorting = sorting
        self.trend_medium = trend_medium
        self.trend_high = trend_high

        self.bookings_open = self._get_bookings_open()


    def _get_bookings_open(self):
        """
            Returns False if no booking limit is defines, otherwise it returns the date from which
            bookings for this class will be accepted.
        """
        get_sys_property = current.globalenv['get_sys_property']

        bookings_open = False
        shop_classes_advance_booking_limit = get_sys_property('shop_classes_advance_booking_limit')
        if not shop_classes_advance_booking_limit is None:
            delta = datetime.timedelta(days=int(shop_classes_advance_booking_limit))
            bookings_open = self.date - delta

        return bookings_open


    def _get_day_filter_query(self):
        """
            Returns the filter query for the schedule
        """
        where = ''

        if self.filter_id_sys_organization:
            where += 'AND cla.sys_organizations_id = ' + unicode(self.filter_id_sys_organization) + ' '
        if self.filter_id_teacher:
            where += 'AND ((CASE WHEN cotc.auth_teacher_id IS NULL \
                            THEN clt.auth_teacher_id  \
                            ELSE cotc.auth_teacher_id END) = '
            where += unicode(self.filter_id_teacher) + ' '
            where += 'OR (CASE WHEN cotc.auth_teacher_id2 IS NULL \
                          THEN clt.auth_teacher_id2  \
                          ELSE cotc.auth_teacher_id2 END) = '
            where += unicode(self.filter_id_teacher) + ') '
        if self.filter_id_school_classtype:
            where += 'AND (CASE WHEN cotc.school_classtypes_id IS NULL \
                           THEN cla.school_classtypes_id  \
                           ELSE cotc.school_classtypes_id END) = '
            where += unicode(self.filter_id_school_classtype) + ' '
        if self.filter_id_school_location:
            where += 'AND (CASE WHEN cotc.school_locations_id IS NULL \
                           THEN cla.school_locations_id  \
                           ELSE cotc.school_locations_id END) = '
            where += unicode(self.filter_id_school_location) + ' '
        if self.filter_id_school_level:
            where += 'AND cla.school_levels_id = '
            where += unicode(self.filter_id_school_level) + ' '
        if self.filter_public:
            where += "AND cla.AllowAPI = 'T' "
            where += "AND sl.AllowAPI = 'T' "
            where += "AND sct.AllowAPI = 'T' "

        return where


    def _get_day_row_status(self, row):
        """
            Return status for row
        """
        status = 'normal'
        status_marker = DIV(_class='status_marker bg_green')
        if row.classes_otc.Status == 'cancelled' or row.school_holidays.id:
            status = 'cancelled'
            status_marker = DIV(_class='status_marker bg_orange')
        elif row.classes_otc.Status == 'open':
            status = 'open'
            status_marker = DIV(_class='status_marker bg_red')
        elif row.classes_teachers.teacher_role == 1:
            status = 'subteacher'
            status_marker = DIV(_class='status_marker bg_blue')

        return dict(status=status, marker=status_marker)


    def _get_day_row_teacher_roles(self, row, repr_row):
        """
            @return: dict with {teacher_role} and {teacher_role2} as keys
             teacher_role and teacher_role2 are names of teacher with labels
              applied
        """
        os_gui = current.globalenv['os_gui']
        T = current.T

        teacher_id = row.classes_teachers.auth_teacher_id
        teacher_id2 = row.classes_teachers.auth_teacher_id2
        teacher = repr_row.classes_teachers.auth_teacher_id
        teacher2 = repr_row.classes_teachers.auth_teacher_id2
        teacher_role = row.classes_teachers.teacher_role
        teacher_role2 = row.classes_teachers.teacher_role2

        # set label for teacher role
        if teacher_role == 1:  # sub
            teacher_role = SPAN(os_gui.get_os_label('blue', teacher),
                                _title=T('Sub teacher'))
        elif teacher_role == 2:  # assist
            teacher_role = SPAN(os_gui.get_os_label('yellow', teacher),
                                _title=T("Assistant"))
        elif teacher_role == 3:  # karma
            teacher_role = SPAN(os_gui.get_os_label('purple', teacher),
                                _title=T('Karma teacher'))
        else:
            teacher_role = teacher

        # set label for teacher role 2
        if teacher_role2 == 1:  # sub
            teacher_role2 = SPAN(os_gui.get_os_label('blue', teacher2),
                                 _title=T("Sub teacher"))
        elif teacher_role2 == 2:  # assist
            teacher_role2 = SPAN(os_gui.get_os_label('yellow', teacher2),
                                 _title=T("Assistant"))
        elif teacher_role2 == 3:  # karma
            teacher_role2 = SPAN(os_gui.get_os_label('purple', teacher2),
                                 _title=T('Karma teacher'))
        else:
            teacher_role2 = teacher2

        return dict(teacher_role=teacher_role,
                    teacher_role2=teacher_role2)


    def _get_day_get_table_class_trend_data(self):
        """
            dict containing trend divs for self.date
        """
        def average(total, classes_counted):
            try:
                average = float(total / classes_counted)
            except ZeroDivisionError:
                average = float(0)

            return average

        DATE_FORMAT = current.DATE_FORMAT
        db = current.db
        T = current.T
        weekday = self.date.isoweekday()

        date_formatted = self.date.strftime(DATE_FORMAT)

        delta = datetime.timedelta(days=28)
        one_month_ago = self.date - delta
        two_months_ago = one_month_ago - delta

        fields = [
            db.classes.id,
            db.classes.Maxstudents,
            db.classes_schedule_count.Attendance4WeeksAgo,
            db.classes_schedule_count.NRClasses4WeeksAgo,
            db.classes_schedule_count.Attendance8WeeksAgo,
            db.classes_schedule_count.NRClasses8WeeksAgo
        ]

        query = """
            SELECT cla.id,
                   CASE WHEN cotc.Maxstudents IS NOT NULL
                        THEN cotc.Maxstudents
                        ELSE cla.Maxstudents
                        END AS Maxstudents, 
                   clatt_4w_ago.att_4w,
                   clatt_4w_nrclasses.att_4w_nrclasses,
                   clatt_8w_ago.att_8w,
                   clatt_8w_nrclasses.att_8w_nrclasses
            FROM classes cla
            LEFT JOIN
                ( SELECT id,
                         classes_id,
                         ClassDate,
                         Status,
                         Description,
                         school_locations_id,
                         school_classtypes_id,
                         Starttime,
                         Endtime,
                         auth_teacher_id,
                         teacher_role,
                         auth_teacher_id2,
                         teacher_role2,
                         Maxstudents,
                         MaxOnlinebooking
                  FROM classes_otc
                  WHERE ClassDate = '{class_date}' ) cotc
            ON cla.id = cotc.classes_id            
            LEFT JOIN
                    ( SELECT classes_id, COUNT(*) as att_4w
                      FROM classes_attendance
                      WHERE classes_attendance.Classdate <  '{class_date}' AND
                            classes_attendance.Classdate >= '{one_month_ago}'
                      GROUP BY classes_id
                    ) clatt_4w_ago
                    ON clatt_4w_ago.classes_id = cla.id
                LEFT JOIN
                    ( SELECT classes_id, COUNT(DISTINCT ClassDate) as att_4w_nrclasses
                      FROM classes_attendance
                      WHERE classes_attendance.Classdate <  '{class_date}' AND
                            classes_attendance.Classdate >= '{one_month_ago}'
                      GROUP BY classes_id
                    ) clatt_4w_nrclasses
                    ON clatt_4w_nrclasses.classes_id = cla.id
                LEFT JOIN
                    ( SELECT classes_id, COUNT(*) as att_8w
                      FROM classes_attendance
                      WHERE classes_attendance.Classdate <  '{one_month_ago}' AND
                            classes_attendance.Classdate >= '{two_months_ago}'
                      GROUP BY classes_id
                    ) clatt_8w_ago
                    ON clatt_8w_ago.classes_id = cla.id
                LEFT JOIN
                    ( SELECT classes_id, COUNT(DISTINCT ClassDate) as att_8w_nrclasses
                      FROM classes_attendance
                      WHERE classes_attendance.Classdate <  '{one_month_ago}' AND
                            classes_attendance.Classdate >= '{two_months_ago}'
                      GROUP BY classes_id
                    ) clatt_8w_nrclasses
                    ON clatt_8w_nrclasses.classes_id = cla.id
            WHERE cla.Week_day = '{week_day}' AND
                  cla.Startdate <= '{class_date}' AND
                  (cla.Enddate >= '{class_date}' OR cla.Enddate IS NULL)
            """.format(class_date=self.date,
                       week_day=weekday,
                       one_month_ago=one_month_ago,
                       two_months_ago=two_months_ago)

        rows = db.executesql(query, fields=fields)

        data = {}

        trend_medium = self.trend_medium
        trend_high = self.trend_high

        for row in rows:
            classes_4w = row.classes_schedule_count.NRClasses4WeeksAgo or 0
            attendance_4w = row.classes_schedule_count.Attendance4WeeksAgo or 0
            avg_4w_ago = average(attendance_4w, classes_4w)
            classes_8w = row.classes_schedule_count.NRClasses8WeeksAgo or 0
            attendance_8w = row.classes_schedule_count.Attendance8WeeksAgo or 0
            avg_8w_ago = average(attendance_8w, classes_8w)

            div = DIV()

            display_class = ''
            capacity = ''

            try:
                avg_att_4w_percentage = (avg_4w_ago / row.classes.Maxstudents) * 100
            except ZeroDivisionError:
                avg_att_4w_percentage = 0
            avg_att_4w_percentage_display = round(avg_att_4w_percentage, 2)

            class_trend_text_color = 'grey'
            if trend_medium:
                capacity = ' - ' + T('Capacity filled: ') + unicode(avg_att_4w_percentage_display) + '%'
                if avg_att_4w_percentage < trend_medium:
                    class_trend_text_color = 'text-red'
                else:
                    class_trend_text_color = 'text-yellow'
            if trend_high:
                capacity = ' - ' + T('Capacity filled: ') + unicode(avg_att_4w_percentage_display) + '%'
                if avg_att_4w_percentage >= trend_high:
                    class_trend_text_color = 'text-green'

            avg_4w_ago_display = DIV(SPAN(int(avg_4w_ago), '/', row.classes.Maxstudents),
                                     _title=T("Average attendance past 4 weeks") + ' ' + capacity,
                                     _class='os-trend_avg_4_weeks inline-block ' + class_trend_text_color)
            try:
                if avg_4w_ago >= avg_8w_ago:
                    # calculate percentual increase
                    increase = avg_4w_ago - avg_8w_ago
                    value = int(round(float(increase / avg_8w_ago) * 100))
                    value = unicode(value) + '%'
                    div = DIV(avg_4w_ago_display, ' ',
                              DIV(_class='os-trend_arrow_up'),
                              SPAN(value, _title=T('Increase during past 4 weeks, compared to 8 weeks ago')),
                              ' ',
                              SPAN(_class='icon user icon-user'))
                else:
                    # calculate percentual decrease
                    decrease = avg_8w_ago - avg_4w_ago
                    value = int(round(float(decrease / avg_8w_ago) * 100))
                    value = unicode(value) + '%'
                    div = DIV(avg_4w_ago_display, ' ',
                              DIV(_class='os-trend_arrow_down'),
                              SPAN(value, _title=T('Decrease during past 4 weeks, compared to 8 weeks ago')),
                              ' ',
                              SPAN(_class='icon user icon-user'))

            except ZeroDivisionError:
                div = ''

            data[row.classes.id] = div

        return data


    def _get_day_get_table_class_trend(self):
        """
            Generates a div that contains the trend for a class.
            Look at past 4 weeks and compare to the classes before it.
            Take cancelled classes & into account by not counting a class
            when it's date doesn't appear in classes_attendance
        """
        web2pytest = current.globalenv['web2pytest']
        request = current.request
        auth = current.auth
        T = current.T

        # get attendance data from cache or db

        # Don't cache when running tests
        if web2pytest.is_running_under_test(request, request.application):
            data = self._get_day_get_table_class_trend_data()
        else:
            twelve_hours = 12*60*60
            cache = current.cache
            DATE_FORMAT = current.DATE_FORMAT
            # A key that isn't cleared when schedule changes occur.
            cache_key = 'openstudio_classschedule_trend_get_day_table_' + \
                        self.date.strftime(DATE_FORMAT)

            data = cache.ram(cache_key , lambda: self._get_day_get_table_class_trend_data(), time_expire=twelve_hours)

        return data


    def _get_day_get_table_get_permissions(self):
        """
            :return: dict containing button permissions for a user
        """
        auth = current.auth
        permissions = {}

        if auth.has_membership(group_id='Admins') or \
           auth.has_permission('read', 'classes_attendance'):
            permissions['classes_attendance'] = True
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
           auth.has_permission('create', 'classes_otc'):
            permissions['classes_otc'] = True
        if auth.has_membership(group_id='Admins') or \
           auth.has_permission('update', 'classes'):
            permissions['classes'] = True
        if auth.has_membership(group_id='Admins') or \
           auth.has_permission('delete', 'classes'):
            permissions['classes_delete'] = True

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
        # check permissions to change this class
        if permissions.get('classes_otc', False):
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

        if row.classes_otc.Status == 'cancelled':
            class_messages.append(T('Cancelled'))

        if row.classes_otc.Status == 'open':
            class_messages.append(T('Open'))

        classes_otc_update_permission = auth.has_membership(group_id='Admins') or \
                                        auth.has_permission('update', 'classes_otc')
        if row.classes_otc.id and classes_otc_update_permission:
            _class = os_gui.get_icon('pencil') + ' grey'
            class_messages.append(
                A(SPAN(SPAN(_class=_class), ' ', T('Edited')),
                  _href=URL('class_edit_on_date',
                            vars={'clsID': clsID,
                                  'date': date_formatted})))

            if row.classes_otc.Description:
                class_messages.append(row.classes_otc.Description)

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
        if row.classes_otc.Status == 'cancelled' or row.school_holidays.id:
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

        delta = datetime.timedelta(days=28)
        one_month_ago = date - delta
        two_months_ago = one_month_ago - delta

        if self.sorting == 'location':
            orderby_sql = 'location_name, Starttime'
        elif self.sorting == 'starttime':
            orderby_sql = 'Starttime, location_name'

        fields = [
            db.classes.id,
            db.classes_otc.Status,
            db.classes_otc.Description,
            db.classes.school_locations_id,
            db.school_locations.Name,
            db.classes.school_classtypes_id,
            db.classes.school_levels_id,
            db.classes.Week_day,
            db.classes.Starttime,
            db.classes.Endtime,
            db.classes.Startdate,
            db.classes.Enddate,
            db.classes.Maxstudents,
            db.classes.MaxOnlineBooking,
            db.classes.MaxReservationsRecurring,
            db.classes.AllowAPI,
            db.classes.sys_organizations_id,
            db.classes_otc.id,
            db.classes_teachers.id,
            db.classes_teachers.auth_teacher_id,
            db.classes_teachers.teacher_role,
            db.classes_teachers.auth_teacher_id2,
            db.classes_teachers.teacher_role2,
            db.school_holidays.id,
            db.school_holidays.Description,
            db.classes_schedule_count.Attendance,
            db.classes_schedule_count.OnlineBooking,
            db.classes_schedule_count.Reservations
        ]

        where_filter = self._get_day_filter_query()

        query = """
        SELECT cla.id,
               CASE WHEN cotc.Status IS NOT NULL
                    THEN cotc.Status
                    ELSE 'normal'
                    END AS Status,
               cotc.Description,
               CASE WHEN cotc.school_locations_id IS NOT NULL
                    THEN cotc.school_locations_id
                    ELSE cla.school_locations_id
                    END AS school_locations_id,
               CASE WHEN cotc.school_locations_id IS NOT NULL
                    THEN slcotc.Name
                    ELSE sl.Name
                    END AS location_name,
               CASE WHEN cotc.school_classtypes_id IS NOT NULL
                    THEN cotc.school_classtypes_id
                    ELSE cla.school_classtypes_id
                    END AS school_classtypes_id,
               cla.school_levels_id,
               cla.Week_day,
               CASE WHEN cotc.Starttime IS NOT NULL
                    THEN cotc.Starttime
                    ELSE cla.Starttime
                    END AS Starttime,
               CASE WHEN cotc.Endtime IS NOT NULL
                    THEN cotc.Endtime
                    ELSE cla.Endtime
                    END AS Endtime,
               cla.Startdate,
               cla.Enddate,
               CASE WHEN cotc.Maxstudents IS NOT NULL
                    THEN cotc.Maxstudents
                    ELSE cla.Maxstudents
                    END AS Maxstudents, 
               CASE WHEN cotc.MaxOnlineBooking IS NOT NULL
                    THEN cotc.MaxOnlineBooking
                    ELSE cla.MaxOnlineBooking
                    END AS MaxOnlineBooking,
               cla.MaxReservationsRecurring,             
               cla.AllowAPI,
               cla.sys_organizations_id,
               cotc.id,
               clt.id,
               CASE WHEN cotc.auth_teacher_id IS NOT NULL
                    THEN cotc.auth_teacher_id
                    ELSE clt.auth_teacher_id
                    END AS auth_teacher_id,
               CASE WHEN cotc.auth_teacher_id IS NOT NULL
                    THEN cotc.teacher_role
                    ELSE clt.teacher_role
                    END AS teacher_role,
               CASE WHEN cotc.auth_teacher_id2 IS NOT NULL
                    THEN cotc.auth_teacher_id2
                    ELSE clt.auth_teacher_id2
                    END AS auth_teacher_id2,
               CASE WHEN cotc.auth_teacher_id2 IS NOT NULL
                    THEN cotc.teacher_role2
                    ELSE clt.teacher_role2
                    END AS teacher_role2,
               sho.id,
               sho.Description,
                /* Count attendance for this class */
               ( SELECT count(clatt.id) as count_att
                 FROM classes_attendance clatt
                 WHERE clatt.classes_id = cla.id AND
                       clatt.ClassDAte ='{class_date}' AND
                       clatt.BookingStatus != 'cancelled') AS count_attendance,
               /* Count of online bookings for this class */
               ( SELECT COUNT(clatt.id) as count_atto
                 FROM classes_attendance clatt
                 WHERE clatt.classes_id = cla.id AND
                       clatt.ClassDate = '{class_date}' AND
                       clatt.BookingStatus != 'cancelled' AND
                       clatt.online_booking = 'T'
                 GROUP BY clatt.classes_id ) as count_clatto,
               /* Count of enrollments (reservations) for this class */
               ( SELECT COUNT(clr.id) as count_clr
                 FROM classes_reservation clr
                 WHERE clr.classes_id = cla.id AND
                       (clr.Startdate <= '{class_date}' AND
                        (clr.Enddate >= '{class_date}' OR clr.Enddate IS NULL))
                 GROUP BY clr.classes_id ) as count_clr
        FROM classes cla
        LEFT JOIN
            ( SELECT id,
                     classes_id,
                     ClassDate,
                     Status,
                     Description,
                     school_locations_id,
                     school_classtypes_id,
                     Starttime,
                     Endtime,
                     auth_teacher_id,
                     teacher_role,
                     auth_teacher_id2,
                     teacher_role2,
                     Maxstudents,
                     MaxOnlinebooking
              FROM classes_otc
              WHERE ClassDate = '{class_date}' ) cotc
            ON cla.id = cotc.classes_id
        LEFT JOIN school_locations sl
            ON sl.id = cla.school_locations_id
        LEFT JOIN school_classtypes sct
            ON sct.id = cla.school_classtypes_id
		LEFT JOIN school_locations slcotc
			ON slcotc.id = cotc.school_locations_id
        LEFT JOIN
            ( SELECT id,
                     classes_id,
                     auth_teacher_id,
                     teacher_role,
                     auth_teacher_id2,
                     teacher_role2
              FROM classes_teachers
              WHERE Startdate <= '{class_date}' AND (
                    Enddate >= '{class_date}' OR Enddate IS NULL)
              ) clt
            ON clt.classes_id = cla.id
        LEFT JOIN
            ( SELECT sh.id, sh.Description, shl.school_locations_id
              FROM school_holidays sh
              LEFT JOIN
                school_holidays_locations shl
                ON shl.school_holidays_id = sh.id
              WHERE sh.Startdate <= '{class_date}' AND
                    sh.Enddate >= '{class_date}') sho
            ON sho.school_locations_id = cla.school_locations_id
        WHERE cla.Week_day = '{week_day}' AND
              cla.Startdate <= '{class_date}' AND
              (cla.Enddate >= '{class_date}' OR cla.Enddate IS NULL)
              {where_filter}
        ORDER BY {orderby_sql}
        """.format(class_date = date,
                   week_day = weekday,
                   orderby_sql = orderby_sql,
                   where_filter = where_filter,
                   one_month_ago = one_month_ago,
                   two_months_ago = two_months_ago)

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
                         TH(T('Trend'), _class='trend'),
                         TH(T('')),
                         _class='os-table_header'),
                      _class='os-schedule')

        rows = self.get_day_rows()

        if len(rows) == 0:
            div_classes=DIV()
        else:
            # Get trend column from cache
            trend_data = self._get_day_get_table_class_trend()
            get_trend_data = trend_data.get

            # avoiding some dots in the loop
            get_status = self._get_day_row_status
            get_teacher_roles = self._get_day_row_teacher_roles
            get_buttons = self._get_day_get_table_get_buttons
            get_reservations = self._get_day_get_table_get_reservations
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

                trend = get_trend_data(row.classes.id, '')
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
                    TD(max_string_length(repr_row.classes.school_locations_id, 15)),
                    TD(max_string_length(repr_row.classes.school_classtypes_id, 24)),
                    TD(SPAN(repr_row.classes.Starttime, ' - ', repr_row.classes.Endtime)),
                    TD(teacher if (not status == 'open' and
                                   not row.classes_teachers.auth_teacher_id is None) \
                               else msg_no_teacher),
                    TD(max_string_length(repr_row.classes.school_levels_id, 12)),
                    TD(api),
                    TD(trend),
                    TD(buttons),
                   _class='os-schedule_class')
                row_tools = TR(
                    TD(' '),
                    TD(class_messages, _colspan=3, _class='grey'),
                    TD(teacher2 if not status == 'open' else ''),
                    TD(),
                    TD(),
                    TD(DIV(reservations,
                           _class='os-schedule_links')),
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
            cache_key = 'openstudio_classschedule_get_day_table_' + \
                        self.date.strftime(DATE_FORMAT) + '_' + \
                        unicode(self.filter_id_school_classtype) + '_' + \
                        unicode(self.filter_id_school_location) + '_' + \
                        unicode(self.filter_id_teacher) + '_' + \
                        unicode(self.filter_id_school_level) + '_' + \
                        unicode(self.filter_id_status) + '_' + \
                        unicode(self.filter_public) + '_' + \
                        self.sorting + '_' + \
                        unicode(self.trend_medium) + '_' + \
                        unicode(self.trend_high)

            rows = cache.ram(cache_key , lambda: self._get_day_table(), time_expire=CACHE_LONG)

        return rows


    def get_day_list(self):
        """
            Format rows as list
        """
        os_gui = current.globalenv['os_gui']
        DATE_FORMAT = current.DATE_FORMAT
        T = current.T
        date_formatted = self.date.strftime(DATE_FORMAT)

        rows = self.get_day_rows()

        get_status = self._get_day_row_status

        classes = []
        for i, row in enumerate(rows):
            repr_row = list(rows[i:i+1].render())[0]

            # get status
            status_result = get_status(row)
            status = status_result['status']

            # get teachers
            teacher_id = row.classes_teachers.auth_teacher_id
            teacher_id2 = row.classes_teachers.auth_teacher_id2
            teacher = repr_row.classes_teachers.auth_teacher_id
            teacher2 = repr_row.classes_teachers.auth_teacher_id2
            teacher_role = row.classes_teachers.teacher_role
            teacher_role2 = row.classes_teachers.teacher_role2

            # check filter for teachers
            if self.filter_id_teacher:
                teacher_filter_id = int(self.filter_id_teacher)
                filter_check = (teacher_filter_id == teacher_id or
                                teacher_filter_id == teacher_id2)
                if not filter_check:
                    # break loop if it's not the teacher searched for
                    continue

            # set holidays
            holiday = False
            holiday_description = ''
            if row.school_holidays.id:
                holiday = True
                holiday_description = row.school_holidays.Description

            cancelled = False
            cancelled_description = ''
            if status == 'cancelled':
                cancelled = True
                cancelled_description = row.classes_otc.Description

            subteacher = False
            if ( row.classes_teachers.teacher_role == 1 or
                 row.classes_teachers.teacher_role2 == 1 ):
                subteacher = True

            # shop url
            shop_url = URL('shop', 'classes_book_options', vars={'clsID': row.classes.id,
                                                                 'date' : date_formatted},
                           scheme=True,
                           host=True,
                           extension='')

            # populate class data
            data = dict()
            data['ClassesID'] = row.classes.id
            data['LocationID'] = row.classes.school_locations_id
            data['Location'] = repr_row.classes.school_locations_id
            data['Starttime'] = repr_row.classes.Starttime
            data['time_starttime'] = row.classes.Starttime
            data['Endtime'] = repr_row.classes.Endtime
            data['time_endtime'] = row.classes.Endtime
            data['ClassTypeID'] = row.classes.school_classtypes_id
            data['ClassType'] = repr_row.classes.school_classtypes_id
            data['TeacherID'] = teacher_id
            data['TeacherID2'] = teacher_id2
            data['Teacher'] = teacher
            data['Teacher2'] = teacher2
            data['LevelID'] = row.classes.school_levels_id
            data['Level'] = repr_row.classes.school_levels_id
            data['Subteacher'] = subteacher
            data['Cancelled'] = cancelled
            data['CancelledDescription'] = cancelled_description
            data['Holiday'] = holiday
            data['HolidayDescription'] = holiday_description
            data['MaxStudents'] = row.classes.Maxstudents or 0 # Spaces for a class
            data['CountAttendance'] = row.classes_schedule_count.Attendance or 0
            data['CountAttendanceOnlineBooking'] = row.classes_schedule_count.OnlineBooking or 0
            data['BookingSpacesAvailable'] = self._get_day_list_booking_spaces(row)
            data['BookingStatus'] = self._get_day_list_booking_status(row)
            data['BookingOpen'] = self.bookings_open
            data['LinkShop'] = shop_url

            classes.append(data)

        return classes
