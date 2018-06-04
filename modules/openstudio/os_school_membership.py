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
        self.row = db.school_memberships(smID)
        

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
    
    
    def get_tax_rates_on_date(self, date):
        """
            Returns tax rates on date
        """
        db = current.globalenv['db']

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
        db = current.globalenv['db']

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
        db = current.globalenv['db']

        db.customers_shoppingcart.insert(
            auth_customer_id     = auth_user_id,
            school_memberhsips_id = self.smID
        )


    def sell_to_customer(self, auth_user_id, date_start, note=None, invoice=True):
        """
            :param auth_user_id: Sell membership to customer
        """
        db = current.globalenv['db']
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
        from openstudio.openstudio import Invoice
        
        db = current.globalenv['db']
        T = current.T

        cm = CustomerMembership(cmID)

        igpt = db.invoices_groups_product_types(ProductType='membership')

        iID = db.invoices.insert(
            invoices_groups_id=igpt.invoices_groups_id,
            Description=cm.get_name(),
            Status='sent'
        )
        
        invoice = Invoice(iID)
        invoice.link_to_customer(cm.row.auth_customer_id)
        invoice.item_add_membership(cmID)

        return iID


    def sell_to_customer_get_enddate(self, date_start):
        """
           Calculate and set enddate when adding a membership
           :param ccdID: db.customers_classcards.id
           :return : enddate for a classcard
        """
        from openstudio.tools import OsTools
        
        tools = OsTools()

        return tools.calculate_validity_enddate(
            date_start, 
            self.row.Validity, 
            self.row.ValidityUnit
        )
        