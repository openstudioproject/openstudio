# -*- coding: utf-8 -*-

from gluon import *


class ShopSales:
    def list(self):
        """
            :return: List of shop products (gluon.dal.rows)
        """
        db = current.db

        left = [
            db.shop_sales_products_variants.on(
                db.shop_sales_products_variants.shop_sales_id ==
                db.shop_sales.id
            ),
            db.shop_products_variants.on(
                db.shop_sales_products_variants.shop_products_variants_id ==
                db.shop_products_variants.id
            ),
            db.receipts_shop_sales.on(
                db.receipts_shop_sales.shop_sales_id ==
                db.shop_sales.id
            )
        ]

        rows = db(db.shop_sales).select(db.shop_sales.ALL,
                                        db.shop_products_variants.ALL,
                                        db.receipts_shop_sales.receipts_id,
                                        orderby=db.shop_sales.CreatedOn)

        return rows


    def list_formatted(self):
        """
            :return: HTML table with shop products
        """
        db = current.db
        T = current.T
        grid_ui = current.globalenv['grid_ui']
        auth = current.auth

        left = [
            db.shop_sales_products_variants.on(
                db.shop_sales_products_variants.shop_sales_id ==
                db.shop_sales.id
            ),
            db.shop_products_variants.on(
                db.shop_sales_products_variants.shop_products_variants_id ==
                db.shop_products_variants.id
            ),
            db.receipts_shop_sales.on(
                db.receipts_shop_sales.shop_sales_id ==
                db.shop_sales.id
            )
        ]

        db.shop_sales.id.readable = False
        fields = [
            db.shop_sales.CreatedOn,
            db.shop_sales.ProductName,
            db.shop_sales.VariantName,
            db.shop_sales.Quantity,
            db.shop_sales.ArticleCode,
            db.shop_sales.Barcode,
            db.receipts_shop_sales.receipts_id,
            db.shop_sales_products_variants.shop_products_variants_id,
            db.shop_products_variants.shop_products_id,
        ]
        links = [
            dict(header=T("Receipt"),
                 body=self._list_formatted_link_receipt),
            dict(header=T("Product"),
                 body=self._list_formatted_link_product_variant),
        ]
        query = (db.shop_sales.id > 0)
        grid = SQLFORM.grid(
            query,
            left=left,
            fields=fields,
            links=links,
            create=False,
            editable=False,
            deletable=False,
            details=False,
            searchable=False,
            csv=False,
            orderby=db.shop_sales.CreatedOn,
            field_id=db.shop_sales.id,
            ui=grid_ui
        )
        grid.element('.web2py_counter', replace=None)  # remove the counter
        grid.elements('span[title=Delete]', replace=None)  # remove text from delete button

        return grid


    def _list_formatted_link_product_variant(self, row):
        """
        Show link to receipt, if any
        :param row:
        :return:
        """
        T = current.T

        link = ''
        spID = row.shop_products_variants.shop_products_id
        spvID = row.shop_sales_products_variants.shop_products_variants_id
        if spvID:
            link = A(T("View"),
                     _href=URL('shop_manage', 'product_variant_edit',
                               vars={'spID': spID,
                                     'spvID': spvID}))

        return link


    def _list_formatted_link_receipt(self, row):
        """
        Show link to receipt, if any
        :param row:
        :return:
        """
        T = current.T

        link = ''
        rID = row.receipts_shop_sales.receipts_id
        if rID:
            link = A(T("Receipt %s" % rID),
                     _href=URL('finance', 'receipt', vars={'rID':rID}),
                     _target="_blank")

        return link
