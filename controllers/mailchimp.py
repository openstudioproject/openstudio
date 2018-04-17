# -*- coding: utf-8 -*-
"""
    This file holds functions for mailchimp lists
"""

def lists_for_customer():
    """
        List mailchimp lists with subscriptions for customer
    """
    from openstudio.os_mailchimp import OsMailChimp
    cuID = request.vars['cuID']

    osmc = OsMailChimp()
    table = osmc.get_mailing_lists_customer_display(cuID)

    return dict(content=table)


def subscribe():
    """
        Sign user up for a list
    """
    from openstudio.os_mailchimp import OsMailChimp

    list_id = request.vars['list_id']

    osmc = OsMailChimp()
    result = osmc.list_member_add(list_id, auth.user.id)
    session.flash = result

    redirect(URL('profile', 'mail'))


def unsubscribe():
    """
        Remove user from a list
    """
    from openstudio.os_mailchimp import OsMailChimp

    list_id = request.vars['list_id']

    osmc = OsMailChimp()
    osmc.list_member_delete(list_id, auth.user.id)

    session.flash = T('Successfully unsubscribed from list')

    redirect(URL('profile', 'mail'))
