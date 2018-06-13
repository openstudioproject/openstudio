# -*- coding: utf-8 -*-

import datetime

from general_helpers import get_last_day_month

from gluon import *


class CustomerSubscription:
    """
        Class that contains functions for customer subscriptions
    """
    def __init__(self, csID):
        """
            Class init function which sets csID
        """
        db = current.db

        self.csID = csID
        self.cs = db.customers_subscriptions(csID)

        self.ssuID = self.cs.school_subscriptions_id
        self.ssu   = db.school_subscriptions(self.ssuID)

        self.name               = self.ssu.Name
        self.auth_customer_id   = self.cs.auth_customer_id
        self.payment_methods_id = self.cs.payment_methods_id
        self.startdate          = self.cs.Startdate
        self.enddate            = self.cs.Enddate


    def create_invoice_for_month(self, SubscriptionYear, SubscriptionMonth):
        """
            :param SubscriptionYear: Year of subscription
            :param SubscriptionMonth: Month of subscription
        """
        from os_invoice import Invoice

        db = current.db
        TODAY_LOCAL = current.TODAY_LOCAL
        DATE_FORMAT = current.DATE_FORMAT

        # create invoice linked to subscription for first subscription term to know the right amount.
        SubscriptionYear = TODAY_LOCAL.year
        SubscriptionMonth = TODAY_LOCAL.month

        firstdaythismonth = datetime.date(SubscriptionYear, SubscriptionMonth, 1)
        lastdaythismonth = get_last_day_month(firstdaythismonth)

        left = [ db.invoices_customers_subscriptions.on(
            db.invoices_customers_subscriptions.invoices_id ==
            db.invoices.id
        )]

        # Check if an invoice already exists, if so, return invoice id
        query = (db.invoices_customers_subscriptions.customers_subscriptions_id == self.csID) & \
                (db.invoices.SubscriptionYear == SubscriptionYear) & \
                (db.invoices.SubscriptionMonth == SubscriptionMonth)
        rows = db(query).select(db.invoices.ALL,
                                left=left)
        if len(rows):
            return rows.first().id

        # Check if the subscription is paused
        query = (db.customers_subscriptions_paused.customers_subscriptions_id == self.csID) & \
                (db.customers_subscriptions_paused.Startdate <= lastdaythismonth) & \
                ((db.customers_subscriptions_paused.Enddate >= firstdaythismonth) |
                 (db.customers_subscriptions_paused.Enddate == None))
        if db(query).count():
            return

        # Check if an alt. price with amount 0 has been defined
        csap = db.customers_subscriptions_alt_prices
        query = (csap.customers_subscriptions_id == self.csID) & \
                (csap.SubscriptionYear == SubscriptionYear) & \
                (csap.SubscriptionMonth == SubscriptionMonth)
        csap_rows = db(query).select(csap.ALL)
        if csap_rows:
            csap_row = csap_rows.first()
            if csap_row.Amount == 0:
                return

        # Ok we've survived all checks, continue with invoice creation
        igpt = db.invoices_groups_product_types(ProductType='subscription')
        igID = igpt.invoices_groups_id

        if TODAY_LOCAL > firstdaythismonth:
            period_begin = TODAY_LOCAL
        else:
            period_begin = firstdaythismonth

        period_end = lastdaythismonth
        if self.enddate:
            if self.startdate >= firstdaythismonth and \
               self.enddate < lastdaythismonth:
                period_end = self.enddate

        item_description = period_begin.strftime(DATE_FORMAT) + ' - ' + \
                           period_end.strftime(DATE_FORMAT)

        iID = db.invoices.insert(
            invoices_groups_id=igID,
            payment_methods_id=self.payment_methods_id,
            customers_subscriptions_id=self.csID,
            SubscriptionYear=SubscriptionYear,
            SubscriptionMonth=SubscriptionMonth,
            Description='',
            Status='sent'
        )

        # create object to set Invoice# and due date
        invoice = Invoice(iID)
        invoice.link_to_customer(self.auth_customer_id)
        invoice.link_to_customer_subscription(self.csID)
        invoice.item_add_subscription(SubscriptionYear, SubscriptionMonth)

        return iID


    def get_credits_balance(self):
        """
            Calculate total credits remaining for a subscription
        """
        db = current.db

        sum = db.customers_subscriptions_credits.MutationAmount.sum()

        query = (db.customers_subscriptions_credits.MutationType == 'add') & \
                (db.customers_subscriptions_credits.customers_subscriptions_id == self.csID)
        add_total = db(query).select(sum).first()[sum] or 0

        query = (db.customers_subscriptions_credits.MutationType == 'sub') & \
                (db.customers_subscriptions_credits.customers_subscriptions_id == self.csID)
        sub_total = db(query).select(sum).first()[sum] or 0

        return round(add_total - sub_total, 1)


    def get_credits_mutations_rows(self,
                                   formatted=False,
                                   editable=False,
                                   deletable=False,
                                   delete_controller='',
                                   delete_function=''):
        """
            Returns raw rows of credit mutations for a subscription
        """
        os_gui = current.globalenv['os_gui']
        auth = current.auth
        db = current.db
        T = current.T

        left = [ db.classes_attendance.on(db.customers_subscriptions_credits.classes_attendance_id ==
                                          db.classes_attendance.id),
                 db.classes.on(db.classes_attendance.classes_id ==
                               db.classes.id) ]

        query = (db.customers_subscriptions_credits.customers_subscriptions_id == self.csID)
        rows = db(query).select(db.customers_subscriptions_credits.ALL,
                                db.classes.Starttime,
                                db.classes.Endtime,
                                db.classes.school_locations_id,
                                db.classes.school_classtypes_id,
                                db.classes_attendance.auth_customer_id,
                                db.classes_attendance.ClassDate,
                                left=left,
                                orderby=~db.customers_subscriptions_credits.MutationDateTime)

        if not formatted:
            return rows
        else:
            edit_permission = (auth.has_membership(group_id='Admins') or
                               auth.has_permission('update', 'customers_subscriptions_credits'))

            delete_permission = (auth.has_membership(group_id='Admins') or
                                 auth.has_permission('delete', 'customers_subscriptions_credits'))

            header = THEAD(TR(TH(T('Date')),
                              TH(T('Description')),
                              TH(T('Credits')),
                              TH(db.customers_subscriptions_credits.MutationType.label), # MutationType
                              TH(),
                              ))

            table = TABLE(header, _class='table table-striped table-hover')
            for i, row in enumerate(rows):
                repr_row = list(rows[i:i + 1].render())[0]

                csID = row.customers_subscriptions_credits.customers_subscriptions_id
                cuID = self.auth_customer_id

                delete = ''
                edit = ''
                if deletable and delete_permission:
                    confirm_msg = T("Really delete this mutation?")
                    onclick_del = "return confirm('" + confirm_msg + "');"

                    rvars = {'csID':csID,
                             'cuID':cuID,
                             'cscID':row.customers_subscriptions_credits.id}

                    delete = os_gui.get_button('delete_notext',
                                               URL(delete_controller, delete_function, vars=rvars),
                                               onclick=onclick_del,
                                               _class='pull-right')
                if editable and edit_permission:
                    edit = os_gui.get_button('edit',
                        URL('customers', 'subscription_credits_edit', vars=rvars))

                buttons = DIV(edit, delete, _class='pull-right')

                tr = TR(TD(repr_row.customers_subscriptions_credits.MutationDateTime),
                        TD(repr_row.customers_subscriptions_credits.Description),
                        TD(repr_row.customers_subscriptions_credits.MutationAmount),
                        TD(SPAN(repr_row.customers_subscriptions_credits.MutationType)),
                        TD(buttons))

                table.append(tr)

            return table


    def add_credits_month(self, year, month):
        """
            Add credits for selected month
        """
        from os_customers_subscriptions_credits import CustomersSubscriptionsCredits

        first_day = datetime.date(year, month, 1)
        last_day = get_last_day_month(first_day)

        if self.cs.Startdate <= first_day:
            p_start = first_day
        else:
            p_start = self.cs.Startdate

        if self.cs.Enddate is None or self.cs.Enddate >= last_day:
            p_end = last_day
        else:
            p_end = self.cs.Enddate

        csch = CustomersSubscriptionsCredits()
        csch.add_subscription_credits_month(
            self.csID,
            self.cs.auth_customer_id,
            year,
            month,
            p_start,
            p_end,
            self.ssu.Classes,
            self.ssu.SubscriptionUnit,
            batch_add=False,
            book_classes=False)


    def _get_allowed_classes_format(self, class_ids):
        """
            :param class_ids: list of db.classes.id
            :return: html table
        """
        T = current.T
        db = current.db
        TODAY_LOCAL = current.TODAY_LOCAL

        query = (db.classes.AllowAPI == True) & \
                (db.classes.id.belongs(class_ids)) & \
                (db.classes.Startdate <= TODAY_LOCAL) & \
                ((db.classes.Enddate == None) |
                 (db.classes.Enddate >= TODAY_LOCAL))
        rows = db(query).select(db.classes.ALL,
                                orderby=db.classes.Week_day|db.classes.Starttime|db.classes.school_locations_id)

        header = THEAD(TR(TH(T('Day')),
                          TH(T('Time')),
                          TH(T('Location')),
                          TH(T('Class'))))
        table = TABLE(header, _class='table table-striped table-hover')
        for i, row in enumerate(rows):
            repr_row = list(rows[i:i + 1].render())[0]

            tr = TR(TD(repr_row.Week_day),
                    TD(repr_row.Starttime, ' - ', repr_row.Endtime),
                    TD(repr_row.school_locations_id),
                    TD(repr_row.school_classtypes_id))

            table.append(tr)

        return table


    def get_allowed_classes_enrollment(self, public_only=True, formatted=False):
        """
            :return: return: list of db.classes.db that are allowed to be enrolled in using this subscription
        """
        permissions = self.get_class_permissions(public_only=public_only)
        class_ids = []
        for clsID in permissions:
            try:
                if permissions[clsID]['Enroll']:
                    class_ids.append(clsID)
            except KeyError:
                pass

        if not formatted:
            return class_ids
        else:
            return self._get_allowed_classes_format(class_ids)


    def get_allowed_classes_booking(self, public_only=True, formatted=False):
        """
            :return: return: list of db.classes.db that are allowed to be booked using this subscription
        """
        permissions = self.get_class_permissions(public_only=public_only)
        class_ids = []
        for clsID in permissions:
            try:
                if permissions[clsID]['ShopBook']:
                    class_ids.append(clsID)
            except KeyError:
                pass


        if not formatted:
            return class_ids
        else:
            return self._get_allowed_classes_format(class_ids)


    def get_allowed_classes_attend(self, public_only=True, formatted=False):
        """
            :return: return list of db.classes that are allowed to be attended using this subscription
        """
        permissions = self.get_class_permissions(public_only=public_only)
        class_ids = []
        for clsID in permissions:
            try:
                if permissions[clsID]['Attend']:
                    class_ids.append(clsID)
            except KeyError:
                pass


        if not formatted:
            return class_ids
        else:
            return self._get_allowed_classes_format(class_ids)


    def _get_class_permissions_format(self, permissions):
        """
            :param permissions: dictionary of class permissions
            :return: html table
        """
        T = current.T
        db = current.db
        os_gui = current.globalenv['os_gui']
        TODAY_LOCAL = current.TODAY_LOCAL

        class_ids = []
        for clsID in permissions:
            class_ids.append(clsID)

        query = (db.classes.AllowAPI == True) & \
                (db.classes.id.belongs(class_ids)) & \
                (db.classes.Startdate <= TODAY_LOCAL) & \
                ((db.classes.Enddate == None) |
                 (db.classes.Enddate >= TODAY_LOCAL))
        rows = db(query).select(db.classes.ALL,
                                orderby=db.classes.Week_day|db.classes.Starttime|db.classes.school_locations_id)

        header = THEAD(TR(TH(T('Day')),
                          TH(T('Time')),
                          TH(T('Location')),
                          TH(T('Class')),
                          TH(T('Enroll')),
                          TH(T('Book in advance')),
                          TH(T('Attend'))))

        table = TABLE(header, _class='table table-striped table-hover')
        green_check = SPAN(os_gui.get_fa_icon('fa-check'), _class='text-green')

        for i, row in enumerate(rows):
            repr_row = list(rows[i:i + 1].render())[0]

            class_permission = permissions[row.id]
            enroll = class_permission.get('Enroll', '')
            shopbook = class_permission.get('ShopBook', '')
            attend = class_permission.get('Attend', '')

            if enroll:
                enroll = green_check

            if shopbook:
                shopbook = green_check

            if attend:
                attend = green_check

            tr = TR(TD(repr_row.Week_day),
                    TD(repr_row.Starttime, ' - ', repr_row.Endtime),
                    TD(repr_row.school_locations_id),
                    TD(repr_row.school_classtypes_id),
                    TD(enroll),
                    TD(shopbook),
                    TD(attend))

            table.append(tr)

        return table



    def get_class_permissions(self, public_only=True, formatted=False):
        """
            :return: return list of class permissons (clsID: enroll, book in shop, attend)
        """
        db = current.db

        # get groups for subscription
        query = (db.school_subscriptions_groups_subscriptions.school_subscriptions_id == self.ssuID)
        rows = db(query).select(db.school_subscriptions_groups_subscriptions.school_subscriptions_groups_id)

        group_ids = []
        for row in rows:
            group_ids.append(row.school_subscriptions_groups_id)

        # get permissions for subscription group
        left = [db.classes.on(db.classes_school_subscriptions_groups.classes_id == db.classes.id)]
        query = (db.classes_school_subscriptions_groups.school_subscriptions_groups_id.belongs(group_ids))

        if public_only:
            query &= (db.classes.AllowAPI == True)

        rows = db(query).select(db.classes_school_subscriptions_groups.ALL,
                                left=left)

        permissions = {}
        for row in rows:
            clsID = row.classes_id
            if clsID not in permissions:
                permissions[clsID] = {}

            if row.Enroll:
                permissions[clsID]['Enroll'] = True
            if row.ShopBook:
                permissions[clsID]['ShopBook'] = True
            if row.Attend:
                permissions[clsID]['Attend'] = True

        if not formatted:
            return permissions
        else:
            return self._get_class_permissions_format(permissions)
        