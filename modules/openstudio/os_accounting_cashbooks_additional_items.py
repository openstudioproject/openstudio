# -*- coding: utf-8 -*-

from gluon import *

class AccountingCashbooksAdditionalItems:
    def list(self, date_from, date_until, booking_type='debit'):
        """
        List cashbook items, debit (in) or credit (out)
        :param item_type: one of ['debit', 'credit']
        :param date_from: datetime.date
        :param date_until: datetime.date
        :return: gluon.dal.rows object of Cashbook Items
        """
        db = current.db

        query = (db.accounting_cashbooks_additional_items.BookingType == booking_type) & \
                (db.accounting_cashbooks_additional_items.BookingDate >= date_from) & \
                (db.accounting_cashbooks_additional_items.BookingDate <= date_until)
        rows = db(query).select(db.accounting_cashbooks_additional_items.ALL,
                                orderby=db.accounting_cashbooks_additional_items.BookingDate)

        return rows


    def list_formatted(self, date_from, date_until, booking_type='debit'):
        """
        List cashbook items, debit (in) or credit (out)
        :param item_type: one of ['debit', 'credit']
        :param date_from: datetime.date
        :param date_until: datetime.date
        :return: HTML table
        """
        from general_helpers import max_string_length
        represent_float_as_amount = current.globalenv['represent_float_as_amount']

        T = current.T
        auth = current.auth
        rows = self.list(date_from, date_until, booking_type)

        permission_edit = auth.has_membership(group_id='Admins') or \
                          auth.has_permission('update', 'accounting_cashbooks_additional_items')
        permission_delete = auth.has_membership(group_id='Admins') or \
                            auth.has_permission('delete', 'accounting_cashbooks_additional_items')

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
                URL('finance_cashbook', 'additional_item_edit', vars={'acaiID': row.id})
            )
            buttons.append(edit)
        if permission_delete:
            onclick_delete = \
                "return confirm('" + \
                T('m_openstudio_os_accounting_cashbooks_additional_items_delete_confirm') + \
                "');"

            delete = os_gui.get_button(
                'delete_notext',
                URL('finance_cashbook', 'additional_item_delete', vars={'acaiID': row.id}),
                onclick=onclick_delete
            )
            buttons.append(delete)

        return buttons

