# -*- coding: utf-8 -*-
"""
    This file holds the settings for integrations
"""

def pos_get_menu(page):
    """
        Menu for system settings pages
    """
    pages = [['index',
              T('General'),
              URL('index')],
             ]

    return os_gui.get_submenu(pages, page, horizontal=True, htype='tabs')


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def index():
    """
        Page to set mailchimp API key
    """
    response.title = T("Settings")
    response.subtitle = T("Point os Sale")
    response.view = 'general/tabs_menu.html'

    menu = pos_get_menu(request.function)

    return dict(content='hello world',
                menu=menu)
                #save=submit)

