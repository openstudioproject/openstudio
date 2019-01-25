# -*- coding: utf-8 -*-

@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'accounting_cashbooks'))
def index():
    """

    :return:
    """
    from openstudio.os_accounting_expenses import AccountingExpenses

    response.title = T('Finance')
    response.subtitle = T('Expenses')
    response.view = 'general/only_content.html'

    ae = AccountingExpenses()
    content = ae.list_sqlform_grid()

    return dict(
        content=content
    )