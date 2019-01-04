# -*- coding: utf-8 -*-
# this file is released under the gplv2 (or later at your choice) license

#########################################################################
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

from general_helpers import User_helpers
from general_helpers import max_string_length

from openstudio.os_mail import OsMail

import datetime

@auth.requires_login()
def index():
    # if not request.user_agent()['is_mobile']:
    #     session.flash = T("Welcome to OpenStudio!")

    if auth.user.login_start == 'profile':
        redirect(URL('profile', 'index'))

    if auth.user.login_start == 'selfcheckin':
        redirect(URL('selfcheckin', 'index'))

    if auth.user.login_start == 'ep':
        redirect(URL('ep', 'index'))

    user_helpers = User_helpers()
    if user_helpers.check_read_permission('pinboard', auth.user.id):
        redirect(URL('pinboard', 'index'))
    else:
        redirect(URL('blank'))


@auth.requires_login()
def blank():
    """
        Returns a blank page
    """
    response.view = 'general/only_content.html'

    return dict(content = T('Welcome to OpenStudio'))


####### Don't mess with the functions below ##########

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    # check if someone is looking for profile
    if 'profile' in request.args:
        redirect(URL('profile', 'index'))

    # Send styles email messages from auth
    osmail = OsMail()
    auth.messages.verify_email = osmail.render_email_template(
        'sys_verify_email',
        return_html=True
    )
    # auth.messages.reset_password = 'Click on the link %(link)s to reset your password'
    auth.messages.reset_password = osmail.render_email_template(
        'sys_reset_password',
        return_html=True
    )
    # Log registration accepted terms (if any)

    auth.settings.register_onaccept.append(user_register_log_acceptance)
    auth.settings.login_onaccept.append(user_set_last_login)

    ## Create auth form
    if session.show_location: # check if we need a requirement for the school_locations_id field for customers
        loc_query = (db.school_locations.AllowAPI == True)
        db.auth_user.school_locations_id.requires = IS_IN_DB(db(loc_query),
                                                             'school_locations.id',
                                                             '%(Name)s',
                                                             error_message=T('Please select a location'),
                                                             zero=T('Please select a location...'))
    # actually create auth form
    # Set nicer error messages for name fields
    db.auth_user.first_name.requires = IS_NOT_EMPTY(
        error_message = T("Please enter your first name")
    )
    db.auth_user.last_name.requires = IS_NOT_EMPTY(
        error_message = T("Please enter your last name")
    )

    form_login = ''
    login_link = ''
    login_title = ''
    login_message = ''
    form_register = ''
    register_link = ''
    register_title = ''
    reset_passwd = ''


    self_checkin  = ''
    error_msg = ''

    try:
        organization = ORGANIZATIONS[ORGANIZATIONS['default']]
        company_name = organization['Name']
        has_terms = True if organization['TermsConditionsURL'] else False
        has_privacy_notice = True if organization['PrivacyNoticeURL'] else False
    except:
        company_name = ''
        organization = False
        has_terms = False
        has_privacy_notice = False

    if 'register' in request.args:
        # Enforce strong passwords
        db.auth_user.password.requires.insert(0, IS_STRONG())
        form = auth()

        register_title = T("Create your account")
        login_title = T("Already have an account?")
        login_link = A(T("Click here to log in"),
                       _href=URL(args='login'))
        login_message = DIV(
            B("Can't register?"), BR(),
            T("In case you can't register because your email address already has an account, click"), ' ',
            A(T("here"),
              _href=URL(args='request_reset_password')), ' ',
            T("to request a new password."), BR(), BR(),
        )
        response.view = 'default/user_login.html'
        user_registration_set_visible_fields()

        first_name = form.element('#auth_user_first_name')
        first_name['_placeholder'] = T("First name...")
        last_name = form.element('#auth_user_last_name')
        last_name['_placeholder'] = T("Last name...")
        email = form.element('#auth_user_email')
        email['_placeholder'] = T("Email...")
        password = form.element('#auth_user_password')
        password['_placeholder'] = T("Password...")
        password2 = form.element('#auth_user_password_two')
        password2['_placeholder'] = T("Repeat Password...")
        submit = form.element('input[type=submit]')
        submit['_value'] = T('Create account')

        location = ''
        if session.show_location:
            location = DIV(LABEL(form.custom.label.school_locations_id),
                           form.custom.widget.school_locations_id,
                           _class='form-group')

        accept_ul = UL(_id='accept_ul')
        accept_ul.append(
            LI(T('Confirm that the data above is true and complete'))
        )
        if organization:
            if organization['TermsConditionsURL']:
                accept_ul.append(SPAN(
                    T('Agree to the'), ' ',
                    A(T('Terms and conditions'),
                      _href=organization['TermsConditionsURL'],
                      _target="_blank")))

            if organization['PrivacyNoticeURL']:
                accept_ul.append(SPAN(
                    T('Accept the'), ' ',
                    A(T('Privacy notice'),
                      _href=organization['PrivacyNoticeURL'],
                      _target="_blank")))


        form = DIV(
            form.custom.begin,
            DIV(LABEL(form.custom.label.first_name),
                form.custom.widget.first_name,
                _class='form-group'),
            DIV(LABEL(form.custom.label.last_name),
                form.custom.widget.last_name,
                _class='form-group'),
            DIV(LABEL(form.custom.label.email),
                form.custom.widget.email,
                _class='form-group'),
            DIV(LABEL(form.custom.label.password),
                form.custom.widget.password,
                _class='form-group'),
            DIV(LABEL(form.custom.label.password_two),
                form.custom.widget.password_two,
                _class='form-group'),
            location,
            SPAN(T('By creating an account I'), _class='bold'),
            accept_ul,
            BR(),
            A(T('Cancel'),
              _href=URL(args='login'),
              _class='btn btn-default',
              _title=T('Back to login')),
            DIV(form.custom.submit, _class='pull-right'),
            form.custom.end)

        form_register = form

    # set logo
    logo_login = user_get_logo_login()


    if 'logout' in request.args or 'not_authorized' in request.args or 'verify_email' in request.args:
        form = auth()


    if 'login' in request.args:
        form = auth()

        response.view = 'default/user_login.html'
        login_title = T("Log in")
        register_title = T("Create your account")

        auth.messages.login_button = T('Sign In')

        email = form.element('#auth_user_email')
        email['_placeholder'] = T("Email...")
        password = form.element('#auth_user_password')
        password['_placeholder'] = T("Password...")

        submit = form.element('input[type=submit]')
        submit['_value'] = T('Sign In')

        form = DIV(
            form.custom.begin,
            DIV(form.custom.widget.email,
                SPAN(_class='glyphicon glyphicon-envelope form-control-feedback'),
                _class='form-group has-feedback'),
            DIV(form.custom.widget.password,
                SPAN(_class='glyphicon glyphicon-lock form-control-feedback'),
                _class='form-group has-feedback'),
            LABEL(form.custom.widget.remember_me, ' ', form.custom.label.remember_me,
                  _id='label_remember'),
            DIV(form.custom.submit, _class='pull-right'),
            form.custom.end,
            )

        if not 'request_reset_password' in auth.settings.actions_disabled:
            reset_passwd = A(T('Lost password?'),
                              _href=URL(args='request_reset_password'))


        if not 'register' in auth.settings.actions_disabled:
            form_register = SPAN(
                T("Are you new here and would you like to create an account?"), BR(),
                T("Please click the button below to get started."), BR(),
            )
            register_link = A(T("Create your account"),
                               _href=URL(args='register',
                                         vars=request.vars),
                               _class='btn btn-primary btn-create_your_account')
        form_login = form


    if 'request_reset_password' in request.args:
        form = auth()
        response.view = 'default/user_login.html'

        cancel = A(T("Cancel"),
                   _href=URL('/user', args='login'),
                   _class='btn btn-default')
        form = DIV(
            form.custom.begin,
            DIV(form.custom.widget.email, _class='form-group'),
            DIV(form.custom.submit, _class='pull-right'),
            cancel,
            form.custom.end)

        form_login = form
        login_title = T("Reset password")

        register_title = T("Info")
        register_link = SPAN(
            T("After entering your email address and clicking the Reset password button"), ' ',
            T("you should receive an email with a link to reset your password within a few minutes."), ' ',
            T("In case you don't receive an email, please check your spam folder."), BR(), BR(),
            A(T("Click here to log in"),
              _href=URL(args="login"))
        )

    # set email placeholder
    if 'login' in request.args or 'request_reset_password' in request.args:
        email = form.element('#auth_user_email')
        email['_placeholder'] = T("Email...")

    if 'reset_password' in request.args:
        # Enforce strong passwords
        db.auth_user.password.requires.insert(0, IS_STRONG())
        form = auth()

        response.view = 'default/user_login.html'

        passwd = form.element('#no_table_new_password')
        passwd['_placeholder'] = T("New password...")
        passwd2 = form.element('#no_table_new_password2')
        passwd2['_placeholder'] = T("Repeat new password...")

        form = DIV(
            form.custom.begin,
            os_gui.get_form_group(form.custom.label.new_password, form.custom.widget.new_password),
            os_gui.get_form_group(form.custom.label.new_password2, form.custom.widget.new_password2),
            form.custom.submit,
            form.custom.end)

        form_login = form
        login_title = T("Reset password")
        register_title = T("Info")
        register_link = SPAN(
            T("After setting a new password, you will be logged in automatically."), ' ',
            T("Please use your new password for future logins."), BR(), BR(),
            A(T("Click here to log in"),
              _href=URL(args="login"))
        )

        
    if 'request_reset_password' in request.args or \
       'reset_password' in request.args:
        submit = form.element('input[type=submit]')
        submit['_value'] = T('Reset password')


    if 'change_password' in request.args:
        # Enforce strong passwords
        db.auth_user.password.requires.insert(0, IS_STRONG())
        form = auth()

        response.view = 'default/user_login.html'
        response.title = T('Change password')

        oldpwd = form.element('#no_table_old_password')
        oldpwd['_placeholder'] = T('Old password...')
        passwd = form.element('#no_table_new_password')
        passwd['_placeholder'] = T("New password...")
        passwd2 = form.element('#no_table_new_password2')
        passwd2['_placeholder'] = T("Repeat password...")

        cancel = A(T('Cancel'),
                   _href=URL('profile', 'index'),
                   _class='btn btn-default')

        form = DIV(
            form.custom.begin,
            os_gui.get_form_group(form.custom.label.old_password, form.custom.widget.old_password),
            os_gui.get_form_group(form.custom.label.new_password, form.custom.widget.new_password),
            os_gui.get_form_group(form.custom.label.new_password2, form.custom.widget.new_password2),
            DIV(form.custom.submit, _class='pull-right'),
            cancel,
            form.custom.end
        )

        form_login = form
        login_title = T("Change password")


    return dict(form=form,
                form_login=form_login,
                form_register=form_register,
                content=form,
                error_msg=error_msg,
                reset_passwd=reset_passwd,
                register_link=register_link,
                register_title=register_title,
                login_link=login_link,
                login_title=login_title,
                login_message=login_message,
                self_checkin=self_checkin,
                company_name=company_name,
                has_organization=True if organization else False,
                has_terms=has_terms,
                has_privacy_notice=has_privacy_notice,
                logo_login=logo_login)


