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
        '''
            :param filter_public: boolean - show only Public products when set to True
            :return: workshop product rows for a workshop
        '''
        db = current.db

        query = (db.workshops_products.workshops_id == self.wsID)
        if filter_public:
            query &= (db.workshops_products.PublicProduct == True)

        rows = db(query).select(db.workshops_products.ALL,
                                orderby = ~db.workshops_products.FullWorkshop)

        return rows


    def get_full_workshop_price(self):
        '''
            :return: price of full workshop product
        '''
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
        '''
            After adding/editing/deleting a workshop activity, call this function
            to update the dates & times on the db.workshops record
        '''
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
        '''
            After selling a product online or adding a customer to a product, check whether products aren't sold out.
            If a product is sold out, check for open orders containing the sold out product and cancel them.
        '''
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


class WorkshopSchedule:
    def __init__(self, filter_date_start,
                       filter_date_end = None,
                       filter_archived = True,
                       filter_only_public = True,
                       sorting = 'date'):

        self.filter_date_start = filter_date_start
        self.filter_date_end = filter_date_end
        self.filter_archived = filter_archived
        self.filter_only_public = filter_only_public

        self.sorting = sorting

    def _get_workshops_rows_filter_query(self):
        '''
            Apply filters to workshops
        '''
        where = ''
        if self.filter_archived:
            where += "AND ws.Archived='F'"
            where += ' '

        if self.filter_only_public:
            where += "AND ws.PublicWorkshop='T'"
            where += ' '

        #TODO: check first activity date as startdate ... or create function in workshops.py that updates dates
        # & times for workshops when an activity is added/updated/deleted.
        if self.filter_date_start:
            where += "AND ws.Startdate >= '" + unicode(self.filter_date_start) + "'"
            where += ' '

        if self.filter_date_end:
            where += "AND ws.Enddate <= " + unicode(self.filter_date_end) + "'"
            where += ' '

        return where


    def _get_workshops_rows_orderby(self):
        '''
            Apply right sorting to rows
        '''
        db = current.db
        orderby = 'ws.Startdate'

        if self.sorting == 'name':
            orderby = 'ws.Name'

        return orderby


    def get_workshops_rows(self):
        '''
            Gets workshop rows
        '''
        db = current.db

        orderby_sql = self._get_workshops_rows_orderby()
        where_filter = self._get_workshops_rows_filter_query()

        fields = [
            db.workshops.id,
            db.workshops.Name,
            db.workshops.Tagline,
            db.workshops.Startdate,
            db.workshops.Enddate,
            db.workshops.Starttime,
            db.workshops.Endtime,
            db.workshops.auth_teacher_id,
            db.workshops.auth_teacher_id2,
            db.workshops.Preview,
            db.workshops.Description,
            db.workshops.school_levels_id,
            db.workshops.school_locations_id,
            db.workshops.picture,
            db.workshops.thumbsmall,
            db.workshops.thumblarge,
            db.workshops_products.Price
        ]

        query = '''
        SELECT ws.id,
               ws.Name,
               ws.Tagline,
               ws.Startdate,
               ws.Enddate,
               ws.Starttime,
               ws.Endtime,
               ws.auth_teacher_id,
               ws.auth_teacher_id2,
               ws.Preview,
               ws.Description,
               ws.school_levels_id,
               ws.school_locations_id,
               ws.picture,
               ws.thumbsmall,
               ws.thumblarge,
               wsp.Price
        FROM workshops ws
        LEFT JOIN
            ( SELECT id, workshops_id, Price FROM workshops_products
              WHERE FullWorkshop = 'T' ) wsp
            ON ws.id = wsp.workshops_id
        WHERE ws.id > 0
              {where_filter}
        ORDER BY {orderby_sql}
        '''.format(orderby_sql = orderby_sql,
                   where_filter = where_filter)

        rows = db.executesql(query, fields=fields)

        return rows


    def get_workshops_list(self):
        '''
            Returns list of workshops
        '''
        rows = self.get_workshops_rows().as_list()


    def _get_workshops_shop(self):
        """
            Format list of workshops in a suitable way for the shop
        """
        def new_workshop_month():
            _class = 'workshops-list-month'

            return DIV(H2(last_day_month.strftime('%B %Y'), _class='center'), _class=_class)

        request = current.request
        os_gui = current.globalenv['os_gui']
        T = current.T
        TODAY_LOCAL = current.TODAY_LOCAL

        rows = self.get_workshops_rows()

        current_month = TODAY_LOCAL
        last_day_month = get_last_day_month(current_month)

        workshops_month = new_workshop_month()
        workshops_month_body = DIV(_class='box-body')


        workshops = DIV()

        for i, row in enumerate(rows):
            repr_row = list(rows[i:i + 1].render())[0]

            more_info = os_gui.get_button('noicon',
                URL('event', vars={'wsID':row.workshops.id}),
                title=T('More info...'),
                btn_class='btn-link',
                btn_size='',
                _class='workshops-list-workshop-more-info')

            # Check if we're going into a later month
            if row.workshops.Startdate > last_day_month:
                if len(workshops_month_body) >= 1:
                    # check if we have more in the month than just the title (the 1 in len())
                    workshops_month.append(DIV(workshops_month_body, _class='box box-solid'))
                    workshops.append(workshops_month)
                last_day_month = get_last_day_month(row.workshops.Startdate)
                workshops_month = new_workshop_month()
                workshops_month_body = DIV(_class='box-body')

            startdate = SPAN(row.workshops.Startdate.strftime('%d %B').lstrip("0").replace(" 0", " "), _class='label_date')
            enddate = ''
            if not row.workshops.Startdate == row.workshops.Enddate:
                enddate = SPAN(row.workshops.Enddate.strftime('%d %B').lstrip("0").replace(" 0", " "), _class='label_date')
            workshop = DIV(
                DIV(DIV(DIV(repr_row.workshops.thumblarge, _class='workshops-list-workshop-image center'),
                        _class='col-xs-12 col-sm-12 col-md-3'),
                        DIV(A(H3(row.workshops.Name), _href=URL('shop', 'event', vars={'wsID':row.workshops.id})),
                            H4(repr_row.workshops.Tagline),
                            DIV(os_gui.get_fa_icon('fa-calendar-o'), ' ',
                                startdate, ' ',
                                repr_row.workshops.Starttime, ' - ',
                                enddate, ' ',
                                repr_row.workshops.Endtime,
                                _class='workshops-list-workshop-date'),
                            DIV(os_gui.get_fa_icon('fa-user-o'), ' ', repr_row.workshops.auth_teacher_id, _class='workshops-list-workshop-teacher'),
                            DIV(os_gui.get_fa_icon('fa-map-marker'), ' ', repr_row.workshops.school_locations_id, _class='workshops-list-workshop-location'),
                            BR(),
                            more_info,
                            _class='col-xs-12 col-sm-12 col-md-9 workshops-list-workshop-info'),
                        _class=''),
                _class='workshops-list-workshop col-md-8 col-md-offset-2 col-xs-12')

            workshops_month_body.append(workshop)

            # if we're at the last row, add the workshops to the page
            if i + 1 == len(rows):
                workshops_month.append(DIV(workshops_month_body, _class='box box-solid'))
                workshops.append(workshops_month)

        return workshops


    def get_workshops_shop(self):
        """
            Use caching when not running as test to return the workshops list in the shop
        """
        web2pytest = current.globalenv['web2pytest']
        request = current.request
        auth = current.auth

        # Don't cache when running tests
        if web2pytest.is_running_under_test(request, request.application):
            rows = self._get_workshops_shop()
        else:
            cache = current.cache
            CACHE_LONG = current.globalenv['CACHE_LONG']
            cache_key = 'openstudio_workshops_workshops_schedule_shop'

            rows = cache.ram(cache_key , lambda: self._get_workshops_shop(), time_expire=CACHE_LONG)

        return rows


