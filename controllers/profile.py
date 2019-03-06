# -*- coding: utf-8 -*-
"""
    This file provides the customer portal for OpenStudio
"""
from openstudio.os_order import Order
from openstudio.os_invoice import Invoice


@auth.requires_login()
def index():
    """
        Main page for customers portal
    """
    from openstudio.os_customer import Customer

    response.title = T('Welcome')
    response.subtitle = auth.user.display_name

    upcoming_workshops = ''
    classcards = ''

    session.profile_class_cancel_confirm_back = 'profile_index'
    session.profile_subscription_credits_back = 'profile_index'

    # verification required
    verification_required = index_get_verification_required()

    # announcements
    announcements = index_get_announcements()

    # customer content
    customer_content = DIV(_class='row')
    cc_left = DIV(_class='col-md-6')
    cc_right = DIV(_class='col-md-6')
    features = db.customers_profile_features(1)

    customer = Customer(auth.user.id)

    if features.Classes:
        upcoming_classes = index_get_upcoming_classes(customer)
        cc_left.append(DIV(upcoming_classes, _class='no-padding-left no-padding-right col-md-12'))

    if features.Workshops:
        upcoming_events = index_get_upcoming_events(customer)
        cc_right.append(DIV(upcoming_events, _class='no-padding-left no-padding-right col-md-12'))

    if features.Classcards:
        classcards = index_get_classcards(customer)
        cc_left.append(DIV(classcards, _class='no-padding-left no-padding-right col-md-12'))

    if features.Subscriptions:
        subscriptions = index_get_subscriptions(customer)
        cc_right.append(DIV(subscriptions, _class='no-padding-left no-padding-right col-md-12'))

    if features.Memberships:
        memberships = index_get_memberships(customer)
        cc_left.append(DIV(memberships, _class='no-padding-left no-padding-right col-md-12'))


    customer_content.append(cc_left)
    customer_content.append(cc_right)

    content = DIV(
        verification_required,
        announcements,
        customer_content
    )

    email_verified = index_get_email_verified()

    return dict(
        content=content,
        header_tools=email_verified,
    )


def index_get_email_verified(var=None):
    """

    """
    auth_user = db.auth_user(auth.user.id)
    if not auth_user.registration_key:
        return SPAN(
            SPAN(os_gui.get_fa_icon('fa-check'),
                 _class='text-green'),
            ' ',
            T("Email verified")
        )
    else:
        return SPAN(
            SPAN(os_gui.get_fa_icon('fa-times'),
                 _class='text-red'),
            ' ',
            T("Email not verified")
        )


def index_get_verification_required(var=None):
    """
        Get verification required
    """
    content = DIV(_class='row')

    auth_user = db.auth_user(auth.user.id)
    if not auth_user.registration_key:
        return ''

    content = DIV(
        T("Welcome!"), ' ',
        T("Soon you'll receive an email from us asking to verify your email address."), ' ',
        T("Please take the time to click the link in the email so we can ensure that you address is correct."), BR(),
        T("In case there is ever a reason for us to contact you concerning your order, we would like to be able to do so."), BR(), BR(),
        T("No email within 15 minutes? Please check your spam folder or contact us in case you need any assistance."), BR(), BR(),

        T("Thank you")
    )

    return os_gui.get_box(T('Email address not yet verified'),
                          content,
                          box_class='box-success',
                          with_border=False,
                          show_footer=False,
                          footer_padding=False)


def index_get_announcements(var=None):
    """
        Get announcements
    """
    content = DIV(_class='row')

    query = (db.customers_profile_announcements.PublicAnnouncement == True) & \
            (db.customers_profile_announcements.Startdate <= TODAY_LOCAL) & \
            ((db.customers_profile_announcements.Enddate >= TODAY_LOCAL) |
             (db.customers_profile_announcements.Enddate == None))

    rows = db(query).select(db.customers_profile_announcements.ALL,
                            orderby=~db.customers_profile_announcements.Sticky |\
                                    db.customers_profile_announcements.Startdate |\
                                    db.customers_profile_announcements.Title)

    if not len(rows):
        return ''

    for row in rows.render():
        announcement = DIV(P(
            B(row.Title), BR(),
            row.Announcement),
            _class='col-md-12')

        content.append(announcement)



    return os_gui.get_box(T('Good to know'),
                          content,
                          box_class='box-solid',
                          with_border=False,
                          show_footer=False,
                          footer_padding=False)


def index_get_upcoming_classes(customer):
    """
    :param customer: openstudio.py Customer object
    :return: list of upcoming classes for a customer
    """
    from openstudio.os_class_attendance import ClassAttendance

    rows = customer.get_classes_attendance_rows(upcoming=True)

    if not rows:
        table = SPAN(T('No upcoming classes.'), BR(), BR(),
                     T("Click "),
                     A(T("here"),
                       _href=URL('shop', 'classes')), ' ',
                     T("to book a class."))
    else:
        header = THEAD(TR(TH(T('Date')),
                          TH(T('Time')),
                          TH(T('Location')),
                          TH(T('Class')),
                          TH()))

        table = TABLE(header, _class='table table-condensed')

        for i, row in enumerate(rows):
            repr_row = list(rows[i:i + 1].render())[0]

            if row.classes_attendance.BookingStatus == 'cancelled':
                continue

            cancel = ''
            clatt = ClassAttendance(row.classes_attendance.id)
            if clatt.get_cancellation_possible() and not row.classes_attendance.BookingStatus == 'cancelled':
                cancel = A(T("Cancel"),
                           _href=URL('class_cancel_confirm', vars={'clattID': row.classes_attendance.id}),
                           _class='pull-right',
                           _title=T('Cancel booking'))

            tr = TR(TD(repr_row.classes_attendance.ClassDate),
                    TD(repr_row.classes.Starttime),
                    TD(repr_row.classes.school_locations_id),
                    TD(repr_row.classes.school_classtypes_id),
                    TD(cancel))

            table.append(tr)


    box_tools = ''

    if len(customer.get_reservations_rows(
            TODAY_LOCAL + datetime.timedelta(days=14),
            recurring_only=True)) > 0:
        box_tools = A(T('Manage enrollments'),
                      _href=URL('profile', 'enrollments'),
                      _class='btn btn-box-tool')


    return os_gui.get_box(T('My classes'),
                          table,
                          box_class='box-solid',
                          box_tools=box_tools,
                          with_border=False,
                          show_footer=True,
                          footer_padding=False,
                          footer_content=DIV(A(SPAN(os_gui.get_fa_icon('fa-history'), ' ', T('All')),
                                               _href=URL('profile', 'classes'),
                                               _class='btn btn-link pull-right',
                                               _title=T('List all classes')),
                                             _class='center'))


