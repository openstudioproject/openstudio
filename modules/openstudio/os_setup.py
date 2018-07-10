# -*- coding: utf-8 -*-

from gluon import *

class OsSetup:
    def setup(self):
        """
        Run setup
        :return:
        """
        self._setup_sys_notifications()


    def _setup_sys_notifications(self):
        """
        Populate db.sys_notifications with default values
        """
        T = current.T
        db = current.db

        db.sys_notifications.insert(
            Notification="order_created",
            NotificationTitle=T("New order"),
            NotificationTemplate="{order_items}"
        )