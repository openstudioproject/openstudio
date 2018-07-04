# -*- coding: utf-8 -*-

from general_helpers import set_form_id_and_get_submit_button

@auth.requires_login()
def index():
    # print auth.user

    return dict()


def set_pos_headers(var=None):
    response.headers["Access-Control-Allow-Origin"] = request.env.HTTP_ORIGIN
    response.headers["Access-Control-Allow-Credentials"] = "true"


def return_json_error(var=None):
    print 'return_json_error'
    print 'cookies:'
    print request.cookies

    set_pos_headers()

    return dict(
        error=403,
        error_message=T("User is not logged in and needs to provide credentials"),
        location='http://dev.openstudioproject.com:8000/user/login?_next=/pos'
    )


@auth.requires_login(otherwise=return_json_error)
def get_logged_in():
    set_pos_headers()

    print 'cookies:'
    print request.cookies

    return auth.is_logged_in()
