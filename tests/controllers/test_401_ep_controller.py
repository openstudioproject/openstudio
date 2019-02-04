# -*- coding: utf-8 -*-

"""
    py.test test cases to test the ep controller (ep.py)
"""

import datetime

from gluon.contrib.populate import populate

from populate_os_tables import populate_auth_user_teachers
from populate_os_tables import prepare_classes
from setup_ep_tests import setup_ep_tests


def test_my_classes(client, web2py):
    """
        Can we add a default rate
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    setup_ep_tests(web2py)
    prepare_classes(web2py, auth_teacher_id=400)

    url = '/ep/my_classes'
    client.get(url)
    assert client.status == 200

    today = datetime.date.today()
    date = datetime.date(today.year, today.month, 1)
    first_monday = date + datetime.timedelta(7 - date.weekday() or 7)

    assert str(first_monday) in client.text

    # If Find sub is in client.text, a class is listed and the Find sub button is showing.

    #TODO Enable as soon as find sub goes live
    # assert 'Find sub' in client.text


def test_my_classes_set_month(client, web2py):
    """
        Does setting a month work?
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    setup_ep_tests(web2py)
    prepare_classes(web2py, auth_teacher_id=400)

    url = '/ep/my_classes_set_month?year=2014&month=1&back=my_classes'
    client.get(url)
    assert client.status == 200

    assert '2014' in client.text


def test_my_classes_show_current(client, web2py):
    """
        Does setting a month work?
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    setup_ep_tests(web2py)
    prepare_classes(web2py, auth_teacher_id=400)

    url = '/ep/my_classes_show_current'
    client.get(url)
    assert client.status == 200

    assert unicode(datetime.date.today().year) in client.text


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

#
# def test_list_sub_requested_classes(client, web2py):
#     """
#     Are sub requested classes listed like they should?
#     """
#     url = '/default/user/login'
#     client.get(url)
#     assert client.status == 200
#
#
#     setup_ep_tests(web2py)
#     prepare_classes(web2py)
#     web2py.db.classes_otc.insert(classes_id = 3,
#                                  Status ='open',
#                                  ClassDate ='2088-04-01')
#     # web2py.db.teachers_classtypes.insert(
#     #     auth_user_id = 400,
#     #     school_classtypes_id = 1
#     # )
#     web2py.db.teachers_classtypes.insert(
#         auth_user_id = 400,
#         school_classtypes_id = 2
#     )
#
#     web2py.db.commit()
#
#     url = '/ep'
#     client.get(url)
#     assert client.status == 200
#
#     assert 'available_for_sub' in client.text


# def test_available_for_sub(client, web2py):
#     """
#
#     :param client:
#     :param web2py:
#     :return:
#     """
#     url = '/default/user/login'
#     client.get(url)
#     assert client.status == 200
#
#     setup_ep_tests(web2py)
#     prepare_classes(web2py)
#     cotcID = web2py.db.classes_otc.insert(classes_id = 3,
#                                  Status ='open',
#                                  ClassDate ='2088-04-01')
#     web2py.db.teachers_classtypes.insert(
#         auth_user_id = 400,
#         school_classtypes_id = 2
#     )
#
#     web2py.db.commit()
#
#     url = '/ep/available_for_sub?cotcID=' + str(cotcID)
#     client.get(url)
#     assert client.status == 200
#
#     query = (web2py.db.classes_otc_sub_avail.id > 0)
#     assert web2py.db(query).count() == 1
#
#
# def test_cancel_available_for_sub(client, web2py):
#     """
#
#     :param client:
#     :param web2py:
#     :return:
#     """
#     url = '/default/user/login'
#     client.get(url)
#     assert client.status == 200
#
#     setup_ep_tests(web2py)
#     prepare_classes(web2py)
#     cotcID = web2py.db.classes_otc.insert(classes_id = 3,
#                                  Status ='open',
#                                  ClassDate ='2088-04-01')
#     web2py.db.teachers_classtypes.insert(
#         auth_user_id = 400,
#         school_classtypes_id = 2
#     )
#
#     cotcsaID = web2py.db.classes_otc_sub_avail.insert(
#         cotcID = cotcID,
#         auth_teacher_id = 400
#     )
#
#     web2py.db.commit()
#
#     url = '/ep/cancel_available_for_sub?cotcsaID=' + str(cotcsaID)
#     client.get(url)
#     assert client.status == 200
#
#     query = (web2py.db.classes_otc_sub_avail.id > 0)
#     assert web2py.db(query).count() == 0


#TODO Enable as soon as find sub goes live
#
# def test_list_sub_requested_classes(client, web2py):
#     """
#     Are sub requested classes listed like they should?
#     """
#     url = '/default/user/login'
#     client.get(url)
#     assert client.status == 200
#
#
#     setup_ep_tests(web2py)
#     prepare_classes(web2py)
#     web2py.db.classes_otc.insert(classes_id = 3,
#                                  Status ='open',
#                                  ClassDate ='2088-04-01')
#     # web2py.db.teachers_classtypes.insert(
#     #     auth_user_id = 400,
#     #     school_classtypes_id = 1
#     # )
#     web2py.db.teachers_classtypes.insert(
#         auth_user_id = 400,
#         school_classtypes_id = 2
#     )
#
#     web2py.db.commit()
#
#     url = '/ep'
#     client.get(url)
#     assert client.status == 200
#
#     assert 'available_for_sub' in client.text


