# vim: set ts=8 sw=4 sts=4 et ai tw=79:
"""
HTTP shortcuts, taken from osso-djuty.

This file is part of the Exact Online REST API Library in Python
(EORALP), licensed under the LGPLv3+.
Copyright (C) 2015-2016 Walter Doekes, OSSO B.V.

We may want to replace this with something simpler.
"""
import urllib
import socket
import ssl
import sys

try:
    from ssl import create_default_context
except ImportError:  # python2.7.9-
    create_default_context = None
try:
    from http.client import HTTPConnection, HTTPS_PORT
except ImportError:  # python2
    from httplib import HTTPConnection, HTTPS_PORT
try:
    from urllib import request
except ImportError:  # python2
    import urllib2 as request
try:
    from urllib.parse import urljoin, quote
except ImportError:  # python2
    from urllib import quote
    from urlparse import urljoin

# For older Python, use this. For newer Python, use nothing to get
# libssl-selected files instead. You can choose to override this
# by importing exactonline.http and updating this value before calling
# any of the http_* functions (through an exactonline API call).
FALLBACK_CACERT_FILE = '/etc/ssl/certs/ca-certificates.crt'


# ; helpers

def binquote(value):
    """
    We use quote() instead of urlencode() because the Exact Online API
    does not like it when we encode slashes -- in the redirect_uri -- as
    well (which the latter does).
    """
    return quote(value.encode('utf-8'))

urljoin  # touch it, we don't use it


# ; http stuff

class BadProtocol(ValueError):
    """
    Raised when you try to http_get or http_post with a disallowed
    protocol.
    """
    pass


class HTTPError(request.HTTPError):
    """
    Override the original HTTPError, drop the fp and add a response and
    add request method and data.
    """
    def __init__(self, url, code, msg, hdrs, response, reqmethod, reqdata):
        request.HTTPError.__init__(self, url, code, msg, hdrs, None)
        self.url = url
        self.response = response        # in
        self.reqmethod = reqmethod
        self.reqdata = reqdata or ''    # out

    @staticmethod
    def clean_and_trim(value):
        if not isinstance(value, str):
            value = value.decode('utf-8', 'replace')
        value = value[0:1023] + ('', '...')[len(value) > 1023]
        value = ''.join(
            ('?', i)[0x20 <= ord(i) <= 0x7F or i in '\t\n\r'] for i in value)
        return value

    def get_content_type(self):
        try:
            # self.hdrs is a ???
            type_ = str(self.hdrs.type)
        except AttributeError:
            # self.hdrs is a HTTPMessage
            type_ = '|'.join(
                i[1] for i in self.hdrs.items()
                if i[0].lower() == 'content-type')
        return type_

    def format_req(self):
        return '%s %s\nContent-Length: %s\n\n%s' % (
            self.reqmethod, self.url, len(self.reqdata),
            self.clean_and_trim(self.reqdata))

    def format_resp(self):
        return '<RESP> %s %s\nContent-Type: %s\nContent-Length: %s\n\n%s' % (
            self.code, self.msg, self.get_content_type(), len(self.response),
            self.clean_and_trim(self.response))

    def __str__(self):
        return (
            'HTTPError: %(msg)s%(sep)s\n%(out)s%(sep)s\n%(in)s%(sep)s' % {
                'msg': self.msg, 'out': self.format_req(),
                'in': self.format_resp(), 'sep': '\n' + ('-' * 71)})


class Options(object):
    # Which protocols to we allow.
    protocols = ('http', 'https')
    # Do we validate the SSL certificate.
    verify_cert = False
    # What we use to validate the SSL certificate.
    cacert_file = None  # None means "use default or fallback if no default"
    # Optional headers.
    headers = None

    # Which properties we have.
    _PROPERTIES = ('protocols', 'verify_cert', 'cacert_file', 'headers')

    def __or__(self, other):
        """
        Join multiple Options together with the or-operator '|'.
        It uses the identity operator to compare values against the
        default values, so non-overridden values won't overwrite
        overridden ones.

        BUG: This will fail if you try to re-set booleans from False
        to True to False.
        """
        new_options = Options()

        for source in (self, other):
            for item in self._PROPERTIES:
                source_item = getattr(source, item)
                if source_item is not getattr(Options, item):  # identity check
                    setattr(new_options, item, source_item)

        return new_options

# Default options.
opt_default = Options()
opt_default__unmodified = opt_default | Options()  # copy, for testing

# SSL-safe options.
opt_secure = Options()
opt_secure.protocols = ('https',)
opt_secure.verify_cert = True
opt_secure__unmodified = opt_secure | Options()  # copy, for testing


class Request(request.Request):
    """
    Override the request.Request class to supply a custom method.
    """
    def __init__(self, method=None, *args, **kwargs):
        request.Request.__init__(self, *args, **kwargs)
        assert method in ('DELETE', 'GET', 'POST', 'PUT')
        self._method = method

    def get_method(self):
        return self._method


