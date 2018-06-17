# -*- coding: utf-8 -*-

import datetime

from gluon import *


class CustomerMembership:
    """
        Class for customer memberships
    """
    def __init__(self, cmID):
        db = current.db

        self.cmID = cmID
        self.row = db.customers_memberships(self.cmID)
        self.school_membership = db.school_memberships(self.row.school_memberships_id)


    def get_name(self):
        return self.school_membership.Name


    def get_period_enddate(self, startdate):
        """

        :return:
        """
        from openstudio.tools import OsTools

        tools = OsTools()

        enddate = tools.calculate_validity_enddate(
            self.row.Startdate,
            self.school_membership.Validity,
            self.school_membership.ValidityUnit
        )

        return enddate


    def _set_date_id_get_next_id(self, digits=5):
        """
            :return: next_id
        """
        db = current.db

        # Reset numbering when adding first membership of the year
        first_day_year = datetime.date(self.row.Startdate.year, 1, 1)
        last_day_year = datetime.date(self.row.Startdate.year, 12, 31)
        query = (db.customers_memberships.Startdate >= first_day_year) & \
                (db.customers_memberships.Startdate <= last_day_year)
        count = db(query).count()

        # Make sure we have 5 characters
        cmDateID = unicode(count)
        while len(cmDateID) < digits:
            cmDateID = '0' + cmDateID

        return cmDateID


    def set_date_id(self):
        """
        set db.customers_memberships.DateID field for membership
        :return:
        """
        db = current.db

        start = self.row.Startdate.strftime('%Y%m%d')
        cmDateID = self._set_date_id_get_next_id()

        date_id = ''.join([start, unicode(cmDateID)])
        self.row.DateID = date_id
        self.row.update_record()

        return date_id


    def set_barcode(self, date_id):
        """
            Set barcode
        """
        import barcode
        from barcode.writer import ImageWriter
        from cStringIO import StringIO

        db = current.db
        stream = StringIO()

        CODE39 = barcode.get_barcode_class('code39')
        code39_barcode = CODE39(
            date_id,
            writer=ImageWriter(),
            add_checksum=False
        )

        code39_barcode.write(stream)
        # print stream.getvalue()
        stream.seek(0)

        self.row.update_record(
            Barcode = db.customers_memberships.Barcode.store(
                stream,
                filename=date_id + '.png'
            )
        )


    def set_date_id_and_barcode(self):
        """
            Set date_id and barcode
        """
        self.set_barcode(self.set_date_id())