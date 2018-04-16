# -*- coding: utf-8 -*-
"""
    This file holds functions for mailchimp lists
"""

def lists_for_customer():
    """
        List mailchimp lists with subscriptions for customer
    """
    import mailchimp3
    cuID = request.vars['cuID']

    return dict(content="Everybody's favorite monkey")


