# -*- coding: utf-8 -*-

from gluon import *

class CustomerSubscriptions:
    """
        Class that contains functions for customer subscriptions
    """
    def __init__(self, csID):
        """
            Class init function which sets csID
        """
        self.csID = csID

    def get_paused(self, date):
        """
            Returns whether a subscription is paused on provided date
        """
        db = current.db
        DATE_FORMAT = current.globalenv['DATE_FORMAT']

        query = (db.customers_subscriptions_paused.customers_subscriptions_id ==
                 self.csID) & \
                (db.customers_subscriptions_paused.Startdate <= date) & \
                ((db.customers_subscriptions_paused.Enddate >= date) |
                 (db.customers_subscriptions_paused.Enddate == None))
        row = db(query).select(db.customers_subscriptions_paused.ALL).first()
        if row:
            return_value = SPAN(current.T('Paused until'), ' ',
                                row.Enddate.strftime(DATE_FORMAT))
        else:
            return_value = False

        return return_value