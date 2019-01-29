# -*- coding: utf-8 -*-

import datetime

from gluon import *

class ClassesOTCSubAvailable:
    def __init__(self, cotcsaID):
        db = current.db

        self.id = cotcsaID
        self.row = db.define_classes_otc_sub_avail(cotcsaID)

    def accept(self):
        """
        Set status to accepted and decline all other offers for this class
        :return: None
        """
        db = current.db

        # Accept this offer
        self.row.Accepted = True
        self.row.update_record()

        # Set teacher as sub
        cotc = db.classes_otc(self.row.classes_otc_id)
        cotc.auth_teacher_id = self.row.auth_teacher_id
        cotc.update_record()

        # Reject all others
        query = (db.classes_otc_sub_avail.classes_otc_id == self.row.classes_otc_id) & \
                (db.classes_otc_sub_avail.id != cotcsaID)
        db(query).update(Accepted = False)

        # Set status to normal for class otc (Remove "open" status)
        db.classes_otc[self.row.classes_otc_id] = dict(Status = None)


    def decline(self):
        """
        Set status to declined
        :return: None
        """
        self.row.Accepted = False
        self.row.update_record()
