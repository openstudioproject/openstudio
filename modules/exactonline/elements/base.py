# vim: set ts=8 sw=4 sts=4 et ai tw=79:
"""
Data structures for communication with remote.

This file is part of the Exact Online REST API Library in Python
(EORALP), licensed under the LGPLv3+.
Copyright (C) 2015 Walter Doekes, OSSO B.V.
"""


class ExactElement(object):
    def __init__(self, api=None, **kwargs):
        super(ExactElement, self).__init__(**kwargs)

        self._api = api

    def get_guid(self):
        # Raises ObjectDoesNotExist if it cannot be found remotely.
        raise NotImplementedError()

    def commit(self):
        # This needs API specific work.
        raise NotImplementedError()
