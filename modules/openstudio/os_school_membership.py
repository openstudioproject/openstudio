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
        db = current.db

        self.smID = smID
        self.row = db.school_memberships(smID)


    def get_price_rows_on_date(self, date):
        """
        :param date: datetime.date
        :return: first db.school_membrships_price row found for date
        """
        db = current.db

        query = (db.school_memberships_price.school_memberships_id ==
                 self.smID) & \
                (db.school_memberships_price.Startdate <= date) & \
                ((db.school_memberships_price.Enddate >= date) |
                 (db.school_memberships_price.Enddate == None))

        rows = db(query).select(db.school_memberships_price.ALL,
                                orderby=db.school_memberships_price.Startdate)

        return rows
        

    def get_price_on_date(self, date, formatted=True):
        """
            Returns the price for a membership on a given date
        """
        db = current.db

        price = ''
        rows = self.get_price_rows_on_date(date)

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
    
    
    def get_tax_rates_on_date(self, date):
        """
            Returns tax rates on date
        """
        db = current.db

        left = [ db.tax_rates.on(db.school_memberships_price.tax_rates_id ==
                                 db.tax_rates.id) ]

        query = (db.school_memberships_price.school_memberships_id ==
                 self.smID) & \
                (db.school_memberships_price.Startdate <= date) & \
                ((db.school_memberships_price.Enddate >= date) |
                 (db.school_memberships_price.Enddate == None))

        rows = db(query).select(db.school_memberships.ALL,
                                db.school_memberships_price.ALL,
                                db.tax_rates.ALL,
                                left=left,
                                orderby=db.school_memberships_price.Startdate)

        if rows:
            row = rows.first()
        else:
            row = None

        return row


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


    def sell_to_customer(self, auth_user_id, date_start, note=None, invoice=True):
        """
            :param auth_user_id: Sell membership to customer
        """
        db = current.db
        cache_clear_customers_classcards = current.globalenv['cache_clear_customers_classcards']

        cmID = db.customers_memberships.insert(
            auth_customer_id = auth_user_id,
            school_memberships_id = self.smID,
            Startdate = date_start,
            Enddate = self.sell_to_customer_get_enddate(date_start),
            Note = note
        )

        #cache_clear_customers_classcards(auth_user_id)

        if invoice:
            self.sell_to_customer_create_invoice(cmID)

        return ccdID


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
        if self.get_price_on_date(cm.row.Startdate):
            period_start = cm.row.Startdate
            period_end = cm.get_period_enddate(cm.row.Startdate)

            igpt = db.invoices_groups_product_types(ProductType='membership')

            iID = db.invoices.insert(
                invoices_groups_id=igpt.invoices_groups_id,
                Description=cm.get_name(),
                MembershipPeriodStart=period_start,
                MembershipPeriodEnd=period_end,
                Status='sent'
            )

            invoice = Invoice(iID)
            invoice.link_to_customer(cm.row.auth_customer_id)
            invoice.item_add_membership(
                cmID,
                period_start,
                period_end
            )

            return iID
        else:
            return None


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
        