def test_staff_payments_link_not_shown(client, web2py):
    """
        The staff payments link shouldn't show
    """
    from setup_profile_tests import setup_profile_tests
    setup_profile_tests(web2py)

    url = '/profile/index'
    client.get(url)
    assert client.status == 200

    assert "Payments not in client.text"


def test_staff_payments(client, web2py):
    """
        Is the staff payments page showing?
    """
    from populate_os_tables import populate_auth_user_teachers_payment_invoices

    setup_profile_tests(web2py)

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
    url = '/profile/staff_payments'
    client.get(url)
    assert client.status == 200

    ic = web2py.db.invoices_customers(auth_customer_id=300)
    invoice = web2py.db.invoices(ic.invoices_id)
    assert invoice.InvoiceID in client.text
