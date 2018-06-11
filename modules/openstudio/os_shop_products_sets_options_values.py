# -*- coding: utf-8 -*-

from gluon import *


class ShopProductsSetsOptionsValues:
    def __init__(self, options_id, url_list):
        self.options_id = options_id
        self.url_list = url_list


    def list(self):
        """
            :return: List of shop products sets options values (gluon.dal.rows)
        """
        db = current.db

        query = (db.shop_products_sets_options_values.shop_products_sets_options_id == \
                 self.options_id)
        rows = db(query).select(db.shop_products_sets_options_values.ALL,
                                orderby=db.shop_products_sets_options_values.Name)

        return rows


    def list_formatted(self):
        """
            :return: HTML table with shop categories
        """
        T = current.T
        os_gui = current.globalenv['os_gui']
        auth = current.auth

        table = TABLE(_class='table')

        permission_create = (auth.has_membership(group_id='Admins') or
                             auth.has_permission('create', 'shop_products_options_values'))
        permission_delete = (auth.has_membership(group_id='Admins') or
                             auth.has_permission('delete', 'shop_products_options_values'))
        onclick_delete = "return confirm('" \
            + T('Do you really want to delete this option value?') + "');"

        rows = self.list()
        for row in rows:
            buttons = DIV()
            delete = ''
            vars = {'spsovID':row.id}

            if permission_delete:
                delete = os_gui.get_button('delete_notext',
                    URL('shop_manage',
                        'shop_products_sets_options_value_delete',
                        vars=vars),
                    onclick=onclick_delete,
                    _class='pull-right')
                buttons.append(delete)

            tr = TR(
                TD(os_gui.max_string_length(row.Name, 30)),
                TD(buttons)
            )

            table.append(tr)

        table.append(TR(TD(self._list_formatted_get_form_add())))

        return table


    def _list_formatted_get_form_add(self):
        """
            :return: CRUD form to add an option
        """
        from os_forms import OsForms

        T = current.T
        db = current.db
        request = current.request

        # make sure the value is saved for the right option
        if 'shop_products_sets_options_id' in request.vars:
            options_id = request.vars['shop_products_sets_options_id']
        else:
            options_id = self.options_id

        db.shop_products_sets_options_values.Name.label = ''
        db.shop_products_sets_options_values.shop_products_sets_options_id.default = \
            options_id

        form_id = "AddValue_" + unicode(self.options_id)

        os_forms = OsForms()
        result = os_forms.get_crud_form_create(
            db.shop_products_sets_options_values,
            self.url_list,
            submit_button=T("Add value"),
            form_id=form_id,
            onaccept=[self._product_set_options_update_variants]
        )

        form = result['form']
        field_id = INPUT(_type='hidden',
                         _value=self.options_id,
                         _form=form_id,
                         _name='shop_products_sets_options_id')

        form.insert(0, field_id)

        return DIV(form, result['submit'])


    def _product_set_options_update_variants(self, form):
        """
        :param form:
        :return:
        """
        from openstudio.os_shop_products_set import ShopProductsSet

        db = current.db

        spsovID = form.vars.id
        option = db.shop_products_sets_options(self.options_id)
        spsID = option.shop_products_sets_id
        product_set = ShopProductsSet(spsID)
        product_set.insert_variants(enabled=False)
