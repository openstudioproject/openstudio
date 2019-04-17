# -*- coding: utf-8 -*-
"""
    This file holds OpenStudio Invoices class
"""

from gluon import *
import datetime

class Teachers:
    """
        This class holds functions related to multiple teachers
    """
    def get_teacher_ids(self):
        """
        :return: gluon.dal.rows containing db.auth_user.id where teacher == True
        """
        db = current.db

        query = (db.auth_user.trashed == False) & \
                (db.auth_user.teacher == True)

        return db(query).select(db.auth_user.id)


    def get_teachers_list_classes_in_month(self, year, month):
        """
        :param year: int
        :param month: int
        :return: dict(teacher_id=[classes])
        """
        from openstudio.os_class_schedule import ClassSchedule
        from general_helpers import get_last_day_month

        ids = self.get_teacher_ids()

        start_date = datetime.date(year, month, 1)
        last_day = get_last_day_month(start_date)

        data = {}

        for teID in ids:
            teID = int(teID)
            data[teID] = {}
            data[teID]['classes'] = {}
            data[teID]['classes_count'] = 0
            for each_day in range(1, last_day.day + 1):
                # list days
                day = datetime.date(year, month, each_day)
                weekday = day.isoweekday()

                class_schedule = ClassSchedule(
                    date=day,
                    filter_id_teacher=int(teID)
                )

                rows = class_schedule.get_day_rows()

                data[teID]['classes'][day] = rows
                data[teID]['classes_count'] += len(rows)

        return data


    def list(self, search_name=None, formatted=False):
        """
        :param formatted: Boolean - return as gluon.dal.rows or html table
        :return: gluon.dal.rows object containing auth_user rows with teacher=True
        """
        db = current.db

        query = (db.auth_user.trashed == False) & \
                (db.auth_user.teacher == True) & \
                (db.auth_user.id > 1)

        if search_name:
            search_name = '%' + search_name.strip() + '%'
            query &= ((db.auth_user.display_name.like(search_name)) |
                      (db.auth_user.email == search_name.replace('%', '')))

        rows = db(query).select(db.auth_user.ALL,
                                orderby=db.auth_user.display_name)

        if not formatted:
            return rows
        else:
            return self._rows_to_table(rows)


    def _rows_to_table(self, rows):
        """
        :param rows: gluon.dal.rows object containing auth_user rows with teacher=True
        :return: HTML table
        """
        T = current.T
        auth = current.auth

        permission = auth.has_membership(group_id='Admins') or \
                     auth.has_permission('update', 'teachers')


        header = THEAD(TR(
            TH(''), # Image
            TH(T('Teacher')),
            TH(T('Classes')),
            TH(T('Events')),
            TH(T('Group (Permissions)')),
            TH() # Actions
        ))

        table = TABLE(header, _class='table table-striped table-hover')

        for i, row in enumerate(rows):
            repr_row = list(rows[i:i + 1].render())[0]

            teaches_classes = ''
            teaches_workshops = ''
            group = ''
            if permission:
                teaches_classes = self._rows_to_table_link_classes(row)
                teaches_events = self._rows_to_table_link_events(row)
                group = self._rows_to_table_link_group(row)

            tr = TR(
                TD(repr_row.thumbsmall),
                TD(repr_row.display_name),
                TD(teaches_classes),
                TD(teaches_events),
                TD(group),
                TD(self._rows_to_table_buttons(row, permission))
            )

            table.append(tr)

        return table


    def _rows_to_table_link_classes(self, row):
        """
            Returns 'yes' if a teacher teaches classes and no if otherwise
        """
        from os_gui import OsGui

        os_gui = OsGui()
        T = current.T

        if row.teaches_classes:
            label = os_gui.get_label('success', T('Yes'))
        else:
            label = os_gui.get_label('default', T('No'))

        return A(label, _href=URL('teaches_classes', vars={'uID':row.id}))


    def _rows_to_table_link_events(self, row):
        """
            Returns 'yes' if a teacher teaches workshops and no if otherwise
        """
        from os_gui import OsGui

        os_gui = OsGui()
        T = current.T

        if row.teaches_workshops:
            label = os_gui.get_label('success', T('Yes'))
        else:
            label = os_gui.get_label('default', T('No'))

        return A(label, _href=URL('teaches_events', vars={'uID':row.id}))


    def _rows_to_table_link_group(self, row):
        """
            This function returns the group a user belongs to and shows it as a link
            to a page which allows users to change it.
        """
        from os_gui import OsGui

        os_gui = OsGui()
        T = current.T
        db = current.db

        no_group = A(os_gui.get_label('default', T('No group')),
                     _href=URL('school_properties', 'account_group_add', args=[row.id]))

        if row.id == 1:
            ret_val = os_gui.get_label('info', "Admins")
        else:  # check if the user had a group
            if db(db.auth_membership.user_id == row.id).count() > 0:  # change group
                query = (db.auth_membership.user_id == row.id)
                left = [db.auth_group.on(db.auth_group.id ==
                                         db.auth_membership.group_id)]
                rows = db(query).select(db.auth_group.ALL,
                                        db.auth_membership.ALL,
                                        left=left)
                for query_row in rows:
                    role = query_row.auth_group.role
                    if 'user' not in role:
                        ret_val = A(os_gui.get_label('info', role),
                                    _href=URL('school_properties',
                                              "account_group_edit",
                                              args=[query_row.auth_membership.id]))
                    else:  # no group added yet
                        ret_val = no_group
            else:  # no group added yet
                ret_val = no_group

        return ret_val


    def _rows_to_table_buttons(self, row, permission):
        """
            This function returns the group a user belongs to and shows it as a link
            to a page which allows users to change it.
        """
        from os_gui import OsGui

        os_gui = OsGui()
        T = current.T
        db = current.db

        if not permission:
            return ''

        delete_onclick = "return confirm('" + \
                         T('Remove from teachers list? - This person will still be a customer.') + "');"

        delete = os_gui.get_button(
              'delete_notext',
              URL('teachers',
                  'delete',
                  vars={'uID': row.id}),
              onclick=delete_onclick,
            _class='pull-right'
        )


        links = []
        # Check Update teachers payment attendance classes
        links.append(A(os_gui.get_fa_icon('fa-usd'), T('Fixed rate payments'),
                       _href=URL('teachers', 'payment_fixed_rate',
                                 vars={'teID': row.id})))
        links.append(A(os_gui.get_fa_icon('fa-subway'), T('Travel allowance'),
                       _href=URL('teachers', 'payment_travel',
                                 vars={'teID': row.id})))
        links.append('divider')
        links.append(A(os_gui.get_fa_icon('fa-check-square-o'), T('Assign classtypes'),
                       _href=URL('teachers', 'edit_classtypes',
                                 vars={'uID': row.id})))
        links.append(A(os_gui.get_fa_icon('fa-pencil'), T('Edit'),
                       _href=URL('customers', 'edit',
                                 args=row.id)))

        actions = os_gui.get_dropdown_menu(
            links=links,
            btn_text=T('Actions'),
            btn_size='btn-sm',
            btn_icon='actions',
            menu_class='btn-group pull-right')

        return DIV(delete, actions, _class='pull-right')