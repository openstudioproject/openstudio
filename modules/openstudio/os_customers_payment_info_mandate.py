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

        if self.row.exact_online_directdebitmandates_id:
            os_eo = OSExactOnline()
            os_eo.delete_dd_mandate(
                self.row.exact_online_directdebitmandates_id
            )
    #
    #
    # def exact_online_get_mandate(self):
    #     """
    #
    #     :return:
    #     """
    #     from openstudio.os_exact_online import OSExactOnline
    #     os_reference = self.row.MandateReference
    #
    #     if not eoID:
    #         return None
    #
    #     os_eo = OSExactOnline()
    #     api = os_eo.get_api()
    #
    #     return api.directdebitmandates.filter(reference=)
    #
    #
    # def exact_online_link_to_bankaccount(self, exact_online_bankaccount_id):
    #     """
    #     :param exact_online_relation_id: Exact Online crm/BankAccounts guid
    #     :return:
    #     """
    #     T = current.T
    #     db = current.db
    #     message = ''
    #
    #     query = (db.customers_payment_info.id != self.cpiID) & \
    #             (db.customers_payment_info.exact_online_bankaccount_id ==
    #                 exact_online_bankaccount_id)
    #     rows = db(query).select(
    #         db.customers_payment_info.id,
    #         db.customers_payment_info.auth_customer_id,
    #         db.customers_payment_info.AccountNumber
    #     )
    #
    #     if len(rows):
    #         row = rows.first()
    #
    #         message = SPAN(
    #             B(T("Unable to update Exact Online bank account link.")),
    #             T("This Exact Online bank account is already linked to "),
    #             A(row.display_name,
    #               _href=URL('customers', 'bankaccount', vars={'cpiID': row.id,
    #                                                           'cuID': row.auth_customer_id}),
    #               _target="_blank"),
    #             '.'
    #         )
    #     else:
    #         self.row.exact_online_bankaccount_id = exact_online_bankaccount_id
    #         self.row.update_record()
    #
    #         message = T("Updated link to Exact Online bank account")
    #
    #     return message
