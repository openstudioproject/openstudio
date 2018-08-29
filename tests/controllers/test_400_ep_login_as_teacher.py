# -*- coding: utf-8 -*-

from setup_ep_tests import setup_ep_tests

def test_logout_and_login_as_teacher(client, web2py):
    # log out and log back in again to make the profile user a teacher
    setup_ep_tests(web2py)

    url = '/default/user/logout'
    client.get(url)
    assert client.status == 200

    data = dict(email='ep@openstudioproject.com',
                password='password',
                _formname='login',
                )
    client.post('/default/user/login', data=data)
    assert client.status == 200