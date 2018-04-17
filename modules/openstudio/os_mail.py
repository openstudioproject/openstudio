# -*- coding: utf-8 -*-
"""
    This file holds mail related classes
"""

from gluon import *


class MailingLists:
    def list(self):
        """
            :return: List of mailinglists (gluon.dal.rows)
        """
        db = current.globalenv['db']

        query = db.mailing_lists
        rows = db(query).select(db.mailing_lists.ALL,
                                orderby=db.mailing_lists.Name)

        return rows


    def list_formatted(self):
        """
            :return: HTML table with mailing lists
        """
        from os_gui import OsGui

        T = current.T
        os_gui = OsGui()
        auth = current.globalenv['auth']

        header = THEAD(TR(TH(T('Name')),
                          TH(T('Description')),
                          TH(T('Frequency')),
                          TH(T('MailChimp ListID')),
                          TH()))
        table = TABLE(header, _class='table table-striped table-hover')

        permission_edit = (auth.has_membership(group_id='Admins') or
                           auth.has_permission('update', 'mailing_lists'))
        permission_delete = (auth.has_membership(group_id='Admins') or
                             auth.has_permission('delete', 'mailing_lists'))

        onclick_delete = "return confirm('" \
            + T('Do you really want to delete this list?') + ' ' \
            + "');"

        rows = self.list()
        for row in rows:
            buttons = ''
            edit = ''
            delete = ''
            vars = {'mlID':row.id}

            if permission_edit:
                edit = os_gui.get_button('edit',
                    URL('settings_mail', 'mailing_list_edit', vars=vars))

            if permission_delete:
                delete = os_gui.get_button('delete_notext',
                    URL('settings_mail', 'mailing_list_delete', vars=vars),
                    onclick=onclick_delete,
                )
            buttons = DIV(edit, delete, _class='pull-right')

            tr = TR(
                TD(os_gui.max_string_length(row.Name, 20)),
                TD(os_gui.max_string_length(row.Description, 30)),
                TD(os_gui.max_string_length(row.Frequency, 20)),
                TD(row.MailChimpListID),
                TD(buttons)
            )

            table.append(tr)

        return table
