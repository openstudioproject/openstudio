# -*- coding: utf-8 -*-

from gluon import *


class ShopProductsSetsOptions:
    def __init__(self,
                 products_sets_id,
                 url_list):
        self.products_sets_id = products_sets_id
        self.url_list = url_list


    def has_linked_products(self):
        """
            :return: boolean
        """
        db = current.db

        query = (db.shop_products.shop_products_sets_id ==
                 self.products_sets_id)

        return True if db(query).count() else False


    def list(self):
        """
            :return: List of shop products sets options
        """
        db = current.db

        query = (db.shop_products_sets_options.shop_products_sets_id ==
                 db.shop_products_sets.id)
        rows = db(query).select(db.shop_products_sets_options.ALL,
                                orderby=db.shop_products_sets_options.Name)

        return rows


    def list_formatted(self):
        """
            :return: HTML table with shop products sets options
        """
        T = current.T
        os_gui = current.globalenv['os_gui']
        auth = current.auth

        linked_products = self.has_linked_products()

        header = THEAD(TR(TH(T('Option')),
                          TH(T('Values')),
                          TH()))
        table = TABLE(header, _class='table')

        if linked_products:
            permission_delete = False
        else:
            permission_delete = (auth.has_membership(group_id='Admins') or
                                 auth.has_permission('delete', 'shop_products_options'))

        onclick_delete = "return confirm('" \
            + T('Do you really want to delete this option?') + "');"

        rows = self.list()
        for row in rows:
            buttons = DIV()
            delete = ''
            vars = {'spsoID':row.id}

            if permission_delete:
                delete = os_gui.get_button('delete_notext',
                    URL('shop_manage',
                        'shop_products_sets_options_delete',
                        vars=vars),
                    onclick=onclick_delete,
                    _class='pull-right')
                buttons.append(delete)

            tr = TR(
                TD(os_gui.max_string_length(row.Name, 30)),
                TD(self._list_formatted_get_option_values(row.id,
                                                          self.url_list)),
                TD(buttons)
            )

            table.append(tr)

        if not linked_products:
            table.append(TR(TD(self._list_formatted_get_form_add())))

        return table


    def _list_formatted_get_option_values(self, options_id, url_list):
        """
            :return: returns a list of option values for an option
        """
        from openstudio.os_shop_products_sets_options_values import ShopProductsSetsOptionsValues

        spsov = ShopProductsSetsOptionsValues(options_id, url_list)
        return spsov.list_formatted()


    def _list_formatted_get_form_add(self):
        """
            :return: CRUD form to add an option
        """
        from os_forms import OsForms

        T = current.T
        db = current.db

        db.shop_products_sets_options.Name.label = ''
        db.shop_products_sets_options.shop_products_sets_id.default = \
            self.products_sets_id

        os_forms = OsForms()
        result = os_forms.get_crud_form_create(
            db.shop_products_sets_options,
            self.url_list,
            submit_button=T("Add option"),
            form_id="AddOption"
        )

        return DIV(result['form'], result['submit'])
