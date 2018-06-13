# -*- coding: utf-8 -*-

from gluon import *


class Shift:
    """
        Class to manage status of a shift
    """
    def __init__(self, shID, date):
        self.date = date
        self.shID = shID


    def _get_sotcID(self):
        """
            :return: db.shifts_otc.id
        """
        db = current.db

        query = (db.shifts_otc.shifts_id == self.shID) & \
                (db.shifts_otc.ShiftDate == self.date)
        rows = db(query).select(db.shifts_otc.id)

        sotcID = None
        if len(rows):
            sotcID = rows.first().id

        return sotcID


    def _set_status(self, status):
        """
            :param status: ['open' or 'cancelled']
            :return: None
        """
        db = current.db
        T = current.T

        sotcID = self.set_status_normal()

        row = db.shifts_otc(sotcID)
        if row:
            row.Status = status
            row.update_record()
        else:
            db.shifts_otc.insert(
                shifts_id = self.shID,
                ShiftDate = self.date,
                Status    = status
            )


    def set_status_normal(self):
        """
            Remove status if found
        """
        db = current.db

        sotcID = self._get_sotcID()

        row = db.shifts_otc(sotcID)
        if row:
            row.Status = None
            row.update_record()

        return sotcID


    def set_status_open(self):
        """
            Change status to open
        """
        self._set_status('open')


    def set_status_cancelled(self):
        """
            Change status to cancelled
        """
        self._set_status('cancelled')
