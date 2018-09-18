# vim: set ts=8 sw=4 sts=4 et ai tw=79:
"""
Resource request methods.

This file is part of the Exact Online REST API Library in Python
(EORALP), licensed under the LGPLv3+.
Copyright (C) 2016-2017 Walter Doekes, OSSO B.V.
"""


class _Resource(object):
    """
    Base class for HTTP/REST requests.

    Used so we don't have to pass three variables around: method, path
    and data. Instead we pass around a POST(path, data) as single
    argument.

    Change properties through the update method. It creates a cloned
    object with the new values::

        r = POST('crmAccount')
        r2 = r.update(resource=('v1/' + r.resource))

    """
    def __init__(self, resource, data=None):
        self._resource = resource  # or "path" or "full url"
        self._data = data

    def __repr__(self):
        return '%s(%r, %r)' % (self.method, self.resource, self.data)

    @property
    def method(self):
        return self.__class__.__name__

    @property
    def resource(self):
        return self._resource

    @property
    def data(self):
        return self._data

    def update(self, **kwargs):
        new_data = dict(**kwargs)

        for prop in ('data', 'resource'):
            if prop not in new_data:
                new_data[prop] = getattr(self, prop)

        return self.__class__(**new_data)


class DELETE(_Resource):
    pass


class GET(_Resource):
    pass


class POST(_Resource):
    pass


class PUT(_Resource):
    pass