def index_get_upcoming_events(customer):
    """
        :return: List of workshops for customer
    """
    rows = customer.get_workshops_rows(upcoming=True)

    if not rows:
        table = SPAN(T('No upcoming events.'), BR(), BR(),
                     T("Click "),
                     A(T("here"),
                       _href=URL('shop', 'events')), ' ',
                     T("to book an event."))
    else:
        header = THEAD(TR(TH(T('Date')),
                          TH(T('Event')),
                          TH(T('Location')),
                          ))

        table = TABLE(header, _class='table table-condensed')

        for i, row in enumerate(rows):
            repr_row = list(rows[i:i + 1].render())[0]

            tr = TR(TD(repr_row.workshops.Startdate, BR(),
                       SPAN(repr_row.workshops.Starttime, _class="grey")),
                    TD(repr_row.workshops.Name, BR(),
                       SPAN(repr_row.workshops_products.Name, _class="grey")),
                    TD(repr_row.workshops.school_locations_id))

            table.append(tr)


    return os_gui.get_box(T('My events'),
                          table,
                          box_class='box-solid',
                          with_border=False,
                          show_footer=True,
                          footer_padding=False,
                          footer_content=DIV(A(SPAN(os_gui.get_fa_icon('fa-history'), ' ', T('All')),
                                               _href=URL('profile', 'events'),
                                               _class='btn btn-link pull-right',
                                               _title=T('List all workshops')),
                                             _class='center'))


def index_get_classcards(customer):
    """
    :return: list of current classcards for a customer
    """
    rows = customer.get_classcards(TODAY_LOCAL, from_cache=False)

    if not rows:
        table = SPAN(T("No current class cards."), BR(), BR(),
                     T("Click "),
                     A(T("here"),
                       _href=URL('shop', 'classcards')), ' ',
                     T("to buy a class card."))
    else:
        header = THEAD(TR(TH(T('Card')),
                          TH(T('Expires')),
                          TH(T('Classes')),
                          ))

        table = TABLE(header, _class='table table-condensed')
        for i, row in enumerate(rows):
            repr_row = list(rows[i:i+1].render())[0]

            remaining = classcard_get_remaining(row)

            tr = TR(TD(row.school_classcards.Name),
                    TD(row.customers_classcards.Enddate),
                    TD(remaining),
                    TD(classcard_get_link_info(row)))

            table.append(tr)

    return os_gui.get_box(T('My Classcards'),
                          table,
                          box_class='box-solid',
                          with_border=False,
                          show_footer=True,
                          footer_padding=False,
                          footer_content=DIV(A(SPAN(os_gui.get_fa_icon('fa-history'), ' ', T('All')),
                                               _href=URL('profile', 'classcards'),
                                               _class='btn btn-link pull-right',
                                               _title=T('List all classcards')),
                                             _class='center'))


def index_get_subscriptions(customer):
    """
    :return: list current subscriptions for a customer
    """
    rows = customer.get_subscriptions_on_date(TODAY_LOCAL, from_cache=False)

    if not rows:
        table = SPAN(T('No current subscriptions.'), BR(), BR(),
                     T("Click "),
                     A(T("here"),
                       _href=URL('shop', 'subscriptions')), ' ',
                     T("to get a subscription."))
    else:
        header = THEAD(TR(TH(T('#')),
                          TH(T('Subscription')),
                          TH(T('Start')),
                          TH(T('Credits')),
                          TH(),
                          ))
        table = TABLE(header, _class='table table-condensed')
        for i, row in enumerate(rows):
            repr_row = list(rows[i:i+1].render())[0]

            credits = subscription_get_link_credits(row)
            info = subscription_get_link_info(row)

            tr = TR(TD(row.customers_subscriptions.id),
                    TD(row.school_subscriptions.Name),
                    TD(repr_row.customers_subscriptions.Startdate),
                    TD(credits),
                    TD(info))

            table.append(tr)

    return os_gui.get_box(T('My Subscriptions'),
                          table,
                          box_class='box-solid',
                          with_border=False,
                          show_footer=True,
                          footer_padding=False,
                          footer_content=DIV(A(SPAN(os_gui.get_fa_icon('fa-history'), ' ', T('All')),
                                               _href=URL('profile', 'subscriptions'),
                                               _class='btn btn-link pull-right'),
                                               _title=T('List all subscriptions'),
                                             _class='center'))


def index_get_memberships(customer):
    """
    :return: list current subscriptions for a customer
    """
    rows = customer.get_memberships_on_date(TODAY_LOCAL, from_cache=False)

    if not rows:
        table = SPAN(T('No current memberships.'), BR(), BR(),
                     T("Click "),
                     A(T("here"),
                       _href=URL('shop', 'memberships')), ' ',
                     T("to get a membership."))
    else:
        header = THEAD(TR(TH(T('#')),
                          TH(T('Membership')),
                          TH(T('Start')),
                          TH(),
                          ))
        table = TABLE(header, _class='table table-condensed')
        for i, row in enumerate(rows):
            repr_row = list(rows[i:i+1].render())[0]

            tr = TR(TD(row.id),
                    TD(repr_row.school_memberships_id),
                    TD(repr_row.Startdate),
                    TD())

            table.append(tr)

    return os_gui.get_box(T('My Memberships'),
                          table,
                          box_class='box-solid',
                          with_border=False,
                          show_footer=True,
                          footer_padding=False,
                          footer_content=DIV(A(SPAN(os_gui.get_fa_icon('fa-history'), ' ', T('All')),
                                               _href=URL('profile', 'memberships'),
                                               _class='btn btn-link pull-right'),
                                               _title=T('List all memberships'),
                                             _class='center'))


def subscription_get_link_credits(row):
    """
        Returns total number of credits for a subscription
    """
    cs = CustomerSubscription(row.customers_subscriptions.id)
    if cs.ssu.Unlimited == True:
        link = SPAN(T("Unlimited"), _class='grey')

    else:
        credits = cs.get_credits_balance()
        link =  A(credits,
                  _href=URL('subscription_credits', vars={'csID':row.customers_subscriptions.id}))
    return link


def subscription_get_link_info(row):
    """
        Returns info link for a subscription
    """
    csID = row.customers_subscriptions.id

    return A(os_gui.get_fa_icon('fa-info-circle'),
             _href=URL('subscription_info', vars={'csID':csID}),
             _title=T('Subscription details'),
             _class='grey pull-right')


def me_requires_complete_profile(auID):
    """
    :param auID: db.auth_user.id
    :return: Check if we require a complete profile
    """
    from openstudio.os_customer import Customer

    # shop_requires_complete_profile_classes = get_sys_property('shop_requires_complete_profile_classes')
    shop_requires_complete_profile_memberships = get_sys_property('shop_requires_complete_profile_memberships')
    # shop_requires_complete_profile_classcards = get_sys_property('shop_requires_complete_profile_classcards')
    # shop_requires_complete_profile_events = get_sys_property('shop_requires_complete_profile_events')
    shop_requires_complete_profile_subscriptions = get_sys_property('shop_requires_complete_profile_subscriptions')

    customer = Customer(auID)

    require_complete_profile = False

    if shop_requires_complete_profile_memberships and customer.has_membership_on_date(TODAY_LOCAL):
        require_complete_profile = True

    if shop_requires_complete_profile_subscriptions and customer.has_subscription_on_date(TODAY_LOCAL):
        require_complete_profile = True

    return require_complete_profile


