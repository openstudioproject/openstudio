# -*- coding: utf-8 -*-

from gluon import *


class ShopSuppliers:
    def __init__(self, show_archive=False):
        self.show_archive = show_archive


    def list(self):
        """
            :return: List of shop suppliers (gluon.dal.rows)
        """
        db = current.db

        query = (db.shop_suppliers.Archived == self.show_archive)
        rows = db(query).select(db.shop_suppliers.ALL,
                                orderby=db.shop_suppliers.Name)

        return rows


    def list_formatted(self):
        """
            :return: HTML table with shop brands
        """
        T = current.T
        os_gui = current.globalenv['os_gui']
        auth = current.auth

        header = THEAD(TR(TH(T('Name')),
                          TH(T('Description')),
                          TH(T('Contact')),
                          TH(T('Phone')),
                          TH(T('Email')),
                          TH()))
        table = TABLE(header, _class='table table-striped table-hover')

        permission_edit = (auth.has_membership(group_id='Admins') or
                           auth.has_permission('update', 'shop_suppliers'))

        rows = self.list()
        for row in rows:
            buttons = ''
            edit = ''
            archive = ''
            vars = {'supID':row.id}

            if permission_edit:
                edit = os_gui.get_button('edit',
                    URL('shop_manage', 'supplier_edit', vars=vars))
                archive = os_gui.get_button('archive',
                    URL('shop_manage', 'supplier_archive', vars=vars))
                buttons = DIV(edit, archive, _class='pull-right')

            tr = TR(
                TD(os_gui.max_string_length(row.Name, 30)),
                TD(os_gui.max_string_length(row.Description, 30)),
                TD(os_gui.max_string_length(row.ContactName, 20),
                   _title=row.ContactName),
                TD(os_gui.max_string_length(row.ContactPhone, 15)),
                TD(os_gui.max_string_length(row.ContactEmail, 32),
                   _title=row.ContactEmail),
                TD(buttons)
            )

            table.append(tr)

        return table
