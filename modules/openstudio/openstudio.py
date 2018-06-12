# -*- coding: utf-8 -*-
import datetime
import calendar
import random
import os

from decimal import Decimal, ROUND_HALF_UP

from gluon import *
from general_helpers import get_last_day_month
from general_helpers import workshops_get_full_workshop_product_id
from general_helpers import max_string_length
from general_helpers import NRtoDay
from general_helpers import represent_validity_units


from openstudio.os_customer import Customer



class ClasscardsHelper:
    '''
        Class that contains functions for classcards
    '''

    def set_classes_taken(self, ccdID):
        '''
            Returns payment for a cuID and wspID
        '''
        db = current.db

        query = (db.classes_attendance.customers_classcards_id == ccdID) & \
                (db.classes_attendance.BookingStatus != 'cancelled')
        count = db(query).count()

        classcard = db.customers_classcards(ccdID)
        classcard.ClassesTaken = count
        classcard.update_record()

    def get_classes_taken(self, ccdID):
        '''
            Returns classes taken on a card
        '''
        db = current.db

        query = (db.classes_attendance.customers_classcards_id == ccdID) & \
                (db.classes_attendance.BookingStatus != 'cancelled')
        count = db(query).count()

        return count

    def get_classes_total(self, ccdID):
        '''
            Returns the total classes on a card
        '''
        db = current.db
        classcard = db.customers_classcards(ccdID)
        school_classcard = db.school_classcards(classcard.school_classcards_id)

        if school_classcard.Unlimited:
            return current.T('Unlimited')
        else:
            return school_classcard.Classes

    def get_classes_remaining(self, ccdID):
        '''
            Returns number of classes remaining on a card
        '''
        taken = self.get_classes_taken(ccdID)
        total = self.get_classes_total(ccdID)

        if total == current.T('Unlimited'):
            return total
        else:
            return total - taken

    def get_classes_available(self, ccdID):
        '''
            Returns True if classes are available on a card
            and False if not.
        '''
        remaining = self.get_classes_remaining(ccdID)

        if remaining > 0:
            available = True
        else:
            available = False

        return available

    def represent_validity(self, validity_months=None, validity_days=None):
        '''
            Represent validity for a school_classcard
        '''
        validity = SPAN()

        if validity_months:
            months = SPAN(validity_months, T(" Month"))
            if validity_months > 1:
                months.append(T('s'))
            validity.append(months)
            validity.append(' ')

        if validity_months and validity_days:
            validity.append(T(" and "))

        if validity_days:
            days = SPAN(validity_days, T(" Day"))
            if validity_days > 1:
                days.append(T('s'))
            validity.append(days)

        return validity


