# -*- coding: utf-8 -*-

import datetime
from decimal import Decimal, ROUND_HALF_UP

from gluon import *


class Receipts:
    """
    Class that contains functions for a receipts
    """
    def list(self, formatted=False):
        """

        :return:
        """
        db = current.db

        if formatted:
            return self._list_formatted()
        else:
            return db(query).select(db.receipts.ALL)


    def _list_formatted_link_view(self, row):
        """
        Returns the 'view' button for a receipt
        """
        from os_gui import OsGui

        T = current.T
        os_gui = OsGui()

        return os_gui.get_button(
            'noicon',
            URL('finance', 'receipt', vars={'rID': row.id}),
            title=T("View")
        )



    def _list_formatted(self):
        """

        :param list:
        :return:
        """
        T = current.T
        db = current.db
        auth = current.auth
        grid_ui = current.globalenv['grid_ui']

        fields = [
            db.receipts.id,
            db.receipts.Created_at,
            db.receipts.payment_methods_id
        ]

        links = [
            self._list_formatted_link_view,
        ]

        db.receipts.id.label = T("Receipt")

        delete_permission = auth.has_membership(group_id='Admins') or \
                            auth.has_permission('delete', 'receipts')

        grid = SQLFORM.grid(
            db.receipts,
            links=links,
            # left=left,
            field_id=db.receipts.id,
            fields=fields,
            create=False,
            editable=False,
            details=False,
            searchable=False,
            deletable=False,
            csv=False,
            # maxtextlengths=maxtextlengths,
            orderby=~db.receipts.id,
            ui=grid_ui
        )
        grid.element('.web2py_counter', replace=None)  # remove the counter
        grid.elements('span[title=Delete]', replace=None)  # remove text from delete button


        return grid

