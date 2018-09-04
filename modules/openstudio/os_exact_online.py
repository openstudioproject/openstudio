# -*- coding: utf-8 -*-

from exactonline.storage import ExactOnlineConfig

from gluon import *

class ExactOnlineStorage(ExactOnlineConfig):
    def get(self, section, option):
        option = self._get_value(section, option)

        if not option:
            raise ValueError('Option not set')

        return option

    def set(self, section, option, value):
        self._set_value(section, option, value)


    def _get_value(self, section, option):
        """

        :param section:
        :param option:
        :return:
        """
        db = current.db

        query = (db.integration_exact_online_storage.ConfigSection == section) & \
                (db.integration_exact_online_storage.ConfigOption == option)
        rows = db(query).select(db.integration_exact_online_storage.ConfigValue)

        value = None
        if rows:
            value = rows.first().ConfigValue

        return value


    def _set_value(self, section, option, value):
        """

        :param section:
        :param option:
        :return:
        """
        db = current.db

        query = (db.integration_exact_online_storage.ConfigSection == section) & \
                (db.integration_exact_online_storage.ConfigOption == option)
        rows = db(query).select(db.integration_exact_online_storage.ALL)

        print rows

        if rows:
            row = rows.first()
            row.ConfigValue = value
            row.update_record()
        else:
            db.integration_exact_online_storage.insert(
                ConfigSection = section,
                ConfigOption = option,
                ConfigValue = value
            )

