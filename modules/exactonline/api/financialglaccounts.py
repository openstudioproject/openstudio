# vim: set ts=8 sw=4 sts=4 et ai tw=79:
"""
Helper for financial/GLAccounts resources.

This file is part of the Exact Online REST API Library in Python
(EORALP), licensed under the LGPLv3+.
"""
from .manager import Manager


class FinancialGLAccounts(Manager):
    resource = 'financial/GLAccounts'
    
    def filter(self, ID=None, Code=None, **kwargs):
	
        if ID is not None:
            remote_id = self._remote_id(ID)
            # Filter by our account number.
            self._filter_append(kwargs, u"ID eq guid%s" % (remote_id,))
	
        if Code is not None:
            remote_id = self._remote_id(Code)
            # Filter by our account number.
            self._filter_append(kwargs, u"Code eq guid%s" % (remote_id,))
            

        return super(FinancialGLAccounts, self).filter(**kwargs)

    def _remote_id(self, ID):
        return u"'%s'" % (ID.replace("'", "''"),)

