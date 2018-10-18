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


    def list_formatted(self):
        """
            :return: HTML table with shop products
        """
        from os_shop_categories import ShopCategories

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

        shop_categories = ShopCategories()
        product_categories = shop_categories.list_products_categories()

        rows = self.list()
        for i, row in enumerate(rows):
            repr_row = list(rows[i:i + 1].render())[0]
            buttons = DIV(_class='pull-right')
            vars = {'spID':row.id}

            product_categories = SPAN()
            for category in categories:
                if category.shop_categories_products.shop_products_id == row.id:
                    product_categories.append(
                        os_gui.get_label('info', category.shop_categories.Name)
                    )
                    product_categories.append(' ')

            delete = ''
            if permission_delete:
                delete = os_gui.get_button(
                    'delete_notext',
                    URL('shop_manage', 'product_delete', vars=vars),
                    onclick=onclick_delete,
                    _class='pull-right'
                )

            actions = self._list_formatted_get_actions(
                   permission_edit,
                   permission_variants,
                   row,
                   os_gui,
                   T
            )

            tr = TR(
                TD(repr_row.thumbsmall),
                TD(os_gui.max_string_length(row.Name, 30)),
                TD(os_gui.max_string_length(row.Description, 30)),
                TD(product_categories),
                TD(delete, actions)
            )

            table.append(tr)

        return table


    def _list_formatted_get_actions(self,
                                    permission_edit,
                                    permission_variants,
                                    row,
                                    os_gui,
                                    T):
        """
            Return actions drop down
        """
        links = []

        vars = {'spID': row.id}

        if permission_variants:
            links.append(
                A(os_gui.get_fa_icon('fa-list'), T('Variants'),
                  _href=URL('shop_manage', 'product_variants',
                            vars=vars))
            )
        if permission_edit:
            links.append(
                A(os_gui.get_fa_icon('fa-pencil'), T('Edit'),
                  _href=URL('shop_manage', 'product_edit',
                            vars=vars))
            )

        # set_default = ''
        # if not row.DefaultVariant:
        #     set_default = A(os_gui.get_fa_icon('fa-check-circle'),
        #                     T('Set default'),
        #                     _href=URL('shop_manage', 'product_variant_set_default',
        #                               vars=vars))

        dd = os_gui.get_dropdown_menu(
            links=links,
            btn_text=T('Actions'),
            btn_size='btn-sm',
            btn_icon='actions',
            menu_class='btn-group pull-right')

        return dd