def user_set_last_login(form):
    """
        Sets last_login field for a user
    """
    email = form.vars.email

    row = db.auth_user(email=email)
    row.last_login = datetime.datetime.now()
    row.update_record()


def user_registration_set_visible_fields(var=None):
    """
        Restricts number of visible fields when registering for an account
    """
    for field in db.auth_user:
        field.readable = False
        field.writable = False

    visible_fields = [
        db.auth_user.first_name,
        db.auth_user.last_name,
        db.auth_user.email,
        db.auth_user.password
    ]

    for field in visible_fields:
        field.readable = True
        field.writable = True


def user_register_log_acceptance(form):
    """
        Log acceptance of general terms, privacy policy and true data
    """
    from openstudio.os_customer import Customer

    cuID = form.vars.id
    customer = Customer(cuID)

    reg_url = URL('default', 'user', args='register', scheme=True, host=True)

    organization = ORGANIZATIONS[ORGANIZATIONS['default']]
    if organization:
        user_register_log_acceptance_terms_and_conditions(customer,
                                                          organization,
                                                          reg_url)
        user_register_log_acceptance_privacy_notice(customer,
                                                    organization,
                                                    reg_url)
    user_register_log_acceptance_true_data(customer,
                                           reg_url)


def user_lockout():
    """
    Page to display when a user is locked out
    :return:
    """
    response.title = T("Your account has been locked")

    content = DIV(
        T("Too many invalid login attempts have been detected."), BR(),
        T("For security purposes your account has been locked."), BR(), BR(),
        T("Please try again in 20 minutes."), BR(), BR(),
        A(T("Back to login"),
          _href=URL('user', args=['login'])),
        BR(), BR(),
        _class='center'
    )

    logo_login = user_get_logo_login()

    return dict(
        content=content,
        logo_login=logo_login
    )


