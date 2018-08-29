# -*- coding: utf-8 -*-

"""
    py.test test cases to test the ep controller (ep.py)
"""

from gluon.contrib.populate import populate

from populate_os_tables import populate_auth_user_teachers
from populate_os_tables import prepare_classes
from setup_ep_tests import setup_ep_tests


def test_my_classes(client, web2py):
    # url = '/default/user/login'
    # client.get(url)
    # assert client.status == 200

    setup_ep_tests(web2py)
    prepare_classes(web2py, auth_teacher_id=400)

    # Check classes display
    url = '/ep/my_classes'
    client.get(url)
    assert client.status == 200

    # If Find sub is in client.text, a class is listed and the Find sub button is showing.
    assert 'Find sub' in client.text


def test_request_sub(client, web2py):
    """
    Can we request a subsitute teacher?
    """
    setup_ep_tests(web2py)
    prepare_classes(web2py, auth_teacher_id=400)

    url = '/ep/request_sub?clsID=1&date=2014-04-01&teachers_id=400'
    client.get(url)
    assert client.status == 200

    query = (web2py.db.classes_otc.Status == 'open')
    # print row
    assert web2py.db(query).count() == 1


def test_list_sub_requested_classes(client, web2py):
    """
    Are sub requested classes listed like they should?
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200


    setup_ep_tests(web2py)
    prepare_classes(web2py)
    web2py.db.classes_otc.insert(classes_id = 3,
                                 Status ='open',
                                 ClassDate ='2088-04-01')
    # web2py.db.teachers_classtypes.insert(
    #     auth_user_id = 400,
    #     school_classtypes_id = 1
    # )
    web2py.db.teachers_classtypes.insert(
        auth_user_id = 400,
        school_classtypes_id = 2
    )

    web2py.db.commit()

    url = '/ep'
    client.get(url)
    assert client.status == 200

    assert 'available_for_sub' in client.text


def test_available_for_sub(client, web2py):
    """

    :param client:
    :param web2py:
    :return:
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    setup_ep_tests(web2py)
    prepare_classes(web2py)
    cotcID = web2py.db.classes_otc.insert(classes_id = 3,
                                 Status ='open',
                                 ClassDate ='2088-04-01')
    web2py.db.teachers_classtypes.insert(
        auth_user_id = 400,
        school_classtypes_id = 2
    )

    web2py.db.commit()

    url = '/ep/available_for_sub?cotcID=' + str(cotcID)
    client.get(url)
    assert client.status == 200

    query = (web2py.db.classes_otc_sub_avail.id > 0)
    assert web2py.db(query).count() == 1


def test_cancel_available_for_sub(client, web2py):
    """

    :param client:
    :param web2py:
    :return:
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    setup_ep_tests(web2py)
    prepare_classes(web2py)
    cotcID = web2py.db.classes_otc.insert(classes_id = 3,
                                 Status ='open',
                                 ClassDate ='2088-04-01')
    web2py.db.teachers_classtypes.insert(
        auth_user_id = 400,
        school_classtypes_id = 2
    )

    cotcsaID = web2py.db.classes_otc_sub_avail.insert(
        cotcID = cotcID,
        auth_teacher_id = 400
    )

    web2py.db.commit()

    url = '/ep/cancel_available_for_sub?cotcsaID=' + str(cotcsaID)
    client.get(url)
    assert client.status == 200

    query = (web2py.db.classes_otc_sub_avail.id > 0)
    assert web2py.db(query).count() == 0


def test_my_payments(client, web2py):
    """
        Is the staff payments page showing?
    """
    from populate_os_tables import populate_auth_user_teachers_payment_invoices
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

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

    data = dict(email='ep@openstudioproject.com',
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

    assert "Payments" not in client.text
