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

    from openstudio.os_exact_online import OSExactOnline
    from openstudio.os_gui import OsGui

    response.title = T("Exact online")
    response.subtitle = T("Divisions")
    response.view = 'general/only_content.html'

    os_gui = OsGui()
    os_eo = OSExactOnline()
    api = os_eo.get_api()
    storage = os_eo.get_storage()
    selected_division = int(storage.get('transient', 'division'))

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