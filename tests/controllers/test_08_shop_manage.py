# -*- coding: utf-8 -*-
#!/usr/bin/env python

'''py.test test cases to test OpenStudio.

These tests run based on webclient and need web2py server running.
'''

def test_workflow(client, web2py):
    '''
        Can we edit the workflow settings?
    '''
    url = '/shop_manage/workflow'
    client.get(url)
    assert client.status == 200

    data = {
        'shop_requires_complete_profile': 'on',
        'shop_classes_advance_booking_limit':'22',
        'shop_classes_cancellation_limit':'7',
        'shop_subscriptions_start':'today'
    }

    client.post(url, data=data)
    assert client.status == 200

    # Check that the settings have been saved in the db
    assert web2py.db.sys_properties(Property='shop_requires_complete_profile').PropertyValue == \
           data['shop_requires_complete_profile']
    assert web2py.db.sys_properties(Property='shop_classes_advance_booking_limit').PropertyValue == \
           data['shop_classes_advance_booking_limit']
    assert web2py.db.sys_properties(Property='shop_classes_cancellation_limit').PropertyValue == \
           data['shop_classes_cancellation_limit']
    assert web2py.db.sys_properties(Property='shop_subscriptions_start').PropertyValue == \
           data['shop_subscriptions_start']