#TODO Enable as soon as find sub goes live
# def test_available_for_sub(client, web2py):
#     """
#
#     :param client:
#     :param web2py:
#     :return:
#     """
#     url = '/default/user/login'
#     client.get(url)
#     assert client.status == 200
#
#     setup_ep_tests(web2py)
#     prepare_classes(web2py)
#     cotcID = web2py.db.classes_otc.insert(classes_id = 3,
#                                  Status ='open',
#                                  ClassDate ='2088-04-01')
#     web2py.db.teachers_classtypes.insert(
#         auth_user_id = 400,
#         school_classtypes_id = 2
#     )
#
#     web2py.db.commit()
#
#     url = '/ep/available_for_sub?cotcID=' + str(cotcID)
#     client.get(url)
#     assert client.status == 200
#
#     query = (web2py.db.classes_otc_sub_avail.id > 0)
#     assert web2py.db(query).count() == 1
#
#
# #TODO Enable as soon as find sub goes live
# def test_cancel_available_for_sub(client, web2py):
#     """
#
#     :param client:
#     :param web2py:
#     :return:
#     """
#     url = '/default/user/login'
#     client.get(url)
#     assert client.status == 200
#
#     setup_ep_tests(web2py)
#     prepare_classes(web2py)
#     cotcID = web2py.db.classes_otc.insert(classes_id = 3,
#                                  Status ='open',
#                                  ClassDate ='2088-04-01')
#     web2py.db.teachers_classtypes.insert(
#         auth_user_id = 400,
#         school_classtypes_id = 2
#     )
#
#     cotcsaID = web2py.db.classes_otc_sub_avail.insert(
#         cotcID = cotcID,
#         auth_teacher_id = 400
#     )
#
#     web2py.db.commit()
#
#     url = '/ep/cancel_available_for_sub?cotcsaID=' + str(cotcsaID)
#     client.get(url)
#     assert client.status == 200
#
#     query = (web2py.db.classes_otc_sub_avail.id > 0)
#     assert web2py.db(query).count() == 0



def test_my_payments(client, web2py):
    """
        Is the staff payments page showing?
    """
    from populate_os_tables import populate_auth_user_teachers_payment_invoices
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    setup_ep_tests(web2py)
    populate_auth_user_teachers_payment_invoices(web2py)

    # Check payments display
    url = '/ep/my_payments'
    client.get(url)
    assert client.status == 200

    ic = web2py.db.invoices_customers(auth_customer_id=400)
    invoice = web2py.db.invoices(ic.invoices_id)
    assert invoice.InvoiceID in client.text


def test_my_expenses(client, web2py):
    """
        Is the my expenses page showing?
    """
    from populate_os_tables import populate_employee_claims

    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_employee_claims(web2py)
    # Check expenses display
    url = '/ep/my_expenses'
    client.get(url)
    assert client.status == 200

    assert 'First Expense' in client.text


def test_my_expenses_add(client, web2py):
    """
        Can we add a expense?
    """
    from populate_os_tables import populate_tax_rates

    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    setup_ep_tests(web2py)
    populate_tax_rates(web2py)

    url = '/ep/my_expenses_expense_add'
    client.get(url)
    assert client.status == 200
    # assert 'Add Expense' in client.text

    data = {
            'Amount': '5',
            'Quantity': '3',
            'tax_rates_id': '1',
            'Description': 'Add First Expense'}

    client.post(url, data=data)
    assert client.status == 200

    assert web2py.db(web2py.db.employee_claims).count() == 1


def test_my_expenses_edit(client, web2py):
    """
         Can you edit an expense
    """
    from populate_os_tables import populate_employee_claims

    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_employee_claims(web2py)

    # Check expenses display
    url = '/ep/my_expenses_expense_edit?ecID=1'
    client.get(url)
    assert client.status == 200

    data = {
        'id': '1',
        'Amount': '5',
        'Quantity': '3',
        'tax_rates_id': '1',
        'Description': 'Edit first expense'}
    
    client.post(url, data=data)
    assert client.status == 200
    assert (web2py.db.employee_claims.Description == data['Description'])


def test_my_expenses_delete(client, web2py):
    """
    Can you delete a expense
    """
    from populate_os_tables import populate_employee_claims

    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_employee_claims(web2py)
    claims_before_delete = web2py.db(web2py.db.employee_claims).count()

    # Check expenses display
    url = '/ep/my_expenses_expense_delete?ecID=1'
    client.get(url)
    assert client.status == 200

    assert web2py.db(web2py.db.employee_claims).count() == claims_before_delete - 1
