# -*- coding: utf-8 -*-

import datetime

from gluon import *

class ClassesOTCSubAvailables:
    def list_formatted(self, cotcID):
        """

        :return: HTML table of available sub teachers
        """
        from os_gui import OsGui

        T = current.T
        db = current.db
        os_gui = OsGui()

        table = TABLE(_class='table table-hover')

        table.append(THEAD(TR(
            # TH(),
            TH(T('Date')),
            TH(T('Start')),
            TH(T('Location')),
            TH(T('Class Type')),
            TH(T('Sub teacher')),
            TH(),  # actions))
        )))

        left = [
            db.classes_otc.on(
                db.classes_otc_sub_avail.classes_otc_id == db.classes_otc.id
            ),
            db.classes.on(
                db.classes_otc.classes_id == db.classes.id
            )
        ]

        query = (db.classes_otc_sub_avail.classes_otc_id == cotcID)

        rows = db(query).select(
            db.classes_otc_sub_avail.ALL,
            db.classes_otc.ALL,
            db.classes.ALL,
            left=left,
            orderby=db.classes_otc.ClassDate | db.classes_otc.Starttime
        )

        for i, row in enumerate(rows):
            repr_row = list(rows[i:i + 1].render())[0]

            if row.classes_otc_sub_avail.Accepted == True:
                status = os_gui.get_label('success', T("Accepted"))
            elif row.classes_otc_sub_avail.Accepted == False:
                status = os_gui.get_label('danger', T("Declined"))
            else:
                status = os_gui.get_label('primary', T("Pending"))
            button = os_gui.get_button('ok_notext',
                                       URL('sub_avail_accept',
                                           vars={
                                               'cotcsaID': row.classes_otc_sub_avail.id
                                           }),
                                       title='Accept', _class='pull-right', btn_class='btn-success')

            button += os_gui.get_button('cancel_notext',
                                        URL('sub_avail_decline',
                                            vars={
                                                'cotcsaID': row.classes_otc_sub_avail.id}),
                                        title='Decline', _class='pull-right', btn_class='btn-danger')

            tr = TR(
                TD(repr_row.classes_otc.ClassDate),
                TD(repr_row.classes.school_locations_id),
                TD(repr_row.classes.Starttime),
                TD(repr_row.classes.school_classtypes_id),
                TD(repr_row.classes_otc_sub_avail.auth_teacher_id),
                TD(status),
                TD(button)
            )

            table.append(tr)

        return table