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
    return URL('index')


@auth.requires_login()
def add():
    """
        Add a new category
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

    # content = DIV(
    #     H4(T('Add category')),
    #     form
    # )

    return dict(content=form,
                save=result['submit'],
                back=back)


@auth.requires_login()
def edit():
    """
        Edit a category
        request.vars['scID'] is expected to be db.shop_categories.id
    """
    from openstudio.os_forms import OsForms

    response.title = T('Shop')
    response.subtitle = T('Catalog')
    response.view = 'general/tabs_menu.html'
    scID = request.vars['scID']

    return_url = shop_categories_get_return_url()

    os_forms = OsForms()
    result = os_forms.get_crud_form_update(
        db.shop_categories,
        return_url,
        scID
    )

    form = result['form']
    back = os_gui.get_button('back', return_url)
    menu = catalog_get_menu('categories')

    content = DIV(
        H4(T('Edit category')),
        form
    )

    return dict(content=content,
                save=result['submit'],
                back=back,
                menu=menu)
