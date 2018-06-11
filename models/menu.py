# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# ----------------------------------------------------------------------------------------------------------------------
# Customize your APP title, subtitle and menus here
# ----------------------------------------------------------------------------------------------------------------------

import os.path
from general_helpers import User_helpers

#NOTE: use this for customer login

response.title = ' '.join(
    word.capitalize() for word in request.application.split('_'))
response.subtitle = T('')

# ----------------------------------------------------------------------------------------------------------------------
# read more at http://dev.w3.org/html5/markup/meta.name.html
# ----------------------------------------------------------------------------------------------------------------------
response.meta.author = myconf.get('app.author')
response.meta.description = myconf.get('app.description')
response.meta.keywords = myconf.get('app.keywords')
response.meta.generator = myconf.get('app.generator')

# ----------------------------------------------------------------------------------------------------------------------
# your http://google.com/analytics id
# ----------------------------------------------------------------------------------------------------------------------
response.google_analytics_id = None

#########################################################################
## this is the main application menu add/remove items as required
#########################################################################


def shoppingcart_menu_item():
    '''
        @return: shopping cart menu link
    '''
    # check login
    try:
        query = (db.customers_shoppingcart.auth_customer_id == auth.user.id)
        count = db(query).count()
    except AttributeError:
        # auth.user.id doesn't exist when not logged in
        count = 0

    return A(I(_class=os_gui.get_icon('shopping-cart')), ' ',
                      os_gui.get_badge(count),
                _href=URL('shop', 'cart', extension=''),
                _title=T('Shopping cart'))



def profile_menu():
    featured_class = ''
    me_class = ''

    features = db.customers_profile_features(1)

    menu = []
    # Home
    menu.append([(#I(_class='fa fa-home'),
                        SPAN(T('Home'))),
                       False,
                       URL('profile', 'index', extension='')])

    # Orders
    if features.Orders:
        menu.append(
                (SPAN(SPAN(#I(_class='fa fa-folder-open-o'), ' ',
                            T('Orders')),
                            _class=featured_class),
                            False,
                            URL('profile', 'orders', extension='')))

    # Me
    menu.append(
            (SPAN(SPAN(#I(_class='fa fa-user', _title=T('My account')), ' ',
                        T('Profile')),
                        _class=me_class,
                        _title=T('My account')),
                        False,
                        URL('profile','me', extension='')))

    # Email
    if features.Mail:
        menu.append(
                (SPAN(SPAN(#I(_class='fa fa-folder-open-o'), ' ',
                            T('Mail')),
                            _class=featured_class),
                            False,
                            URL('profile', 'mail', extension='')))

    # Teacher payments
    if features.StaffPayments and (auth.user.teacher == True or auth.user.employee == True):
        menu.append(
                (SPAN(SPAN(#I(_class='fa fa-folder-open-o'), ' ',
                            T('Payments')),
                            _class=featured_class),
                            False,
                            URL('profile', 'staff_payments', extension='')))

    return menu


def shop_links():
    """
        Gets additional links for the shop pages
    """
    menu = []
    rows = db(db.shop_links).select(db.shop_links.ALL,
                                    orderby=db.shop_links.Name)

    for row in rows:
        menu.append([(#I(_class='fa fa-graduation-cap'),
                      SPAN(row.Name)),
                     False,
                     row.URL])

    try:
        if auth.user.login_start == 'backend':
            menu.append((SPAN(T('Back end')), False, URL('pinboard', 'index')))
    except AttributeError:
        pass

    return menu


