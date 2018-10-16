# -*- coding: utf-8 -*-

from gluon import *

class ClassPrices:
    def get_prices_for_class(self, clsID):
        """
        :param clsID: db.classes.id
        :return: gluon.dal.rows object containing db.classes_price for a class
        """
        db = current.db

        query = (db.classes_price.classes_id == clsID)

        return db(query).select(db.classes_price.ALL)


    def get_prices_for_class_display(self, clsID):
        """
        Get table to display prices for a class
        :param clsID: db.classes.id
        :return: HTML table
        """
        from openstudio.os_gui import  OsGui

        os_gui = OsGui()
        auth = current.auth

        rows = self.get_prices_for_class(clsID)
        table = TABLE(
            self._get_prices_for_class_display_header(),
            _class="table table-striped table-hover"
        )

        edit_permission = (auth.has_membership(group_id='Admins') or
                           auth.has_permission('update', 'classes_price'))
        delete_permission = (auth.has_membership(group_id='Admins') or
                             auth.has_permission('delete', 'classes_price'))

        for i, row in enumerate(rows):
            repr_row = list(rows[i:i + 1].render())[0]

            tr = TR(
                TD(repr_row.Startdate),
                TD(repr_row.Enddate),
                TD(repr_row.Dropin, BR(),
                   repr_row.tax_rates_id_dropin),
                TD(repr_row.Trial, BR(),
                   repr_row.tax_rates_id_trial),
                TD(SPAN(repr_row.DropinMembership, BR(),
                   repr_row.tax_rates_id_dropin_membership) if row.DropinMembership else ''),
                TD(SPAN(repr_row.TrialMembership, BR(),
                   repr_row.tax_rates_id_trial_membership) if row.TrialMembership else ''),
                TD(repr_row.GLAccountDropin),
                TD(repr_row.GLAccountTrial),
                TD(self._get_prices_for_class_display_buttons(
                    os_gui,
                    row,
                    edit_permission,
                    delete_permission
                ))
            )


            table.append(tr)

        return table


    def _get_prices_for_class_display_buttons(self, os_gui, row, edit_permission, delete_permission):
        """
            Buttons for class prices table
        """
        T = current.T
        buttons = DIV(_class='pull-right')

        if edit_permission:
            edit = os_gui.get_button(
                'edit',
                URL('class_price_edit', vars={'clpID': row.id, 'clsID': row.classes_id})
            )
            buttons.append(edit)

        if delete_permission:
            onclick = "return confirm('" + \
                     T('Do you really want to remove these prices?') + "');"

            edit = os_gui.get_button(
                'delete_notext',
                URL('class_price_delete', vars={'clpID': row.id, 'clsID': row.classes_id}),
                onclick=onclick
            )
            buttons.append(edit)


        return buttons


    def _get_prices_for_class_display_header(self):
        """
        :return: THEAD header for class prices table
        """
        T = current.T

        header = THEAD(TR(
            TH(T('Start date')),
            TH(T('End date')),
            TH(T('Drop-in')),
            TH(T('Trial')),
            TH(T('Membership Drop-in')),
            TH(T('Membership Trial')),
            TH(T('G/L Account Drop-in')),
            TH(T('G/L Account Trial')),
            TH() # buttons
        ))

        return header