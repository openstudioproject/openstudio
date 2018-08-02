# -*- coding: utf-8 -*-

import datetime

from gluon import *


class TeachersPaymentAttendanceClasses:
    """
        Class that gathers useful functions for db.teachers_payments_attendance
    """
    def get_not_processed(self):
        """
        All classes not
        :return: gluon.dal.rows
        """
        db = current.db

        left = [
            db.classes.on(
                db.teachers_payment_attendance_classes.classes_id ==
                db.classes.id
            )
        ]

        query = (db.teachers_payment_attendance_classes.Status != 'processed')
        rows = db(query).select(
            db.teachers_payment_attendance_classes.ALL,
            db.classes.ALL,
            left=left
        )

        return rows


    def get_not_processed_formatted(self):
        """

        :return:
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

        rows = self.get_not_processed()
        print rows

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
