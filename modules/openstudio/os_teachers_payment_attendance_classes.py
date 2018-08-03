# -*- coding: utf-8 -*-

import datetime

from gluon import *


class TeachersPaymentAttendanceClasses:
    """
        Class that gathers useful functions for db.teachers_payments_attendance
    """
    def get_rows(self, status='not_verified', sorting='time', formatted=False):
        db = current.db

        left = [
            db.classes.on(
                db.teachers_payment_attendance_classes.classes_id ==
                db.classes.id
            )
        ]

        if sorting == 'time':
            orderby = db.teachers_payment_attendance_classes.ClassDate | \
                      db.classes.Starttime
        elif sorting == 'teacher':
            orderby = db.teachers_payment_attendance_classes.auth_teacher_id

        query = (db.teachers_payment_attendance_classes.Status == status)
        rows = db(query).select(
            db.teachers_payment_attendance_classes.ALL,
            db.classes.ALL,
            left=left,
            orderby=orderby
        )

        if not formatted:
            return rows
        else:
            return self.rows_to_table(rows, status)


    def rows_to_table(self, rows, status):
        """
        turn rows object into an html table
        :param rows: gluon.dal.rows with all fields of db.teachers_payment_attendance_classes
        and db.classes
        :return: html table
        """
        from os_gui import OsGui

        T = current.T
        auth = current.auth
        os_gui = OsGui()

        header = THEAD(TR(
            TH(T("Date")),
            TH(T("Time")),
            TH(T("Location")),
            TH(T("Class type")),
            TH(T("Teacher")),
            TH(T("Attendance")),
            TH(T("Amount")),
            TH(T("Status")),
            TH() # Actions
        ))

        table = TABLE(header, _class="table table-striped table-hover")

        permissions = self._rows_to_table_button_permissions()

        for i, row in enumerate(rows):
            repr_row = list(rows[i:i + 1].render())[0]


            if status == 'not_verified':
                buttons = self._rows_to_table_get_not_verified_buttons(row, os_gui, permissions)
            elif status == 'verified':
                buttons = self._rows_to_table_get_verified_buttons(row, os_gui, permissions)
            else:
                buttons = ''

            tr = TR(
                TD(repr_row.teachers_payment_attendance_classes.ClassDate),
                TD(repr_row.classes.Starttime),
                TD(repr_row.classes.school_locations_id),
                TD(repr_row.classes.school_classtypes_id),
                TD(repr_row.teachers_payment_attendance_classes.auth_teacher_id, BR(),
                   repr_row.teachers_payment_attendance_classes.auth_teacher_id2),
                TD(repr_row.teachers_payment_attendance_classes.AttendanceCount),
                TD(repr_row.teachers_payment_attendance_classes.Amount),
                TD(repr_row.teachers_payment_attendance_classes.Status),
                TD(buttons)
            )

            table.append(tr)

        return table


    def _rows_to_table_button_permissions(self):
        """
            :return: dict containing button permissions for a user
        """
        auth = current.auth
        permissions = {}

        if auth.has_membership(group_id='Admins') or \
                auth.has_permission('read', 'classes_attendance'):
            permissions['classes_attendance'] = True
        if auth.has_membership(group_id='Admins') or \
                auth.has_permission('update', 'teachers_payment_attendance_classes'):
            permissions['teachers_payment_attendance_classes'] = True

        return permissions


    def _rows_to_table_get_not_verified_buttons(self, row, os_gui, permissions):
        """
            Returns buttons for schedule
            - one button group for edit & attendance buttons
            - separate button for delete
        """
        T = current.T
        DATE_FORMAT = current.DATE_FORMAT
        buttons = DIV(_class='pull-right')


        links = []
        links.append(['header', T('Actions')])
        # Check Update teachers payment attendance classes
        if permissions.get('teachers_payment_attendance_classes', False):
            links.append(A(os_gui.get_fa_icon('fa-check'), T('Verify'),
                           _href=URL('finance', 'teachers_payment_attendance_class_verify',
                                     vars={'tpacID': row.teachers_payment_attendance_classes.id}),
                           _class='text-green'))
            links.append('divider')

        # Check Attendance permission
        if permissions.get('classes_attendance', False):
            links.append(['header', T('Go to')])
            links.append(A(os_gui.get_fa_icon('fa-chevron-right'), T('Attendance'),
                           _href=URL('classes', 'attendance',
                                     vars={'clsID': row.classes.id,
                                           'date':row.teachers_payment_attendance_classes.ClassDate.strftime(DATE_FORMAT)})))


        tpac_menu = os_gui.get_dropdown_menu(
            links=links,
            btn_text=T('Actions'),
            btn_size='btn-sm',
            btn_icon='actions',
            menu_class='btn-group pull-right')

        return DIV(tpac_menu, _class='pull-right')


    def _rows_to_table_get_verified_buttons(self, row, os_gui, permissions):
        """
            Returns buttons for schedule
            - one button group for edit & attendance buttons
            - separate button for delete
        """
        T = current.T
        DATE_FORMAT = current.DATE_FORMAT
        buttons = DIV(_class='pull-right')


        links = []
        # Check Attendance permission
        if permissions.get('classes_attendance', False):
            links.append(['header', T('Go to')])
            links.append(A(os_gui.get_fa_icon('fa-chevron-right'), T('Attendance'),
                           _href=URL('classes', 'attendance',
                                     vars={'clsID': row.classes.id,
                                           'date':row.teachers_payment_attendance_classes.ClassDate.strftime(DATE_FORMAT)})))


        tpac_menu = os_gui.get_dropdown_menu(
            links=links,
            btn_text=T('Actions'),
            btn_size='btn-sm',
            btn_icon='actions',
            menu_class='btn-group pull-right')

        return DIV(tpac_menu, _class='pull-right')


    def get_not_verified(self, formatted=False):
        """
        All classes not
        :return: gluon.dal.rows or html table
        """
        return self.get_rows(
            status='not_verified',
            formatted=formatted
        )


    def get_verified(self, formatted=False):
        """
        All classes verified
        :return: gluon.dal.rows or html table
        """
        return self.get_rows(
            status='verified',
            formatted=formatted
        )


    def get_processed(self, formatted=False):
        """
        All processed classes
        :param formatted: Bool
        :return: gluon.dal.rows or html table
        """
        return self.get_rows(
            status='processed',
            formatted=formatted
        )


    def process_verified(self):
        """
        Create credit invoices for verified classes
        :return:
        """
        from os_invoice import Invoice

        T = current.T
        db = current.db

        # Sort verified classes by teacher
        rows = self.get_rows(
            status='verified',
            sorting='teacher',
            formatted=False
        )

        previous_teacher = None
        current_teacher = None
        processed = 0
        invoices_created = 0
        # For each teacher, create credit invoice and add all verified classes
        for i, row in enumerate(rows):
            print i
            teID = row.teachers_payment_attendance_classes.auth_teacher_id
            if i == 0 or not previous_teacher == teID:
                current_teacher = teID

                igpt = db.invoices_groups_product_types(ProductType='teacher_payments')
                iID = db.invoices.insert(
                    invoices_groups_id=igpt.invoices_groups_id,
                    TeacherPayment=True,
                    Description=T('Classes'),
                    Status='sent'
                )

                invoice = Invoice(iID)
                invoice.link_to_customer(teID)

                invoices_created += 1

            invoice.item_add_teacher_class_attendance_credit_payment(
                row.teachers_payment_attendance_classes.id
            )

            previous_teacher = current_teacher
            processed += 1



        # Calculate total

        return processed

