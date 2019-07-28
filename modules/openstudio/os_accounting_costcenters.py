# -*- coding: utf-8 -*-

from gluon import *

class AccountingCostCenters:
    def list(self, archived=False):
        """

        :return:
        """
        db = current.db

        query = (db.accounting_costcenters.Archived == archived)
        rows = db(query).select(db.accounting_costcenters.ALL,
                                orderby=db.accounting_costcenters.Name)

        return rows


    def list_formatted(self, archived=False):
        """

        :return: HTML table of Accounting costcenters
        """
        T = current.T
        auth = current.auth
        rows = self.list(archived=archived)

        permission_edit = auth.has_membership(group_id='Admins') or \
                          auth.has_permission('update', 'accounting_costcenters')

        header = THEAD(TR(
            TH(T("Name")),
            TH(T("Accounting Code")),
            TH(), # Buttons
        ))

        table = TABLE(header, _class="table table-striped table-hover")
        for i, row in enumerate(rows):
            repr_row = list(rows[i:i + 1].render())[0]

            table.append(TR(
                TD(repr_row.Name),
                TD(repr_row.AccountingCode),
                TD(self._list_formatted_get_buttons(
                    row,
                    permission_edit,
                ))
            ))

        return table


    def _list_formatted_get_buttons(self,
                                    row,
                                    permission_edit):
        """
        :param row:
        :param permission_edit:
        :return:
        """
        from .os_gui import OsGui

        os_gui = OsGui()
        buttons = DIV(_class='pull-right')

        if permission_edit:
            edit = os_gui.get_button(
                'edit',
                URL('settings', 'financial_costcenter_edit', vars={'acID': row.id})
            )
            buttons.append(edit)
            archive = os_gui.get_button(
                'archive',
                URL('settings', 'financial_costcenter_archive', vars={'acID': row.id})
            )
            buttons.append(archive)

        return buttons

