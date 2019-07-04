# -*- coding: utf-8 -*-

import datetime

from gluon import *



class AttendanceHelper:
    """
        This class collects common function for attendance in OpenStudio
    """
    def get_attendance_rows(self, clsID, date):
        """
            :param clsID: db.classes.db
            :param date: class date
            :return: attendance rows
        """
        db = current.db

        filter_date_teacher_notes = date - datetime.timedelta(days=92)

        fields = [
            db.auth_user.id,
            db.auth_user.trashed,
            db.auth_user.birthday,
            db.auth_user.thumbsmall,
            db.auth_user.first_name,
            db.auth_user.last_name,
            db.auth_user.display_name,
            db.auth_user.email,
            db.customers_subscriptions.id,
            db.school_subscriptions.Name,
            db.customers_classcards.id,
            db.school_classcards.Name,
            db.classes_reservation.id,
            db.classes_reservation.ResType,
            db.classes_reservation.Startdate,
            db.classes_reservation.Enddate,
            db.invoices.id,
            db.invoices.InvoiceID,
            db.invoices.Status,
            db.invoices.payment_methods_id,
            db.classes_attendance.id,
            db.classes_attendance.AttendanceType,
            db.classes_attendance.online_booking,
            db.classes_attendance.BookingStatus,
            db.classes_attendance.CreatedOn,
            db.auth_user.teacher_notes_count,  # Holds count of recent teacher notes
            db.auth_user.teacher_notes_count_injuries
        ]

        query = """
            SELECT au.id,
                   au.trashed,
                   au.birthday,
                   au.thumbsmall,
                   au.first_name,
                   au.last_name,
                   au.display_name,
                   au.email, 
                   cs.id,
                   ssu.Name,
                   cc.id,
                   scc.Name,
                   clr.id,
                   clr.restype,
                   clr.Startdate,
                   clr.Enddate,
                   inv.id,
                   inv.InvoiceID,
                   inv.Status,
                   inv.payment_methods_id,
                   clatt.id,
                   clatt.AttendanceType,
                   clatt.online_booking,
                   clatt.BookingStatus,
                   clatt.CreatedOn,
                   ( SELECT COUNT(*) FROM customers_notes cn 
                     WHERE cn.TeacherNote = 'T' AND 
                           cn.auth_customer_id = au.id AND
                           cn.NoteDate >= '{filter_date_teacher_notes}' ),
                   ( SELECT COUNT(*) FROM customers_notes cn 
                     WHERE cn.TeacherNote = 'T' AND 
                           cn.auth_customer_id = au.id AND
                           cn.Injury = 'T' )
            FROM auth_user au
            LEFT JOIN
                ( SELECT id,
                         auth_customer_id,
                         AttendanceType,
                         online_booking,
                         BookingStatus,
                         customers_classcards_id,
                         customers_subscriptions_id,
                         CreatedOn
                  FROM classes_attendance
                  WHERE ClassDate = '{date}' AND classes_id = {clsID} ) clatt
                ON clatt.auth_customer_id = au.id
            LEFT JOIN customers_classcards cc ON clatt.customers_classcards_id = cc.id
            LEFT JOIN school_classcards scc ON cc.school_classcards_id = scc.id
            LEFT JOIN customers_subscriptions cs ON clatt.customers_subscriptions_id = cs.id
            LEFT JOIN school_subscriptions ssu ON cs.school_subscriptions_id = ssu.id
            LEFT JOIN
                ( SELECT id,
                         auth_customer_id,
                         classes_id,
                         Startdate,
                         Enddate,
                         ResType,
                         TrialClass
                  FROM classes_reservation
                  WHERE classes_id = {clsID} AND
                        Startdate <= '{date}' AND
                        (Enddate >= '{date}' or Enddate IS NULL)) clr
                ON clr.auth_customer_id = au.id
            LEFT JOIN
                invoices_items_classes_attendance iica
                ON iica.classes_attendance_id = clatt.id
            LEFT JOIN 
                invoices_items ii
                ON ii.id = iica.invoices_items_id
            LEFT JOIN
                invoices inv ON ii.invoices_id = inv.id
            WHERE clatt.id IS NOT NULL
            ORDER BY au.display_name
        """.format(date  = date,
                   filter_date_teacher_notes = filter_date_teacher_notes,
                   clsID = clsID)

        rows = db.executesql(query, fields=fields)

        return rows


    def get_attendance_rows_past_days(self, clsID, date, days):
        """
            :param clsID: db.classes.id 
            :param date: datetime.date
            :param days: int
            :return: 
        """
        from os_class import Class

        db = current.db
        cache = current.cache

        cls = Class(clsID, date)

        delta = datetime.timedelta(days=days)
        x_days_ago = date - delta

        left = [ db.classes.on(db.classes_attendance.classes_id ==
                               db.classes.id),
                 db.auth_user.on(db.classes_attendance.auth_customer_id ==
                                 db.auth_user.id) ]

        query = (db.classes.school_classtypes_id == cls.cls.school_classtypes_id) & \
                (db.classes.school_locations_id == cls.cls.school_locations_id) & \
                (db.classes_attendance.classes_id == clsID) & \
                (db.classes_attendance.ClassDate <= date) & \
                (db.classes_attendance.ClassDate >= x_days_ago) & \
                (db.auth_user.trashed == False) & \
                (db.auth_user.customer == True)


        rows = db(query).select(db.auth_user.id,
                                db.auth_user.trashed,
                                db.auth_user.birthday,
                                db.auth_user.thumbsmall,
                                db.auth_user.first_name,
                                db.auth_user.last_name,
                                db.auth_user.display_name,
                                db.auth_user.email,
                                db.classes.school_classtypes_id,
                                left=left,
                                orderby=db.auth_user.display_name,
                                distinct=True,
                                cache=(cache.ram, 30))

        return rows


    def get_reservation_rows(self, clsID, date):
        """
            :param clsID: db.classes.id 
            :param date: datetime.date
            :return: reservation rows for a class
        """
        db = current.db

        fields = [
            db.auth_user.id,
            db.auth_user.trashed,
            db.auth_user.birthday,
            db.auth_user.thumbsmall,
            db.auth_user.first_name,
            db.auth_user.last_name,
            db.auth_user.display_name,
            db.auth_user.email,
            db.classes_reservation.id,
            db.classes_reservation.ResType,
            db.classes_reservation.Startdate,
            db.classes_reservation.Enddate,
        ]

        query = """
            SELECT au.id,
                   au.trashed,
                   au.birthday,
                   au.thumbsmall,
                   au.first_name,
                   au.last_name,
                   au.display_name,
                   au.email,
                   clr.id,
                   clr.restype,
                   clr.Startdate,
                   clr.Enddate
            FROM auth_user au
            LEFT JOIN
                ( SELECT id,
                         auth_customer_id
                  FROM classes_attendance
                  WHERE ClassDate = '{date}' AND classes_id = {clsID} ) clatt
                ON clatt.auth_customer_id = au.id
            LEFT JOIN
                ( SELECT id,
                         auth_customer_id,
                         classes_id,
                         Startdate,
                         Enddate,
                         ResType,
                         TrialClass
                  FROM classes_reservation
                  WHERE Startdate <= '{date}' AND
                        (Enddate >= '{date}' or Enddate IS NULL)) clr
                ON clr.auth_customer_id = au.id
            WHERE clr.classes_id = '{clsID}'
            ORDER BY clr.TrialClass DESC, au.display_name
        """.format(date  = date,
                   clsID = clsID)

        rows = db.executesql(query, fields=fields)

        return rows


    def get_attending_list_between(self,
                                   start_date,
                                   end_date):
        """
            Returns distincs a list of customers attending any classes between start_date
            and end_date as a list of db.auth_user_id
        """
        db = current.db

        left = [ db.auth_user.on(db.classes_attendance.auth_customer_id == db.auth_user.id) ]

        query = (db.classes_attendance.ClassDate >= start_date) & \
                (db.classes_attendance.ClassDate <= end_date) & \
                ((db.classes_attendance.AttendanceType == None) |
                 (db.classes_attendance.AttendanceType == 3))

        rows = db(query).select(db.classes_attendance.auth_customer_id,
                                distinct=True,
                                left=left,
                                orderby=db.auth_user.display_name)

        attending = []
        for row in rows:
            attending.append(row.auth_customer_id)

        return attending


    def get_last_attendance(self, customer_ids):
        """
            For each customer id returns the date when the customer last attended
            a class. Returns a dictionary where the key is the customer id and the
            value is the last date when the customer attended a class.

            :param customer_ids: the customers to check
        """
        db = current.db
        max = db.classes_attendance.ClassDate.max()
        having_query = (db.classes_attendance.auth_customer_id.belongs(customer_ids))
        rows = db().select(db.classes_attendance.auth_customer_id,
            max,
            groupby=db.classes_attendance.auth_customer_id,
            having=having_query)

        last_dates = {}
        for row in rows:
            last_dates[row.classes_attendance.auth_customer_id] = row[max]

        return last_dates


    def get_checkin_list_customers_booked(self,
                                          clsID,
                                          date,
                                          class_full=False,
                                          pictures=True,
                                          reservations=True,
                                          invoices=True,
                                          show_notes=True,
                                          show_booking_time=True,
                                          show_subscriptions=True,
                                          manage_checkin=True):
        """
            :param clsID: db.classes.id
            :param date: Class date
            :return: Table of customers checked in for this class
        """
        def add_table_row(row,
                          repr_row,
                          pictures=pictures,
                          reservations=reservations,
                          show_subscriptions=show_subscriptions,
                          invoices=invoices,
                          show_notes=show_notes,
                          show_booking_time=show_booking_time,
                          ):
            """'
                Adds a row to the table
            """
            cuID = row.auth_user.id

            customer = Customer(cuID)
            subscr_cards = ''
            if show_subscriptions:
                subscr_cards = customer.get_subscriptions_and_classcards_formatted(
                    date,
                    new_cards=False,
                    show_subscriptions=show_subscriptions,
                    )

            # check attendance
            if row.classes_attendance.BookingStatus == 'attending':
                links = []
                # Check update permission
                if (auth.has_membership(group_id='Admins') or
                    auth.has_permission('update', 'classes_attendance')):
                    links = [['header', T('Booking status')]]
                    links.append(A(os_gui.get_fa_icon('fa-check-circle-o'),
                                   T('Booked'), ' ',
                                   _href=URL('classes', 'attendance_set_status',
                                             vars={'clattID':row.classes_attendance.id,
                                                   'status':'booked'}),
                                   _class="text-blue"))
                    links.append(A(os_gui.get_fa_icon('fa-ban'),
                                   T('Cancelled'), ' ',
                                   _href=URL('classes', 'attendance_set_status',
                                             vars={'clattID':row.classes_attendance.id,
                                                   'status':'cancelled'}),
                                   _class="text-yellow"))

                # Check delete permission
                if (auth.has_membership(group_id='Admins') or
                    auth.has_permission('delete', 'classes_attendance')):
                    delete_onclick = "return confirm('" + \
                              T('Do you really want to remove this booking?') + "');"

                    links.append('divider')
                    links.append(A(os_gui.get_fa_icon('fa-minus-circle'),
                                   T('Remove'), ' ',
                                   _href=URL('classes', 'attendance_remove', vars={'clattID':row.classes_attendance.id}),
                                   _onclick=delete_onclick,
                                   _class="text-red"))

                btn = os_gui.get_dropdown_menu(
                    links=links,
                    btn_text=T('Actions'),
                    btn_size='btn-sm',
                    btn_icon='actions',
                    menu_class='btn-group pull-right')

                # btn = DIV(_class='btn-group pull-right')
                attending = SPAN(_class='glyphicon glyphicon-ok green very_big_check')


            else:
                attending = SPAN(_class='glyphicon glyphicon-ok grey-light very_big_check')
                btn = ''
                # Check update permission
                if (auth.has_membership(group_id='Admins') or
                    auth.has_permission('update', 'classes_attendance')):

                    checkin = ''
                    if not class_full:
                        checkin = os_gui.get_button('noicon',
                                                    URL('classes', 'attendance_set_status',
                                                        vars={'clattID':row.classes_attendance.id,
                                                              'status':'attending'}),
                                                    title=T('Check in'))

                    links = [['header', T('Booking status')]]
                    links.append(A(os_gui.get_fa_icon('fa-ban'),
                                   T('Cancelled'), ' ',
                                   _href=URL('classes', 'attendance_set_status',
                                             vars={'clattID':row.classes_attendance.id,
                                                   'status':'cancelled'}),
                                   _class="text-yellow"))

                # Check delete permission
                if (auth.has_membership(group_id='Admins') or
                        auth.has_permission('delete', 'classes_attendance')):
                    delete_onclick = "return confirm('" + \
                                     T('Do you really want to remove this booking?') + "');"

                    links.append('divider')
                    links.append(A(os_gui.get_fa_icon('fa-minus-circle'),
                                   T('Remove'), ' ',
                                   _href=URL('classes', 'attendance_remove',
                                             vars={'clattID': row.classes_attendance.id}),
                                   _onclick=delete_onclick,
                                   _class="text-red"))

                dropdown = os_gui.get_dropdown_menu(
                    links=links,
                    btn_text='',
                    btn_size='btn-sm',
                    btn_icon='actions',
                    menu_class='btn-group pull-right')


                if not manage_checkin:
                    # Remove additional options on check-in button for self checkin
                    btn = DIV(checkin, _class='pull-right')
                else:
                    btn = DIV(checkin, dropdown, _class='btn-group pull-right')

            # Customer picture
            td_pic = ''
            if pictures:
                td_pic = TD(repr_row.auth_user.thumbsmall,
                            _class='os-customer_image_td hidden-xs')


            td_labels = TD(repr_row.classes_attendance.BookingStatus, _class='hidden-xs')
            if reservations and row.classes_reservation.id:
                date_formatted = date.strftime(DATE_FORMAT)
                crID = row.classes_reservation.id

                td_labels.append(SPAN(' ', repr_row.classes_reservation.ResType))

                try:
                    if row.classes_attendance.AttendanceType == 1:
                        td_labels.append(' ')
                        td_labels.append(os_gui.get_label('success', T('Trial class')))

                    elif row.classes_attendance.AttendanceType == 2:
                        td_labels.append(' ')
                        td_labels.append(os_gui.get_label('primary', T('Drop in')))
                except AttributeError:
                    pass

            # Add a small label for online bookings
            try:
                if row.classes_attendance.online_booking:
                    td_labels.append(' ')
                    td_labels.append(os_gui.get_label('info', T('Online')))
            except AttributeError:
                pass

            if row.classes_attendance.AttendanceType == 4:
                td_labels.append(' ')
                td_labels.append(os_gui.get_label('default', T('Complementary')))

            if row.classes_attendance.AttendanceType == 5:
                td_labels.append(' ')
                td_labels.append(os_gui.get_label('warning', T("Review")))

            if row.classes_attendance.AttendanceType == 6:
                td_labels.append(' ')
                td_labels.append(os_gui.get_label('warning', T('Reconcile later')))

            if show_booking_time:
                td_labels.append(BR())
                td_labels.append(SPAN(T('Booked on'), ' ', repr_row.classes_attendance.CreatedOn,
                                      _class='vsmall_font grey'))




            ##
            # Invoice for drop in or trial class
            ##
            td_inv = ''
            if invoices:
                invoices = Invoices()
                if row.invoices.id:
                    invoice = invoices.represent_invoice_for_list(
                        row.invoices.id,
                        repr_row.invoices.InvoiceID,
                        repr_row.invoices.Status,
                        row.invoices.Status,
                        row.invoices.payment_methods_id
                    )
                else:
                    invoice = ''

                td_inv = TD(invoice)

            ##
            # Link to notes page
            ##
            link_notes = ''
            if show_notes:
                notes_text = T('notes')
                if row.auth_user.teacher_notes_count == 1:
                    notes_text = T('note')
                notes_link_text = SPAN(row.auth_user.teacher_notes_count, ' ', T('Recent'), ' ', notes_text)

                count_injuries = row.auth_user.teacher_notes_count_injuries
                if count_injuries > 0:
                    injuries_text = T('Injuries')
                    if count_injuries == 1:
                        injuries_text = T('Injury')
                    notes_link_text.append(BR())
                    notes_link_text.append(SPAN(count_injuries, ' ', injuries_text, _class='smaller_font text-red bold'))

                link_notes = SPAN(A(notes_link_text,
                                    _href=URL('classes', 'attendance_teacher_notes',
                                              vars={'cuID':row.auth_user.id,
                                                    'clsID':clsID,
                                                    'date':date.strftime(DATE_FORMAT)})))

            # TD('notes', row.auth_user.eetra_field_intxtra_field_int),

            tr = TR(TD(attending, _class='very_big_check'),
                    td_pic,
                    TD(SPAN(row.auth_user.display_name, _class='bold'), BR(),
                       subscr_cards),
                    td_labels,
                    td_inv,
                    TD(link_notes),
                    btn)

            table.append(tr)

        ##
        # Start main function
        ##
        from os_customer import Customer
        from os_invoices import Invoices

        T = current.T
        db = current.db
        auth = current.auth
        os_gui = current.globalenv['os_gui']
        DATE_FORMAT = current.DATE_FORMAT

        modals = DIV()

        cls = db.classes(clsID)

        header = THEAD(TR(TH(),
                          TH(),
                          TH(T('Customer')),
                          TH(T('Status')), # Booking Status [and Enrollment]
                          TH(),
                          TH(),
                          TH()))

        rows = self.get_attendance_rows(clsID, date)
        table = TABLE(header, _class='table table-striped table-hover')

        for i, row in enumerate(rows):
            #print row
            repr_row = list(rows[i:i+1].render())[0]
            add_table_row(row,
                          repr_row,
                          reservations=reservations,
                          show_subscriptions=show_subscriptions,
                          invoices=invoices,
                          show_notes=show_notes,
                          show_booking_time=show_booking_time)

        return table


    def get_checkin_list_customers(self,
                                   clsID,
                                   date,
                                   pictures=False,
                                   manual_enabled=False,
                                   this_class=False,
                                   reservations=False,
                                   reservations_cancel=False,
                                   subscriptions=True,
                                   invoices=False,
                                   show_notes=False,
                                   class_full=False):
        """
            Returns a list of customers who have a reservation or have attended
            a class of this type in the past month

            this_class
            True: look for attendance for this class in the past month
            False: look for attendance for this classtype in the past month
        """
        def add_table_row(row,
                          repr_row,
                          reservations=False,
                          invoices=False,
                          show_notes=False,
                          modals=None):
            """'
                Adds a row to the table
            """
            cuID = row.auth_user.id

            customer = Customer(cuID)
            subscr_cards = customer.get_subscriptions_and_classcards_formatted(
                date,
                new_cards=False,
                show_subscriptions=subscriptions,
                )

            # check attendance
            if cuID in attendance_list:
                btn = DIV(_class='btn-group pull-right')
                attending = SPAN(_class='glyphicon glyphicon-ok green very_big_check')
                date_formatted = date.strftime(DATE_FORMAT)

                notes = ''
                notes_perm = auth.has_membership(group_id='Admins') or \
                             auth.has_permission('read', 'customers_notes_teachers')
                if show_notes and notes_perm:
                    result = self._get_teachers_note_modal(customer.row.id,
                                                           customer.row.display_name,
                                                           modals)
                    modals = result['modals_div']
                    btn.append(result['button'])

                onclick = "return confirm('" + \
                          T('Really check out?') + "');"
                remove = os_gui.get_button('delete_notext',
                                           URL('classes', 'attendance_remove',
                                               vars={'clsID': clsID,
                                                     'cuID': cuID,
                                                     'date': date_formatted}),
                                           title=T('Cancel'),
                                           btn_class='btn-danger',
                                           btn_size='',
                                           onclick=onclick)
                btn.append(remove)


            else:
                attending = SPAN(_class='glyphicon glyphicon-ok grey-light very_big_check')
                if not class_full:
                    btn = self.get_signin_buttons(clsID,
                                                  date,
                                                  cuID,
                                                  manual_enabled=manual_enabled)
                else:
                    btn = ''

            # Customer picture
            td_pic = ''
            if pictures:
                td_pic = TD(repr_row.auth_user.thumbsmall,
                            _class='os-customer_image_td hidden-xs')

            td_res = ''
            if reservations and row.classes_reservation.id:
                date_formatted = date.strftime(DATE_FORMAT)
                crID = row.classes_reservation.id

                td_res = TD(repr_row.classes_reservation.ResType, _class='hidden-xs')

            td_atttype = ''
            try:
                td_atttype = TD()
                if row.classes_attendance.AttendanceType == 1:
                    td_atttype.append(os_gui.get_label('success', T('Trial class')))

                elif row.classes_attendance.AttendanceType == 2:
                    td_atttype.append(os_gui.get_label('primary', T('Drop in')))
            except AttributeError:
                pass

            # Add a small label for online bookings
            td_online_booking = ''
            try:
                if row.classes_attendance.online_booking:
                    td_online_booking = TD(os_gui.get_label('info', T('Online')))
            except AttributeError:
                pass


            td_inv = ''
            if invoices:
                invoices = Invoices()
                if row.invoices.id:
                    invoice = invoices.represent_invoice_for_list(
                        row.invoices.id,
                        repr_row.invoices.InvoiceID,
                        repr_row.invoices.Status,
                        row.invoices.Status,
                        row.invoices.payment_methods_id
                    )
                else:
                    invoice = ''

                td_inv = TD(invoice)


            tr = TR(TD(attending, _class='very_big_check'),
                    td_pic,
                    TD(SPAN(row.auth_user.display_name, _class='bold'), BR(),
                       subscr_cards),
                    td_res,
                    td_atttype,
                    td_online_booking,
                    td_inv,
                    btn)

            table.append(tr)

        # Set some values from the globalenv
        T = current.T
        db = current.db
        auth = current.auth
        os_gui = current.globalenv['os_gui']
        DATE_FORMAT = current.DATE_FORMAT

        modals = DIV()

        cls = db.classes(clsID)

        header = THEAD(TR(TH(),
                          TH(),
                          TH(),
                          TH(), # Enrollment
                          TH(),
                          TH()))


        table = TABLE(header,
                      _class='table table-striped table-hover full-width')

        # ## get list of customers attending this class
        rows = self.get_attendance_rows(clsID, date)

        attendance_list = []
        for i, row in enumerate(rows):
            attendance_list.append(row.auth_user.id)

            repr_row = list(rows[i:i+1].render())[0]
            add_table_row(row,
                          repr_row,
                          reservations=True,
                          invoices=invoices,
                          show_notes=show_notes,
                          modals=modals)


        ## get list of reservations
        rows = self.get_reservation_rows(clsID, date)

        reservations_list = []
        for i, row in enumerate(rows):
            if row.auth_user.id in attendance_list:
                continue

            repr_row = list(rows[i:i+1].render())[0]
            add_table_row(row, repr_row, reservations=True)

            reservations_list.append(row.auth_user.id)


        ## get list of customers who have attended this class during the last 2 weeks
        rows = self.get_attendance_rows_past_days(clsID, date, days=15)

        for i, row in enumerate(rows):
            if row.auth_user.id in attendance_list:
                continue

            if row.auth_user.id in reservations_list:
                continue

            repr_row = list(rows[i:i+1].render())[0]
            add_table_row(row, repr_row, reservations=False)

        return DIV(table, modals)


    def get_checkin_list_customers_email_list(self, clsID, date, days=15):
        """
            :param clsID: db.classes.is 
            :param date: datetime.date
            :param days: int
            :return: list containing email addresses for all people attending, with reservations or expected to attend
        """
        # Set some values from the globalenv
        db = current.db

        mailing_list = []
        # ## get list of customers attending this class
        rows = self.get_attendance_rows(clsID, date)

        attendance_list = []
        for i, row in enumerate(rows):
            attendance_list.append(row.auth_user.id)

            mailing_list.append([row.auth_user.first_name, row.auth_user.last_name, row.auth_user.email])


        ## get list of reservations
        rows = self.get_reservation_rows(clsID, date)

        reservations_list = []
        for i, row in enumerate(rows):
            if row.auth_user.id in attendance_list:
                continue

            mailing_list.append([row.auth_user.first_name, row.auth_user.last_name, row.auth_user.email])

            reservations_list.append(row.auth_user.id)


        ## get list of customers who have attended this class during the last x days
        rows = self.get_attendance_rows_past_days(clsID, date, days=days)

        for i, row in enumerate(rows):
            if row.auth_user.id in attendance_list:
                continue

            if row.auth_user.id in reservations_list:
                continue

                mailing_list.append([row.auth_user.first_name, row.auth_user.last_name, row.auth_user.email])

        return mailing_list


    def get_checkin_list_customers_email_excel(self, clsID, date, days=15):
        """
            :param clsID: db.classes.is 
            :param date: datetime.date
            :param days: int
            :return: cStringIO stream containing: 
                list containing email addresses for all people attending, with reservations or expected to attend
        """
        T = current.T

        import cStringIO, openpyxl
        stream = cStringIO.StringIO()

        title = T('MailingList')
        wb = openpyxl.workbook.Workbook(write_only=True)
        ws = wb.create_sheet(title=title)

        header = [ "First name",
                   "Last name",
                   "Email" ]
        ws.append(header)

        mailing_list = self.get_checkin_list_customers_email_list(clsID, date, days)
        for row in mailing_list:
            ws.append(row)

        wb.save(stream)


        return stream


    def get_signin_buttons(self, clsID, date, cuID, manual_enabled=True):
        """
            Returns sign in buttons for a class
        """
        db = current.db
        os_gui = current.globalenv['os_gui']
        DATE_FORMAT = current.DATE_FORMAT
        date_formatted = date.strftime(DATE_FORMAT)

        customer = Customer(cuID)
        # set random id, used for modal classes
        random_id = unicode(int(random.random() * 1000000000000))

        li_link_class = 'btn btn-default btn-lg full-width'

        button = ''
        btn_group = DIV(_class='btn-group pull-right')
        modals = DIV()
        button_text = current.T('Check in')
        # check if not already added
        check = db.classes_attendance(auth_customer_id = cuID,
                                      classes_id       = clsID,
                                      ClassDate        = date)
        if not check:
            # check for subscription
            subscription = ''
            li_subscription = ''
            li_trial = ''
            li_dropin = ''

            rows = customer.get_subscriptions_on_date(date)
            if rows:
                subscription = rows.first()
                csID = subscription.customers_subscriptions.id
                subscription_url = URL('classes', 'attendance_sign_in_subscription',
                                       vars={'cuID'  : cuID,
                                             'clsID' : clsID,
                                             'csID'  : csID,
                                             'date'  : date_formatted})
                li_subscription = LI(A(SPAN(os_gui.get_fa_icon('fa-edit'), ' ', current.T('Subscription')),
                                        _href=subscription_url,
                                        _class=li_link_class))

            ## check for class card
            classcard = ''
            classcard_choose_url = URL('classes',
                                       'attendance_list_classcards',
                                        vars={'cuID'  : cuID,
                                              'clsID' : clsID,
                                              'date'  : date_formatted},
                                        extension='')
            # set default classcard li, which links to page with add button
            li_classcard = LI(A(SPAN(os_gui.get_fa_icon('fa-ticket'), ' ', current.T('Class card')),
                              _href=classcard_choose_url,
                              _class=li_link_class))


            rows = customer.get_classcards(date)
            if rows:
                classcard_count = len(rows)
                classcard = rows.first()
                ccdID = classcard.customers_classcards.id

                classcard_sign_in_url = URL('classes',
                                            'attendance_sign_in_classcard',
                                            vars={'cuID'  : cuID,
                                                  'clsID' : clsID,
                                                  'ccdID' : ccdID,
                                                  'date'  : date_formatted})

                if classcard_count == 1:
                    classcard_url = classcard_sign_in_url
                else: # more than 1 card, allow user to choose
                    classcard_url = classcard_choose_url

                li_classcard = LI(A(SPAN(os_gui.get_fa_icon('fa-ticket'), ' ', current.T('Class card')),
                                    _href=classcard_url,
                                    _class=li_link_class))


            dropin_url = URL('classes', 'attendance_sign_in_dropin',
                             vars={'cuID'  : cuID,
                                   'clsID' : clsID,
                                   'date'  : date_formatted})
            li_dropin = LI(A(SPAN(os_gui.get_fa_icon('fa-level-down'), ' ', current.T('Drop in class')),
                             _href=dropin_url,
                             _class=li_link_class))
            trial_url = URL('classes', 'attendance_sign_in_trialclass',
                             vars={'cuID'  : cuID,
                                   'clsID' : clsID,
                                   'date'  : date_formatted})
            li_trial = LI(A(SPAN(os_gui.get_fa_icon('fa-compass'), ' ', current.T('Trial class')),
                            _href=trial_url,
                            _class=li_link_class))

            if classcard and subscription:
                modal_content = UL(li_subscription,
                                   li_classcard,
                                   _class='check-in_options')
                modal_class   = 'modal_signin_' + random_id
                button_class  = 'btn btn-default btn-checkin'
                modal_title   = current.T('Check in on subscription or class card?')
                result = os_gui.get_modal(button_text   = button_text,
                                          button_class  = button_class,
                                          modal_title   = modal_title,
                                          modal_content = modal_content,
                                          modal_class   = modal_class)
                btn_group.append(result['button'])
                modals.append(result['modal'])
            elif subscription:
                 # subscription button
                button = A(
                    button_text,
                    _href=subscription_url,
                    _class='btn btn-default btn-checkin')
                btn_group.append(button)
            elif classcard:
                button = A(
                    button_text,
                    _href=classcard_url,
                    _class='btn btn-default btn-checkin')
                btn_group.append(button)
            else:
                # drop in or trial class?
                # classes_attendance customers_id & trialclass attendance type count
                message = SPAN(current.T('No subscription or classcard found for this date.'))
                message.append(' ')
                message.append(current.T("Available options:"))
                modal_content = DIV(message,
                                    BR(), BR(),
                                    UL(li_trial,
                                       li_dropin,
                                       _class='check-in_options'))
                modal_class   = 'modal_signin_' + random_id
                button_class  = 'btn btn-default btn-checkin'
                modal_title   = current.T('Sign in as trial class or drop in class?')
                result = os_gui.get_modal(button_text   = button_text,
                                          button_class  = button_class,
                                          modal_title   = modal_title,
                                          modal_content = modal_content,
                                          modal_class   = modal_class)
                btn_group.append(result['button'])
                modals.append(result['modal'])

            ### Button with modal for manual choice ###

            modal_content = UL(_class='check-in_options')
            if li_subscription:
                modal_content.append(li_subscription)
            if li_classcard:
                modal_content.append(li_classcard)
            if li_dropin:
                modal_content.append(li_dropin)
            if li_trial:
                modal_content.append(li_trial)

            modal_class = 'modal_signin_manual_' + random_id
            button_class = 'btn btn-default pull-right'
            button_text = XML(SPAN(_class='glyphicon glyphicon-edit'))
            modal_title = current.T('Manual check in')
            result = os_gui.get_modal(button_text   = button_text,
                                      button_class  = button_class,
                                      button_title  = current.T("Manual check in"),
                                      modal_title   = modal_title,
                                      modal_content = modal_content,
                                      modal_class   = modal_class)
            if manual_enabled:
                btn_group.append(result['button'])
                modals.append(result['modal'])


        return SPAN(btn_group, modals)


    def get_customer_class_booking_options(self,
                                           clsID,
                                           date,
                                           customer,
                                           trial=False,
                                           request_review=False,
                                           complementary=False,
                                           list_type='shop'):
        """
        :param clsID: db.classes.id
        :param date: datetime.date
        :param customer: os_customer.Customer object
        :param trial: bool
        :param complementary: bool
        :param list_type: should be in ["shop", "attendance", "selfcheckin"]
        :param controller: web2py controller
        :return: list of booking options
        """
        from os_class import Class
        from os_customer_classcard import CustomerClasscard
        from os_customer_subscription import CustomerSubscription

        T = current.T
        db = current.db
        get_sys_property = current.globalenv['get_sys_property']

        options = {
            'subscriptions': [],
            'classcards': [],
            'dropin': False,
            'trial': False,
            'complementary': False
        }

        # Subscriptions
        subscriptions = customer.get_subscriptions_on_date(date)
        if subscriptions:
            for subscription in subscriptions:
                csID = subscription.customers_subscriptions.id
                # Check remaining credits
                credits = subscription.customers_subscriptions.CreditsRemaining or 0
                recon_classes = subscription.school_subscriptions.ReconciliationClasses
                # Create subscription object
                cs = CustomerSubscription(csID)

                if list_type == 'shop':
                    subscription_permission_check = not int(clsID) in cs.get_allowed_classes_booking(public_only=True)
                else:
                    subscription_permission_check = not int(clsID) in cs.get_allowed_classes_attend(public_only=False)

                allowed = True
                if subscription_permission_check:
                    allowed = False

                credits_remaining = credits > (recon_classes * -1)

                options['subscriptions'].append({
                    'clsID': clsID,
                    'Type': 'subscription',
                    'id': csID,
                    'auth_customer_id': subscription.customers_subscriptions.auth_customer_id,
                    'Name': subscription.school_subscriptions.Name,
                    'Allowed': allowed,
                    'Credits': credits,
                    'CreditsRemaining': credits_remaining,
                    'Unlimited': subscription.school_subscriptions.Unlimited,
                    'school_memberships_id': subscription.school_subscriptions.school_memberships_id,
                    'Blocked': cs.get_blocked(date)
                })

        # class cards
        classcards = customer.get_classcards(date)
        if classcards:
            for classcard in classcards:
                ccdID = classcard.customers_classcards.id

                ccd = CustomerClasscard(ccdID)
                classes_remaining = ccd.get_classes_remaining()

                if list_type == 'shop':
                    allowed_classes = ccd.get_allowed_classes_booking()
                else:
                    allowed_classes = ccd.get_allowed_classes_attend(public_only=False)

                allowed = True
                if not int(clsID) in allowed_classes:
                    allowed = False

                options['classcards'].append({
                    'clsID': clsID,
                    'Type': 'classcard',
                    'id': ccdID,
                    'auth_customer_id': classcard.customers_classcards.auth_customer_id,
                    'Name': classcard.school_classcards.Name,
                    'Allowed': allowed,
                    'Enddate': classcard.customers_classcards.Enddate,
                    'ClassesRemaining': classes_remaining,
                    'Unlimited': classcard.school_classcards.Unlimited,
                    'school_memberships_id': classcard.school_classcards.school_memberships_id,
                })

        # Get class prices
        cls = Class(clsID, date)
        prices = cls.get_prices()

        price = prices['dropin']
        has_membership = customer.has_membership_on_date(date)
        membership_price = has_membership and prices['dropin_membership']
        if membership_price:
            price = prices['dropin_membership']

        if price:
            options['dropin'] = {
                'clsID': clsID,
                "Type": "dropin",
                "Name": T('Drop-in'),
                "Price": price,
                "MembershipPrice": membership_price,
                "Message": get_sys_property('shop_classes_dropin_message') or ''
            }

        # Trial
        # get trial class price
        system_enable_class_checkin_trialclass = get_sys_property('system_enable_class_checkin_trialclass')

        if trial and system_enable_class_checkin_trialclass:
            price = prices['trial'] or 0
            membership_price = has_membership and prices['trial_membership']
            if membership_price:
                price = prices['trial_membership']

            options['trial'] = {
                'clsID': clsID,
                "Type": "trial",
                "Name": T('Trial'),
                "Price": price,
                "MembershipPrice": membership_price,
                "Message": get_sys_property('shop_classes_trial_message') or ''
            }

        # Request review
        options['under_review'] = False
        if request_review:
            under_review = self._attendance_sign_in_check_under_review(
                clsID,
                customer.row.id,
                date
            )

            if under_review:
                options['under_review'] = True
            else:
                options['request_review'] = {
                    'clsID': clsID,
                    "Type": "request_review",
                    "Name": T('Request review'),
                }

        # Complementary
        if complementary:
            options['complementary'] = {
                'clsID': clsID,
                "Type": "complementary",
                "Name": T('Complementary'),
            }

        # Reconcile later
        system_enable_class_checkin_reconcile_later = get_sys_property('system_enable_class_checkin_reconcile_later')
        if system_enable_class_checkin_reconcile_later:
            options['reconcile_later'] = {
                'clsID': clsID,
                "Type": "reconcile_later",
                "Name": T('Reconcile later'),
            }


        return options


    def get_customer_class_booking_options_formatted(self,
                                                     clsID,
                                                     date,
                                                     customer,
                                                     trial=False,
                                                     request_review=False,
                                                     complementary=False,
                                                     list_type='shop',
                                                     controller=''):
        """
        :param clsID: db.classes.id
        :param date: datetime.date
        :param date_formatted: datetime.date object formatted with current.DATE_FORMAT
        :param customer: Customer object
        :param: list_type: [shop, attendance, selfcheckin]
        :return:
        """
        def classes_book_options_get_button_book(url, btn_text=""):
            """
                Return book button for booking options
            """
            button_text = T('Book')
            if list_type == 'attendance' or list_type == 'selfcheckin':
                button_text = T("Check in")

            if btn_text:
                button_text = btn_text

            button_book = A(SPAN(button_text, ' ', os_gui.get_fa_icon('fa-chevron-right')),
                            _href=url,
                            _class='pull-right btn btn-link')

            return button_book

        from os_class import Class
        from os_customer_classcard import CustomerClasscard
        from os_customer_subscription import CustomerSubscription

        T = current.T
        db = current.db
        os_gui = current.globalenv['os_gui']
        CURRSYM = current.globalenv['CURRSYM']
        DATE_FORMAT = current.DATE_FORMAT
        get_sys_property = current.globalenv['get_sys_property']

        date_formatted = date.strftime(DATE_FORMAT)

        options = self.get_customer_class_booking_options(
            clsID,
            date,
            customer,
            trial=trial,
            request_review=request_review,
            complementary=complementary,
            list_type=list_type
        )
        formatted_options = DIV(_class='shop-classes-booking-options row')

        if options['under_review']:
            formatted_options.append(
                DIV(
                    os_gui.get_alert(
                        'warning',
                        SPAN(T("You're reviewing this check-in."), ' ',
                             T("By choosing one of the options below it'll automatically be removed from the 'Review requested' list."),
                             BR(),
                             T("Click"), ' ',
                             A(T("here"),
                               _href=URL('reports', 'attendance_review_requested')), ' ',
                             T("to go back to the overview of requested check-in reviews.")
                             ),
                        dismissable=False,
                    ),
                    _class="col-md-10 col-md-offset-1 col-xs-12"
                )
            )

        if options['subscriptions']:
            for subscription in options['subscriptions']:
                csID = subscription['id']
                if not subscription['Allowed']:
                    button_book = os_gui.get_button('noicon',
                                                    URL('#'),
                                                    title=SPAN(T("Not allowed for this class")),
                                                    btn_class='btn-link',
                                                    _class='disabled pull-right grey')
                else:
                    if subscription['Blocked']:
                        button_book = os_gui.get_button('noicon',
                                                        URL('#'),
                                                        title=SPAN(T('Blocked')),
                                                        btn_class='btn-link',
                                                        _class='disabled pull-right grey')
                    elif subscription['CreditsRemaining']:
                        url = URL(controller, 'class_book', vars={'clsID': clsID,
                                                      'csID': csID,
                                                      'cuID': customer.row.id,
                                                      'date': date_formatted})
                        button_book = classes_book_options_get_button_book(url)
                    else:
                        button_book = os_gui.get_button('noicon',
                                                        URL('#'),
                                                        title=SPAN(T('No credits remaining')),
                                                        btn_class='btn-link',
                                                        _class='disabled pull-right grey')

                # Check Credits display
                credits_remaining = subscription['CreditsRemaining']

                if subscription['Unlimited']:
                    credits_display = T('Unlimited')
                else:
                    if subscription['CreditsRemaining'] < 0:
                        credits_display = SPAN(round(subscription['CreditsRemaining'], 1), ' ', T('Credits'))
                    else:
                        credits_display = SPAN(round(subscription['CreditsRemaining'], 1), ' ',
                                               T('Credits remaining'))

                # let's put everything together
                option = DIV(DIV(T('Subscription'),
                                 _class='col-md-3 bold'),
                             DIV(subscription['Name'],
                                 SPAN(XML(' &bull; '),
                                      credits_display,
                                      _class='grey'),
                                 _class='col-md-6'),
                             DIV(button_book,
                                 _class='col-md-3'),
                             _class='col-md-10 col-md-offset-1 col-xs-12')

                formatted_options.append(option)

        elif list_type =='shop':
            # show buy link if list type shop
            features = db.customers_shop_features(1)
            if features.Subscriptions:
                button_buy = A(SPAN(T('Shop'), ' ', os_gui.get_fa_icon('fa-chevron-right')),
                               _href=URL('shop', 'subscriptions'),
                               _class='pull-right btn btn-link')

                option = DIV(DIV(T('Subscription'),
                                 _class='col-md-3 bold'),
                             DIV(T('No subscription found'), BR(),
                                 SPAN(T('Click "Shop" to sign up for a subscription'), _class='grey'),
                                 _class='col-md-6'),
                             DIV(button_buy,
                                 _class='col-md-3'),
                             _class='col-md-10 col-md-offset-1 col-xs-12')

                formatted_options.append(option)


        # class cards
        if options['classcards']:
            for classcard in options['classcards']:
                ccdID = classcard['id']

                ccd = CustomerClasscard(ccdID)
                classes_remaining = ccd.get_classes_remaining_formatted()

                if not classcard['Allowed']:
                    # Check book permission
                    button_book = os_gui.get_button('noicon',
                                                    URL('#'),
                                                    title=SPAN(T("Not allowed for this class")),
                                                    btn_class='btn-link',
                                                    _class='disabled pull-right grey')
                else:
                    url = URL(controller, 'class_book', vars={'clsID': clsID,
                                                  'ccdID': ccdID,
                                                  'cuID': customer.row.id,
                                                  'date': date_formatted})
                    button_book = classes_book_options_get_button_book(url)


                option = DIV(DIV(T('Class card'),
                                 _class='col-md-3 bold'),
                             DIV(classcard['Name'], ' ',
                                 SPAN(XML(' &bull; '), T('expires'), ' ',
                                      classcard['Enddate'].strftime(DATE_FORMAT),
                                      XML(' &bull; '), classes_remaining,
                                      _class='small_font grey'),
                                 _class='col-md-6'),
                             DIV(button_book,
                                 _class='col-md-3'),
                             _class='col-md-10 col-md-offset-1 col-xs-12')

                formatted_options.append(option)

        elif list_type == 'attendance':
                url = URL('customers', 'classcard_add',
                          vars={'cuID': customer.row.id,
                                'clsID': clsID,
                                'date': date_formatted})
                button_add = A(SPAN(T('Sell card'), ' ', os_gui.get_fa_icon('fa-chevron-right')),
                                _href=url,
                                _class='pull-right btn btn-link')


                option = DIV(DIV(T('Class card'),
                                 _class='col-md-3 bold'),
                             DIV(T('No cards found - sell a new card',),
                                 _class='col-md-6'),
                             DIV(button_add,
                                 _class='col-md-3'),
                             _class='col-md-10 col-md-offset-1 col-xs-12')

                formatted_options.append(option)

        elif list_type =='shop':
            # show buy link if list type shop
            features = db.customers_shop_features(1)
            if features.Classcards:
                button_buy = A(SPAN(T('Shop'), ' ', os_gui.get_fa_icon('fa-chevron-right')),
                               _href=URL('shop', 'classcards'),
                               _class='pull-right btn btn-link')

                option = DIV(DIV(T('Class card'),
                                 _class='col-md-3 bold'),
                             DIV(T('No class card found'), BR(),
                                 SPAN(T('Click "Shop" to buy a card'), _class='grey'),
                                 _class='col-md-6'),
                             DIV(button_buy,
                                 _class='col-md-3'),
                             _class='col-md-10 col-md-offset-1 col-xs-12')

                formatted_options.append(option)

        # Get class prices
        cls = Class(clsID, date)
        prices = cls.get_prices()

        # drop in
        if options['dropin']:
            dropin = options['dropin']

            url = URL(controller, 'class_book', vars={'clsID': clsID,
                                                      'dropin': 'true',
                                                      'cuID': customer.row.id,
                                                      'date': date_formatted})
            button_book = classes_book_options_get_button_book(url)

            membership_notification = ''
            if dropin['MembershipPrice']:
                membership_notification = SPAN(' ', XML('&bull;'), ' ', '(', T('Membership price'), ')',
                                               _class='grey')

            option = DIV(DIV(T('Drop in'),
                             _class='col-md-3 bold'),
                         DIV(T('Class price:'), ' ', CURRSYM, ' ', format(dropin['Price'], '.2f'), ' ',
                             membership_notification,
                             BR(),
                             SPAN(dropin.get('Message', ''),
                                  _class='grey'),
                             _class='col-md-6'),
                         DIV(button_book,
                             _class='col-md-3'),
                         _class='col-md-10 col-md-offset-1 col-xs-12')

            formatted_options.append(option)

        # Trial
        # get trial class price
        if trial and options['trial']:
            url = URL(controller, 'class_book', vars={'clsID': clsID,
                                                      'trial': 'true',
                                                      'cuID': customer.row.id,
                                                      'date': date_formatted})
            button_book = classes_book_options_get_button_book(url)

            trial = options['trial']

            membership_notification = ''
            if trial['MembershipPrice']:
                membership_notification = SPAN(' ', XML('&bull;'), ' ', '(', T('Membership price'), ')',
                                               _class='grey')

            option = DIV(DIV(T('Trial'),
                             _class='col-md-3 bold'),
                         DIV(T('Class price:'), ' ', CURRSYM, ' ', format(trial['Price'], '.2f'), ' ',
                             membership_notification,
                             BR(),
                             SPAN(trial.get('Message', ''),
                                  _class='grey'),
                             _class='col-md-6'),
                         DIV(button_book,
                             _class='col-md-3'),
                         _class='col-md-10 col-md-offset-1 col-xs-12')

            formatted_options.append(option)


        # Request review
        if request_review and 'request_review' in options:
            request_review = options['request_review']

            formatted_options.append(DIV(HR(), _class='col-md-10 col-md-offset-1'))

            url = URL(controller, 'class_book', vars={'clsID': clsID,
                                                      'request_review': 'true',
                                                      'cuID': customer.row.id,
                                                      'date': date_formatted})
            button_book = classes_book_options_get_button_book(url, T("Request review"))

            option = DIV(DIV(request_review['Name'],
                             _class='col-md-3 bold'),
                         DIV(T('Should someone review this check-in later?'),
                             BR(),
                             SPAN(T("Please use this option in case an expected check-in option isn't available"),
                                  _class='grey'),
                             _class='col-md-6'),
                         DIV(button_book,
                             _class='col-md-3'),
                         _class='col-md-10 col-md-offset-1 col-xs-12')

            formatted_options.append(option)


        # Complementary
        if complementary and options['complementary'] and not list_type =='shop':
            complementary = options['complementary']

            formatted_options.append(DIV(HR(), _class='col-md-10 col-md-offset-1'))

            url = URL(controller, 'class_book', vars={'clsID': clsID,
                                                      'complementary': 'true',
                                                      'cuID': customer.row.id,
                                                      'date': date_formatted})
            button_book = classes_book_options_get_button_book(url)

            option = DIV(DIV(complementary['Name'],
                             _class='col-md-3 bold'),
                         DIV(T('Give this class for free'),
                             _class='col-md-6'),
                         DIV(button_book,
                             _class='col-md-3'),
                         _class='col-md-10 col-md-offset-1 col-xs-12')

            formatted_options.append(option)

        # Reconcile later
        system_enable_class_checkin_reconcile_later = get_sys_property('system_enable_class_checkin_reconcile_later')
        if system_enable_class_checkin_reconcile_later and options['reconcile_later'] and not list_type =='shop':
            reconcile_later = options['reconcile_later']

            formatted_options.append(DIV(HR(), _class='col-md-10 col-md-offset-1'))

            url = URL(controller, 'class_book', vars={'clsID': clsID,
                                                      'reconcile_later': 'true',
                                                      'cuID': customer.row.id,
                                                      'date': date_formatted})
            button_book = classes_book_options_get_button_book(url)

            option = DIV(DIV(reconcile_later['Name'],
                             _class='col-md-3 bold'),
                         DIV(T("Pay at a later time for this drop-in class"),
                             _class='col-md-6'),
                         DIV(button_book,
                             _class='col-md-3'),
                         _class='col-md-10 col-md-offset-1 col-xs-12')

            formatted_options.append(option)

        return formatted_options


    def get_customer_class_enrollment_options(self,
                                              clsID,
                                              date,
                                              customer,
                                              list_type='shop',
                                              controller=''):
        """
        :param clsID: db.classes.id
        :param date: datetime.date
        :param date_formatted: datetime.date object formatted with current.DATE_FORMAT
        :param customer: Customer object
        :param: list_type: [shop, attendance]
        :return:
        """
        from os_customer_subscription import CustomerSubscription
        from os_gui import OsGui

        T = current.T
        os_gui = OsGui()
        DATE_FORMAT = current.DATE_FORMAT

        date_formatted = date.strftime(DATE_FORMAT)
        customer_subscriptions = customer.get_subscriptions_on_date(date)


        public_only = True
        if list_type == 'attendance':
            public_only = False

        options = DIV(_class="shop-classes-booking-options row")
        try:
            for s in customer_subscriptions:
                cs = CustomerSubscription(s.customers_subscriptions.id)
                credits_remaining = cs.get_credits_balance()
                if int(clsID) in cs.get_allowed_classes_enrollment(public_only=public_only):
                    btn_enroll = A(SPAN(T('Enroll'), ' ',
                                        os_gui.get_fa_icon('fa-chevron-right')),
                                   _href=URL(controller, 'class_enroll',
                                             vars={'cuID': customer.cuID,
                                                   'clsID': clsID,
                                                   'csID': s.customers_subscriptions.id,
                                                   'date': date_formatted}),
                                   _class='btn btn-link pull-right'),

                else:
                    btn_enroll = os_gui.get_button('noicon',
                                                    URL('#'),
                                                    title=SPAN(T("Not allowed for this class")),
                                                    btn_class='btn-link',
                                                    _class='disabled pull-right grey')

                # Check Credits display
                if s.school_subscriptions.Unlimited:
                    credits_display = T('Unlimited')
                else:
                    if credits_remaining < 0:
                        credits_display = SPAN(round(credits_remaining, 1), ' ', T('Credits'))
                    else:
                        credits_display = SPAN(round(credits_remaining, 1), ' ',
                                               T('Credits remaining'))

                ##
                # Option to enroll on this subscription (or not, but list it for user clarity)
                ##
                option = DIV(DIV(T("Subscription"),
                                 _class='col-md-3 bold'),
                             DIV(SPAN(s.school_subscriptions.Name), ' ', XML('&bull;'), ' ',
                                 SPAN(credits_display, _class='grey'), BR(),
                                 # SPAN(T("Start:"), ' ', s.customers_subscriptions.Startdate.strftime(DATE_FORMAT),
                                 #      _class='grey'),
                                 _class='col-md-6'),
                             DIV(btn_enroll,
                                 _class='col-md-3'),
                             _class='col-md-10 col-md-offset-1 col-xs-12')
                options.append(option)
        except TypeError:
            pass


        return options

    def _get_teachers_note_modal(self,
                                 cuID,
                                 customers_name,
                                 modals_div):
        """
            Returns a modal popup for teacher notes
        """
        T = current.T
        db = current.db
        os_gui = current.globalenv['os_gui']

        notes = LOAD('customers', 'notes.load', ajax=True,
                     vars={'cuID':cuID,
                           'note_type':'teachers'})

        modal_class = 'customers_te_notes_' + unicode(cuID)
        modal_title = SPAN(T('Teacher notes for'), ' ', customers_name)

        query = (db.customers_notes.TeacherNote == True) & \
                (db.customers_notes.auth_customer_id == cuID)
        count_notes = db(query).count()

        notes_text = T('Notes')
        if count_notes == 1:
            notes_text = T('Note ')

        notes_text = SPAN(unicode(count_notes), ' ', notes_text)
        button_text = XML(notes_text)

        result = os_gui.get_modal(button_text=button_text,
                                  modal_title=modal_title,
                                  modal_content=notes,
                                  modal_class=modal_class,
                                  button_class='btn btn-default btn-checkin')
        modals_div.append(result['modal'])
        button = result['button']

        return dict(modals_div = modals_div,
                    button=button)


    def attendance_sign_in_subscription(self,
                                        cuID,
                                        clsID,
                                        csID,
                                        date,
                                        online_booking=False,
                                        credits_hard_limit=False,
                                        booking_status='booked'):
        """
            :param cuID: db.auth_user.id
            :param clsID: db.classes.id 
            :param csID: db.customers_subscriptions.id
            :param date: datetime.date
            :return: dict status[ok|fail], message
        """
        def take_credit():
            # Take 1 credit
            cls = Class(clsID, date)
            cscID = db.customers_subscriptions_credits.insert(
                customers_subscriptions_id = csID,
                classes_attendance_id = clattID,
                MutationType = 'sub',
                MutationAmount = '1',
                Description = cls.get_name(pretty_date=True)
            )

        from os_class import Class

        db = current.db
        T = current.T
        DATE_FORMAT = current.DATE_FORMAT
        cache_clear_customers_subscriptions = current.globalenv['cache_clear_customers_subscriptions']

        status = 'ok'
        message = ''
        signed_in = self._attendance_sign_in_check_signed_in(clsID, cuID, date)
        # check credits remaining

        paused = self._attedance_sign_in_subscription_check_paused(csID, date)
        blocked = self._attedance_sign_in_subscription_check_blocked(csID, date)
        credits_remaining = self._attendance_sign_in_subscription_credits_remaining(csID)
        message_no_credits = T('No credits remaining on this subscription')

        class_data = dict(
            auth_customer_id=cuID,
            CustomerMembership=self._attendance_sign_in_has_membership(cuID, date),
            classes_id=clsID,
            ClassDate=date,
            AttendanceType=None,  # None = subscription
            customers_subscriptions_id=csID,
            online_booking=online_booking,
            BookingStatus=booking_status
        )


        if not credits_remaining and credits_hard_limit:
            # return message, don't sign in
            message = message_no_credits
            status = 'fail'
        elif paused: # check for paused subscription
            # return message, don't sign in
            message = paused
            status = 'fail'
        elif blocked: # check for blocked subscription
            # return message, don't sign in
            message = blocked
            status = 'fail'
        else:
            if signed_in:
                if signed_in.AttendanceType == 5:
                    # Under review, so update
                    db(db.classes_attendance._id == signed_in.id).update(**class_data)
                    clattID = signed_in.id
                    take_credit()
                else:
                    # return message, don't sign in
                    status = 'fail'
                    message = T("Customer has already booked or is already checked-in")
            else:
                # Check Class Checkin Limit
                cs = db.customers_subscriptions(csID)
                ssu = db.school_subscriptions(cs.school_subscriptions_id)

                if ssu.ClassCheckinLimit:
                    left = [
                        db.customers_subscriptions.on(
                            db.classes_attendance.customers_subscriptions_id ==
                            db.customers_subscriptions.id
                        )
                    ]

                    query = (db.classes_attendance.classes_id == clsID) & \
                            (db.classes_attendance.ClassDate == date) & \
                            (db.customers_subscriptions.school_subscriptions_id == ssu.id)

                    rows = db(query).select(
                        db.classes_attendance.id,
                        left=left
                    )

                    if len(rows) >= ssu.ClassCheckinLimit:
                        status = 'fail'
                        message = T("Check-in limit reached for this subscription in this class")

                if status == 'ok':
                    clattID = db.classes_attendance.insert(**class_data)
                    take_credit()
                    cache_clear_customers_subscriptions(cuID)

        return dict(status=status, message=message)


    def _attendance_sign_in_subscription_credits_remaining(self, csID):
        """
        Check if this subscription has remaining classes, if not, set message

        :param csID:
        :param clattID:
        :param date:
        :return:
        """
        from os_customer_subscription import CustomerSubscription

        T = current.T
        db = current.db

        cs = CustomerSubscription(csID)
        balance = cs.get_credits_balance()
        recon_classes = cs.ssu.ReconciliationClasses

        credits_remaining = balance > (recon_classes * -1)

        return credits_remaining


    def _attedance_sign_in_subscription_check_paused(self, csID, date):
        """
            Check if the subscription if paused on given date, if so, display
            a message for the user
        """
        from openstudio.os_customer_subscriptions import CustomerSubscriptions

        T = current.T
        message = ''

        cs = CustomerSubscriptions(csID)
        paused = cs.get_paused(date)
        if paused:
            message = T("Subscription is paused on this date")

        return message


    def _attedance_sign_in_subscription_check_blocked(self, csID, date):
        """
            Check if the subscription if blocked on given date, if so, display
            a message for the user
        """
        from openstudio.os_customer_subscription import CustomerSubscription

        T = current.T
        message = ''

        cs = CustomerSubscription(csID)
        blocked = cs.get_blocked(date)
        if blocked:
            message = T("Subscription is blocked on this date")

        return message


    def _attendance_sign_in_has_membership(self, cuID, date):
        """
        :param cuID: db.auth_user.id
        :return: Bool - true if customer has membership, else false
        """
        from os_customer import Customer

        customer = Customer(cuID)
        return customer.has_membership_on_date(date)


    def _attendance_sign_in_create_invoice(self,
                                           cuID,
                                           caID,
                                           clsID,
                                           date,
                                           product_type):
        """
            Creates an invoice for a drop in or trial class
        """
        from os_class import Class
        from os_customer import Customer
        from os_invoice import Invoice

        db = current.db
        DATE_FORMAT = current.DATE_FORMAT
        T = current.T

        date_formatted = date.strftime(DATE_FORMAT)

        if product_type not in ['trial', 'dropin']:
            raise ValueError('Product type has to be trial or dropin')

        customer = Customer(cuID)
        cls = Class(clsID, date)
        prices = cls.get_prices()

        has_membership = customer.has_membership_on_date(date)

        if product_type == 'dropin':
            price = prices['dropin']

            if has_membership and prices['dropin_membership']:
                price = prices['dropin_membership']

        elif product_type == 'trial':
            price = prices['trial']

            if has_membership and prices['trial_membership']:
                price = prices['trial_membership']

        # check if the price is > 0 when adding an invoice
        if price == 0:
            return

        igpt = db.invoices_groups_product_types(ProductType=product_type)

        iID = db.invoices.insert(
            invoices_groups_id=igpt.invoices_groups_id,
            # classes_attendance_id      = caID,
            Description=T('Class on ') + date_formatted,
            Status='sent'
        )

        # create object to set Invoice# and due date
        invoice = Invoice(iID)
        invoice.item_add_class(
            cuID,
            caID,
            clsID,
            date,
            product_type
        )
        invoice.set_amounts()


    def attendance_sign_in_classcard_recurring(self, cuID, clsID, ccdID, date, date_until, online_booking=False, booking_status='booked'):
        """
        :param cuID:
        :param clsID:
        :param ccdID:
        :param date:
        :param until_date:
        :param online_booking:
        :param booking_status:
        :return:
        """
        from os_class import Class
        from os_customer_classcard import CustomerClasscard

        T = current.T
        TODAY_LOCAL = current.TODAY_LOCAL
        DATE_FORMAT = current.DATE_FORMAT
        get_sys_property = current.globalenv['get_sys_property']

        ccd = CustomerClasscard(ccdID)
        ccd_enddate = ccd.classcard.Enddate


        classes_booked = 0
        messages = []

        classes_remaining = ccd.get_classes_remaining()

        shop_classes_advance_booking_limit = get_sys_property('shop_classes_advance_booking_limit')
        # print shop_classes_advance_booking_limit
        book_date_limit = False
        if shop_classes_advance_booking_limit:
            book_date_limit = TODAY_LOCAL + datetime.timedelta(int(shop_classes_advance_booking_limit))


        while date <= date_until:
            # print date
            date_formatted = date.strftime(DATE_FORMAT)
            sign_in_ok = True
            # Check if class is taking place
            cls = Class(clsID, date)
            if cls.is_taking_place() == False:
                sign_in_ok = False
                # print 'class not happening'
                messages.append(T("Class is cancelled or falls within a holiday"))

            # Check online booking spaces available
            if cls.get_full_bookings_shop() == True: # no spaces available
                sign_in_ok = False
                # print "Class full"
                messages.append(T("There are no more spaces for online bookings available for this class"))

            # Check classes remaining
            #if classes_remaining != 'unlimited' or classes_remaining < 1:
            if classes_remaining == 0: # This will pass when it's 'unlimited'
                # print 'no classes remaining'
                date = date_until  # Stop loop
                #TODO: message for customer
                sign_in_ok = False
                messages.append(T('No more classes remaining on this card for class on') + ' ' + date_formatted)

            # Check not past max sign in date
            # print 'booking date limit'
            # print book_date_limit
            if book_date_limit:
                if date > book_date_limit:
                    # print 'class past booking in advance limit'
                    # TODO: message for customer
                    date = date_until # Stop loop
                    sign_in_ok = False

            # Check not past classcard enddate
            if date >= ccd_enddate:
                # print 'class past classcard enddate'
                date = date_until  # Stop loop
                #TODO: message for customer
                sign_in_ok = False
                messages.append(T('Date is past card expiration date:') + ' ' + date_formatted)

            # Check sign in status for fail (if fail, don't add count)
            if sign_in_ok:
                result = self.attendance_sign_in_classcard(cuID, clsID, ccdID, date)
                if not result['status'] == 'fail':
                    messages.append(T("Booked class on") + ' ' + date_formatted)
                    # update remaining classes
                    if not classes_remaining == 'unlimited':
                        classes_remaining -= 1

                    classes_booked += 1

            date += datetime.timedelta(days=7)

        return dict(classes_booked=classes_booked,
                    messages=messages)


    def attendance_sign_in_classcard(self, cuID, clsID, ccdID, date, online_booking=False, booking_status='booked'):
        """
            :param cuID: db.auth_user.id 
            :param clsID: db.classes.id
            :param ccdID: db.customers_classcards.id
            :param date: datetime.date
            :return: 
        """
        from os_classcards_helper import ClasscardsHelper

        db = current.db
        T = current.T

        ccdh = ClasscardsHelper()
        classes_available = ccdh.get_classes_available(ccdID)

        status = 'fail'
        message = ''
        if classes_available:
            class_data = dict(
                auth_customer_id=cuID,
                CustomerMembership=self._attendance_sign_in_has_membership(cuID, date),
                classes_id=clsID,
                ClassDate=date,
                AttendanceType=3,  # 3 = classcard
                customers_classcards_id=ccdID,
                online_booking=online_booking,
                BookingStatus=booking_status
            )

            signed_in = self._attendance_sign_in_check_signed_in(clsID, cuID, date)
            if signed_in:
                if signed_in.AttendanceType == 5:
                    # Under review, so update
                    status = 'ok'
                    db(db.classes_attendance._id == signed_in.id).update(**class_data)
                else:
                    message = T("Already checked in for this class")
            else:
                status = 'ok'

                db.classes_attendance.insert(
                    **class_data
                )

                # update class count
                ccdh = ClasscardsHelper()
                ccdh.set_classes_taken(ccdID)
        else:
            message = T("Unable to add, no classes left on card")


        return dict(status=status, message=message)


    def attendance_sign_in_dropin(self,
                                  cuID,
                                  clsID,
                                  date,
                                  online_booking=False,
                                  invoice=True,
                                  booking_status='booked'):
        """
            :param cuID: db.auth_user.id
            :param clsID: db.classes.id
            :param date: datetime.date
            :return: 
        """
        db = current.db
        T = current.T

        status = 'fail'
        message = ''
        caID = ''

        class_data = dict(
            auth_customer_id=cuID,
            CustomerMembership=self._attendance_sign_in_has_membership(cuID, date),
            classes_id=clsID,
            ClassDate=date,
            AttendanceType=2,  # 2 = drop in class
            online_booking=online_booking,
            BookingStatus=booking_status
        )

        signed_in = self._attendance_sign_in_check_signed_in(clsID, cuID, date)
        if signed_in:
            if signed_in.AttendanceType == 5:
                # Under review, so update
                db(db.classes_attendance._id == signed_in.id).update(**class_data)
                status = 'ok'
                caID = signed_in.id
                if invoice:
                    self._attendance_sign_in_create_invoice(cuID,
                                                            caID,
                                                            clsID,
                                                            date,
                                                            'dropin')
            else:
                message = T("Already checked in for this class")
        else:
            status = 'ok'
            caID = db.classes_attendance.insert(**class_data)

            if invoice:
                self._attendance_sign_in_create_invoice(cuID,
                                                        caID,
                                                        clsID,
                                                        date,
                                                        'dropin')

        return dict(status=status, message=message, caID=caID)


    def attendance_sign_in_trialclass(self,
                                      cuID,
                                      clsID,
                                      date,
                                      online_booking=False,
                                      invoice=True,
                                      booking_status='booked'):
        """
            :param cuID: db.auth_user.id
            :param clsID: db.classes.id
            :param date: datetime.date
            :return: 
        """
        db = current.db
        T = current.T

        status = 'fail'
        message = ''
        caID = ''

        class_data = dict(
            auth_customer_id=cuID,
            CustomerMembership=self._attendance_sign_in_has_membership(cuID, date),
            classes_id=clsID,
            ClassDate=date,
            AttendanceType=1,  # 1 = trial class
            online_booking=online_booking,
            BookingStatus=booking_status
        )

        signed_in = self._attendance_sign_in_check_signed_in(clsID, cuID, date)

        if signed_in:
            if signed_in.AttendanceType == 5:
                status = 'ok'
                db(db.classes_attendance._id == signed_in.id).update(**class_data)
                caID = signed_in.id
                if invoice:
                    self._attendance_sign_in_create_invoice(cuID,
                                                            caID,
                                                            clsID,
                                                            date,
                                                            'trial')
            else:
                message = T("Already checked in for this class")
        else:
            status = 'ok'
            caID = db.classes_attendance.insert(**class_data)

            if invoice:
                self._attendance_sign_in_create_invoice(cuID,
                                                        caID,
                                                        clsID,
                                                        date,
                                                        'trial')

        return dict(status=status, message=message, caID=caID)


    def attendance_sign_in_complementary(self,
                                         cuID,
                                         clsID,
                                         date,
                                         booking_status='booked'):
        """
            :param cuID: db.auth_user.id
            :param clsID: db.classes.id
            :param date: datetime.date
            :return:
        """
        from tools import OsTools

        os_tools = OsTools()
        db = current.db
        T = current.T

        status = 'ok'
        message = ''
        caID = ''

        class_data = dict(
            auth_customer_id=cuID,
            CustomerMembership=self._attendance_sign_in_has_membership(cuID, date),
            classes_id=clsID,
            ClassDate=date,
            AttendanceType=4,  # 4 = Complementary class
            online_booking=False,
            BookingStatus=booking_status
        )

        signed_in = self._attendance_sign_in_check_signed_in(clsID, cuID, date)

        if signed_in:
            if signed_in.AttendanceType == 5:
                # Under review, so update
                db(db.classes_attendance._id == signed_in.id).update(**class_data)
            else:
                status = 'fail'
                message = T("Already checked in for this class")
        else:
            # not signed in
            max_complementary_checkins = \
                os_tools.get_sys_property('class_attendance_max_complementary_checkins')

            if max_complementary_checkins:
                # count number of complementary check-ins
                query = (db.classes_attendance.classes_id == clsID) & \
                        (db.classes_attendance.ClassDate == date) & \
                        (db.classes_attendance.AttendanceType == 4)
                if db(query).count() >= int(max_complementary_checkins):
                    status = 'fail'
                    message = T("Maximum number of complementary check-ins reached for this class")

            if status == "ok":
                caID = db.classes_attendance.insert(**class_data)


        return dict(status=status, message=message, caID=caID)


    def attendance_sign_in_reconcile_later(self,
                                           cuID,
                                           clsID,
                                           date,
                                           booking_status='booked'):
        """
            :param cuID: db.auth_user.id
            :param clsID: db.classes.id
            :param date: datetime.date
            :return:
        """
        from tools import OsTools

        os_tools = OsTools()
        db = current.db
        T = current.T

        status = 'ok'
        message = ''
        caID = ''

        class_data = dict(
            auth_customer_id=cuID,
            CustomerMembership=self._attendance_sign_in_has_membership(cuID, date),
            classes_id=clsID,
            ClassDate=date,
            AttendanceType=6,  # 4 = Reconcile later
            online_booking=False,
            BookingStatus=booking_status
        )

        signed_in = self._attendance_sign_in_check_signed_in(clsID, cuID, date)

        if signed_in:
            if signed_in.AttendanceType == 5:
                # Under review, so update
                db(db.classes_attendance._id == signed_in.id).update(**class_data)
            else:
                status = 'fail'
                message = T("Already checked in for this class")
        else:
            # not signed in
            if status == "ok":
                caID = db.classes_attendance.insert(**class_data)


        return dict(status=status, message=message, caID=caID)


    def attendance_sign_in_request_review(self,
                                         cuID,
                                         clsID,
                                         date,
                                         booking_status='attending'):
        """
            :param cuID: db.auth_user.id
            :param clsID: db.classes.id
            :param date: datetime.date
            :return:
        """
        db = current.db
        T = current.T

        status = 'fail'
        message = ''
        caID = ''

        signed_in = self._attendance_sign_in_check_signed_in(clsID, cuID, date)

        if signed_in:
            if signed_in.AttendanceType == 5:
                # Under review, so update
                message = T("A review has already been requested for this check-in")
            else:
                message = T("Already checked in for this class")
        else:
            status = 'ok'
            caID = db.classes_attendance.insert(
                auth_customer_id=cuID,
                CustomerMembership = self._attendance_sign_in_has_membership(cuID, date),
                classes_id=clsID,
                ClassDate=date,
                AttendanceType=5, # 5 = Request review
                online_booking=False,
                BookingStatus=booking_status
            )

        return dict(status=status, message=message, caID=caID)


    def _attendance_sign_in_check_signed_in(self, clsID, cuID, date):
        """
            Check if a customer isn't already signed in to a class
        """
        db = current.db
        query = (db.classes_attendance.classes_id == clsID) & \
                (db.classes_attendance.auth_customer_id == cuID) & \
                (db.classes_attendance.ClassDate == date) & \
                (db.classes_attendance.BookingStatus != 'cancelled')

        rows = db(query).select(db.classes_attendance.ALL)
        if rows:
            return rows.first()
        else:
            return False


    def _attendance_sign_in_check_under_review(self, clsID, cuID, date):
        """
            Check if a customer isn't already signed in to a class
        """
        under_review = False

        attending = self._attendance_sign_in_check_signed_in(
            clsID,
            cuID,
            date
        )

        if attending and attending.AttendanceType == 5:
            under_review = True

        return under_review


    def attendance_cancel_classes_in_school_holiday(self, shID):
        """
            :param shID: db.school_holidays.id
            :return: list of db.classes.id
        """
        db = current.db

        # Get locations
        query = (db.school_holidays_locations.school_holidays_id == shID)
        rows =  db(query).select(db.school_holidays_locations.school_locations_id)
        location_ids = []
        for row in rows:
            location_ids.append(row.school_locations_id)

        # Get classes
        query = (db.classes.school_locations_id.belongs(location_ids))
        rows = db(query).select(db.classes.id)
        class_ids = []
        for row in rows:
            class_ids.append(row.id)

        # Get holiday record and cancel classes
        sh = db.school_holidays(shID)
        self.attendance_cancel_reservations_for_classes(class_ids, sh.Startdate, sh.Enddate)


    def attendance_cancel_reservations_for_classes(self, class_ids, p_start, p_end = None):
        """
            :param class_ids: list of db.classes.id
            :param p_start: datetime.date
            :param p_end: datetime.date
            :return: None
        """
        from os_customers_subscriptions_credits import CustomersSubscriptionsCredits

        db = current.db

        # in case end period is not specified, assume it's for one day
        if not p_end:
            p_end = p_start

        query = (db.classes_attendance.classes_id.belongs(class_ids)) & \
                (db.classes_attendance.ClassDate >= p_start) & \
                (db.classes_attendance.ClassDate <= p_end)

        db(query).update(BookingStatus='cancelled')

        # Return subscription credits to customers
        csch = CustomersSubscriptionsCredits()
        csch.refund_credits_in_period(query)
        