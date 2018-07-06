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
        db = current.db

        # TODO Add message
        db.sys_notifications.insert(
            Notification="order_created",
            NotificationTitle=T("Order created"),
            NotificationMessage="""
            
            """
        )