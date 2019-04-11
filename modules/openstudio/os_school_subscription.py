# -*- coding: utf-8 -*-

from gluon import *


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

        if not price:
            price = 0

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
            classes = SPAN(unicode(self.Classes) + ' ' + classes_text + ' ' + T('a') + ' ' + T('week'))
        elif self.SubscriptionUnit == 'month':
            classes = SPAN(unicode(self.Classes) + ' ' + classes_text + ' ' + T('a') + ' ' + T('month'))

        return classes


    def sell_to_customer(self, auth_user_id, date_start, payment_methods_id=3, note=None):
        """
            :param auth_user_id: Sell subscription to customer
        """
        from os_cache_manager import OsCacheManager
        db = current.db
        ocm = OsCacheManager()

        csID = db.customers_subscriptions.insert(
            auth_customer_id = auth_user_id,
            school_subscriptions_id = self.ssuID,
            Startdate = date_start,
            Note = note,
            payment_methods_id = payment_methods_id
        )

        ocm.clear_customers_subscriptions(auth_user_id)

        return csID