@auth.requires_login()
def me():
    """
        Allows users to edit part of their profile
    """
    response.title = T('Profile')
    response.subtitle = ''

    _next = request.vars['_next']

    db.auth_user.email.comment =  os_gui.get_info_icon(
         title=T("If you change your email address, you'll have to use the new address to login."),
         btn_icon='info')

    session.profile_me_bankaccount_next = URL('me_bankaccount')

    customer_fields = [
        db.auth_user.first_name,
        db.auth_user.last_name,
        db.auth_user.email,
        db.auth_user.gender,
        db.auth_user.school_discovery_id,
        db.auth_user.date_of_birth,
        db.auth_user.address,
        db.auth_user.postcode,
        db.auth_user.city,
        db.auth_user.country,
        db.auth_user.phone,
        db.auth_user.mobile,
        db.auth_user.emergency,
        db.auth_user.newsletter
    ]

    db.auth_user.mobile.requires = IS_NOT_EMPTY(error_message = T('Please enter your mobile number'))

    if me_requires_complete_profile(auth.user.id):
        dis_query = dis_query = (db.school_discovery.Archived == False)

        db.auth_user.gender.requires=IS_IN_SET(GENDERS, error_message=T("Cannot be empty"))
        db.auth_user.school_discovery_id.requires=IS_IN_DB(db(dis_query),
                                                           'school_discovery.id',
                                                           '%(Name)s',
                                                           error_message="Cannot be empty")
        db.auth_user.date_of_birth.requires=IS_DATE(format=DATE_FORMAT, error_message=T('Cannot be empty'))
        db.auth_user.address.requires=IS_NOT_EMPTY(error_message=T("Cannot be empty"))
        db.auth_user.city.requires=IS_NOT_EMPTY(error_message=T("Cannot be empty"))
        db.auth_user.postcode.requires=IS_NOT_EMPTY(error_message=T("Cannot be empty"))
        db.auth_user.country.requires=IS_IN_SET(country_codes, error_message=T("Cannot be empty"))

    if session.show_location:
        loc_query = (db.school_locations.AllowAPI == True)
        db.auth_user.school_locations_id.requires = IS_IN_DB(db(loc_query),
                                                             'school_locations.id',
                                                             '%(Name)s',
                                                             error_message=T('Please select a location'),
                                                             zero=T('Please select a location...'))
        customer_fields.append(db.auth_user.school_locations_id)

    for field in db.auth_user:
        field.readable=False
        field.writable=False

    for field in customer_fields:
        field.readable=True
        field.writable=True

    form = SQLFORM(db.auth_user, auth.user.id,
                   submit_button = T('Save'),
                   formstyle='divs')

    if form.process().accepted:
        response.flash = T('Saved')

        if _next:
            redirect(_next)

    elif form.errors:
        response.flash = ''

    change_passwd = A(os_gui.get_fa_icon('fa-unlock-alt'), ' ', T('Change password'),
                      _href=URL('default', 'user', args=['change_password'], vars={'_next=':URL('profile', 'me')}),
                      _class='btn btn-link pull-right')

    input_location = ''
    if session.show_location:
        input_location = DIV(os_gui.get_form_group(form.custom.label.school_locations_id,
                                                       form.custom.widget.school_locations_id),
                             _class='col-md-4')


    form = DIV(
        form.custom.begin,
        DIV(DIV(os_gui.get_form_group(form.custom.label.first_name,
                                      form.custom.widget.first_name),
                _class='col-md-4'),
            DIV(os_gui.get_form_group(form.custom.label.last_name,
                                      form.custom.widget.last_name),
                _class='col-md-4'),
            DIV(os_gui.get_form_group(form.custom.label.email,
                                      form.custom.widget.email),
                _class='col-md-4'),
            _class='row'),
        DIV(DIV(os_gui.get_form_group(form.custom.label.date_of_birth,
                                      form.custom.widget.date_of_birth),
                _class='col-md-4'),
            DIV(os_gui.get_form_group(form.custom.label.gender,
                                      form.custom.widget.gender),
                _class='col-md-4'),
            DIV(os_gui.get_form_group(form.custom.label.school_discovery_id,
                                      form.custom.widget.school_discovery_id),
                _class='col-md-4'),
            _class='row'),
        DIV(DIV(os_gui.get_form_group(form.custom.label.address,
                                     form.custom.widget.address),
            _class='col-md-4'),
            DIV(os_gui.get_form_group(form.custom.label.city,
                                      form.custom.widget.city),
                _class='col-md-4'),
            DIV(os_gui.get_form_group(form.custom.label.postcode,
                                      form.custom.widget.postcode),
            _class='col-md-2'),
            DIV(os_gui.get_form_group(form.custom.label.country,
                                      form.custom.widget.country),
                _class='col-md-2'),
            _class='row'),
        DIV(DIV(os_gui.get_form_group(form.custom.label.phone,
                                     form.custom.widget.phone),
            _class='col-md-4'),
            DIV(os_gui.get_form_group(form.custom.label.mobile,
                                      form.custom.widget.mobile),
            _class='col-md-4'),
            DIV(os_gui.get_form_group(form.custom.label.emergency,
                                      form.custom.widget.emergency),
            _class='col-md-4'),
            _class='row'),
        DIV(input_location,
            _class='row'
        ),
        DIV(INPUT(_type="checkbox",
                    _id='data_true_and_complete',
                    _class="iCheck-line-aero"), ' ',
            LABEL(T("I confirm that the data above is true and complete"),
                  _for="data_true_and_complete"),
              _class="form-group"),
        DIV(DIV(change_passwd, form.custom.submit, _class='col-md-12'),
            _class='row'),
            form.custom.end,
    _class='grid')

    content = form
    privacy = me_get_link_privacy()
    menu = me_get_menu(request.function)
    return dict(content = content,
                menu=menu,
                header_tools = SPAN(T('Your CustomerID is ') + auth.user.id,
                                    BR(), privacy)

                )


@auth.requires_login()
def me_bankaccount():
    """
            Allows users to edit payment information of their profile
    """
    from openstudio.os_customer import Customer
    from general_helpers import set_form_id_and_get_submit_button
    response.title = T('Profile')
    response.subtitle = 'Bank Account'
    response.view = 'profile/me.html'

    customer = Customer(auth.user.id)

    db.customers_payment_info.payment_methods_id.default = 3
    db.customers_payment_info.payment_methods_id.readable = False
    db.customers_payment_info.payment_methods_id.writable = False

    query = (db.customers_payment_info.auth_customer_id == auth.user_id)
    if db(query).count() < 1:
        db.customers_payment_info.auth_customer_id.default = auth.user.id
        form = SQLFORM(
            db.customers_payment_info,
            submit_button = T("Save")
        )

    else:
        db.customers_payment_info.auth_customer_id.default = auth.user.id
        pi = db.customers_payment_info(auth_customer_id=auth.user.id)

        form = SQLFORM(
            db.customers_payment_info,
            pi.id,
            submit_button = T("Save")
        )

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']


    if form.process().accepted:
        session.flash = T("Saved")
        redirect(session.profile_me_bankaccount_next)

    elif form.errors:
        response.flash = ''

    form = DIV(
        XML('<form id="MainForm" action="#" enctype="multipart/form-data" method="post">'),
        DIV(DIV(os_gui.get_form_group(form.custom.label.AccountNumber,
                                      form.custom.widget.AccountNumber),
                _class='col-md-4'),
            DIV(os_gui.get_form_group(form.custom.label.AccountHolder,
                                      form.custom.widget.AccountHolder),
                _class='col-md-4'),
            DIV(os_gui.get_form_group(form.custom.label.BIC,
                                      form.custom.widget.BIC),
                _class='col-md-4'),
            _class='row'),
        DIV(DIV(os_gui.get_form_group(form.custom.label.BankName,
                                      form.custom.widget.BankName),
                _class='col-md-4'),
            DIV(os_gui.get_form_group(form.custom.label.BankLocation,
                                      form.custom.widget.BankLocation),
                _class='col-md-4'),
            _class='row'),

    DIV(INPUT(_type="checkbox",
              _id='data_true_and_complete',
              _class="iCheck-line-aero"), ' ',
        LABEL(T("I confirm that the data above is true and complete"),
              _for="data_true_and_complete"),
        _class="form-group"),
    DIV(DIV(submit, _class='col-md-12'),
        _class='row'),
    form.custom.end,
    _class='grid')

    content = form

    mandates = customer.get_payment_info_mandates(formatted=True)
    privacy = me_get_link_privacy()
    menu = me_get_menu(request.function)
    return dict(content=content,
                menu=menu,
                save=submit,
                content_extra=mandates,
                header_tools=SPAN(T('Your CustomerID is ') + auth.user.id,
                                  BR(), privacy)

                )


