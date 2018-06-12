# -*- coding: utf-8 -*-

from gluon import *

class StaffSchedule:
    def __init__(self, date,
                       filter_id_school_shifts = None,
                       filter_id_school_locations = None,
                       filter_id_employee = None,
                       filter_id_status = None,
                       sorting = 'starttime'):
        self.date = date

        self.filter_id_school_shifts = filter_id_school_shifts
        self.filter_id_school_locations = filter_id_school_locations
        self.filter_id_employee = filter_id_employee
        self.filter_id_status = filter_id_status
        self.sorting = sorting


    def _get_day_filter_query(self):
        """
            Returns the filter query for the schedule
        """
        where = ''
        if self.filter_id_school_shifts:
            where += 'AND sh.school_shifts_id = '
            where += unicode(self.filter_id_school_shifts) + ' '

        if self.filter_id_school_locations:
            where += 'AND sh.school_locations_id = '
            where += unicode(self.filter_id_school_locations) + ' '

        return where


    def _get_day_row_status(self, row):
        """
            Return status for row
        """
        status = 'normal'
        status_marker = DIV(_class='status_marker bg_green')
        if row.shifts_otc.Status == 'cancelled':
            status = 'cancelled'
            status_marker = DIV(_class='status_marker bg_orange')
        elif row.shifts_otc.Status == 'open':
            status = 'open'
            status_marker = DIV(_class='status_marker bg_red')
        elif not row.shifts_otc.auth_employee_id == None:
            status = 'sub'
            status_marker = DIV(_class='status_marker bg_blue')

        return dict(status=status, marker=status_marker)


    def _get_day_row_staff(self, row, repr_row, status):
        """
            Return employees for a row
        """
        if status == 'sub':
            print row
            print '---'
            print repr_row

            employee_id  = row.shifts_otc.auth_employee_id
            employee_id2 = row.shifts_otc.auth_employee_id2
            employee     = repr_row.shifts_otc.auth_employee_id
            employee2    = repr_row.shifts_otc.auth_employee_id2
        else:
            employee_id  = row.shifts_staff.auth_employee_id
            employee_id2 = row.shifts_staff.auth_employee_id2
            employee     = repr_row.shifts_staff.auth_employee_id
            employee2    = repr_row.shifts_staff.auth_employee_id2

        return dict(employee_id  = employee_id,
                    employee_id2 = employee_id2,
                    employee     = employee,
                    employee2    = employee2)


    def _get_day_table_buttons(self, shID):
        """
            Returns edit & delete buttons for schedule
        """
        auth = current.auth
        os_gui = current.globalenv['os_gui']
        T = current.T
        DATE_FORMAT = current.DATE_FORMAT
        date_formatted = self.date.strftime(DATE_FORMAT)

        buttons = DIV(_class='pull-right')

        vars = { 'shID' : shID, 'date' : date_formatted }


        if auth.has_membership(group_id='Admins') or \
           auth.has_permission('delete', 'shifts'):

            onclick_remove = "return confirm('" + \
                             T('Do you really want to delete this shift?') + \
                             "');"
            remove = os_gui.get_button('delete_notext',
                       URL('shift_delete', vars=vars),
                       onclick=onclick_remove,
                       _class='pull-right')

            buttons.append(remove)

        edit_menu = ''
        links = [['header', T('Shift on') + ' ' + date_formatted]]

        # check permissions to change this class
        if auth.has_membership(group_id='Admins') or \
                auth.has_permission('create', 'shifts_otc'):
            links.append(A(os_gui.get_fa_icon('fa-pencil'),
                           T('Edit'),
                           _href=URL('shift_edit_on_date', vars=vars)))
        # Check permission to update weekly class
        if auth.has_membership(group_id='Admins') or \
                auth.has_permission('update', 'shifts'):
            links.append('divider')
            links.append(['header', T('All shifts in series')])

            # Add edit link
            links.append(A(os_gui.get_fa_icon('fa-pencil'),
                           T('Edit'), ' ',
                           _href=URL('shift_edit', vars=vars)))

            # Add staff link
            if auth.has_membership(group_id='Admind') or \
               auth.has_permission('read', 'shifts_staff'):
                links.append(A(os_gui.get_fa_icon('fa-user'),
                               T('Staff'), ' ',
                               _href=URL('shift_staff', vars=vars)))

            edit_menu = os_gui.get_dropdown_menu(
                links,
                btn_text = '',
                btn_size = 'btn-sm',
                btn_icon = 'pencil',
                menu_class = 'btn-group pull-right'
            )

            buttons.append(edit_menu)

        return buttons


    def get_day_rows(self):
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
            orderby_sql = 'sl.Name, sh.Starttime'
        elif self.sorting == 'starttime':
            orderby_sql = 'sh.Starttime, sl.Name'

        fields = [
            db.shifts.id,
            db.shifts_otc.Status,
            db.shifts_otc.Description,
            db.shifts.school_locations_id,
            db.shifts.school_shifts_id,
            db.shifts.Week_day,
            db.shifts.Starttime,
            db.shifts.Endtime,
            db.shifts.Startdate,
            db.shifts.Enddate,
            db.shifts_otc.id,
            db.shifts_otc.auth_employee_id,
            db.shifts_otc.auth_employee_id2,
            db.shifts_staff.id,
            db.shifts_staff.auth_employee_id,
            db.shifts_staff.auth_employee_id2,
        ]

        where_filter = self._get_day_filter_query()

        query = '''
        SELECT sh.id,
               CASE WHEN sotc.Status IS NOT NULL
                    THEN sotc.Status
                    ELSE 'normal'
                    END AS Status,
               sotc.Description,
               CASE WHEN sotc.school_locations_id IS NOT NULL
                    THEN sotc.school_locations_id
                    ELSE sh.school_locations_id
                    END AS school_locations_id,
               CASE WHEN sotc.school_shifts_id IS NOT NULL
                    THEN sotc.school_shifts_id
                    ELSE sh.school_shifts_id
                    END AS school_shifts_id,
               sh.Week_day,
               CASE WHEN sotc.Starttime IS NOT NULL
                    THEN sotc.Starttime
                    ELSE sh.Starttime
                    END AS Starttime,
               CASE WHEN sotc.Endtime IS NOT NULL
                    THEN sotc.Endtime
                    ELSE sh.Endtime
                    END AS Endtime,
               sh.Startdate,
               sh.Enddate,
               sotc.id,
               sotc.auth_employee_id,
               sotc.auth_employee_id2,
               shs.id,
               shs.auth_employee_id,
               shs.auth_employee_id2
        FROM shifts sh
        LEFT JOIN school_locations sl
            ON sl.id = sh.school_locations_id
        LEFT JOIN
            ( SELECT id,
                     shifts_id,
                     ShiftDate,
                     Status,
                     Description,
                     school_locations_id,
                     school_shifts_id,
                     Starttime,
                     Endtime,
                     auth_employee_id,
                     auth_employee_id2
              FROM shifts_otc
              WHERE ShiftDate = '{shift_date}' ) sotc
            ON sh.id = sotc.shifts_id
        LEFT JOIN
            ( SELECT id,
                     shifts_id,
                     auth_employee_id,
                     auth_employee_id2
              FROM shifts_staff
              WHERE Startdate <= '{shift_date}' AND (
                    Enddate >= '{shift_date}' OR Enddate IS NULL)
              ) shs
            ON sh.id = shs.shifts_id
        WHERE sh.Week_day = '{week_day}' AND
              sh.Startdate <= '{shift_date}' AND
              (sh.Enddate >= '{shift_date}' OR sh.Enddate IS NULL)
              {where_filter}
        ORDER BY {orderby_sql}
        '''.format(shift_date = date,
                   week_day = weekday,
                   orderby_sql = orderby_sql,
                   where_filter = where_filter)

        rows = db.executesql(query, fields=fields)

        return rows


    def get_day_table(self):
        """
            Calls the schedule_get_day_rows function and formats the rows
            in a desktop friendly table
        """
        from general_helpers import max_string_length
        from general_helpers import NRtoDay


        DATE_FORMAT = current.DATE_FORMAT
        T = current.T
        auth = current.auth

        rows = self.get_day_rows()

        if len(rows) == 0:
            table = DIV()
        else:
            table = TABLE(TR(TH(' ', _class='td_status_marker'), # status marker
                             TH(T('Location'), _class='location'),
                             TH(T('Shift'), _class='classtype'),
                             TH(T('Time'), _class='time'),
                             TH(T('Employee'), _class='teacher'),
                             TH(T('')),
                             _class='os-table_header'),
                          _class='os-schedule')
            # Generate list of classes
            for i, row in enumerate(rows):
                print '###########'
                print unicode(i)


                repr_row = list(rows[i:i+1].render())[0]
                shID = row.shifts.id

                get_status = self._get_day_row_status(row)
                status = get_status['status']
                status_marker = get_status['marker']

                print status

                # filter status
                if self.filter_id_status:
                    if status != self.filter_id_status:
                        continue

                result = self._get_day_row_staff(row, repr_row, status)

                print result

                employee_id  = result['employee_id']
                employee_id2 = result['employee_id2']
                employee     = result['employee']
                employee2    = result['employee2'] or ''

                # check filter for employees
                if self.filter_id_employee:
                    self.filter_id_employee = int(self.filter_id_employee)
                    filter_check = (self.filter_id_employee == employee_id or
                                    self.filter_id_employee == employee_id2)
                    if not filter_check:
                        # break loop if it's not the employee searched for
                        continue

                location = max_string_length(
                    repr_row.shifts.school_locations_id, 15)
                shift_type = max_string_length(
                    repr_row.shifts.school_shifts_id, 24)
                time = SPAN(repr_row.shifts.Starttime, ' - ',
                            repr_row.shifts.Endtime)

                buttons = self._get_day_table_buttons(shID)

                row_class = TR(TD(status_marker),
                               TD(location),
                               TD(shift_type),
                               TD(time),
                               TD(employee),
                               TD(buttons),
                               _class='os-schedule_class')
                row_tools = TR(TD(' '),
                               TD(_colspan=3),
                               TD(employee2, _class='grey'),
                               TD(),
                               _class='os-schedule_links',
                               _id='class_' + unicode(shID))

                table.append(row_class)
                table.append(row_tools)

        return dict(table=table,
                    weekday=NRtoDay(self.date.isoweekday()),
                    date=self.date.strftime(DATE_FORMAT))


    def get_day_list(self, show_id = False):
        """
            Format rows as list
        """
        os_gui = current.globalenv['os_gui']
        DATE_FORMAT = current.DATE_FORMAT
        T = current.T
        date_formatted = self.date.strftime(DATE_FORMAT)

        rows = self.get_day_rows()

        shifts = []
        for i, row in enumerate(rows):
            repr_row = list(rows[i:i+1].render())[0]

            # get status
            status_result = self._get_day_row_status(row)
            status = status_result['status']

            # get employees
            result = self._get_day_row_staff(row, repr_row, status)
            employee_id  = result['employee_id']
            employee_id2 = result['employee_id2']
            employee     = result['employee']
            employee2    = result['employee2']

            # check filter for employees
            if self.filter_id_employee:
                self.filter_id_employee = int(self.filter_id_employee)
                filter_check = (self.filter_id_employee == employee_id or
                                self.filter_id_employee == employee_id2)
                if not filter_check:
                    # break loop if it's not the employee searched for
                    continue


            # get cancelled
            cancelled = False
            if status == 'cancelled':
                cancelled = True

            # get sub
            sub = False
            if status == 'sub':
                subteacher = True

            # populate class data
            data = dict()
            if show_id:
                data['id'] = row.shifts.id
            data['LocationID'] = row.shifts.school_locations_id
            data['Location'] = repr_row.shifts.school_locations_id
            data['Starttime'] = repr_row.shifts.Starttime
            data['Endtime'] = repr_row.shifts.Endtime
            data['ShiftID'] = row.shifts.school_shifts_id
            data['Shift'] = repr_row.shifts.school_shifts_id
            data['EmployeeID'] = employee_id
            data['EmployeeID2'] = employee_id2
            data['Employee'] = employee
            data['Employee2'] = employee2
            data['Sub'] = sub
            data['Cancelled'] = cancelled

            shifts.append(data)

        return shifts
