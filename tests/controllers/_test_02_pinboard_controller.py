#!/usr/bin/env python

"""py.test test cases to test OpenStudio.

These tests run based on webclient and need web2py server running.
"""

import datetime

from gluon.contrib.populate import populate

from populate_os_tables import prepare_classes

def setup_teacher_classes_tests(web2py):
    # make admin a teacher for this test
    row = web2py.db.auth_user(1)
    row.teacher = True
    row.update_record()

    # set teacher to class 1 to admin (currently logged in)
    row = web2py.db.classes_teachers(1)
    row.auth_teacher_id = 1
    row.update_record()

    web2py.db.commit()


def test_teacher_classes_month(client, web2py):
    """
        Can we add a default rate
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    prepare_classes(web2py)
    setup_teacher_classes_tests(web2py)

    url = '/pinboard/teacher_classes_month'
    client.get(url)
    assert client.status == 200

    today = datetime.date.today()
    date = datetime.date(today.year, today.month, 1)
    first_monday = date + datetime.timedelta(7 - date.weekday() or 7)

    assert str(first_monday) in client.text


def test_teacher_classes_set_month(client, web2py):
    """
        Does setting a month work?
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    prepare_classes(web2py)
    setup_teacher_classes_tests(web2py)

    url = '/pinboard/teacher_classes_set_month?year=2014&month=1&back=teacher_classes_month'
    client.get(url)
    assert client.status == 200

    assert '2014' in client.text


def test_teacher_classes_show_current(client, web2py):
    """
        Does setting a month work?
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    prepare_classes(web2py)
    setup_teacher_classes_tests(web2py)

    url = '/pinboard/teacher_classes_show_current'
    client.get(url)
    assert client.status == 200

    assert '2018' in client.text

