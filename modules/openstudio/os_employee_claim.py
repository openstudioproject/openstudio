import datetime

from gluon import *


class EmployeeClaim:
    """
        Class that gathers useful functions for db.teachers_payments_attendance
    """
    def __init__(self, ecID):
        db = current.db

        self.ecID = ecID
        self.row = db.employee_claims(ecID)


    def accept(self):
        """
        accept employee claim
        :return:
        """


        auth = current.auth
        NOW_LOCAL = current.NOW_LOCAL


        self.row.VerifiedBy = auth.user.id

        self.row.Status = 'Accepted'
        self.row.VerifiedOn = NOW_LOCAL

        result = self.row.update_record()

        return result


    def reject(self):
        """
        Unverify class attendance
        :return:
        """
        auth= current.auth

        self.row.VerifiedBy = auth.user.id
        self.row.Status = 'Rejected'
        self.row.VerifiedOn = current.NOW_LOCAL

        result = self.row.update_record()

        return result


    def set_status(self, status):
        """

        :param status:
        :return:
        """
        self.row.Status = status
        self.row.update_record()


    # def set_status_processed(self):
    #     self.set_status('processed')
