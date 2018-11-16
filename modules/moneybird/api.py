from __future__ import absolute_import
import logging
from urlparse import urljoin

import requests

from moneybird.authentication import Authentication

VERSION = u'0.1.3'

logger = logging.getLogger(u'moneybird')


class MoneyBird(object):
    u"""
    Client for the MoneyBird API.

    :param authentication: The authentication method to use.
    """
    version = u'v2'
    base_url = u'https://moneybird.com/api/'

    def __init__(self, authentication):
        self.authentication = authentication
        self.session = None
        self.renew_session()

    def get(self, resource_path, administration_id = None):
        u"""
        Performs a GET request to the endpoint identified by the resource path.

        Example:
            >>> from moneybird import MoneyBird, TokenAuthentication
            >>> moneybird = MoneyBird(TokenAuthentication('access_token'))
            >>> moneybird.get('administrations')
            [{'id': 123, 'name': 'Parkietje B.V.', 'language': 'nl', ...
            >>> moneybird.get('contacts/synchronization', 123)
            [{'id': '143273868766741508', 'version': 1450856630}, ...

        :param resource_path: The resource path.
        :param administration_id: The administration id (optional, depending on the resource path).
        :return: The decoded JSON response for the request.
        """
        response = self.session.get(
            url=self._get_url(administration_id, resource_path),
        )
        return self._process_response(response)

    def post(self, resource_path, data, administration_id = None):
        u"""
        Performs a POST request to the endpoint identified by the resource path. POST requests are usually used to add
        new data.

        Example:
            >>> from moneybird import MoneyBird, TokenAuthentication
            >>> moneybird = MoneyBird(TokenAuthentication('access_token'))
            >>> data = {'url': 'http://www.mocky.io/v2/5185415ba171ea3a00704eed'}
            >>> moneybird.post('webhooks', data, 123)
            {'id': '143274315994891267', 'url': 'http://www.mocky.io/v2/5185415ba171ea3a00704eed', ...

        :param resource_path: The resource path.
        :param data: The data to send to the server.
        :param administration_id: The administration id (optional, depending on the resource path).
        :return: The decoded JSON response for the request.
        """
        response = self.session.post(
            url=self._get_url(administration_id, resource_path),
            json=data,
        )
        return self._process_response(response)

    def patch(self, resource_path, data, administration_id = None):
        u"""
        Performs a PATCH request to the endpoint identified by the resource path. PATCH requests are usually used to
        change existing data.

        From a client perspective, PATCH requests behave similarly to POST requests.

        :param resource_path: The resource path.
        :param data: The data to send to the server.
        :param administration_id: The administration id (optional, depending on the resource path).
        :return: The decoded JSON response for the request.
        """
        response = self.session.patch(
            url=self._get_url(administration_id, resource_path),
            json=data,
        )
        return self._process_response(response)

    def delete(self, resource_path, administration_id = None):
        u"""
        Performs a DELETE request to the endpoint identified by the resource path. DELETE requests are usually used to
        (permanently) delete existing data. USE THIS METHOD WITH CAUTION.

        From a client perspective, DELETE requests behave similarly to GET requests.

        :param resource_path: The resource path.
        :param administration_id: The administration id (optional, depending on the resource path).
        :return: The decoded JSON response for the request.
        """
        response = self.session.delete(
            url=self._get_url(administration_id, resource_path),
        )
        return self._process_response(response)

    def renew_session(self):
        u"""
        Clears all session data and starts a new session using the same settings as before.

        This method can be used to clear session data, e.g., cookies. Future requests will use a new session initiated
        with the same settings and authentication method.
        """
        logger.debug(u"API session renewed")
        self.session = self.authentication.get_session()
        self.session.headers.update({
            u'User-Agent': u'MoneyBird for Python %s' % VERSION,
            u'Accept': u'application/json',
        })

    @classmethod
    def _get_url(cls, administration_id, resource_path):
        u"""
        Builds the URL to the API endpoint specified by the given parameters.

        :param administration_id: The ID of the administration (may be None).
        :param resource_path: The path to the resource.
        :return: The absolute URL to the endpoint.
        """
        url = urljoin(cls.base_url, u'%s/' % cls.version)

        if administration_id is not None:
            url = urljoin(url, u'%s/' % administration_id)

        url = urljoin(url, u'%s.json' % resource_path)

        return url

    @staticmethod
    def _process_response(response, expected = []):
        u"""
        Processes an API response. Raises an exception when appropriate.

        The exception that will be raised is MoneyBird.APIError. This exception is subclassed so implementing programs
        can easily react appropriately to different exceptions.

        The following subclasses of MoneyBird.APIError are likely to be raised:
          - MoneyBird.Unauthorized: No access to the resource or invalid authentication
          - MoneyBird.Throttled: Access (temporarily) denied, please try again
          - MoneyBird.NotFound: Resource not found, check resource path
          - MoneyBird.InvalidData: Validation errors occured while processing your input
          - MoneyBird.ServerError: Error on the server

        :param response: The response to process.
        :param expected: A list of expected status codes which won't raise an exception.
        :return: The useful data in the response (may be None).
        """
        responses = {
            200: None,
            201: None,
            204: None,
            400: MoneyBird.Unauthorized,
            401: MoneyBird.Unauthorized,
            403: MoneyBird.Throttled,
            404: MoneyBird.NotFound,
            406: MoneyBird.NotFound,
            422: MoneyBird.InvalidData,
            429: MoneyBird.Throttled,
            500: MoneyBird.ServerError,
        }

        logger.debug(u"API request: %s %s\n" % (response.request.method, response.request.url) +
                     u"Response: %s %s" % (response.status_code, response.text))

        if response.status_code not in expected:
            if response.status_code not in responses:
                logger.error(u"API response contained unknown status code")
                raise MoneyBird.APIError(response, u"API response contained unknown status code")
            elif responses[response.status_code] is not None:
                try:
                    description = response.json()[u'error']
                except (AttributeError, TypeError, KeyError, ValueError):
                    description = None
                raise responses[response.status_code](response, description)

        try:
            data = response.json()
        except ValueError:
            logger.error(u"API response is not JSON decodable")
            data = None

        return data

    class APIError(Exception):
        u"""
        Exception for cases where communication with the API went wrong.

        This exception is specialized into a number of exceptions with the exact same properties.
        """
        def __init__(self, response, description = None):
            u"""
            :param response: The API response.
            :param description: Description of the error.
            """
            self._response = response

            msg = u'API error %d' % response.status_code
            if description:
                msg += u': %s' % description
            super(MoneyBird.APIError, self).__init__(msg)

        @property
        def status_code(self):
            u"""
            HTTP status code of the request.
            """
            return self._response.status_code

        @property
        def response(self):
            u"""
            JSON encoded data of the response.
            """
            return self._response.json()

        @property
        def request(self):
            u"""
            Short string representation of the request (method and URL).
            """
            return u'%s %s' % (self._response.request.method, self._response.request.url)

    class Unauthorized(APIError):
        pass

    class NotFound(APIError):
        pass

    class InvalidData(APIError):
        pass

    class Throttled(APIError):
        pass

    class ServerError(APIError):
        pass
