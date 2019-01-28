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


    def _get_enddate(self, startdate):
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


    def set_enddate(self):
        """
        Set enddate
        """
        enddate = self._get_enddate(self.row.Startdate)

        self.row.Enddate = enddate
        self.row.update_record()


    def get_linked_invoice(self):
        """
        :return: db.invoices.id (Linked invoiceID)
        """
        db = current.db

        query = (db.invoices_items_customers_memberships.customers_memberships_id == self.cmID)
        left = [
            db.invoices_items.on(
                db.invoices_items_customers_memberships.invoices_items_id ==
                db.invoices_items.id
            )
        ]

        rows = db(query).select(
            db.invoices_items.invoices_id,
            left=left
        )

        if rows:
            return rows.first().invoices_id
        else:
            return None
