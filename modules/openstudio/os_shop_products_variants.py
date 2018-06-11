# -*- coding: utf-8 -*-

from gluon import *


class ShopProductsVariants:
    def __init__(self, shop_products_id):
        self.shop_products_id = shop_products_id

    def list(self):
        """
            :return: List of shop product variants(gluon.dal.rows)
        """
        db = current.db

        query = (db.shop_products_variants.shop_products_id ==
                 self.shop_products_id)
        rows = db(query).select(db.shop_products_variants.ALL,
                                orderby=db.shop_products_variants.Name)

        return rows


    def list_formatted(self):
        """
            :return: HTML table with shop products variants
        """
        T = current.T
        os_gui = current.globalenv['os_gui']
        auth = current.auth

        product = ShopProduct(self.shop_products_id)

        header = THEAD(TR(TH(),
                          TH(T('Name')),
                          TH(T('Price')),
                          TH(T('Article Code')),
                          TH(T('Keep stock')),
                          TH(T('Stock shop')),
                          TH(T('Stock warehouse')),
                          TD(),
                          TH()))
        table = TABLE(header, _class='table table-striped table-hover')
        table_disabled = TABLE(header, _class='table table-striped table-hover')

        permission_edit = (auth.has_membership(group_id='Admins') or
                           auth.has_permission('update', 'shop_products_variants'))
        permission_delete = (auth.has_membership(group_id='Admins') or
                             auth.has_permission('delete', 'shop_products_variants'))

        onclick_delete = self._list_formatted_get_onclick_delete()

        rows = self.list()
        for i, row in enumerate(rows):
            repr_row = list(rows[i:i + 1].render())[0]

            default = self._list_formatted_get_label_default(T, os_gui, row)
            buttons = self._list_formatted_get_buttons(
                permission_edit,
                permission_delete,
                onclick_delete,
                T,
                os_gui,
                row
            )

            tr = TR(
                TD(repr_row.thumbsmall),
                TD(os_gui.max_string_length(row.Name, 50)),
                TD(repr_row.Price),
                TD(repr_row.ArticleCode),
                TD(repr_row.KeepStock),
                TD(row.StockShop),
                TD(row.StockWarehouse),
                TD(default),
                TD(buttons)
            )

            if row.Enabled:
                table.append(tr)
            else:
                table_disabled.append(tr)

        if product.has_products_set():
            return DIV(table, H4(T('Disabled')), table_disabled)
        else:
            return table


    def _list_formatted_get_label_default(self, T, os_gui, row):
        """

        """
        default = ''
        if row.DefaultVariant:
            default = os_gui.get_label('success', T('Default'))

        return default


    def _list_formatted_get_buttons(self,
                                    permission_edit,
                                    permission_delete,
                                    onclick_delete,
                                    T,
                                    os_gui,
                                    row):
        """
            :return:
        """
        buttons = DIV(_class='pull-right')
        vars = {'spvID': row.id, 'spID': self.shop_products_id}

        if row.Enabled:
            if permission_delete:
                disabled = False if not row.DefaultVariant else True
                delete = os_gui.get_button('delete_notext',
                                           URL('shop_manage', 'product_variant_delete',
                                               vars=vars),
                                           onclick=onclick_delete,
                                           _class='pull-right',
                                           _disabled=disabled)
                buttons.append(delete)

            if permission_edit:
                edit = self._list_formatted_get_buttons_edit(
                    T,
                    os_gui,
                    row,
                    vars
                )
                buttons.append(edit)
        else:
            buttons.append(A(T('Enable'),
                             _href=URL('shop_manage',
                                       'product_variant_enable',
                                       vars=vars)))
        return buttons


    def _list_formatted_get_buttons_edit(self, T, os_gui, row, vars):
        """
            Return edit drop down
        """
        edit = A(os_gui.get_fa_icon('fa-pencil'),
                 T('Edit'),
                 _href=URL('shop_manage', 'product_variant_edit',
                           vars=vars))
        set_default = ''
        if not row.DefaultVariant:
            set_default = A(os_gui.get_fa_icon('fa-check-circle'),
                            T('Set default'),
                            _href=URL('shop_manage', 'product_variant_set_default',
                                      vars=vars))
        links = [
            edit,
            set_default
        ]

        dd = os_gui.get_dropdown_menu(
            links=links,
            btn_text=T('Actions'),
            btn_size='btn-sm',
            btn_icon='actions',
            menu_class='btn-group pull-right')

        return dd


    def _list_formatted_get_onclick_delete(self):
        """
            :return: onclick delete for
        """
        T = current.T
        product = ShopProduct(self.shop_products_id)
        if product.has_products_set():
            delete_message = T('Do you really want to disable this variant?')
        else:
            delete_message = T('Do you really want to delete this variant?')
        onclick_delete = "return confirm('" \
            + delete_message + "');"

        return onclick_delete

