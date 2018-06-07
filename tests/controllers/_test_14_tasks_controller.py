#!/usr/bin/env python

'''
    py.test test cases to test OpenStudio.
    These tests run based on webclient and need web2py server running.
'''

from gluon.contrib.populate import populate

from populate_os_tables import populate_tasks


def test_task_list(client, web2py):
    '''
        Test if the task list is working
    '''
    # get url so admin user is created
    url = '/tasks/index'
    client.get(url)
    assert client.status == 200

    populate_tasks(web2py)

    # get the page again now everything's been populated
    client.get(url)
    assert client.status == 200

    assert 'grapes' in client.text

    # check colors for tasks today & yesterday
    assert 'red' in client.text
    assert 'green' in client.text


def test_task_list_finished(client, web2py):
    '''
        Test if the task list is working for finished tasks
    '''
    # get url so admin user is created
    url = '/tasks/index'
    client.get(url)
    assert client.status == 200

    populate_tasks(web2py)

    # get the page again now everything's been populated
    url = '/tasks/index?filter=finished'
    client.get(url)
    assert client.status == 200

    assert 'bananas' in client.text
    assert 'line-through' in client.text # class for finished tasks in table row


def test_task_list_all(client, web2py):
    '''
        Test if the task list is working for finished tasks
    '''
    # get url so admin user is created
    url = '/tasks/index'
    client.get(url)
    assert client.status == 200

    populate_tasks(web2py)

    # get the page again now everything's been populated
    url = '/tasks/index?filter=all'
    client.get(url)
    assert client.status == 200

    assert 'bananas' in client.text
    assert 'grapes' in client.text


def test_task_pinboard(client, web2py):
    '''
        Test if open tasks for today are listed on the pin board
    '''
    # get url so admin user is created
    url = '/pinboard/index'
    client.get(url)
    assert client.status == 200

    populate_tasks(web2py)

    # get the page again now everything's been populated
    client.get(url)
    assert client.status == 200

    # make sure the item for today is in the list on the pin board
    assert 'grapes' in client.text


def test_task_add(client, web2py):
    '''
        Can we add a new task?
    '''
    # get url so admin user is created
    url = '/tasks/add'
    client.get(url)
    assert client.status == 200

    populate_tasks(web2py)

    # post the data
    data = { 'Task'         : 'Hello world!',
             'Description'  : 'Adding some items to the list',
             'Duedate'      : '2014-01-01',
             'Priority'     : 1,
             'auth_user_id' : 1 }

    url = '/tasks/add'
    client.post(url, data=data)
    assert client.status == 200

    assert 'world!' in client.text


def test_task_customer_add(client, web2py):
    '''
        Can we add a new task linked to a customer?
    '''
    # get url so admin user is created
    url = '/tasks/add'
    client.get(url)
    assert client.status == 200

    populate_tasks(web2py)

    # post the data
    data = { 'Task'            : 'Hello world!',
             'Description'     : 'Adding some items to the list',
             'Duedate'         : '2014-01-01',
             'Priority'        : 1,
             'auth_user_id'    : 2 }

    url = '/tasks/add?cuID=1001'
    client.post(url, data=data)
    assert client.status == 200

    assert 'world!' in client.text

    # check database
    query = (web2py.db.tasks.auth_customer_id == 1001)
    count = web2py.db(query).count()

    assert count == 1


def test_task_workshop_add(client, web2py):
    '''
        Can we add a new task linked to a workshop?
    '''
    # get url so admin user is created
    url = '/tasks/add'
    client.get(url)
    assert client.status == 200

    populate_tasks(web2py)

    # post the data
    data = { 'Task'         : 'Hello world!',
             'Description'  : 'Adding some items to the list',
             'Duedate'      : '2014-01-01',
             'Priority'     : 1,
             'auth_user_id' : 1 }

    url = '/tasks/add?wsID=1'
    client.post(url, data=data)
    assert client.status == 200

    assert 'world!' in client.text

    # check database
    query = (web2py.db.tasks.workshops_id == 1)
    count = web2py.db(query).count()

    assert count == 1


def test_task_edit(client, web2py):
    '''
        Can we edit a task?
    '''
    # get url so admin user is created
    url = '/tasks/index'
    client.get(url)
    assert client.status == 200

    populate_tasks(web2py)
    web2py.db.auth_user.insert(
        first_name = 'tasks',
        last_name  = 'user',
        email      = 'tasks@openstudioproject.com',
        password   = '')

    web2py.db.commit()

    # post the data
    url = '/tasks/edit?tID=1'
    client.get(url)
    assert client.status == 200

    data = { 'id'           : 1,
             'Task'         : 'Hello world!',
             'Description'  : 'Adding some items to the list',
             'Duedate'      : '2014-01-01',
             'Priority'     : 1,
             'auth_user_id' : 2,
             'wsID'         : '',
             'cuID'         : '' }

    url = '/tasks/edit?tID=1'
    client.post(url, data=data)
    assert client.status == 200

    assert 'Tasks' in client.text # verify redirection

    assert 'world!' in client.text