def me_get_menu(page=None):
    pages = []

    pages.append(['me',
                  T("General Information"),
                  URL("me")])
    pages.append(['me_bankaccount',
                T("Bank Account"),
                      URL("me_bankaccount"),
                  ])

    return os_gui.get_submenu(pages, page, _id='os-customers_edit_menu', horizontal=True, htype='tabs')


def me_get_link_privacy(var=None):
    """

    """
    # Privacy
    features = db.customers_profile_features(1)
    if not features.Privacy:
        return ''

    else:
        return A(
            SPAN(os_gui.get_fa_icon('fa-user-secret'), ' ', T("Privacy")),
            _href=URL('profile','privacy'),
            _class='pull-right'
        )


@auth.requires_login()
def classcards():
    """
        Lists classcards for a customer
    """
    response.title = T('Profile')
    response.subtitle = T('Class cards')

    features = db.customers_profile_features(1)
    if not features.Classcards:
        redirect(URL('profile', 'index'))

    left = [ db.school_classcards.on(
                 db.school_classcards.id ==
                 db.customers_classcards.school_classcards_id ) ]

    query = (db.customers_classcards.auth_customer_id == auth.user.id)
    rows = db(query).select(db.customers_classcards.ALL,
                            db.school_classcards.Classes,
                            db.school_classcards.Unlimited,
                            left=left,
                            orderby=~db.customers_classcards.id)

    header = THEAD(TR(TH(T('Card #')),
                      TH(T('Card')),
                      TH(T('Start')),
                      TH(T('Expiration')),
                      TH(T('Classes')),
                      TH(),
                      ))
    table = TABLE(header, _class='table table-hover table-striped')
    tbody = TBODY()
    for i, row in enumerate(rows):
        repr_row = list(rows[i:i+1].render())[0]

        remaining = classcard_get_remaining(row)

        tr = TR(TD(row.customers_classcards.id),
                TD(repr_row.customers_classcards.school_classcards_id),
                TD(repr_row.customers_classcards.Startdate),
                TD(repr_row.customers_classcards.Enddate),
                TD(remaining),
                TD(classcard_get_link_info(row)))

        tbody.append(tr)


    table.append(tbody)

    link_shop = ''
    features = db.customers_shop_features(1)
    if features.Classcards:
        link_shop = A(SPAN(os_gui.get_fa_icon('fa-shopping-cart'), ' ', T('New card'), BR(), BR()), _href=URL('shop', 'classcards'))

    back = os_gui.get_button('back', URL('profile', 'index'))

    return dict(content=table, back=back)


def classcard_get_remaining(row):
    total_classes = row.school_classcards.Classes
    if total_classes == 0 or row.school_classcards.Unlimited:
        remaining = T('Unlimited')
    else:
        taken_classes = row.customers_classcards.ClassesTaken
        remaining = total_classes - taken_classes

        if remaining == 1:
            remaining = SPAN(remaining, ' ', T('Class remaining'))
        else:
            remaining = SPAN(remaining, ' ', T('Classes remaining'))

    return remaining


def classcard_get_link_info(row):
    """
        Returns info link for a subscription
    """
    ccdID = row.customers_classcards.id

    return A(os_gui.get_fa_icon('fa-info-circle'),
             _href=URL('classcard_info', vars={'ccdID':ccdID}),
             _title=T('Class card details'),
             _class='grey pull-right')


@auth.requires_login()
def classcard_info():
    """
        Page to list permissions for a subscription
    """
    from openstudio.os_customer_classcard import CustomerClasscard

    ccdID = request.vars['ccdID']
    response.title = T('Profile')
    response.subtitle = T('Class card info')
    response.view = 'shop/index.html'

    # Check of the subscriptions feature is enabled
    features = db.customers_profile_features(1)
    if not features.Classcards:
        redirect(URL('profile', 'index'))

    # Check if this subscription belongs to the currently signed in user
    ccd = CustomerClasscard(ccdID)
    if ccd.classcard.auth_customer_id != auth.user.id:
        session.flash = T("That class card doesn't belong to this user")
        return URL('profile', 'index')

    content = DIV(H4(T('Class access'), ' ', ccd.name),
                  ccd.get_class_permissions(formatted=True))

    back = os_gui.get_button('back', URL('profile', 'index'))

    return dict(content=content, back=back)


