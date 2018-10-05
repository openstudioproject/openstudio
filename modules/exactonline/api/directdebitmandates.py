# vim: set ts=8 sw=4 sts=4 et ai tw=79:
"""
Helper for direct debit mandates resources.

This file is part of the Exact Online REST API Library in Python
(EORALP), licensed under the LGPLv3+.
"""
from .manager import Manager


class DirectDebitMandates(Manager):
    resource = 'cashflow/DirectDebitMandates'
    
    def filter(self, ID=None, **kwargs):
        
        if 'top' not in kwargs:
            kwargs['top'] = 1
        
        if ID is not None:
            remote_id = self._remote_id(ID)
            # Filter by our account number.
            self._filter_append(kwargs, u"ID eq guid%s" % (remote_id,))

        return super(DirectDebitMandates, self).filter(**kwargs)

    def _remote_id(self, ID):
        return u"'%s'" % (ID.replace("'", "''"),)

