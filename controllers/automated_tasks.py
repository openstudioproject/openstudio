# -*- coding: utf-8 -*-

from general_helpers import max_string_length
from general_helpers import set_form_id_and_get_submit_button

@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'automated_tasks'))
def index():
    """
        Lists announcements
    """
    response.title = T("Automated tasks")
    response.subtitle = T("")
    response.view = 'general/only_content.html'

    return dict(content='hello world')