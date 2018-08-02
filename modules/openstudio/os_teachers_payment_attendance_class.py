# -*- coding: utf-8 -*-

import datetime

from gluon import *


class TeachersPaymentAttendanceClass:
    """
        Class that gathers useful functions for db.teachers_payments_attendance
    """
    def __init__(self, tpacID):
        db = current.db

        self.tpacID = tpacID
        self.row = db.teachers_payment_attendance_class(tpacID)

        
