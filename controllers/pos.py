# -*- coding: utf-8 -*-

from general_helpers import set_form_id_and_get_submit_button

# auth.settings.on_failed_authorization = URL('return_json_permissions_error')


@auth.requires_login()
def index():
    # print auth.user

    return dict()


def set_headers(var=None):
    response.headers["Access-Control-Allow-Origin"] = request.env.HTTP_ORIGIN
    response.headers["Access-Control-Allow-Credentials"] = "true"


def return_json_login_error(var=None):
    print 'return_json_login_error'
    print 'cookies:'
    print request.cookies

    set_headers()

    return dict(
        error=401,
        error_message=T("User is not logged in and needs to provide credentials"),
        location=URL('user', args='login', vars={'_next':"/pos"}, scheme=True, host=True)
        # location='http://dev.openstudioproject.com:8000/user/login?_next=/pos'
    )


def return_json_permissions_error():
    set_headers()
    print 'return_json_permissions_error'
    print 'cookies:'
    print request.cookies

    try:
        # Dev
        location = request.env.HTTP_ORIGIN + '/#/permissions_error'
    except TypeError:
        # Live
        location = request.env.wsgi_url_scheme + '://' + request.env.http_host + '/pos#/permissions_error'
        print location

    return dict(
        error=403,
        error_message=T("You don't have the permissions required to perform this action"),
        location=location

    )


def is_authorized(permission):
    """
    :param permission: in form auth.has_permission('read', 'permission')
    :return: None
    """
    return (auth.has_membership(group_id="Admins") or
            permission)


@auth.requires_login(otherwise=return_json_login_error)
def get_logged_in():
    set_headers()

    print 'cookies:'
    print request.cookies

    return auth.is_logged_in()


@auth.requires_login(otherwise=return_json_login_error)
def get_user():
    set_headers()

    # if not is_authorized(auth.has_permission('read', 'auth_user')):
    #     return return_json_permissions_error()
    # Permissions error

    print 'cookies:'
    print request.cookies

    # get group membership
    membership = db.auth_membership(user_id=auth.user.id)
    group_id = membership.group_id

    print group_id

    # get group permissions
    query = (db.auth_permission.group_id == group_id) & \
            (db.auth_permission.record_id == 0)
    rows = db(query).select(db.auth_permission.name,
                            db.auth_permission.table_name)
    permissions = {}
    for row in rows:
        print row
        if row.table_name in permissions:
            permissions[row.table_name].append(row.name)
        else:
            permissions[row.table_name] = [row.name]

    print permissions


    return dict(user=auth.user,
                permissions=permissions)