@auth.requires_login()
def invoice():
    """
    Display invoice for a customer
    """
    from openstudio.os_invoice import Invoice

    response.title = T('Invoice')

    iID = request.vars['iID']

    invoice = Invoice(iID)

    if not invoice.get_linked_customer_id() == auth.user.id:
        session.flash = T("Unable to show invoice")
        redirect(URL('profile', 'invoices'))

    response.subtitle = invoice.invoice.InvoiceID

    si = invoice.get_studio_info()
    studio_info = DIV(
        DIV(H3(T('From'), _class='box-title'),
            _class='box-header'),
        DIV(B(si['name']),
            XML(si['address']), BR(),
            si['email'], BR(),
            si['phone'], BR(),
            si['registration'], BR(),
            si['tax_registration'], BR(),
            _class="box-body"),
        _class='box box-solid'
    )

    ci = invoice.get_customer_info()
    customer_info = DIV(
        DIV(H3(T('Bill to'), _class='box-title'),
            _class='box-header'),
        DIV(B(ci['company']),
            ci['name'], BR(),
            XML(ci['address'].replace('\n', '<br>')), BR(),
            # ci['registration'], BR(),
            # ci['tax_registration'], BR(),
            _class="box-body"),
        _class='box box-solid'
    )

    invoice_info = DIV(
        DIV(H3(T('About'), _class='box-title'),
            _class='box-header'),
        DIV(LABEL(T("Issued")), BR(),
            invoice.invoice.DateCreated.strftime(DATE_FORMAT), BR(),
            LABEL(T("Due date")), BR(),
            invoice.invoice.DateDue.strftime(DATE_FORMAT), BR(),
            LABEL(T("Status")), BR(),
            represent_invoice_status(invoice.invoice.Status, invoice.invoice),
            _class="box-body"),
        _class='box box-solid'
    )

    items_header = THEAD(TR(
        TH('Product Name'),
        TH('Description'),
        TH('Quantity'),
        TH('Price incl. VAT'),
        TH(SPAN('Subtotal', _class='pull-right')),
        TH(SPAN('Tax rate', _class='pull-right')),
    ))
    items = TABLE(items_header, _class="table table-striped")
    rows = invoice.get_invoice_items_rows()
    for i, row in enumerate(rows):
        repr_row = repr_row = list(rows[i:i + 1].render())[0]

        items.append(TR(
            TD(row.ProductName),
            TD(row.Description),
            TD(row.Quantity),
            TD(repr_row.Price),
            TD(SPAN(repr_row.TotalPrice, _class='pull-right')),
            TD(SPAN(repr_row.tax_rates_id, _class='pull-right')),
        ))

    # add totals
    amounts_total = invoice.get_amounts()
    amounts_vat   = invoice.get_amounts_tax_rates(formatted=False)

    # try:
    tfoot = TFOOT()
    amounts = [ [ T('Sub total'), amounts_total.TotalPrice ] ]

    for tax_rate in amounts_vat:
        amounts.append( [ tax_rate['Name'], tax_rate['Amount']])

    amounts.append([T('Total')    , amounts_total.TotalPriceVAT ])

    for amount in amounts:
        tfoot.append(TR(TD(),
                        TD(),
                        TD(),
                        TD(amount[0], _class='bold'),
                        TD(SPAN(CURRSYM, ' ',
                                format(amount[1], '.2f'),
                                _class='bold pull-right')),
                        # TD(),
                        # TD(),
                        TD(),
                        ))
    items.append(tfoot)

    invoice_terms = XML(invoice.invoice.Terms.replace('\n', '<br>') if invoice.invoice.Terms else '')
    invoice_footer = XML(invoice.invoice.Footer.replace('\n', '<br>') if invoice.invoice.Footer else '')

    header_tools = DIV(
        os_gui.get_button(
            'print',
            URL('invoices', 'pdf', vars={'iID':iID}),
            btn_size=''),
            _class='pull-right'
    )

    if invoice.invoice.Status == 'sent':
        header_tools.append(os_gui.get_button(
            'noicon',
            URL('mollie', 'invoice_pay', vars={'iID':iID}),
            title=T("Pay now"),
            _class='pull-right',
            btn_class="btn-success",
            btn_size=''
        ))

    back = os_gui.get_button(
        'back',
        URL('profile', 'invoices')
    )

    return dict(studio_info = studio_info,
                customer_info = customer_info,
                invoice_info = invoice_info,
                invoice_items = items,
                invoice_terms = invoice_terms,
                invoice_footer = invoice_footer,
                header_tools = header_tools,
                back=back)


@auth.requires_login()
def invoices():
    """
        Shows all invoices for a customer
    """
    from openstudio.os_customer import Customer

    response.title = T('Invoices')
    response.subtitle = ''
    #response.view = 'shop/index.html'

    features = db.customers_profile_features(1)
    if not features.Invoices:
        redirect(URL('profile', 'index'))

    customer = Customer(auth.user.id)
    rows = customer.get_invoices_rows(debit_only=True, synced_only=True)

    # content = "hello world"

    #TODO: migrate this to a responsive layout

    header = DIV(
        DIV(T("Invoice #"), _class="col-md-2"),
        DIV(T("Date"), _class="col-md-2"),
        DIV(T("Due"), _class="col-md-2"),
        DIV(T("Amount"), _class="col-md-2"),
        DIV(T("Status"), _class="col-md-2"),
        DIV(XML('&nbsp;'), _class="col-md-2"),
        _class="row bold hidden-xs hidden-sm"
    )

    content = DIV(
        header
    )


    for i, row in enumerate(rows):
        repr_row = list(rows[i:i + 1].render())[0]
        pay_now = ''
        online_payment_provider = get_sys_property('online_payment_provider')

        pay_now = ''
        if not online_payment_provider == 'disabled':
            if row.invoices.Status == 'sent':
                pay_now = A(T('Pay now'),
                            _href=URL('mollie', 'invoice_pay', vars={'iID': row.invoices.id}),
                            _class='btn btn-success')

        content.append(DIV(
            DIV(A(repr_row.invoices.InvoiceID, _href=URL('invoice', vars={'iID': row.invoices.id})),
                _class='col-md-2'),
            DIV(repr_row.invoices.DateCreated, _class='col-md-2'),
            DIV(repr_row.invoices.DateDue, _class='col-md-2'),
            DIV(repr_row.invoices_amounts.TotalPriceVAT, _class='col-md-2'),
            DIV(repr_row.invoices.Status, _class='col-md-2'),
            DIV(DIV(os_gui.get_button('print', URL('invoices', 'pdf', vars={'iID': row.invoices.id}),
                                                   btn_size=''),
                                 _class='btn-group pull-right'),
                DIV(pay_now, _class='pull-right'),
                _class='col-md-2'),
            _class='row'
        ))

    back = os_gui.get_button('back', URL('profile', 'orders'), _class='btn-link')

    return dict(content=content, back=back)


@auth.requires_login()
def events():
    """
        Page to show list of workshops with invoices for a customer
    """
    from openstudio.os_customer import Customer

    response.title = T('Profile')
    response.subtitle = T('Events')
    # response.view = 'shop/index.html'

    features = db.customers_profile_features(1)
    if not features.Workshops:
        redirect(URL('profile', 'index'))

    customer = Customer(auth.user.id)
    rows = customer.get_workshops_rows()

    #link_shop = A(T('Book workshops'), _href=URL('shop', 'workshops'))
    link_shop = ''
    features = db.customers_shop_features(1)
    if features.Workshops:
        link_shop = A(SPAN(os_gui.get_fa_icon('fa-shopping-cart'), ' ', T('Book workshop'), BR(), BR()),
                      _href=URL('shop', 'workshops'))

    back = os_gui.get_button('back', URL('profile', 'index'))

    return dict(rows=rows, link_shop=link_shop, back=back)


@auth.requires_login()
def orders():
    """
        Page to show list of orders for a customer
    """
    response.title = T('Orders')
    response.subtitle = ''
    # response.view = 'shop/index.html'

    features = db.customers_profile_features(1)
    if not features.Orders:
        redirect(URL('profile', 'index'))

    orders = orders_display()

    link_invoices = A(T('All invoices'),
                     _href=URL('profile','invoices'),
                     _title=T('All invoices'),
                     _class='btn btn-link')


    return dict(orders=orders, link_invoices=link_invoices)


