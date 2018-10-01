# -*- coding: utf-8 -*-

import calendar
import datetime

from gluon import *


class SchoolClasscard:
    """
        Class that contains functions for a class card
    """
    def __init__(self, scdID, set_db_info=False):
        """
            Class init function which sets ssuID
        """
        self.scdID = scdID

        if set_db_info:
            self._set_db_info()


    def _set_db_info(self):
        """
        Set db info
        :return: None
        """
        db = current.db

        self.row = db.school_classcards(self.scdID)


    def get_validity_formatted(self):
        """
            :return: Validity for school classcard
        """
        from general_helpers import represent_validity_units

        T  = current.T
        db = current.db

        row = db.school_classcards(self.scdID)
        validity = SPAN(unicode(row.Validity), ' ')

        validity_in = represent_validity_units(row.ValidityUnit, row)
        if row.Validity == 1: # Cut the last 's"
            validity_in = validity_in[:-1]

        validity.append(validity_in)

        return validity


    def add_to_shoppingcart(self, auth_user_id):
        """
            :param auth_user_id: db.auth_user.id
        """
        db = current.db

        db.customers_shoppingcart.insert(
            auth_customer_id     = auth_user_id,
            school_classcards_id = self.scdID
        )


    def sell_to_customer(self, auth_user_id, date_start, note=None, invoice=True):
        """
            :param auth_user_id: Sell classcard to customer
        """
        db = current.db
        cache_clear_customers_classcards = current.globalenv['cache_clear_customers_classcards']

        ccdID = db.customers_classcards.insert(
            auth_customer_id = auth_user_id,
            school_classcards_id = self.scdID,
            Startdate = date_start,
            Enddate = self.sell_to_customer_get_enddate(date_start),
            Note = note
        )

        cache_clear_customers_classcards(auth_user_id)

        if invoice:
            self.sell_to_customer_create_invoice(ccdID)

        return ccdID


    def sell_to_customer_create_invoice(self, ccdID):
        """
            Add an invoice after adding a classcard
        """
        from os_customer_classcard import CustomerClasscard
        from os_invoice import Invoice

        db = current.db
        T = current.T

        classcard = CustomerClasscard(ccdID)

        igpt = db.invoices_groups_product_types(ProductType='classcard')

        iID = db.invoices.insert(
            invoices_groups_id=igpt.invoices_groups_id,
            Description=classcard.get_name(),
            Status='sent'
        )

        # create object to set Invoice# and due date
        invoice = Invoice(iID)

        # link invoice to customer
        invoice.link_to_customer(classcard.get_auth_customer_id())

        # add classcard item
        invoice.item_add_classcard(ccdID)


    def sell_to_customer_get_enddate(self, date_start):
        """
           Calculate and set enddate when adding a classcard
           :param ccdID: db.customers_classcards.id
           :return : enddate for a classcard
        """
        def add_months(sourcedate, months):
            month = sourcedate.month - 1 + months
            year = int(sourcedate.year + month / 12)
            month = month % 12 + 1
            last_day_new = calendar.monthrange(year, month)[1]
            day = min(sourcedate.day, last_day_new)

            ret_val = datetime.date(year, month, day)

            last_day_source = calendar.monthrange(sourcedate.year,
                                                  sourcedate.month)[1]

            if sourcedate.day == last_day_source and last_day_source > last_day_new:
                return ret_val
            else:
                delta = datetime.timedelta(days=1)
                return ret_val - delta

        db = current.db

        # get info
        card = db.school_classcards(self.scdID)

        if card.ValidityUnit == 'months':
            # check for and add months
            months = card.Validity
            if months:
                enddate = add_months(date_start, months)
        else:
            if card.ValidityUnit == 'weeks':
                days = card.Validity * 7
            else:
                days = card.Validity

            delta_days = datetime.timedelta(days=days)
            enddate = (date_start + delta_days) - datetime.timedelta(days=1)

        return enddate
