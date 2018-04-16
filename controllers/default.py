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

from openstudio.openstudio import OsMail

import datetime

@auth.requires_login()
def index():
    # if not request.user_agent()['is_mobile']:
    #     session.flash = T("Welcome to OpenStudio!")

    if auth.user.login_start == 'profile':
        redirect(URL('profile', 'index'))

    if auth.user.login_start == 'selfcheckin':
        redirect(URL('selfcheckin', 'index'))

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
    auth.messages.verify_email = osmail.render_email_template('email_template_sys_verify_email', return_html=True)
    # auth.messages.reset_password = 'Click on the link %(link)s to reset your password'
    auth.messages.reset_password = osmail.render_email_template('email_template_sys_reset_password', return_html=True)
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
    form=auth()

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
        response.view = 'default/user_login.html'
        #auth.settings.formstyle = 'divs'
        user_registration_set_visible_fields()
        #db.auth_user.password.requires=IS_STRONG()

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

        location = ''
        if session.show_location:
            location = DIV(LABEL(form.custom.label.school_locations_id),
                           form.custom.widget.school_locations_id,
                           _class='form-group')

        privacy_notice = ''
        terms_and_conditions = ''
        link_pp = ''
        link_tc = ''
        if organization:
            tc_pp_links = DIV(' ', _class="form-group")
            if organization['TermsConditionsURL']:
                tc_pp_links.append(A(T('Terms and conditions'),
                                     _href=organization['TermsConditionsURL'],
                                     _target="_blank"))
                terms_and_conditions = DIV(INPUT(_type="checkbox",
                                                 _id="accept_terms_and_conditions",
                                                 _class="iCheck-line-aero"), ' ',
                                           LABEL(T("I accept the Terms and conditions")),
                                           _class="form-group")

            if organization['PrivacyNoticeURL']:
                tc_pp_links.append(SPAN(
                    SPAN(' ', XML('&bull;'), ' ', _class='grey'),
                    A(T('Privacy notice'),
                      _href=organization['PrivacyNoticeURL'],
                      _target="_blank")))
                privacy_notice = DIV(INPUT(_type="checkbox",
                                           _id='accept_privacy_policy',
                                           _class="iCheck-line-aero"), ' ',
                                     LABEL(T("I accept the privacy notice")),
                                     _class="form-group")

        complete_data = DIV(INPUT(_type="checkbox",
                                  _id='data_true_and_complete',
                                  _class="iCheck-line-aero"), ' ',
                             LABEL(T("I confirm that the data entered in this form is true and complete")),
                             _class="form-group")

        form = DIV(
            H4(T('Register'), _class='grey text-center no-margin-top'),
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
            tc_pp_links,
            terms_and_conditions,
            privacy_notice,
            complete_data,
            BR(),
            A(T('Cancel'),
              _href=URL(args='login'),
              _class='btn btn-default',
              _title=T('Back to login')),
            DIV(form.custom.submit, _class='pull-right'),
            form.custom.end)

    reset_passwd = ''
    register = ''
    self_checkin  = ''
    error_msg = ''

    # set logo
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

    logo_login = DIV(logo_img, logo_text,
                     _class=logo_class)

    # set email placeholder
    if 'login' in request.args or 'request_reset_password' in request.args:
        email = form.element('#auth_user_email')
        email['_placeholder'] = T("Email...")

    if 'login' in request.args:
        response.view = 'default/user_login.html'

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
            BR(),
            HR(),
            )

        if not 'request_reset_password' in auth.settings.actions_disabled:
            reset_passwd = A(T('Lost password?'),
                              _href=URL(args='request_reset_password'))


        if not 'register' in auth.settings.actions_disabled:
            register = A(T("I don't have an account yet"),
                          _href=URL(args='register'))


    if 'request_reset_password' in request.args or \
       'reset_password' in request.args:
        submit = form.element('input[type=submit]')
        submit['_value'] = T('Reset password')


    if 'request_reset_password' in request.args:
        response.view = 'default/user_login.html'

        cancel = A(T("Cancel"),
                   _href=URL('/user', args='login'),
                   _class='btn btn-default')
        form = DIV(
            form.custom.begin,
            DIV(LABEL('Request reset password'),
                form.custom.widget.email, _class='form-group'),
            DIV(form.custom.submit, _class='pull-right'),
            cancel,
            form.custom.end)

    if 'reset_password' in request.args:
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


    if 'change_password' in request.args:
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
            H4(T('Change password'), _class='grey text-center no-margin-top'),
            form.custom.begin,
            os_gui.get_form_group(form.custom.label.old_password, form.custom.widget.old_password),
            os_gui.get_form_group(form.custom.label.new_password, form.custom.widget.new_password),
            os_gui.get_form_group(form.custom.label.new_password2, form.custom.widget.new_password2),
            DIV(form.custom.submit, _class='pull-right'),
            cancel,
            form.custom.end
        )


    return dict(form=form,
                content=form,
                error_msg=error_msg,
                reset_passwd=reset_passwd,
                register=register,
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
