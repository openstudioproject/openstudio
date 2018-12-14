# -*- coding: utf-8 -*-

from gluon import *

class AccountingCostCenter:

    def __init__(self, acID):
        db = current.db

        self.acID = acID
        self.row = db.accounting_costcenters(acID)


    def archive(self):
        self.row.Archived = not self.row.Archived
        self.row.update_record()



