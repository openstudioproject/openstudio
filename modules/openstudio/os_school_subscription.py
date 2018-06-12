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

        self.MembershipRequired = row.MembershipRequired
        self.Name = row.Name
        self.Classes = row.Classes
        self.SubscriptionUnit = row.SubscriptionUnit
        self.Archived = row.Archived
        self.Terms = row.Terms


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
