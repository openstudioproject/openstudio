# -*- coding: utf-8 -*-

import datetime
from decimal import Decimal, ROUND_HALF_UP

from gluon import *


class Receipt:
    """
    Class that contains functions for a receipt
    """
    def __init__(self, rID):
        """
        Init function for an receipt
        """
        db = current.db

        self.receipts_id = rID
        self.row = db.receipts(rID)

        # New receipt?
        query = (db.receipts_amounts.receipts_id == self.receipts_id)
        if not db(query).count():
            self.on_create()


    def on_create(self):
        """
        functions to be called when creating an receipt
        """
        self._insert_amounts()


    def on_update(self):
        """
        functions to be called when updating an receipt or receipt items
        """
        pass


    def _set_updated_at(self):
        """
        Set db.receipts.Updated_at to current time (UTC)
        """
        self.row.Updated_at = datetime.datetime.now()
        self.row.update_record()


    def _insert_amounts(self):
        """
            Insert amounts row for receipt, without data
        """
        db = current.db
        db.receipts_amounts.insert(receipts_id = self.receipts_id)


    def set_amounts(self):
        """
            Set subtotal, vat and total incl vat
        """
        db = current.db
        # set sums
        sum_subtotal = db.receipts_items.TotalPrice.sum()
        sum_vat = db.receipts_items.VAT.sum()
        sum_totalvat = db.receipts_items.TotalPriceVAT.sum()

        # get info from db
        query = (db.receipts_items.receipts_id == self.receipts_id)
        rows = db(query).select(sum_subtotal,
                                sum_vat,
                                sum_totalvat)

        sums = rows.first()
        subtotal = sums[sum_subtotal]
        vat      = sums[sum_vat]
        total    = sums[sum_totalvat]

        if subtotal is None:
            subtotal = 0
        if vat is None:
            vat = 0
        if total is None:
            total = 0

        # check if we have any payments
        paid = self.get_amount_paid()
        balance = self.get_balance()

        # check what to do
        amounts = db.receipts_amounts(receipts_id = self.receipts_id)
        if amounts:
            # update current row
            amounts.TotalPrice    = subtotal
            amounts.VAT           = vat
            amounts.TotalPriceVAT = total
            amounts.Paid          = paid
            amounts.Balance       = balance
            amounts.update_record()
        else:
            # insert new row
            db.receipts_amounts.insert(
                receipts_id   = self.receipts_id,
                TotalPrice    = subtotal,
                VAT           = vat,
                TotalPriceVAT = total,
                Paid          = paid,
                Balance       = balance)


        self.on_update()


    def get_amounts(self):
        """
            Get subtotal, vat and total incl vat
        """
        db = current.db

        amounts = db.receipts_amounts(receipts_id = self.receipts_id)

        return amounts


    def get_amounts_tax_rates(self, formatted=False):
        """
            Returns vat for each tax rate as list sorted by tax rate percentage
            format: [ [ Name, Amount ] ]
        """
        db = current.db
        iID = self.receipts_id
        CURRSYM = current.globalenv['CURRSYM']

        amounts_vat = []
        rows = db().select(db.tax_rates.id, db.tax_rates.Name,
                           orderby=db.tax_rates.Percentage)
        for row in rows:
            sum = db.receipts_items.VAT.sum()
            query = (db.receipts_items.receipts_id == iID) & \
                    (db.receipts_items.tax_rates_id == row.id)

            result = db(query).select(sum).first()

            if not result[sum] is None:
                if formatted:
                    amount = SPAN(CURRSYM, ' ', format(result[sum], '.2f'))
                else:
                    amount = result[sum]
                amounts_vat.append({'Name'   : row.Name,
                                    'Amount' : amount})

        return amounts_vat


    def get_studio_info(self):
        """
        :return: dict with studio info
        """
        ORGANIZATIONS = current.globalenv['ORGANIZATIONS']

        try:
            organization = ORGANIZATIONS[ORGANIZATIONS['default']]

            company_name = organization['Name']
            company_address = organization['Address']
            company_email = organization['Email'] or ''
            company_phone = organization['Phone'] or ''
            company_registration = organization['Registration'] or ''
            company_tax_registration = organization['TaxRegistration'] or ''
        except KeyError:
            company_name = ''
            company_address = ''
            company_email = ''
            company_phone = ''
            company_registration = ''
            company_tax_registration = ''

        return dict(
            name = company_name,
            address = company_address,
            email = company_email,
            phone = company_phone,
            registration = company_registration,
            tax_registration = company_tax_registration,
        )


    def get_item_next_sort_nr(self):
        """
            Returns the next item number for an receipt
            use to set sorting when adding an item
        """
        db = current.db
        query = (db.receipts_items.receipts_id == self.receipts_id)

        return db(query).count() + 1


    def get_receipt_items_rows(self):
        """
            :return: db.customers_orders_items rows for order
        """
        db = current.db

        query = (db.receipts_items.receipts_id == self.receipts_id)
        rows = db(query).select(db.receipts_items.ALL,
                                orderby=db.receipts_items.Sorting)

        return rows


    def get_payment_method(self):
        """
        :return: db.payment_methods_row for receipt
        """
        db = current.db

        if self.receipts.payment_methods_id:
            return db.payment_methods(self.receipt.payment_methods_id)
        else:
            return None
        
        
    def receipt_item_add_product_variant(self, pvID, quantity):
        """
        
        :return: 
        """
        db = current.db
        
        sorting = self.get_item_next_sort_nr()
        variant = db.shop_products_variants(pvID)
        product = db.shop_products(variant.shop_products_id)
        
        reID = db.receipts_items.insert(
            receipts_id = self.receipts_id,
            Sorting = sorting,
            ProductName = product.Name,
            Description = variant.Name,
            Quantity = quantity,
            Price = variant.Price,
            tax_rates_id = variant.tax_rates_id,
            GLAccount = variant.GLAccount
        )

        return reID


    def item_add_class(self,
                       cuID,
                       caID,
                       clsID,
                       date,
                       product_type):
        """
        Add receipt item when checking in to a class

        :param cuID: db.auth_user.id
        :param caID: db.classes_attendance.id
        :param clsID: db.classes.id
        :param date: datetime.date (class date)
        :param product_type: has to be 'trial' or 'dropin'
        :return:
        """
        from os_customer import Customer
        from os_class import Class

        db = current.db
        DATE_FORMAT = current.DATE_FORMAT
        T = current.T

        date_formatted = date.strftime(DATE_FORMAT)

        if product_type not in ['trial', 'dropin']:
            raise ValueError("Product type has to be 'trial' or 'dropin'.")

        customer = Customer(cuID)
        cls = Class(clsID, date)
        prices = cls.get_prices()

        has_membership = customer.has_membership_on_date(date)

        if product_type == 'dropin':
            price = prices['dropin']
            tax_rates_id = prices['dropin_tax_rates_id']
            glaccount = prices['dropin_glaccount']

            if has_membership and prices['dropin_membership']:
                price = prices['dropin_membership']
                tax_rates_id = prices['dropin_tax_rates_id_membership']

            description = cls.get_receipt_order_description(2) # 2 = drop in class

        elif product_type == 'trial':
            price = prices['trial']
            tax_rates_id = prices['trial_tax_rates_id']
            glaccount = prices['trial_glaccount']

            if has_membership and prices['trial_membership']:
                price = prices['trial_membership']
                tax_rates_id = prices['trial_tax_rates_id_membership']

            description = cls.get_receipt_order_description(1) # 1 = trial class

        # link receipt to attendance
        self.link_to_classes_attendance(caID)

        next_sort_nr = self.get_item_next_sort_nr()
        iiID = db.receipts_items.insert(
            receipts_id=self.receipts_id,
            ProductName=T("Class"),
            Description=description,
            Quantity=1,
            Price=price,
            Sorting=next_sort_nr,
            tax_rates_id=tax_rates_id,
            GLAccount=glaccount
        )

        self.link_to_customer(cuID)
        # This calls self.on_update()
        self.set_amounts()


    def item_add_class_from_order(self, order_item_row, caID):
        """
            Add class to receipt from Order.deliver()

            :param clsID: db.classes.id
            :param class_date: datetime.date
            :param attendance_type: int 1 or 2 
            :return: db.receipts_items.id
        """
        from os_class import Class

        DATE_FORMAT = current.DATE_FORMAT
        TIME_FORMAT = current.TIME_FORMAT
        db = current.db
        T  = current.T

        cls = Class(order_item_row.classes_id, order_item_row.ClassDate)

        # Get GLAccount info
        prices = cls.get_prices()
        glaccount = None
        if order_item_row.AttendanceType == 1:
            # Trial
            glaccount = prices['trial_glaccount']
        else:
            # Drop in
            glaccount = prices['dropin_glaccount']

        # link receipt to attendance
        db.receipts_classes_attendance.insert(
            receipts_id=self.receipts_id,
            classes_attendance_id=caID
        )

        # add item to receipt
        next_sort_nr = self.get_item_next_sort_nr()

        iiID = db.receipts_items.insert(
            receipts_id=self.receipts_id,
            ProductName=order_item_row.ProductName,
            Description=order_item_row.Description,
            Quantity=order_item_row.Quantity,
            Price=order_item_row.Price,
            Sorting=next_sort_nr,
            tax_rates_id=order_item_row.tax_rates_id,
            GLAccount=glaccount
        )

        # This calls self.on_update()
        self.set_amounts()

        return iiID


    def item_add_classcard(self, ccdID):
        """
            :param ccdID: Add customer classcard to receipt
            :return: None
        """
        from os_customer_classcard import CustomerClasscard

        db = current.db
        T  = current.T

        classcard = CustomerClasscard(ccdID)
        # link receipt to classcard sold to customer
        db.receipts_customers_classcards.insert(
            receipts_id=self.receipts_id,
            customers_classcards_id=ccdID
        )

        # add item to receipt
        next_sort_nr = self.get_item_next_sort_nr()
        price = classcard.price

        iiID = db.receipts_items.insert(
            receipts_id=self.receipts_id,
            ProductName=T("Class card"),
            Description=classcard.name.decode('utf-8') + u' (' + T("Class card") + u' ' + unicode(ccdID) + u')',
            Quantity=1,
            Price=price,
            Sorting=next_sort_nr,
            tax_rates_id=classcard.school_classcard.tax_rates_id,
            GLAccount=classcard.glaccount
        )

        # This calls self.on_update()
        self.set_amounts()

        return iiID

    #
    # def item_add_workshop_product(self, wspcID):
    #     """
    #         :param wspID: db.workshops_products_id
    #         :return: db.receipts_items.id
    #     """
    #     DATE_FORMAT = current.DATE_FORMAT
    #     db = current.db
    #     T  = current.T
    #
    #     wspc = db.workshops_products_customers(wspcID)
    #     wsp = db.workshops_products(wspc.workshops_products_id)
    #     ws = db.workshops(wsp.workshops_id)
    #     # Link receipt to workshop product sold to customer
    #     db.receipts_workshops_products_customers.insert(
    #         receipts_id = self.receipts_id,
    #         workshops_products_customers_id = wspcID
    #     )
    #
    #     # Add item to receipt
    #     next_sort_nr = self.get_item_next_sort_nr()
    #
    #     iiID = db.receipts_items.insert(
    #         receipts_id=self.receipts_id,
    #         ProductName=T('Event'),
    #         Description=ws.Name.decode('utf-8') + u' - ' + wsp.Name.decode('utf-8') + ' [' + ws.Startdate.strftime(DATE_FORMAT) + ']',
    #         Quantity=1,
    #         Price=wsp.Price,
    #         Sorting=next_sort_nr,
    #         tax_rates_id=wsp.tax_rates_id,
    #         GLAccount=wsp.GLAccount
    #     )
    #
    #     # This calls self.on_update()
    #     self.set_amounts()
    #
    #     return iiID
    #
    #
    # def item_add_donation(self, amount, description):
    #     """
    #         :param amount: donation amount
    #         :param description: donation description
    #         :return: db.customers_orders.items.id of inserted item
    #     """
    #     db = current.db
    #     T  = current.T
    #     get_sys_property = current.globalenv['get_sys_property']
    #
    #     sys_property = 'shop_donations_tax_rates_id'
    #     tax_rates_id = int(get_sys_property(sys_property))
    #
    #     # add item to receipt
    #     next_sort_nr = self.get_item_next_sort_nr()
    #     price = amount
    #
    #     iiID = db.receipts_items.insert(
    #         receipts_id=self.receipts_id,
    #         ProductName=T("Donation"),
    #         Description=description.decode('utf-8'),
    #         Quantity=1,
    #         Price=price,
    #         Sorting=next_sort_nr,
    #         tax_rates_id=tax_rates_id,
    #     )
    #
    #     # This calls self.on_update()
    #     self.set_amounts()
    #
    #     return iiID


    def item_add_subscription(self, SubscriptionYear, SubscriptionMonth, description=''):
        """
            :param SubscriptionYear: Year of subscription
            :param SubscriptionMonth: Month of subscription
            :return: db.receipts_items.id
        """
        from general_helpers import get_last_day_month

        from os_customer_subscription import CustomerSubscription
        from os_school_subscription import SchoolSubscription

        db = current.db
        DATE_FORMAT = current.DATE_FORMAT

        next_sort_nr = self.get_item_next_sort_nr()

        date = datetime.date(int(SubscriptionYear),
                             int(SubscriptionMonth),
                             1)

        ics = db.receipts_customers_subscriptions(receipts_id = self.receipts_id)
        csID = ics.customers_subscriptions_id
        cs = CustomerSubscription(csID)
        ssuID = cs.ssuID
        ssu = SchoolSubscription(ssuID)
        row = ssu.get_tax_rates_on_date(date)

        if row:
            tax_rates_id = row.school_subscriptions_price.tax_rates_id
        else:
            tax_rates_id = None

        period_start = date
        period_end = get_last_day_month(date)
        glaccount = ssu.get_glaccount_on_date(date)
        price = 0

        # check for alt price
        csap = db.customers_subscriptions_alt_prices
        query = (csap.customers_subscriptions_id == csID) & \
                (csap.SubscriptionYear == SubscriptionYear) & \
                (csap.SubscriptionMonth == SubscriptionMonth)
        csap_rows = db(query).select(csap.ALL)
        if csap_rows:
            csap_row = csap_rows.first()
            price    = csap_row.Amount
            description = csap_row.Description
        else:
            price = ssu.get_price_on_date(date, False)

            broken_period = False
            if cs.startdate > date and cs.startdate <= period_end:
                # Start later in month
                broken_period = True
                period_start = cs.startdate
                delta = period_end - cs.startdate
                cs_days = delta.days + 1
                total_days = period_end.day

            if cs.enddate:
                if cs.enddate >= date and cs.enddate < period_end:
                    # End somewhere in month
                    broken_period = True

                    delta = cs.enddate - date
                    cs_days = delta.days + 1
                    total_days = period_end.day

                    period_end = cs.enddate

            if broken_period:
                price = round(float(cs_days) / float(total_days) * float(price), 2)

            if not description:
                description = cs.name.decode('utf-8') + u' ' + period_start.strftime(DATE_FORMAT) + u' - ' + period_end.strftime(DATE_FORMAT)

        iiID = db.receipts_items.insert(
            receipts_id = self.receipts_id,
            ProductName = current.T("Subscription") + ' ' + unicode(csID),
            Description = description,
            Quantity = 1,
            Price = price,
            Sorting = next_sort_nr,
            tax_rates_id = tax_rates_id,
            GLAccount = glaccount
        )

        ##
        # Check if a registration fee should be added
        ##
        query = (((db.customers_subscriptions.auth_customer_id == cs.auth_customer_id) &
                 (db.customers_subscriptions.id != cs.csID) &
                 (db.customers_subscriptions.school_subscriptions_id == cs.ssuID)) |
                 (db.customers_subscriptions.RegistrationFeePaid == True))

        fee_paid_in_past = db(query).count()
        ssu = db.school_subscriptions(ssuID)
        if not fee_paid_in_past and ssu.RegistrationFee: # Registration fee not already paid and RegistrationFee defined?
            regfee_to_be_paid = ssu.RegistrationFee or 0
            if regfee_to_be_paid:
                db.receipts_items.insert(
                    receipts_id = self.receipts_id,
                    ProductName = current.T("Registration fee"),
                    Description = current.T('One time registration fee'),
                    Quantity = 1,
                    Price = regfee_to_be_paid,
                    Sorting = next_sort_nr,
                    tax_rates_id = tax_rates_id,
                )

                # Mark registration fee as paid for subscription
                db.customers_subscriptions[cs.csID] = dict(RegistrationFeePaid=True)

        ##
        # Always call these
        ##
        # This calls self.on_update()
        self.set_amounts()

        return iiID


    def item_add_membership(self, cmID, period_start, period_end):
        """
        :param cmID: db.customers_memberships.id
        :return: db.receipts_items.id
        """
        from openstudio.os_customer_membership import CustomerMembership
        from openstudio.os_school_membership import SchoolMembership

        db = current.db
        DATE_FORMAT = current.DATE_FORMAT

        next_sort_nr = self.get_item_next_sort_nr()

        cm = CustomerMembership(cmID)
        sm = SchoolMembership(cm.row.school_memberships_id)
        price_rows = sm.get_price_rows_on_date(period_start)

        if not price_rows:
            return # Don't do anything if we don't have a price

        price_row = price_rows.first()
        tax_rates_id = price_row.tax_rates_id
        price = price_row.Price

        if price == 0:
            return # Don't do anything if the price is 0

        description = cm.get_name() + ' ' + \
                      period_start.strftime(DATE_FORMAT) + ' - ' + \
                      period_end.strftime(DATE_FORMAT)

        iiID = db.receipts_items.insert(
            receipts_id = self.receipts_id,
            ProductName = current.T("Membership") + ' ' + unicode(cmID),
            Description = description,
            Quantity = 1,
            Price = price,
            Sorting = next_sort_nr,
            tax_rates_id = tax_rates_id,
            GLAccount = sm.row.GLAccount
        )

        self.link_to_customer_membership(cmID)
        # This calls self.on_update()
        self.set_amounts()

        return iiID


    def payment_add(self,
                    amount,
                    date,
                    payment_methods_id,
                    note=None,
                    mollie_payment_id=None):
        """
            Add payment to receipt
        """
        db = current.db

        ipID = db.receipts_payments.insert(
            receipts_id = self.receipts_id,
            Amount = amount,
            PaymentDate = date,
            payment_methods_id = payment_methods_id,
            Note = note,
            mollie_payment_id = mollie_payment_id
        )

        self.is_paid()
        self.on_update()

        return ipID