def shop_menu():
    featured_class = ''
    classes_class = ''
    classcards_class = ''
    subscriptions_class = ''
    workshops_class = ''
    donate_class = ''
    contact_class = ''
    me_class = ''

    features = db.customers_shop_features(1)

    menu = []
    # Featured
    # response.menu.append(
    #         (SPAN(SPAN(#SPAN(_class='glyphicon glyphicon-pushpin'), ' ',
    #                                         T('Featured')),
    #                                         _class=featured_class),
    #                         False,
    #                         URL('shop', 'index')) )
    # Classes
    if features.Classes:
        menu.append([(#I(_class='fa fa-graduation-cap'),
                      SPAN(T('Classes'))),
                     False,
                     URL('shop', 'classes', extension='')])

    # Memberships
    if features.Memberships:
        menu.append([(#I(_class='fa fa-pencil-square-o'),
                      SPAN(T('Memberships'))),
                     False,
                     URL('shop', 'memberships', extension='')])

    # Subscriptions
    if features.Subscriptions:
        menu.append([(#I(_class='fa fa-pencil-square-o'),
                      SPAN(T('Subscriptions'))),
                     False,
                     URL('shop', 'subscriptions', extension='')])

    # Class cards
    if features.Classcards:
        menu.append([(#I(_class='fa fa-id-card-o'),
                      SPAN(T('Class cards'))),
                     False,
                     URL('shop', 'classcards', extension='')])

    # Events
    if features.Workshops:
        menu.append([(#I(_class='fa fa-object-group'),
                      SPAN(T('Events'))),
                     False,
                     URL('shop', 'events', extension='')])

    # Donations
    if features.Donations:
        menu.append([(#I(_class='fa fa-usd'),
                      SPAN(T('Donate'))),
                     False,
                     URL('shop', 'donate', extension='')])


    return menu


def shop_menu_about():
    menu = []

    # Contact
    menu.append([(#I(_class='fa fa-info-circle'),
                        SPAN(T('Contact'))),
                       False,
                       URL('shop', 'contact', extension='')])

    return menu


