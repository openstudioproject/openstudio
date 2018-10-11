# -*- coding: utf-8 -*-

from gluon import *


class ShopProducts:
    def list(self):
        """
            :return: List of shop products (gluon.dal.rows)
        """
        db = current.db

        rows = db(db.shop_products).select(db.shop_products.ALL,
                                           orderby=db.shop_products.Name)

        return rows


    def list_products_categories(self):
        """
        :return:
        """
        db = current.db

        left = [
            db.shop_categories_products.on(
                db.shop_categories_products.shop_categories_id ==
                db.shop_categories.id
            )
        ]

        query = (db.shop_categories.Archived == False)
        rows = db(query).select(
            db.shop_categories_products.ALL,
            left=left,
            orderby=db.shop_categories.Name
        )

        print rows


    def list_formatted(self):
        """
            :return: HTML table with shop products
        """
        T = current.T
        os_gui = current.globalenv['os_gui']
        auth = current.auth

        header = THEAD(TR(TH(),
                          TH(T('Name')),
                          TH(T('Description')),
                          TH(T('Categories')),
                          TH()))
        table = TABLE(header, _class='table table-striped table-hover')


        categories = self.list_products_categories()

        permission_variants = (auth.has_membership(group_id='Admins') or
                               auth.has_permission('read', 'shop_products_variants'))
        permission_edit = (auth.has_membership(group_id='Admins') or
                           auth.has_permission('update', 'shop_products'))
        permission_delete = (auth.has_membership(group_id='Admins') or
                             auth.has_permission('delete', 'shop_products'))

        onclick_delete = "return confirm('" \
            + T('Do you really want to delete this product?') + "');"

        rows = self.list()
        for i, row in enumerate(rows):
            repr_row = list(rows[i:i + 1].render())[0]
            buttons = DIV(_class='pull-right')
            vars = {'spID':row.id}

            if permission_variants:
                variants = os_gui.get_button('noicon',
                    URL('shop_manage', 'product_variants', vars=vars),
                    title=T('Variants'))
                buttons.append(variants)
            if permission_edit:
                edit = os_gui.get_button('edit',
                    URL('shop_manage', 'product_edit', vars=vars))
                buttons.append(edit)
            if permission_delete:
                delete = os_gui.get_button('delete_notext',
                    URL('shop_manage', 'product_delete', vars=vars),
                    onclick=onclick_delete)
                buttons.append(delete)

            tr = TR(
                TD(repr_row.thumbsmall),
                TD(os_gui.max_string_length(row.Name, 30)),
                TD(os_gui.max_string_length(row.Description, 30)),
                TD('categories here'),
                TD(buttons)
            )

            table.append(tr)

        return table
