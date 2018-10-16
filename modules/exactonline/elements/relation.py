# vim: set ts=8 sw=4 sts=4 et ai tw=79:
"""
Data structures for communication with remote.

Example usage::

    class BossoExactCustomer(ExactCustomer):
        def __init__(self, bosso_relation=None, **kwargs):
            super(BossoExactRelation, self).__init__(**kwargs)

            self._bosso_relation = bosso_relation

        def get_code(self):
            return self._bosso_relation.code

        def get_name(self):
            return self._bosso_relation.name

        def get_address(self):
            address = self._bosso_relation.billing_address
            if address:
                return {
                    'AddressLine1': address.street_and_number(),
                    'Postcode': address.zipcode,
                    'City': address.city.name,
                }
            return {}

This file is part of the Exact Online REST API Library in Python
(EORALP), licensed under the LGPLv3+.
Copyright (C) 2015 Walter Doekes, OSSO B.V.
"""
from .base import ExactElement
from ..exceptions import ObjectDoesNotExist


class ExactRelation(ExactElement):
    def get_guid(self):
        exact_relation = self._api.relations.get(relation_code=self.get_code())
        return exact_relation['ID']

    def get_code(self):
        # The "foreign"/local relation code.
        raise NotImplementedError()

    def get_name(self):
        raise NotImplementedError()

    def get_address(self):
        # Return a dict, like:
        # {'AddressLine1': 'x', 'Postcode': 'y',
        #  'City': 'z'}
        return {}

    def assemble(self):
        # Compile a dict to be pushed.
        raise NotImplementedError()

    def commit(self):
        try:
            exact_guid = self.get_guid()
        except ObjectDoesNotExist:
            exact_guid = None

        data = self.assemble()

        if exact_guid:
            ret = self._api.relations.update(exact_guid, data)
            # ret is None
        else:
            ret = self._api.relations.create(data)
            # ret is a exact_relation

        return ret


