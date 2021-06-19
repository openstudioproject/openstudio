#!/usr/bin/env python

"""
    py.test test cases to test OpenStudio.
    These tests run based on webclient and need web2py server running.
"""

from populate_os_tables import populate_sys_organizations


def test_user_register_phone_mandatory(client, web2py):
    """
    Is mobile required when the setting is set
    """
    web2py.db.sys_properties.insert(
        Property="registration_requires_mobile",
        PropertyValue="on"
    )
    web2py.db.commit()

    url ='/default/user/register'
    client.get(url)
    assert client.status == 200

    assert "Phone..." in client.text


def test_user_register_phone_not_mandatory(client, web2py):
    """
    Is mobile required when the setting is set
    """

    url ='/default/user/register'
    client.get(url)
    assert client.status == 200

    assert "Phone..." not in client.text


def test_user_register_log_acceptance_documents(client, web2py):
    """
        Is acceptance of terms and conditions logged like it should?
    """
    populate_sys_organizations(web2py)

    url ='/default/user/register'
    client.get(url)
    assert client.status == 200

    data = {
        'first_name': 'openstudio',
        'last_name': 'user',
        'email': 'pytest@openstudioproject.com',
        'password': 'V3rYStr0ng#',
        'password_two': 'V3rYStr0ng#',
    }

    client.post(url, data=data)
    assert client.status == 200

    version = web2py.db.sys_properties(Property='Version').PropertyValue
    release = web2py.db.sys_properties(Property='VersionRelease').PropertyValue
    os_version = ".".join([version, release])
    org = web2py.db.sys_organizations(1)
    log_tc = web2py.db.log_customers_accepted_documents(1)
    log_pp = web2py.db.log_customers_accepted_documents(2)
    log_td = web2py.db.log_customers_accepted_documents(3)

    # Check logging of terms and conditions
    assert log_tc.DocumentName == 'Terms and Conditions'
    assert log_tc.DocumentDescription == org.TermsConditionsURL
    assert log_tc.DocumentVersion == org.TermsConditionsVersion
    assert log_tc.DocumentURL == 'http://localhost:8001/user/register'
    assert log_tc.OpenStudioVersion == os_version

    # Check logging of privacy notice
    assert log_pp.DocumentName == 'Privacy Notice'
    assert log_pp.DocumentDescription == org.PrivacyNoticeURL
    assert log_pp.DocumentVersion == org.PrivacyNoticeVersion
    assert log_pp.DocumentURL == 'http://localhost:8001/user/register'
    assert log_pp.OpenStudioVersion == os_version

    # Check logging of true and complete data acceptance
    assert log_td.DocumentName == 'Registration form'
    assert log_td.DocumentDescription == 'True and complete data'
    assert log_td.DocumentURL == 'http://localhost:8001/user/register'
    assert log_td.OpenStudioVersion == os_version


def test_index_exists(client):
    """
        page index exists?
    """
    client.get('/default/user/login') # get a page
    assert client.status == 200
    assert "login" in client.text.lower()


def test_user_login(client, web2py):
    """
        user login is working?
        This check is important, if it fails all other tests also don't work
    """
    import datetime
    data = dict(email='admin@openstudioproject.com',
                password='OSAdmin1#',
                _formname='login')
    client.post('/default/user/login', data=data)

    client.get('/default/index') # get the index page, which should now read the pin board title
    assert client.status == 200
    assert "Pinboard" in client.text

    # Check last_login set
    # time should have been set in the last 10 seconds
    delta = datetime.timedelta(seconds = 10)
    row = web2py.db.auth_user(1)
    assert row.last_login > datetime.datetime.now() - delta


#def test_validate_new_person(client, web2py):
    #"""Is the form validating?
    #"""

    #data = dict(name='',
                #phone='',
                #_formname='new_person_form')
    #client.post('/people/new_person', data=data) # post data
    #assert client.status == 200

    #assert 'name__error' in client.text
    #assert 'phone__error' in client.text

    #assert web2py.db(web2py.db.people).count() == 0

    ## You can create other test case to check other validations, too.


#def test_save_new_person(client, web2py):
    #"""Created a new person?
    #"""

    #data = dict(name='Homer Simpson',
                #phone='9988-7766',
                #_formname='new_person_form')
    #client.post('/people/new_person', data=data)
    #assert client.status == 200

    #assert 'New person saved' in client.text

    #assert web2py.db(web2py.db.people).count() == 1
    #assert web2py.db(web2py.db.people.name == data['name']).count() == 1


#def test_get_person_by_creation_date(client, web2py):
    #"""Is my filter working?
    #"""

    #from gluon.contrib.populate import populate
    #populate(web2py.db.people, 3) # insert 3 persons with random data
    #web2py.db.commit()
    #assert web2py.db(web2py.db.people).count() == 3

    #data = dict(
            #name='John Smith',
            #phone='3322-4455',
            #created_at='1999-04-03 18:00:00')

    #web2py.db.people.insert(**data) # insert my controlled person
    #web2py.db.commit()

    #client.get('/people/get_by_creation_date.json/' +
            #data['created_at'].split()[0])
    #assert client.status == 200
    #assert 'application/json' in client.headers['content-type']

    #import json
    #person = json.loads(client.text)
    #assert person['name'] == data['name']
