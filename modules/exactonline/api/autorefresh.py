# vim: set ts=8 sw=4 sts=4 et ai tw=79:
"""
Refreshes OAuth tokens as-needed on receiving a 401.

This file is part of the Exact Online REST API Library in Python
(EORALP), licensed under the LGPLv3+.
Copyright (C) 2015-2017 Walter Doekes, OSSO B.V.
"""
from ..http import HTTPError


class Autorefresh(object):
    def rest(self, request):
        try:
            decoded = super(Autorefresh, self).rest(request)
        except HTTPError as e:
            if e.code != 401:
                raise

            # Refresh token.
            self.refresh_token()

            # Retry.
            decoded = super(Autorefresh, self).rest(request)

        return decoded
