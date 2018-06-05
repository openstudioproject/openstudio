# -*- coding: utf-8 -*-

from gluon import *


class ShopProductsSet:
    def __init__(self, spsID):
        db = current.globalenv['db']
        self.spsID = spsID
        self.row = db.shop_products_sets(self.spsID)


    def options(self):
        """
            :return: list of options for a products set
        """
        db = current.globalenv['db']

        query = (db.shop_products_sets_options.shop_products_sets_id ==
                 self.spsID)
        return db(query).select(db.shop_products_sets_options.ALL,
                                orderby=db.shop_products_sets_options.Name)


    def get_option_names(self):
        """
            :return: dict mapping ids to option names
        """
        options = self.options()
        names = {}
        for option in options:
            names[option.id] = option.Name

        return names


    def options_with_values(self):
        """
            :return: list of options with values for a products set
        """
        db = current.globalenv['db']

        options = {}
        for option in self.options():
            query = (db.shop_products_sets_options_values.shop_products_sets_options_id ==
                     option.id)
            rows = db(query).select(db.shop_products_sets_options_values.ALL,
                                    orderby=db.shop_products_sets_options_values.Name)
            values = []
            for row in rows:
                values.append(int(row.id))

            options[option.id] = {
                'name': option.Name,
                'values': values
            }

        return options


    def get_value_names(self):
        """
             :return: dict[db.shop_products_sets_options_values.id] = name
        """
        db = current.globalenv['db']

        option_ids = []
        for option in self.options():
            option_ids.append(option.id)

        query = (db.shop_products_sets_options_values.shop_products_sets_options_id.belongs(option_ids))
        rows = db(query).select(db.shop_products_sets_options_values.id,
                                db.shop_products_sets_options_values.Name)
        value_names = {}
        for row in rows:
            value_names[row.id] = row.Name

        return value_names


    def get_linked_products(self):
        """
        :return: list containing ids of linked products
        """
        db = current.globalenv['db']

        query = (db.shop_products.shop_products_sets_id == self.spsID)
        rows = db(query).select(db.shop_products.id)
        ids = []
        for row in rows:
            ids.append(row.id)

        return ids


    def insert_variants(self, enabled=True):
        """
        insert (missing) variants for all products linked to this set
        :param enabled: boolean
        :return: None
        """
        linked_products = self.get_linked_products()
        for shop_products_id in linked_products:
            self.insert_variants_for_product(shop_products_id,
                                             enabled=enabled)


    def insert_variants_for_product(self, shop_products_id, enabled=True):
        """
        :param shop_products_id: db.shop_products.id
        :param enabled: boolean
        :return: None
        """
        from itertools import product, combinations, permutations

        db = current.globalenv['db']
        options = self.options_with_values()
        value_names = self.get_value_names()

        values = []
        for key in options:
            values.append(options[key]['values'])
        variants = list(product(*values))

        for i, variant in enumerate(variants):
            variant_code = '-'.join(str(value) for value in variant)
            variant_name = ''
            for value in variant:
                option_name = ''
                value_name = value_names.get(value, '')
                for key in options:
                    if value in options[key]['values']:
                        option_name = options[key]['name']
                        if len(variant_name):
                            variant_name += ', '
                        variant_name += option_name + ': ' + value_name
                        break

            query = (db.shop_products_variants.VariantCode == variant_code) & \
                    (db.shop_products_variants.shop_products_id == shop_products_id)
            count = db(query).count()
            if not count:
                db.shop_products_variants.insert(
                    Enabled=enabled,
                    shop_products_id = shop_products_id,
                    Name = variant_name,
                    DefaultVariant = True if not i else False,
                    VariantCode = variant_code
                )