def orders_display(var=None):
    """
        Returns orders display
    """
    from openstudio.os_customer import Customer

    customer = Customer(auth.user.id)
    orders = customer.get_orders_with_items_and_amounts()

    content = DIV()
    items_header = THEAD(TR(TH(T('Product')),
                            TH(T('Description')),
                            TH(T('Quantity')),
                            TH(T('Price')),
                            TH(T('Total'))))

    for order in orders:
        cancel = ''
        if order['row'].customers_orders.Status == 'awaiting_payment' or \
           order['row'].customers_orders.Status == 'received':
            onclick = "return confirm('" + \
                      T('Do you really want to cancel this order?') + "');"

            cancel = A(T('Cancel'),
                       _href=URL('order_cancel', vars={'coID':order['row'].customers_orders.id}),
                       _title=T('Cancel this order'),
                       _onclick=onclick,
                       _class='btn btn-link btn-xs')

        online_payment_provider = get_sys_property('online_payment_provider')
        pay_now = ''
        if order['row'].customers_orders.Status == 'awaiting_payment' and not online_payment_provider == 'disabled':
            pay_now = A(T('Pay now'),
                        _href=URL('mollie', 'order_pay', vars={'coID': order['row'].customers_orders.id}),
                        _class='btn btn-success btn-xs pull-right')

        invoice = ''
        if order['row'].invoices.id:
            invoice = A(I(_class="fa fa-file-pdf-o"), ' ', order['row'].invoices.InvoiceID,
                        _href=URL('invoices', 'pdf', vars={'iID':order['row'].invoices.id}),
                        _title=T('Save invoice as PDF'))

        items = TABLE(items_header, _class='table table-condensed')
        for i, item in enumerate(order['items']):
            repr_item = list(order['items'][i:i + 1].render())[0]
            items.append(TR(TD(item.ProductName),
                            TD(item.Description),
                            TD(item.Quantity),
                            TD(repr_item.Price),
                            TD(repr_item.TotalPriceVAT)))

        items.append(TR(TD(),
                        TD(),
                        TD(),
                        TD(),
                        TD(B(order['repr_row'].customers_orders_amounts.TotalPriceVAT))))

        status = order['row'].customers_orders.Status
        repr_status = order['repr_row'].customers_orders.Status
        display_status = DIV(repr_status, _class='pull-right')
        box_class = ''
        if status == 'delivered':
            box_class = 'box-success'
        elif status == 'cancelled':
            box_class = 'box-warning'
        elif status == 'awaiting_payment' or status == 'received':
            box_class = 'box-primary'

        customer_message = ''
        if order['row'].customers_orders.CustomerNote:
            customer_message = DIV(
                T("We received the following message with your order:"), BR(),
                order['row'].customers_orders.CustomerNote,
                _class='grey'
            )


        display_order = DIV(
            display_status,
            H5(order['repr_row'].customers_orders.DateCreated),
            DIV(DIV(DIV(cancel, ' ', pay_now, ' ', invoice, _class='pull-right'),
                        H3(T('Order'), ' #', order['row'].customers_orders.id, _class='box-title'),
                    _class='box-header with-border'),
                DIV(DIV(items,
                        _class=''),
                    customer_message,
                    _class='box-body'),
            _class='box ' + box_class)
        )

        content.append(display_order)

    return content


@auth.requires_login()
def order_cancel():
    """
        Cancel order
    """
    coID = request.vars['coID']
    order = Order(coID)

    permission  = ((auth.has_membership(group_id='Admins') or
                    auth.has_permission('read', 'invoices')) or
                   order.order.auth_customer_id == auth.user.id)

    if not permission:
        return T("Not authorized")

    order.set_status_cancelled()

    redirect(URL('profile', 'orders'))


@auth.requires_login()
def order():
    """
        Page to show order content
    """
    coID = request.vars['coID']

    features = db.customers_profile_features(1)
    if not features.Orders:
        redirect(URL('profile', 'index'))

    order = Order(coID)
    if not order.order.auth_customer_id == auth.user.id:
        return 'Not authorized'

    rows = order.get_order_items_rows()
    amounts = order.get_amounts()

    response.title = T('Order')
    response.subtitle = T('# ') + coID

    back = os_gui.get_button('back', URL('profile', 'orders'), _class='btn-link')

    return dict(rows=rows, amounts=amounts, order=order.order, back=back)


@auth.requires_login()
def classes():
    """
        Page to list classes for a customer
    """
    from openstudio.os_customer import Customer
    from openstudio.os_class_attendance import ClassAttendance

    response.title = T('Profile')
    response.subtitle = T('Classes')

    features = db.customers_profile_features(1)
    if not features.Classes:
        redirect(URL('profile', 'index'))

    customer = Customer(auth.user.id)
    if 'all' in request.vars:
        limit = False
        link_all = ''
    else:
        limit_nr = 25
        limit = limit_nr + 1
        link_all = A(T('Show all'), _href=URL(vars={'all': True}))

    session.profile_class_cancel_confirm_back = 'profile_classes'

    # select 1 row extra, if we get one extra row, we need the show all link
    rows = customer.get_classes_attendance_rows(limit)

    header = THEAD(TR(TH(T('Date')),
                        TH(T('Time')),
                        TH(T('Class')),
                        TH(T('Location')),
                        TH(T('Used')),
                        TH(),
                        TH()))
    table = TABLE(header, _class='table table-striped table-hover')

    for i, row in enumerate(rows):
        repr_row = list(rows[i:i + 1].render())[0]

        att_type = ''
        if row.classes_attendance.customers_subscriptions_id:
            att_type = repr_row.classes_attendance.customers_subscriptions_id
        elif row.classes_attendance.customers_classcards_id:
            att_type = SPAN(row.school_classcards.Name,
                            _title=T('Class card') + ' ' + unicode(row.classes_attendance.customers_classcards_id))


        cancel = ''
        clatt = ClassAttendance(row.classes_attendance.id)
        if clatt.get_cancellation_possible() and not row.classes_attendance.BookingStatus == 'cancelled':
            cancel = A(T('Cancel'),
                       _href=URL('class_cancel_confirm', vars={'clattID':row.classes_attendance.id}),
                       _class='pull-right')

        status = SPAN(repr_row.classes_attendance.BookingStatus, _class='pull-right')

        table.append(TR(TD(repr_row.classes_attendance.ClassDate),
                      TD(SPAN(repr_row.classes.Starttime, ' - ', repr_row.classes.Endtime)),
                      TD(repr_row.classes.school_classtypes_id),
                      TD(repr_row.classes.school_locations_id),
                      TD(att_type),
                      TD(cancel),
                      TD(status)))

    # determine whether to show show all link
    if limit:
        if len(rows) <= limit_nr:
            link_all = ''

    link_shop = ''
    features = db.customers_shop_features(1)
    if features.Classes:
        link_shop = A(SPAN(os_gui.get_fa_icon('fa-shopping-cart'), ' ', T('Book classes')),
                      _href=URL('shop', 'classes'))

    back = os_gui.get_button('back', URL('profile', 'index'))

    return dict(content=table, link_all=link_all, link_shop=link_shop, back=back)


def class_cancel_get_return_url(var=None):
    """
        Get return url for cancel class confirm and class_cancel functions
    """
    if session.profile_class_cancel_confirm_back == 'profile_index':
        return_url = URL('profile', 'index')
    else:
        return_url = URL('profile', 'classes')

    return return_url


@auth.requires_login()
def class_cancel():
    """
        Cancel class
    """
    from openstudio.os_class_attendance import ClassAttendance

    clattID = request.vars['clattID']

    clatt = ClassAttendance(clattID)
    if not clatt.row.auth_customer_id == auth.user.id:
        return T('This class is not yours')

    message = clatt.set_status_cancelled()
    session.flash = message

    redirect(class_cancel_get_return_url())


