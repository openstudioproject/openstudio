# -*- coding: utf-8 -*-

from gluon import *

class OSSAULA:
    def update_login_attempts(self, form):
        """
        Store the number of failed login attempts in cache
        :param form:
        :return:
        """
        cache = current.cache

        failed_attempts_cache_key = "auth_login_failed_attempts_%s" % request.vars.email
        print failed_attempts_cache_key
        print "failed attempts"

        failed_attempts = cache.ram(failed_attempts_cache_key, lambda: 0, time_expire=1800)
        print failed_attempts
        cache.ram.clear(regex=failed_attempts_cache_key)

        failed_attempts = cache.ram(failed_attempts_cache_key, lambda: failed_attempts + 1, time_expire=1800)
        print failed_attempts


    def login_check_lockout(self, form):
        """
        Lockout validation to be performed before any database IO.
        Lockout by redirecting to lockout page before
        :param form:
        :return:
        """
        cache = current.cache

        allowed_attempts = 7
        email = form.vars.email
        failed_attempts_cache_key = "auth_login_failed_attempts_%s" % email

        failed_attempts = cache.ram(failed_attempts_cache_key, lambda: 0, time_expire=1800)

        if failed_attempts >= allowed_attempts:
            redirect(URL('default', 'user_lockout'))
        elif failed_attempts == allowed_attempts - 1:
            auth.messages.invalid_login = \
                T('You have one more login attempt before you are locked out for 30 minutes')
        elif failed_attempts == allowed_attempts - 2:
            auth.messages.invalid_login = \
                T('You have two more login attempts before you are locked out for 30 minutes')
        elif failed_attempts == allowed_attempts - 3:
            auth.messages.invalid_login = \
                T('You have three more login attempts before you are locked out for 30 minutes')


    def login_reset_failed_attempts(self, form):
        """
        Reset failed login attempts count after successful login, before redirection
        :param form:
        :return:
        """
        from openstudio.os_cache_manager import OsCacheManager
        email = form.vars.email
        ocm = OsCacheManager()
        ocm.clear_auth_user_login_attempts(email)
