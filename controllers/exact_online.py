# -*- coding: utf-8 -*-
"""
    This file holds functions for Exact online integration
"""

@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def authorize():
    from openstudio.os_exact_online import OSExactOnline

    os_eo = OSExactOnline()
    api = os_eo.get_api()

    url = api.create_auth_request_url()
    redirect(url)


def oauth2_success():
    """

    :return:
    """
    from openstudio.os_exact_online import OSExactOnline
    code = request.vars['code']


    os_eo = OSExactOnline()
    api = os_eo.get_api()

    # Set transient api client access data like access code, token and expiry
    api.request_token(code)

    # Set authorized to true in database
    set_sys_property('exact_online_authorized', 'True')

    session.flash = T("Authorization success! You can now select a default division.")
    redirect(URL('divisions'))


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def divisions():
    """
    List divisions
    """
    def get_button_set_default(division_id):
        if division_id == selected_division:
            return DIV(
                os_gui.get_label(
                    'success',
                    T('Selected'),
                ),
                _class='pull-right'
            )

        else:
            return os_gui.get_button(
                'noicon',
                URL('division_set_default', vars={'division_id': division_id}),
                _class='pull-right',
                btn_class='btn-link',
                title=T("Select this division")
            )

    from ConfigParser import NoOptionError
    from openstudio.os_exact_online import OSExactOnline
    from openstudio.os_gui import OsGui

    response.title = T("Exact online")
    response.subtitle = T("Divisions")
    response.view = 'general/only_content.html'

    os_gui = OsGui()
    os_eo = OSExactOnline()
    api = os_eo.get_api()
    storage = os_eo.get_storage()
    try:
        selected_division = int(storage.get('transient', 'division'))
    except NoOptionError:
        selected_division = None

    division_choices, current_division = api.get_divisions()

    header = THEAD(TR(
        TH('Name'),
        TH('Exact ID'),
        TH()
    ))

    table = TABLE(header, _class="table table-striped table-hover")

    for division_id in division_choices:
        tr = TR(
            TD(division_choices[division_id]),
            TD(division_id),
            TD(get_button_set_default(division_id)) # buttons
        )

        table.append(tr)

    content = table

    back = os_gui.get_button(
        'back',
        URL('settings_integration', 'exact_online')
    )

    return dict(content=content,
                back=back)


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def logistics_items():
    """
    List items
    """
    from ConfigParser import NoOptionError
    from openstudio.os_exact_online import OSExactOnline

    from exactonline.exceptions import ObjectDoesNotExist
    from exactonline.resource import GET, POST, PUT, DELETE

    from openstudio.os_gui import OsGui

    response.title = T("Exact online")
    response.subtitle = T("Logistics Items")
    response.view = 'general/only_content.html'

    os_gui = OsGui()
    os_eo = OSExactOnline()
    api = os_eo.get_api()
    storage = os_eo.get_storage()
    try:
        selected_division = int(storage.get('transient', 'division'))
    except NoOptionError:
        selected_division = None

    items = api.logisticsitems.all()

    header = THEAD(TR(
        TH('Exact Item Code'),
        TH('Exact Item Description'),
        TH('Exact Item ID'),
    ))

    table = TABLE(header, _class="table table-striped table-hover")

    for item in items:
        tr = TR(
            TD(item['Code']),
            TD(item['Description']),
            TD(item['ID'])
        )

        table.append(tr)

    content = table

    back = os_gui.get_button(
        'back',
        URL('settings_integration', 'exact_online')
    )

    return dict(content=content,
                back=back)


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def division_set_default():
    """
    Set default division
    """
    from openstudio.os_exact_online import OSExactOnline

    division_id = request.vars['division_id']

    os_eo = OSExactOnline()
    api = os_eo.get_api()

    api.set_division(division_id)  # select ID of given division

    session.flash = T("Changed selected division")
    redirect(URL('divisions'))


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def relations():
    """

    :return:
    """
    from openstudio.os_exact_online import OSExactOnline

    os_eo = OSExactOnline()
    api = os_eo.get_api()

    relations = api.relations.all()

    return locals()

#
# def bankaccount_get():
#     eoID = "e984cfcb-80c9-46d7-b6b2-b2b6e60d09fb"
#
#     import pprint
#
#     from ConfigParser import NoOptionError
#     from openstudio.os_exact_online import OSExactOnline
#     from exactonline.http import HTTPError
#
#     os_eo = OSExactOnline()
#     storage = os_eo.get_storage()
#     api = os_eo.get_api()
#
#     # result = api.bankaccounts.all()
#     result = api.bankaccounts.filter(account=eoID)
#
#     pp = pprint.PrettyPrinter(depth=6)
#     pp.pprint(result)
#
#     return 'success'


# def bankaccount_create():
#     eoID = "e984cfcb-80c9-46d7-b6b2-b2b6e60d09fb"
#
#     from ConfigParser import NoOptionError
#     from openstudio.os_exact_online import OSExactOnline
#     from exactonline.http import HTTPError
#
#     os_eo = OSExactOnline()
#     storage = os_eo.get_storage()
#     api = os_eo.get_api()
#
#     bank_account_dict = {
#         'Account': eoID,
#         'BankAccount': 'NL21INGB0009355195'
#     }
#
#     result = api.bankaccounts.create(bank_account_dict)
#
#     pp = pprint.PrettyPrinter(depth=6)
#     pp.pprint(result)
#     return result


# def bankaccount_update():
#     eoID = "e984cfcb-80c9-46d7-b6b2-b2b6e60d09fb"
#
#     from ConfigParser import NoOptionError
#     from openstudio.os_exact_online import OSExactOnline
#     from exactonline.http import HTTPError
#
#     os_eo = OSExactOnline()
#     storage = os_eo.get_storage()
#     api = os_eo.get_api()
#
#     bank_account_dict = {
#         'Account': eoID,
#         'BankAccount': 'NL21INGB0009355195'
#     }
#
#     print api.bankaccounts.update(bank_account_dict)

#    api.restv1(POST('crm/BankAccounts', bank_account_dict))