# -*- coding: utf-8 -*-
"""
    This file holds functions for Exact online integration
"""
def get_api(var=None):
    """
    Return ExactAPI linked to config and token storage
    """
    import os
    from exactonline.api import ExactApi
    from exactonline.exceptions import ObjectDoesNotExist

    # from openstudio.os_exact_online import ExactOnlineStorage

    # storage = ExactOnlineStorage()

    from exactonline.storage import IniStorage

    class MyIniStorage(IniStorage):
        def get_response_url(self):
            "Configure your custom response URL."
            return self.get_base_url() + '/exact_online/oauth2_success/'


    import os

    config_file = os.path.join(
        request.folder,
        'private',
        'eo_config.ini'
    )

    storage = MyIniStorage(config_file)

    return ExactApi(storage=storage)


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def authorize():
    api = get_api()

    url = api.create_auth_request_url()
    redirect(url)


def oauth2_success():
    """

    :return:
    """
    code = request.vars['code']
    api = get_api()

    # Set transient api client access data like access code, token and expiry
    api.request_token(code)

    session.flash = T("Authentication success!")
    redirect(URL('divisions'))


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'settings'))
def divisions():
    """
    Set default division
    """
    api = get_api()

    division_choices, current_division = api.get_divisions()

    return locals()


    #api.relations.all()

    # division_choices, current_division = api.get_divisions()
    #
    # print division_choices
    # print current_division
