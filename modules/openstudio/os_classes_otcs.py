# -*- coding: utf-8 -*-


import datetime

from gluon import *


class ClassesOTCs:
    def get_sub_teacher_rows(self,
                             date_from,
                             date_until=None,
                             school_classtypes_ids=None,
                             only_open=False):
        """
        Return rows of open classes

        :param date_from: datetime.date
        :param date_until: datetime.date
        :param school_classtypes_id: db.school_classtypes.id
        :return: gluon.dal.rows
        """
        db = current.db


        where_date_until = ''
        if date_until:
            where_date_until = " AND cotc.ClassDate <= '{date_until}'".format(
                date_until=date_until
            )

        where_classtype = ''
        if school_classtypes_ids:
            unicode_ids = [str(id) for id in school_classtypes_ids]
            where_classtype = """ 
                AND (CASE WHEN cotc.school_classtypes_id IS NOT NULL
				          THEN cotc.school_classtypes_id
                          ELSE cla.school_classtypes_id
                          END) IN({ctIDs})""".format(
                ctIDs = ",".join(unicode_ids))

        where_only_open = " AND (cotc.Status = 'open' OR cotc.auth_teacher_id IS NOT NULL) "
        if only_open:
            where_only_open = " AND (cotc.Status = 'open') "

        fields = [
            db.classes_otc.id,
            db.classes_otc.ClassDate,
            db.classes_otc.Status,
            db.classes_otc.auth_teacher_id,
            db.classes_otc.CountSubsAvailable,
            db.classes.id,
            db.classes.school_locations_id,
            db.classes.school_classtypes_id,
            db.classes.Starttime,
            db.classes.Endtime
        ]

        query = """
        SELECT cotc.id,
               cotc.ClassDate,
               cotc.Status,
               cotc.auth_teacher_id,
               COUNT(cotcsa.classes_otc_id),
               cla.id,
               CASE WHEN cotc.school_locations_id IS NOT NULL
                    THEN cotc.school_locations_id
                    ELSE cla.school_locations_id
                    END AS school_locations_id,
               CASE WHEN cotc.school_classtypes_id IS NOT NULL
                    THEN cotc.school_classtypes_id
                    ELSE cla.school_classtypes_id
                    END AS school_classtypes_id,
               CASE WHEN cotc.Starttime IS NOT NULL
                    THEN cotc.Starttime
                    ELSE cla.Starttime
                    END AS Starttime,
               CASE WHEN cotc.Endtime IS NOT NULL
                    THEN cotc.Endtime
                    ELSE cla.Endtime
                    END AS Endtime
        FROM classes_otc cotc
        LEFT JOIN classes cla ON cla.id = cotc.classes_id
        LEFT JOIN classes_otc_sub_avail cotcsa ON cotcsa.classes_otc_id = cotc.id                          
        WHERE cotc.ClassDate >= '{date_from}' 
            {where_date_until}
            {where_classtype}
            {where_only_open}
        GROUP BY cotc.id
        ORDER BY cotc.ClassDate, Starttime
        """.format(date_from=date_from,
                   where_date_until=where_date_until,
                   where_classtype=where_classtype,
                   where_only_open=where_only_open)

        rows = db.executesql(query, fields=fields)

        return rows