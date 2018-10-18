# -*- coding: utf-8 -*-
"""
    This file holds OpenStudio MailChimp class
"""

from gluon import *


class PaymentBatch:
    def __init__(self, pbID):
        """
        :param pbID: db.payment_batches_id
        """
        db = current.db
        get_sys_property = current.globalenv['get_sys_property']

        self.id = pbID
        self.row = db.payment_batches(pbID)

        self.currency = get_sys_property('Currency') or 'EUR'


    def generate_batch_items(self):
        """
        Generate batch items for this payment batch
        :return: None
        """
        if self.row.BatchTypeDescription == 'teacher_payments':
            self._generate_batch_items_teacher_payments()
        elif self.row.BatchTypeDescription == 'employee_claims':
            self._generate_batch_items_employee_claims()


    def _generate_batch_items_teacher_payments(self):
        """
        :return: None
        """
        db = current.db

        # Get teacher payment invoices with status sent for month
        left = [
            db.invoices_amounts.on(
                db.invoices_amounts.invoices_id ==
                db.invoices.id
            ),
            db.invoices_customers.on(
                db.invoices_customers.invoices_id ==
                db.invoices.id
            ),
            db.auth_user.on(
                db.invoices_customers.auth_customer_id ==
                db.auth_user.id
            ),
            db.customers_payment_info.on(
                db.customers_payment_info.auth_customer_id ==
                db.auth_user.id
            )
        ]

        query = (db.invoices.TeacherPayment == True) & \
                (db.invoices.Status == 'sent')

        rows = db(query).select(db.invoices.ALL,
                                db.auth_user.ALL,
                                db.invoices_amounts.ALL,
                                db.customers_payment_info.ALL,
                                left=left,
                                orderby=db.auth_user.id)

        print rows


        for row in rows:
            cuID = row.auth_user.id
            csID = row.invoices.customers_subscriptions_id
            iID = row.invoices.id

            amount = row.invoices_amounts.TotalPriceVAT

            # check for zero amount
            if not self.row.IncludeZero and amount == 0:
                continue

            # set description
            description = row.invoices.Description
            if not description:
                description = self.row.Description

            try:
                description = description.strip()
            except:
                pass

            # set account number
            try:
                accountnr = row.customers_payment_info.AccountNumber.strip()
            except AttributeError:
                accountnr = ''
            # set BIC
            try:
                bic = row.customers_payment_info.BIC.strip()
            except AttributeError:
                bic = ''

            msdate = row.customers_payment_info.MandateSignatureDate

            # set bank name
            if row.customers_payment_info.BankName == '':
                row.customers_payment_info.BankName = None

            db.payment_batches_items.insert(
                payment_batches_id=self.id,
                auth_customer_id=cuID,
                customers_subscriptions_id=csID,
                invoices_id=iID,
                AccountHolder=row.customers_payment_info.AccountHolder,
                BIC=bic,
                AccountNumber=accountnr,
                MandateSignatureDate=msdate,
                Amount=amount,
                Currency=self.currency,
                Description=description,
                BankName=row.customers_payment_info.BankName,
                BankLocation=row.customers_payment_info.BankLocation
            )


    def _generate_batch_items_employee_claims(self):
        """
        :return: None
        """
        db = current.db

        # Get teacher payment invoices with status sent for month
        left = [
            db.invoices_amounts.on(
                db.invoices_amounts.invoices_id ==
                db.invoices.id
            ),
            db.invoices_customers.on(
                db.invoices_customers.invoices_id ==
                db.invoices.id
            ),
            db.auth_user.on(
                db.invoices_customers.auth_customer_id ==
                db.auth_user.id
            ),
            db.customers_payment_info.on(
                db.customers_payment_info.auth_customer_id ==
                db.auth_user.id
            )
        ]

        query = (db.invoices.EmployeeClaim == True) & \
                (db.invoices.Status == 'sent')

        rows = db(query).select(db.invoices.ALL,
                                db.auth_user.ALL,
                                db.invoices_amounts.ALL,
                                db.customers_payment_info.ALL,
                                left=left,
                                orderby=db.auth_user.id)

        print rows

        for row in rows:
            cuID = row.auth_user.id
            csID = row.invoices.customers_subscriptions_id
            iID = row.invoices.id

            amount = row.invoices_amounts.TotalPriceVAT

            # check for zero amount
            if not self.row.IncludeZero and amount == 0:
                continue

            # set description
            description = row.invoices.Description
            if not description:
                description = self.row.Description

            try:
                description = description.strip()
            except:
                pass

            # set account number
            try:
                accountnr = row.customers_payment_info.AccountNumber.strip()
            except AttributeError:
                accountnr = ''
            # set BIC
            try:
                bic = row.customers_payment_info.BIC.strip()
            except AttributeError:
                bic = ''

            msdate = row.customers_payment_info.MandateSignatureDate

            # set bank name
            if row.customers_payment_info.BankName == '':
                row.customers_payment_info.BankName = None

            db.payment_batches_items.insert(
                payment_batches_id=self.id,
                auth_customer_id=cuID,
                customers_subscriptions_id=csID,
                invoices_id=iID,
                AccountHolder=row.customers_payment_info.AccountHolder,
                BIC=bic,
                AccountNumber=accountnr,
                MandateSignatureDate=msdate,
                Amount=amount,
                Currency=self.currency,
                Description=description,
                BankName=row.customers_payment_info.BankName,
                BankLocation=row.customers_payment_info.BankLocation
            )
