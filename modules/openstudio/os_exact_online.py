# -*- coding: utf-8 -*-

from gluon import *


class OSExactOnline:
    def get_api(self):
        """
        Return ExactAPI linked to config and token storage
        """
        import os
        from exactonline.api import ExactApi
        from exactonline.exceptions import ObjectDoesNotExist
        from exactonline.storage import IniStorage

        storage = self.get_storage()

        return ExactApi(storage=storage)


    def get_storage(self):
        """
        Get ini storage
        """
        import os
        from ConfigParser import NoOptionError
        from exactonline.storage import IniStorage

        class MyIniStorage(IniStorage):
            def get_response_url(self):
                "Configure your custom response URL."
                return self.get_base_url() + '/exact_online/oauth2_success/'

        request = current.request

        config_file = os.path.join(
            request.folder,
            'private',
            'eo_config.ini'
        )

        return MyIniStorage(config_file)


    def create_relation(self, os_customer):
        """
        :param os_customer: OsCustomer object
        :return: exact online relation id
        """
        from tools import OsTools

        os_tools = OsTools()
        authorized = os_tools.get_sys_property('exact_online_authorized')

        if not authorized:
            self._log_error(
                'create',
                'relation',
                os_customer.row.id,
                "Exact online integration not authorized"
            )

            return

        else:
            import pprint

            from ConfigParser import NoOptionError
            from openstudio.os_exact_online import OSExactOnline
            from exactonline.http import HTTPError

            storage = self.get_storage()
            api = self.get_api()

            try:
                selected_division = int(storage.get('transient', 'division'))
            except NoOptionError:
                selected_division = None

            print "division:"
            print selected_division

            relation_dict = {
                "Name": os_customer.row.display_name,
                "Code": os_customer.row.id,
                "Division": selected_division,
                "Email": os_customer.row.email,
                "Status": "C" # Customer
            }

            error = False

            try:
                result = api.relations.create(relation_dict)
                rel_id = result['ID']
                print rel_id
                os_customer.row.exact_online_relation_id = rel_id
                os_customer.row.update_record()

            except HTTPError as e:
                error = True
                self._log_error(
                    'create',
                    'relation',
                    os_customer.row.id,
                    e
                )

            if error:
                return False

            return rel_id


    def update_relation(self, os_customer):
        """
        :param os_customer: OsCustomer object
        :return: dict(error=True|False, message='')
        """
        from tools import OsTools

        os_tools = OsTools()
        authorized = os_tools.get_sys_property('exact_online_authorized')

        if not authorized:
            self._log_error(
                'create',
                'relation',
                os_customer.row.id,
                "Exact online integration not authorized"
            )

            return

        print 'update'

        eoID = os_customer.row.exact_online_relation_id

        print eoID
        if not eoID:
            print 'creating relation'
            self.create_relation(os_customer)
            return

        import pprint

        from ConfigParser import NoOptionError
        from openstudio.os_exact_online import OSExactOnline
        from exactonline.http import HTTPError

        os_eo = OSExactOnline()
        storage = os_eo.get_storage()
        api = os_eo.get_api()

        try:
            selected_division = int(storage.get('transient', 'division'))
        except NoOptionError:
            selected_division = None

        print "division:"
        print selected_division

        relation_dict = {
            "Name": os_customer.row.display_name,
            "Code": os_customer.row.id,
            "Email": os_customer.row.email,
            "Status": "C"
        }

        error = False
        message = ''

        print 'update'
        print eoID

        # api.relations.update(eoID, relation_dict)
        try:
            api.relations.update(eoID, relation_dict)
        except HTTPError as e:
            error = True
            message = e

            self._log_error(
                'update',
                'relation',
                os_customer.row.id,
                e
            )


        return dict(error=error, message=message)


    def _log_error(self, action, object, object_id, result):
        """
        :param action: should be in ['create', 'read', 'update', 'delete']
        :param object: object name
        :param object_id: object id
        :param message: string
        :return: None
        """
        db = current.db

        db.integration_exact_online_log.insert(
            ActionName = action,
            ObjectName = object,
            ObjectID = object_id,
            ActionResult = result,
            Status = 'fail'
        )



# class ExactOnlineStorage(ExactOnlineConfig):
#     def get_response_url(self):
#         """Configure your custom response URL."""
#         return self.get_base_url() + '/exact_online/oauth2_success/'
#
#     def get(self, section, option):
#         option = self._get_value(section, option)
#
#         if not option:
#             raise ValueError('Required option is not set')
#
#         return option
#
#     def set(self, section, option, value):
#         self._set_value(section, option, value)
#
#
#     def _get_value(self, section, option):
#         """
#
#         :param section:
#         :param option:
#         :return:
#         """
#         db = current.db
#
#         query = (db.integration_exact_online_storage.ConfigSection == section) & \
#                 (db.integration_exact_online_storage.ConfigOption == option)
#         rows = db(query).select(db.integration_exact_online_storage.ConfigValue)
#
#         value = None
#         if rows:
#             value = rows.first().ConfigValue
#
#         return value
#
#
#     def _set_value(self, section, option, value):
#         """
#
#         :param section:
#         :param option:
#         :return:
#         """
#         db = current.db
#
#         query = (db.integration_exact_online_storage.ConfigSection == section) & \
#                 (db.integration_exact_online_storage.ConfigOption == option)
#         rows = db(query).select(db.integration_exact_online_storage.ALL)
#
#         if rows:
#             row = rows.first()
#             row.ConfigValue = value
#             row.update_record()
#         else:
#             db.integration_exact_online_storage.insert(
#                 ConfigSection = section,
#                 ConfigOption = option,
#                 ConfigValue = value
#             )
#
