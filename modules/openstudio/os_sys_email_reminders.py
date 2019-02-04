# -*- coding: utf-8 -*-

from gluon import *


class SysEmailReminders:
    def __init__(self, reminder=None):
        self.reminder=reminder


    def list(self):
        """
        :return: list of reminders
        """
        db = current.db

        query = (db.sys_email_reminders.id > 0)

        if self.reminder:
            query &= (db.sys_email_reminders.Reminder == self.reminder)

        return db(query).select(db.sys_email_reminders.ALL)


    def list_formatted(self):
        """

        :return: HTML table of reminders
        """
        T = current.T

        rows = self.list()

        if not len(rows):
            return T("No reminders configured")


        header = THEAD(TR(
            TH('Reminder'),
            TH()
        ))
        table = TABLE(header, _class='table table-striped table-hover')

        for row in rows:
            table.append(TR(
                TD(T("Send email %s days before class date" % row.Days)),
                TD()
            ))

        return table