def get_backend_menu():
    user_helpers = User_helpers()

    default_class = ''
    pinboard_class = ''
    tasks_class = ''
    customers_class = ''
    classes_class = ''
    employees_class = ''
    workshops_class = ''
    sp_class = ''
    reports_class = ''
    finance_class = ''
    shop_class = ''
    settings_class = ''
    jumpto_class = ''

    active_class = 'active'

    if not request.is_scheduler and not request.is_shell:
        if request.controller == 'default':
            default_class = active_class
        elif request.controller == 'pinboard':
            pinboard_class = active_class
        elif request.controller == 'tasks':
            tasks_class = active_class
        elif request.controller == 'customers':
            customers_class = active_class
        elif request.controller == 'classes':
            classes_class = active_class
        elif request.controller == 'staff':
            classes_class = active_class
        elif request.controller == 'workshops':
            workshops_class = active_class
        elif request.controller == 'school_properties' or request.controller == 'teachers':
            sp_class = active_class
        elif request.controller == 'reports':
            reports_class = active_class
        elif request.controller == 'finance':
            finance_class = active_class
        elif request.controller == 'shop':
            shop_class = active_class
        elif request.controller == 'settings':
            settings_class = active_class


    if not auth.user is None:
        user_id = auth.user.id

        menu = []

        # Pinboard
        if user_helpers.check_read_permission('pinboard', user_id):
            menu.append(
                ((I(_class='fa fa-comments-o'),
                  SPAN(T('Pinboard'))),
                False,
                URL('pinboard', 'index')) )

        # tasks
        if user_helpers.check_read_permission('tasks', user_id):
            menu += [ ((I(_class='fa fa-check-square-o'),
                                 SPAN(T('Tasks'))),
                                False,
                                URL('tasks', 'index', extension='')) ]
        # customers
        if user_helpers.check_read_permission('auth_user', user_id):
            menu += [ ((I(_class='fa fa-users'),
                                 SPAN(T('Customers'))),
                                False,
                                URL('customers', 'index', extension='')) ]
        # Schedule ( classes & employees )
        if ( user_helpers.check_read_permission('classes', user_id) or
             user_helpers.check_read_permission('shifts', user_id) ):

            submenu = []
            if user_helpers.check_read_permission('classes', user_id):
                submenu.append(((I(_class='fa fa-caret-right'), SPAN(T('Classes'))),
                                False,
                                URL('classes', 'schedule', extension='')))
            if user_helpers.check_read_permission('shifts', user_id):
                submenu.append(((I(_class='fa fa-caret-right'), SPAN(T('Studio staff'))),
                                False,
                                URL('staff', 'schedule', extension='')))

            menu += [ ((I(_class='fa fa-calendar'),
                                 SPAN(T('Schedule')),
                                 SPAN(I(_class='fa fa-angle-left pull-right'),
                                      _class="pull-right-container")),
                                 False,
                                 URL('classes', 'schedule', extension=''),
                                 submenu) ]

        # Events
        if user_helpers.check_read_permission('workshops', user_id):
            menu += [ ((I(_class='fa fa-ticket'),
                                 SPAN(T('Events'))),
                                False,
                                URL('events', 'index', extension='')) ]
        # school properties
        if user_helpers.check_read_permission('schoolproperties', user_id):
            submenu = []

            if user_helpers.check_read_permission('teachers', user_id):
                submenu.append(((I(_class='fa fa-caret-right'), SPAN(T('Teachers')), ),
                                False,
                                URL('teachers', 'index', extension='')))

            if user_helpers.check_read_permission('employees', user_id):
                submenu.append(((I(_class='fa fa-caret-right'), SPAN(T('Employees')), ),
                                False,
                                URL('school_properties', 'employees', extension='')))

            if user_helpers.check_read_permission('school_memberships', user_id):
                submenu.append(((I(_class='fa fa-caret-right'), SPAN(T('Memberships')), ),
                                False,
                                URL('school_properties', 'memberships', extension='')))

            if user_helpers.check_read_permission('school_subscriptions', user_id):
                submenu.append(((I(_class='fa fa-caret-right'), SPAN(T('Subscriptions')), ),
                                False,
                                URL('school_properties', 'subscriptions', extension='')))

            if user_helpers.check_read_permission('school_classcards', user_id):
                submenu.append(((I(_class='fa fa-caret-right'), SPAN(T('Class cards')), ),
                                False,
                                URL('school_properties', 'classcards', extension='')))

            if user_helpers.check_read_permission('school_clastypes', user_id):
                submenu.append(((I(_class='fa fa-caret-right'), SPAN(T('Class types')), ),
                                False,
                                URL('school_properties', 'classtypes', extension='')))

            if user_helpers.check_read_permission('school_locations', user_id):
                submenu.append(((I(_class='fa fa-caret-right'), SPAN(T('Locations')), ),
                                False,
                                URL('school_properties', 'locations', extension='')))


            if user_helpers.check_read_permission('school_shifts', user_id):
                submenu.append(((I(_class='fa fa-caret-right'), SPAN(T('Shifts')), ),
                                False,
                                URL('school_properties', 'shifts', extension='')))

            if user_helpers.check_read_permission('school_holidays', user_id):
                submenu.append(((I(_class='fa fa-caret-right'), SPAN(T('Holidays')), ),
                                False,
                                URL('schedule', 'holidays', extension='')))

            if user_helpers.check_read_permission('school_languages', user_id):
                submenu.append(((I(_class='fa fa-caret-right'), SPAN(T('Languages')), ),
                                False,
                                URL('school_properties', 'languages', extension='')))

            if user_helpers.check_read_permission('school_levels', user_id):
                submenu.append(((I(_class='fa fa-caret-right'), SPAN(T('Practice levels')), ),
                                False,
                                URL('school_properties', 'levels', extension='')))

            if user_helpers.check_read_permission('school_discovery', user_id):
                submenu.append(((I(_class='fa fa-caret-right'), SPAN(T('Discovery')), ),
                                False,
                                URL('school_properties', 'discovery', extension='')))

            if user_helpers.check_read_permission('schoolproperties_keys', user_id):
                submenu.append(((I(_class='fa fa-caret-right'), SPAN(T('Keys')), ),
                                False,
                                URL('school_properties', 'list_keys', extension='')))



            menu += [ ((I(_class='fa fa-graduation-cap'),
                                 SPAN(T('School')),
                                 SPAN(I(_class='fa fa-angle-left pull-right'),
                                      _class="pull-right-container")),
                                False,
                                URL('school_properties', 'index', extension=''),
                        submenu) ]
        # reports

        submenu = []
        if user_helpers.check_read_permission('reports_customers', user_id):
            submenu.append(((I(_class='fa fa-caret-right'), SPAN(T('Inactive customers'))),
                            False,
                            URL('reports', 'customers_inactive', extension='')))
        if user_helpers.check_read_permission('reports_classcards', user_id):
            submenu.append(((I(_class='fa fa-caret-right'), SPAN(T('Class cards'))),
                            False,
                            URL('reports', 'classcards', extension='')))
            #submenu.append((SPAN(os_gui.get_fa_icon('fa-ticket'), ' ', T('Class cards')), False, URL('reports', 'classcards')))
        if user_helpers.check_read_permission('reports_subscriptions', user_id):
            submenu.append(((I(_class='fa fa-caret-right'), SPAN(T('Subscriptions'))),
                            False,
                            URL('reports', 'subscriptions_overview', extension='')))
            #submenu.append((SPAN(os_gui.get_fa_icon('fa-edit'), ' ', T('Subscriptions')), False, URL('reports', 'subscriptions_overview')))
        if user_helpers.check_read_permission('reports_dropinclasses', user_id):
            submenu.append(((I(_class='fa fa-caret-right'), SPAN(T('Drop in classes'))),
                            False,
                            URL('reports', 'dropinclasses', extension='')))
            #submenu.append((SPAN(os_gui.get_fa_icon('fa-level-down'), ' ', T('Drop in classes')), False, URL('reports', 'dropinclasses')))
        if user_helpers.check_read_permission('reports_trialclasses', user_id):
            submenu.append(((I(_class='fa fa-caret-right'), SPAN(T('Trial'))),
                            False,
                            URL('reports', 'trialclasses', extension='')))
            #submenu.append((SPAN(os_gui.get_fa_icon('fa-compass'), ' ', T('Trial classes / cards')), False, URL('reports', 'trialclasses')))
        if user_helpers.check_read_permission('reports_classtypes', user_id) or auth.has_membership(group_id='Admins'):
            submenu.append(((I(_class='fa fa-caret-right'), SPAN(T('Attendance'))),
                            False,
                            URL('reports', 'attendance_classes', extension='')))
            #submenu.append((SPAN(os_gui.get_fa_icon('fa-check-square-o'), ' ', T('Attendance')), False, URL('reports', 'attendance_classtypes')))
        if user_helpers.check_read_permission('reports_retention', user_id):
            submenu.append(((I(_class='fa fa-caret-right'), SPAN(T('Attendance retention'))),
                            False,
                            URL('reports', 'retention_rate', extension='')))
            #submenu.append((SPAN(os_gui.get_fa_icon('fa-magnet'), ' ', T('Retention')), False, URL('reports', 'retention_rate')))
        if user_helpers.check_read_permission('reports_teacherclasses', user_id):
            submenu.append(((I(_class='fa fa-caret-right'), SPAN(T('Teacher classes'))),
                            False,
                            URL('reports', 'teacher_classes', extension='')))
            # submenu.append((SPAN(os_gui.get_fa_icon('fa-user'), ' ', T('Teacher classes')), False, URL('reports', 'teacher_classes')))
        if user_helpers.check_read_permission('reports_revenue', user_id):
            submenu.append(((I(_class='fa fa-caret-right'), SPAN(T('Revenue'))),
                            False,
                            URL('reports', 'revenue', extension='')))
            #submenu.append((SPAN(os_gui.get_fa_icon('fa-money'), ' ', T('Revenue')), False, URL('reports', 'revenue')))
        if user_helpers.check_read_permission('reports_discovery', user_id):
            submenu.append(((I(_class='fa fa-caret-right'), SPAN(T('Discovery'))),
                            False,
                            URL('reports', 'discovery', extension='')))
            #submenu.append((SPAN(os_gui.get_fa_icon('fa-binoculars'), ' ', T('Discovery')), False, URL('reports', 'discovery')))
        if user_helpers.check_read_permission('reports_geography', user_id):
            submenu.append(((I(_class='fa fa-caret-right'), SPAN(T('Geography'))),
                            False,
                            URL('reports', 'geography', extension='')))
            #submenu.append((SPAN(os_gui.get_fa_icon('fa-map-o'), ' ', T('Geography')), False, URL('reports', 'geography')))
        if user_helpers.check_read_permission('reports', user_id):
            menu += [
               ((I(_class='fa fa-bar-chart'), ' ',
                          SPAN(T('Reports')),
                          SPAN(I(_class='fa fa-angle-left pull-right'),
                               _class="pull-right-container")),
                False,
                URL('#', extension=''),
                submenu)]

        # Finance
        if user_helpers.check_read_permission('finance', user_id):
            finance_text = T('Finance')

            submenu = []

            if user_helpers.check_read_permission('invoices', user_id):
                submenu.append(((I(_class='fa fa-caret-right'), SPAN(T('Invoices'))),
                                False,
                                URL('finance', 'invoices', extension='')))
                submenu.append(((I(_class='fa fa-caret-right'), SPAN(T('Teacher payments'))),
                                False,
                                URL('finance', 'teacher_payments', extension='')))
                #submenu.append(( SPAN(os_gui.get_fa_icon('fa-file-o'), ' ', T('Invoices')), False, URL('finance', 'invoices') ))

            if user_helpers.check_read_permission('payment_batches', user_id):
                submenu.append(((I(_class='fa fa-caret-right'), SPAN(T('Batch collections'))),
                                False,
                                URL('finance', 'batches_index', vars={'export':'collection'}, extension='')))
                submenu.append(((I(_class='fa fa-caret-right'), SPAN(T('Batch payments'))),
                                False,
                                URL('finance', 'batches_index', vars={'export':'payment'}, extension='')))

                #submenu.append(( SPAN(os_gui.get_fa_icon('fa-th-list'), ' ', T('Batch collections')), False,
                #      URL('finance', 'batches_index', vars={'export':'collection'}) ))
                #submenu.append(( SPAN(os_gui.get_fa_icon('fa-th-list'), ' ', T('Batch payments')), False,
                #          URL('finance', 'batches_index', vars={'export':'payment'}) ))


            if user_helpers.check_read_permission('reports_direct_debit_extra', user_id):
                submenu.append(((I(_class='fa fa-caret-right'), SPAN(T('Direct debit extra'))),
                                False,
                                URL('reports', 'direct_debit_extra', extension='')))
                # submenu.append((SPAN(os_gui.get_fa_icon('fa-table'), ' ', T('Direct debit extra')),
                #                 False,
                #                 URL('reports', 'direct_debit_extra')))

            menu += [ ((I(_class=finance_class + ' fa fa-bank', _title=T('Finance')),
                                 SPAN(T('Finance')),
                                 SPAN(I(_class='fa fa-angle-left pull-right'),
                                      _class="pull-right-container")),
                                False,
                                URL('finance', 'invoices', extension=''), submenu )
                             ]
        # Shop
        if user_helpers.check_read_permission('shop_manage', user_id):
            shop_text_text = T('Shop')

            submenu = []
            # Workflow
            if user_helpers.check_read_permission('settings', user_id):
                submenu.append(((I(_class='fa fa-caret-right'), SPAN(T('Workflow'))),
                                False,
                                URL('shop_manage', 'workflow', extension='')))
            # Orders
            if user_helpers.check_read_permission('customers_orders', user_id):
                submenu.append(((I(_class='fa fa-caret-right'), SPAN(T('Orders'))),
                                False,
                                URL('orders', 'index', extension='')))
            # Catalog
            if user_helpers.check_read_permission('shop_products', user_id):
                submenu.append(((I(_class='fa fa-caret-right'), SPAN(T('Catalog [BETA]'))),
                                False,
                                URL('shop_manage', 'products', extension='')))


            menu += [ ((I(_class=finance_class + ' fa fa-shopping-bag', _title=T('Shop')),
                                 SPAN(T('Shop')),
                                 SPAN(I(_class='fa fa-angle-left pull-right'),
                                      _class="pull-right-container")),
                                False,
                                URL('#', extension=''), submenu )
                             ]

        # settings
        if user_helpers.check_read_permission('settings', user_id):
            submenu = []

            submenu.append(((I(_class='fa fa-caret-right'), SPAN(T('System'))),
                            False,
                            URL('settings', 'index', extension='')))
            submenu.append(((I(_class='fa fa-caret-right'), SPAN(T('Integration'))),
                            False,
                            URL('settings_integration', 'mollie', extension='')))
            submenu.append(((I(_class='fa fa-caret-right'), SPAN(T('Mail'))),
                            False,
                            URL('settings_mail', 'mailing_lists', extension='')))
            submenu.append(((I(_class='fa fa-caret-right'), SPAN(T('Branding'))),
                            False,
                            URL('settings_branding', 'logos', extension='')))

            menu += [ ((I(_class=settings_class + ' fa fa-cog', _title=T('Settings')),
                                 SPAN(T('Settings')),
                                 SPAN(I(_class='fa fa-angle-left pull-right'),
                                        _class="pull-right-container")),
                                False,
                                URL('#', extension=''), submenu)
                             ]

        # Flash to
        submenu = [
            ( '', False, A((os_gui.get_fa_icon('fa-caret-right'),
                            SPAN(T('Shop'))),
                           _href=URL('shop', 'index', extension=''),
                           _target='_blank')),
        ]

        if user_helpers.check_read_permission('selfcheckin', user_id):
            submenu.insert(0, ( '', False, A((os_gui.get_fa_icon('fa-caret-right'),
                                              SPAN(T('Self check-in'))),
                                              _href=URL('selfcheckin', 'index', extension=''),
                                              _target='_blank')))

        menu += [ ((I(_class=jumpto_class + ' fa fa-flash', _title=T('Go to')),
                            SPAN(T('Go to')),
                            SPAN(I(_class='fa fa-angle-left pull-right'),
                                  _class="pull-right-container")),
                            False,
                            URL('selfcheckin', 'index', extension=''), submenu )
                         ]

        # help # cannot contain more items yet.. in this version of web2py drop down menu items are forced to load in the same window
        # https://groups.google.com/forum/#!topic/web2py/9S34_LHW2qQ
        # menu += [
        #     (SPAN('', False,
        #           A((I(_class='fa fa-question-circle', _title=T("Help")),
        #              SPAN(T('Quick start'))),
        #             _href='http://www.openstudioproject.com/content/manual',
        #             _target="_blank")))]


        return menu


