# -*- coding: utf-8 -*-

import datetime
from decimal import Decimal, ROUND_HALF_UP

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
            self.on_create()


    def on_create(self):
        """
        functions to be called when creating an invoice
        """
        self._set_invoiceID() # We can call another function for this one when Moneybird is active and linked or get the data from moneybird in the function
        self._set_duedate() # Perhaps also get this one from Moneybird?
        self._insert_amounts() # We always need to call this one
        self._set_terms_and_footer() # Terms and footer from Moneybird or simply make sure the texts match....?


    def on_update(self):
        """
        functions to be called when updating an invoice or invoice items
        """
        from tools import OsTools
        from os_exact_online import OSExactOnline

        os_tools = OsTools()
        eo_authorized = os_tools.get_sys_property('exact_online_authorized')

        # Set last updated datetime
        self._set_updated_at()

        # Exact online integration
        if eo_authorized == 'True':
            os_eo = OSExactOnline()
            if not self.invoice_group.JournalID:
                os_eo._log_error(
                    'update',
                    'invoice',
                    self.invoices_id,
                    'No JournalID specified for invoice group'
                )
            else:
                os_eo.update_sales_entry(self)


    def _set_updated_at(self):
        """
        Set db.invoices.Updated_at to current time (UTC)
        """
        self.invoice.Updated_at = datetime.datetime.now()
        self.invoice.update_record()


    def _set_invoiceID(self):
        """
        Set db.invoices.InvoiceID field for invoice
        """
        self.invoice.InvoiceID = self._get_next_invoice_id()
        self.invoice.update_record()

        return self.invoice.InvoiceID


    def _set_duedate(self):
        """
        Set db.invoices.Duedate field
        """
        delta = datetime.timedelta(days = self.invoice_group.DueDays)
        self.invoice.DateDue = self.invoice.DateDue + delta

        self.invoice.update_record()

        return self.invoice.DateDue


    def _insert_amounts(self):
        """
            Insert amounts row for invoice, without data
        """
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

            # Check if NextID should be reset
            self._get_next_invoice_id_year_prefix_reset_numbering()

        invoice_id += unicode(self.invoice_group.NextID)

        self.invoice_group.NextID += 1
        self.invoice_group.update_record()

        return invoice_id


    def _get_next_invoice_id_year_prefix_reset_numbering(self):
        """
        Reset  numbering to 1 for first invoice in year
        """
        db = current.db

        year = self.invoice.DateCreated.year
        year_start = datetime.date(year, 1, 1)
        year_end = datetime.date(year, 12, 31)

        # Check if we have invoices this year for this group
        query = (db.invoices.DateCreated >= year_start) & \
                (db.invoices.DateCreated <= year_end) & \
                (db.invoices.invoices_groups_id == self.invoice.invoices_groups_id)

        invoices_for_this_group_in_year = db(query).count()

        if invoices_for_this_group_in_year == 1:
            # This is the first invoice in this group for this year
            self.invoice_group.NextID = 1
            self.invoice_group.update_record()


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

            self.on_update()
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


        self.on_update()


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


    def get_customer_info(self):
        """
        :return: dict with customer info
        """
        return dict(
            company = self.invoice.CustomerCompany or '',
            company_registration = self.invoice.CustomerCompanyRegistration or '',
            company_tax_registration = self.invoice.CustomerCompanyTaxRegistration or '',
            name = self.invoice.CustomerName or '',
            list_name = self.invoice.CustomerListName or '',
            address = self.invoice.CustomerAddress or ''
        )


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
        rows = db(query).select(db.invoices_items.ALL,
                                orderby=db.invoices_items.Sorting)

        return rows


    def get_payment_method(self):
        """
        :return: db.payment_methods_row for invoice
        """
        db = current.db

        if self.invoice.payment_methods_id:
            return db.payment_methods(self.invoice.payment_methods_id)
        else:
            return None


    def item_duplicate(self, iiID):
        """
        :param iiID: db.invoices_items.id
        :return: int - ID of newly inserted (duplicated) item
        """
        T = current.T
        db = current.db

        item = db.invoices_items(iiID)
        next_sort_nr = self.get_item_next_sort_nr()

        db.invoices_items.insert(
            invoices_id = item.invoices_id,
            Sorting = next_sort_nr,
            ProductName = item.ProductName,
            Description = item.Description + ' ' + T("(Copy)"),
            Quantity = item.Quantity,
            Price = item.Price,
            tax_rates_id = item.tax_rates_id,
            TotalPriceVAT = item.TotalPriceVAT,
            VAT = item.VAT,
            TotalPrice = item.TotalPrice,
            accounting_glaccounts_id = item.accounting_glaccounts_id,
            accounting_costcenters_id = item.accounting_costcenters_id
        )

        # This calls self.on_update()
        self.set_amounts()


    def item_add_product_variant(self,
                                 product_name,
                                 description,
                                 quantity,
                                 price,
                                 tax_rates_id,
                                 glaccount):
        """
        :param product_name: string
        :param description: string
        :param quantity: float
        :param price: float
        :param tax_rates_id: db.tax_rates_id
        :return:
        """
        db = current.db

        next_sort_nr = self.get_item_next_sort_nr()

        iiID = db.invoices_items.insert(
            invoices_id=self.invoices_id,
            ProductName=product_name,
            Description=description,
            Quantity=quantity,
            Price=price,
            Sorting=next_sort_nr,
            tax_rates_id=tax_rates_id,
            GLAccount=glaccount
        )

        # This calls self.on_update()
        self.set_amounts()

        return iiID


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
            costcenter = prices['dropin_costcenter']

            if has_membership and prices['dropin_membership']:
                price = prices['dropin_membership']
                tax_rates_id = prices['dropin_tax_rates_id_membership']

            description = cls.get_invoice_order_description(2) # 2 = drop in class

        elif product_type == 'trial':
            price = prices['trial']
            tax_rates_id = prices['trial_tax_rates_id']
            glaccount = prices['trial_glaccount']
            costcenter = prices['trial_costcenter']

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
            accounting_glaccounts_id=glaccount,
            accounting_costcenters_id=costcenter
        )

        self.link_to_customer(cuID)
        # This calls self.on_update()
        self.set_amounts()


    def item_add_class_from_order(self, order_item_row, caID):
        """
            Add class to invoice from Order.deliver()

            :param clsID: db.classes.id
            :param class_date: datetime.date
            :param attendance_type: int 1 or 2 
            :return: db.invoices_items.id
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
            accounting_glaccounts_id=order_item_row.accounting_glaccounts_id,
            accounting_costcenters_id=order_item_row.accounting_costcenters_id,
        )

        # This calls self.on_update()
        self.set_amounts()

        return iiID


    def item_add_classcard(self, ccdID):
        """
            :param ccdID: Add customer classcard to invoice
            :return: None
        """
        from os_customer_classcard import CustomerClasscard

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
            accounting_glaccounts_id=classcard.school_classcard.accounting_glaccounts_id,
            accounting_costcenters_id=classcard.school_classcard.accounting_costcenters_id
        )

        # This calls self.on_update()
        self.set_amounts()

        return iiID


    def item_add_workshop_product(self, wspcID):
        """
            :param wspID: db.workshops_products_id
            :return: db.invoices_items.id
        """
        DATE_FORMAT = current.DATE_FORMAT
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
            Description=ws.Name.decode('utf-8') + u' - ' + wsp.Name.decode('utf-8') + ' [' + ws.Startdate.strftime(DATE_FORMAT) + ']',
            Quantity=1,
            Price=wsp.Price,
            Sorting=next_sort_nr,
            tax_rates_id=wsp.tax_rates_id,
            accounting_glaccounts_id=wsp.accounting_glaccounts_id,
            accounting_costcenters_id=wsp.accounting_costcenters_id
        )

        # This calls self.on_update()
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

        # This calls self.on_update()
        self.set_amounts()

        return iiID


    def item_add_subscription(self, SubscriptionYear, SubscriptionMonth, description=''):
        """
            :param SubscriptionYear: Year of subscription
            :param SubscriptionMonth: Month of subscription
            :return: db.invoices_items.id
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
        glaccount = ssu.get_glaccount_on_date(date)
        costcenter = ssu.get_costcenter_on_date(date)
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
            invoices_id = self.invoices_id,
            ProductName = current.T("Subscription") + ' ' + unicode(csID),
            Description = description,
            Quantity = 1,
            Price = price,
            Sorting = next_sort_nr,
            tax_rates_id = tax_rates_id,
            accounting_glaccounts_id = glaccount,
            accounting_costcenters_id = costcenter

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
                db.invoices_items.insert(
                    invoices_id = self.invoices_id,
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


    def item_add_membership(self, cmID):
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

        price = sm.row.Price
        tax_rates_id = sm.row.tax_rates_id

        if price == 0:
            return # Don't do anything if the price is 0

        description = cm.get_name() + ' ' + \
                      cm.row.Startdate.strftime(DATE_FORMAT) + ' - ' + \
                      cm.row.Enddate.strftime(DATE_FORMAT)

        iiID = db.invoices_items.insert(
            invoices_id = self.invoices_id,
            ProductName = current.T("Membership") + ' ' + unicode(cmID),
            Description = description,
            Quantity = 1,
            Price = price,
            Sorting = next_sort_nr,
            tax_rates_id = tax_rates_id,
            accounting_glaccounts_id = sm.row.accounting_glaccounts_id,
            accounting_costcenters_id = sm.row.accounting_costcenters_id
        )

        self.link_to_customer_membership(cmID)
        # This calls self.on_update()
        self.set_amounts()

        return iiID


    def item_add_teacher_class_attendance_credit_payment(self,
                                                         tpcID):
        """
        :param clsID: db.classes.id
        :param date: datetime.date class date
        :return:
        """
        from os_class import Class
        from os_teacher import Teacher
        from os_teachers_payment_class import TeachersPaymentClass

        DATE_FORMAT = current.DATE_FORMAT
        TIME_FORMAT = current.TIME_FORMAT
        db = current.db
        T = current.T

        tpc = TeachersPaymentClass(tpcID)
        cls = Class(
            tpc.row.classes_id,
            tpc.row.ClassDate
        )

        # Get amount & tax rate
        rate = tpc.row.ClassRate
        tax_rates_id = tpc.row.tax_rates_id

        tax_rate = db.tax_rates(tax_rates_id)
        percentage = float(tax_rate.Percentage / 100)
        price = rate * (1 + percentage)

        # add item to invoice
        if price > 0:
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

            self.link_to_teachers_payment_class(tpcID)

            # This calls self.on_update()
            self.set_amounts()

            return iiID


    def item_add_teacher_class_credit_travel_allowance(self,
                                                       clsID,
                                                       date,
                                                       amount,
                                                       tax_rates_id):
        """
        :param clsID: db.classes.id
        :param date: datetime.date class date
        :return:
        """
        from os_class import Class
        from os_teacher import Teacher

        DATE_FORMAT = current.DATE_FORMAT
        TIME_FORMAT = current.TIME_FORMAT
        db = current.db
        T = current.T

        cls = Class(clsID, date)

        tax_rate = db.tax_rates(tax_rates_id)
        percentage = float(tax_rate.Percentage / 100)
        price = amount * (1 + percentage)

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

        # This calls self.on_update()
        self.set_amounts()

        return iiID


    def item_add_employee_claim_credit_payment(self,
                                                         ecID,
                                                        ):
        """
        :param clsID: db.classes.id
        :param date: datetime.date class date
        :return:
        """
        from os_teacher import Teacher
        from os_employee_claim import EmployeeClaim

        DATE_FORMAT = current.DATE_FORMAT
        TIME_FORMAT = current.TIME_FORMAT
        db = current.db
        T = current.T

        ec = EmployeeClaim(ecID)

        # Get amount & tax rate
        price = ec.row.Amount
        tax_rates_id = ec.row.tax_rates_id

        # add item to invoice
        if price > 0:
            next_sort_nr = self.get_item_next_sort_nr()

            iiID = db.invoices_items.insert(
                invoices_id=self.invoices_id,
                ProductName=T('Expense'),
                Description=ec.row.Description,
                Quantity=ec.row.Quantity,
                Price=price * -1,
                Sorting=next_sort_nr,
                tax_rates_id=tax_rates_id,
            )
            self.link_to_employee_claim(ecID)

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
        self.on_update()

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
            self.set_status('paid')
            self.invoice.update_record()
            return True
        else:
            self.set_status('sent')
            self.invoice.update_record()
            return False


    def is_credit_invoice(self):
        """
        True if credit invoice, False otherwise
        :return: Boolean
        """
        credit_invoice = False
        if self.invoice.credit_invoice_for:
            credit_invoice = True

        return credit_invoice


    def set_customer_info(self, cuID):
        """
            Set customer information for an invoice
        """
        from os_customer import Customer

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
            CustomerCompanyRegistration = customer.row.company_registration,
            CustomerCompanyTaxRegistration = customer.row.company_tax_registration,
            CustomerName = customer.row.full_name,
            CustomerListName = list_name,
            CustomerAddress = address,
        )

        self.on_update()


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

        self.on_update() # now we know which customer the invoice belongs to


    def link_to_customer_subscription(self, csID):
        """
            Link invoice to customer subscription
        """
        db = current.db
        db.invoices_customers_subscriptions.insert(
            invoices_id = self.invoices_id,
            customers_subscriptions_id = csID
        )


    def link_to_employee_claim(self, ecID):
        """
            Link invoice to employee claim
        """
        db = current.db
        db.invoices_employee_claims.insert(
            invoices_id = self.invoices_id,
            employee_claims_id = ecID
        )


    def link_to_teachers_payment_class(self, tpcID):
        """
            Link invoice to teachers payment class
        """
        db = current.db
        db.invoices_teachers_payment_classes.insert(
            invoices_id = self.invoices_id,
            teachers_payment_classes_id = tpcID
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

