# -*- coding: utf-8 -*-

import datetime

from gluon import *


class Order:
    """
        Class containing functions for OpenStudio orders
    """
    def __init__(self, coID):
        """
            Init class
        """
        db = current.db

        self.coID = coID
        self.order = db.customers_orders(coID)


    def set_status_awaiting_payment(self):
        """
            Change status to 'awaiting_payment'
        """
        self.order.Status = 'awaiting_payment'
        self.order.update_record()


    def set_status_delivered(self):
        """
            Change status to 'awaiting_payment'
        """
        self.order.Status = 'delivered'
        self.order.update_record()


    def set_status_cancelled(self):
        """
            Change status to 'awaiting_payment'
        """
        self.order.Status = 'cancelled'
        self.order.update_record()


    def contains_subscription(self):
        """
        Returns True if there's a subscription in this order, else false
        :return:
        """
        db = current.db

        query = (db.customers_orders_items.customers_orders_id == self.coID) & \
                (db.customers_orders_items.school_subscriptions_id != None)

        if db(query).count():
            return True
        else:
            return False


    def order_item_add_product_variant(self, shop_product_variant_id, quantity=1):
        """
        :param shop_product_variant_id: db.shop_products_variants.id
        :return:
        """
        T = current.T
        db = current.db

        pv = db.shop_products_variants(shop_product_variant_id)
        product = db.shop_products(pv.shop_products_id)

        coiID = db.customers_orders_items.insert(
            customers_orders_id  = self.coID,
            ProductVariant = True,
            ProductName = product.Name,
            Description = pv.Name,
            Quantity = quantity,
            Price = pv.Price,
            tax_rates_id = pv.tax_rates_id,
            accounting_glaccounts_id = product.accounting_glaccounts_id,
            accounting_costcenters_id = product.accounting_costcenters_id,
        )

        self.set_amounts()

        # Link order item to product variant
        db.customers_orders_items_shop_products_variants.insert(
            customers_orders_items_id = coiID,
            shop_products_variants_id = shop_product_variant_id
        )

        return coiID


    def order_item_add_classcard(self, school_classcards_id):
        """
            :param school_classcards_id: db.school_classcards.id
            :return : db.customers_orders_items.id of inserted item
        """
        db = current.db
        T  = current.T

        school_classcard = db.school_classcards(school_classcards_id)

        coiID = db.customers_orders_items.insert(
            customers_orders_id  = self.coID,
            school_classcards_id = school_classcards_id,
            ProductName = T('Classcard'),
            Description = school_classcard.Name,
            Quantity = 1,
            Price = school_classcard.Price,
            tax_rates_id = school_classcard.tax_rates_id,
            accounting_glaccounts_id = school_classcard.accounting_glaccounts_id,
            accounting_costcenters_id = school_classcard.accounting_costcenters_id
        )

        self.set_amounts()

        return coiID


    def order_item_add_subscription(self, school_subscriptions_id, dummy_subscription=False):
        """
            :param school_subscriptions_id: db.school_subscriptions.id
            :return : db.customers_orders_items.id of inserted item
        """
        from general_helpers import get_first_day_next_month
        from .os_school_subscription import SchoolSubscription

        db = current.db
        T  = current.T
        TODAY_LOCAL = current.TODAY_LOCAL

        ssu = SchoolSubscription(school_subscriptions_id)
        ssu_tax_rates = ssu.get_tax_rates_on_date(TODAY_LOCAL)
        price = ssu.get_price_today(formatted=False)
        if dummy_subscription:
            price = ssu.get_price_on_date(get_first_day_next_month(TODAY_LOCAL), formatted=False)

        coiID = db.customers_orders_items.insert(
            customers_orders_id  = self.coID,
            DummySubscription = dummy_subscription,
            school_subscriptions_id = school_subscriptions_id if not dummy_subscription else None,
            ProductName = T('Subscription'),
            Description = ssu.get_name(),
            Quantity = 1,
            Price = price,
            tax_rates_id = ssu_tax_rates.tax_rates.id,
            accounting_glaccounts_id = ssu.get_glaccount_on_date(TODAY_LOCAL),
            accounting_costcenters_id = ssu.get_costcenter_on_date(TODAY_LOCAL),
        )

        self.set_amounts()

        return coiID

    def order_item_add_subscription_registration_fee(self, school_subscriptions_id):
        """
            :param school_subscriptions_id: db.school_subscriptions.id
            :return : db.customers_orders_items.id of inserted item
        """
        from .os_school_subscription import SchoolSubscription

        db = current.db
        T  = current.T
        TODAY_LOCAL = current.TODAY_LOCAL

        ssu = SchoolSubscription(school_subscriptions_id, set_db_info=True)
        ssu_tax_rates = ssu.get_tax_rates_on_date(TODAY_LOCAL)

        if ssu_tax_rates:
            tax_rates_id = ssu_tax_rates.school_subscriptions_price.tax_rates_id
        else:
            tax_rates_id = None

        coiID = db.customers_orders_items.insert(
            customers_orders_id  = self.coID,
            SubscriptionRegistrationFee = True,
            ProductName=current.T("Registration fee"),
            Description=current.T('One time registration fee'),
            Quantity = 1,
            Price = ssu.RegistrationFee,
            tax_rates_id = tax_rates_id,
            accounting_glaccounts_id = ssu.get_glaccount_on_date(TODAY_LOCAL),
            accounting_costcenters_id = ssu.get_costcenter_on_date(TODAY_LOCAL),
        )

        self.set_amounts()

        return coiID


    def order_item_add_membership(self, school_memberships_id, startdate):
        """
            :param school_memberships_id: db.school_memberships.id
            :return : db.customers_orders_items.id of inserted item
        """
        from .os_school_membership import SchoolMembership

        db = current.db
        T  = current.T

        sme = SchoolMembership(school_memberships_id)

        coiID = db.customers_orders_items.insert(
            customers_orders_id  = self.coID,
            school_memberships_id = school_memberships_id,
            ProductName = T('Membership'),
            Description = sme.row.Name,
            Quantity = 1,
            Price = sme.row.Price,
            tax_rates_id = sme.row.tax_rates_id,
            accounting_glaccounts_id = sme.row.accounting_glaccounts_id,
            accounting_costcenters_id = sme.row.accounting_costcenters_id,
        )

        self.set_amounts()

        return coiID


    def order_item_add_workshop_product(self, workshops_products_id):
        """
            :param workshops_products_id: db.workshops_products.id
            :return: db.customers_orders_items.id of inserted item
        """
        from .os_workshop_product import WorkshopProduct

        db = current.db
        T  = current.T

        wsp = WorkshopProduct(workshops_products_id)
        ws = wsp.workshop

        # Check for subscription price
        price = wsp.get_price_for_customer(self.order.auth_customer_id)


        coiID = db.customers_orders_items.insert(
            customers_orders_id = self.coID,
            workshops_products_id = workshops_products_id,
            ProductName = T('Event'),
            Description = ws.Name + ' - ' + wsp.name,
            Quantity = 1,
            Price = price,
            tax_rates_id = wsp.tax_rates_id,
            accounting_glaccounts_id = wsp.workshop_product.accounting_glaccounts_id,
            accounting_costcenters_id = wsp.workshop_product.accounting_costcenters_id
        )

        self.set_amounts()

        return coiID


    def order_item_add_donation(self, amount, description):
        """
            :param amount: donation amount
            :param description: donation description
            :return: db.customers_orders.items.id of inserted item 
        """
        db = current.db
        T  = current.T
        get_sys_property = current.globalenv['get_sys_property']

        sys_property = 'shop_donations_tax_rates_id'
        tax_rates_id = int(get_sys_property(sys_property))


        coiID = db.customers_orders_items.insert(
            customers_orders_id=self.coID,
            Donation=True,
            ProductName=T('Donation'),
            Description=description,
            Quantity=1,
            Price=amount,
            tax_rates_id=tax_rates_id,
        )

        self.set_amounts()

        return coiID


    def order_item_add_class(self, clsID, class_date, attendance_type, force_membership_price=False):
        """
            :param workshops_products_id: db.workshops_products.id
            :return: db.customers_orders_items.id of inserted item
        """
        from .os_class import Class

        DATE_FORMAT = current.DATE_FORMAT
        TIME_FORMAT = current.TIME_FORMAT
        db = current.db
        T  = current.T

        cls = Class(clsID, class_date)
        prices = cls.get_prices_customer(self.order.auth_customer_id, force_membership_price)

        if attendance_type == 1:
            price = prices['trial']
            tax_rates_id = prices['trial_tax_rates_id']
            glaccount = prices['trial_glaccount']
            costcenter = prices['trial_costcenter']
        elif attendance_type == 2:
            price = prices['dropin']
            tax_rates_id = prices['dropin_tax_rates_id']
            glaccount = prices['dropin_glaccount']
            costcenter = prices['dropin_costcenter']

        description = cls.get_invoice_order_description(attendance_type)

        coiID = db.customers_orders_items.insert(
            customers_orders_id = self.coID,
            classes_id = clsID,
            AttendanceType = attendance_type,
            ClassDate = class_date,
            ProductName = T('Class'),
            Description = description,
            Quantity = 1,
            Price = price,
            tax_rates_id = tax_rates_id,
            accounting_glaccounts_id = glaccount,
            accounting_costcenters_id = costcenter
        )

        self.set_amounts()

        return coiID


    def order_item_add_custom(self,
                              product_name,
                              description,
                              quantity,
                              price,
                              tax_rates_id,
                              glaccount=None,
                              costcenter=None):
        """
            :param workshops_products_id: db.workshops_products.id
            :return: db.customers_orders_items.id of inserted item
        """
        DATE_FORMAT = current.DATE_FORMAT
        TIME_FORMAT = current.TIME_FORMAT
        db = current.db
        T  = current.T

        coiID = db.customers_orders_items.insert(
            customers_orders_id = self.coID,
            Custom = True,
            ProductName = product_name,
            Description = description,
            Quantity = quantity,
            Price = price,
            tax_rates_id = tax_rates_id,
            accounting_glaccounts_id = glaccount,
            accounting_costcenters_id = costcenter
        )

        self.set_amounts()

        return coiID


    def has_subscription_registration_fee_item(self):
        """

        :return:
        """
        db = current.db

        query = (db.customers_orders_items.customers_orders_id == self.coID) & \
                (db.customers_orders_items.SubscriptionRegistrationFee == True)

        if db(query).count():
            return True
        else:
            return False


    def get_order_items_rows(self):
        """
            :return: db.customers_orders_items rows for order
        """
        db = current.db

        left = [
            db.customers_orders_items_shop_products_variants.on(
                db.customers_orders_items_shop_products_variants.customers_orders_items_id ==
                db.customers_orders_items.id
            )
        ]

        query = (db.customers_orders_items.customers_orders_id == self.coID)
        rows = db(query).select(
            db.customers_orders_items.ALL,
            db.customers_orders_items_shop_products_variants.ALL,
            left=left
        )

        return rows


    def get_order_items_summary_display(self, with_customer_message=True):
        """

        :return: html table with simple order summary
        """
        represent_decimal_as_amount = current.globalenv['represent_decimal_as_amount']
        T = current.T

        rows = self.get_order_items_rows()
        table = TABLE(THEAD(TR(
            TH(T("Item")),
            TH(SPAN(T("Price"), _class='pull-right')),
        )), _class='table table-striped')

        for row in rows.render():
            table.append(TR(
                TD(row.customers_orders_items.ProductName, BR(),
                   SPAN(row.customers_orders_items.Description, _class='text-muted')),
                TD(SPAN(row.customers_orders_items.TotalPriceVAT, _class='pull-right'))
            ))

        amounts = self.get_amounts()
        table.append(TFOOT(TR(
            TH(T("Total")),
            TH(SPAN(represent_decimal_as_amount(amounts.TotalPriceVAT),
                    _class='pull-right'))
        )))


        message = ''
        if with_customer_message and self.order.CustomerNote:
            message = DIV(
                B(T("We received the following message with your order"), ':'), BR(), BR(),
                XML(self.order.CustomerNote.replace('\n', '<br>')),
                _class='well'
            )

        return DIV(table, BR(), message)


    def get_amounts(self):
        """
            Get subtotal, vat and total incl vat
        """
        db = current.db

        amounts = db.customers_orders_amounts(customers_orders_id = self.coID)

        return amounts


    def get_customer_name(self):
        """
        :return: customer name for order
        """
        db = current.db
        row = db.auth_user(self.order.auth_customer_id)

        return row.display_name


    def set_amounts(self):
        """
            Set subtotal, vat and total incl vat
        """
        db = current.db
        # set sums
        sum_subtotal = db.customers_orders_items.TotalPrice.sum()
        sum_vat = db.customers_orders_items.VAT.sum()
        sum_totalvat = db.customers_orders_items.TotalPriceVAT.sum()

        # get info from db
        query = (db.customers_orders_items.customers_orders_id == self.coID)
        rows = db(query).select(sum_subtotal,
                                sum_vat,
                                sum_totalvat)

        sums = rows.first()
        subtotal = sums[sum_subtotal]
        vat = sums[sum_vat]
        total = sums[sum_totalvat]

        if subtotal is None:
            subtotal = 0
        if vat is None:
            vat = 0
        if total is None:
            total = 0

        # check what to do
        amounts = db.customers_orders_amounts(customers_orders_id = self.coID)
        if amounts:
            # update current row
            amounts.TotalPrice = subtotal
            amounts.VAT = vat
            amounts.TotalPriceVAT = total
            amounts.update_record()
        else:
            # insert new row
            db.customers_orders_amounts.insert(
                customers_orders_id = self.coID,
                TotalPrice=subtotal,
                VAT=vat,
                TotalPriceVAT=total
            )


    def deliver(self, class_online_booking=True, class_booking_status='booked', payment_methods_id=None):
        """
            Create invoice for order and deliver goods
        """
        from .os_attendance_helper import AttendanceHelper
        from .os_cache_manager import  OsCacheManager
        from .os_invoice import Invoice
        from .os_school_classcard import SchoolClasscard
        from .os_school_subscription import SchoolSubscription
        from .os_customer_subscription import CustomerSubscription
        from .os_school_membership import SchoolMembership
        from .os_customer_membership import CustomerMembership
        from .os_workshop import Workshop
        from .os_workshop_product import WorkshopProduct

        cache_clear_classschedule_api = current.globalenv['cache_clear_classschedule_api']
        get_sys_property = current.globalenv['get_sys_property']
        TODAY_LOCAL = current.TODAY_LOCAL
        ocm = OsCacheManager()
        db = current.db
        T = current.T
        checkin_status = None
        checkin_message = None

        if self.order.Status == 'delivered':
            return

        create_invoice = False
        iID = None
        invoice = None
        # Only create an invoice if order amount > 0
        amounts = self.get_amounts()

        sys_property_create_invoice = 'shop_donations_create_invoice'
        create_invoice_for_donations = get_sys_property(sys_property_create_invoice)
        if create_invoice_for_donations == 'on':
            create_invoice_for_donations = True
        else:
            create_invoice_for_donations = False

        if amounts:
            if amounts.TotalPriceVAT > 0:
                if not self.order.Donation or (self.order.Donation and create_invoice_for_donations):
                    create_invoice = True

                    # Create blank invoice
                    igpt = db.invoices_groups_product_types(ProductType='shop')

                    iID = db.invoices.insert(
                        invoices_groups_id=igpt.invoices_groups_id,
                        Description=T('Order #') + str(self.coID),
                        Status='sent'
                    )

                    # Link invoice to order
                    db.invoices_customers_orders.insert(
                        customers_orders_id = self.coID,
                        invoices_id = iID
                    )

                    # Call init function for invoices to set Invoice # , etc.
                    invoice = Invoice(iID)
                    invoice.link_to_customer(self.order.auth_customer_id)

        # Add items to the invoice
        rows = self.get_order_items_rows()

        for row in rows:
            ##
            # Only rows where school_classcards_id, workshops_products_id , classes_id or Donation are set
            # are put on the invoice
            ##
            if row.customers_orders_items.DummySubscription:
                # Don't process dummy items
                continue

            # Check for product:
            if row.customers_orders_items.ProductVariant:
                if create_invoice:
                    invoice.item_add_product_variant(
                        product_name = row.customers_orders_items.ProductName,
                        description = row.customers_orders_items.Description,
                        quantity = row.customers_orders_items.Quantity,
                        price = row.customers_orders_items.Price,
                        tax_rates_id = row.customers_orders_items.tax_rates_id,
                        accounting_glaccounts_id = row.customers_orders_items.accounting_glaccounts_id,
                        accounting_costcenters_id = row.customers_orders_items.accounting_costcenters_id
                    )

            # Check for classcard
            if row.customers_orders_items.school_classcards_id:
                # Deliver card
                card_start = TODAY_LOCAL
                scd = SchoolClasscard(row.customers_orders_items.school_classcards_id)
                ccdID = scd.sell_to_customer(self.order.auth_customer_id,
                                             card_start,
                                             invoice=False)

                # clear cache
                ocm.clear_customers_classcards(self.order.auth_customer_id)

                # Add card to invoice
                if create_invoice:
                    invoice.item_add_classcard(ccdID)

            # Check for subscription
            if row.customers_orders_items.school_subscriptions_id:
                ## Deliver subscription
                # Determine payment method
                cs_payment_method = get_sys_property('shop_subscriptions_payment_method')
                if cs_payment_method == 'mollie':
                    payment_method_id = 100
                else:
                    payment_method_id = 3

                subscription_start = TODAY_LOCAL
                ssu = SchoolSubscription(row.customers_orders_items.school_subscriptions_id)
                csID = ssu.sell_to_customer(
                    self.order.auth_customer_id,
                    subscription_start,
                    payment_methods_id=payment_method_id,
                    origin="SHOP"
                )

                # Add credits for the first month
                cs = CustomerSubscription(csID)
                cs.add_credits_month(
                    subscription_start.year,
                    subscription_start.month
                )

                # clear cache
                ocm.clear_customers_subscriptions(self.order.auth_customer_id)

                if create_invoice:
                    # This will also add the registration fee if required.
                    iiID = invoice.item_add_subscription(
                        csID,
                        TODAY_LOCAL.year,
                        TODAY_LOCAL.month
                    )


            # Check for membership
            if row.customers_orders_items.school_memberships_id:
                # Deliver membership
                membership_start = TODAY_LOCAL
                sme = SchoolMembership(row.customers_orders_items.school_memberships_id)
                cmID = sme.sell_to_customer(
                    self.order.auth_customer_id,
                    membership_start,
                    invoice=False, # Don't create a separate invoice
                )

                # clear cache
                ocm.clear_customers_memberships(self.order.auth_customer_id)

                if create_invoice:
                    cm = CustomerMembership(cmID)

                    # Check if price exists and > 0:
                    if sme.row.Price:
                        iiID = invoice.item_add_membership(cmID)

            # Check for workshop
            if row.customers_orders_items.workshops_products_id:
                # Deliver workshop product
                wsp = WorkshopProduct(row.customers_orders_items.workshops_products_id)
                wspcID = wsp.sell_to_customer(self.order.auth_customer_id,
                                              invoice=False)

                # Add workshop product to invoice
                if create_invoice:
                    invoice.item_add_workshop_product(wspcID)

                # Check if sold out
                if wsp.is_sold_out():
                    # Cancel all unpaid orders with a sold out product for this workshop
                    ws = Workshop(wsp.wsID)
                    ws.cancel_orders_with_sold_out_products()

            # Check for classes
            if row.customers_orders_items.classes_id:
                # Deliver class
                ah = AttendanceHelper()
                if row.customers_orders_items.AttendanceType == 1:
                    result = ah.attendance_sign_in_trialclass(
                        self.order.auth_customer_id,
                        row.customers_orders_items.classes_id,
                        row.customers_orders_items.ClassDate,
                        online_booking=class_online_booking,
                        invoice=False,
                        booking_status=class_booking_status
                    )
                elif row.customers_orders_items.AttendanceType == 2:
                    result = ah.attendance_sign_in_dropin(
                        self.order.auth_customer_id,
                        row.customers_orders_items.classes_id,
                        row.customers_orders_items.ClassDate,
                        online_booking=class_online_booking,
                        invoice=False,
                        booking_status=class_booking_status,
                    )

                if create_invoice:
                    invoice.item_add_class_from_order(row, result['caID'])

                # Clear api cache to update available spaces
                cache_clear_classschedule_api()

            # Check for donation
            if row.customers_orders_items.Donation:
                # Add donation line to invoice
                if create_invoice and create_invoice_for_donations:
                    invoice.item_add_donation(
                        row.customers_orders_items.TotalPriceVAT,
                        row.customers_orders_items.Description
                    )

            # Check for custom item
            if row.customers_orders_items.Custom:
                # Add custom line to invoice
                if create_invoice:
                    invoice.item_add_custom_from_order(row)


        # Notify customer of new invoice
        #if create_invoice:
            #invoice.mail_customer_invoice_created()

        receipt = None
        if self.order.Origin == "pos":
            from .os_receipt import Receipt

            rID = db.receipts.insert(payment_methods_id=payment_methods_id)
            receipt = Receipt(rID)

            for row in rows:
                receipt.item_add_from_order_item(row)

        # Update status
        self.set_status_delivered()
        # Notify customer of order delivery
        self._deliver_mail_customer()

        return dict(
            iID=iID,
            invoice=invoice,
            receipt=receipt,
            checkin_status=checkin_status,
            checkin_message=checkin_message,
        )


    def _deliver_mail_customer(self):
        """
            Notify customer of order delivery
        """
        from .os_mail import OsMail

        osmail = OsMail()
        msgID = osmail.render_email_template(
            'order_delivered',
            customers_orders_id=self.coID
        )

        osmail.send_and_archive(msgID, self.order.auth_customer_id)
