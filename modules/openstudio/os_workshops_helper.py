# -*- coding: utf-8 -*-

from gluon import *


class WorkshopsHelper:
    def get_customer_info(self, wsp_cuID, wsID, WorkshopInfo, resend_link=''):
        """
            Returns checkboxes for payment confirmation and workshop info
            wsp_cuID = workshops_products_customers.id
        """
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
        """
            Returns a list of gluon.dal.row objects for each customer attending
            a workshop

            If count is set to True, return a count of customers attending
            the workshop
        """
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
        """
            Return id of full workshop product
        """
        db = current.db
        query = (db.workshops_products.workshops_id == wsID) & \
                (db.workshops_products.FullWorkshop == True)

        return db(query).select().first().id