class ExactCustomer(ExactRelation):
    def assemble(self):
        data = {
            # 18 spaces for code.
            'Code': '%18s' % (self.get_code(),),
            'Name': self.get_name(),
            # This speaks for itself.
            'PaymentConditionSales': 15,
            'PaymentConditionSalesDescription': 'Binnen 15 dagen',
            # This defaults to 1, no idea what this is.
            'InvoiceAttachmentType': 0,
            # Status is: A=supplier, C=customer (I think)
            # (suppliers have IsPurchase and IsSales as False and have
            # IsSupplier as True instead)
            'Status': 'C',
            'IsPurchase': True,
            'IsSales': True,
        }

        # Billing address.
        data.update(self.get_address())

        # Example data:
        # {'AccountManager': None,
        #  'AccountManagerFullName': None,
        #  'AccountManagerHID': None,
        #  'Accountant': None,
        #  'ActivitySector': None,
        #  'ActivitySubSector': None,
        #  'AddressLine1': 'SomeAddress 1',
        #  'AddressLine2': None,
        #  'AddressLine3': None,
        #  'BRIN': None,
        #  'BankAccounts': {u'__deferred':
        #    {u'uri': "https://start.exactonline.nl/api/v1/543210/\
        #              crm/Accounts(guid'eb7...600')/BankAccounts"}},
        #  'Blocked': False,
        #  'BusinessType': None,
        #  'CanDropShip': False,
        #  'ChamberOfCommerce': None,
        #  'City': 'SomeCity',
        #  'Classification': None,
        #  'ClassificationDescription': None,
        #  'Code': '               255',
        #  'CodeAtSupplier': None,
        #  'CompanySize': None,
        #  'ConsolidationScenario': 2,
        #  'ControlledDate': None,
        #  'CostPaid': 0,
        #  'Costcenter': None,
        #  'CostcenterDescription': None,
        #  'Country': 'NL ',
        #  'Created': '/Date(1392224884577)/',
        #  'Creator': 'e17...1cb',
        #  'CreatorFullName': 'Her...Bos',
        #  'CreditLinePurchase': 0,
        #  'CreditLineSales': 0,
        #  'Currency': None,
        #  'CustomerSince': None,
        #  'DiscountPurchase': 0,
        #  'DiscountSales': 0,
        #  'Division': 543210,
        #  'Document': None,
        #  'DunsNumber': None,
        #  'Email': None,
        #  'EndDate': None,
        #  'Fax': None,
        #  'GLAP': None,
        #  'GLAR': None,
        #  'GLAccountPurchase': None,
        #  'GLAccountSales': None,
        #  'ID': 'eb7...600',
        #  'IntraStatArea': None,
        #  'IntraStatDeliveryTerm': None,
        #  'IntraStatSystem': None,
        #  'IntraStatTransactionA': None,
        #  'IntraStatTransactionB': None,
        #  'IntraStatTransportMethod': None,
        #  'InvoiceAccount': None,
        #  'InvoiceAccountCode': None,
        #  'InvoiceAccountName': None,
        #  'InvoiceAttachmentType': 0,
        #  'InvoicingMethod': 0,
        #  'IsAccountant': 0,
        #  'IsAgency': 0,
        #  'IsBank': False,
        #  'IsCompetitor': 0,
        #  'IsMailing': 0,
        #  'IsMember': False,
        #  'IsPilot': False,
        #  'IsPurchase': True,
        #  'IsReseller': False,
        #  'IsSales': True,
        #  'IsSupplier': False,
        #  'Language': None,
        #  'LanguageDescription': None,
        #  'Latitude': None,
        #  'LeadSource': None,
        #  'Logo': None,
        #  'LogoFileName': None,
        #  'LogoThumbnailUrl': 'https://start.exactonline.nl//docs/images/\
        #                       placeholder_account_myeol.png',
        #  'LogoUrl': 'https://start.exactonline.nl//docs/images/\
        #              placeholder_account_myeol.png',
        #  'Longitude': None,
        #  'MainContact': None,
        #  'Modified': '/Date(1392228726777)/',
        #  'Modifier': 'e17...1cb',
        #  'ModifierFullName': 'Her...Bos',
        #  'Name': 'SOME CUSTOMER',
        #  'Parent': None,
        #  'PaymentConditionPurchase': None,
        #  'PaymentConditionPurchaseDescription': None,
        #  'PaymentConditionSales': '15',
        #  'PaymentConditionSalesDescription': 'Binnen 15 dagen',
        #  'Phone': None,
        #  'PhoneExtension': None,
        #  'Postcode': '1111 AA',
        #  'PriceList': None,
        #  'PurchaseCurrency': 'EUR',
        #  'PurchaseCurrencyDescription': 'Euro',
        #  'PurchaseLeadDays': 0,
        #  'PurchaseVATCode': None,
        #  'PurchaseVATCodeDescription': None,
        #  'RecepientOfCommissions': False,
        #  'Remarks': None,
        #  'Reseller': None,
        #  'ResellerCode': None,
        #  'ResellerName': None,
        #  'SalesCurrency': 'EUR',
        #  'SalesCurrencyDescription': 'Euro',
        #  'SalesVATCode': None,
        #  'SalesVATCodeDescription': None,
        #  'SearchCode': None,
        #  'SecurityLevel': 10,
        #  'SeparateInvPerProject': 0,
        #  'SeparateInvPerSubscription': 0,
        #  'ShippingLeadDays': 0,
        #  'ShippingMethod': None,
        #  'StartDate': '/Date(1392163200000)/',
        #  'State': None,
        #  'StateName': None,
        #  'Status': 'C',
        #  'StatusSince': '/Date(1392163200000)/',
        #  'Type': 'A',
        #  'VATLiability': None,
        #  'VATNumber': None,
        #  'Website': None,
        #  '__metadata': {u'type': 'Exact.Web.Api.Models.Account',
        #                  'uri': "https://start.exactonline.nl/api/v1/543210/\
        #                          crm/Accounts(guid'eb7...600')"}}

        return data
