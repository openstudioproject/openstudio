# vim: set ts=8 sw=4 sts=4 et ai tw=79:
"""
Looks for __next values, and begins to download those documents
automatically; it unpaginates resultsets.

This file is part of the Exact Online REST API Library in Python
(EORALP), licensed under the LGPLv3+.
Copyright (C) 2015-2017 Walter Doekes, OSSO B.V.
"""


class Unwrap(object):
    def rest(self, request):
        iteration = 0
        ret = []

        while request:
            if iteration >= 50:
                raise ValueError(
                    'Iteration %d limit reached! Last resource %r' % (
                        iteration, request.resource))

            decoded = super(Unwrap, self).rest(request)

            # DELETE and PUT methods return None.
            if not decoded:
                assert request.method in ('DELETE', 'PUT'), request.method
                assert iteration == 0, iteration
                return decoded

            # GET/POST methods return a host of different types.
            result_data = decoded.pop(u'd', None)
            if result_data is None or decoded:
                raise ValueError(
                    'Expected *only* "d" in response, got this: '
                    'response=%r, d=%r' % (decoded, result_data))

            # POST methods return a nice dictionary inside of 'd'.
            if request.method == 'POST':
                assert iteration == 0, iteration
                return result_data

            # GET methods...
            assert request.method == 'GET'

            if isinstance(result_data, dict):
                result_data, resource = self._rest_to_result_data_and_next(
                    result_data)
                ret.extend(result_data)

                if resource:
                    request = request.update(resource=resource)  # next request
                else:
                    request = None  # no next

            elif isinstance(result_data, list):
                assert iteration == 0, iteration
                ret = result_data
                request = None  # no next
            else:
                raise ValueError(
                    'Expected *list* or *dict* in "d", got this: d=%r' % (
                        result_data,))

            iteration += 1

        return ret

    def _rest_to_result_data_and_next(self, result_data):
        results = result_data.pop(u'results', None)
        next_ = result_data.pop(u'__next', None)
        if results is None or result_data:
            raise ValueError(
                'Expected *only* "results" in "d", got this: '
                'd=%r, results=%r' % (result_data, results))

        ret = results
        assert isinstance(ret, list)
        return ret, next_  # next_ is None when at the end
