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





        ]
        # links = [lambda row: os_gui.get_button('edit',
        #                                        URL('classtype_edit', args=[row.id]),
        #                                        T("Edit the name of this classtype")),
        #          classtypes_get_link_archive]
        # maxtextlengths = {'school_classtypes.Name': 50,
        #                   'school_classtypes.Link': 120,
        #                   'school_classtypes.Description': 60}
        query = (db.shop_sales.id > 0)
        grid = SQLFORM.grid(
            query,
            left=left,
            # maxtextlengths=maxtextlengths,
            fields=fields,
            # links=links,
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

