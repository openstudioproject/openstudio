# -*- coding: utf-8 -*-

import calendar
import datetime
from gluon import *


class SchoolMembership:
    """
        Class for school membership
    """
    def __init__(self, smID):
        """
            Class init function which sets ssuID
        """
        db = current.db

        self.smID = smID
        self.row = db.school_memberships(smID)


    def get_validity_formatted(self):
        """
            :return: Validity for school membership
        """
        T  = current.T
        db = current.db

        validity = SPAN(unicode(self.row.Validity), ' ')

        validity_in = represent_validity_units(self.row.ValidityUnit, self.row)
        if self.row.Validity == 1: # Cut the last 's"
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
            school_memberhsips_id = self.smID
        )


    def sell_to_customer(self, auth_user_id, date_start, note=None, invoice=True, payment_methods_id=None):
        """
            :param auth_user_id: Sell membership to customer
        """
        from os_customer_membership import CustomerMembership
        from os_cache_manager import OsCacheManager

        db = current.db
        ocm = OsCacheManager()

        cmID = db.customers_memberships.insert(
            auth_customer_id = auth_user_id,
            school_memberships_id = self.smID,
            Startdate = date_start,
            Enddate = self.sell_to_customer_get_enddate(date_start),
            Note = note,
            payment_methods_id=payment_methods_id
        )

        # Init membership
        cm = CustomerMembership(cmID)
        cm.set_enddate()

        # Clear memberships cache for this user
        ocm.clear_customers_memberships(auth_user_id)

        if invoice:
            self.sell_to_customer_create_invoice(cmID)

        return cmID


    def sell_to_customer_create_invoice(self, cmID):
        """
        Add an invoice after adding a membership
        :param cmID: db.customers_memberships.id
        :return: db.invoices.id
        """
        from openstudio.os_customer_membership import CustomerMembership
        from openstudio.os_invoice import Invoice
        
        db = current.db
        T = current.T

        cm = CustomerMembership(cmID)

        # Check if price exists and > 0:
        if self.row.Price:
            igpt = db.invoices_groups_product_types(ProductType='membership')

            iID = db.invoices.insert(
                invoices_groups_id=igpt.invoices_groups_id,
                Description=cm.get_name(),
                Status='sent',
                payment_methods_id=cm.row.payment_methods_id
            )

            invoice = Invoice(iID)
            invoice.link_to_customer(cm.row.auth_customer_id)
            invoice.item_add_membership(
                cmID,
            )

            return iID
        else:
            return None


    def sell_to_customer_get_enddate(self, date_start):
        """
           Calculate and set enddate when adding a membership
           :param cmID: db.customers_memberships.id
           :return : enddate for a membership
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
        sm = db.school_memberships(self.smID)

        if sm.ValidityUnit == 'months':
            # check for and add months
            months = sm.Validity
            if months:
                enddate = add_months(date_start, months)
        else:
            if sm.ValidityUnit == 'weeks':
                days = sm.Validity * 7
            else:
                days = sm.Validity

            delta_days = datetime.timedelta(days=days)
            enddate = (date_start + delta_days) - datetime.timedelta(days=1)

        return enddate
    # def sell_to_customer_get_enddate(self, date_start):
    #     """
    #        Calculate and set enddate when adding a membership
    #        :param ccdID: db.customers_classcards.id
    #        :return : enddate for a classcard
    #     """
    #     from openstudio.tools import OsTools
    #
    #     tools = OsTools()
    #
    #     return tools.calculate_validity_enddate(
    #         date_start,
    #         self.row.Validity,
    #         self.row.ValidityUnit
    #     )
        