# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
    py.test test cases to test OpenStudio.
    These tests run based on webclient and need web2py server running.
"""

from gluon.contrib.populate import populate

from populate_os_tables import populate_mailing_lists


def test_settings_pos_index(client, web2py):
    """
        Can we list mailing lists?
    """
    url = '/settings_pos/index'
    client.get(url)
    assert client.status == 200

    data = {
        'pos_barcodes_checkin': 'membership_id'
    }

    client.post(url, data=data)
    assert client.status == 200

    sp = web2py.db.sys_properties(Property='pos_barcodes_checkin')
    assert sp.PropertyValue == data['pos_barcodes_checkin']