class WorkshopsHelper:
    def get_customer_info(self, wsp_cuID, wsID, WorkshopInfo, resend_link=''):
        '''
            Returns checkboxes for payment confirmation and workshop info
            wsp_cuID = workshops_products_customers.id
        '''
        T = current.T

        form = SQLFORM.factory(
            Field('WorkshopInfo', 'boolean',
                  default=WorkshopInfo)
        )

        hidden_field_id = INPUT(_type="hidden",
                                _name="id",
                                _value=wsp_cuID)

        inputs = DIV(
            form.custom.widget.WorkshopInfo, ' ',
            LABEL(T('Event Info'),
                  _for='no_table_WorkshopInfo')
        )

        form = DIV(form.custom.begin,
                   #table,
                   inputs,
                   hidden_field_id,
                   form.custom.end,
                   resend_link)

        return form


    def get_all_workshop_customers(self, wsID, count=False, ids_only=False):
        '''
            Returns a list of gluon.dal.row objects for each customer attending
            a workshop

            If count is set to True, return a count of customers attending
            the workshop
        '''
        # Get list of all customers with email for a workshop
        # Get all workshop_products_ids
        db = current.db
        query = (db.workshops_products.workshops_id == wsID)
        rows = db(query).select(db.workshops_products.id)
        products_ids = []
        for row in rows:
            products_ids.append(row.id)

        wspID = db.workshops_products_customers.workshops_products_id

        query = (wspID.belongs(products_ids))
        customers_rows = []
        left = [db.auth_user.on(db.auth_user.id == \
                                db.workshops_products_customers.auth_customer_id)]
        rows = db(query).select(db.workshops_products_customers.ALL,
                                db.auth_user.id,
                                db.auth_user.trashed,
                                db.auth_user.thumbsmall,
                                db.auth_user.first_name,
                                db.auth_user.last_name,
                                left=left )

        for row in rows:
            if row not in customers_rows:
                customers_rows.append(row)

        if count:
            return_value = len(customers_rows)
        elif ids_only:
            return_value = [row.auth_user.id for row in rows]
        else:
            return_value = customers_rows

        return return_value


    def get_product_sell_buttons(self, cuID, wsID, wspID, cid):
        """
            Returns buttons for workshop_product_sell list type
            This is a select button to select a customer to sell a product to
        """
        db = current.db
        os_gui = current.globalenv['os_gui']

        buttons = DIV(DIV(current.T("Already added"), _class='btn'),
                     _class='btn-group pull-right hidden')

        products_sold = db.workshops_products_customers
        # find full workshop id
        fwspID = self.get_full_workshop_product_id_for_workshop(wsID)

        # check if full workshop has been sold
        check_full_ws = products_sold(workshops_products_id=fwspID,
                                      auth_customer_id=cuID)

        # check if product has been sold
        check = products_sold(workshops_products_id=wspID,
                              auth_customer_id=cuID)

        if not check and not check_full_ws:
            buttons = DIV(os_gui.get_button('add',
                                        URL('events',
                                            'ticket_sell_to_customer',
                                            vars={'cuID' : cuID,
                                                  'wsID' : wsID,
                                                  'wspID': wspID},
                                            extension='')),
                         A(current.T('To waitinglist'),
                           _href=URL('events',
                                     'ticket_sell_to_customer',
                                     vars={'cuID'     : cuID,
                                           'wsID'     : wsID,
                                           'wspID'    : wspID,
                                           'waiting'  : True},
                                     extension=''),
                           _class='btn btn-default btn-sm'),
                        _class='btn-group pull-right')

        return buttons

    def get_full_workshop_product_id_for_workshop(self, wsID):
        '''
            Return id of full workshop product
        '''
        db = current.db
        query = (db.workshops_products.workshops_id == wsID) & \
                (db.workshops_products.FullWorkshop == True)

        return db(query).select().first().id


