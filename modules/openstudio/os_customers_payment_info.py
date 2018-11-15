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
