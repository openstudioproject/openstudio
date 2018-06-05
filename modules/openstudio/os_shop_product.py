# -*- coding: utf-8 -*-

from gluon import *


class ShopProduct:
    def __init__(self, spID):
        """
            :param spID: db.shop_products.id
        """
        db = current.globalenv['db']

        self.id = spID
        self.row = db.shop_products(self.id)


    def count_variants(self):
        """
            :return: integer - number of variants for this product
        """
        db = current.globalenv['db']
        query = (db.shop_products_variants.shop_products_id == self.id)

        return db(query).count()


    def add_default_variant(self):
        """
            Create default variant for a product without a product set
            :return: None
        """
        T = current.globalenv['T']
        db = current.globalenv['db']

        db.shop_products_variants.insert(
            Enabled=True,
            shop_products_id = self.id,
            Name = T('Default'),
            DefaultVariant = True
        )


    def has_products_set(self):
        """
        :return: boolean
        """
        return True if self.row.shop_products_sets_id else False
    