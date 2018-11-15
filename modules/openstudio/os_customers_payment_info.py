# -*- coding: utf-8 -*-

from gluon import *


class OsCustomersPaymentInfo:
    def __init__(self, cpiID):
        db = current.db

        self.cpiID = cpiID
        self.row = db.customers_payment_info(cpiID)


    def on_create(self):
        """

        :return:
        """
        from os_customer import Customer
        from os_exact_online import OSExactOnline

        os_customer = Customer(self.row.auth_customer_id)

        os_eo = OSExactOnline()
        os_eo.create_bankaccount(os_customer, self)


    def on_update(self):
        """

        :return:
        """
        from os_customer import Customer
        from os_exact_online import OSExactOnline

        os_customer = Customer(self.row.auth_customer_id)

        os_eo = OSExactOnline()
        os_eo.update_bankaccount(os_customer, self)


    def exact_online_get_bankaccount(self):
        """

        :return:
        """
        from openstudio.os_exact_online import OSExactOnline
        eoID = self.row.exact_online_bankaccount_id

        if not eoID:
            return None

        os_eo = OSExactOnline()
        api = os_eo.get_api()

        return api.bankaccounts.filter(ID=eoID)


    def exact_online_link_to_bankaccount(self, exact_online_bankaccount_id):
        """
        :param exact_online_relation_id: Exact Online crm/BankAccounts guid
        :return:
        """
        T = current.T
        db = current.db
        message = ''

        query = (db.customers_payment_info.id != self.cpiID) & \
                (db.customers_payment_info.exact_online_bankaccount_id ==
                    exact_online_bankaccount_id)
        rows = db(query).select(
            db.customers_payment_info.id,
            db.customers_payment_info.auth_customer_id,
            db.customers_payment_info.AccountNumber
        )

        if len(rows):
            row = rows.first()

            message = SPAN(
                B(T("Unable to update Exact Online bank account link.")),
                T("This Exact Online bank account is already linked to "),
                A(row.display_name,
                  _href=URL('customers', 'bankaccount', vars={'cpiID': row.id,
                                                              'cuID': row.auth_customer_id}),
                  _target="_blank"),
                '.'
            )
        else:
            self.row.exact_online_bankaccount_id = exact_online_bankaccount_id
            self.row.update_record()

            message = T("Updated link to Exact Online bank account")

        return message
