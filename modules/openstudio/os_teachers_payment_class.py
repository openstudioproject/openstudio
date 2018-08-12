# -*- coding: utf-8 -*-

import datetime

from gluon import *


class TeachersPaymentClass:
    """
        Class that gathers useful functions for db.teachers_payments_attendance
    """
    def __init__(self, tpcID):
        db = current.db

        self.tpcID = tpcID
        self.row = db.teachers_payment_classes(tpcID)


    def verify(self):
        """
        Verify class attendance
        :return:
        """
        from os_class import Class

        auth = current.auth
        NOW_LOCAL = current.NOW_LOCAL

        cls = Class(
            self.row.classes_id,
            self.row.ClassDate
        )

        teachers = cls.get_teachers()

        self.row.auth_teacher_id = teachers['teacher']['id']
        try:
            self.row.auth_teacher_id2 = teachers['teacher2']['id']
        except (KeyError, TypeError):
            pass

        self.row.VerifiedBy = auth.user.id
        self.row.Status = 'verified'
        self.row.VerifiedOn = NOW_LOCAL

        result = self.row.update_record()

        return result


    def set_status(self, status):
        """

        :param status:
        :return:
        """
        self.row.Status = status
        self.row.update_record()


    def set_status_processed(self):
        self.set_status('processed')
