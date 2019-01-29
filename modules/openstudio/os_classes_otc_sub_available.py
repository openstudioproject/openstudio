# -*- coding: utf-8 -*-

import datetime

from gluon import *

class ClassesOTCSubAvailable:
    def __init__(self, cotcsaID):
        db = current.db

        self.id = cotcsaID
        self.row = db.classes_otc_sub_avail(cotcsaID)

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
                (db.classes_otc_sub_avail.id != self.id)
        db(query).update(Accepted = False)

        # Set status to normal for class otc (Remove "open" status)
        db.classes_otc[self.row.classes_otc_id] = dict(Status = None)

        # Notify teachers offering to sub this class
        self._accept_send_mail()


    def _accept_send_mail(self):
        """
        Notify all teachers offering to sub class that a substitute has been found
        :return:
        """
        print 'send mail'


    def decline(self):
        """
        Set status to declined
        :return: None
        """
        self.row.Accepted = False
        self.row.update_record()

        self._decline_send_mail()


    def _decline_send_mail(self):
        """
        Notify teacher that he/she won't be subbing this class
        :return:
        """
        from os_mail import OsMail
        from os_teacher import Teacher

        teacher = Teacher(self.row.auth_teacher_id)

        osmail = OsMail()
        # msgID = osmail.render_email_template(
        #     'teacher_reject_sub_request',
        #
        # )
        msgID = db.messages.insert(
            msg_subject='subject test email',
            msg_content='Test Content email'
        )

        osmail.send(msgID, teacher.id)

        print 'send mail'