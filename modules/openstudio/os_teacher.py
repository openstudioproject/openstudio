# -*- coding: utf-8 -*-
"""
    This file holds OpenStudio Teacher class
"""

from gluon import *
from mailchimp3 import MailChimp
from mailchimp3.mailchimpclient import MailChimpError

class Teacher:
    """

    """
    def __init__(self, auID):
        """
            Init function for teacher
        """
        db = current.globalenv['db']

        self.id = auID
        self.row = db.auth_user(auID)


    def get_payment_fixed_rate_default(self, render=False):
        """
        :return: gluon.dal.row object of db.teachers_payment_fixed_rate_default
        """
        db = current.globalenv['db']

        query = (db.teachers_payment_fixed_rate_default.auth_teacher_id ==
                 self.id)
        rows = db(query).select(db.teachers_payment_fixed_rate_default.ALL)

        if rows:
            if not render:
                return rows
            else:
                return rows.render()
        else:
            return False


    def get_payment_fixed_rate_default_display(self):
        """
        :return: HTML display of default rate for teacher
        """
        T = current.T
        row = list(self.get_payment_fixed_rate_default(render=True))[0]
        represent_float_as_amount = current.globalenv['represent_float_as_amount']

        display = DIV(
            H3(T("Default rate"))
        )

        edit_url = URL('edit_teacher_payment_fixed_rate_default',
                            vars={'cuID':self.id})

        if not row:
            display.append(
                A(T('Set default rate'),
                  _href=edit_url)
            )
            return display

        display.append(DIV(
            SPAN(T('Class rate:'), _class='bold'), ' ',
            row.ClassRate, ' ',
            row.tax_rates_id, BR(),
            A(T('Edit'),
               _href=edit_url)
        ))

        return display


    def get_payment_fixed_rate_class(self, clsID, render=False):
        """
        :return: gluon.dal.row object of db.teachers_payment_fixed_rate_class
        """
        db = current.globalenv['db']

        query = (db.teachers_payment_fixed_rate_class.auth_teacher_id ==
                 self.id) &\
                (db.teachers_payment_fixed_rate_class.classes_id ==
                 clsID)
        rows = db(query).select(db.teachers_payment_fixed_rate_class.ALL)

        if rows:
            if not render:
                return rows
            else:
                return rows.render()
        else:
            return False

