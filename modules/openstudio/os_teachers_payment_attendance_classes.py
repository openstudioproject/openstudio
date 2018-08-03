# -*- coding: utf-8 -*-

import datetime

from gluon import *


class TeachersPaymentAttendanceClasses:
    """
        Class that gathers useful functions for db.teachers_payments_attendance
    """
    def get_rows(self, status='not_verified', formatted=False):
        db = current.db

        left = [
            db.classes.on(
                db.teachers_payment_attendance_classes.classes_id ==
                db.classes.id
            )
        ]

        query = (db.teachers_payment_attendance_classes.Status == status)
        rows = db(query).select(
            db.teachers_payment_attendance_classes.ALL,
            db.classes.ALL,
            left=left
        )

        if not formatted:
            return rows
        else:
            return self.rows_to_table(rows)


    def rows_to_table(self, rows):
        """
        turn rows object into an html table
        :param rows: gluon.dal.rows with all fields of db.teachers_payment_attendance_classes
        and db.classes
        :return: html table
        """
        T = current.T

        header = THEAD(TR(
            TH(T("Date")),
            TH(T("Time")),
            TH(T("Location")),
            TH(T("Class type")),
            TH(T("Teacher")),
            TH(T("Status")),
            TH() # Actions
        ))

        table = TABLE(header, _class="table table-striped table-hover")

        for i, row in enumerate(rows):
            repr_row = list(rows[i:i + 1].render())[0]

            tr = TR(
                TD(repr_row.teachers_payment_attendance_classes.ClassDate),
                TD(repr_row.classes.Starttime),
                TD(repr_row.classes.school_locations_id),
                TD(repr_row.classes.school_classtypes_id),
                TD(repr_row.teachers_payment_attendance_classes.auth_teacher_id, BR(),
                   repr_row.teachers_payment_attendance_classes.auth_teacher_id2),
                TD(repr_row.teachers_payment_attendance_classes.Status),
                TD()
            )

            table.append(tr)

        return table


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


