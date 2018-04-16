# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
    py.test test cases to test OpenStudio.
    These tests run based on webclient and need web2py server running.
"""

from gluon.contrib.populate import populate

from populate_os_tables import populate_customers
from populate_os_tables import populate_sys_organizations
from populate_os_tables import populate_postcode_groups
from populate_os_tables import populate_settings_shop_links
from populate_os_tables import populate_settings_shop_customers_profile_announcements


def test_settings_mail_mailing_lists(client, web2py):
    """
        Can we list mailing lists?
    """



def test_settings_mail_mailing_list_add(client, web2py):
    """
        Can we add mailing_lists?
    """