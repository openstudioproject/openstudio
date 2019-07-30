# -*- coding: utf-8 -*-

import datetime

from gluon import *


class ClassesReservation:
    """
    This class collects functions for a class reservation
    """
    def __init__(self, clrID):
        db = current.db

        self.row = db.classes_reservation(clrID)


    def get_classes(self, date_from, date_until=None, respect_booking_open=True):
        """
        :param date_from: datetime.date
        :param date_until: datetime.date
        :return: [] Return list of upcoming classes
        """
        import calendar

        from .os_attendance_helper import AttendanceHelper
        from .os_class_schedule import ClassSchedule
        from .os_classes_reservations import ClassesReservations


        db = current.db
        TODAY_LOCAL = current.TODAY_LOCAL
        ah = AttendanceHelper()

        data = []
        date = date_from

        if date_until is None:
            year = TODAY_LOCAL.year
            month = TODAY_LOCAL.month + 1

            if month == 13:
                month = 1
                year = TODAY_LOCAL.year + 1

            date_until =  datetime.date(
                year,
                month,
                calendar.monthrange(
                    year,
                    month,
                    )[1]
                ) # Last day of next month from today (local time)

        while date <= date_until:
            cs = ClassSchedule(date)
            classes = cs.get_day_list()

            for cls in classes:
                if ( cls['Cancelled']
                     or cls['Holiday']
                     or not cls['ClassesID'] == self.row.classes_id
                     or (respect_booking_open and cls['BookingOpen'] and cls['BookingOpen'] > date)
                    ):
                    # Class is cancelled, in a holiday, not the class we're looking for
                    # or not yet bookable -> nothing to do
                    continue

                attending = []
                rows = ah.get_attendance_rows(cls['ClassesID'], date)
                for row in rows:
                    if row.classes_attendance.BookingStatus == 'booked' or \
                       row.classes_attendance.BookingStatus == 'attending':
                        attending.append(row.auth_user.id)

                # add customer to list in case not already attending
                if not self.row.auth_customer_id in attending:
                    value = {'clsID':cls['ClassesID'],
                             'date':date}
                    data.append(value)

            date += datetime.timedelta(days=1)

        return data


    def book_classes(self, csID, date_from, date_until=None):
        """
        :param csID: db.customers_subscriptions.id
        :param date_from: datetime.date
        :param date_until: datetime.date
        :return: Integer - number of classes booked
        """
        from .os_attendance_helper import AttendanceHelper
        from .os_customer import Customer
        from .os_customer_subscription import CustomerSubscription


        # Check subscription credits, if none, don't do anything
        credits = 0
        customer = Customer(self.row.auth_customer_id)

        cs = CustomerSubscription(csID)
        credits += cs.get_credits_balance()

        # Get list of classes for customer in a given month, based on reservations
        upcoming_classes = self.get_classes(date_from, date_until)
        ah = AttendanceHelper()
        classes_booked = 0
        while credits > 0 and len(upcoming_classes):
            # Sign in to a class
            ##
            # remove this reservation from the list, as we have just booked it, so it won't be booked again using
            # another subscription
            ##
            cls = upcoming_classes.pop(0) # always get the first in the list, we pop all classes already booked
            ah.attendance_sign_in_subscription(
                self.row.auth_customer_id,
                cls['clsID'],
                cs.cs.id,
                cls['date']
            )

            classes_booked += 1

            # Subtract one credit from current balance in this object (self.add_credists_balance)
            credits -= 1

        return classes_booked


    def remove_attendance_booked_classes(self, cancel_from):
        """
        This function is used to cancel all classes after a given date for
        a reservation. Used when setting an end date for a reservation or
        deleting a reservation

        :param cancel_from: datetime.date (usually TODAY_LOCAL)
        :return: None
        """
        from .os_cache_manager import OsCacheManager

        T = current.T
        db = current.db

        # Find all booked classes
        attendance_deleted = 0
        if self.row.customers_subscriptions_id:
            query = (db.classes_attendance.classes_id == self.row.classes_id) & \
                    (db.classes_attendance.auth_customer_id == self.row.auth_customer_id) & \
                    (db.classes_attendance.customers_subscriptions_id == self.row.customers_subscriptions_id) & \
                    (db.classes_attendance.ClassDate > cancel_from)

            attendance_deleted = db(query).count()
            db(query).delete()

            # Clear cache
            ocm = OsCacheManager()
            ocm.clear_customers_subscriptions(self.row.auth_customer_id)
            ocm.clear_classschedule_api()

        return attendance_deleted
