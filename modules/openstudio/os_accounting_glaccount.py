# -*- coding: utf-8 -*-

from gluon import *

class AccountingGLAccount:

    def __init__(self, agID):
        db = current.db

        self.agID = agID
        self.row = db.accounting_glaccounts(agID)


    def archive(self):
        self.row.Archived = not self.row.Archived
        self.row.update_record()



