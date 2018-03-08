# -*- coding: utf-8 -*-
'''
    Test scheduler tasks
'''

@auth.requires(auth.has_membership(group_id='Admins'))
def test_daily():
    '''
        Run daily tasks
    '''
    if request.env.remote_addr == '127.0.0.1':
        _task_mollie_subscription_invoices_and_payments()
    else:
        return None