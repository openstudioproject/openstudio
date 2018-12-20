# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------
# This scaffolding model makes your app work on Google App Engine too
# File is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

#print request.global_settings.web2py_version
#if request.global_settings.web2py_version < "2.14.1":
#    raise HTTP(500, "Requires web2py 2.13.3 or newer")

# -------------------------------------------------------------------------
# Imports for testing
# -------------------------------------------------------------------------
from web2pytest import web2pytest
import os
import datetime


# -------------------------------------------------------------------------
# if SSL/HTTPS is properly configured and you want all HTTP requests to
# be redirected to HTTPS, uncomment the line below:
# -------------------------------------------------------------------------
# request.requires_https()

if not request.env.web2py_runtime_gae:
    # ---------------------------------------------------------------------
    # if NOT running on Google App Engine use SQLite or other DB
    # ---------------------------------------------------------------------
    ## if NOT running on Google App Engine use SQLite or other DB
    if web2pytest.is_running_under_test(request, request.application):
        # When running under test, db cannot be ':memory:'
        # because it is recreated in each request and a webclient test
        # can make many requests to validate a single scenario.
        db = DAL('sqlite://%s.sqlite' % request.application,
                folder=os.path.dirname(web2pytest.testfile_name()),
                pool_size=1,
                check_reserved=['all'],
                lazy_tables=False)
    else:
        db = DAL(myconf.get('db.uri'),
                 pool_size=myconf.get('db.pool_size'),
                 migrate_enabled=myconf.get('db.migrate'),
                 check_reserved=['all'],
                 db_codec=myconf.get('db.db_codec'),
                 bigint_id=myconf.get('db.bigint_id'),
                 lazy_tables=myconf.get('db.lazy_tables'),
                 fake_migrate_all=myconf.get('db.fake_migrate_all'),
                 )
else:
    # ---------------------------------------------------------------------
    # connect to Google BigTable (optional 'google:datastore://namespace')
    # ---------------------------------------------------------------------
    db = DAL('google:datastore+ndb')
    # ---------------------------------------------------------------------
    # store sessions and tickets there
    # ---------------------------------------------------------------------
    session.connect(request, response, db=db)
    # ---------------------------------------------------------------------
    # or store session in Memcache, Redis, etc.
    # from gluon.contrib.memdb import MEMDB
    # from google.appengine.api.memcache import Client
    # session.connect(request, response, db = MEMDB(Client()))
    # ---------------------------------------------------------------------

if myconf.get('cache.cache') == 'redis':
    # If we have redis in the stack, let's use it for sessions
    from gluon.contrib.redis_utils import RConn
    from gluon.contrib.redis_session import RedisSession

    redis_host = str(myconf.get('cache.redis_host'))
    redis_port = str(myconf.get('cache.redis_port'))
    rconn = RConn(redis_host, redis_port)
    sessiondb = RedisSession(redis_conn=rconn, session_expiry=False)
    session.connect(request, response, db = sessiondb)

# -------------------------------------------------------------------------
# by default give a view/generic.extension to all actions from localhost
# none otherwise. a pattern can be 'controller/function.extension'
# -------------------------------------------------------------------------
response.generic_patterns = ['*.json', '*.xml', '*.load', '*.html']
# -------------------------------------------------------------------------
# choose a style for forms
# -------------------------------------------------------------------------
response.formstyle = myconf.get('forms.formstyle')  # or 'bootstrap3_stacked' or 'bootstrap2' or other
response.form_label_separator = myconf.get('forms.separator') or ''

# -------------------------------------------------------------------------
# (optional) optimize handling of static files
# -------------------------------------------------------------------------
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

# -------------------------------------------------------------------------
# (optional) static assets folder versioning
# -------------------------------------------------------------------------
# response.static_version = '0.0.0'

