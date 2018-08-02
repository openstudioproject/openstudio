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
        rows = self.get_not_processed()

        header = THEAD(TR(
            TH(),
        ))

        table = TABLE()
