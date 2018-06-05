# -*- coding: utf-8 -*-

from gluon import *


class ShopProductsVariant:
    def __init__(self, shop_products_variants_id):
        db = current.globalenv['db']

        self.id = shop_products_variants_id
        self.row = db.shop_products_variants(self.id)


    def set_default(self):
        """
            Set this product variant as default for a product
        """
        db = current.globalenv['db']

        query = (db.shop_products_variants.shop_products_id ==
                 self.row.shop_products_id)
        db(query).update(DefaultVariant=False)

        self.row.DefaultVariant = True
        self.row.update_record()


    def disable(self):
        """
            Disable variant
        """
        self.row.Enabled = False
        self.row.update_record()


    def enable(self):
        """
            Enable variant
        """
        self.row.Enabled = True
        self.row.update_record()