class WorkshopProduct:
    '''
        Class for workshop products
    '''
    def __init__(self, wspID):
        db = current.db

        self.wspID = int(wspID)
        self.workshop_product = db.workshops_products(self.wspID)
        self.workshop         = db.workshops(self.workshop_product.workshops_id)

        self.name          = self.workshop_product.Name
        self.workshop_name = self.workshop.Name
        self.wsID          = self.workshop.id
        self.tax_rates_id  = self.workshop_product.tax_rates_id

        self._set_price()


    def _set_price(self):
        if self.workshop_product.Price:
            self.price = self.workshop_product.Price
        else:
            self.price = 0


    def get_price(self):
        return self.workshop_product.Price


    def get_tax_rate_percentage(self):
        '''
            Returns the tax percentage for a workshop product, if any
        '''
        db = current.db

        if self.workshop_product.tax_rates_id:
            tax_rate = db.tax_rates(self.workshop_product.tax_rates_id)
            tax_rate_percentage = tax_rate.Percentage
        else:
            tax_rate_percentage = None

        return tax_rate_percentage


    def get_activities(self):
        '''
            Returns all activities for a workshop product
        '''
        db = current.db

        if self.workshop_product.FullWorkshop:
            query = (db.workshops_activities.workshops_id == self.workshop.id)
            left = None
        else:
            query = (db.workshops_products_activities.workshops_products_id == self.wspID)
            left = [ db.workshops_activities.on(
                db.workshops_products_activities.workshops_activities_id ==
                db.workshops_activities.id) ]


        rows = db(query).select(db.workshops_activities.ALL,
                                left=left,
                                orderby=db.workshops_activities.Activitydate|\
                                        db.workshops_activities.Starttime)

        return rows


    def is_sold_to_customer(self, cuID):
        '''
            :param cuID: db.auth_user.id
            :return: True when sold to customer, False when not
        '''
        db = current.db

        query = (db.workshops_products_customers.auth_customer_id == cuID) & \
                (db.workshops_products_customers.workshops_products_id == self.wspID)
        count = db(query).count()

        if count > 0:
            return True
        else:
            return False


    def is_sold_out(self):
        '''
            This function checks if a product is sold out
            It's sold out when any of the activities it contains is completely full
        '''
        def activity_list_customers_get_list_activity_query(wsaID):
            '''
                Returns a query that returns a set of all customers in a specific
                workshop activity, without the full workshop customers
            '''
            query = (db.workshops_activities.id ==
                     db.workshops_products_activities.workshops_activities_id) & \
                    (db.workshops_products_customers.workshops_products_id ==
                     db.workshops_products_activities.workshops_products_id) & \
                    (db.workshops_products_activities.workshops_activities_id ==
                     wsaID) & \
                    (db.workshops_products_customers.Waitinglist == False)

            return query

        def activity_count_reserved(wsaID):
            # count full workshop customers
            query = (db.workshops_products_customers.workshops_products_id == fwsID)
            count_full_ws = db(query).count()
            # count activity customers
            query = activity_list_customers_get_list_activity_query(wsaID)
            count_activity = db(query).count()

            return count_full_ws + count_activity

        db = current.db
        check = False

        fwsID = workshops_get_full_workshop_product_id(self.workshop.id)


        if self.wspID == fwsID:
            # Full workshops check, check if any activity is full
            query = (db.workshops_activities.workshops_id == self.workshop.id)
            rows = db(query).select(db.workshops_activities.ALL)
            for row in rows:
                reserved = activity_count_reserved(row.id)
                if reserved >= row.Spaces:
                    check = True
                    break
        else:
            # Product check, check if any a activity is full
            left = [ db.workshops_activities.on(
                db.workshops_products_activities.workshops_activities_id ==
                db.workshops_activities.id
            )]
            query = (db.workshops_products_activities.workshops_products_id == self.wspID)
            rows = db(query).select(db.workshops_products_activities.ALL,
                                    db.workshops_activities.Spaces,
                                    left=left)
            for row in rows:
                wsaID = row.workshops_products_activities.workshops_activities_id
                reserved = activity_count_reserved(wsaID)
                if reserved >= row.workshops_activities.Spaces:
                    check = True
                    break

        return check


    def add_to_shoppingcart(self, cuID):
        '''
            Add a workshop product to the shopping cart of a customer
        '''
        db = current.db

        db.customers_shoppingcart.insert(
            auth_customer_id = cuID,
            workshops_products_id = self.wspID
        )


    def sell_to_customer(self, cuID, waitinglist=False, invoice=True):
        '''
            Sells a workshop to a customer and creates an invoice
            Creates an invoice when a workshop product is sold
        '''
        db = current.db
        T = current.T

        info = False
        if self.workshop.AutoSendInfoMail:
            info = True

        wspID = self.wspID
        wspcID = db.workshops_products_customers.insert(
            auth_customer_id=cuID,
            workshops_products_id=wspID,
            Waitinglist=waitinglist,
            WorkshopInfo=info)

        ##
        # Add invoice
        ##
        if invoice and not waitinglist and self.price > 0:
            igpt = db.invoices_groups_product_types(ProductType = 'wsp')

            description = self.workshop_name + ' - ' + self.name
            
            iID = db.invoices.insert(
                invoices_groups_id = igpt.invoices_groups_id,
                Description = description,
                Status = 'sent'
                )

            # link invoice to sold workshop product for customer
            db.invoices_workshops_products_customers.insert(
                invoices_id = iID,
                workshops_products_customers_id = wspcID )

            # create object to set Invoice# and due date
            invoice = Invoice(iID)
            next_sort_nr = invoice.get_item_next_sort_nr()

            price = self.price

            iiID = db.invoices_items.insert(
                invoices_id  = iID,
                ProductName  = T("Event"),
                Description  = description,
                Quantity     = 1,
                Price        = price,
                Sorting      = next_sort_nr,
                tax_rates_id = self.tax_rates_id,
            )

            invoice.set_amounts()
            invoice.link_to_customer(cuID)

        ##
        # Send info mail to customer if we have some practical info
        ##
        if self.workshop.AutoSendInfoMail:
            osmail = OsMail()
            msgID = osmail.render_email_template('workshops_info_mail', workshops_products_customers_id=wspcID)
            osmail.send(msgID, cuID)

        if not waitinglist:
            # Check if sold out
            if self.is_sold_out():
                # Cancel all unpaid orders with a sold out product for this workshop
                ws = Workshop(self.wsID)
                ws.cancel_orders_with_sold_out_products()

        return wspcID



