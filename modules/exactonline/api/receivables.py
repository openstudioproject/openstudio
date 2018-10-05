# vim: set ts=8 sw=4 sts=4 et ai tw=79:
"""
Helper for receivables (invoices sent by you).

This file is part of the Exact Online REST API Library in Python
(EORALP), licensed under the LGPLv3+.
Copyright (C) 2015 Walter Doekes, OSSO B.V.
"""
from .manager import Manager


class Receivables(Manager):
    """
    Get the elements that make up the Financial Reporting of Outstanding
    Receivables, you call this.
    """
    resource = 'read/financial/ReceivablesList'

    def filter(self, relation_id=None, duedate__lt=None, duedate__gte=None,
               **kwargs):
        """
        A common query would be duedate__lt=date(2015, 1, 1) to get all
        Receivables that are due in 2014 and earlier.
        """
        if relation_id is not None:
            # Filter by (relation) account_id. There doesn't seem to be
            # any reason to prefer
            # 'read/financial/ReceivablesListByAccount?accountId=X' over
            # this.
            relation_id = self._remote_guid(relation_id)
            self._filter_append(kwargs, u'AccountId eq %s' % (relation_id,))

        if duedate__lt is not None:
            # Not sure what the AgeGroup means in
            # ReceivablesListByAgeGroup, but we can certainly do
            # without.
            duedate__lt = self._remote_datetime(duedate__lt)
            self._filter_append(kwargs, u'DueDate lt %s' % (duedate__lt,))

        if duedate__gte is not None:
            # Not sure what the AgeGroup means in
            # ReceivablesListByAgeGroup, but we can certainly do
            # without.
            duedate__gte = self._remote_datetime(duedate__gte)
            self._filter_append(kwargs, u'DueDate ge %s' % (duedate__gte,))

        return super(Receivables, self).filter(**kwargs)
