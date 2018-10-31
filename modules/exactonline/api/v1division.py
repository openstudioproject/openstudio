# vim: set ts=8 sw=4 sts=4 et ai tw=79:
"""
Autoselects the division.

This file is part of the Exact Online REST API Library in Python
(EORALP), licensed under the LGPLv3+.
Copyright (C) 2015-2017 Walter Doekes, OSSO B.V.
"""
from ..exceptions import ExactOnlineError
from ..http import urljoin
from ..resource import GET
from ..storage import NoOptionError


class V1DivisionError(ExactOnlineError):
    pass


class V1Division(object):
    def restv1(self, request):
        try:
            division = self.storage.get_division()
        except NoOptionError:
            raise V1DivisionError('Division unset/blank in config')
        if not division:
            raise V1DivisionError('Division unset/blank in config')

        urlbase = 'v1/%d/' % (division,)
        request = request.update(resource=urljoin(urlbase, request.resource))
        return self.rest(request)

    def get_divisions(self):
        """
        Get the "current" division and return a dictionary of divisions
        so the user can select the right one.
        """
        ret = self.rest(GET('v1/current/Me?$select=CurrentDivision'))
        current_division = ret[0]['CurrentDivision']
        assert isinstance(current_division, int)

        urlbase = 'v1/%d/' % (current_division,)
        resource = urljoin(urlbase, 'hrm/Divisions?$select=Code,Description')
        ret = self.rest(GET(resource))

        choices = dict((i['Code'], i['Description']) for i in ret)
        return choices, current_division

    def set_division(self, division):
        """
        Select the "current" division that we'll be working on/with.
        """
        try:
            division = int(division)
        except (TypeError, ValueError):
            raise V1DivisionError('Supplied division %r is not a number' %
                                  (division,))

        urlbase = 'v1/%d/' % (division,)
        resource = urljoin(
            urlbase,
            "crm/Accounts?$select=ID&$filter=Name+eq+'DOES_NOT_EXIST'")
        try:
            self.rest(GET(resource))
        except AssertionError:
            raise V1DivisionError('Invalid division %r according to server' %
                                  (division,))

        self.storage.set_division(division)
