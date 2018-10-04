# -*- coding: utf-8 -*-

from gluon import *


class OsCustomersPaymentInfoMandate:
    def __init__(self, cpimID):
        db = current.db

        self.cpimID = cpimID
        self.row = db.customers_payment_info_mandates(cpimID)


    def on_create(self):
        """

        :return:
        """
        from os_customers_payment_info import OsCustomersPaymentInfo
        from os_exact_online import OSExactOnline

        print 'Syncing mandate to Exact!'

        os_customer_payment_info = OsCustomersPaymentInfo(self.row.customers_payment_info_id)

        os_eo = OSExactOnline()
        os_eo.create_dd_mandate(
            os_customer_payment_info,
            self
        )


    def on_update(self):
        """

        :return:
        """
        from os_customer import Customer
        from os_exact_online import OSExactOnline

        os_customer = Customer(self.row.auth_customer_id)

        os_eo = OSExactOnline()
        #os_eo.update_dd_mandate(os_customer, self)


    def on_delete(self):
        """

        :return:
        """
        from os_exact_online import OSExactOnline

        os_eo = OSExactOnline()
        os_eo.delete_dd_mandate(
            self.row.exact_online_directdebitmandates_id
        )
