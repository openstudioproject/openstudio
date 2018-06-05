# -*- coding: utf-8 -*-

from gluon import *



class ShopProductsSets:
    def list(self):
        """
            :return: List of shop products_sets (gluon.dal.rows)
        """
        db = current.globalenv['db']

        query = (db.shop_products_sets)
        rows = db(query).select(db.shop_products_sets.ALL,
                                orderby=db.shop_products_sets.Name)

        return rows


    def list_formatted(self):
        """
            :return: HTML table with shop products_sets
        """
        T = current.globalenv['T']
        os_gui = current.globalenv['os_gui']
        auth = current.globalenv['auth']

        header = THEAD(TR(TH(T('Product set')),
                          TH(T('Description')),
                          TH()))
        table = TABLE(header, _class='table table-striped table-hover')

        permission_options = (auth.has_membership(group_id='Admins') or
                              auth.has_permission('read', 'shop_products_sets_options'))
        permission_edit = (auth.has_membership(group_id='Admins') or
                           auth.has_permission('update', 'shop_products_sets'))
        permission_delete = (auth.has_membership(group_id='Admins') or
                             auth.has_permission('delete', 'shop_products_sets'))

        onclick_delete = "return confirm('" \
            + T('Do you really want to delete this product set?') + ' ' \
            + T('It will remove all product variants in products linked to this set.') \
            + "');"


        rows = self.list()
        for row in rows:
            buttons = ''
            edit = ''
            delete = ''
            vars = {'spsID':row.id}
            buttons = DIV(_class="pull-right")

            if permission_options:
                options = os_gui.get_button(
                    'noicon',
                    URL('shop_manage', 'products_set_options', vars=vars),
                    title=T('Options')
                )
                buttons.append(options)

            if permission_edit:
                edit = os_gui.get_button('edit',
                    URL('shop_manage', 'products_set_edit', vars=vars))
                buttons.append(edit)
            if permission_delete:
                delete = os_gui.get_button('delete_notext',
                    URL('shop_manage', 'products_set_delete', vars=vars),
                    onclick = onclick_delete)
                buttons.append(delete)

            tr = TR(
                TD(os_gui.max_string_length(row.Name, 30)),
                TD(os_gui.max_string_length(row.Description, 60)),
                TD(buttons)
            )

            table.append(tr)

        return table
