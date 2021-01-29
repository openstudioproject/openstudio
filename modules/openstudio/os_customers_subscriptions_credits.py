# -*- coding: utf-8 -*-

import datetime

from gluon import *

from general_helpers import get_last_day_month


class CustomersSubscriptionsCredits:
    """
        Class to group functions related to operations on multiple customer subscriptions credits records
    """
    def __init__(self):
        """
            Init functions
        """
        self.add_credits_balance = {} # Dictionary with customerID as key to hold about of credits added for a customer


    def _get_customers_list_classes_recurring_reservations(self, year, month):
        """
            Get list of classes a customer has a reservation for in a selected month
        """
        from .os_attendance_helper import AttendanceHelper
        from .os_class_schedule import ClassSchedule
        from .os_classes_reservations import ClassesReservations
        db = current.db

        ah = AttendanceHelper()
        crh = ClassesReservations()
        first_day = datetime.date(year, month, 1)
        last_day = get_last_day_month(first_day)

        data = {}

        date = first_day
        while date <= last_day:
            # get list of classes on date
            #print date

            cs = ClassSchedule(date)
            #print 'getting classes'
            classes = cs.get_day_list()
            reservations = crh.get_recurring_reservations_on_date(date)
            for cls in classes:
                if cls['Cancelled'] or cls['Holiday']:
                    # Class is cancelled or in a holiday, nothing to do
                    continue

                # Get list of bookings with status "attending" or "booked"
                #print 'getting attendance for class'

                attending = []
                rows = ah.get_attendance_rows(cls['ClassesID'], date)
                for row in rows:
                    # print row
                    if row.classes_attendance.BookingStatus == 'booked' or \
                       row.classes_attendance.BookingStatus == 'attending':
                        attending.append(row.auth_user.id)

                # if classes_id found on both lists, add class to reservations list for that customer
                for res in reservations:
                    if res.classes_id == cls['ClassesID']:
                        # add customer to list in case not already attending
                        if not res.auth_customer_id in attending:
                            #print res.auth_customer_id


                            value = {'clsID':cls['ClassesID'],
                                     'date':date}

                            # print value
                            # print '###############'

                            try:
                                data[res.auth_customer_id].append(value)
                            except KeyError:
                                data[res.auth_customer_id] = [value]

            date += datetime.timedelta(days=1)

        return data


    def refund_credits_in_period(self, query):
        """
            :param query: query containing constraints for period and classes from classes_attendance
            :return: None
        """
        db = current.db
        rows = db(query).select(db.classes_attendance.id)
        att_ids = []
        for row in rows:
            att_ids.append(row.id)

        # delete rows from customers_subscriptions_credits
        query = (db.customers_subscriptions_credits.classes_attendance_id.belongs(att_ids))
        db(query).delete()


    def add_subscription_credits_month(self,
                                       csID,
                                       cuID,
                                       year,
                                       month,
                                       p_start,
                                       p_end,
                                       classes,
                                       subscription_unit,
                                       batch_add=True,
                                       book_classes=True):
        """
            Insert subscription credits and clear cache for customer subscription
            :param csID: db.customers_subscriptions.id
            :param cuID: db.auth_user.id
            :param year: int
            :param month: int
            :param p_start: datetime.date (Period start)
            :param p_end: datetime.date (Period end)
            :param classes: int
            :param subscription_unit: string either 'week' or 'month'
            :return: None
        """
        from .os_attendance_helper import AttendanceHelper
        from .os_customer_subscription import CustomerSubscription

        T = current.T
        db = current.db
        now = current.NOW_LOCAL
        cache_clear_customers_subscriptions = current.globalenv['cache_clear_customers_subscriptions']
        TODAY_LOCAL = current.TODAY_LOCAL

        first_day = datetime.date(year, month, 1)
        last_day = get_last_day_month(first_day)

        t_days = (last_day - first_day) + datetime.timedelta(days=1)  # Total days (Add 1, when subsctraced it's one day less)
        p_days = (p_end - p_start) + datetime.timedelta(days=1)  # Period days

        percent = float(p_days.days) / float(t_days.days)
        if subscription_unit == 'month':
            credits = round(classes * percent, 1)
        else:
            weeks_in_month = round(t_days.days / float(7), 1)
            credits = round((weeks_in_month * (classes or 0)) * percent, 1)

        mutation_datetime = now
        # Check if credits have already been added for this subscription.
        query = (db.customers_subscriptions_credits.MutationType == "add") & \
                (db.customers_subscriptions_credits.customers_subscriptions_id == csID)
        if not db(query).count():
            # No credits found yet, so add on the start of the subscription
            mutation_datetime = p_start

        db.customers_subscriptions_credits.insert(
            customers_subscriptions_id=csID,
            MutationDateTime=mutation_datetime,
            MutationType='add',
            MutationAmount=credits,
            Description=T('Credits') + ' ' + first_day.strftime('%B %Y'),
            SubscriptionYear=year,
            SubscriptionMonth=month
        )

        if batch_add:
            try:
                self.add_credits_balance[cuID] += credits
            except KeyError:
                self.add_credits_balance[cuID] = credits
        else:
            cs = CustomerSubscription(csID)
            self.add_credits_balance[cuID] = cs.get_credits_balance()

        if book_classes:
            # Get list of classes for customer in a given month, based on reservations
            classes_this_month = self.add_credits_reservations.get(cuID, False)
            ah = AttendanceHelper()
            if classes_this_month:
                # Book classess
                while len(self.add_credits_reservations.get(cuID)) > 0 and self.add_credits_balance[cuID] > 0:
                    # Sign in to a class
                    ##
                    # remove this reservation from the list, as we have just booked it, so it won't be booked again using
                    # another subscription
                    ##
                    reservation = self.add_credits_reservations[cuID].pop(0) # always get the first in the list, we pop all classes already booked
                    ah.attendance_sign_in_subscription(cuID, reservation['clsID'], csID, reservation['date'])

                    # Subtract one credit from current balance in this object (self.add_credits_balance)
                    self.add_credits_balance[cuID] -= 1


        # Clear cache
        cache_clear_customers_subscriptions(cuID)


    def add_credits_get_subscription_rows_month(self, year, month):
        """
            return subscription rows for month
        """
        db = current.db

        first_day = datetime.date(year, month, 1)
        last_day = get_last_day_month(first_day)

        fields = [
            db.customers_subscriptions.id,
            db.customers_subscriptions.Startdate,
            db.customers_subscriptions.Enddate,
            db.customers_subscriptions.auth_customer_id,
            db.customers_subscriptions_credits.id,
            db.customers_subscriptions_paused.id,
            db.school_subscriptions.Name,
            db.school_subscriptions.Classes,
            db.school_subscriptions.SubscriptionUnit,
            db.school_subscriptions.Unlimited,
        ]

        query = """
            SELECT cs.id,
                   cs.Startdate,
                   cs.Enddate,
                   cs.auth_customer_id,
                   csc.id, 
                   csp.id, 
                   ssu.Name, 
                   ssu.Classes, 
                   ssu.subscriptionunit, 
                   ssu.unlimited
            FROM customers_subscriptions cs
            LEFT JOIN (	SELECT id, SubscriptionYear, SubscriptionMonth, customers_subscriptions_id
                        FROM customers_subscriptions_credits
                        WHERE MutationType = 'add' AND 
                              SubscriptionYear = '{year}' AND 
                              SubscriptionMonth = '{month}' ) csc
                ON csc.customers_subscriptions_id = cs.id
            LEFT JOIN ( SELECT id, customers_subscriptions_id
                        FROM customers_subscriptions_paused 
                        WHERE startdate <= '{last_day}' AND ENDDATE >= '{first_day}' ) csp
                ON csp.customers_subscriptions_id = cs.id
            LEFT JOIN school_subscriptions ssu
                ON cs.school_subscriptions_id = ssu.id
            WHERE cs.Startdate <= '{last_day}' AND (cs.Enddate >= '{first_day}' OR cs.Enddate IS NULL)
        """.format(year=year,
                   month=month,
                   first_day=first_day,
                   last_day=last_day)

        rows = db.executesql(query, fields=fields)

        return rows


    def add_credits(self, year, month):
        """
            Add subscription credits for month
        """
        from .os_customers import Customers

        T = current.T
        db = current.db

        first_day = datetime.date(year, month, 1)
        last_day = get_last_day_month(first_day)

        # Get list of bookable classes for each customer, based on recurring reservations

        self.add_credits_reservations = self._get_customers_list_classes_recurring_reservations(year, month)
        # Get list of total credits balance for each customer
        customers = Customers()
        self.add_credits_balance = customers.get_credits_balance(first_day, include_reconciliation_classes=True)


        customers_credits_added = 0

        rows = self.add_credits_get_subscription_rows_month(year, month)

        for row in rows:
            # Don't do anything if this subscription already got credits for this month is paused
            # or has no classes or subscription unit defined
            if row.customers_subscriptions_credits.id:
                continue
            if row.customers_subscriptions_paused.id:
                continue
            if row.school_subscriptions.Classes == 0 or row.school_subscriptions.Classes is None:
                continue
            if row.school_subscriptions.SubscriptionUnit is None:
                continue

            # calculate number of credits
            # only add partial credits if startdate != first day, add full credits if startdate < first day
            if row.customers_subscriptions.Startdate <= first_day:
                p_start = first_day
            else:
                p_start = row.customers_subscriptions.Startdate

            if row.customers_subscriptions.Enddate is None or row.customers_subscriptions.Enddate >= last_day:
                p_end = last_day
            else:
                p_end = row.customers_subscriptions.Enddate


            self.add_subscription_credits_month(
                row.customers_subscriptions.id,
                row.customers_subscriptions.auth_customer_id,
                year,
                month,
                p_start,
                p_end,
                row.school_subscriptions.Classes,
                row.school_subscriptions.SubscriptionUnit,
            )

            # Increase counter
            customers_credits_added += 1

        return customers_credits_added or 0
    

    def expire_credits(self, date):
        """
        Check if there are any expired credits, if so, add a subtract mutation with the expired amount
        where the 'Expired' field is set to True

        :param date: datetime.date
        :return: number of subscriptions for which credits were expired
        """
        T = current.T
        db = current.db
        NOW_LOCAL = current.NOW_LOCAL
        web2pytest = current.globalenv['web2pytest']
        request = current.request

        # Create dictionary of expiration for school_subscriptions
        subscriptions_count_expired = 0
        query = (db.school_subscriptions.Archived == False)
        rows = db(query).select(db.school_subscriptions.id,
                                db.school_subscriptions.CreditValidity)

        for row in rows:
            if not row.CreditValidity:
                continue

            # Get list of all active subscriptions
            fields = [
                db.customers_subscriptions.id,
                db.customers_subscriptions.auth_customer_id,
                db.customers_subscriptions.Startdate,
                db.customers_subscriptions.Enddate,
                db.customers_subscriptions.payment_methods_id,
                db.school_subscriptions.id,
                db.school_subscriptions.Name,
                db.customers_subscriptions.CreditsRemaining,
                db.customers_subscriptions.PeriodCreditsAdded,
            ]

            if web2pytest.is_running_under_test(request, request.application):
                # the test environment uses sqlite
                mutation_date_sql = "date('{date}', '-{validity} day')".format(
                    date=date,
                    validity=row.CreditValidity
                )
            else:
                # MySQL format
                mutation_date_sql = "DATE_SUB('{date}', INTERVAL {validity} DAY)".format(
                    date=date,
                    validity=row.CreditValidity
                )

            sql = """SELECT cs.id, 
                            cs.auth_customer_id,
                            cs.Startdate, 
                            cs.Enddate,
                            cs.payment_methods_id,
                            ssu.id,
                            ssu.Name,
                            ( IFNULL((SELECT SUM(csc.MutationAmount)
                               FROM customers_subscriptions_credits csc
                               WHERE csc.customers_subscriptions_id = cs.id AND
                                     csc.MutationType = 'add'), 0) - 
                               IFNULL(( SELECT SUM(csc.MutationAmount)
                               FROM customers_subscriptions_credits csc
                               WHERE csc.customers_subscriptions_id = cs.id AND
                                     csc.MutationType = 'sub'), 0)) AS credits,
                            IFNULL(( SELECT SUM(csc.MutationAmount)
                             FROM customers_subscriptions_credits csc
                             WHERE csc.customers_subscriptions_id = cs.id AND
                                   csc.MutationType = 'add' AND
                                   csc.MutationDateTime >= {mutation_date}), 0) as c_add_in_period
                            FROM customers_subscriptions cs
                            LEFT JOIN 
                            school_subscriptions ssu ON cs.school_subscriptions_id = ssu.id
                            WHERE ssu.id = {ssuID} AND 
                                  (cs.Startdate <= '{date}' AND 
                                  (cs.Enddate >= '{date}' OR cs.Enddate IS NULL))
                            ORDER BY cs.Startdate
                            """.format(date=date, ssuID=row.id, mutation_date=mutation_date_sql)

            cs_rows = db.executesql(sql, fields=fields)

            for row in cs_rows:

                expired_credits = (float(row.customers_subscriptions.CreditsRemaining) -
                                   float(row.customers_subscriptions.PeriodCreditsAdded))

                if expired_credits > 0 and row.customers_subscriptions.CreditsRemaining > 0:
                    db.customers_subscriptions_credits.insert(
                        customers_subscriptions_id = row.customers_subscriptions.id,
                        MutationDateTime = NOW_LOCAL,
                        MutationType = 'sub',
                        MutationAmount = round(expired_credits, 1),
                        Description = T('Credits expiration'),
                        Expiration = True
                    )

                    subscriptions_count_expired += 1

        return subscriptions_count_expired
    