class ValidHTTPSConnection(HTTPConnection):
    """
    This class allows communication via SSL.

    Originally by: Walter Cacau, 2013-01-14
    Source: http://stackoverflow.com/questions/6648952/\
            urllib-and-validation-of-server-certificate
    """
    default_port = HTTPS_PORT
    cacert_file = opt_default.cacert_file

    def __init__(self, *args, **kwargs):
        HTTPConnection.__init__(self, *args, **kwargs)

    def connect(self):
        "Connect to a host on a given (SSL) port."
        sock = socket.create_connection((self.host, self.port),
                                        self.timeout, self.source_address)
        if self._tunnel_host:
            self.sock = sock
            self._tunnel()

        # Python 2.7.9+
        if create_default_context:
            # Newer python will use the "right" cacert file automatically. So
            # the default of None can safely be passed along.
            ctx = create_default_context(cafile=self.cacert_file)
            sock = ctx.wrap_socket(sock, server_hostname=self.host)
        else:
            # Take the supplied file, or FALLBACK_CACERT_FILE if nothing
            # was supplied.
            cacert_file = self.cacert_file or FALLBACK_CACERT_FILE
            sock = ssl.wrap_socket(sock, ca_certs=cacert_file,
                                   cert_reqs=ssl.CERT_REQUIRED)

        self.sock = sock


class ValidHTTPSHandler(request.HTTPSHandler):
    """
    Originally by: Walter Cacau, 2013-01-14
    Source: http://stackoverflow.com/questions/6648952/\
            urllib-and-validation-of-server-certificate
    """
    def __init__(self, cacert_file):
        self.cacert_file = cacert_file
        request.HTTPSHandler.__init__(self)

    def https_open(self, req):
        # If someone uses an alternate cacert_file, we have no decent
        # way of telling that to a subclass (not instance).
        if self.cacert_file == ValidHTTPSConnection.cacert_file:
            class_ = ValidHTTPSConnection
        else:
            # Yuck. Create a local subclass so we can set a custom
            # cacert_file.
            class CustomValidHTTPSConnection(ValidHTTPSConnection):
                cacert_file = self.cacert_file
            class_ = CustomValidHTTPSConnection

        return self.do_open(class_, req)


def http_delete(url, opt=opt_default):
    """
    Shortcut for urlopen (DELETE) + read. We'll probably want to add a
    nice timeout here later too.
    """
    return _http_request(url, method='DELETE', opt=opt)


def http_get(url, opt=opt_default):
    """
    Shortcut for urlopen (GET) + read. We'll probably want to add a nice
    timeout here later too.
    """
    return _http_request(url, method='GET', opt=opt)


def http_post(url, data=None, opt=opt_default):
    """
    Shortcut for urlopen (POST) + read. We'll probably want to add a
    nice timeout here later too.
    """
    return _http_request(url, method='POST', data=_marshalled(data), opt=opt)


def http_put(url, data=None, opt=opt_default):
    """
    Shortcut for urlopen (PUT) + read. We'll probably want to add a nice
    timeout here later too.
    """
    return _http_request(url, method='PUT', data=_marshalled(data), opt=opt)


def _marshalled(data):
    if not data:
        data = ''.encode('utf-8')  # ensure PUT/POST-mode
    elif isinstance(data, type(u'')):
        data = data.encode('utf-8')
    elif isinstance(data, (bytes, str)):
        pass
    else:
        data = urllib.urlencode(data)
    return data


def _http_request(url, method=None, data=None, opt=None):
    # Check protocol.
    proto = url.split(':', 1)[0]
    if proto not in opt.protocols:
        raise BadProtocol('Protocol %s in URL %r disallowed by caller' %
                          (proto, url))

    # Create URL opener.
    if opt.verify_cert:
        # It's legal to pass either a class or an instance here.
        opener = request.build_opener(ValidHTTPSHandler(opt.cacert_file))
    else:
        opener = request.build_opener()

    # Create the Request with optional extra headers.
    req = Request(url=url, data=data, method=method,
                  headers=(opt.headers or {}))

    exc_info, fp, stored_exception = None, None, None
    try:
        fp = opener.open(req)
        # print fp.info()  # (temp, print headers)
        response = fp.read()
    except request.HTTPError as exception:
        fp = exception.fp  # see finally clause
        exc_info = sys.exc_info()
        stored_exception = exception
    except Exception as exception:
        exc_info = sys.exc_info()
        stored_exception = exception
    finally:
        if fp:
            # Try a bit harder to flush the connection and close it
            # properly. In case of errors, our django testserver peer
            # will show an error about us killing the connection
            # prematurely instead of showing the URL that causes the
            # error. Flushing the data here helps.
            if exc_info:
                response = fp.read()
                fp.close()
                # And, even more importantly. Some people want the
                # exception/error info. Store it in our HTTPError
                # subclass.
                raise HTTPError(
                    exc_info[1].url,
                    exc_info[1].code,
                    exc_info[1].msg,
                    exc_info[1].hdrs,
                    response,
                    method or '(none)',
                    data)
            fp.close()

    if exc_info:
        raise stored_exception  # exc_info[0], exc_info[1], exc_info[2]
    return response
