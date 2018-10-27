# vim: set ts=8 sw=4 sts=4 et ai tw=79:
"""
Base API interface.

This file is part of the Exact Online REST API Library in Python
(EORALP), licensed under the LGPLv3+.
Copyright (C) 2015-2017 Walter Doekes, OSSO B.V.
"""
import json

from time import time

from .http import (
    Options, opt_secure, http_delete, http_get, http_post, http_put,
    binquote, urljoin)


def _json_safe(data):
    """
    json.loads wants an unistr in Python3. Convert it.
    """
    if not hasattr(data, 'encode'):
        try:
            data = data.decode('utf-8')
        except UnicodeDecodeError:
            raise ValueError(
                'Expected valid UTF8 for JSON data, got %r' % (data,))
    return data


class ExactRawApi(object):
    def __init__(self, storage, **kwargs):
        super(ExactRawApi, self).__init__(**kwargs)
        self.storage = storage

    def create_auth_request_url(self):
        # Build the URLs manually so we get consistent order.
        auth_params = {
            'client_id': binquote(self.storage.get_client_id()),
            'redirect_uri': binquote(self.storage.get_response_url()),
            'response_type': 'code',  # or 'token' for JS apps
        }
        auth_data = ('client_id=%(client_id)s'
                     '&redirect_uri=%(redirect_uri)s'
                     '&response_type=%(response_type)s' %
                     auth_params)

        url = '?'.join([self.storage.get_auth_url(), auth_data])
        return url

    def request_token(self, code):
        # Build the URLs manually so we get consistent order.
        token_params = {
            'client_id': binquote(self.storage.get_client_id()),
            'client_secret': binquote(self.storage.get_client_secret()),
            'code': binquote(code),
            'grant_type': 'authorization_code',
            'redirect_uri': binquote(self.storage.get_response_url()),
        }
        token_data = ('client_id=%(client_id)s'
                      '&client_secret=%(client_secret)s'
                      '&code=%(code)s'
                      '&grant_type=%(grant_type)s'
                      '&redirect_uri=%(redirect_uri)s' %
                      token_params)

        # Fire away!
        url = self.storage.get_token_url()
        response = _json_safe(http_post(url, token_data, opt=opt_secure))

        # Validate and store the values.
        self._set_tokens(response)
        # Store the code first after _set_tokens() has validated the
        # data. We don't want to store some bogus code fed to use by Joe
        # Random user.
        self.storage.set_code(code)

    def refresh_token(self):
        # Bring on the fresh stuff!
        # Build the URLs manually so we get consistent order.
        refresh_params = {
            'client_id': binquote(self.storage.get_client_id()),
            'client_secret': binquote(self.storage.get_client_secret()),
            'grant_type': 'refresh_token',
            'refresh_token': binquote(self.storage.get_refresh_token()),
        }
        refresh_data = ('client_id=%(client_id)s'
                        '&client_secret=%(client_secret)s'
                        '&grant_type=%(grant_type)s'
                        '&refresh_token=%(refresh_token)s' %
                        refresh_params)

        # Fire away!
        url = self.storage.get_refresh_url()
        response = _json_safe(http_post(url, refresh_data, opt=opt_secure))

        # Validate and store the values.
        self._set_tokens(response)

    # Don't pass "/api" in the resource, it's in the base URL already!
    # And don't start with a slash either, since we use urljoin on it.
    #
    # See this for a list of possible resources.
    # https://start.exactonline.co.uk/docs/HlpRestAPIResources.aspx?SourceAction=10
    def rest(self, request):
        url = urljoin(
            self.storage.get_rest_url().rstrip('/') + '/', request.resource)

        # Convert data to json.
        if request.data is None:
            data = None
        elif isinstance(request.data, str):
            data = request.data
        else:
            data = json.dumps(request.data)

        new_request = request.update(resource=url, data=data)
        response = self._rest_query(new_request)

        if request.method in ('DELETE', 'PUT'):
            if response != '':
                raise ValueError(
                    'Expected empty data for %s operation: '
                    'resource=%r, returned=%r' % (
                        request.method, request.resource, response))
            decoded = None
        else:
            try:
                decoded = json.loads(response)
            except ValueError:
                raise ValueError(
                    'Expected valid JSON data for %s operation: '
                    'resource=%r, returned=%r' % (
                        request.method, request.resource, response))

        return decoded

    def _rest_query(self, request):
        token = self.storage.get_access_token()
        opt_custom = Options()
        opt_custom.headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer %s' % (token,),
        }
        if request.method in ('POST', 'PUT'):
            opt_custom.headers.update({'Content-Type': 'application/json'})
        opt = (opt_secure | opt_custom)

        if request.method == 'DELETE':
            assert request.data is None
            response = http_delete(request.resource, opt=opt)
        elif request.method == 'GET':
            assert request.data is None
            response = http_get(request.resource, opt=opt)
        elif request.method == 'POST':
            response = http_post(request.resource, request.data, opt=opt)
        elif request.method == 'PUT':
            response = http_put(request.resource, request.data, opt=opt)
        else:
            raise NotImplementedError(
                'No REST handler for request.method %s' % (
                    request.method,))

        return _json_safe(response)

    def _set_tokens(self, jsondata):
        # The json should look somewhat like this:
        # {"access_token":"AAEA..",
        #  "token_type":"bearer",
        #  "expires_in":"600",
        #  "refresh_token":"__1P!I.."}
        decoded = json.loads(jsondata)

        # Validate the values.
        assert decoded['access_token']
        expires_in = int(decoded['expires_in'])
        assert expires_in > 0
        assert decoded['refresh_token']
        assert decoded['token_type'] == 'bearer'

        # Store the values.
        self.storage.set_access_expiry(int(time()) + expires_in)
        self.storage.set_access_token(decoded['access_token'])
        self.storage.set_refresh_token(decoded['refresh_token'])
