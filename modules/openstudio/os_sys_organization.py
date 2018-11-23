# -*- coding: utf-8 -*-

# Import all helpers, etc.
from gluon import *

class SysOrganization:

    def __init__(self, soID):
        """

        :param soID: db.sys_organizations.id
        """
        db = current.globalenv['db']
        self.soID = soID
        self.row = db.sys_organizations(self.soID)

