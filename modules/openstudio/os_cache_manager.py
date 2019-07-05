# -*- coding: utf-8 -*-

from gluon import *

class OsCacheManager:
    def clear(self, var_one=None, var_two=None):
        """
            Clears all cache entries on disk & in ram
            # Takes arguments in case it's called from a crud form or SQLFORM.grid
        """
        cache = current.cache

        cache.ram.clear()
        cache.disk.clear()


    def clear_customers(self):
        """

        :return:
        """
        cache = current.cache

        # Pos
        key = "openstudio_pos_get_customers"
        cache.ram.clear(regex=key)


    def clear_auth_user_login_attempts(self, email):
        """
        :param email: email address
        :return:
        """
        cache = current.cache

        failed_attempts_cache_key = "auth_login_failed_attempts_%s" % email
        cache.ram.clear(regex=failed_attempts_cache_key)


    def clear_customers_memberships(self, cuID):
        """
            Clears memberships cache entries on disk & in ram
        """
        cache = current.cache

        cu_sub_regex = 'openstudio_customer_get_memberships_on_date_' + str(cuID) + '*'
        cache.ram.clear(regex=cu_sub_regex)
        cache.disk.clear(regex=cu_sub_regex)


    def clear_customers_subscriptions(self, cuID):
        """
            Clears subscription cache entries on disk & in ram
        """
        cache = current.cache

        cu_sub_regex = 'openstudio_customer_get_subscriptions_on_date_' + str(cuID) + '*'
        cache.ram.clear(regex=cu_sub_regex)
        cache.disk.clear(regex=cu_sub_regex)


    def clear_customers_classcards(self, cuID):
        """
            Clears subscription cache entries on disk & in ram
        """
        cache = current.cache

        cu_cc_regex = 'openstudio_customer_get_classcards_' + str(cuID) + '*'
        cache.ram.clear(regex=cu_cc_regex)
        cache.disk.clear(regex=cu_cc_regex)


    def clear_classschedule(self, var_one=None, var_two=None):
        """
            Clears the class schedule cache
            takes 2 dummy arguments in case it's called from a CRUD form or from SQLFORM.grid
        """
        cache = current.cache

        class_schedule_regex = 'openstudio_classschedule_get_day_*'
        cache.ram.clear(regex=class_schedule_regex)
        cache.disk.clear(regex=class_schedule_regex)

        cache_clear_classschedule_api()


    def clear_classschedule_api(self, var_one=None, var_two=None):
        """
            Clears the class schedule api cache
            takes 2 dummy arguments in case it's called from a CRUD form or from SQLFORM.grid
        """
        cache = current.cache

        api_schedule_regex = 'openstudio_api_schedule_get_*'
        cache.ram.clear(regex=api_schedule_regex)
        cache.disk.clear(regex=api_schedule_regex)


    def clear_classschedule_trend(self, var_one=None, var_two=None):
        """
            Clears the class schedule trend column cache
            takes 2 dummy arguments in case it's called from a CRUD form or from SQLFORM.grid
        """
        cache = current.cache

        trend_regex = 'openstudio_classschedule_trend_*'
        cache.ram.clear(regex=trend_regex)
        cache.disk.clear(regex=trend_regex)


    def clear_sys_properties(self):
        """
            Clears the sys_properties keys in cache
            :return: None
        """
        cache = current.cache

        sprop_regex = 'openstudio_system_property_*'
        cache.ram.clear(regex=sprop_regex)
        cache.disk.clear(regex=sprop_regex)


    def clear_menu_backend(self):
        """
            Clears the backend menu's in cache
        """
        cache = current.cache

        menu_regex = 'openstudio_menu_backend_*'
        cache.ram.clear(regex=menu_regex)
        cache.disk.clear(regex=menu_regex)


    def clear_workshops(self, var_one=None, var_two=None):
        """
            Clears the workshops cache
            # accepts two vars to the function can be called from SQLFORM.grid ondelete or crud functions
        """
        cache = current.cache

        workshops_regex = 'openstudio_workshops_*'
        cache.ram.clear(regex=workshops_regex)
        cache.disk.clear(regex=workshops_regex)


    def clear_school_subscriptions(self, var_one=None, var_two=None):
        """
            Clears the school subscriptions cache
            # accepts two vars to the function can be called from SQLFORM.grid ondelete or crud functions
        """
        cache = current.cache

        school_subscriptions_regex = 'openstudio_school_subcriptions_api_*'
        cache.ram.clear(regex=school_subscriptions_regex)
        cache.disk.clear(regex=school_subscriptions_regex)

        # Clear all customer subscriptions, as the cache also stores some school subscription info
        cu_sub_regex = 'openstudio_customer_get_subscriptions_on_date_*'
        cache.ram.clear(regex=cu_sub_regex)
        cache.disk.clear(regex=cu_sub_regex)


    def clear_school_classcards(self, var_one=None, var_two=None):
        """
            Clears the school classcards cache
            # accepts two vars to the function can be called from SQLFORM.grid ondelete or crud functions
        """
        cache = current.cache

        school_classcards_regex = 'openstudio_school_classcards_api_*'
        cache.ram.clear(regex=school_classcards_regex)
        cache.disk.clear(regex=school_classcards_regex)


    def clear_school_teachers(self, var_one=None, var_two=None):
        """
            Clears the school teachers (API) cache
            # accepts two vars to the function can be called from SQLFORM.grid ondelete or crud functions
        """
        cache = current.cache

        school_teachers_api_regex = 'openstudio_school_teachers_api_get'
        cache.ram.clear(regex=school_teachers_api_regex)
        cache.disk.clear(regex=school_teachers_api_regex)


    def clear_school_classtypes(self, var_one=None, var_two=None):
        """
            Clears the school teachers (API) cache
            # accepts two vars to the function can be called from SQLFORM.grid ondelete or crud functions
        """
        cache = current.cache

        school_teachers_api_regex = 'openstudio_school_teachers_api_get'
        cache.ram.clear(regex=school_teachers_api_regex)
        cache.disk.clear(regex=school_teachers_api_regex)


    def clear_sys_organizations(self, var_one=None, var_two=None):
        """
            Clears the workshops cache
            # accepts two vars to the function can be called from SQLFORM.grid ondelete or crud functions
        """
        cache = current.cache

        sys_org_regex = 'openstudio_sys_organizations*'
        cache.ram.clear(regex=sys_org_regex)
        cache.disk.clear(regex=sys_org_regex)
