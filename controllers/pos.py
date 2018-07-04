# -*- coding: utf-8 -*-

from general_helpers import set_form_id_and_get_submit_button

@auth.requires_login()
def index():
    print auth.user

    return dict()


def return_json(var=None):
    response.headers["Access-Control-Allow-Origin"] = "*"

    return dict(
        error=403,
        error_message=T("User is not logged in and needs to provide credentials"),
        location='http://dev.openstudioproject.com:8000/user/login?_next=/pos'
    )


@auth.requires_login(otherwise=return_json)
def get_logged_in():
    # response.headers["Access-Control-Allow-Origin"] = "http://localhost:8080"
    response.headers["Access-Control-Allow-Origin"] = "*"

    if not auth.is_logged_in():
        return True
    else:
        return False

