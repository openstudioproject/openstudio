# vim: set ts=8 sw=4 sts=4 et ai tw=79:
"""
Helper for invoice resources.

This file is part of the Exact Online REST API Library in Python
(EORALP), licensed under the LGPLv3+.
Copyright (C) 2015-2017 Walter Doekes, OSSO B.V.
"""
from .manager import Manager
from ..resource import GET


class Invoices(Manager):
    resource = 'salesentry/SalesEntries'

    def get(self, **kwargs):
        invoice_dict = super(Invoices, self).get(**kwargs)
        try:
            uri = invoice_dict[u'SalesEntryLines'][u'__deferred']['uri']
        except KeyError:
            # Perhaps there is a 'select' filter.
            pass
        else:
            invoicelines_dict = self._api.restv1(GET(str(uri)))
            invoice_dict[u'SalesEntryLines'] = invoicelines_dict
        return invoice_dict

    def filter(self, invoice_number=None, invoice_number__in=None,
               reporting_period=None, **kwargs):
        if invoice_number is not None:
            remote_id = self._remote_invoice_number(invoice_number)
            # Filter by our invoice_number.
            self._filter_append(kwargs, u'YourRef eq %s' % (remote_id,))
            # # Let the query return the invoice lines too. <-- DOES NOT WORK
            # assert 'expand' not in kwargs
            # kwargs['expand'] = 'SalesInvoiceLines'
            # kwargs['select'] = ('Amount,SalesInvoiceLines/LineNumber,'
            #                     'SalesInvoiceLines/Amount,'
            #                     'SalesInvoiceLines/VATAmount')

        if invoice_number__in is not None:
            # Filter by any of the supplied invoice numbers.
            remote_filter = []
            for invoice_number in invoice_number__in:
                remote_id = self._remote_invoice_number(invoice_number)
                remote_filter.append(u'YourRef eq %s' % (remote_id,))
            self._filter_append(
                kwargs, u'(%s)' % (u' or '.join(remote_filter),))

        if reporting_period is not None:
            # Filter by reporting period.
            self._filter_append(
                kwargs, u'ReportingYear eq %d' % (reporting_period.year,))
            self._filter_append(
                kwargs, u'ReportingPeriod eq %d' % (reporting_period.month,))

        return super(Invoices, self).filter(**kwargs)

    def map_exact2foreign_invoice_numbers(self, exact_invoice_numbers=None):
        """
        Optionally supply a list of ExactOnline invoice numbers.

        Returns a dictionary of ExactOnline invoice numbers to foreign
        (YourRef) invoice numbers.
        """
        # Quick, select all. Not the most nice to the server though.
        if exact_invoice_numbers is None:
            ret = self.filter(select='InvoiceNumber,YourRef')
            return dict((i['InvoiceNumber'], i['YourRef']) for i in ret)

        # Slower, select what we want to know. More work for us.
        exact_to_foreign_map = {}

        # Do it in batches. If we append 300 InvoiceNumbers at once, we
        # get a 12kB URI. (If the list is empty, we skip the entire
        # forloop and correctly return the empty dict.)
        exact_invoice_numbers = list(set(exact_invoice_numbers))  # unique
        for offset in range(0, len(exact_invoice_numbers), 40):
            batch = exact_invoice_numbers[offset:(offset + 40)]
            filter_ = ' or '.join(
                'InvoiceNumber eq %s' % (i,) for i in batch)
            assert filter_  # if filter was empty, we'd get all!
            ret = self.filter(filter=filter_, select='InvoiceNumber,YourRef')
            exact_to_foreign_map.update(
                dict((i['InvoiceNumber'], i['YourRef']) for i in ret))

        # Any values we missed?
        for exact_invoice_number in exact_invoice_numbers:
            if exact_invoice_number not in exact_to_foreign_map:
                exact_to_foreign_map[exact_invoice_number] = None

        return exact_to_foreign_map

    def map_foreign2exact_invoice_numbers(self, foreign_invoice_numbers=None):
        """
        Optionally supply a list of foreign (your) invoice numbers.

        Returns a dictionary of your invoice numbers (YourRef) to Exact
        Online invoice numbers.
        """
        # Quick, select all. Not the most nice to the server though.
        if foreign_invoice_numbers is None:
            ret = self.filter(select='InvoiceNumber,YourRef')
            return dict((i['YourRef'], i['InvoiceNumber']) for i in ret)

        # Slower, select what we want to know. More work for us.
        foreign_to_exact_map = {}

        # Do it in batches. If we append 300 InvoiceNumbers at once, we
        # get a 12kB URI. (If the list is empty, we skip the entire
        # forloop and correctly return the empty dict.)
        foreign_invoice_numbers = list(set(foreign_invoice_numbers))  # unique
        for offset in range(0, len(foreign_invoice_numbers), 40):
            batch = foreign_invoice_numbers[offset:(offset + 40)]
            filter_ = ' or '.join(
                'YourRef eq %s' % (self._remote_invoice_number(i),)
                for i in batch)
            assert filter_  # if filter was empty, we'd get all!
            ret = self.filter(filter=filter_, select='InvoiceNumber,YourRef')
            foreign_to_exact_map.update(
                dict((i['YourRef'], i['InvoiceNumber']) for i in ret))

        # Any values we missed?
        for foreign_invoice_number in foreign_invoice_numbers:
            if foreign_invoice_number not in foreign_to_exact_map:
                foreign_to_exact_map[foreign_invoice_number] = None

        return foreign_to_exact_map

    def _remote_invoice_number(self, invoice_number):
        return u"'%s'" % (invoice_number.replace("'", "''"),)
