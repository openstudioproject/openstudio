# vim: set ts=8 sw=4 sts=4 et ai tw=79:
"""
Standard exceptions.

This file is part of the Exact Online REST API Library in Python
(EORALP), licensed under the LGPLv3+.
Copyright (C) 2015 Walter Doekes, OSSO B.V.
"""


class ExactOnlineError(Exception):
    pass


class MultipleObjectsReturned(ExactOnlineError):
    """
    Exception named Django style.
    """
    pass


class ObjectDoesNotExist(ExactOnlineError):
    """
    Exception named Django style.
    """
    pass
