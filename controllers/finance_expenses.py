# -*- coding: utf-8 -*-

@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'accounting_cashbooks'))
def index():
    """

    :return:
    """
    response.title = T('Finance')
    response.subtitle = T('Expenses')
    response.view = 'general/only_content.html'

    content = T("Hello world")

    return dict(
        content=content
    )