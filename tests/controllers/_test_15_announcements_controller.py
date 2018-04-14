#!/usr/bin/env python

'''
    py.test test cases to test OpenStudio.
    These tests run based on webclient and need web2py server running.
'''

from gluon.contrib.populate import populate

from populate_os_tables import populate_announcements

def test_announcement_list(client, web2py):
    '''
        Test if the announcement list is working
    '''
    # get url so admin user is created
    url = '/announcements/index'
    client.get(url)
    assert client.status == 200

    populate_announcements(web2py)

    # get the page again now everything's been populated
    client.get(url)
    assert client.status == 200

    announcement = web2py.db.announcements(1)
    assert announcement.Title.split(' ')[0] in client.text

def test_announcement_add(client, web2py):
    '''
        Test if we can add an announcement
    '''
    url = '/announcements/add'
    client.get(url)
    assert client.status == 200

    data = { 'Visible'    : 'on',
             'Title'      : 'Pineapple',
             'Note'       : 'Note goes here',
             'Startdate'  : '2014-01-01',
             'Enddate'    : '',
             'Priority'   : '2'}

    client.post(url, data=data)
    assert client.status == 200

    assert data['Title'] in client.text
    assert web2py.db(web2py.db.announcements.id > 0).count() == 1


def test_announcement_edit(client, web2py):
    '''
        Test if we can edit an announcement
    '''
    # get url so admin user is created
    url = '/announcements/index'
    client.get(url)
    assert client.status == 200

    populate_announcements(web2py, 1)

    url = '/announcements/edit?aID=1'
    client.get(url)
    assert client.status == 200

    data = { 'id'         : '1',
             'Visible'    : 'on',
             'Title'      : 'Pineapple',
             'Note'       : 'Note goes here',
             'Startdate'  : '2014-01-01',
             'Enddate'    : '',
             'Priority'   : '2'}

    client.post(url, data=data)
    assert client.status == 200

    assert data['Title'] in client.text
    assert web2py.db(web2py.db.announcements.id > 0).count() == 1


def test_announcement_pinboard(client, web2py):
    '''
        Test if an announcement shows up on the pinboard properly
    '''
    web2py.db.announcements.insert(
        Visible   = True,
        Title     = 'Pineapple',
        Note      = 'Message here',
        Startdate = '2014-01-01',
        Priority  = 2)

    web2py.db.commit()
    assert web2py.db(web2py.db.announcements.id > 0).count() == 1

    url = '/pinboard/index'
    client.get(url)
    assert client.status == 200

    assert 'Pineapple' in client.text
