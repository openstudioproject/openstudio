# -*- coding: utf-8 -*-

from gluon import *


class ShopCategory:

    def __init__(self, scID):
        """
        Init class
        :param scID: db.shop_categories.id
        """
        db = current.db

        self.id = scID
        self.row = db.shop_categories(self.id)


    def get_products(self):
        """

        :return: All products in this category
        """
        db = current.db


        left = [
            db.shop_products.on(
                db.shop_categories_products.shop_products_id ==
                db.shop_products.id
            )
        ]

        query = (db.shop_categories_products.shop_categories_id == self.id)

        rows = db(query).select(
            db.shop_products.ALL,
            orderby=db.shop_products.Name,
            left=left
        )

        return rows


    def get_products_with_variants(self):
        """

        :return: All products in this category
        """
        from general_helpers import get_download_url

        db = current.db

        products_with_variants = []

        product_rows = self.get_products()

        for product_row in product_rows:
            query = (db.shop_products_variants.shop_products_id == self.id)

            rows = db(query).select(
                db.shop_products_variants.ALL,
                orderby=db.shop_products_variants.Name,
            )

            products_with_variants.append({
                'id': product_row.id,
                'name': product_row.Name,
                'description': product_row.DescriptionShop,
                'picture': product_row.picture,
                'thumbsmall': get_download_url(product_row.thumbsmall),
                'thumblarge': get_download_url(product_row.thumblarge),
                'variants': rows.as_list(),
            })


        return products_with_variants

