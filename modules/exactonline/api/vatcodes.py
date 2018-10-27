# vim: set ts=8 sw=4 sts=4 et ai tw=79:
"""
Helper for vat code resources.

This file is part of the Exact Online REST API Library in Python
(EORALP), licensed under the LGPLv3+.
Copyright (C) 2017 Walter Doekes, OSSO B.V.
"""
from .manager import Manager


class VatCodes(Manager):
    resource = 'vat/VATCodes'

    def filter(self, vat_code=None, **kwargs):
        # $select=ID,Code,Percentage
        if 'select' not in kwargs:
            kwargs['select'] = 'ID,Code,Percentage'

        if vat_code is not None:
            remote_id = self._remote_vat_code(vat_code)
            self._filter_append(kwargs, u'Code eq %s' % (remote_id,))
        return super(VatCodes, self).filter(**kwargs)

    def get_percentage(self, vat_code=None, **kwargs):
        vat = super(VatCodes, self).get(
            vat_code=vat_code, select='Percentage', **kwargs)
        return vat['Percentage']

    def _remote_vat_code(self, code):
        return u"'%s'" % (code.replace("'", "''"),)
