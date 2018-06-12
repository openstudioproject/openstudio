# -*- coding: utf-8 -*-

from gluon import *


class ClassesReservations:
    """
        This class collects functions classes_reservation that can return or modify multple records at once
    """
    def get_recurring_reservations_on_date(self, date, by_class=False):
        """
        :param date: datetime.date
        :return: rows of all recurring reservations on a given date
        """
        db = current.db

        query = (db.classes_reservation.Startdate <= date) & \
                ((db.classes_reservation.Enddate >= date) |
                 (db.classes_reservation.Enddate == None)) & \
                (db.classes_reservation.ResType == 'recurring')

        return db(query).select(db.classes_reservation.ALL)