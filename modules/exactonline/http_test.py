# vim: set ts=8 sw=4 sts=4 et ai tw=79:
"""
HTTP shortcut tests, taken from osso-djuty.

This file is part of the Exact Online REST API Library in Python
(EORALP), licensed under the LGPLv3+.
Copyright (C) 2015-2016 Walter Doekes, OSSO B.V.

We may want to replace this with something simpler.
"""
import ssl
import sys

from os import environ, path
from unittest import TestCase, skipIf

from .http import (
    BadProtocol, HTTPError, Options,
    binquote,
    http_get, http_post, http_put, http_delete,
    opt_secure__unmodified as opt_secure)

try:
    from urllib import request
except ImportError:  # python2
    import urllib2 as request


class HttpTestServer(object):
    "Super simple builtin HTTP test server."
    def __init__(self, method, code, body=None, use_ssl=False):
        from multiprocessing import Process
        from socket import socket, SHUT_RDWR

        self.SHUT_RDWR = SHUT_RDWR
        self.method = method
        self.code = code
        self.body = body

        self.socket = socket()
        if use_ssl:
            here = path.dirname(__file__)
            self.socket = ssl.wrap_socket(
                self.socket,
                certfile=path.join(here, 'http_testserver.crt'),
                keyfile=path.join(here, 'http_testserver.key'))
        self.socket.bind(('127.0.0.1', 0))
        # We must listen() before starting the subprocess, otherwise
        # the main process may get a connection refused if it's too
        # fast.
        self.socket.listen(0)
        self.port = self.socket.getsockname()[1]

        self.process = Process(target=self.respond)
        self.process.start()
        self.socket.close()  # client is done with it

    def join(self):
        self.process.join()

    def respond(self):
        try:
            peersock, peeraddr = self.socket.accept()
        except ssl.SSLError:
            # Broken connection by peer.
            return

        data = peersock.recv(4096)
        if HttpTestCase.to_str(data).startswith(self.method + ' '):
            if self.body is None:
                # If body is None, pass the indata as outdata.
                body = data
                if str != bytes:
                    body = body.decode('utf-8')
            else:
                body = self.body

            peersock.send(
                ('HTTP/1.0 %s Unused Response Title\r\n'
                 'Content-Type: text/plain; utf-8\r\n'
                 '\r\n%s' % (self.code, body)
                 ).encode('utf-8'))
        else:
            peersock.send(
                ('HTTP/1.0 405 Method Not Implemented\r\n'
                 'Content-Type: text/plain; utf-8\r\n'
                 '\r\nUnexpected stuff'
                 ).encode('utf-8'))
        peersock.shutdown(self.SHUT_RDWR)
        peersock.close()
        self.socket.close()  # server is done with it