@auth.requires_login()
def class_cancel_confirm():
    """
        Ask user for confirmation about really cancelling booking for a class
    """
    from openstudio.os_class_attendance import ClassAttendance
    from openstudio.os_class import Class

    clattID = request.vars['clattID']

    clatt = ClassAttendance(clattID)
    if not clatt.row.auth_customer_id == auth.user.id:
        return T('This class is not yours')

    response.title = T('Confirmation')
    response.subtitle = T('Cancel class booking?')
    response.view = 'profile/index.html'

    cls = Class(clatt.row.classes_id, clatt.row.ClassDate)
    name = XML(cls.get_name_shop())

    yes = A(T('Yes'),
            _href=URL('class_cancel', vars={'clattID':clattID}),
            _class='btn btn-primary')

    return_url = class_cancel_get_return_url()

    no = A(T('No'),
           _href=return_url,
           _class='btn btn-default')

    if clatt.get_cancellation_possible():
        buttons = DIV(yes, no, _class='')
    else:
        hours_limit = get_sys_property('shop_classes_cancellation_limit')
        buttons = DIV(B(T("We're sorry to inform you that this booking can no longer be cancelled.")), BR(),
                      SPAN(T('We accept cancellations until'), ' ', hours_limit, ' ',
                           T('hours before the start of a class.'),
                           _class='grey'),
                      BR(),
                      A(T('Back'), _href=URL('profile', 'classes'), _class='btn btn-link'))

    content = DIV(DIV(DIV(H3(T('Are you sure you want to cancel your booking for the following class?')),
                       H4(name), BR(),
                       buttons),
                      _class='box-body'),
                  _class='box box-primary center')

    back = os_gui.get_button('back', return_url)

    return dict(content=content, back=back)


@auth.requires_login()
def memberships():
    """
        Page to list subscriptions for a customer
    """
    response.title = T('Profile')
    response.subtitle = T('Memberships')

    features = db.customers_profile_features(1)
    if not features.Memberships:
        redirect(URL('profile', 'index'))

    left = db.school_memberships.on(
        db.customers_memberships.school_memberships_id ==
        db.school_memberships.id
    )

    query = (db.customers_memberships.auth_customer_id == auth.user.id)
    rows = db(query).select(db.customers_memberships.ALL,
                            db.school_memberships.Name,
                            left=left,
                            orderby=~db.customers_memberships.Startdate)


    back = os_gui.get_button('back', URL('index'))

    return dict(rows=rows, back=back)


@auth.requires_login()
def subscriptions():
    """
        Page to list subscriptions for a customer
    """
    response.title = T('Profile')
    response.subtitle = T('Subscriptions')

    features = db.customers_profile_features(1)
    if not features.Subscriptions:
        redirect(URL('profile', 'index'))

    session.profile_subscription_credits_back = 'profile_subscriptions'

    left = db.school_subscriptions.on(db.customers_subscriptions.school_subscriptions_id ==
                                      db.school_subscriptions.id)

    query = (db.customers_subscriptions.auth_customer_id == auth.user.id)
    rows = db(query).select(db.customers_subscriptions.ALL,
                            db.school_subscriptions.Name,
                            left=left,
                            orderby=~db.customers_subscriptions.Startdate)


    back = os_gui.get_button('back', URL('index'))

    return dict(rows=rows, back=back, fcredits=subscription_get_link_credits, finfo=subscription_get_link_info)


@auth.requires_login()
def subscription_credits():
    """
        Page to list subscription credits mutations
    """
    response.title = T('Profile')
    response.subtitle = T('Subscription credits')

    response.view = 'shop/index.html'

    csID = request.vars['csID']

    # Check of the subscriptions feature is enabled
    features = db.customers_profile_features(1)
    if not features.Subscriptions:
        redirect(URL('profile', 'index'))

    # Check if this subscription belongs to the currently signed in user
    cs = CustomerSubscription(csID)
    response.subtitle += ' - ' + cs.name

    if not cs.auth_customer_id == auth.user.id:
        session.flash = T("That subscription doesn't belong to this user")
        redirect(URL('profile', 'index'))

    # List mutations
    total = H4(T('Balance:'), ' ', cs.get_credits_balance(), _class='pull-right')
    mutations = cs.get_credits_mutations_rows(formatted=True,
                                              editable=False,
                                              deletable=False)

    if session.profile_subscription_credits_back == 'profile_index':
        return_url = URL('profile', 'index')
    else:
        return_url = URL('profile', 'subscriptions')

    back = os_gui.get_button('back',return_url)

    return dict(content=DIV(total, mutations), back=back)


@auth.requires_login()
def subscription_info():
    """
        Page to list permissions for a subscription
    """
    csID = request.vars['csID']
    response.title = T('Profile')
    response.subtitle = T('Subscription info')
    response.view = 'shop/index.html'

    # Check of the subscriptions feature is enabled
    features = db.customers_profile_features(1)
    if not features.Subscriptions:
        redirect(URL('profile', 'index'))

    # Check if this subscription belongs to the currently signed in user
    cs = CustomerSubscription(csID)
    if cs.cs.auth_customer_id != auth.user.id:
        session.flash = T("That subscription doesn't belong to this user")
        return URL('profile', 'index')

    content = DIV(H4(T('Class access'), ' ', cs.name),
                  cs.get_class_permissions(formatted=True))

    back = os_gui.get_button('back', URL('profile', 'index'))

    return dict(content=content, back=back)


def enrollments_get_back(var=None):
    """
    :param var: Unused variable to prevent Web2py making this function public
    :return: return url for enrollments
    """
    url = URL('profile', 'index')

    return url


@auth.requires_login()
def enrollments():
    """
        List recurring class reservations for customers
    """
    from openstudio.os_customer import Customer

    response.title = T('Profile')
    response.subtitle = T('Enrollments')

    response.view = 'shop/index.html'

    customer = Customer(auth.user.id)

    header = THEAD(TR(
        TH(T('Weekday')),
        TH(T('Time')),
        TH(T('Location')),
        TH(T('Class')),
        TH(T('Start')),
        TH(T('End')),
    ))

    table = TABLE(header, _class='table table-hover table-striped')

    rows = customer.get_reservations_rows()
    for i, row in enumerate(rows):
        repr_row = list(rows[i:i + 1].render())[0]

        enddate = repr_row.classes_reservation.Enddate
        if not row.classes_reservation.Enddate:
            enddate = A(T("End enrollment"),
                        _href=URL('enrollment_end', args=row.classes_reservation.id))


        table.append(TR(
            TD(repr_row.classes.Week_day),
            TD(repr_row.classes.Starttime, ' - ', repr_row.classes.Endtime),
            TD(repr_row.classes.school_locations_id),
            TD(repr_row.classes.school_classtypes_id),
            TD(repr_row.classes_reservation.Startdate),
            TD(enddate),
        ))

    content = table

    back = os_gui.get_button('back', enrollments_get_back())

    return dict(content=content, back=back)


