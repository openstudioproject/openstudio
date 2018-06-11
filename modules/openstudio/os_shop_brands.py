# -*- coding: utf-8 -*-

from gluon import *

class ShopBrands:
    def __init__(self, show_archive=False):
        self.show_archive = show_archive


    def list(self):
        """
            :return: List of shop brands (gluon.dal.rows)
        """
        db = current.db

        query = (db.shop_brands.Archived == self.show_archive)
        rows = db(query).select(db.shop_brands.ALL,
                                orderby=db.shop_brands.Name)

        return rows


    def list_formatted(self):
        """
            :return: HTML table with shop brands
        """
        T = current.T
        os_gui = current.globalenv['os_gui']
        auth = current.auth

        header = THEAD(TR(TH(T('Brand')),
                          TH(T('Description')),
                          TH()))
        table = TABLE(header, _class='table table-striped table-hover')

        permission_edit = (auth.has_membership(group_id='Admins') or
                           auth.has_permission('update', 'shop_brands'))

        rows = self.list()
        for row in rows:
            buttons = ''
            edit = ''
            archive = ''
            vars = {'sbID':row.id}

            if permission_edit:
                edit = os_gui.get_button('edit',
                    URL('shop_manage', 'brand_edit', vars=vars))
                archive = os_gui.get_button('archive',
                    URL('shop_manage', 'brand_archive', vars=vars))
                buttons = DIV(edit, archive, _class='pull-right')

            tr = TR(
                TD(os_gui.max_string_length(row.Name, 30)),
                TD(os_gui.max_string_length(row.Description, 60)),
                TD(buttons)
            )

            table.append(tr)

        return table