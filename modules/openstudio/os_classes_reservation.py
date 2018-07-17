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


    def get_classes(self, date_from, date_until, respect_booking_open=True):
        """
        :param date_from: datetime.date
        :param date_until: datetime.date
        :return: [] Return list of upcoming classes
        """
        from os_attendance_helper import AttendanceHelper
        from os_class_schedule import ClassSchedule
        from os_classes_reservations import ClassesReservations
        db = current.db

        data = []
        date = date_from
        while date <= date_until:
            print date

            cs = ClassSchedule(date)
            classes = cs.get_day_list()

            if ( cls['Cancelled']
                 or cls['Holiday']
                 or not cls['ClassesID'] == self.row.classes_id
                 or (respect_booking_open and cls['BookingOpen'] > date)
                ):
                # Class is cancelled, in a holiday, not the class we're looking for
                # or not yet bookable -> nothing to do
                continue

            attending = []
            rows = ah.get_attendance_rows(cls['ClassesID'], date)
            for row in rows:
                # print row
                if row.classes_attendance.BookingStatus == 'booked' or \
                   row.classes_attendance.BookingStatus == 'attending':
                    attending.append(row.auth_user.id)

            # add customer to list in case not already attending
            if not self.row.auth_customer_id in attending:
                #print res.auth_customer_id
                value = {'clsID':cls['ClassesID'],
                         'date':date}
                data.append(value)

            date += datetime.timedelta(days=1)

        return data


        def book_classes(self, csID, date_from, date_until):
            """
            :param csID: db.customers_subscriptions.id
            :param date_from: datetime.date
            :param date_until: datetime.date
            :return: Integer - number of classes booked
            """
            from os_attendance_helper import AttendanceHelper
            from os_customer_subscription import CustomerSubscription

            # Check subscription credits, if none, don't do anything
            cs = CustomerSubscription(csID)
            credits = cs.get_credits_balance()

            print credits

            # Get list of classes for customer in a given month, based on reservations
            classes_this_month = self.get_classes(date_from, date_until)
            ah = AttendanceHelper()
            if classes_this_month:
                # Book classess
                while credits > 0:
                    # Sign in to a class
                    ##
                    # remove this reservation from the list, as we have just booked it, so it won't be booked again using
                    # another subscriptin
                    ##
                    cls = classes.pop(0) # always get the first in the list, we pop all classes already booked
                    ah.attendance_sign_in_subscription(
                        cuID,
                        cls['clsID'],
                        csID,
                        cls['date']
                    )

                    # Subtract one credit from current balance in this object (self.add_credists_balance)
                    self.acredits -= 1


    # Use the function below as template to get classes in a month for a specific reservation
    #
    # def _get_customers_list_classes_recurring_reservations(self, year, month):
    #     """
    #         Get list of classes a customer has a reservation for in a selected month
    #     """
    #     from os_attendance_helper import AttendanceHelper
    #     from os_class_schedule import ClassSchedule
    #     from os_classes_reservations import ClassesReservations
    #     db = current.db
    #
    #     ah = AttendanceHelper()
    #     crh = ClassesReservations()
    #     first_day = datetime.date(year, month, 1)
    #     last_day = get_last_day_month(first_day)
    #
    #     data = {}
    #
    #     date = first_day
    #     while date <= last_day:
    #         # get list of classes on date
    #         #print date
    #
    #         cs = ClassSchedule(date)
    #         #print 'getting classes'
    #         classes = cs.get_day_list()
    #         reservations = crh.get_recurring_reservations_on_date(date)
    #         for cls in classes:
    #             if cls['Cancelled'] or cls['Holiday']:
    #                 # Class is cancelled or in a holiday, nothing to do
    #                 continue
    #
    #             # Get list of bookings with status "attending" or "booked"
    #             #print 'getting attendance for class'
    #
    #             attending = []
    #             rows = ah.get_attendance_rows(cls['ClassesID'], date)
    #             for row in rows:
    #                 # print row
    #                 if row.classes_attendance.BookingStatus == 'booked' or \
    #                    row.classes_attendance.BookingStatus == 'attending':
    #                     attending.append(row.auth_user.id)
    #
    #             # if classes_id found on both lists, add class to reservations list for that customer
    #             for res in reservations:
    #                 if res.classes_id == cls['ClassesID']:
    #                     # add customer to list in case not already attending
    #                     if not res.auth_customer_id in attending:
    #                         #print res.auth_customer_id
    #
    #
    #                         value = {'clsID':cls['ClassesID'],
    #                                  'date':date}
    #
    #                         # print value
    #                         # print '###############'
    #
    #                         try:
    #                             data[res.auth_customer_id].append(value)
    #                         except KeyError:
    #                             data[res.auth_customer_id] = [value]
    #
    #         date += datetime.timedelta(days=1)
    #
    #     return data