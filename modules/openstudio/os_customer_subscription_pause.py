# -*- coding: utf-8 -*-

import datetime

from general_helpers import get_last_day_month

from gluon import *


class CustomerSubscriptionPause:
    """
        Class that contains functions for customer subscription pause
    """
    def __init__(self, cspID):
        """
            Class init function which sets csID
        """
        db = current.db

        self.cspID = cspID
        self.row = db.customers_subscriptions_paused(cspID)


    def get_pause_gte_min_duration(self):
        """
        :return: True if >= min pause length
        """
        from .tools import OsTools

        os_tools = OsTools()
        min_duration = os_tools.get_sys_property('subscription_pauses_min_duration')

        if not min_duration:
            # Return True when min duration is not defined
            return True

        min_duration = int(min_duration)
        delta = self.row.Enddate - self.row.Startdate
        pause_duration = delta.days


        if pause_duration >= min_duration:
            return True
        else:
            return False

