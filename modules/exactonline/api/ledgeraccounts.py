# vim: set ts=8 sw=4 sts=4 et ai tw=79:
"""
Helper for ledgeraccount resources.

This file is part of the Exact Online REST API Library in Python
(EORALP), licensed under the LGPLv3+.
Copyright (C) 2015 Walter Doekes, OSSO B.V.
"""
from .manager import Manager


class LedgerAccounts(Manager):
    resource = 'financial/GLAccounts'

    def filter(self, code__in=None, **kwargs):
        # $select=ID,Code,Name
        if 'select' not in kwargs:
            kwargs['select'] = 'ID,Code'

        if code__in is not None:
            code_filter = []
            for code in code__in:
                code = self._remote_code(code)
                code_filter.append(u'Code eq %s' % (code,))
            self._filter_append(kwargs, u'(%s)' % (u' or '.join(code_filter),))
        return super(LedgerAccounts, self).filter(**kwargs)

    def _remote_code(self, code):
        return u"'%s'" % (code.replace("'", "''"),)
