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

    session.finance_expenses_add_edit_back = 'finance_expenses_index'

    ae = AccountingExpenses()
    content = ae.list_sqlform_grid()

    add = os_gui.get_button(
        'add',
        URL('add')
    )

    return dict(
        content=content,
        header_tools=add
    )


def add_edit_get_return_url(var=None):
    """
        :return: URL to shop categories list page
    """
    if session.finance_expenses_add_edit_back == 'finance_cashbook_index':
        return_url = URL('finance_cashbook', 'index')
    else:
        return_url = URL('index')

    return return_url


@auth.requires_login()
def add():
    """
        Add a new expense
    """
    from openstudio.os_forms import OsForms
    response.title = T('Finance')
    response.subtitle = T('Add expense')
    response.view = 'general/only_content.html'

    return_url = add_edit_get_return_url()

    os_forms = OsForms()
    result = os_forms.get_crud_form_create(
        db.accounting_expenses,
        return_url,
    )

    form = result['form']
    back = os_gui.get_button('back', return_url)

    return dict(content=form,
                save=result['submit'],
                back=back)


@auth.requires_login()
def edit():
    """
    Edit expense
    request.vars['aeID'] is expected to be db.accounting_expenses.id
    """
    from openstudio.os_forms import OsForms

    response.title = T('Finance')
    response.subtitle = T('Edit expense')
    response.view = 'general/only_content.html'
    aeID = request.vars['aeID']

    return_url = add_edit_get_return_url()

    os_forms = OsForms()
    result = os_forms.get_crud_form_update(
        db.accounting_expenses,
        return_url,
        aeID
    )

    form = result['form']
    back = os_gui.get_button('back', return_url)

    return dict(content=form,
                save=result['submit'],
                back=back)