if request.controller == 'shop' or request.controller == 'profile':
    #response.menu = ''
    #response.menu_shop = shop_menu()
    #response.menu_profile = profile_menu()
    response.menu_shop = shop_menu()
    response.menu_shop_about = shop_menu_about()
    response.menu_shopping_cart = shoppingcart_menu_item()
    response.menu_profile = profile_menu()
    response.menu_links = shop_links()

    response.logo = SPAN(B('Open'), 'Studio', _class='logo-lg')

    if not request.is_scheduler and not request.is_shell:
        branding_logo = os.path.join(request.folder,
                                     'static',
                                     'plugin_os-branding',
                                     'logos',
                                     'branding_logo_header.png')
        if os.path.isfile(branding_logo):
            logo_src = URL('static', 'plugin_os-branding/logos/branding_logo_header.png', extension='')
            response.logo = SPAN(IMG(_src=logo_src), _class='logo=lg')


    response.logo_url = '#'
    shop_header_logo_url = get_sys_property('shop_header_logo_url')
    if shop_header_logo_url:
        response.logo_url = shop_header_logo_url

else:
    if auth.user:
        cache_key = 'openstudio_menu_backend_user_' + unicode(auth.user.id)
        response.menu = cache.ram(cache_key,
                                 lambda: get_backend_menu(),
                                 time_expire=259200)
    else:
        response.menu = ''






