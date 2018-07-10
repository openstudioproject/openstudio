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
            tax_rates_id = school_classcard.tax_rates_id
        )

        self.set_amounts()

        return coiID


    def order_item_add_workshop_product(self, workshops_products_id):
        """
            :param workshops_products_id: db.workshops_products.id
            :return: db.customers_orders_items.id of inserted item
        """
        db = current.db
        T  = current.T

        wsp = db.workshops_products(workshops_products_id)
        ws = db.workshops(wsp.workshops_id)

        coiID = db.customers_orders_items.insert(
            customers_orders_id = self.coID,
            workshops_products_id = workshops_products_id,
            ProductName = T('Event'),
            Description = ws.Name + ' - ' + wsp.Name,
            Quantity = 1,
            Price = wsp.Price,
            tax_rates_id = wsp.tax_rates_id
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


    def order_item_add_class(self, clsID, class_date, attendance_type):
        """
            :param workshops_products_id: db.workshops_products.id
            :return: db.customers_orders_items.id of inserted item
        """
        from os_class import Class

        DATE_FORMAT = current.DATE_FORMAT
        TIME_FORMAT = current.TIME_FORMAT
        db = current.db
        T  = current.T

        cls = Class(clsID, class_date)
        prices = cls.get_prices_customer(self.order.auth_customer_id)
        if attendance_type == 1:
            price = prices['trial']
            tax_rates_id = prices['trial_tax_rates_id']
        elif attendance_type == 2:
            price = prices['dropin']
            tax_rates_id = prices['dropin_tax_rates_id']

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
        )

        self.set_amounts()

        return coiID


    def get_order_items_rows(self):
        """
            :return: db.customers_orders_items rows for order
        """
        db = current.db

        query = (db.customers_orders_items.customers_orders_id == self.coID)
        rows = db(query).select(db.customers_orders_items.ALL)

        return rows


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


    def deliver(self):
        """
            Create invoice for order and deliver goods
        """
        from os_attendance_helper import AttendanceHelper
        from os_invoice import Invoice
        from os_school_classcard import SchoolClasscard
        from os_school_subscription import SchoolSubscription
        from os_workshop import Workshop
        from os_workshop_product import WorkshopProduct

        cache_clear_classschedule_api = current.globalenv['cache_clear_classschedule_api']
        get_sys_property = current.globalenv['get_sys_property']
        db = current.db
        T = current.T

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
                        Description=T('Order #') + unicode(self.coID),
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

            # Check for classcard
            if row.school_classcards_id:
                # Deliver card
                card_start = datetime.date.today()
                scd = SchoolClasscard(row.school_classcards_id)
                ccdID = scd.sell_to_customer(self.order.auth_customer_id,
                                             card_start,
                                             invoice=False)
                # Add card to invoice
                if create_invoice:
                    invoice.item_add_classcard(ccdID)

            # Check for workshop
            if row.workshops_products_id:
                # Deliver workshop product
                wsp = WorkshopProduct(row.workshops_products_id)
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
            if row.classes_id:
                # Deliver class
                ah = AttendanceHelper()
                if row.AttendanceType == 1:
                    result = ah.attendance_sign_in_trialclass(self.order.auth_customer_id,
                                                              row.classes_id,
                                                              row.ClassDate,
                                                              online_booking=True,
                                                              invoice=False)
                elif row.AttendanceType == 2:
                    result = ah.attendance_sign_in_dropin(self.order.auth_customer_id,
                                                          row.classes_id,
                                                          row.ClassDate,
                                                          online_booking=True,
                                                          invoice=False)

                if create_invoice:
                    invoice.item_add_class_from_order(row, result['caID'])

                # Clear api cache to update available spaces
                cache_clear_classschedule_api()

            # Check for donation
            if row.Donation:
                # Add donation line to invoice
                if create_invoice and create_invoice_for_donations:
                    invoice.item_add_donation(row.TotalPriceVAT, row.Description)


        # Notify customer of new invoice
        #if create_invoice:
            #invoice.mail_customer_invoice_created()

        # Update status
        self.set_status_delivered()
        # Notify customer of order delivery
        self._deliver_mail_customer()

        return dict(iID=iID, invoice=invoice)


    def _deliver_mail_customer(self):
        """
            Notify customer of order delivery
        """
        from os_mail import OsMail

        osmail = OsMail()
        msgID = osmail.render_email_template('email_template_order_delivered', customers_orders_id=self.coID)

        osmail.send(msgID, self.order.auth_customer_id)