@auth.requires_login()
def enrollment_end():
    """
        Allow customers to end their enrollment
    """
    response.title = T('Profile')
    response.subtitle = T('End enrollment')

    response.view = 'shop/index.html'

    clrID = request.args[0]

    ##
    # Check whether this enrollment actually belongs to this user
    # To prevent URL manipulation
    ##
    clr = db.classes_reservation(clrID)
    if not clr.auth_customer_id == auth.user.id:
        redirect(URL('enrollments'))

    return_url =  URL('profile', 'enrollments')
    content = DIV(_class='col-md-10 col-md-offset-1 col-xs-12')
    cls = db.classes(clr.classes_id)

    location = db.school_locations[cls.school_locations_id].Name

    classtype = db.school_classtypes[cls.school_classtypes_id].Name
    class_header = NRtoDay(cls.Week_day) + ' ' + \
                 cls.Starttime.strftime(TIME_FORMAT) + ' - ' + \
                 cls.Endtime.strftime(TIME_FORMAT) + ' ' + \
                 classtype + ' ' + \
                 T('in') + ' ' + location

    content.append(DIV(H3(XML(class_header), _class=''), BR(), H4(T('End enrollment'), _class=''), _class=''))

    info = P(T('By setting an enddate below, you can end your enrollment for this class.'))
    info2 = P(T("Please note that we won't cancel any class reservations made for this class, please cancel them manually from your profile home page in case you no longer wish to attend these classes."))

    content.append(DIV(info, info2))

    ##
    # Enrollment form (It actually shows just 2 buttons, everything else is a hidden field)
    ##
    db.classes_reservation.id.readable = False
    db.classes_reservation.id.writable = False
    db.classes_reservation.Startdate.readable = False
    db.classes_reservation.Startdate.writable = False
    db.classes_reservation.Enddate.comment = BR()

    form = SQLFORM(db.classes_reservation,
                   clrID,
                   formstyle='divs',
                   submit_button=T("End enrollment"))

    form.add_button(T("Cancel"), return_url)

    if form.process().accepted:
        session.flash = T('Saved')
        redirect(URL('profile', 'enrollments'))
    elif form.errors:
        response.flash = T('Form has errors')

    content.append(DIV(form, _class='col-md-6 no-padding-left'))

    back = os_gui.get_button('back', return_url)

    return dict(content=content, back=back)


def privacy_get_message(var=None):
    """
        return translatable string privacy message
    """
    privacy_notice = ''

    organization = ORGANIZATIONS[ORGANIZATIONS['default']]
    if organization['PrivacyNoticeURL']:
        privacy_notice = SPAN(
            T("and review our"), ' ',
            A(T("privacy notice"),
              _href=organization['PrivacyNoticeURL'],
              _target="_blank")
        )

    return SPAN(
        T("We use your information to provide the best service possible"), ', ',
        T("to improve our services and to be able to give personalized advice."), BR(),
        T("Below you can download data and files (if any) associated with your account."), BR(),
        T("While you're here, why not review our"), ' ', privacy_notice,'?'
    )


@auth.requires_login()
def privacy():
    """
        Privacy page for account
    """
    response.title = T('Privacy')
    response.view = 'shop/index.html'

    # Check whether the privacy feature is enabled
    features = db.customers_profile_features(1)
    if not features.Privacy:
        redirect(URL('profile', 'index'))

    download = os_gui.get_button(
        'noicon',
        URL('profile', 'privacy_download'),
        title=T('Download')
    )

    documents = privacy_get_documents()

    content = DIV(
        privacy_get_message(), BR(), BR(),
        documents,
        H4(T('Data')),
        download,
    )

    back = os_gui.get_button('back', URL('profile', 'me'))

    return dict(content=content, back=back)


def privacy_get_documents(var=None):
    """
        returns list of documents for customer
    """
    from openstudio.os_customer import Customer

    customer = Customer(auth.user.id)
    rows = customer.get_documents_rows()

    if not len(rows):
        return ''

    header = THEAD(
        TR(
            TH(T("Description")),
            TH(T("Download")),
        )
    )
    table = TABLE(header, _class='table table-striped table-hover')
    for row in rows:
        tr = TR(
            TD(row.Description),
            TD(A(T("Download"),
                 _href=URL('default', 'download', args=row.DocumentFile)))
        )

        table.append(tr)

    documents = DIV(
        H4(T('Files')),
        table
    )

    return documents


@auth.requires_login()
def privacy_download():
    """
    :return: xlsx document containing all data of an account
    """
    from openstudio.os_customer_export import CustomerExport

    # Check whether the privacy feature is enabled
    features = db.customers_profile_features(1)
    if not features.Privacy:
        redirect(URL('profile', 'index'))

    ce = CustomerExport(auth.user.id)
    stream = ce.excel()

    fname = 'customer_data.xlsx'
    response.headers['Content-Type'] = 'application/vnd.ms-excel'
    response.headers['Content-disposition'] = 'attachment; filename=' + fname

    return stream.getvalue()


@auth.requires_login()
def mail():
    """
        List MailChimp mailing lists
    """
    response.title = T('Mail')
    response.view = 'shop/index.html'

    # Check whether the privacy feature is enabled
    features = db.customers_profile_features(1)
    if not features.Mail:
        redirect(URL('profile', 'index'))

    content = DIV(LOAD('mailchimp', 'lists_for_customer.load',
                              content=os_gui.get_ajax_loader(message=T("Loading mailing lists...")),
                              vars={'cuID':auth.user.id},
                              ajax=True))

    return dict(content=content)

#
# @auth.requires_login()
# def staff_payments():
#     """
#         List staff payments
#     """
#     response.title = T('Payments')
#     response.view = 'shop/index.html'
#
#     if auth.user.teacher == False and auth.user.employee == False:
#         redirect(URL('profile', 'index'))
#
#     # Check whether the privacy feature is enabled
#     features = db.customers_profile_features(1)
#     if not features.StaffPayments:
#         redirect(URL('profile', 'index'))
#
#     content = staff_payments_get_content()
#
#     return dict(content=content)
#
#
# def staff_payments_get_content(var=None):
#     """
#
#     :param var:
#     :return:
#     """
#     from openstudio.os_customer import Customer
#
#     customer = Customer(auth.user.id)
#     rows = customer.get_invoices_rows(
#         public_group=False,
#         payments_only=True
#     )
#
#     header = THEAD(TR(
#         TH(T('Invoice #')),
#         TH(T('Date')),
#         TH(T('Due')),
#         TH(T('Amount')),
#         TH(T('Status')),
#         TH(),
#     ))
#
#     table = TABLE(header, _class='table table-striped table-hover')
#
#     for i, row in enumerate(rows):
#         repr_row = list(rows[i:i + 1].render())[0]
#
#         pdf = os_gui.get_button(
#             'print',
#             URL('invoices', 'pdf',
#                 vars={'iID':row.invoices.id}),
#             btn_size='',
#             _class='pull-right'
#         )
#
#         table.append(TR(
#             TD(row.invoices.InvoiceID),
#             TD(repr_row.invoices.DateCreated),
#             TD(repr_row.invoices.DateDue),
#             TD(repr_row.invoices_amounts.TotalPriceVAT),
#             TD(repr_row.invoices.Status),
#             TD(pdf)
#         ))
#
#     return table