# -------------------------------------------------------------------------
# Here is sample code if you need for
# - email capabilities
# - authentication (registration, login, logout, ... )
# - authorization (role based authorization)
# - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
# - old style crud actions
# (more options discussed in gluon/tools.py)
# -------------------------------------------------------------------------

from gluon.tools import Auth, Crud, Service, PluginManager

# host names must be a list of allowed host names (glob syntax allowed)
auth = Auth(db, host_names=myconf.get('host.names'))
service = Service()
plugins = PluginManager()
crud = Crud(db)

# -------------------------------------------------------------------------
# Turn of record change detection globally to allow saving a form multiple times
crud.settings.detect_record_change = False
crud.settings.label_separator = ' '
crud.settings.update_deletable = False
crud.settings.auth = auth
crud.messages.record_created = T('Saved')
crud.messages.record_updated = T('Saved')
crud.messages.submit_button = T('Save')
# -------------------------------------------------------------------------

# -------------------------------------------------------------------------
# create all tables needed by auth if not custom tables
# -------------------------------------------------------------------------
# auth.define_tables(username=False, signature=False)

# -------------------------------------------------------------------------
# configure email
# -------------------------------------------------------------------------
mail = auth.settings.mailer
#mail.settings.server = 'logging' if request.is_local else myconf.get('smtp.server')

mail.settings.server = myconf.get('smtp.server')
mail.settings.sender = myconf.get('smtp.sender')
if myconf.get('smtp.login'):
    mail.settings.login = myconf.get('smtp.login')
mail.settings.tls = myconf.get('smtp.tls') or False
mail.settings.ssl = myconf.get('smtp.ssl') or False

if web2pytest.is_running_under_test(request, request.application):
    mail.settings.server = 'logging'

# -------------------------------------------------------------------------
# configure auth policy
# -------------------------------------------------------------------------
# Log failed login attempts
from openstudio_sec.oss_auth_user_login_attempts import OSSAULA
ossaula = OSSAULA()


auth.settings.login_onfail.append(ossaula.update_login_attempts)
auth.settings.login_onvalidation = [ossaula.login_check_lockout]
auth.settings.login_onaccept = [ossaula.login_reset_failed_attempts]
auth.settings.create_user_groups = None # Don't create groups for individual users
auth.settings.expiration = myconf.get('auth.session_expiration') or 1800
auth.settings.registration_requires_verification = True
auth.settings.login_after_registration = True
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True
auth.settings.reset_password_next = URL('profile', 'index')
auth.settings.password_min_length = 8
auth.settings.logged_url = URL('profile', 'index')
auth.messages.email_sent = T("Email sent. Please check your inbox or your spam folder in case you don't receive a message within 15 minutes")
auth.messages.email_verified = T('Email verified, you can now log in using your email address and the password chosen when registering.')
auth.messages.registration_verifying = T('Please verify your email address by clicking on the link in the verification email.')

# -------------------------------------------------------------------------
# Make some objects accessible in modules through current imported from gluon
# -------------------------------------------------------------------------
from gluon import current
current.db = db
current.auth = auth
current.crud = crud
current.web2pytest = web2pytest
current.CACHE_LONG  = CACHE_LONG


# -------------------------------------------------------------------------
# Define your tables below (or better in another model file) for example
#
# >>> db.define_table('mytable', Field('myfield', 'string'))
#
# Fields can be 'string','text','password','integer','double','boolean'
#       'date','time','datetime','blob','upload', 'reference TABLENAME'
# There is an implicit 'id integer autoincrement' field
# Consult manual for more options, validators, etc.
#
# More API examples for controllers:
#
# >>> db.mytable.insert(myfield='value')
# >>> rows = db(db.mytable.myfield == 'value').select(db.mytable.ALL)
# >>> for row in rows: print row.id, row.myfield
# -------------------------------------------------------------------------

# -------------------------------------------------------------------------
# after defining tables, uncomment below to enable auditing
# -------------------------------------------------------------------------
# auth.enable_record_versioning(db)
