# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
    py.test test cases to test OpenStudio.
    These tests run based on webclient and need web2py server running.
"""

from gluon.contrib.populate import populate

from populate_os_tables import populate_mailing_lists
from populate_os_tables import populate_sys_notifications


def test_settings_mail_mailing_lists(client, web2py):
    """
        Can we list mailing lists?
    """
    populate_mailing_lists(web2py)

    url = '/settings_mail/mailing_lists'
    client.get(url)
    assert client.status == 200

    ml = web2py.db.mailing_lists(1)
    assert ml.Name in client.text


def test_settings_mail_mailing_list_add(client, web2py):
    """
        Can we add mailing_lists?
    """
    url = '/settings_mail/mailing_list_add'
    client.get(url)
    assert client.status == 200

    data = {
        'Name': 'Newsletter',
        'Description': 'The latest offering of whatever we do in this business',
        'Frequency': 'Twice daily, at least',
        'MailChimpListID': '1235346_test'
    }

    client.post(url, data=data)
    assert client.status == 200

    assert data['Name'] in client.text
    ml = web2py.db.mailing_lists(1)
    assert ml.Name == data['Name']


def test_settings_mail_mailing_list_edit(client, web2py):
    """
        Can we edit mailing_lists?
    """
    populate_mailing_lists(web2py)

    url = '/settings_mail/mailing_list_edit?mlID=1'
    client.get(url)
    assert client.status == 200

    data = {
        'id': 1,
        'Name': 'Newsletter_edited',
        'Description': 'The latest offering of whatever we do in this business',
        'Frequency': 'Twice daily, at least',
        'MailChimpListID': '1235346_test'
    }

    client.post(url, data=data)
    assert client.status == 200

    assert data['Name'] in client.text
    ml = web2py.db.mailing_lists(1)
    assert ml.Name == data['Name']


def test_settings_mail_mailing_list_delete(client, web2py):
    """
        Can we delete mailing_lists?
    """
    populate_mailing_lists(web2py)

    url = '/settings_mail/mailing_list_delete?mlID=1'
    client.get(url)
    assert client.status == 200

    query = (web2py.db.mailing_lists.id > 0)
    assert web2py.db(query).count() == 0


def test_sys_notifications(client, web2py):
    """
    Are sys_notification listed like they should?
    """
    populate_sys_notifications(web2py)

    url = '/settings_mail/notifications'
    client.get(url)
    assert client.status == 200

    notification = web2py.db.sys_notifications(1)
    assert notification.NotificationTitle in client.text

    sys_notification_email = web2py.db.sys_notifications_email(1)
    assert sys_notification_email.Email in client.text


def test_sys_notifications_email_add(client, web2py):
    """
    Can sys_notification_emails be added?
    """
    populate_sys_notifications(web2py, with_email=False)

    url = '/settings_mail/notifications_email_add?snID=1'
    client.get(url)
    assert client.status == 200

    data = {
        'Email': 'admin@openstudioproject.com'
    }

    client.post(url, data=data)
    assert client.status == 200

    sne = web2py.db.sys_notifications_email(1)
    assert sne.Email == data['Email']

    assert data['Email'] in client.text


def test_sys_notifications_email_delete(client, web2py):
    """
    Are sys_notification listed like they should?
    """
    populate_sys_notifications(web2py, with_email=True)

    url = '/settings_mail/notifications_email_delete?sneID=1'
    client.get(url)
    assert client.status == 200

    query = web2py.db.sys_notifications_email
    assert web2py.db(query).count() == 0