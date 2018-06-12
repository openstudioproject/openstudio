# -*- coding: utf-8 -*-

from gluon import *


class Customer:
    """
        Class that contains functions for customer
    """
    def __init__(self, cuID):
        """
            Class init function which sets cuID
        """
        db = current.db

        self.cuID = cuID
        self.row = db.auth_user(cuID)


    def get_name(self):
        """
            Returns the name for a customer
        """
        return self.row.display_name


    def get_email_hash(self, hash_type='md5'):
        """

        """
        import hashlib

        md5 = hashlib.md5()
        md5.update(self.row.email.lower())

        return md5.hexdigest()


    def _get_subscriptions_on_date(self, date):
        '''
            Returns subscription for a date
        '''
        db = current.db
        cache = current.cache
        request = current.request
        web2pytest = current.globalenv['web2pytest']

        fields = [
            db.customers_subscriptions.id,
            db.customers_subscriptions.auth_customer_id,
            db.customers_subscriptions.Startdate,
            db.customers_subscriptions.Enddate,
            db.customers_subscriptions.payment_methods_id,
            db.customers_subscriptions.Note,
            db.school_subscriptions.Name,
            db.school_subscriptions.ReconciliationClasses,
            db.school_subscriptions.Unlimited,
            db.customers_subscriptions.CreditsRemaining,
        ]

        sql = '''SELECT cs.id,
                        cs.auth_customer_id,
                        cs.Startdate,
                        cs.Enddate,
                        cs.payment_methods_id,
                        cs.Note,
                        ssu.Name,
                        ssu.ReconciliationClasses,
                        ssu.Unlimited,
(IFNULL(( SELECT SUM(csc.MutationAmount)
 FROM customers_subscriptions_credits csc
 WHERE csc.customers_subscriptions_id = cs.id AND
	   csc.MutationType = 'add'), 0) -
IFNULL(( SELECT SUM(csc.MutationAmount)
 FROM customers_subscriptions_credits csc
 WHERE csc.customers_subscriptions_id = cs.id AND
	   csc.MutationType = 'sub'), 0)) AS credits
FROM customers_subscriptions cs
LEFT JOIN
school_subscriptions ssu ON cs.school_subscriptions_id = ssu.id
WHERE cs.auth_customer_id = {cuID} AND
(cs.Startdate <= '{date}' AND (cs.Enddate >= '{date}' OR cs.Enddate IS NULL))
ORDER BY cs.Startdate'''.format(cuID=self.cuID, date=date)

        rows = db.executesql(sql, fields=fields)

        #print db._lastsql[0]

        if len(rows) > 0:
            return_value = rows
        else:
            return_value = False

        return return_value


    def get_subscriptions_on_date(self, date, from_cache=True):
        '''
            Get day rows with caching
        '''
        web2pytest = current.globalenv['web2pytest']
        request = current.request

        # Don't cache when running tests
        if web2pytest.is_running_under_test(request, request.application) or not from_cache:
            rows = self._get_subscriptions_on_date(date)
        else:
            cache = current.cache
            DATE_FORMAT = current.DATE_FORMAT
            CACHE_LONG = current.globalenv['CACHE_LONG']
            cache_key = 'openstudio_customer_get_subscriptions_on_date_' + \
                        str(self.cuID) + '_' + \
                        date.strftime(DATE_FORMAT)
            rows = cache.ram(cache_key , lambda: self._get_subscriptions_on_date(date), time_expire=CACHE_LONG)

        return rows


    def has_subscription_on_date(self, date):
        """
        :param date: datetime.date
        :return: Boolean
        """
        if self.get_subscriptions_on_date(date):
            return True
        else:
            return False


    def get_subscription_latest(self):
        '''
            @return: Latest subscription for a customer
        '''
        db = current.db
        os_gui = current.globalenv['os_gui']
        DATE_FORMAT = current.DATE_FORMAT

        fields = [
            db.auth_user.id,
            db.school_subscriptions.Name,
            db.customers_subscriptions.Startdate,
            db.customers_subscriptions.Enddate
        ]

        query = """
            SELECT au.id,
                   ssu.name,
                   cs.startdate,
                   cs.enddate
                   FROM auth_user au
            LEFT JOIN customers_subscriptions cs ON cs.auth_customer_id = au.id
            LEFT JOIN
                (SELECT auth_customer_id,
                        school_subscriptions_id,
                        max(startdate) as startdate,
                        enddate
                FROM customers_subscriptions GROUP BY auth_customer_id) chk
            ON au.id = chk.auth_customer_id
            LEFT JOIN
                (SELECT id, name FROM school_subscriptions) ssu
            ON ssu.id = cs.school_subscriptions_id
            WHERE cs.startdate = chk.startdate
                  AND au.id = {cuID} """.format(cuID=self.cuID)

        # show the latest subscription
        result = db.executesql(query, fields=fields)

        if len(result):
            record = result.first()
            try:
                return SPAN(os_gui.get_fa_icon('fa-clock-o'), ' ',
                            record.school_subscriptions.Name,
                            ' [',
                            record.customers_subscriptions.Startdate.strftime(DATE_FORMAT), ' - ',
                            record.customers_subscriptions.Enddate.strftime(DATE_FORMAT),
                            '] ',
                            _class='small_font',
                            _title='Latest subscription (past)')
            except AttributeError:
                return False

        else:
            return False


    def _get_memberships_on_date(self, date):
        """
        :param date: datetime.date
        :return: db.customers_memberships rows for customer
        """
        db = current.db

        query = (db.customers_memberships.auth_customer_id == self.cuID) & \
                (db.customers_memberships.Startdate <= date) & \
                ((db.customers_memberships.Enddate >= date) |
                 (db.customers_memberships.Enddate == None))
        rows = db(query).select(db.customers_memberships.ALL,
                                orderby=db.customers_memberships.Startdate)

        return rows


    def get_memberships_on_date(self, date, from_cache=True):
        """
            Get day rows with caching
        """
        web2pytest = current.globalenv['web2pytest']
        request = current.request

        # Don't cache when running tests
        if web2pytest.is_running_under_test(request, request.application) or not from_cache:
            rows = self._get_memberships_on_date(date)
        else:
            cache = current.cache
            DATE_FORMAT = current.DATE_FORMAT
            CACHE_LONG = current.globalenv['CACHE_LONG']
            cache_key = 'openstudio_customer_get_memberships_on_date_' + \
                        str(self.cuID) + '_' + \
                        date.strftime(DATE_FORMAT)
            rows = cache.ram(cache_key, lambda: self._get_memberships_on_date(date), time_expire=CACHE_LONG)

        return rows


    def has_membership_on_date(self, date):
        """
        :param date: datetime.date
        :return: Boolean
        """
        if self.get_memberships_on_date(date):
            return True
        else:
            return False


    def _get_classcards(self, date):
        """
            Returns classcards for customer(cuID) on date
        """
        db = current.db
        cache = current.cache
        request = current.request
        web2pytest = current.globalenv['web2pytest']

        left = [ db.school_classcards.on(
            db.customers_classcards.school_classcards_id==\
            db.school_classcards.id)]
        query = (db.customers_classcards.auth_customer_id == self.cuID) & \
                (db.customers_classcards.Startdate <= date) & \
                ((db.customers_classcards.Enddate >= date) |
                 (db.customers_classcards.Enddate == None)) & \
                ((db.school_classcards.Classes > db.customers_classcards.ClassesTaken) |
                 (db.school_classcards.Classes == 0) |
                 (db.school_classcards.Unlimited == True))

        rows = db(query).select(db.customers_classcards.ALL,
                                db.school_classcards.Name,
                                db.school_classcards.Classes,
                                db.school_classcards.Unlimited,
                                left=left,
                                orderby=db.customers_classcards.Enddate)

        #print rows

        if len(rows) > 0:
            return_value = rows
        else:
            return_value = False

        return return_value


    def get_classcards(self, date, from_cache=True):
        """
            Get day rows with caching
        """
        web2pytest = current.globalenv['web2pytest']
        request = current.request

        # Don't cache when running tests
        if web2pytest.is_running_under_test(request, request.application) or not from_cache:
            rows = self._get_classcards(date)
        else:
            cache = current.cache
            DATE_FORMAT = current.DATE_FORMAT
            CACHE_LONG = current.globalenv['CACHE_LONG']
            cache_key = 'openstudio_customer_get_classcards_' + \
                        str(self.cuID) + '_' + \
                        date.strftime(DATE_FORMAT)
            rows = cache.ram(cache_key , lambda: self._get_classcards(date), time_expire=CACHE_LONG)

        return rows


    def has_classcard_on_date(self, date):
        """
        :param date: datetime.date
        :return: Boolean
        """
        if self.get_classcards(date):
            return True
        else:
            return False


    def get_subscriptions_and_classcards_formatted(self,
                date,
                new_cards=True,
                show_subscriptions=True):
        """
            Returns a formatted list of subscriptions and classcards for
            a customer
        """
        from openstudio.os_customer_classcard import CustomerClasscard
        from openstudio.os_customer_subscriptions import CustomerSubscriptions

        DATE_FORMAT = current.DATE_FORMAT
        T = current.T
        os_gui = current.globalenv['os_gui']

        cuID = self.cuID
        subscription = ''
        has_subscription = False
        if show_subscriptions:
            subscriptions = self.get_subscriptions_on_date(date)
            if subscriptions:
                has_subscription = True
                subscription = DIV()
                for cs in subscriptions:
                    csID = cs.customers_subscriptions.id
                    # dates
                    subscr_dates = SPAN(' [', cs.customers_subscriptions.Startdate.strftime(DATE_FORMAT))
                    if cs.customers_subscriptions.Enddate:
                        subscr_dates.append(' - ')
                        subscr_dates.append(cs.customers_subscriptions.Enddate.strftime(DATE_FORMAT))
                    subscr_dates.append('] ')
                    # credits
                    #TODO: Add check for system setting if we should show the credits
                    subscr_credits = ''
                    if cs.customers_subscriptions.CreditsRemaining:
                        subscr_credits = SPAN(XML(' &bull; '), round(cs.customers_subscriptions.CreditsRemaining, 1), ' ',
                                              T('Credits'))
                    subscription.append(SPAN(cs.school_subscriptions.Name, subscr_dates, subscr_credits))

                    cs = CustomerSubscriptions(csID)
                    paused = cs.get_paused(date)
                    if paused:
                        pause_text = SPAN(' | ', paused, _class='bold')
                        subscription.append(pause_text)
                    subscription.append(BR())


        # get class card for customer
        has_classcard = False
        customer_classcards = self.get_classcards(date)
        if customer_classcards:
            has_classcard = True
            classcards = DIV()
            for card in classcards:
                ccdID = card.customers_classcards.id
                classcard = CustomerClasscard(ccdID)
                remaining_classes = ccd.get_classes_remaining()
                if not remaining_classes:
                    continue

                try:
                    enddate = card.customers_classcards.Enddate.strftime(DATE_FORMAT)
                except AttributeError:
                    enddate = T('No expiry')

                classcards.append(
                    SPAN(card.school_classcards.Name, XML(' &bull; '),
                    T('expires'), ' ',
                    enddate, XML(' &bull; '),
                    remaining_classes)
                )

                if not card.school_classcards.Unlimited:
                    classcards.append(SPAN(' ', T("Classes remaining")))

                classcards.append(BR())

        else:
            classcards = T("")

        # format data for display
        subscr_cards = TABLE(_class='grey small_font')

        if not has_subscription and not has_classcard:
            if show_subscriptions:
                subscr_cards.append(DIV(T("No subscription or class card"),
                                         _class='red'))
                latest = self.get_subscription_latest()
                subscr_cards.append(latest if latest else '')

        else:
            if subscription and show_subscriptions:
                subscr_cards.append(TR(subscription))
            if classcards:
                subscr_cards.append(TR(classcards))

        return subscr_cards


    def get_had_trialclass(self):
        '''
            Returns True if a customer has had a trialclass and false when not
        '''
        db = current.db

        query = (db.classes_attendance.auth_customer_id == self.cuID) & \
                (db.classes_attendance.AttendanceType == 1)

        count = db(query).count()

        if count > 0:
            had_trial = True
        else:
            had_trial = False

        return had_trial


    def get_workshops_rows(self, upcoming=False):
        """
            Returns workshops for a customer
        """
        db = current.db
        TODAY_LOCAL = current.TODAY_LOCAL

        db_icwspc = db.invoices_workshops_products_customers


        orderby = ~db.workshops.Startdate
        query = (db.workshops_products_customers.auth_customer_id == self.cuID)

        if upcoming:
            query &= (db.workshops.Startdate >= TODAY_LOCAL)
            orderby = db.workshops.Startdate

        rows = db(query).select(
            db.workshops_products_customers.ALL,
            db.workshops.ALL,
            db.workshops_products.Name,
            db.workshops_products.FullWorkshop,
            db.invoices.ALL,
            left=[db.workshops_products.on(
                db.workshops_products.id == \
                db.workshops_products_customers.workshops_products_id),
                db.workshops.on(db.workshops_products.workshops_id == \
                                db.workshops.id),
                db.invoices_workshops_products_customers.on(
                    db_icwspc.workshops_products_customers_id ==
                    db.workshops_products_customers.id),
                db.invoices.on(db_icwspc.invoices_id == db.invoices.id)
            ],
            orderby=~db.workshops.Startdate)

        return rows


    def get_invoices_rows(self,
                          public_group=True,
                          payments_only=False):
        """
            Returns invoices records for a customer as gluon.dal.rows object
        """
        db = current.db

        left = [
            db.invoices_amounts.on(
                db.invoices_amounts.invoices_id == db.invoices.id),
            db.invoices_groups.on(
                db.invoices.invoices_groups_id == db.invoices_groups.id),
            db.invoices_customers.on(
                db.invoices_customers.invoices_id ==
                db.invoices.id
            )
        ]
        query = (db.invoices_customers.auth_customer_id == self.cuID) & \
                (db.invoices.Status != 'draft')
        if public_group:
                (db.invoices_groups.PublicGroup == True)

        if payments_only:
            query &= (db.invoices.TeacherPayment == True)

        rows = db(query).select(db.invoices.ALL,
                                db.invoices_amounts.ALL,
                                left=left,
                                orderby=~db.invoices.DateCreated)

        return rows


    def get_orders_rows(self):
        """
            Returns orders for a customer
        """
        db = current.db

        query = (db.customers_orders.auth_customer_id == self.cuID)
        rows = db(query).select(
            db.customers_orders.ALL,
            db.customers_orders_amounts.ALL,
            db.invoices.ALL,
            db.invoices_amounts.ALL,
            left = [ db.customers_orders_amounts.on(db.customers_orders.id ==
                                                    db.customers_orders_amounts.customers_orders_id),
                     db.invoices_customers_orders.on(db.customers_orders.id ==
                                                     db.invoices_customers_orders.customers_orders_id),
                     db.invoices.on(db.invoices.id == db.invoices_customers_orders.invoices_id),
                     db.invoices_amounts.on(db.invoices_amounts.invoices_id == db.invoices.id)],
            orderby = ~db.customers_orders.id
        )

        return rows


    def get_orders_with_items_and_amounts(self):
        """
            Returns orders info for a customer with additional info
        """
        from openstudio.os_order import Order

        db = current.db

        orders = []
        rows = self.get_orders_rows()
        for i, row in enumerate(rows):
            repr_row = list(rows[i:i + 1].render())[0]

            order_obj = Order(row.customers_orders.id)
            order = {}
            order['row'] = row
            order['repr_row'] = repr_row
            order['items'] = order_obj.get_order_items_rows()

            orders.append(order)

        return orders


    def get_documents_rows(self):
        """
        :return: document rows for customer
        """
        db = current.db

        query = (db.customers_documents.auth_customer_id == self.cuID)
        return db(query).select(db.customers_documents.ALL)


    def has_recurring_reservation_for_class(self, clsID, date):
        '''
        :param clsID: db.classes.id
        :param date: datetime.date
        :return: Boolean
        '''
        db = current.db

        query = (db.classes_reservation.auth_customer_id == self.cuID) & \
                (db.classes_reservation.classes_id == clsID) & \
                (db.classes_reservation.Startdate <= date) & \
                ((db.classes_reservation.Enddate >= date) |
                 (db.classes_reservation.Enddate == None)) & \
                (db.classes_reservation.ResType == 'recurring')

        count = db(query).count()

        if count > 0:
            return True
        else:
            return False


    def get_reservations_rows(self, date=None, recurring_only=True):
        '''
            Returns upcoming reservations for this customer
        '''
        db = current.db

        left = [ db.classes.on(db.classes_reservation.classes_id == db.classes.id) ]

        query = (db.classes_reservation.auth_customer_id == self.cuID)
        if date:
            query &= (db.classes_reservation.Startdate <= date) & \
                     ((db.classes_reservation.Enddate >= date) |
                      (db.classes_reservation.Enddate == None))

        if recurring_only:
            query &= (db.classes_reservation.ResType == 'recurring')


        rows = db(query).select(db.classes_reservation.ALL,
                                db.classes.ALL,
                                left=left,
                                orderby=~db.classes_reservation.Startdate)

        return rows


    def get_classes_attendance_rows(self, limit=False, upcoming=False):
        '''
            @param limit: (int) number of attendance records to return
            @return: gluon.dal.rows obj with classes attendance rows for
            customer
        '''
        TODAY_LOCAL = current.TODAY_LOCAL
        db = current.db

        fields = [
            db.classes_attendance.id,
            db.classes_attendance.ClassDate,
            db.classes_attendance.AttendanceType,
            db.classes_attendance.customers_subscriptions_id,
            db.classes_attendance.customers_classcards_id,
            db.classes_attendance.auth_customer_id,
            db.classes_attendance.BookingStatus,
            db.classes.id,
            db.classes.school_locations_id,
            db.classes.school_classtypes_id,
            db.classes.school_levels_id,
            db.classes.Week_day,
            db.classes.Starttime,
            db.classes.Endtime,
            db.classes.Startdate,
            db.classes.Enddate,
            db.invoices.id,
            db.invoices.InvoiceID,
            db.invoices.Status,
            db.invoices.payment_methods_id,
            db.school_classcards.Name
        ]

        where_sql = ''
        if upcoming:
            where_sql = "AND clatt.ClassDate >= '{today}'".format(today=TODAY_LOCAL)
            limit = 20

        limit_sql = ''
        if limit:
            limit_sql = 'LIMIT ' + unicode(limit)

        orderby_sql = 'clatt.ClassDate DESC, cla.Starttime DESC'


        query = '''
        SELECT clatt.id,
               clatt.ClassDate,
               clatt.AttendanceType,
               clatt.customers_subscriptions_id,
               clatt.customers_classcards_id,
               clatt.auth_customer_id,
               clatt.BookingStatus,
               cla.id,
               CASE WHEN cotc.school_locations_id IS NOT NULL
                    THEN cotc.school_locations_id
                    ELSE cla.school_locations_id
                    END AS school_locations_id,
               CASE WHEN cotc.school_classtypes_id IS NOT NULL
                    THEN cotc.school_classtypes_id
                    ELSE cla.school_classtypes_id
                    END AS school_classtypes_id,
               cla.school_levels_id,
               cla.Week_day,
               CASE WHEN cotc.Starttime IS NOT NULL
                    THEN cotc.Starttime
                    ELSE cla.Starttime
                    END AS Starttime,
               CASE WHEN cotc.Endtime IS NOT NULL
                    THEN cotc.Endtime
                    ELSE cla.Endtime
                    END AS Endtime,
               cla.Startdate,
               cla.Enddate,
               inv.id,
               inv.InvoiceID,
               inv.Status,
               inv.payment_methods_id,
               scd.Name
        FROM classes_attendance clatt
        LEFT JOIN classes cla on cla.id = clatt.classes_id
        LEFT JOIN customers_classcards cd ON cd.id = clatt.customers_classcards_id
        LEFT JOIN school_classcards scd ON scd.id = cd.school_classcards_id
        LEFT JOIN
            invoices_classes_attendance ica
            ON ica.classes_attendance_id = clatt.id
        LEFT JOIN
            invoices inv ON ica.invoices_id = inv.id
        LEFT JOIN
            ( SELECT id,
                     classes_id,
                     ClassDate,
                     Status,
                     school_locations_id,
                     school_classtypes_id,
                     Starttime,
                     Endtime,
                     auth_teacher_id,
                     teacher_role,
                     auth_teacher_id2,
                     teacher_role2
              FROM classes_otc ) cotc
            ON clatt.classes_id = cotc.classes_id AND clatt.ClassDate = cotc.ClassDate
        WHERE clatt.auth_customer_id = {cuID}
        {where_sql}
        ORDER BY {orderby_sql}
        {limit_sql}
        '''.format(orderby_sql = orderby_sql,
                   where_sql = where_sql,
                   limit_sql = limit_sql,
                   cuID = self.cuID)

        rows = db.executesql(query, fields=fields)

        # print db._lastsql
        # print rows

        return rows


    def get_shoppingcart_rows(self):
        '''
            Get shopping cart rows for customer
        '''
        db = current.db

        left = [
            db.workshops_products.on(db.workshops_products.id == db.customers_shoppingcart.workshops_products_id),
            db.workshops.on(db.workshops.id == db.workshops_products.workshops_id),
            db.school_classcards.on(db.school_classcards.id == db.customers_shoppingcart.school_classcards_id),
            db.classes.on(db.classes.id == db.customers_shoppingcart.classes_id)
        ]

        query = (db.customers_shoppingcart.auth_customer_id == self.cuID)
        rows = db(query).select(db.customers_shoppingcart.ALL,
                                db.workshops.Name,
                                db.workshops.Startdate,
                                db.workshops_products.id,
                                db.workshops_products.Name,
                                db.workshops_products.Price,
                                db.workshops_products.tax_rates_id,
                                db.school_classcards.id,
                                db.school_classcards.Name,
                                db.school_classcards.Price,
                                db.school_classcards.Classes,
                                db.school_classcards.Unlimited,
                                db.school_classcards.tax_rates_id,
                                db.classes.id,
                                db.classes.school_classtypes_id,
                                db.classes.school_locations_id,
                                db.classes.Starttime,
                                db.classes.Endtime,
                                left=left)

        return rows


    def shoppingcart_maintenance(self):
        '''
            Do some housekeeping to keep things neat and tidy
        '''
        messages = []
        message = self.shoppingcart_remove_past_classes()
        if message:
            messages.append(message)

        return messages


    def shoppingcart_remove_past_classes(self):
        """
            Check if a class is already past, if so, remove it from the shopping cart.
        """
        from openstudio.openstudio import Class

        import pytz

        T = current.T
        db = current.db
        now = current.NOW_LOCAL
        TIMEZONE = current.TIMEZONE

        message = False

        query = (db.customers_shoppingcart.auth_customer_id == self.cuID) & \
                (db.customers_shoppingcart.classes_id != None)
        rows = db(query).select(db.customers_shoppingcart.id,
                                db.customers_shoppingcart.classes_id,
                                db.customers_shoppingcart.ClassDate)
        for row in rows:
            cls = Class(row.classes_id, row.ClassDate)

            if cls.is_past():
                del_query = (db.customers_shoppingcart.id == row.id)
                db(query).delete()

                message = T('One past class was removed from your shopping cart')

        return message


    def get_mollie_mandates(self):
        """
            Returns mollie mandates
        """
        get_sys_property = current.globalenv['get_sys_property']

        import Mollie
        # init mollie
        mollie = Mollie.API.Client()
        mollie_api_key = get_sys_property('mollie_website_profile')
        mollie.setApiKey(mollie_api_key)

        # check if we have a mollie customer id
        if self.row.mollie_customer_id:
            mollie_customer_id = self.row.mollie_customer_id
            #print mollie_customer_id
        else:
            # create one
            mollie_customer = mollie.customers.create({
                'name': self.row.display_name,
                'email': self.row.email
            })
            mollie_customer_id = mollie_customer['id']
            self.row.mollie_customer_id = mollie_customer_id
            self.row.update_record()

        return mollie.customer_mandates.withParentId(mollie_customer_id).all()


    def get_accepted_documents(self):
        """
        :return: rows object with rows of accepted documents for this customer
        """
        db = current.db

        query = (db.log_customers_accepted_documents.auth_customer_id == self.cuID)
        rows = db(query).select(db.log_customers_accepted_documents.ALL,
                                orderby=db.log_customers_accepted_documents.CreatedOn)
        return rows


    def log_document_acceptance(self,
                                document_name,
                                document_description='',
                                document_version='',
                                document_url=''):
        """
            :return:
        """
        db = current.db

        version = db.sys_properties(Property='Version').PropertyValue
        release = db.sys_properties(Property='VersionRelease').PropertyValue

        db.log_customers_accepted_documents.insert(
            auth_customer_id = self.cuID,
            DocumentName = document_name,
            DocumentDescription = document_description,
            DocumentVersion = document_version,
            DocumentURL = document_url,
            OpenStudioVersion = '.'.join([version, release])
        )


