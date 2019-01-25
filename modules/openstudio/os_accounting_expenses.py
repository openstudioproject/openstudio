# -*- coding: utf-8 -*-

from gluon import *

class AccountingExpenses:
    def list(self, date_from, date_until):
        """
        List expenses
        :param date_from: datetime.date
        :param date_until: datetime.date
        :return: gluon.dal.rows object of Expenses records
        """
        db = current.db

        query = (db.accounting_expenses.BookingDate >= date_from) & \
                (db.accounting_expenses.BookingDate <= date_until)
        rows = db(query).select(db.accounting_expenses.ALL,
                                orderby=db.accounting_expenses.BookingDate)

        return rows


    def list_formatted_simple(self, date_from, date_until):
        """
        List expenses in an HTML table
        :param date_from: datetime.date
        :param date_until: datetime.date
        :return: HTML table
        """
        from general_helpers import max_string_length
        represent_float_as_amount = current.globalenv['represent_float_as_amount']

        T = current.T
        auth = current.auth
        rows = self.list(date_from, date_until)

        permission_edit = auth.has_membership(group_id='Admins') or \
                          auth.has_permission('update', 'accounting_expenses')
        permission_delete = auth.has_membership(group_id='Admins') or \
                            auth.has_permission('delete', 'accounting_expenses')

        header = THEAD(TR(
            TH(T("Date")),
            TH(T("Description")),
            TH(T("Amount")),
            TH(), # Buttons
        ))

        total = 0

        table = TABLE(header, _class="table table-striped table-hover")
        for i, row in enumerate(rows):
            repr_row = list(rows[i:i + 1].render())[0]

            table.append(TR(
                TD(repr_row.BookingDate),
                TD(max_string_length(repr_row.Description, 44),
                   _title=repr_row.Description),
                TD(repr_row.Amount),
                TD(self._list_formatted_get_buttons(
                    row,
                    permission_edit,
                    permission_delete
                ))
            ))

            total += row.Amount

        table.append(TFOOT(TR(
            TH(),
            TH(T("Total")),
            TH(represent_float_as_amount(total)),
            TH()
        )))

        return dict(
            table=table,
            total=total
        )


    def _list_formatted_get_buttons(self,
                                    row,
                                    permission_edit,
                                    permission_delete):
        """
        :param row:
        :param permission_edit:
        :return:
        """
        from os_gui import OsGui

        T = current.T
        os_gui = OsGui()
        buttons = DIV(_class='pull-right')

        if permission_edit:
            edit = os_gui.get_button(
                'edit',
                URL('finance_expenses', 'edit', vars={'aeID': row.id})
            )
            buttons.append(edit)
        if permission_delete:
            onclick_delete = \
                "return confirm('" + \
                T('Are you sure you want to delete this expense?') + \
                "');"

            delete = os_gui.get_button(
                'delete_notext',
                URL('finance_expenses', 'delete', vars={'aeiID': row.id}),
                onclick=onclick_delete
            )
            buttons.append(delete)

        return buttons


    def list_sqlform_grid(self, date_from=None, date_until=None):
        """
        SQLFORM.grid for accounting_expenses
        :param date_from:
        :param date_until:
        :return:
        """
        db = current.db
        auth = current.auth
        session = current.session
        grid_ui = current.globalenv['grid_ui']
        DATE_FORMAT = current.DATE_FORMAT
        from general_helpers import datestr_to_python
        from openstudio.os_gui import OsGui
        os_gui = OsGui()
        T = current.T

        query = (db.accounting_expenses.id > 0)

        delete_permission = auth.has_membership(group_id='Admins') or \
                            auth.has_permission('delete', 'accounting_expenses')

        grid = SQLFORM.grid(query,
                            # links=links,
                            # left=left,
                            field_id=db.accounting_expenses.id,
                            # fields=fields,
                            create=False,
                            editable=False,
                            details=False,
                            searchable=False,
                            deletable=delete_permission,
                            csv=False,
                            # maxtextlengths=maxtextlengths,
                            orderby=~db.accounting_expenses.id,
                            ui=grid_ui)
        grid.element('.web2py_counter', replace=None)  # remove the counter
        grid.elements('span[title=Delete]', replace=None)  # remove text from delete button

        return grid
