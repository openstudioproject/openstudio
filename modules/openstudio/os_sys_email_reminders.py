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
        from os_gui import OsGui

        T = current.T
        auth = current.auth
        os_gui = OsGui()

        rows = self.list()

        if not len(rows):
            return T("No reminders configured")

        permission = auth.has_membership(group_id='Admins') or \
                     auth.has_permission('delete', 'sys_email_reminders')


        header = THEAD(TR(
            TH('Reminder'),
            TH()
        ))
        table = TABLE(header, _class='table table-striped table-hover')

        for row in rows:
            table.append(TR(
                TD(T("%s Day(s) before class date, email reminder about open class to teacher." % row.Days)),
                TD(self._list_formatted_get_delete_button(row.id, permission, os_gui))
            ))

        return table


    def _list_formatted_get_delete_button(self, serID, permission, os_gui):
        """
        HTML delete button
        :param serID: db.sys_email_reminders.id
        :param permission: Bool
        :return: HTML delete button
        """
        if not permission:
            return ''

        T = current.T

        onclick = "return confirm('" + \
             T("Are you sure you want to delete this reminder?") + ' ' + \
             "');"

        return os_gui.get_button(
            'delete_notext',
            URL('reminder_delete', vars={'serID': serID}),
            onclick=onclick,
            _class='pull-right'
        )
