#!/usr/bin/env python

"""
    py.test test cases to test the ep controller (ep.py)
"""

from gluon.contrib.populate import populate

from populate_os_tables import populate_auth_user_teachers
from setup_ep_tests import setup_ep_tests


def test_my_classes(client, web2py):
    from populate_os_tables import populate_classes

    populate_classes(web2py)


    au = web2py.db.auth_user(2)
    au.password = 'password'
    au.login_start = 'ep'
    au.update_record()

    web2py.db.commit()

    # log out and log back in again to make the profile user a teacher
    url = '/default/user/logout'
    client.get(url)
    assert client.status == 200

    data = dict(email='teacher@openstudioproject.com',
                password='password',
                _formname='login')
    client.post('/default/user/login', data=data)
    assert client.status == 200

    # Check classes display
    url = '/ep/my_classes'
    client.get(url)
    assert client.status == 200

    # url = 'ep/request_sub?clsID=1&date=2018-08-01&teachers_id=2'
    # client.get(url)
    # assert client.status == 200






def test_my_payments(client, web2py):
    """
        Is the staff payments page showing?
    """
    from populate_os_tables import populate_auth_user_teachers_payment_invoices

    setup_ep_tests(web2py)

    au = web2py.db.auth_user(300)
    au.teacher = True
    au.update_record()

    web2py.db.commit()

    populate_auth_user_teachers_payment_invoices(web2py)

    # log out and log back in again to make the profile user a teacher
    url = '/default/user/logout'
    client.get(url)
    assert client.status == 200

    data = dict(email='profile@openstudioproject.com',
                password='password',
                _formname='login')
    client.post('/default/user/login', data=data)
    assert client.status == 200

    # Check payments display
    url = '/ep/my_payments'
    client.get(url)
    assert client.status == 200

    ic = web2py.db.invoices_customers(auth_customer_id=300)
    invoice = web2py.db.invoices(ic.invoices_id)
    assert invoice.InvoiceID in client.text


def test_my_payments_link_not_shown(client, web2py):
    """
        The staff payments link shouldn't show
    """

    populate_auth_user_teachers(web2py)
    setup_ep_tests(web2py)
    url = '/ep/index'
    client.get(url)
    assert client.status == 200

    assert "Payments not in client.text"
