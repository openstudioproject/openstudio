# -*- coding: utf-8 -*-

from gluon import *


class OSMoneybird:
    def get_api(self):
        """
        Return Moneybird API 
        """
        import os
        from moneybird import MoneyBird, TokenAuthentication
        from tools import OsTools
        
        os_tools = OsTools()

        return MoneyBird(TokenAuthentication(os_tools.get_sys_property('moneybird_token')))


    def create_sales_entry(self, os_invoice):
        """
        :param os_customer: OsCustomer object
        :param os_invoice: OsInvoice Object
        :return:
        """
        from exactonline.resource import GET
        from os_customer import Customer
        from tools import OsTools

        db = current.db
        os_tools = OsTools()
        authorized = os_tools.get_sys_property('moneybird_administration_id')

        if not authorized:
            self._log_error(
                'create',
                'sales_entry',
                os_invoice.invoice.id,
                "Moneybird integration not authorized"
            )

            return

        items = os_invoice.get_invoice_items_rows()
        if not len(items):
            return # Don't do anything for invoices without items


        import pprint

        from ConfigParser import NoOptionError
        from exactonline.http import HTTPError

        storage = self.get_storage()
        api = self.get_api()
        cuID = os_invoice.get_linked_customer_id()
        os_customer = Customer(os_invoice.get_linked_customer_id())
        eoID = os_customer.row.exact_online_relation_id

        if not eoID:
            self._log_error(
                'create',
                'sales_entry',
                os_invoice.invoice.id,
                "This customer is not linked to Moneybird - " + unicode(os_customer.row.id)
            )
            return

        try:
            selected_division = int(storage.get('transient', 'division'))
        except NoOptionError:
            selected_division = None

        amounts = os_invoice.get_amounts()

        remote_journal = os_invoice.invoice_group.JournalID
        invoice_date = os_invoice.invoice.DateCreated
        is_credit_invoice = os_invoice.is_credit_invoice()
        local_invoice_number = os_invoice.invoice.id
        payment_method = os_invoice.get_payment_method()

        invoice_data = {
            'AmountDC': str(amounts.TotalPriceVAT),  # DC = default currency
            'AmountFC': str(amounts.TotalPriceVAT),  # FC = foreign currency
            'EntryDate': invoice_date.strftime('%Y-%m-%dT%H:%M:%SZ'),  # pretend we're in UTC
            'Customer': eoID,
            'Description': os_invoice.invoice.Description,
            'Journal': remote_journal,  # 70 "Verkoopboek"
            'ReportingPeriod': invoice_date.month,
            'ReportingYear': invoice_date.year,
            'SalesEntryLines': self.format_os_sales_entry_lines(os_invoice),
            'VATAmountDC': str(amounts.VAT),
            'VATAmountFC': str(amounts.VAT),
            'YourRef': local_invoice_number,
        }

        if payment_method and payment_method.AccountingCode:
            invoice_data['PaymentCondition'] = payment_method.AccountingCode

        if is_credit_invoice:
            invoice_data['Type'] = 21


        error = False

        try:
            result = api.invoices.create(invoice_data)
            #
            # print "Create invoice result:"
            # pp = pprint.PrettyPrinter(depth=6)
            # pp.pprint(result)

            eoseID = result['EntryID']
            os_invoice.invoice.ExactOnlineSalesEntryID = eoseID
            os_invoice.invoice.InvoiceID = result['EntryNumber']
            os_invoice.invoice.update_record()

            uri = result[u'SalesEntryLines'][u'__deferred']['uri']
            entry_lines = api.restv1(GET(str(uri)))
            # pp.pprint(entry_lines)

            for i, line in enumerate(entry_lines):
                query = (db.invoices_items.invoices_id == os_invoice.invoice.id) & \
                        (db.invoices_items.Sorting == i + 1)
                db(query).update(ExactOnlineSalesEntryLineID = line['ID'])

        except HTTPError as e:
            error = True
            self._log_error(
                'create',
                'sales_entry',
                os_invoice.invoice.id,
                e
            )

        if error:
            return False

        return eoseID


    def update_sales_entry(self, os_invoice):
        """
        :param os_customer: OsCustomer object
        :return: None
        """
        from exactonline.resource import GET

        from os_customer import Customer
        from tools import OsTools

        os_tools = OsTools()
        authorized = os_tools.get_sys_property('moneybird_administration_id')

        if not authorized:
            self._log_error(
                'update',
                'sales_entry',
                os_invoice.invoice.id,
                "Moneybird integration not authorized"
            )

            return

        items = os_invoice.get_invoice_items_rows()
        if not len(items):
            return # Don't do anything for invoices without items

        eoseID = os_invoice.invoice.ExactOnlineSalesEntryID

        if not eoseID:
            self.create_sales_entry(os_invoice)
            return


        import pprint

        from ConfigParser import NoOptionError
        from exactonline.http import HTTPError

        storage = self.get_storage()
        api = self.get_api()
        cuID = os_invoice.get_linked_customer_id()
        os_customer = Customer(os_invoice.get_linked_customer_id())

        try:
            selected_division = int(storage.get('transient', 'division'))
        except NoOptionError:
            selected_division = None

        amounts = os_invoice.get_amounts()

        remote_journal = os_invoice.invoice_group.JournalID
        invoice_date = os_invoice.invoice.DateCreated
        is_credit_invoice = os_invoice.is_credit_invoice()
        local_invoice_number = os_invoice.invoice.id
        payment_method = os_invoice.get_payment_method()

        invoice_data = {
            'AmountDC': str(amounts.TotalPriceVAT),  # DC = default currency
            'AmountFC': str(amounts.TotalPriceVAT),  # FC = foreign currency
            'EntryDate': invoice_date.strftime('%Y-%m-%dT%H:%M:%SZ'),  # pretend we're in UTC
            'Customer': os_customer.row.exact_online_relation_id,
            'Description': os_invoice.invoice.Description,
            'Journal': remote_journal,  # 70 "Verkoopboek"
            'ReportingPeriod': invoice_date.month,
            'ReportingYear': invoice_date.year,
            'VATAmountDC': str(amounts.VAT),
            'VATAmountFC': str(amounts.VAT),
            'YourRef': local_invoice_number,
        }

        if payment_method and payment_method.AccountingCode:
            invoice_data['PaymentCondition'] = payment_method.AccountingCode
            
        if is_credit_invoice:
            invoice_data['Type'] = 21

        error = False

        try:
            result = api.invoices.update(eoseID, invoice_data)
            # print "Update invoice result:"
            # pp = pprint.PrettyPrinter(depth=6)
            # pp.pprint(result)

            self.update_sales_entry_lines(os_invoice)

        except HTTPError as e:
            error = True
            self._log_error(
                'create',
                'sales_entry',
                os_invoice.invoice.id,
                e
            )

        if error:
            return False


    def create_sales_entry_line(self, line):
        """
        :param line: dict
        :return:
        """
        api = self.get_api()

        return api.salesentrylines.create(line)


    def update_sales_entry_line(self, ID, line):
        """
        :param line: dict
        :return:
        """
        api = self.get_api()

        return api.salesentrylines.update(ID, line)


    def delete_sales_entry_line(self, ID):
        """
        :param ID: Moneybird SalesEntryLine ID
        :return:
        """
        api = self.get_api()

        return api.salesentrylines.delete(ID)


    def update_sales_entry_lines(self, os_invoice):
        """
        :param os_invoice: Invoice object
        :return:
        """
        db = current.db

        is_credit_invoice = os_invoice.is_credit_invoice()

        items = os_invoice.get_invoice_items_rows()

        for item in items:
            glaccount = self.get_glaccount(item.GLAccount)
            tax_rate = db.tax_rates(item.tax_rates_id)
            line = {
                'AmountFC': item.TotalPrice,
                'Description': item.Description,
                'GLAccount': glaccount[0][u'ID'],
                'Quantity': item.Quantity,
                'VATCode': tax_rate.VATCodeID
            }

            if is_credit_invoice:
                line['Type'] = 21

            ID = item.ExactOnlineSalesEntryLineID

            if not ID: # Create
                line['AmountDC'] = item.TotalPrice
                line['EntryID'] = os_invoice.invoice.ExactOnlineSalesEntryID

                result = self.create_sales_entry_line(line)

                item.ExactOnlineSalesEntryLineID = result['ID']
                item.update_record()

            else: # Update
                result = self.update_sales_entry_line(ID, line)


    def get_glaccount(self, code):
        """
        :param code: Exact G/L Account code. eg. 0150
        :return: glaccount dict
        """
        api = self.get_api()

        return api.financialglaccounts.filter(Code=code)


    def get_journal(self, code):
        """
        :param code: Exact G/L Account code. eg. 0150
        :return: glaccount dict
        """
        api = self.get_api()

        return api.financialjournals.filter(Code=code)


    def get_sales_entry(self, os_invoice):
        """
        :param os_invoice: Invoice object
        :return: SalesEntry dict
        """
        api = self.get_api()

        return api.invoices.filter(
            invoice_number=unicode(os_invoice.invoice.id)
        )


    def format_os_sales_entry_lines(self, os_invoice):
        """
        GLAccount is gotten from API for each call
        :param os_invoice: Invoice object
        :return: SalesEntryLines dict
        """
        db = current.db

        is_credit_invoice = os_invoice.is_credit_invoice()
        items = os_invoice.get_invoice_items_rows()

        lines = []
        for item in items:
            glaccount = self.get_glaccount(item.GLAccount)

            tax_rate = db.tax_rates(item.tax_rates_id)
            line = {
                'AmountDC': item.TotalPrice,
                'AmountFC': item.TotalPrice,
                'Description': item.Description,
                'GLAccount': glaccount[0][u'ID'],
                'Quantity': item.Quantity,
                'VATCode': tax_rate.VATCodeID,
            }

            if is_credit_invoice:
                line['Type'] = 21

            lines.append(line)


        return lines


    def create_contact(self, os_customer):
        """
        :param os_customer: OsCustomer object
        :return: Moneybird relation id
        """
        from tools import OsTools
        from moneybird import MoneyBird

        os_tools = OsTools()
        authorized = os_tools.get_sys_property('moneybird_administration_id')

        if not authorized:
            self._log_error(
                'create',
                'relation',
                os_customer.row.id,
                "Moneybird not authorized"
            )

            return

        else:
            api = self.get_api()

            contact_data = {
                "contact": {
                    "firstname": os_customer.row.first_name,
                    "lastname": os_customer.row.last_name,
                    "address1": os_customer.row.address,
                    "phone": os_customer.row.phone,
                    "zipcode": os_customer.row.postcode,
                    "city": os_customer.row.city,
                    "send_invoices_to_email": os_customer.row.email,
                    "tax_number": os_customer.row.company_tax_registration,
                    "chamber_of_commerce": os_customer.row.company_registration,
                    "country": os_customer.row.country,
                }
            }
            error = False

            try:
                result = api.post('contacts', contact_data, authorized)
                rel_id = result['id']

                os_customer.row.moneybird_contact_id = rel_id
                os_customer.row.update_record()

            except MoneyBird.APIError as e:
                error = True
                self._log_error(
                    'create',
                    'relation',
                    os_customer.row.id,
                    e
                )

            if error:
                return False

            return rel_id


    def update_contact(self, os_customer):
        """
        :param os_customer: OsCustomer object
        :return: dict(error=True|False, message='')
        """
        from tools import OsTools
        from moneybird import MoneyBird

        os_tools = OsTools()
        authorized = os_tools.get_sys_property('moneybird_administration_id')

        if not authorized:
            self._log_error(
                'create',
                'contact',
                os_customer.row.id,
                "Moneybird integration not authorized"
            )

            return

        mbID = os_customer.row.moneybird_contact_id

        if not mbID:
            self.create_contact(os_customer)
            return
            
        api = self.get_api()

        contact_data = {
                "contact": {
                    "firstname": os_customer.row.first_name,
                    "lastname": os_customer.row.last_name,
                    "address1": os_customer.row.address,
                    "phone": os_customer.row.phone,
                    "zipcode": os_customer.row.postcode,
                    "city": os_customer.row.city,
                    "send_invoices_to_email": os_customer.row.email,
                    "tax_number": os_customer.row.company_tax_registration,
                    "chamber_of_commerce": os_customer.row.company_registration,
                    "country": os_customer.row.country,
                }
            }

        error = False
        message = ''

        try:
            result = api.patch('contacts/'+mbID, contact_data, authorized)
        except MoneyBird.APIError as e:
            error = True
            message = e

            self._log_error(
                'update',
                'contact',
                os_customer.row.id,
                e
            )


        return dict(error=error, message=message)


    def _log_error(self, action, object, object_id, result):
        """
        :param action: should be in ['create', 'read', 'update', 'delete']
        :param object: object name
        :param object_id: object id
        :param message: string
        :return: None
        """
        db = current.db

        db.integration_moneybird_log.insert(
            ActionName = action,
            ObjectName = object,
            ObjectID = object_id,
            ActionResult = result,
            Status = 'fail'
        )