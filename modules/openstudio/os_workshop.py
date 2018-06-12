# -*- coding: utf-8 -*-

from gluon import *


class Workshop:
    def __init__(self, wsID):
        self.wsID = wsID

        db = current.db
        query = (db.workshops.id == self.wsID)
        rows = db(query).select(db.workshops.ALL)
        self.workshop = rows.first()
        repr_row = rows.render(0)

        self.Name = self.workshop.Name
        self.Tagline = self.workshop.Tagline or ''
        self.Startdate = self.workshop.Startdate
        self.Startdate_formatted = repr_row.Startdate
        self.Enddate = self.workshop.Enddate
        self.Enddate_formatted = repr_row.Enddate
        self.Starttime = self.workshop.Starttime
        self.Endtime = self.workshop.Endtime
        self.auth_teacher_id = self.workshop.auth_teacher_id
        self.auth_teacher_id2 = self.workshop.auth_teacher_id2
        self.auth_teacher_name = repr_row.auth_teacher_id
        self.auth_teacher_name2 = repr_row.auth_teacher_id2
        self.Preview = self.workshop.Preview
        self.Description = self.workshop.Description
        self.school_levels_id = self.workshop.school_levels_id
        self.school_level = repr_row.school_levels_id
        self.school_locations_id = self.workshop.school_locations_id
        self.school_location = repr_row.school_locations_id
        self.picture = self.workshop.picture
        self.thumbsmall = self.workshop.thumbsmall
        self.thumblarge = self.workshop.thumblarge
        self.picture_2 = self.workshop.picture_2
        self.thumbsmall_2 = self.workshop.thumbsmall_2
        self.thumblarge_2 = self.workshop.thumblarge_2
        self.picture_3 = self.workshop.picture_3
        self.thumbsmall_3 = self.workshop.thumbsmall_3
        self.thumblarge_3 = self.workshop.thumblarge_3
        self.picture_4 = self.workshop.picture_3
        self.thumbsmall_4 = self.workshop.thumbsmall_4
        self.thumblarge_4 = self.workshop.thumblarge_4
        self.picture_5 = self.workshop.picture_5
        self.thumbsmall_5 = self.workshop.thumbsmall_5
        self.thumblarge_5 = self.workshop.thumblarge_5
        self.PublicWorkshop = self.workshop.PublicWorkshop


    def get_products(self, filter_public = False):
        """
            :param filter_public: boolean - show only Public products when set to True
            :return: workshop product rows for a workshop
        """
        db = current.db

        query = (db.workshops_products.workshops_id == self.wsID)
        if filter_public:
            query &= (db.workshops_products.PublicProduct == True)

        rows = db(query).select(db.workshops_products.ALL,
                                orderby = ~db.workshops_products.FullWorkshop)

        return rows


    def get_full_workshop_price(self):
        """
            :return: price of full workshop product
        """
        full_ws_product = self.get_products().first()

        return full_ws_product.Price


    def get_activities(self):
        db = current.db

        query = (db.workshops_activities.workshops_id == self.wsID)
        rows = db(query).select(db.workshops_activities.ALL,
                                orderby = db.workshops_activities.Activitydate|\
                                          db.workshops_activities.Starttime)

        return rows


    def update_dates_times(self):
        """
            After adding/editing/deleting a workshop activity, call this function
            to update the dates & times on the db.workshops record
        """
        activities = self.get_activities()

        time_from  = None
        time_until = None
        date_from  = None
        date_until = None
        if len(activities) > 0:
            date_from = activities[0].Activitydate
            date_until = activities[0].Activitydate
            time_from = activities[0].Starttime
            time_until = activities[0].Endtime

        if len(activities) > 1:
            date_until = activities[len(activities) - 1].Activitydate
            time_until = activities[len(activities) - 1].Endtime

        self.workshop.Startdate = date_from
        self.workshop.Enddate   = date_until
        self.workshop.Starttime = time_from
        self.workshop.Endtime   = time_until
        self.workshop.update_record()


    def cancel_orders_with_sold_out_products(self):
        """
            After selling a product online or adding a customer to a product, check whether products aren't sold out.
            If a product is sold out, check for open orders containing the sold out product and cancel them.
        """
        db = current.db

        products = self.get_products()
        for product in products:
            wsp = WorkshopProduct(product.id)
            if wsp.is_sold_out():
                # Cancel all unpaid orders with this product
                left = [db.customers_orders.on(
                    db.customers_orders_items.customers_orders_id == db.customers_orders.id)]
                query = ((db.customers_orders.Status == 'awaiting_payment') |
                         (db.customers_orders.Status == 'received')) & \
                        (db.customers_orders_items.workshops_products_id == product.id)
                sold_out_rows = db(query).select(db.customers_orders_items.ALL,
                                                 db.customers_orders.ALL,
                                                 left=left)
                for sold_out_row in sold_out_rows:
                    order = Order(sold_out_row.customers_orders.id)
                    order.set_status_cancelled()