def user_get_logo_login(var=None):
    branding_logo = os.path.join(request.folder,
                                 'static',
                                 'plugin_os-branding',
                                 'logos',
                                 'branding_logo_login.png')
    if os.path.isfile(branding_logo):
        logo_img = IMG(_src=URL('static',
                                'plugin_os-branding/logos/branding_logo_login.png'))
        logo_text = ''
        logo_class = 'logo_login'
    else:
        logo_img = ''
        logo_text = SPAN(B('Open'), 'Studio')

        logo_class = ''

    return DIV(logo_img, logo_text, _class=logo_class)


def user_register_log_acceptance_terms_and_conditions(customer, organization, reg_url):
    """
    :param customer: Customer object
    :param organization: the default organization
    :param reg_url: url of registration form
    :return: None
    """
    if organization['TermsConditionsURL']:
        customer.log_document_acceptance(
            document_name=T("Terms and Conditions"),
            document_description=organization['TermsConditionsURL'],
            document_version=organization.get('TermsConditionsVersion', None),
            document_url=reg_url
        )


def user_register_log_acceptance_privacy_notice(customer, organization, reg_url):
    """
    :param customer: Customer object
    :param organization: the default organization
    :param reg_url: url of registration form
    :return: None
    """
    if organization['PrivacyNoticeURL']:
        customer.log_document_acceptance(
            document_name=T("Privacy Notice"),
            document_description=organization['PrivacyNoticeURL'],
            document_version=organization.get('PrivacyNoticeVersion', None),
            document_url=reg_url
        )


def user_register_log_acceptance_true_data(customer, reg_url):
    """
    :param customer: Customer object
    :param reg_url: url of registration form
    :return: None
    """
    customer.log_document_acceptance(
        document_name=T("Registration form"),
        document_description=T("True and complete data"),
        document_url=reg_url
    )


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()
