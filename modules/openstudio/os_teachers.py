# -*- coding: utf-8 -*-
"""
    This file holds OpenStudio Invoices class
"""

from gluon import *
import datetime

class Teachers:
    """
        This class holds functions related to multiple teachers
    """
    def get_teacher_ids(self):
        """
        :return: gluon.dal.rows containing db.auth_user.id where teacher == True
        """
        db = current.globalenv['db']

        query = (db.auth_user.trashed == False) & \
                (db.auth_user.teacher == True)

        return db(query).select(db.auth_user.id)


    def get_teachers_list_classes_in_month(self, year, month):
        """
        :param year: int
        :param month: int
        :return: dict(teacher_id=[classes])
        """
        from openstudio import ClassSchedule
        from general_helpers import get_last_day_month

        ids = self.get_teacher_ids()

        start_date = datetime.date(year, month, 1)
        last_day = get_last_day_month(start_date)

        data = {}

        for teID in ids:
            teID = int(teID)
            data[teID] = {}
            data[teID]['classes'] = {}
            data[teID]['classes_count'] = 0
            for each_day in range(1, last_day.day + 1):
                # list days
                day = datetime.date(year, month, each_day)
                weekday = day.isoweekday()

                class_schedule = ClassSchedule(
                    date=day,
                    filter_id_teacher=int(teID)
                )

                rows = class_schedule.get_day_rows()

                data[teID]['classes'][day] = rows
                data[teID]['classes_count'] += len(rows)

        return data
