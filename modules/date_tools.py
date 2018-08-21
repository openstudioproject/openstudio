# -*- coding: utf-8 -*-

import datetime

class DateTools:
    def days_between_dates(self, d1, d2):
        """
        :param d1: datetime.date
        :param d2: datetime.date
        :return: Number of days between dates
        """
        if d1 > d2:
            return False

        delta = d2 - d1

        return delta.days
