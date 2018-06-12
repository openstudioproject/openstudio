# -*- coding: utf-8 -*-

from gluon import *


class Invoice:
    """
        Class that contains functions for an invoice
    """
    def __init__(self, iID):
        """
            Init function for an invoice
        """
        db = current.db

        self.invoices_id = iID
        self.invoice = db.invoices(iID)
        self.invoice_group = db.invoices_groups(self.invoice.invoices_groups_id)

        if not self.invoice.InvoiceID:
            self._set_invoice_id_duedate_and_amounts()
            self._set_terms_and_footer()


    def _set_invoice_id_duedate_and_amounts(self):
        """
            Set invoice id and duedate for an invoice
        """
        self.invoice.InvoiceID = self._get_next_invoice_id()

        delta = datetime.timedelta(days = self.invoice_group.DueDays)
        self.invoice.DateDue = self.invoice.DateDue + delta

        self.invoice.update_record()

        db = current.db
        db.invoices_amounts.insert(invoices_id = self.invoices_id)


    def _set_terms_and_footer(self):
        """
            Set terms and footer
        """
        if not self.invoice.Terms:
            self.invoice.Terms = self.invoice_group.Terms
        if not self.invoice.Footer:
            self.invoice.Footer = self.invoice_group.Footer


        self.invoice.update_record()


    def _get_next_invoice_id(self):
        """
            Returns the number for an invoice
        """
        invoice_id = self.invoice_group.InvoicePrefix

        if self.invoice_group.PrefixYear:
            year = unicode(datetime.date.today().year)
            invoice_id += year

        invoice_id += unicode(self.invoice_group.NextID)

        self.invoice_group.NextID += 1
        self.invoice_group.update_record()

        return invoice_id


    def set_status(self, status):
        """
            Sets the status of this invoice
        """
        # check if the status exists:
        actual_status = False
        for status_name, status_text in current.globalenv['invoice_statuses']:
            if status == status_name:
                actual_status = True

        if actual_status:
            self.invoice.Status = status
            self.invoice.update_record()
        else:
            return False


    def set_amounts(self):
        """
            Set subtotal, vat and total incl vat
        """
        db = current.db
        # set sums
        sum_subtotal = db.invoices_items.TotalPrice.sum()
        sum_vat = db.invoices_items.VAT.sum()
        sum_totalvat = db.invoices_items.TotalPriceVAT.sum()

        # get info from db
        query = (db.invoices_items.invoices_id == self.invoices_id)
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
        amounts = db.invoices_amounts(invoices_id = self.invoices_id)
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
            db.invoices_amounts.insert(
                invoices_id   = self.invoices_id,
                TotalPrice    = subtotal,
                VAT           = vat,
                TotalPriceVAT = total,
                Paid          = paid,
                Balance       = balance)


    def get_amounts(self):
        """
            Get subtotal, vat and total incl vat
        """
        db = current.db

        amounts = db.invoices_amounts(invoices_id = self.invoices_id)

        return amounts


    def get_amounts_tax_rates(self, formatted=False):
        """
            Returns vat for each tax rate as list sorted by tax rate percentage
            format: [ [ Name, Amount ] ]
        """
        db = current.db
        iID = self.invoices_id
        CURRSYM = current.globalenv['CURRSYM']

        amounts_vat = []
        rows = db().select(db.tax_rates.id, db.tax_rates.Name,
                           orderby=db.tax_rates.Percentage)
        for row in rows:
            sum = db.invoices_items.VAT.sum()
            query = (db.invoices_items.invoices_id == iID) & \
                    (db.invoices_items.tax_rates_id == row.id)

            result = db(query).select(sum).first()

            if not result[sum] is None:
                if formatted:
                    amount = SPAN(CURRSYM, ' ', format(result[sum], '.2f'))
                else:
                    amount = result[sum]
                amounts_vat.append({'Name'   : row.Name,
                                    'Amount' : amount})

        return amounts_vat


    def get_amount_paid(self, formatted=False):
        """
            Returns the total amount paid
        """
        db = current.db
        sum = db.invoices_payments.Amount.sum()
        query = (db.invoices_payments.invoices_id == self.invoices_id)

        rows = db(query).select(sum)
        paid = rows.first()[sum]
        if paid is None:
            paid = 0

        if formatted:
            return_value = SPAN(current.globalenv['CURRSYM'], ' ',
                                format(paid, '.2f'))
        else:
            return_value = paid

        return return_value


    def get_balance(self, formatted=False):
        """
            Returns the balance for an invoice
        """
        db = current.db
        paid = self.get_amount_paid()
        total = self.get_amounts()['TotalPriceVAT']

        # round numbers first to prevent weird outcomes by decemals
        balance = round(total, 2) - round(paid, 2)

        if formatted:
            return_value = SPAN(current.globalenv['CURRSYM'], ' ',
                                format(balance, '.2f'))
        else:
            return_value = balance

        return return_value


    def get_item_next_sort_nr(self):
        """
            Returns the next item number for an invoice
            use to set sorting when adding an item
        """
        db = current.db
        query = (db.invoices_items.invoices_id == self.invoices_id)

        return db(query).count() + 1


    def get_invoice_items_rows(self):
        """
            :return: db.customers_orders_items rows for order
        """
        db = current.db

        query = (db.invoices_items.invoices_id == self.invoices_id)
        rows = db(query).select(db.invoices_items.ALL)

        return rows


    def item_add_class(self,
                       cuID,
                       caID,
                       clsID,
                       date,
                       product_type):
        """
        Add invoice item when checking in to a class

        :param cuID: db.auth_user.id
        :param caID: db.classes_attendance.id
        :param clsID: db.classes.id
        :param date: datetime.date (class date)
        :param product_type: has to be 'trial' or 'dropin'
        :return:
        """
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

            if has_membership and prices['dropin_membership']:
                price = prices['dropin_membership']
                tax_rates_id = prices['dropin_tax_rates_id_membership']

            description = cls.get_invoice_order_description(2) # 2 = drop in class

        elif product_type == 'trial':
            price = prices['trial']
            tax_rates_id = prices['trial_tax_rates_id']

            if has_membership and prices['trial_membership']:
                price = prices['trial_membership']
                tax_rates_id = prices['trial_tax_rates_id_membership']

            description = cls.get_invoice_order_description(1) # 1 = trial class

        # link invoice to attendance
        self.link_to_classes_attendance(caID)

        next_sort_nr = self.get_item_next_sort_nr()
        iiID = db.invoices_items.insert(
            invoices_id=self.invoices_id,
            ProductName=T("Class"),
            Description=description,
            Quantity=1,
            Price=price,
            Sorting=next_sort_nr,
            tax_rates_id=tax_rates_id,
        )

        self.set_amounts()
        self.link_to_customer(cuID)


    def item_add_class_from_order(self, order_item_row, caID):
        """
            Add class to invoice from Order.deliver()

            :param clsID: db.classes.id
            :param class_date: datetime.date
            :param attendance_type: int 1 or 2 
            :return: db.invoices_items.id
        """
        DATE_FORMAT = current.DATE_FORMAT
        TIME_FORMAT = current.TIME_FORMAT
        db = current.db
        T  = current.T

        cls = Class(order_item_row.classes_id, order_item_row.ClassDate)

        # link invoice to attendance
        db.invoices_classes_attendance.insert(
            invoices_id=self.invoices_id,
            classes_attendance_id=caID
        )

        # add item to invoice
        next_sort_nr = self.get_item_next_sort_nr()


        iiID = db.invoices_items.insert(
            invoices_id=self.invoices_id,
            ProductName=order_item_row.ProductName,
            Description=order_item_row.Description,
            Quantity=order_item_row.Quantity,
            Price=order_item_row.Price,
            Sorting=next_sort_nr,
            tax_rates_id=order_item_row.tax_rates_id,
        )

        self.set_amounts()

        return iiID


    def item_add_classcard(self, ccdID):
        """
            :param ccdID: Add customer classcard to invoice
            :return: None
        """
        db = current.db
        T  = current.T

        classcard = CustomerClasscard(ccdID)
        # link invoice to classcard sold to customer
        db.invoices_customers_classcards.insert(
            invoices_id=self.invoices_id,
            customers_classcards_id=ccdID
        )

        # add item to invoice
        next_sort_nr = self.get_item_next_sort_nr()
        price = classcard.price

        iiID = db.invoices_items.insert(
            invoices_id=self.invoices_id,
            ProductName=T("Class card"),
            Description=classcard.name.decode('utf-8') + u' (' + T("Class card") + u' ' + unicode(ccdID) + u')',
            Quantity=1,
            Price=price,
            Sorting=next_sort_nr,
            tax_rates_id=classcard.school_classcard.tax_rates_id,
        )

        self.set_amounts()

        return iiID


    def item_add_workshop_product(self, wspcID):
        """
            :param wspID: db.workshops_products_id
            :return: db.invoices_items.id
        """
        db = current.db
        T  = current.T

        wspc = db.workshops_products_customers(wspcID)
        wsp = db.workshops_products(wspc.workshops_products_id)
        ws = db.workshops(wsp.workshops_id)
        # Link invoice to workshop product sold to customer
        db.invoices_workshops_products_customers.insert(
            invoices_id = self.invoices_id,
            workshops_products_customers_id = wspcID
        )

        # Add item to invoice
        next_sort_nr = self.get_item_next_sort_nr()

        iiID = db.invoices_items.insert(
            invoices_id=self.invoices_id,
            ProductName=T('Event'),
            Description=ws.Name.decode('utf-8') + u' - ' + wsp.Name.decode('utf-8'),
            Quantity=1,
            Price=wsp.Price,
            Sorting=next_sort_nr,
            tax_rates_id=wsp.tax_rates_id
        )

        self.set_amounts()

        return iiID


    def item_add_donation(self, amount, description):
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

        # add item to invoice
        next_sort_nr = self.get_item_next_sort_nr()
        price = amount

        iiID = db.invoices_items.insert(
            invoices_id=self.invoices_id,
            ProductName=T("Donation"),
            Description=description.decode('utf-8'),
            Quantity=1,
            Price=price,
            Sorting=next_sort_nr,
            tax_rates_id=tax_rates_id,
        )

        self.set_amounts()

        return iiID


    def item_add_subscription(self, SubscriptionYear, SubscriptionMonth, description=''):
        """
            :param SubscriptionYear: Year of subscription
            :param SubscriptionMonth: Month of subscription
            :return: db.invoices_items.id
        """
        db = current.db
        DATE_FORMAT = current.DATE_FORMAT

        next_sort_nr = self.get_item_next_sort_nr()

        date = datetime.date(int(SubscriptionYear),
                             int(SubscriptionMonth),
                             1)

        ics = db.invoices_customers_subscriptions(invoices_id = self.invoices_id)
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

        iiID = db.invoices_items.insert(
            invoices_id  = self.invoices_id,
            ProductName  = current.T("Subscription") + ' ' + unicode(csID),
            Description  = description,
            Quantity     = 1,
            Price        = price,
            Sorting      = next_sort_nr,
            tax_rates_id = tax_rates_id,
        )

        self.set_amounts()

        return iiID


    def item_add_membership(self, cmID, period_start, period_end):
        """
        :param cmID: db.customers_memberships.id
        :return: db.invoices_items.id
        """
        from openstudio.os_customer_membership import CustomerMembership
        from openstudio.os_school_membership import SchoolMembership

        db = current.db
        DATE_FORMAT = current.DATE_FORMAT

        next_sort_nr = self.get_item_next_sort_nr()

        cm = CustomerMembership(cmID)
        sm = SchoolMembership(cm.row.school_memberships_id)
        row = sm.get_tax_rates_on_date(period_start)

        if row:
            tax_rates_id = row.school_memberships_price.tax_rates_id
        else:
            tax_rates_id = None

        price = sm.get_price_on_date(cm.row.Startdate, False)
        description = cm.get_name() + ' ' + \
                      period_start.strftime(DATE_FORMAT) + ' - ' + \
                      period_end.strftime(DATE_FORMAT)

        iiID = db.invoices_items.insert(
            invoices_id  = self.invoices_id,
            ProductName  = current.T("Membership") + ' ' + unicode(cmID),
            Description  = description,
            Quantity     = 1,
            Price        = price,
            Sorting      = next_sort_nr,
            tax_rates_id = tax_rates_id,
        )

        self.link_to_customer_membership(cmID)
        self.set_amounts()

        return iiID


    def item_add_teacher_class_credit_payment(self,
                                              clsID,
                                              date,
                                              payment_type='fixed_rate'):
        """
        :param clsID: db.classes.id
        :param date: datetime.date class date
        :return:
        """
        from os_teacher import Teacher

        DATE_FORMAT = current.DATE_FORMAT
        TIME_FORMAT = current.TIME_FORMAT
        db = current.db
        T = current.T

        cls = Class(clsID, date)
        teID = self.get_linked_customer_id()
        teacher = Teacher(teID)

        default_rates = teacher.get_payment_fixed_rate_default()
        class_rates = teacher.get_payment_fixed_rate_classes_dict()

        if not default_rates and not class_rates:
            return None  # No rates set, not enough data to create invoice item

        default_rate = default_rates.first()
        price = default_rate.ClassRate
        tax_rates_id = default_rate.tax_rates_id

        # Set price and tax rate
        try:
            class_prices = class_rates.get(int(clsID), False)
            if class_prices:
                price = class_prices.ClassRate
                tax_rates_id = class_prices.tax_rates_id
        except (AttributeError, KeyError):
            pass


        # add item to invoice
        next_sort_nr = self.get_item_next_sort_nr()

        iiID = db.invoices_items.insert(
            invoices_id=self.invoices_id,
            ProductName=T('Class'),
            Description=cls.get_name(),
            Quantity=1,
            Price=price * -1,
            Sorting=next_sort_nr,
            tax_rates_id=tax_rates_id,
        )

        self.set_amounts()

        return iiID


    def item_add_teacher_class_credit_travel_allowance(self,
                                                clsID,
                                                date,
                                                payment_type='fixed_rate'):
        """
        :param clsID: db.classes.id
        :param date: datetime.date class date
        :return:
        """
        from os_teacher import Teacher

        DATE_FORMAT = current.DATE_FORMAT
        TIME_FORMAT = current.TIME_FORMAT
        db = current.db
        T = current.T

        cls = Class(clsID, date)
        teID = self.get_linked_customer_id()
        teacher = Teacher(teID)

        travel_allowance = teacher.get_payment_fixed_rate_travel_allowance_location(cls.cls.school_locations_id)
        if travel_allowance:
            price = travel_allowance.TravelAllowance
            tax_rates_id = travel_allowance.tax_rates_id

            # add item to invoice
            next_sort_nr = self.get_item_next_sort_nr()

            iiID = db.invoices_items.insert(
                invoices_id=self.invoices_id,
                ProductName=T('Travel allowance'),
                Description=cls.get_name(),
                Quantity=1,
                Price=price * -1,
                Sorting=next_sort_nr,
                tax_rates_id=tax_rates_id,
            )

            self.set_amounts()

            return iiID


    def payment_add(self,
                    amount,
                    date,
                    payment_methods_id,
                    note=None,
                    mollie_payment_id=None):
        """
            Add payment to invoice
        """
        db = current.db

        ipID = db.invoices_payments.insert(
            invoices_id = self.invoices_id,
            Amount = amount,
            PaymentDate = date,
            payment_methods_id = payment_methods_id,
            Note = note,
            mollie_payment_id = mollie_payment_id
        )

        self.is_paid()

        return ipID


    def is_paid(self):
        """
            Check if the status should be changed to 'paid'
        """
        db = current.db

        # Update invoice status
        sum_payments = db.invoices_payments.Amount.sum()
        query = (db.invoices_payments.invoices_id == self.invoices_id)
        # sum
        amount_paid = db(query).select(sum_payments).first()[sum_payments]
        # Decimal
        amount_paid = Decimal(amount_paid)
        # Rounded to 2 decimals
        amount_paid = Decimal(amount_paid.quantize(Decimal('.01'),
                                                   rounding=ROUND_HALF_UP))


        invoice_amounts = db.invoices_amounts(invoices_id=self.invoices_id)
        invoice_amount = Decimal(invoice_amounts.TotalPriceVAT)
        invoice_total = Decimal(invoice_amount.quantize(Decimal('.01'),
                                                        rounding=ROUND_HALF_UP))

        if amount_paid >= invoice_total:
            self.invoice.Status = 'paid'
            self.invoice.update_record()
            return True
        else:
            return False


    def set_customer_info(self, cuID):
        """
            Set customer information for an invoice
        """
        customer = Customer(cuID)

        address = ''
        if customer.row.address:
            address = ''.join([address, customer.row.address, '\n'])
        if customer.row.city:
            address = ''.join([address, customer.row.city, ' '])
        if customer.row.postcode:
            address = ''.join([address, customer.row.postcode, '\n'])
        if customer.row.country:
            address = ''.join([address, customer.row.country])

        list_name = customer.row.full_name
        if customer.row.company:
            list_name = customer.row.company

        self.invoice.update_record(
            CustomerCompany = customer.row.company,
            CustomerName = customer.row.full_name,
            CustomerListName = list_name,
            CustomerAddress = address,
        )


    def link_to_customer(self, cuID):
        """
            Link invoice to customer
        """
        db = current.db
        # Insert link
        db.invoices_customers.insert(
            invoices_id = self.invoices_id,
            auth_customer_id = cuID
        )

        # Set customer info
        self.set_customer_info(cuID)


    def link_to_customer_subscription(self, csID):
        """
            Link invoice to customer subscription
        """
        db = current.db
        db.invoices_customers_subscriptions.insert(
            invoices_id = self.invoices_id,
            customers_subscriptions_id = csID
        )


    def link_to_customer_membership(self, cmID):
        """
            Link invoice to customer subscription
        """
        db = current.db
        db.invoices_customers_memberships.insert(
            invoices_id=self.invoices_id,
            customers_memberships_id=cmID
        )


    def link_to_classes_attendance(self, caID):
        """
        Link invoice to classes attendance
        :param caID: db.classes_attendance.id
        :return: None
        """
        db = current.db
        db.invoices_classes_attendance.insert(
            invoices_id=self.invoices_id,
            classes_attendance_id=caID
        )


    def get_linked_customer_id(self):
        """
            Returns auth.user.id of account linked to this invoice
            :return: auth.user.id
        """
        db = current.db

        query = (db.invoices_customers.invoices_id == self.invoices_id)
        rows = db(query).select(db.invoices_customers.auth_customer_id)

        if rows:
            return rows.first().auth_customer_id
        else:
            return None


    def get_linked_customer_subscription_id(self):
        """
            Returns auth.user.id of account linked to this invoice
            :return: auth.user.id
        """
        db = current.db

        query = (db.invoices_customers_subscriptions.invoices_id == self.invoices_id)
        rows = db(query).select(db.invoices_customers_subscriptions.customers_subscriptions_id)

        if rows:
            return rows.first().customers_subscriptions_id
        else:
            return None