DEVELOPMENT_MENU = False

#########################################################################
## provide shortcuts for development. remove in production
#########################################################################

def _():
    # shortcuts
    app = request.application
    ctr = request.controller
    # useful links to internal and external resources
    response.menu += [
        (SPAN('web2py', _class='highlighted'), False, 'http://web2py.com', [
        (T('My Sites'), False, URL('admin', 'default', 'site')),
        (T('This App'), False, URL('admin', 'default', 'design/%s' % app), [
        (T('Controller'), False,
         URL(
         'admin', 'default', 'edit/%s/controllers/%s.py' % (app, ctr))),
        (T('View'), False,
         URL(
         'admin', 'default', 'edit/%s/views/%s' % (app, response.view))),
        (T('Layout'), False,
         URL(
         'admin', 'default', 'edit/%s/views/layout.html' % app)),
        (T('Stylesheet'), False,
         URL(
         'admin', 'default', 'edit/%s/static/css/web2py.css' % app)),
        (T('DB Model'), False,
         URL(
         'admin', 'default', 'edit/%s/models/db.py' % app)),
        (T('Menu Model'), False,
         URL(
         'admin', 'default', 'edit/%s/models/menu.py' % app)),
        (T('Database'), False, URL(app, 'appadmin', 'index')),
        (T('Errors'), False, URL(
         'admin', 'default', 'errors/' + app)),
        (T('About'), False, URL(
         'admin', 'default', 'about/' + app)),
        ]),
            ('web2py.com', False, 'http://www.web2py.com', [
             (T('Download'), False,
              'http://www.web2py.com/examples/default/download'),
             (T('Support'), False,
              'http://www.web2py.com/examples/default/support'),
             (T('Demo'), False, 'http://web2py.com/demo_admin'),
             (T('Quick Examples'), False,
              'http://web2py.com/examples/default/examples'),
             (T('FAQ'), False, 'http://web2py.com/AlterEgo'),
             (T('Videos'), False,
              'http://www.web2py.com/examples/default/videos/'),
             (T('Free Applications'),
              False, 'http://web2py.com/appliances'),
             (T('Plugins'), False, 'http://web2py.com/plugins'),
             (T('Layouts'), False, 'http://web2py.com/layouts'),
             (T('Recipes'), False, 'http://web2pyslices.com/'),
             (T('Semantic'), False, 'http://web2py.com/semantic'),
             ]),
            (T('Documentation'), False, 'http://www.web2py.com/book', [
             (T('Preface'), False,
              'http://www.web2py.com/book/default/chapter/00'),
             (T('Introduction'), False,
              'http://www.web2py.com/book/default/chapter/01'),
             (T('Python'), False,
              'http://www.web2py.com/book/default/chapter/02'),
             (T('Overview'), False,
              'http://www.web2py.com/book/default/chapter/03'),
             (T('The Core'), False,
              'http://www.web2py.com/book/default/chapter/04'),
             (T('The Views'), False,
              'http://www.web2py.com/book/default/chapter/05'),
             (T('Database'), False,
              'http://www.web2py.com/book/default/chapter/06'),
             (T('Forms and Validators'), False,
              'http://www.web2py.com/book/default/chapter/07'),
             (T('Email and SMS'), False,
              'http://www.web2py.com/book/default/chapter/08'),
             (T('Access Control'), False,
              'http://www.web2py.com/book/default/chapter/09'),
             (T('Services'), False,
              'http://www.web2py.com/book/default/chapter/10'),
             (T('Ajax Recipes'), False,
              'http://www.web2py.com/book/default/chapter/11'),
             (T('Components and Plugins'), False,
              'http://www.web2py.com/book/default/chapter/12'),
             (T('Deployment Recipes'), False,
              'http://www.web2py.com/book/default/chapter/13'),
             (T('Other Recipes'), False,
              'http://www.web2py.com/book/default/chapter/14'),
             (T('Buy this book'), False,
              'http://stores.lulu.com/web2py'),
             ]),
            (T('Community'), False, None, [
             (T('Groups'), False,
              'http://www.web2py.com/examples/default/usergroups'),
                        (T('Twitter'), False, 'http://twitter.com/web2py'),
                        (T('Live Chat'), False,
                         'http://webchat.freenode.net/?channels=web2py'),
                        ]),
                (T('Plugins'), False, None, [
                        ('plugin_wiki', False,
                         'http://web2py.com/examples/default/download'),
                        (T('Other Plugins'), False,
                         'http://web2py.com/plugins'),
                        (T('Layout Plugins'),
                         False, 'http://web2py.com/layouts'),
                        ])
                ]
         )]
if DEVELOPMENT_MENU: _()
