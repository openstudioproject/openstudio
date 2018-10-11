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