class HttpTestCase(TestCase):
    def test_options_or_operator(self):
        a = Options()
        a.protocols = ('ftp',)
        a.cacert_file = 'overwrite_me'
        b = Options()
        b.cacert_file = '/tmp/test.crt'
        c = a | b

        self.assertEqual(c.protocols, ('ftp',))
        self.assertFalse(c.verify_cert)
        self.assertEqual(c.cacert_file, '/tmp/test.crt')

    def test_testserver(self):
        # Ensure that the testserver refuses if the method is bad.
        server = HttpTestServer('FAIL', '555', 'failure')
        self.assertRaises(HTTPError, http_get,
                          'http://127.0.0.1:%d/path' % (server.port,))
        server.join()

    def test_delete(self):
        server = HttpTestServer('DELETE', '200', 'whatever1')
        data = http_delete('http://127.0.0.1:%d/path' % (server.port,))
        server.join()
        self.assertDataEqual(data, 'whatever1')

    def test_get(self):
        server = HttpTestServer('GET', '200', 'whatever2')
        data = http_get('http://127.0.0.1:%d/path' % (server.port,))
        server.join()
        self.assertDataEqual(data, 'whatever2')

    def test_post(self):
        server = HttpTestServer('POST', '200', 'whatever3')
        data = http_post('http://127.0.0.1:%d/path' % (server.port,))
        server.join()
        self.assertDataEqual(data, 'whatever3')

    def test_post_actual_data(self):
        server = HttpTestServer('POST', '200', body=None)  # no body => echo
        indata = 'abc DEF\nghi JKL\n'
        data = http_post(
            'http://127.0.0.1:%d/path' % (server.port,), data=indata)
        server.join()

        data = data.decode('utf-8')
        header, outdata = data.split('\r\n\r\n', 1)
        self.assertEqual(outdata, indata)

    def test_put(self):
        server = HttpTestServer('PUT', '200', 'whatever4')
        data = http_put('http://127.0.0.1:%d/path' % (server.port,))
        server.join()
        self.assertDataEqual(data, 'whatever4')

    def test_502(self):
        server = HttpTestServer('GET', '502', 'eRrOr')
        try:
            http_get('http://127.0.0.1:%d/path' % (server.port,))
        except HTTPError as e:
            self.assertTrue(isinstance(e, request.HTTPError))
            self.assertEqual(e.code, 502)
            self.assertDataEqual(e.response, 'eRrOr')
        else:
            self.assertFalse(True)
        server.join()

    def test_exception_str(self):
        server = HttpTestServer('POST', '503', '{"errno":1}')
        url = 'http://127.0.0.1:%d/path' % (server.port,)
        try:
            http_post(url, data='{"action":1}')
        except HTTPError as e:
            self.assertTrue(isinstance(e, request.HTTPError))
            error_str = str(e)
            self.assertIn('503', error_str)
            self.assertIn(url, error_str)
            self.assertIn('{"action":1}', error_str)
            self.assertIn('{"errno":1}', error_str)
        else:
            self.assertFalse(True)
        server.join()

    def test_https_only_through_options(self):
        self.assertRaises(BadProtocol, http_get,
                          'http://127.0.0.1/path', opt=opt_secure)
        self.assertRaises(BadProtocol, http_get,
                          'ftp://127.0.0.1/path', opt=opt_secure)

    @skipIf(sys.version_info >= (2, 7, 9),
            'PEP-0476: Since Python 2.7.9, certificate verification is always '
            'enabled.')
    def test_https_no_secure(self):
        server = HttpTestServer('GET', '200', 'ssl', use_ssl=True)
        data = http_get('https://127.0.0.1:%d/path' % (server.port,))
        server.join()
        self.assertDataEqual(data, 'ssl')

    @skipIf(environ.get('NO_EXTERNAL_REQUESTS', '') not in ('', '0'),
            'Calls external services. Do not run automatically.')
    def test_https_with_real_secure(self):
        # This should work with a proper certificate.
        data = http_get('https://api.github.com/', opt=opt_secure)
        self.assertEqual(HttpTestCase.to_str(data)[0:1], '{')  # json :)

    def test_https_with_self_signed(self):
        # This should fail, because the testserver uses a self-signed
        # certificate.
        server = HttpTestServer('GET', '200', 'ssl', use_ssl=True)
        self.assertRaises(request.URLError, http_get,
                          'https://127.0.0.1:%d/path' % (server.port,),
                          opt=opt_secure)
        server.join()

    def test_https_with_allowed_self_signed(self):
        my_opt = Options()
        my_opt.cacert_file = path.join(
            path.dirname(__file__), 'http_testserver.crt')
        my_opt = opt_secure | my_opt
        server = HttpTestServer('GET', '200', 'ssl2', use_ssl=True)
        data = http_get('https://127.0.0.1:%d/path' % (server.port,),
                        opt=my_opt)
        server.join()
        self.assertDataEqual(data, 'ssl2')

    @skipIf(environ.get('NO_EXTERNAL_REQUESTS', '') not in ('', '0'),
            'Calls external services. Do not run automatically.')
    def test_https_with_disallowed_real_secure(self):
        # This should fail because we use a custom cacert file which won't
        # contain the real cert.
        my_opt = Options()
        my_opt.cacert_file = path.join(
            path.dirname(__file__), 'http_testserver.crt')
        my_opt = opt_secure | my_opt
        self.assertRaises(request.URLError, http_get,
                          'https://api.github.com/', opt=my_opt)

    # ; Python23 compatibility helpers

    try:
        unicode  # python2
    except NameError:
        to_str = staticmethod(lambda x: x.decode('utf-8'))  # binstr-to-unistr
    else:
        to_str = staticmethod(lambda x: x)  # binstr-to-binstr

    def assertDataEqual(self, data, unistr):
        """
        Compares http_* returned data with a plain string. That plain string
        can be unicode (python3) or binstring (python2). The data is always a
        binstring.
        """
        unistr_passed = self.to_str(data)
        self.assertEqual(unistr_passed, unistr)


class UtilTestCase(TestCase):
    def test_binquote(self):
        self.assertEqual(binquote('abc'), 'abc')
        self.assertEqual(binquote('abc/def'), 'abc/def')  # don't touch /
        self.assertEqual(binquote('abc=def'), 'abc%3Ddef')  # do touch =
