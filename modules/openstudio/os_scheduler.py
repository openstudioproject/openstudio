# -*- coding: utf-8 -*-

import datetime

from gluon import *


class OsScheduler:
    def set_tasks(self):
        """
            Queue all tasks here
            Call during setup & migration
        """
        scheduler = current.globalenv['scheduler']

        today = datetime.date.today()
        start_time = datetime.datetime(today.year,
                                       today.month,
                                       today.day,
                                       00,
                                       01)  # Do stuff at 1 minute past midnight

        # clean up first
        self._remove_tasks()
        # add all tasks
        scheduler.queue_task('daily',
                             start_time=start_time,
                             timeout=1800, # Run for max half an hour
                             prevent_drift=True,
                             period=24*60*60, # once a day
                             repeats=0, # Every day
                             )

    def _remove_tasks(self):
        """
            Removes all scheduled tasks
        """
        db = current.db

        query = (db.scheduler_task.id > 0)
        db(query).delete()
        
        