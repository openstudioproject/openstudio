# -*- coding: utf-8 -*-

from general_helpers import set_form_id_and_get_submit_button

@auth.requires_login()
def index():
    print auth.user

    return dict()
