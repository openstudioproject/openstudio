# -*- coding: utf-8 -*-

from gluon import *
import calendar
import datetime


class SchoolSubscription:
    """
        Class that contains functions for school subscriptions
    """
    def __init__(self, ssuID, set_db_info=False):
        """
            Class init function which sets ssuID
        """
        db = current.db

        self.ssuID = ssuID

        if set_db_info:
            self._set_dbinfo()


    def _set_dbinfo(self):
        """
            Gets information about the subscription from db and adds it
            to the object
        """
        db = current.db

        row = db.school_subscriptions(self.ssuID)

        self.Name = row.Name
        self.MinDuration = row.MinDuration
        self.Classes = row.Classes
        self.SubscriptionUnit = row.SubscriptionUnit
        self.Archived = row.Archived
        self.Terms = row.Terms
        self.school_memberships_id = row.school_memberships_id
        self.Unlimited = row.Unlimited
        self.Description = row.Description
        self.RegistrationFee = row.RegistrationFee


    def get_glaccount_on_date(self, date):
        """
        Returns glaccount from db.school_subscriptions_price on date
        :param date: datetime.date
        :return: string - glaccount
        """
        db = current.db

        glaccount = ''

        query = (db.school_subscriptions_price.school_subscriptions_id ==
                 self.ssuID) & \
                (db.school_subscriptions_price.Startdate <= date) & \
                ((db.school_subscriptions_price.Enddate >= date) |
                 (db.school_subscriptions_price.Enddate == None))

        rows = db(query).select(db.school_subscriptions_price.accounting_glaccounts_id,
                                orderby=db.school_subscriptions_price.Startdate)

        if len(rows):
            row = rows.first()
            glaccount = row.accounting_glaccounts_id

        return glaccount


    def get_costcenter_on_date(self, date):
        """
        Returns glaccount from db.school_subscriptions_price on date
        :param date: datetime.date
        :return: string - glaccount
        """
        db = current.db

        glaccount = ''

        query = (db.school_subscriptions_price.school_subscriptions_id ==
                 self.ssuID) & \
                (db.school_subscriptions_price.Startdate <= date) & \
                ((db.school_subscriptions_price.Enddate >= date) |
                 (db.school_subscriptions_price.Enddate == None))

        rows = db(query).select(db.school_subscriptions_price.accounting_costcenters_id,
                                orderby=db.school_subscriptions_price.Startdate)

        if len(rows):
            row = rows.first()
            glaccount = row.accounting_costcenters_id

        return glaccount


    def get_price_on_date(self, date, formatted=True):
        """
            Returns the price for a subscription on a given date
        """
        from decimal import Decimal, ROUND_HALF_UP

        db = current.db

        price = ''
        query = (db.school_subscriptions_price.school_subscriptions_id ==
                 self.ssuID) & \
                (db.school_subscriptions_price.Startdate <= date) & \
                ((db.school_subscriptions_price.Enddate >= date) |
                 (db.school_subscriptions_price.Enddate == None))

        rows = db(query).select(db.school_subscriptions_price.ALL,
                                orderby=db.school_subscriptions_price.Startdate)
        if len(rows):
            if formatted:
                repr_row = list(rows[0:1].render())[0] # first row
                price = repr_row.Price
            else:
                row = rows.first()
                price = row.Price
                price = price.quantize(Decimal('.01'), rounding=ROUND_HALF_UP)

        if not price:
            price = 0

        return price


    def get_price_today_display(self, formatted=False):
        """
        Use this function to display subscription price to customers
        """
        from decimal import Decimal, ROUND_HALF_UP
        from .tools import OsTools
        from general_helpers import get_last_day_month

        db = current.db
        os_tools = OsTools()
        CURRSYM = current.globalenv['CURRSYM']
        TODAY_LOCAL = current.TODAY_LOCAL

        price_today = self.get_price_today(formatted=False)

        subscription_first_invoice_two_terms = os_tools.get_sys_property(
            'subscription_first_invoice_two_terms')

        if subscription_first_invoice_two_terms == "on":
            first_next_month = get_last_day_month(TODAY_LOCAL) + datetime.timedelta(days=1)
            price_today += self.get_price_on_date(first_next_month, formatted = False)

        price_display = Decimal(price_today).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)

        if formatted:
            return SPAN(CURRSYM, ' ', str(price_display))
        else:
            return price_display


    def get_price_today(self, formatted=True):
        """
        Return calculated price for a subscription, assuming TODAY_LOCAL
        is the startdate
        """
        from decimal import Decimal, ROUND_HALF_UP
        from general_helpers import get_last_day_month
        db = current.db
        TODAY_LOCAL = current.TODAY_LOCAL
        CURRSYM = current.globalenv['CURRSYM']

        price = self.get_price_on_date(TODAY_LOCAL, False)

        period_start = TODAY_LOCAL
        period_end = get_last_day_month(period_start)

        delta = period_end - period_start
        days = delta.days + 1
        total_days = period_end.day
        price = Decimal(float(days) / float(total_days) * float(price))
        price = price.quantize(Decimal('.01'), rounding=ROUND_HALF_UP)

        if formatted:
            return SPAN(CURRSYM, ' ', format(price, '.2f'))
        else:
            return price


    def get_tax_rates_on_date(self, date):
        """
            Returns tax rates on date
        """
        db = current.db

        left = [ db.tax_rates.on(db.school_subscriptions_price.tax_rates_id ==
                                 db.tax_rates.id) ]

        query = (db.school_subscriptions_price.school_subscriptions_id ==
                 self.ssuID) & \
                (db.school_subscriptions_price.Startdate <= date) & \
                ((db.school_subscriptions_price.Enddate >= date) |
                 (db.school_subscriptions_price.Enddate == None))

        rows = db(query).select(db.school_subscriptions.ALL,
                                db.school_subscriptions_price.ALL,
                                db.tax_rates.ALL,
                                left=left,
                                orderby=db.school_subscriptions_price.Startdate)

        if rows:
            row = rows.first()
        else:
            row = None

        return row


    def get_name(self):
        """
            Returns the name of the subscription
        """
        self._set_dbinfo()

        return self.Name


    def get_classes_formatted(self):
        """
            SPAN object containing
        """
        T = current.T
        self._set_dbinfo()

        classes_text = T('classes')
        if self.Classes == 1:
            classes_text = T('class')

        classes = ''
        if self.SubscriptionUnit == 'week':
            classes = SPAN(str(self.Classes) + ' ' + classes_text + ' ' + T('a') + ' ' + T('week'))
        elif self.SubscriptionUnit == 'month':
            classes = SPAN(str(self.Classes) + ' ' + classes_text + ' ' + T('a') + ' ' + T('month'))

        return classes


    def _sell_to_customer_get_min_end_date(self, date_start):
        """

        :return:
        """
        def add_months(sourcedate, months):
            month = sourcedate.month - 1 + months
            year = int(sourcedate.year + month / 12)
            month = month % 12 + 1
            last_day_new = calendar.monthrange(year, month)[1]
            day = min(sourcedate.day, last_day_new)

            ret_val = datetime.date(year, month, day)

            last_day_source = calendar.monthrange(sourcedate.year,
                                                  sourcedate.month)[1]

            if sourcedate.day == last_day_source and last_day_source > last_day_new:
                return ret_val
            else:
                delta = datetime.timedelta(days=1)
                return ret_val - delta


        self._set_dbinfo()
        return add_months(date_start, self.MinDuration)


    def sell_to_customer(self, auth_user_id, date_start, payment_methods_id=3, note=None, origin="BACKEND"):
        """
            :param auth_user_id: Sell subscription to customer
        """
        from .os_cache_manager import OsCacheManager
        db = current.db
        ocm = OsCacheManager()

        print('call sell to customer')

        csID = db.customers_subscriptions.insert(
            auth_customer_id = auth_user_id,
            school_subscriptions_id = self.ssuID,
            Startdate = date_start,
            MinEnddate = self._sell_to_customer_get_min_end_date(date_start),
            Note = note,
            payment_methods_id = payment_methods_id,
            Origin = origin
        )

        ocm.clear_customers_subscriptions(auth_user_id)

        return csID