# -*- coding: utf-8 -*-

from gluon import *


class SchoolMembership:
    """
        Class for school membership
    """
    def __init__(self, smID):
        """
            Class init function which sets ssuID
        """
        db = current.globalenv['db']

        self.smID = smID


    def get_price_on_date(self, date, formatted=True):
        """
            Returns the price for a membership on a given date
        """
        db = current.globalenv['db']

        price = ''
        query = (db.school_memberships_price.school_memberships_id ==
                 self.smID) & \
                (db.school_memberships_price.Startdate <= date) & \
                ((db.school_memberships_price.Enddate >= date) |
                 (db.school_memberships_price.Enddate == None))

        rows = db(query).select(db.school_memberships_price.ALL,
                                orderby=db.school_memberships_price.Startdate)
        if len(rows):
            if formatted:
                repr_row = list(rows[0:1].render())[0] # first row
                price = repr_row.Price
            else:
                row = rows.first()
                price = row.Price

        if not price:
            price = 0

        return price