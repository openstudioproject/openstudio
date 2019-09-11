# -*- coding: utf-8 -*-

from mollie.api.client import Client
from mollie.api.error import Error as MollieError

from general_helpers import workshops_get_full_workshop_product_id
from general_helpers import datestr_to_python
from general_helpers import iso_to_gregorian
from general_helpers import NRtoDay
from general_helpers import get_lastweek_year


def index():
    """
        Main page of the shop
    """
    response.title= T('Shop')

    #response.view = 'cl/cl.html'

    content = ''

    return dict(content = content)


def contact():
    """
        Page to hold contact info page for shop
    """
    response.title = T('Contact')
    # Company info
    try:
        organization = ORGANIZATIONS[ORGANIZATIONS['default']]

        company_name = organization['Name']
        company_address = organization['Address']
        company_email = organization['Email'] or ''
        company_phone = organization['Phone'] or ''
        company_registration = organization['Registration'] or ''
        company_tax_registration = organization['TaxRegistration'] or ''
        company_terms_conditions_url = organization['TermsConditionsURL']
        company_privacy_policy_url = organization['PrivacyNoticeURL']
    except KeyError:
        company_name = ''
        company_address = ''
        company_email = ''
        company_phone = ''
        company_registration = ''
        company_tax_registration = ''
        company_terms_conditions_url = ''
        company_privacy_policy_url = ''

    # Logo
    branding_logo = os.path.join(request.folder,
                                 'static',
                                 'plugin_os-branding',
                                 'logos',
                                 'branding_logo_login.png')
    if os.path.isfile(branding_logo):
        logo_img = IMG(_src=URL('static',
                       'plugin_os-branding/logos/branding_logo_login.png'))
        logo_text = ''
        company = ''
        logo_class = 'logo_login'

        logo_login = DIV(logo_img, logo_text, BR(),
                         company,
                         _class=logo_class)
    else:
        logo_login = ''


    return dict(company_name=company_name,
                company_address=XML(company_address),
                company_email=company_email,
                company_phone=company_phone,
                company_registration=company_registration,
                company_terms_conditions_url=company_terms_conditions_url,
                company_privacy_policy_url=company_privacy_policy_url,
                logo_login=logo_login)


def classcards():
    """
        List available classcards
    """
    from openstudio.os_school import School

    response.title = T('Shop')
    response.subtitle = T('Class cards')
    response.view = 'shop/no_box.html'

    auth_user_id = None
    if auth.user:
        auth_user_id = auth.user.id

    cards = T('No cards available at this time, please check back later.')
    features = db.customers_shop_features(1)
    if features.Classcards:
        school = School()
        cards = school.get_classcards_formatted(
            auth_user_id,
            public_only=True,
            per_row=3,
            link_type='shop'
        )

    return dict(content=cards)

#
# def cart_get_price_total(rows):
#     """
#         @return: total price for items in shopping cart
#     """
#     from openstudio.os_class import Class
#     from openstudio.os_workshop_product import WorkshopProduct
#
#     cuID = auth.user.id
#
#     total = 0
#     for row in rows:
#         if row.customers_shoppingcart.workshops_products_id:
#             wsp = WorkshopProduct(row.customers_shoppingcart.workshops_products_id)
#             total += wsp.get_price_for_customer(row.customers_shoppingcart.auth_customer_id) or 0
#
#         if row.customers_shoppingcart.school_classcards_id:
#             total += row.school_classcards.Price or 0
#
#         if row.customers_shoppingcart.classes_id:
#             cls = Class(row.customers_shoppingcart.classes_id,
#                         row.customers_shoppingcart.ClassDate)
#             prices = cls.get_prices_customer(cuID)
#
#             if row.customers_shoppingcart.AttendanceType == 1:
#                 total += prices['trial']
#             elif row.customers_shoppingcart.AttendanceType == 2:
#                 total += prices['dropin']
#
#
#     return total
#
#
# @auth.requires_login()
# def cart():
#     """
#         Page showing shopping cart for customer
#     """
#     from openstudio.os_customer import Customer
#
#     response.title = T('Shopping cart')
#     response.subtitle = ''
#
#     customer = Customer(auth.user.id)
#     messages = customer.shoppingcart_maintenance()
#     alert = ''
#     if len(messages):
#         alert_content = SPAN()
#         for m in messages:
#             alert_content.append(m)
#             alert_content.append(BR())
#
#         alert = os_gui.get_alert('info', alert_content, dismissable=True)
#
#     rows = customer.get_shoppingcart_rows()
#
#     total = SPAN(CURRSYM, ' ', format(cart_get_price_total(rows), '.2f'))
#
#
#     order = ''
#     if len(rows):
#         order = A(B(T('Proceed to Checkout')),
#                   _href=URL('checkout'),
#                   _class='btn btn-primary pull-right')
#
#     return dict(rows=rows, total=total, order=order, progress='', messages=alert)


def checkout_get_progress(function):
    """
        :param function:
        :return: Formatted tracker to show checkout progress to customer
    """
    checkout_progress = DIV(_class='center')

    spacer = SPAN(' ', os_gui.get_fa_icon('fa-chevron-right'), ' ', _class='grey small_font')
    active_class = 'text-green bold'
    checkout_class = ''
    received_class = ''
    complete_class = ''

    step_order = [
        'classcard',
        'membership',
        'subscription',
        'event_ticket',
        'class_checkout',
    ]

    if function in step_order :
        checkout_class = active_class

    checkout_progress.append(SPAN(T('Order'), _class=checkout_class))
    checkout_progress.append(spacer)

    step_received = [
        'classcard_order',
        'membership_order',
        'subscription_order',
        'event_ticket_order',
        'class_order'
    ]

    if function in step_received:
        received_class = active_class

    checkout_progress.append(SPAN(T('Payment'), _class=received_class))
    checkout_progress.append(spacer)

    if function == 'complete':
        complete_class = active_class

    checkout_progress.append(SPAN(T('Complete'), _class=complete_class))
    checkout_progress.append(BR())
    checkout_progress.append(BR())

    return checkout_progress


def checkout_get_form_order(submit_button="Place order"):
    """
    :return: SQLForm to create an order
    """
    db.customers_orders.Status.readable = False
    db.customers_orders.Status.writable = False
    db.customers_orders.Origin.readable = False
    db.customers_orders.Origin.writable = False
    db.customers_orders.DateCreated.readable = False
    db.customers_orders.DateCreated.writable = False

    db.customers_orders.auth_customer_id.default = auth.user.id

    form = SQLFORM(
        db.customers_orders,
        formstyle="bootstrap3_stacked",
        submit_button=T(submit_button)
    )

    return form


def order_received_redirect_complete(coID):
    """
        Handle free products/events
        :param coID: db.customers_orders.id
    """
    from openstudio.os_order import Order

    order = Order(coID)
    result = order.deliver()
    redirect(URL('shop', 'complete', vars={'coID': coID}))


def order_received_mail_customer(coID):
    """
        Send an email to a customer after getting an order
    """
    """
        Mail email with invoice to customer
    """
    from openstudio.os_mail import OsMail

    osmail = OsMail()
    msgID = osmail.render_email_template(
        'order_received',
        customers_orders_id=coID
    )

    osmail.send_and_archive(msgID, auth.user.id)


def checkout_order_membership(smID, order):
    """
        Add class card to order
    """
    items = order.get_order_items_rows()
    membership_already_ordered = False
    for item in items:
        if item.customers_orders_items.school_memberships_id == int(smID):
            membership_already_ordered = True
            break

    if not membership_already_ordered:
        order.order_item_add_membership(smID, TODAY_LOCAL)


def checkout_order_classcard(scdID, order):
    """
        Add class card to order
    """
    items = order.get_order_items_rows()
    card_already_ordered = False
    for item in items:
        if item.customers_orders_items.school_classcards_id == int(scdID):
            card_already_ordered = True
            break

    if not card_already_ordered:
        order.order_item_add_classcard(scdID)


def checkout_order_subscription(ssuID, order):
    """
        Add subscription to order
    """
    items = order.get_order_items_rows()
    already_ordered = False
    for item in items:
        if item.customers_orders_items.school_subscriptions_id == int(ssuID):
            already_ordered = True
            break

    if not already_ordered:
        order.order_item_add_subscription(ssuID)


def checkout_order_workshop_product(wspID, order):
    """
        :param wspID: db.workshops_products.id
        :param order: Order object
        :return: None
    """
    items = order.get_order_items_rows()
    already_ordered = False
    for item in items:
        if item.customers_orders_items.workshops_products_id == int(wspID):
            already_ordered = True
            break

    if not already_ordered:
        order.order_item_add_workshop_product(wspID)


def checkout_order_class(clsID, class_date, attendance_type, order):
    """
        :param clsID: db.classes
        :param order: Order object
        :return: None
    """
    items = order.get_order_items_rows()
    already_ordered = False
    for item in items:
        if item.customers_orders_items.classes_id == int(clsID) and item.customers_orders_items.ClassDate == class_date:
            already_ordered = True
            break

    if not already_ordered:
        order.order_item_add_class(clsID, class_date, attendance_type)


@auth.requires_login()
def complete():
    """
        Landing page for customer after Mollie session
    """
    from openstudio.os_order import Order
    from openstudio.os_invoice import Invoice

    response.title = T('Shop')

    iID = request.vars['iID']
    coID = request.vars['coID']

    content_body = ''
    progress = ''
    donation = False
    # Check if the order belongs to the currently logged in user
    if coID:
        order = Order(coID)
        amounts = order.get_amounts()


        # Does this order belong to this customer?
        if not order.order.auth_customer_id == auth.user.id:
            session.flash = T("Unable to show order")
            redirect(URL('profile', 'index'))

        # Do we have a donation?
        if order.order.Donation:
            donation = True

        if not donation:
            progress = checkout_get_progress(request.function)
            success_header = T('Thank you!')
            online_payment_provider = get_sys_property('online_payment_provider')
            if online_payment_provider == 'disabled':
                success_msg = T('All items from the order have been added to your profile and an invoice has been \
                                added to your account.')
            else:
                success_msg = SPAN()
                if amounts.TotalPriceVAT:
                    success_msg.append(T('We have received the payment for your order.'))
                    success_msg.append(BR())
                success_msg.append(T('All items listed have been added to your account.'))
        else:
            success_header = T('Thank you for your donation!')
            success_msg = T("You're awesome! Please click below to continue...")


        msg_success = DIV(H4(success_header),
                          success_msg,
                          BR(), BR(),
                          DIV(A(T('Continue'), " ", os_gui.get_fa_icon('fa-angle-double-right'),
                                _href=URL('profile', 'index'),
                                _class='btn btn-default')),
                          _class='')

        msg_fail = DIV(H4(T('Looks like something went wrong with your payment...')),
                       SPAN(T("Believe this is a mistake? Please"), ' ',
                            A(T('contact'), _href=URL('shop', 'contact')), ' ',
                            T('us.'),
                            _class='grey'),
                       _class='center')

        if order.order.Status == 'delivered':
            if donation:
                response.subtitle = T('Donation received')
            else:
                response.subtitle = T('Payment received')
            content_body = msg_success
        else:
            response.subtitle = T('No payment received')
            content_body = msg_fail

    # Check if the invoice belongs to the currently logged in user
    if iID:
        invoice = Invoice(iID)

        if not invoice.get_linked_customer_id() == auth.user.id:
            session.flash = T("Unable to show invoice")
            redirect(URL('profile', 'index'))


        msg_fail = DIV(H4(T('Looks like something went wrong with your payment...')),
                       SPAN(T("Believe this is a mistake? Please"), ' ',
                            A(T('contact'), _href=URL('shop', 'contact')), ' ',
                            T('us.'),
                            _class='grey'),
                       _class='center')

        if invoice.invoice.Status == 'paid':
            session.flash = SPAN(B(T('Thank you')), BR(),
                                 T('Payment received for invoice ' + invoice.invoice.InvoiceID))
            redirect(URL('profile', 'invoices'))
            #response.subtitle = T('Payment received')
            #content = msg_success
        else:
            response.subtitle = T('No payment received')
            content_body = msg_fail

    order_summary = ""
    if coID:
        order_summary = order.get_order_items_summary_display()

    content = DIV(
        DIV(content_body, _class='col-md-6'),
        DIV(H4(T("Order summary")),
            order_summary,
            _class='col-md-6'),
        _class="row"
    )


    # What would you like to do next? Continue shopping or go to your profile?

    return dict(content=content, progress=progress)


def _event_check_exists(wsID):
    """
    It might happen that a customer bookmarks an event, which is no longer available due to being
    deleted. It should show a decent message.
    :return:
    """
    wsID = int(wsID)
    query = (db.workshops.Archived == False) & \
            (db.workshops.PublicWorkshop == True)

    rows = db(query).select(db.workshops.id)
    ids = []
    for row in rows:
        ids.append(row.id)

    if not wsID in ids:
        redirect(URL('event_not_found'))


def event_not_found():
    """

    :return:
    """
    response.title = T('Shop')
    response.subtitle = T('Event not found')
    response.view = 'shop/index.html'

    content = DIV(
        T("It looks like the event you're looking for is no longer available."), ' ',
        T("It's most likely in the past."), BR(),
        T("Please use the button below to view our current and upcoming events."), BR(), BR(),
        os_gui.get_button(
            'noicon',
            URL('events'),
            title=T("Current events"),
            btn_size='',
            btn_class='btn-primary'
        ),
        _class='center'
    )

    back = os_gui.get_button('back', URL('shop', 'events'))

    return dict(content=content,
                back=back,
                og_title='',
                og_description='',
                og_url='',
                og_image='')


def event():
    """
        Details for an event
    """
    from openstudio.os_workshop import Workshop

    wsID = request.vars['wsID']
    _event_check_exists(wsID)

    workshop = Workshop(wsID)
    response.title = T('Shop')
    response.subtitle = T('Event')

    if workshop.Startdate == workshop.Enddate or not workshop.Enddate:
        info_date = workshop.Startdate_formatted
    else:
        info_date = SPAN(workshop.Startdate_formatted, ' - ',
                         workshop.Enddate_formatted)

    workshop_info = DIV(
        H2(T('Information'), _class='no-margin-top'),
        XML(workshop.Description)
    )

    result = event_get_products_filter_prices_book_buttons(workshop)
    products_filter = result['products_filter']
    products_prices = result['products_prices']
    add_to_cart_buttons = result['add_to_cart_buttons']
    activities = event_get_activities(workshop)
    fullwspID = workshops_get_full_workshop_product_id(wsID)

    content = DIV(
        DIV(
            DIV(H2(workshop.Name),
                H4(workshop.Tagline),
                _class="col-md-10 col-md-offset-1"),
            _class='row'),
        DIV(DIV(_class='col-md-1'),
            event_get_pictures(workshop),
            DIV(XML(workshop.Description),
                _class='col-md-6'),
            DIV(_class='col-md-1'),
            _class='row shop_workshop_info'),
        DIV(DIV(products_filter,
                _class="col-md-10 col-md-offset-1"),
            _class='row shop_workshop_tickets'),
        activities,
        BR(), BR(),
        DIV(DIV(products_prices,
                _class="col-md-10 col-md-offset-1"),
            _class="row"),
        #DIV(workshop_get_button_book(fullwspID), _class='center'),
        DIV(DIV(add_to_cart_buttons,
                _class="col-md-10 col-md-offset-1"),
            _class="row"),
        _class='shop_workshop')

    #TODO: add teacher info
    #TODO: add location info

    features = db.customers_shop_features(1)
    if not features.Workshops:
        content = T('This feature is disabled')

    back = os_gui.get_button('back', URL('shop', 'events'))

    return dict(content=content,
                back=back,
                og_title=workshop.Name,
                og_description=workshop.Tagline, 
                og_url=URL('shop', 'event', vars={'wsID':wsID}, scheme=True, host=True),
                og_image=URL('default', 'download', args=workshop.picture))


def event_get_pictures(workshop):
    """
    :param wsID: db.workshops.id
    :return: pictures for event
    """
    def get_img_thumbnail(thumbsmall, thumblarge):
        return IMG(_src=URL('default', 'download', args=thumbsmall),
                   _data_link=URL('default', 'download', args=thumblarge),
                   _class='workshop_thumbsmall clickable')

    count_thumbnails = 0
    thumbnails = DIV(_class='shop_workshop_thumbnails')

    if workshop.picture:
        count_thumbnails += 1
        thumbnails.append(get_img_thumbnail(workshop.thumbsmall,
                                            workshop.thumblarge))
    if workshop.picture_2:
        count_thumbnails += 1
        thumbnails.append(get_img_thumbnail(workshop.thumbsmall_2,
                                            workshop.thumblarge_2))
    if workshop.picture_3:
        count_thumbnails += 1
        thumbnails.append(get_img_thumbnail(workshop.thumbsmall_3,
                                            workshop.thumblarge_3))
    if workshop.picture_4:
        count_thumbnails += 1
        thumbnails.append(get_img_thumbnail(workshop.thumbsmall_4,
                                            workshop.thumbsmall_4))
    if workshop.picture_5:
        count_thumbnails += 1
        thumbnails.append(get_img_thumbnail(workshop.thumbsmall_5,
                                            workshop.thumblarge_5))



    pictures = DIV(IMG(_src=URL('default', 'download', args=workshop.thumblarge),
                       _class='workshop_image',
                       _id='workshop_thumblarge'),
                   _class='col-md-4')

    if count_thumbnails > 1:
        pictures.append(thumbnails)

    return pictures


def event_get_products_filter_prices_book_buttons(workshop):
    """
        :param workshop: Workshop object
        :return: div button group for products filter
    """
    from openstudio.os_workshop_product import WorkshopProduct

    #NOTE: maybe add prices here as well, saves a db query to get the products again
    # products_filter = DIV(_class='btn-group workshop-products-filter', _role='group', **{'_data-toggle':'buttons'})
    products_filter = DIV()
    products_prices = DIV()
    products_select = SELECT(_id='workshops-products-select', _name='products')
    add_to_cart_buttons = DIV(_class='workshop-add-to-cart-buttons')

    # get public workshops
    products = workshop.get_products(filter_public=True)

    sold_out = False

    for i, product in enumerate(products):
        # Products filter
        # label_class = 'btn btn-default'
        label_class= ''
        if i == 0:
            label_class += ' active fullws'

        # Check if a product has been sold out
        sold_out = False
        wsp = WorkshopProduct(product.id)
        if wsp.is_sold_out():
            sold_out = True

        if sold_out:
            label_class += ' sold_out'

        if auth.user:
            price = wsp.get_price_for_customer(auth.user.id)
        else:
            price = product.Price

        if product.FullWorkshop:
            products_filter.append(
                LABEL(INPUT(_type='radio',
                            _name='products',
                            _checked='checked',
                            _id=product.id,
                            _class=label_class),
                      product.Name, ' (', CURRSYM, ' ', format(price, '.2f'), ')'))
        else:
            products_filter.append(
                LABEL(XML('<input type="radio" name="products" id="{id}" class="{label_class}">'.format(
                          id=product.id,
                          label_class=label_class)),
                      product.Name, ' (', CURRSYM, ' ', format(price, '.2f'), ')'))
        products_filter.append(BR())

        # Products prices
        price_class = 'workshop_price'
        if i == 0:
            price_class += ' fullws_price'

        if sold_out:
            display_price = T("Sold out")
        else:
            # Set price
            if product.Price:
                display_price = SPAN(CURRSYM, ' ', format(price, '.2f'))
            else:
                display_price = T("No admission fee")

            # Check for donation
            if product.Donation:
                display_price = T("Donation based")

        products_prices.append(DIV(display_price,
                                   _class=price_class,
                                   _id='wsp_price_'+str(product.id),
                                   _style='display: none;'))

        # add to cart buttons
        btn_text = T('Buy ticket')
        btn_class = 'btn-success'
        _target = ''

        link_class = 'workshop_book_now'
        if i == 0:
            link_class += ' fullws_book_now'

        if product.ExternalShopURL:
            _target='_blank'
            button_icon = 'noicon'
            btn_class = 'btn-primary'
            url = product.ExternalShopURL
            if product.AddToCartText:
                btn_text = product.AddToCartText
        else:
            url = URL('shop', 'event_ticket', vars={'wspID':product.id})
            button_icon = 'ticket'

        add_to_cart = os_gui.get_button(button_icon,
                url,
                btn_class=btn_class,
                btn_size='',
                title=btn_text,
                _class=link_class,
                _style='display: none;',
                _target=_target,
                _id='add_to_cart_' + str(product.id)) if not sold_out else ""

        add_to_cart_buttons.append(add_to_cart)

    products_filter = DIV(H3(T("Tickets")),
        products_filter),

    if len(products) == 1:
        products_filter = ''

    return dict(products_filter=products_filter,
                products_prices=products_prices,
                add_to_cart_buttons=add_to_cart_buttons)


def event_get_activities(workshop):
    """
        :param workshop: Workshop object
        :return: responsive list of activities
    """
    activities = DIV(
        DIV(DIV(T('Date'), _class='col-md-2'),
            DIV(T('Time'), _class='col-md-2'),
            DIV(T('Activity'), _class='col-md-3'),
            DIV(T('Teacher'), _class='col-md-3'),
            DIV(T('Location'), _class='col-md-2'),
            _class='row bold hidden-sm hidden-xs workshop-activity-header')
    )

    rows = workshop.get_activities()
    for i, row in enumerate(rows):
        repr_row = list(rows[i:i+1].render())[0]

        products = event_get_activities_get_products(row.id)
        class_product_ids = ''
        for product_id in products:
            class_product_ids += ' '
            class_product_ids += str(product_id)

        activity_date = row.Activitydate.strftime('%d %B %Y')
        activity_time = SPAN(repr_row.Starttime, ' - ', repr_row.Endtime)
        activity_name = repr_row.Activity
        activity_teacher = repr_row.auth_teacher_id
        activity = DIV(
            DIV(activity_date, _class='col-md-2'),
            DIV(activity_time, _class='col-md-2'),
            DIV(activity_name, _class='col-md-3'),
            DIV(activity_teacher, _class='col-md-3'),
            DIV(SPAN(repr_row.school_locations_id), _class='col-md-2'),
            _class='row workshop-activity hidden-sm hidden-xs' + class_product_ids)
            #_class='row workshop-activity' + class_product_ids)

        activities.append(activity)

        activity_mobile = DIV(
            DIV(SPAN(os_gui.get_fa_icon('fa-calendar-o')), ' ',
                activity_date, ' ',
                #' @ ',
                os_gui.get_fa_icon('fa-clock-o'), ' ',
                activity_time,
                _class='col-sm-12 col-xs-12 mobile-bold'),
            DIV(activity_name, T(' with '), activity_teacher, _class='col-sm-12 grey'),
            DIV(SPAN(repr_row.school_locations_id), _class='col-sm-12 grey'),
            _class='row workshop-activity hidden-md hidden-lg'  + class_product_ids)
            #_class='row mobile-center workshop-activity'  + class_product_ids)

        activities.append(activity_mobile)

    return DIV(DIV(H3(T('Agenda')), activities, _class='col-md-10 col-md-offset-1'),
               _class='row workshop-activities')


def event_get_activities_get_products(wsaID):
    """
        :param wsaID: db.workshops_activities.id
        :return: list of workshop products this activity is linked to
    """
    query = (db.workshops_products_activities.workshops_activities_id == wsaID)
    rows = db(query).select(db.workshops_products_activities.workshops_products_id)

    product_ids = []
    for row in rows:
        product_ids.append(row.workshops_products_id)

    return product_ids


@auth.requires_login()
def event_ticket():
    """
    Ticket order page
    :return:
    """
    from openstudio.os_customer import Customer
    from openstudio.os_workshop_product import WorkshopProduct

    response.title= T('Shop')
    response.subtitle = T('Event')
    response.view = 'shop/index.html'

    features = db.customers_shop_features(1)
    if not features.Workshops:
        return T('This feature is disabled')

    wspID = request.vars['wspID']
    wsp = WorkshopProduct(wspID)

    # check if we require a complete profile
    shop_requires_complete_profile = get_sys_property('shop_requires_complete_profile_events')
    if shop_requires_complete_profile:
        check_add_to_cart_requires_complete_profile(
            auth.user.id,
            _next=URL(request.controller, request.function, vars={'wspID': wspID})
        )

    ticket_info = event_ticket_get_info(wsp)
    form = checkout_get_form_order()
    if form.process().accepted:
        redirect(URL('shop', 'event_ticket_order',
                     vars={'coID': form.vars.id,
                           'wspID': wspID}))

    checkout_message_events = get_sys_property('shop_checkout_message_events') or ''
    checkout_message = ''
    if checkout_message_events:
        checkout_message = DIV(
            H4(T("Order info")),
            XML(checkout_message_events), BR(),
            _class='col-md-6'
        )

    ## Membership check
    customer = Customer(auth.user.id)

    m_required = ''
    m_required_message = ''

    content = DIV(
        DIV(
            DIV(H4(T("Selected ticket")), BR(),
                ticket_info,
                BR(),
                _class='col-md-6'
            ),
            checkout_message,
            _class="col-md-12"
        ),
        DIV(
            DIV(form, _class='col-md-12'),
            _class='col-md-12'
        ),
    _class="row")

    back = os_gui.get_button(
        'back',
        URL('classcards')
    )

    return dict(content=content, back=back, progress=checkout_get_progress(request.function))


def event_ticket_get_info(wsp):
    """
    Get workshop product info
    :param wsp: WorkshopProduct object
    :return:
    """
    info = UL(
        LI(B(T("Workshop")), BR(), wsp.workshop_name),
        LI(B(T("Ticket")), BR(), wsp.name),
        # LI(B(T("Price")), BR(), represent_decimal_as_amount(wsp.price)),
        LI(B(T("Price")), BR(), represent_decimal_as_amount(wsp.get_price_for_customer(auth.user.id))),
    )

    if wsp.description:
        info.append(
            LI(B(T("Description")), BR(), wsp.description)
        )

    return info


@auth.requires_login()
def event_ticket_order():
    """
    Event ticket order confirmation and link to payment or complete without payment
    """
    from openstudio.os_customer import Customer
    from openstudio.os_order import Order
    from openstudio.os_workshop_product import WorkshopProduct

    response.title= T('Shop')
    response.subtitle = T('Order confirmation')
    response.view = 'shop/index.html'

    features = db.customers_shop_features(1)
    if not features.Workshops:
        return T("This feature is disabled")

    wspID = request.vars['wspID']
    coID = request.vars['coID']
    wsp = WorkshopProduct(wspID)
    order = Order(coID)
    # Set status awaiting payment
    order.set_status_awaiting_payment()

    # Add items to order
    customer = Customer(auth.user.id)
    checkout_order_workshop_product(wspID, order)

    # mail order to customer
    order_received_mail_customer(coID)

    # check if this order needs to be paid or it's free and can be added to the customers' account straight away
    amounts = order.get_amounts()

    if not amounts:
        order_received_redirect_complete(coID)
    elif amounts.TotalPriceVAT == 0:
        order_received_redirect_complete(coID)

    # Check if an online payment provider is enabled:
    online_payment_provider = get_sys_property('online_payment_provider')
    if online_payment_provider == 'disabled':
        # no payment provider, deliver order and redirect to complete.
        order.deliver()
        redirect(URL('complete', vars={'coID':coID}))

    # We have a payment provider, lets show a pay now page!
    pay_now = A(T("Pay now"), ' ',
                os_gui.get_fa_icon('fa-angle-right'),
                _href=URL('mollie', 'order_pay', vars={'coID': coID}),
                _class='btn btn-success bold')

    content = DIV(
        DIV(H4(T('We have received your order')),
            T("The items in your order will be delivered as soon as we've received the payment for this order."), BR(),
            T("Click 'Pay now' to complete the payment."), BR(),
            BR(), BR(),
            pay_now,
            _class='col-md-6'
        ),
        DIV(H4(T("Order summary")),
            order.get_order_items_summary_display(),
            _class="col-md-6"),
        _class='row')

    # Send sys notification
    os_mail = OsMail()
    os_mail.send_notification(
        'order_created',
        customers_orders_id=coID
    )

    return dict(content=content, progress=checkout_get_progress(request.function))


def events():
    """
        Events list for shop
    """
    from openstudio.os_workshop_schedule import WorkshopSchedule

    response.title= T('Shop')
    response.subtitle = T('Events')

    content = T('No workshops available at this time, please check back later.')
    features = db.customers_shop_features(1)
    if features.Workshops:
        workshop_schedule = WorkshopSchedule(
            filter_date_start = TODAY_LOCAL
        )
        content = workshop_schedule.get_workshops_shop()

    return dict(content = content)


def memberships():
    """
        Memberships list for shop
    """
    from openstudio.os_school import School

    response.title= T('Shop')
    response.subtitle = T('Memberships')
    response.view = 'shop/no_box.html'

    content = T('No memberships available at this time, please check back later.')
    features = db.customers_shop_features(1)
    if features.Memberships:
        school = School()
        content = school.get_memberships_formatted(public_only=True, link_type='shop')

    return dict(content = content)


def membership():
    """
        Buy membership confirmation page
    """
    from openstudio.os_customer import Customer
    from openstudio.os_school_membership import SchoolMembership

    response.title= T('Shop')
    response.subtitle = T('Membership')
    response.view = 'shop/index.html'

    smID = request.vars['smID']

    features = db.customers_shop_features(1)
    if not features.Memberships:
        return T('This feature is disabled')

    # check if we require a complete profile
    shop_requires_complete_profile = get_sys_property('shop_requires_complete_profile_memberships')
    if shop_requires_complete_profile:
        check_add_to_cart_requires_complete_profile(
            auth.user.id,
            _next = URL(request.controller, request.function, vars={'smID': smID})
        )

    sm = SchoolMembership(smID)
    price = sm.row.Price

    response.subtitle += ' '
    response.subtitle += sm.row.Name

    general_terms = get_sys_property('shop_memberships_terms')
    specific_terms = sm.row.Terms

    terms = DIV()
    if general_terms:
        terms.append(B(T('General terms & conditions')))
        terms.append(XML(general_terms))
    if specific_terms:
        terms.append(B(T('Membership specific terms & conditions')))
        terms.append(XML(specific_terms))

    conditions = DIV(terms, _class='well')

    form = checkout_get_form_order()
    if form.process().accepted:
        redirect(URL('shop', 'membership_order',
                     vars={'coID': form.vars.id,
                           'smID': smID}))

    checkout_message_memberships = get_sys_property('shop_checkout_message_memberships') or ''
    checkout_message = ''
    if checkout_message_memberships:
        checkout_message = DIV(
            H4(T("Order info")),
            XML(checkout_message_memberships), BR(),
            _class='col-md-6'
        )


    ## Membership check
    customer = Customer(auth.user.id)

    membership = SchoolMembership(smID)
    message_agree = DIV(
        BR(),
        B((os_gui.get_fa_icon('fa-exclamation-circle')), " ",
          T("By ordering this card you agree to the terms and conditions for the required membership")), BR(),
        BR(),
        _class="col-md-12"
    )

    content = DIV(
        DIV(
            DIV(H4(T("Selected membership")), BR(),
                membership_get_info(membership),
                BR(),
                _class='col-md-6'
            ),
            DIV(H4(T("Terms & Conditions")),
                subscription_get_membership_terms(membership),
                _class='col-md-6'
            ),
            checkout_message,
            _class="col-md-12"
        ),
        DIV(
            message_agree,
            DIV(form, _class='col-md-12'),
            _class='col-md-12'
        ),
    _class="row")

    back = os_gui.get_button(
        'back',
        URL('classcards')
    )

    return dict(content=content, back=back, progress=checkout_get_progress(request.function))

    # confirm = A(B(T('I agree')),
    #             _href=URL('mollie', 'membership_buy_now', vars={'smID':smID}),
    #             _class='btn btn-primary')
    # cancel = A(B(T('Cancel')),
    #            _href=URL('memberships'),
    #            _class='btn btn-default')
    #
    # content = DIV(H4(T('Terms & conditions')),
    #               conditions,
    #               confirm,
    #               cancel)

    return dict(content=content)


def membership_get_info(sm):
    """
    :param sm: SchoolMembership object
    :return: UL with subscription info
    """
    info = UL(
        LI(B(T("Membership")), BR(), sm.row.Name),
        LI(B(T("Price")), BR(), represent_decimal_as_amount(sm.row.Price)),
        LI(B(T("Validity")), BR(), sm.get_validity_formatted()),
    )
    if sm.row.Description:
        info.append(
            LI(B(T("Additional info")), BR(), sm.row.Description)
        )

    return info


@auth.requires_login()
def membership_order():
    """
    Membership order confirmation and link to payment or complete without payment
    """
    from openstudio.os_customer import Customer
    from openstudio.os_order import Order
    from openstudio.os_school_membership import SchoolMembership

    response.title= T('Shop')
    response.subtitle = T('Order confirmation')
    response.view = 'shop/index.html'

    features = db.customers_shop_features(1)
    if not features.Memberships:
        return T("This feature is disabled")

    smID = request.vars['smID']
    coID = request.vars['coID']
    scd = SchoolMembership(smID)
    order = Order(coID)
    # Set status awaiting payment
    order.set_status_awaiting_payment()

    # Add items to order
    customer = Customer(auth.user.id)
    checkout_order_membership(smID, order)

    # mail order to customer
    order_received_mail_customer(coID)

    # check if this order needs to be paid or it's free and can be added to the customers' account straight away
    amounts = order.get_amounts()

    if not amounts:
        order_received_redirect_complete(coID)
    elif amounts.TotalPriceVAT == 0:
        order_received_redirect_complete(coID)

    # Check if an online payment provider is enabled:
    online_payment_provider = get_sys_property('online_payment_provider')
    if online_payment_provider == 'disabled':
        # no payment provider, deliver order and redirect to complete.
        order.deliver()
        redirect(URL('classcard_order_complete', vars={'coID':coID}))


    # We have a payment provider, lets show a pay now page!
    pay_now = A(T("Pay now"), ' ',
                os_gui.get_fa_icon('fa-angle-right'),
                _href=URL('mollie', 'order_pay', vars={'coID': coID}),
                _class='btn btn-success bold')

    content = DIV(
        DIV(H4(T('We have received your order')),
            T("The items in your order will be delivered as soon as we've received the payment for this order."), BR(),
            T("Click 'Pay now' to complete the payment."), BR(),
            BR(), BR(),
            pay_now,
            _class='col-md-6'
        ),
        DIV(H4(T("Order summary")),
            order.get_order_items_summary_display(),
            _class="col-md-6"),
        _class='row')

    # Send sys notification
    os_mail = OsMail()
    os_mail.send_notification(
        'order_created',
        customers_orders_id=coID
    )

    return dict(content=content, progress=checkout_get_progress(request.function))


def subscriptions():
    """
        Subscriptions list in shop
    """
    from openstudio.os_school import School

    response.title= T('Shop')
    response.subtitle = T('Subscriptions')
    response.view = 'shop/no_box.html'

    auth_user_id = None
    if auth.user:
        auth_user_id = auth.user.id

    content = T('No subscriptions available at this time, please check back later.')
    features = db.customers_shop_features(1)
    if features.Subscriptions:
        school = School()
        content = school.get_subscriptions_formatted(auth_user_id, public_only=True, link_type='shop')

    return dict(content = content)


def subscription_check_valid_bankdetails(payment_method, ssuID):
    """

    :param var:
    :return:
    """
    if payment_method != 'mollie' :
        query = ((db.customers_payment_info.auth_customer_id == auth.user.id) &
                 (db.customers_payment_info.AccountNumber != None) &
                 (db.customers_payment_info.AccountHolder != None))
        complete_bankaccount_details = db(query).count()

        if not complete_bankaccount_details:
             redirect(URL('subscription_add_bankaccount', vars={'ssuID': ssuID}))


@auth.requires_login()
def subscription():
    """
        Buy subscription confirmation page
    """
    from openstudio.os_customer import Customer
    from openstudio.os_school_subscription import SchoolSubscription
    from openstudio.os_school_membership import SchoolMembership

    response.title= T('Shop')
    response.subtitle = T('Subscription')
    response.view = 'shop/index.html'

    features = db.customers_shop_features(1)
    if not features.Subscriptions:
        return T('This feature is disabled')

    ssuID = request.vars['ssuID']
    ssu = SchoolSubscription(ssuID, set_db_info=True)

    # check if we require a complete profile
    shop_requires_complete_profile = get_sys_property('shop_requires_complete_profile_subscriptions')
    if shop_requires_complete_profile:
        check_add_to_cart_requires_complete_profile(
            auth.user.id,
            _next=URL(request.controller, request.function, vars={'ssuID': ssuID})
        )

    ##
    # Check for valid bank details
    ##
    payment_method = get_sys_property('shop_subscriptions_payment_method')
    subscription_check_valid_bankdetails(payment_method, ssuID)

    ##
    # Check startdate of subscription
    ##
    startdate = TODAY_LOCAL
    shop_subscriptions_start = get_sys_property('shop_subscriptions_start')
    if not shop_subscriptions_start == None:
        if shop_subscriptions_start == 'next_month':
            startdate = get_last_day_month(TODAY_LOCAL) + datetime.timedelta(days=1)

    ##
    # Check if customer already has this subscription
    ##
    customer = Customer(auth.user.id)
    customer_has_membership = customer.has_membership_on_date(startdate)
    customer_subscriptions_ids = customer.get_school_subscriptions_ids_on_date(startdate)

    if int(ssuID) in customer_subscriptions_ids:
        content =  SPAN(
            H3(ssu.Name),
            SPAN(T("You have this subscription"), _class='bold'), ' ', XML('&bull;'), ' ',
            SPAN(T("Please proceed to the invoices page in case you haven't paid yet.")), BR(), BR(),
            os_gui.get_button(
                'noicon',
                URL('profile', 'invoices'),
                title=T("View invoices"),
                btn_class='btn-primary'
            )
        )
    else:
        # buy now
        # part terms
        # membership check & display if required
        # automatic payment
        ssu = SchoolSubscription(ssuID)
        ssu._set_dbinfo()
        price = ssu.get_price_on_date(TODAY_LOCAL)
        classes = ssu.get_classes_formatted()
        subscription_conditions = subscription_get_terms(ssu)

        form = ''
        direct_debit_mandate = ''
        confirm = ''
        if payment_method == 'mollie':
            form = checkout_get_form_order()
            if form.process().accepted:
                # response.flash = T('Accepted order')
                redirect(URL('shop', 'subscription_order',
                             vars={'coID': form.vars.id,
                                   'ssuID': ssuID}))

            # confirm = A(B(T('I agree')),
            #             _href=URL('mollie', 'subscription_buy_now', vars={'ssuID':ssuID}),
            #             _class='btn btn-primary')
        else:
            form =  A(B(T('I agree')),
                      _href=URL('subscription_direct_debit', vars={'ssuID': ssuID}),
                      _class='btn btn-primary')

            if not customer.has_payment_info_mandate():
                mandate_text = get_sys_property('shop_direct_debit_mandate_text')
                if mandate_text:
                    direct_debit_mandate = DIV(
                        H4(T('Direct Debit Mandate')),
                        DIV(XML(mandate_text), _class='well')
                    )

        subscription_info = subscription_get_info(ssu)

        checkout_message_subscriptions = get_sys_property('shop_checkout_message_subscriptions') or ''
        checkout_message = ''
        if checkout_message_subscriptions:
            checkout_message = DIV(
                H4(T("Order info")),
                XML(checkout_message_subscriptions), BR(),
                _class='col-md-6'
            )

        ## Membership check
        customer = Customer(auth.user.id)

        m_required = ''
        if ssu.school_memberships_id and not customer.has_given_membership_on_date(ssu.school_memberships_id, TODAY_LOCAL):
            membership = SchoolMembership(ssu.school_memberships_id)
            m_required = DIV(
                DIV(H4(T("Membership required")),
                    T("To activate this subscription the following membership is required"), BR(), BR(),
                    subscription_get_membership_info(membership),
                    _class='col-md-6'),
                DIV(H4(T("Membership terms & conditions")),
                    subscription_get_membership_terms(membership),
                    _class='col-md-6'),
                _class='col-md-12'
            )

        content = DIV(
            DIV(
                DIV(H4(T("Selected subscription")), BR(),
                    subscription_info,
                    BR(),
                    _class='col-md-6'
                ),
                DIV(H4(T('Subscription terms & conditions')), BR(),
                    subscription_conditions,
                    direct_debit_mandate,
                    _class='col-md-6'
                ),
                checkout_message,
                _class="col-md-12"
            ),
            m_required,
            DIV(
                DIV(B((os_gui.get_fa_icon('fa-exclamation-circle')), " ", T("Your subscription is almost activated")), BR(),
                    T("By continuing you agree to the terms and conditions and will activate this subscription with a payment obligation."),
                    BR(), BR(), BR(),
                    _class="col-md-12"),
                DIV(form, _class='col-md-12'),
                _class='col-md-12'
            ),
        _class="row")

    back = os_gui.get_button('back', URL('subscriptions'))

    return dict(content=content, back=back, progress=checkout_get_progress(request.function))


def subscription_get_terms(ssu):
    """
    :param ssu: SchoolSubscription object
    :return:
    """
    general_terms = get_sys_property('shop_subscriptions_terms')
    specific_terms = ssu.Terms

    terms = DIV()
    if general_terms:
        terms.append(B(T('General terms & conditions')))
        terms.append(XML(general_terms))
    if specific_terms:
        terms.append(B(T('Subscription specific terms & conditions')))
        terms.append(XML(specific_terms))

    return DIV(terms, _class='well')


def subscription_get_info(ssu):
    """
    :param ssu: SchoolSubscription object
    :return: UL with subscription info
    """

    months_text = T("months")
    if ssu.MinDuration == 1:
        months_text = T("month")

    classes = ''
    classes_unit = ''
    classes_text = T("Classes")
    if ssu.Unlimited:
        classes = T('Unlimited')
        classes_unit = T("Classes")
    elif ssu.SubscriptionUnit == 'week':
        if ssu.Classes == 1:
            classes_text = T("Class")
        classes = SPAN(str(ssu.Classes) + ' ' + classes_text)
        classes_unit = T("Per week")
    elif ssu.SubscriptionUnit == 'month':
        if ssu.Classes == 1:
            classes_text = T("Class")
        classes = SPAN(str(ssu.Classes) + ' ' + classes_text)
        classes_unit = T("Per month")

    subscription_info = UL(
        LI(B(T("Subscription")), BR(), ssu.Name),
        LI(B(T("Classes")), BR(), classes, ' ', classes_unit),
        LI(B(T("Payment")), BR(), T("Monthly")),
        LI(B(T("Minimum duration")), BR(), ssu.MinDuration, ' ', months_text),
        LI(B(T("Monthly fee")), BR(), ssu.get_price_on_date(TODAY_LOCAL)),
    )
    if ssu.Description:
        subscription_info.append(
            LI(B(T("Additional info")), BR(), ssu.Description)
        )

    return subscription_info


def subscription_get_membership_info(sm):
    """

    :param sm: SchoolMembership object
    :return: UL with membership info
    """

    info = UL(
        LI(B(T("Membership")), BR(), sm.row.Name),
        LI(B(T("Validity")), BR(), sm.get_validity_formatted()),
        LI(B(T("Price")), BR(), represent_decimal_as_amount(sm.row.Price)),
    )

    if sm.row.Description:
        info.append(
            LI(B(T("Additional info")), BR(), sm.row.Description)
        )


    return info


def subscription_get_membership_terms(sm):
    """
    :param sm: SchoolMembership object
    :return:
    """
    general_terms = get_sys_property('shop_memberships_terms')
    specific_terms = sm.row.Terms

    terms = DIV()
    if general_terms:
        terms.append(B(T('General terms & conditions')))
        terms.append(XML(general_terms))
    if specific_terms:
        terms.append(B(T('Membership specific terms & conditions')))
        terms.append(XML(specific_terms))

    return DIV(terms, _class='well')


@auth.requires_login()
def subscription_order():
    """
    Subscription order confirmation and link to payment or complete without payment
    """
    from general_helpers import get_last_day_month

    from openstudio.os_customer import Customer
    from openstudio.os_order import Order
    from openstudio.os_school_subscription import SchoolSubscription

    response.title= T('Shop')
    response.subtitle = T('Order confirmation')
    response.view = 'shop/index.html'

    features = db.customers_shop_features(1)
    if not features.Subscriptions:
        return T("This feature is disabled")

    ssuID = request.vars['ssuID']
    coID = request.vars['coID']
    ssu = SchoolSubscription(ssuID, set_db_info=True)
    order = Order(coID)
    # Set status awaiting payment
    order.set_status_awaiting_payment()

    # Add items to order
    customer = Customer(auth.user.id)
    checkout_order_subscription(ssuID, order)
    if ssu.school_memberships_id and not customer.has_given_membership_on_date(ssu.school_memberships_id, TODAY_LOCAL):
        checkout_order_membership(ssu.school_memberships_id, order)

    # mail order to customer
    order_received_mail_customer(coID)

    # check if this order needs to be paid or it's free and can be added to the customers' account straight away
    amounts = order.get_amounts()

    if not amounts:
        order_received_redirect_complete(coID)
    elif amounts.TotalPriceVAT == 0:
        order_received_redirect_complete(coID)

    # Check if an online payment provider is enabled:
    online_payment_provider = get_sys_property('online_payment_provider')
    if online_payment_provider == 'disabled':
        # no payment provider, deliver order and redirect to complete.
        order.deliver()
        redirect(URL('complete', vars={'coID':coID}))

    # We have a payment provider, lets show a pay now page!
    pay_now = A(T("Pay now"), ' ',
                os_gui.get_fa_icon('fa-angle-right'),
                _href=URL('mollie', 'order_pay', vars={'coID': coID}),
                _class='btn btn-success bold')

    content = DIV(
        DIV(H4(T('We have received your order')),
            T("The items in your order will be delivered as soon as we've received the payment for this order."), BR(),
            T("Click 'Pay now' to complete the payment."), BR(), BR(),
            T("The first payment will be for the period of"), ' ', TODAY_LOCAL.strftime(DATE_FORMAT), ' ',
            T("until"), ' ', get_last_day_month(TODAY_LOCAL).strftime(DATE_FORMAT), '.', BR(),
            T("This is the regular monthly fee :"), ' ',
            SPAN(ssu.get_price_on_date(TODAY_LOCAL, formatted=True), _class='bold'), BR(),
            BR(), BR(),
            pay_now,
            _class='col-md-6'
        ),
        DIV(H4(T("Order summary")),
            order.get_order_items_summary_display(),
            _class="col-md-6"),
        _class='row')

    # Send sys notification
    os_mail = OsMail()
    os_mail.send_notification(
        'order_created',
        customers_orders_id=coID
    )

    return dict(content=content, progress=checkout_get_progress(request.function))


@auth.requires_login()
def subscription_direct_debit():
    """
       Get a subscription
    """
    from openstudio.os_customer import Customer
    from openstudio.os_school_subscription import SchoolSubscription

    ssuID = request.vars['ssuID']

    # Check for mandate
    row = db.customers_payment_info(auth_customer_id = auth.user.id)
    query = (db.customers_payment_info_mandates.customers_payment_info_id == row.id)
    if not db(query).count():
        mandate_text = get_sys_property('shop_direct_debit_mandate_text')

        cpimID = db.customers_payment_info_mandates.insert(
            customers_payment_info_id = row.id,
            MandateText = mandate_text
        )


    # Add subscription to customer﻿​
    startdate = TODAY_LOCAL
    shop_subscriptions_start = get_sys_property('shop_subscriptions_start')
    if not shop_subscriptions_start == None:
        if shop_subscriptions_start == 'next_month':
            startdate = get_last_day_month(TODAY_LOCAL) + datetime.timedelta(days=1)

    csID = db.customers_subscriptions.insert(
        auth_customer_id=auth.user.id,
        school_subscriptions_id=ssuID,
        Startdate=startdate,
        payment_methods_id=3,  # important, 3 = Direct Debit
    )

    # Add accepted terms
    customer = Customer(auth.user.id)
    ssu = SchoolSubscription(ssuID, set_db_info=True)

    terms = [
        get_sys_property('shop_subscriptions_terms') or '', # general terms
        ssu.Terms or '' # Subscription specific terms
    ]
    full_terms = '\n'.join(terms)

    customer.log_document_acceptance(
        document_name=T("Subscription terms"),
        document_description=T("Terms for all subscriptions and subscription specific terms"),
        document_content=full_terms
    )

    # Add credits for the first month
    cs = CustomerSubscription(csID)
    cs.add_credits_month(startdate.year, startdate.month)

    # clear cache to make sure it shows in the back end
    cache_clear_customers_subscriptions(auth.user.id)

    # Create invoice
    cs = CustomerSubscription(csID)
    iID = cs.create_invoice_for_month(TODAY_LOCAL.year, TODAY_LOCAL.month)
    # iID.payment_method_id = 3
    redirect(URL('subscription_activated', vars={'csID': csID}))


@auth.requires_login()
def subscription_add_bankaccount():
    """
    Request customer to enter bank account info
    """
    response.title = T('Shop')
    response.subtitle = T('Subscription')
    response.view = 'shop/index.html'

    ssuID = request.vars['ssuID']

    content = DIV(
        H3(T('Please enter your bank account details')),
        T('A valid bank account is required to continue. All subscriptions are paid using direct debit.'), BR(),
        T('After entering your bank account, you will be redirected back to the page to get a subscription.'), BR(),
        T('Please click "Continue" below to enter your bank account details.'), BR(), BR(),
        os_gui.get_button(
            'noicon',
            URL('profile', 'me_bankaccount'),
            title=T("Continue"),
            btn_class='btn-primary'
        ))

    session.profile_me_bankaccount_next = URL('shop', 'subscription', vars={'ssuID': ssuID})

    return dict(content = content)


@auth.requires_login()
def subscription_activated():
    response.title = T('Shop')
    response.subtitle = T('Subscription activated')
    response.view = 'shop/index.html'

    csID = request.vars['csID']

    msg_activated = get_sys_property('shop_subscriptions_message_activated')
    msg_activated_display = ''
    if msg_activated:
        msg_activated_display = DIV(
            XML(msg_activated), BR(),
            _class='col-md-8 col-md-offset-2'
        )


    content = DIV(
        DIV(
            H3(T("Thank you!")),
            H4(T("Your subscription has been activated and added to your account.")),
            H4(T("We are happy to welcome you at the studio!")), BR(),
            _class='col-md-12'
        ),
        msg_activated_display, BR(), BR(),
        DIV(
            A(T("Continue"), ' ', os_gui.get_fa_icon('fa-angle-double-right'),
              _class='btn btn-success',
              _href=URL("profile", "index")),
            BR(), BR(), BR(),
            T("In case you have any questions, please "),
            A(T('contact us'), _href=URL('shop', 'contact')), '. ',
            _class='col-md-12'
        ),
        _class='center row'
    )

    # msg_fail = DIV(H3(T('Looks like something went wrong with your payment...')),
    #                SPAN(T("Believe this is a mistake? Please"), ' ',
    #                     A(T('contact'), _href=URL('shop', 'contact')), ' ',
    #                     T('us.'),
    #                     _class='grey'),
    #                _class='center')

    # Add button to here: URL('profile','index')

    return dict(content = content)


@auth.requires_login()
def classcard():
    """
        Buy classcard confirmation page
    """
    from openstudio.os_customer import Customer
    from openstudio.os_school_classcard import SchoolClasscard
    from openstudio.os_school_membership import SchoolMembership

    response.title= T('Shop')
    response.subtitle = T('Classcard')
    response.view = 'shop/index.html'

    customer = Customer(auth.user.id)
    features = db.customers_shop_features(1)
    if not features.Classcards:
        return T('This feature is disabled')

    scdID = request.vars['scdID']
    scd = SchoolClasscard(scdID, set_db_info=True)


    # check if we require a complete profile
    shop_requires_complete_profile = get_sys_property('shop_requires_complete_profile_classcards')
    if shop_requires_complete_profile:
        check_add_to_cart_requires_complete_profile(
            auth.user.id,
            _next=URL(request.controller, request.function, vars={'scdID': scdID})
        )

    ##
    # Check startdate of card
    ##
    startdate = TODAY_LOCAL

    # Membership check
    classcard_info = classcard_get_info(scd)

    form = checkout_get_form_order("Order class card")
    if form.process().accepted:
        # response.flash = T('Accepted order')
        redirect(URL('shop', 'classcard_order',
                     vars={'coID': form.vars.id,
                           'scdID': scdID}))

    checkout_message_classcards = get_sys_property('shop_checkout_message_classcards') or ''
    checkout_message = ''
    if checkout_message_classcards:
        checkout_message = DIV(
            H4(T("Order info")),
            XML(checkout_message_classcards), BR(),
            _class='col-md-6'
        )

    m_required = ''
    m_required_message = ''

    if scd.row.school_memberships_id and not customer.has_given_membership_on_date(scd.row.school_memberships_id, TODAY_LOCAL):
        membership = SchoolMembership(scd.row.school_memberships_id)
        m_required = DIV(
            DIV(H4(T("Membership required")),
                T("To purchase this classcard the following membership is required. It will be added to your order."), BR(), BR(),
                subscription_get_membership_info(membership),
                _class='col-md-6'),
            DIV(H4(T("Membership terms & conditions")),
                subscription_get_membership_terms(membership),
                _class='col-md-6'),
            _class='col-md-12'
        )
        m_required_message = DIV(
            BR(),
            B((os_gui.get_fa_icon('fa-exclamation-circle')), " ",
              T("By ordering this card you agree to the terms and conditions for the required membership")), BR(),
            BR(),
            _class="col-md-12"
        )

    content = DIV(
        DIV(
            DIV(H4(T("Selected card")), BR(),
                classcard_info,
                BR(),
                _class='col-md-6'
            ),
            checkout_message,
            _class="col-md-12"
        ),
        m_required,
        DIV(
            m_required_message,
            DIV(form, _class='col-md-12'),
            _class='col-md-12'
        ),
    _class="row")

    # Check if customer is allowed to purchase this card
    allow_trial_for_existing_customers = get_sys_property(
        'shop_allow_trial_cards_for_existing_customers'
    )

    if allow_trial_for_existing_customers != 'on' and scd.row.Trialcard:
        has_or_had_subscription = customer.get_has_or_had_subscription()
        has_or_had_card = customer.get_has_or_had_classcard()

        if has_or_had_card or has_or_had_subscription:
            content = T("Unable to sell this card. Trial cards can only be purchased by new customers.")

    back = os_gui.get_button(
        'back',
        URL('classcards')
    )

    return dict(content=content, back=back, progress=checkout_get_progress(request.function))


def classcard_get_info(scd):
    """
    :param scd: SchoolClasscard object
    :return: UL with subscription info
    """

    info = UL(
        LI(B(T("Card")), BR(), scd.row.Name),
        LI(B(T("Classes")), BR(), scd.row.Classes),
        LI(B(T("Price")), BR(), represent_decimal_as_amount(scd.row.Price)),
        LI(B(T("Validity")), BR(), scd.get_validity_formatted()),
    )
    if scd.row.Description:
        info.append(
            LI(B(T("Additional info")), BR(), scd.row.Description)
        )

    return info


@auth.requires_login()
def classcard_order():
    """
    Classcard order confirmation and link to payment or complete without payment
    """
    from openstudio.os_customer import Customer
    from openstudio.os_order import Order
    from openstudio.os_school_classcard import SchoolClasscard

    response.title= T('Shop')
    response.subtitle = T('Order confirmation')
    response.view = 'shop/index.html'

    features = db.customers_shop_features(1)
    if not features.Classcards:
        return T("This feature is disabled")

    scdID = request.vars['scdID']
    coID = request.vars['coID']
    scd = SchoolClasscard(scdID, set_db_info=True)
    order = Order(coID)
    # Set status awaiting payment
    order.set_status_awaiting_payment()

    # Add items to order
    customer = Customer(auth.user.id)
    checkout_order_classcard(scdID, order)
    if scd.row.school_memberships_id and not customer.has_given_membership_on_date(scd.row.school_memberships_id, TODAY_LOCAL):
        checkout_order_membership(scd.row.school_memberships_id, order)


    # mail order to customer
    order_received_mail_customer(coID)

    # check if this order needs to be paid or it's free and can be added to the customers' account straight away
    amounts = order.get_amounts()

    if not amounts:
        order_received_redirect_complete(coID)
    elif amounts.TotalPriceVAT == 0:
        order_received_redirect_complete(coID)

    # Check if an online payment provider is enabled:
    online_payment_provider = get_sys_property('online_payment_provider')
    if online_payment_provider == 'disabled':
        # no payment provider, deliver order and redirect to complete.
        order.deliver()
        redirect(URL('complete', vars={'coID':coID}))

    # We have a payment provider, lets show a pay now page!
    pay_now = A(T("Pay now"), ' ',
                os_gui.get_fa_icon('fa-angle-right'),
                _href=URL('mollie', 'order_pay', vars={'coID': coID}),
                _class='btn btn-success bold')

    content = DIV(
        DIV(H4(T('We have received your order')),
            T("The items in your order will be delivered as soon as we've received the payment for this order."), BR(),
            T("Click 'Pay now' to complete the payment."), BR(),
            BR(), BR(),
            pay_now,
            _class='col-md-6'
        ),
        DIV(H4(T("Order summary")),
            order.get_order_items_summary_display(),
            _class="col-md-6"),
        _class='row')

    # Send sys notification
    os_mail = OsMail()
    os_mail.send_notification(
        'order_created',
        customers_orders_id=coID
    )

    return dict(content=content, progress=checkout_get_progress(request.function))


def classes():
    """
        List classes in shop
    """
    response.title= T('Shop')
    response.subtitle = T('Classes')
    response.view = 'shop/index.html'

    features = db.customers_shop_features(1)
    if not features.Classes:
        return T('This feature is disabled')

    # if 'year' in request.vars:
    #     year = int(request.vars['year'])
    # else:
    #     year = TODAY_LOCAL.year
    # if 'week' in request.vars:
    #     week = int(request.vars['week'])
    # else:
    #     week = TODAY_LOCAL.isocalendar()[1]
    #     if week == 0:
    #         week = 1

    if 'date' in request.vars:
        start_date = datestr_to_python(DATE_FORMAT, request.vars['date'])
        if start_date < TODAY_LOCAL:
            start_date = TODAY_LOCAL
    else:
        start_date = TODAY_LOCAL

    # set up filter variables
    filter_id_school_location = ''
    filter_id_school_classtype = ''
    filter_id_school_level = ''
    filter_id_teacher = ''

    if 'location' in request.vars:
        filter_id_school_location = request.vars['location']
    if 'teacher' in request.vars:
        filter_id_teacher = request.vars['teacher']
    if 'classtype' in request.vars:
        filter_id_school_classtype = request.vars['classtype']

    filter = classes_get_filter(start_date,
                                filter_id_school_classtype=filter_id_school_classtype,
                                filter_id_school_location=filter_id_school_location,
                                filter_id_school_level='',
                                filter_id_teacher=filter_id_teacher)

    days = []
    for day in range(0, 7):
        date = start_date + datetime.timedelta(days=day)
        classes_list = classes_get_day(date,
                                       filter_id_school_classtype=filter_id_school_classtype,
                                       filter_id_school_location=filter_id_school_location,
                                       filter_id_school_level='',
                                       filter_id_teacher=filter_id_teacher)

        days.append(dict(date=date, weekday=date.isoweekday(), classes=classes_list))


    classes = DIV()
    for day in days:
        header = H3(NRtoDay(day['weekday']), ' ',
                    XML('<small>' + day['date'].strftime('%d %B %Y') + '</small>'))

        table_header = DIV(
            DIV(SPAN(T('Time')),
                _class='col-md-2'),
            DIV(SPAN(T('Location')),
                _class='col-md-2'),
            DIV(SPAN(T('Class')),
                _class='col-md-3'),
            DIV(SPAN(T('Teacher')),
                _class='col-md-2'),
            DIV(SPAN(T('Spaces')),
                _class='col-md-1'),
            DIV(' ',
                _class='col-md-2'), # Actions
            _class='row shop_classes_table_header bold'
        )

        table = DIV(table_header, _class='shop-classes')
        for c in day['classes']:
            time = SPAN(c['Starttime'], ' - ', c['Endtime'])

            sub = ''
            if c['Subteacher']:
                sub = ' (sub)'

            book = classes_get_button_book(c)

            table_row = DIV(
                DIV(time,
                    _class='col-md-2'),
                DIV(c['Location'],
                    _class='col-md-2'),
                DIV(c['ClassType'],
                    _class='col-md-3'),
                DIV(c['Teacher'], ' ', sub,
                    _class='col-md-2'),
                DIV('(', c['BookingSpacesAvailable'] , ')',
                    _class='col-md-1 grey'),
                DIV(DIV(book, _class='pull-right'),
                    _class='col-md-2'),  # Actions
                _class='row'
            )

            table.append(table_row)

        class_day = DIV(header, table)
        classes.append(class_day)

    return dict(content=DIV(filter, classes))


def classes_get_button_book(c):
    """
        :param  c: Class from openstudio.py.ClassSchedule.get_day_list
        :return: book class button (or text)
    """
    book = SPAN(T('Finished'), _class='grey small_font')
    if c['BookingStatus'] == 'ongoing':
        book = SPAN(T('In session...'), _class='grey small_font')
    elif c['BookingStatus'] == 'cancelled':
        book = SPAN(T('Cancelled'), _class='grey small_font')
    elif c['BookingStatus'] == 'not_yet_open':
        book = SPAN(T('Book from'), ' ', c['BookingOpen'].strftime(DATE_FORMAT), _class='grey small_font')
    elif c['BookingStatus'] == 'full':
        book = SPAN(T('Fully booked'), _class='grey small_font')
    elif c['BookingStatus'] == 'ok':
        book = A(SPAN(T('Book'), ' ', os_gui.get_fa_icon('fa-chevron-right')), _href=c['LinkShop'])

    return book


def classes_get_filter(date,
                       filter_id_school_classtype='',
                       filter_id_school_location='',
                       filter_id_school_level='',
                       filter_id_teacher=''):
    """
        :param filter_id_school_classtype: db.school_classtypes.id
        :param filter_id_school_location: db.school_locations.id
        :param filter_id_school_level: db.school_levels.id
        :param filter_id_teacher: db.auth_user.id (teacher = True)
        :return: div containing filter form for shop classes
    """
    date_formatted = date.strftime(DATE_FORMAT)

    au_query = (db.auth_user.teacher == True) & \
               (db.auth_user.trashed == False)

    sl_query = (db.school_locations.Archived == False) & \
               (db.school_locations.AllowAPI == True)

    ct_query = (db.school_classtypes.Archived == False) & \
               (db.school_classtypes.AllowAPI == True)

    sle_query = (db.school_levels.Archived == False)

    form = SQLFORM.factory(
        Field('location',
            requires=IS_IN_DB(db(sl_query),'school_locations.id', '%(Name)s',
                              zero=T('All locations')),
            default=filter_id_school_location,
            label=""),
        Field('teacher',
            requires=IS_IN_DB(db(au_query),'auth_user.id',
                              '%(full_name)s',
                              zero=T('All teachers')),
            default=filter_id_teacher,
            label=""),
        Field('classtype',
            requires=IS_IN_DB(db(ct_query),'school_classtypes.id', '%(Name)s',
                              zero=T('All classtypes')),
            default=filter_id_school_classtype,
            label=""),
        # Field('level',
        #     requires=IS_IN_DB(db(sle_query),'school_levels.id', '%(Name)s',
        #                       zero=T('All levels')),
        #     default=filter_id_school_level,
        #     label=""),
        submit_button=T('Go'),
        formstyle='divs',
        )

    # submit form on change
    selects = form.elements('select')
    for select in selects:
        select.attributes['_onchange'] = "this.form.submit();"

    div = DIV(
        form.custom.begin,
        DIV(form.custom.widget.location,
            _class='col-md-3'),
        DIV(form.custom.widget.teacher,
            _class='col-md-3'),
        DIV(form.custom.widget.classtype,
            _class='col-md-3'),
        # form.custom.widget.level,
        DIV(classes_get_week_browser(date),
            _class='col-md-3'),
        form.custom.end,
        _class='row'
        )

    return div


def classes_get_week_browser(date):
    """
        :param week: int week
        :param year: int year
        :return: buttons to browse through weeks 
    """
    one_week = datetime.timedelta(days=7)
    date_prev = (date - one_week).strftime(DATE_FORMAT)
    date_next = (date + one_week).strftime(DATE_FORMAT)


    url_prev = URL('classes', vars={ 'date': date_prev })
    if date <= TODAY_LOCAL:
        url_prev = '#'
    url_next = URL('classes', vars={ 'date': date_next })

    previous = A(I(_class='fa fa-angle-left'),
                 _href=url_prev,
                 _class='btn btn-default')

    if date <= TODAY_LOCAL:
        previous['_disabled'] = 'disabled'

    nxt = A(I(_class='fa fa-angle-right'),
            _href=url_next,
            _class='btn btn-default')

    today = ''
    if date > TODAY_LOCAL:
        today = os_gui.get_button(
            'noicon',
            URL('shop', 'classes',
                vars={'date': TODAY_LOCAL.strftime(DATE_FORMAT)}),
            title=T('Today'),
            btn_size='',
            _class="pull-right"
        )

    buttons = DIV(previous, nxt, _class='btn-group pull-right')

    return DIV(buttons, ' ', today, _class='shop-classes-week-chooser')


def classes_get_day(date,
                    filter_id_school_classtype,
                    filter_id_school_location,
                    filter_id_school_level,
                    filter_id_teacher):
    """
        :param weekday: ISO weekday (1-7)
        :return: List of classes for day
    """
    from openstudio.os_class_schedule import ClassSchedule

    cs = ClassSchedule(
        date,
        filter_id_school_classtype = filter_id_school_classtype,
        filter_id_school_location = filter_id_school_location,
        filter_id_school_level = filter_id_school_level,
        filter_id_teacher = filter_id_teacher,
        filter_public = True,
        sorting = 'starttime' )

    return cs.get_day_list()


def classes_book_options_get_button_book(url):
    """
        Return book button for booking options
    """
    button_book = A(SPAN(T('Book'), ' ', os_gui.get_fa_icon('fa-chevron-right')),
                    _href=url,
                    _class='pull-right btn btn-link')

    return button_book


def class_book_options_get_url_next_weekday(clsID, date, isoweekday):
    """
        Go to next weekday
    """
    from general_helpers import next_weekday
    from openstudio.os_class import Class

    # Check if today's class is taking place, if not, go to next week.
    cls_today = Class(clsID, TODAY_LOCAL)
    if cls_today.is_taking_place():
        next_class = TODAY_LOCAL
    else:
        next_class = next_weekday(TODAY_LOCAL, isoweekday)

    return URL('classes_book_options', vars={'clsID':clsID,
                                             'date':next_class.strftime(DATE_FORMAT)})


def class_book_get_class_header(clsID, date):
    """
        Pretty display of class name
    """
    from openstudio.os_class import Class

    cls = Class(clsID, date)
    location = db.school_locations[cls.cls.school_locations_id].Name


    classtype = db.school_classtypes[cls.cls.school_classtypes_id].Name
    class_name = date.strftime('%d %B %Y') + ' ' + '<br><small>' + \
                 cls.cls.Starttime.strftime(TIME_FORMAT) + ' - ' + \
                 cls.cls.Endtime.strftime(TIME_FORMAT) + ' ' + \
                 classtype + ' ' + \
                 T('in') + ' ' + location + '</small>'

    return class_name


@auth.requires_login()
def classes_book_options():
    """
        Lists ways to book classes
         - subscriptions
         - cards
         - drop in (with price & add to cart button)
    """
    from openstudio.os_attendance_helper import AttendanceHelper
    from openstudio.os_class import Class
    from openstudio.os_customer import Customer

    response.title= T('Shop')
    response.subtitle = T('Book class')
    response.view = 'shop/index.html'

    features = db.customers_shop_features(1)
    if not features.Classes:
        return T('This feature is disabled')

    back = os_gui.get_button('back', URL('shop', 'classes'))

    clsID = request.vars['clsID']
    date_formatted = request.vars['date']
    date = datestr_to_python(DATE_FORMAT, date_formatted)

    # Get class data and populate info content
    class_header = class_book_get_class_header(clsID, date)

    customer = Customer(auth.user.id)

    content = DIV(H2(XML(class_header), _class='center'), BR(), H4(T('Booking options for this class')), _class='center')

    # Check if class is bookable
    shop_classes_advance_booking_limit = get_sys_property('shop_classes_advance_booking_limit')
    if not shop_classes_advance_booking_limit is None:
        delta = datetime.timedelta(days=int(shop_classes_advance_booking_limit))
        booking_allowed_until = TODAY_LOCAL + delta

        bookings_open = date - delta
        if date > booking_allowed_until:
            content.append(DIV(B(T("Bookings for this class are accepted from ") + bookings_open.strftime(DATE_FORMAT))))
            content.append(BR())
            content.append(BR())

            return dict(content=content, back=back)

    # Check is class isn't in the past, cancelled, in a holiday or url requested with a wrong date
    cls = Class(clsID, date)
    if not cls.is_taking_place():
        content.append(DIV(B(T("Unable to show booking options for this class."))))
        content.append(DIV(T("Would you like to try"), ' ',
                           A(T('next week'),
                             _href=class_book_options_get_url_next_weekday(clsID, date, cls.cls.Week_day)),
                           T('?')))

        return dict(content=content, back=back)

    # Check if the class isn't booked yet
    if cls.is_booked_by_customer(auth.user.id):
        content.append(DIV(B(T("You've already booked this class"))))
        return dict(content=content, back=back)

    ##
    # Class booking options
    ##
    trial = cls.get_trialclass_allowed_in_shop()
    ah = AttendanceHelper()
    options =  ah.get_customer_class_booking_options_formatted(clsID, date, customer, trial=trial, controller='shop')

    content.append(options)

    ##
    # Enrollment options
    ##
    content.append(DIV(DIV(H4(T('Join every week'), _class='center'), _class='col-md-12'),
                       _class='row'))

    enrollment_options = class_book_options_get_enrollment_options(clsID, date, date_formatted, features, customer)
    content.append(enrollment_options)


    return dict(content=content, back=back)



def class_book_options_get_enrollment_options(clsID, date, date_formatted, features, customer):
    """
        List enrollment options
    """
    from openstudio.os_attendance_helper import AttendanceHelper
    from openstudio.os_class import Class

    options = DIV(_class='shop-classes-booking-options row')

    cls = Class(clsID, date)

    ##
    # Check for already enrolled
    ##
    if customer.has_recurring_reservation_for_class(clsID, date):
        option = DIV(
            DIV(T("You're enrolled in this class."), _class='grey center'),
            _class='col-md-10 col-md-offset-1 col-xs-12'
        )

        options.append(option)
        return options


    ##
    # Check enrollment spaces
    ##
    if not cls.has_recurring_reservation_spaces():
        option = DIV(
            DIV(T("All spaces for enrollments are currently filled. Please check again later."), _class='grey center'),
            _class='col-md-10 col-md-offset-1 col-xs-12'
        )

        options.append(option)
        return options

    ##
    # Check if customer has a subscription
    ##
    subscriptions = customer.get_subscriptions_on_date(date)
    if not subscriptions or len(subscriptions) == 0:
        option = DIV(
            DIV(T("A subscription is required to enroll"), _class='grey center'),
            _class='col-md-10 col-md-offset-1 col-xs-12'
        )

        if features.Subscriptions:
            option.append(BR())
            option.append(DIV(A(T('Get a subcription'),
                              _href=URL('shop', 'subscriptions')),
                            _class='center'))

        options.append(option)

        return options
    else:
        ##
        # Check if enrollment allowed on this suscription
        ##
        for subscription in subscriptions:
            csID = subscription.customers_subscriptions.id
            cs = CustomerSubscription(csID)
            enrollment_allowed = False
            if int(clsID) in cs.get_allowed_classes_booking():
                enrollment_allowed = True
                break

        if not enrollment_allowed:
            option = DIV(
                DIV(T("Enrollment in this class is not possible using your current subscription(s)."), _class='grey center'),
                _class='col-md-10 col-md-offset-1 col-xs-12'
            )

            options.append(option)
            return options

    ##
    # Options to enroll
    ##
    ah = AttendanceHelper()
    options = DIV(
        BR(),
        T("In case you would like to join this class every week, you can enroll and we'll reserve a space for you!"), BR(),
        T("You can enroll using the following subscription(s)"),
        BR(), BR(),
        ah.get_customer_class_enrollment_options(
            clsID,
            date,
            customer,
            list_type='shop',
            controller='shop'
        )
    )

    # options = ah.get_customer_class_enrollment_options(
    #         clsID,
    #         date,
    #         customer,
    #         list_type='shop',
    #         controller='shop'
    #     )

    # option = DIV(DIV(T('Enroll'),
    #                  _class='col-md-3 bold'),
    #              DIV(T("In case you would like to join this class every week, you can enroll and we'll reserve a space for you!"),
    #                  _class='col-md-6'),
    #              DIV(A(SPAN(T('Enroll'), ' ',
    #                    os_gui.get_fa_icon('fa-chevron-right')),
    #                    _href=URL('class_enroll', vars={'clsID':clsID, 'date':date_formatted}),
    #                    _class='btn btn-link pull-right'),
    #                  _class='col-md-3'),
    #              _class='col-md-10 col-md-offset-1 col-xs-12')
    # options.append(option)


    return options


@auth.requires_login()
def class_enroll():
    """
    :return:
    """
    from openstudio.os_class import Class

    response.title= T('Shop')
    response.subtitle = T('Enroll in class')
    response.view = 'shop/index.html'

    csID = request.vars['csID']
    clsID = request.vars['clsID']
    date_formatted = request.vars['date']
    date = datestr_to_python(DATE_FORMAT, date_formatted)

    return_url = URL('shop', 'classes_book_options', vars={'clsID':clsID, 'date':date_formatted})
    back = os_gui.get_button('back', return_url)
    content = DIV()

    ##
    # Information
    ##
    cls = Class(clsID, date)
    location = db.school_locations[cls.cls.school_locations_id].Name

    classtype = db.school_classtypes[cls.cls.school_classtypes_id].Name
    class_header = NRtoDay(cls.cls.Week_day) + ' ' + \
                 cls.cls.Starttime.strftime(TIME_FORMAT) + ' - ' + \
                 cls.cls.Endtime.strftime(TIME_FORMAT) + ' ' + \
                 classtype + ' ' + \
                 T('in') + ' ' + location

    content.append(DIV(H3(XML(class_header), _class=''), BR(), H4(T('Enrollment information'), _class=''), _class='center'))

    info = P(T("By enrolling in a class a space will be reserved for you every week."), BR(),
             T("After enrolling you can manage your enrollments from your profile."),
             _class="center")
    content.append(DIV(info, _class='col-md-10 col-md-offset-1 col-xs-12'))

    ##
    # Enrollment form (It actually shows just 2 buttons, everything else is a hidden field)
    ##
    db.classes_reservation.auth_customer_id.default = auth.user.id
    db.classes_reservation.customers_subscriptions_id.default = csID
    db.classes_reservation.classes_id.default = clsID
    db.classes_reservation.Startdate.readable = False
    db.classes_reservation.Enddate.readable = False
    db.classes_reservation.Startdate.writable = False
    db.classes_reservation.Enddate.writable = False
    db.classes_reservation.Startdate.default = date

    form = SQLFORM(db.classes_reservation,
                   formstyle='divs',
                   submit_button=T("Enroll"))

    form.add_button(T('Cancel'), return_url)

    if form.process().accepted:
        from openstudio.os_classes_reservation import ClassesReservation

        clrID = form.vars.id

        reservation = ClassesReservation(clrID)
        classes_booked = reservation.book_classes(
            csID=csID,
            date_from=date,
        )

        classes = T("classes")
        if classes_booked == 1:
            classes = T("class")

        session.flash = T('Enrollment added, booked' + ' ' + str(classes_booked) + ' ' + classes)
        redirect(URL('profile', 'enrollments'))
    elif form.errors:
        response.flash = T('Form has errors')

    content.append(DIV(form, _class='col-md-10 col-md-offset-1 col-xs-12 center'))

    return dict(content=content,
                back=back)


@auth.requires_login()
def class_book():
    """
        Actually book class
    """
    def wrong_user():
        return "Unable to use this subscription or class card"

    from openstudio.os_attendance_helper import AttendanceHelper
    from openstudio.os_class import Class
    from openstudio.os_customer_classcard import CustomerClasscard
    from openstudio.os_customer_subscription import CustomerSubscription

    cuID = auth.user.id
    csID = request.vars['csID']
    ccdID = request.vars['ccdID']
    clsID = request.vars['clsID']
    dropin = request.vars['dropin']
    date_formatted = request.vars['date']
    date  = datestr_to_python(DATE_FORMAT, request.vars['date'])


    url_booking_options = URL('shop', 'classes_book_options', vars={'clsID':clsID,
                                                                   'date':date_formatted})
    # Redirect back to book options in case class isn't bookable
    cls = Class(clsID, date)
    if not cls.is_taking_place():
        redirect(url_booking_options)

    # Actually book class
    ah = AttendanceHelper()

    if csID:
        # Redirect back to book options in case booking this class isn't allowed on this subscription
        cs = CustomerSubscription(csID)
        if not int(clsID) in cs.get_allowed_classes_booking():
            redirect(url_booking_options)

        if not (cs.cs.auth_customer_id == auth.user.id):
            wrong_user()

        result = ah.attendance_sign_in_subscription(cuID,
                                                    clsID,
                                                    csID,
                                                    date,
                                                    online_booking=True,
                                                    credits_hard_limit=True)
        if result['status'] == 'fail':
            session.flash = result['message']
        else:
            session.flash = T('Class booked')

    if ccdID:
        ccd = CustomerClasscard(ccdID)
        if not (ccd.classcard.auth_customer_id == auth.user.id):
            wrong_user()

        # Redirect back to book options page in case class booking in advance isn't allowed on this card
        if not int(clsID) in ccd.get_allowed_classes_booking():

            redirect(url_booking_options)

        result = ah.attendance_sign_in_classcard(cuID, clsID, ccdID, date, online_booking=True)
        if result['status'] == 'fail':
            #print 'failed'
            session.flash = result['message']
        else:
            session.flash = T('Class booked')

            # validity > today + 7 days and classes remaining
            if not ccd.classcard.Enddate:
                valid_next_week = True
            else:
                valid_next_week = ccd.classcard.Enddate > (TODAY_LOCAL + datetime.timedelta(days=7))

            if ccd.unlimited:
                classes_remaining = True
            else:
                classes_remaining = ccd.get_classes_remaining()

            if valid_next_week and classes_remaining:
                redirect(URL('class_book_classcard_recurring', vars={'clsID':clsID,
                                                                     'date':date_formatted,
                                                                     'ccdID':ccdID}))

    # Clear api cache to update available spaces
    cache_clear_classschedule_api()

    dropin = request.vars['dropin']
    trial = request.vars['trial']
    if dropin == 'true' or trial =='true':
        # Add drop in class to shopping cart
        redirect(URL('class_checkout', vars={'clsID':clsID,
                                             'date':date_formatted,
                                             'dropin':dropin,
                                             'trial':trial}))

    redirect(URL('profile', 'classes'))


@auth.requires_login()
def class_checkout():
    """
        Buy class confirmation page
    """
    from general_helpers import datestr_to_python
    from openstudio.os_customer import Customer
    from openstudio.os_class import Class

    response.title= T('Shop')
    response.subtitle = T('Class')
    response.view = 'shop/index.html'

    features = db.customers_shop_features(1)
    if not features.Classes:
        return T('This feature is disabled')

    clsID = request.vars['clsID']
    date_formatted = request.vars['date']
    date = datestr_to_python(DATE_FORMAT, date_formatted)
    dropin = True if request.vars['dropin'] == 'true' else False
    trial = True if request.vars['trial'] == 'true' else False
    cls = Class(clsID, date)

    # check if we require a complete profile
    shop_requires_complete_profile = get_sys_property('shop_requires_complete_profile_classes')
    if shop_requires_complete_profile:
        check_add_to_cart_requires_complete_profile(
            auth.user.id,
            _next=URL(request.controller, request.function, vars=request.vars)
        )

    # automatic payment
    class_info = class_checkout_get_info(cls, dropin, trial)
    form = checkout_get_form_order(submit_button="Book class")

    if form.process().accepted:
        redirect(URL('shop', 'class_order',
                     vars={'coID': form.vars.id,
                           'clsID': clsID,
                           'date': date_formatted,
                           'dropin': dropin,
                           'trial': trial}))

    checkout_message_classes = get_sys_property('shop_checkout_message_classes') or ''
    checkout_message = ''
    if checkout_message_classes:
        checkout_message = DIV(
            H4(T("Order info")),
            XML(checkout_message_classes), BR(),
            _class='col-md-6'
        )

    customer = Customer(auth.user.id)

    content = DIV(
        DIV(
            DIV(H4(T("Selected class")), BR(),
                class_info,
                BR(),
                _class='col-md-6'
            ),
            checkout_message,
            _class="col-md-12"
        ),
        DIV(
            DIV(form, _class='col-md-12'),
            _class='col-md-12'
        ),
    _class="row")

    back = os_gui.get_button(
        'back',
        URL('classcards')
    )

    return dict(content=content, back=back, progress=checkout_get_progress(request.function))


def class_checkout_get_info(cls, dropin, trial):
    """
    :param scd: SchoolClasscard object
    :return: UL with subscription info
    """
    prices = cls.get_prices_customer(auth.user.id)


    info = UL(
        LI(B(T("Date & time")), BR(), cls.date.strftime(DATE_FORMAT), ' ',
           cls.cls.Starttime.strftime(TIME_FORMAT)),
        LI(B(T("Class")), BR(), cls.get_classtype_name()),
        LI(B(T("Location")), BR(), cls.get_location_name()),
        LI(B(T("Type")), BR(), T("Drop in") if dropin else T("Trial")),
        LI(B(T("Price")), BR(),
           represent_decimal_as_amount(prices['dropin'] if dropin else prices['trial'])),
    )

    return info


@auth.requires_login()
def class_order():
    """
    Class order confirmation and link to payment or complete without payment
    """
    from openstudio.os_customer import Customer
    from openstudio.os_class import Class
    from openstudio.os_order import Order

    response.title= T('Shop')
    response.subtitle = T('Order confirmation')
    response.view = 'shop/index.html'

    features = db.customers_shop_features(1)
    if not features.Classes:
        return T("This feature is disabled")

    coID = request.vars['coID']
    clsID = request.vars['clsID']
    date_formatted = request.vars['date']
    date = datestr_to_python(DATE_FORMAT, date_formatted)
    dropin = request.vars['dropin']
    trial = request.vars['trial']
    cls = Class(clsID, date)
    order = Order(coID)
    # Set status awaiting payment
    order.set_status_awaiting_payment()

    # Add items to order
    customer = Customer(auth.user.id)

    attendance_type = 2 # dropin
    if trial == 'True':
        attendance_type = 1
    checkout_order_class(clsID, date, attendance_type, order)

    # mail order to customer
    order_received_mail_customer(coID)

    # check if this order needs to be paid or it's free and can be added to the customers' account straight away
    amounts = order.get_amounts()

    if not amounts:
        order_received_redirect_complete(coID)
    elif amounts.TotalPriceVAT == 0:
        order_received_redirect_complete(coID)

    # Check if an online payment provider is enabled:
    online_payment_provider = get_sys_property('online_payment_provider')
    if online_payment_provider == 'disabled':
        # no payment provider, deliver order and redirect to complete.
        order.deliver()
        redirect(URL('complete', vars={'coID':coID}))

    # We have a payment provider, lets show a pay now page!
    pay_now = A(T("Pay now"), ' ',
                os_gui.get_fa_icon('fa-angle-right'),
                _href=URL('mollie', 'order_pay', vars={'coID': coID}),
                _class='btn btn-success bold')

    content = DIV(
        DIV(H4(T('We have received your order')),
            T("Your class will be booked as soon as we've received the payment for this order."), BR(),
            T("Click 'Pay now' to complete the payment."), BR(),
            BR(), BR(),
            pay_now,
            _class='col-md-6'
        ),
        DIV(H4(T("Order summary")),
            order.get_order_items_summary_display(),
            _class="col-md-6"),
        _class='row')

    # Send sys notification
    os_mail = OsMail()
    os_mail.send_notification(
        'order_created',
        customers_orders_id=coID
    )

    return dict(content=content, progress=checkout_get_progress(request.function))


@auth.requires_login()
def class_book_classcard_recurring():
    """
        Offer option to make multiple booking for this class
    """
    from openstudio.os_attendance_helper import AttendanceHelper
    from openstudio.os_class import Class
    from openstudio.os_customer_classcard import CustomerClasscard

    ccdID = request.vars['ccdID']
    clsID = request.vars['clsID']
    date_formatted = request.vars['date']
    date  = datestr_to_python(DATE_FORMAT, request.vars['date'])

    response.title= T('Shop')
    response.subtitle = T('Book class')
    response.view = 'shop/index.html'

    return_url = URL('profile', 'classes')

    ccd = CustomerClasscard(ccdID)
    if not (ccd.classcard.auth_customer_id == auth.user.id):
        redirect(return_url)

    form = class_book_classcard_recurring_get_form(ccd)

    if form.process().accepted:
        recur_until = request.vars['recur_until']
        ah = AttendanceHelper()
        result = ah.attendance_sign_in_classcard_recurring(auth.user.id,
                                                           clsID,
                                                           ccdID,
                                                           date,
                                                           datestr_to_python(DATE_FORMAT, recur_until),
                                                           online_booking=False,
                                                           booking_status='booked')

        session.flash = SPAN(T('Booked'), ' ', str(result['classes_booked']), ' ', T('classes'), BR()
                             #TODO: Add message returned
                             )


        redirect(return_url)
    elif form.errors:
        response.flash = T('')



    cls = Class(clsID, date)
    location = db.school_locations[cls.cls.school_locations_id].Name

    classtype = db.school_classtypes[cls.cls.school_classtypes_id].Name
    class_name = NRtoDay(cls.cls.Week_day) + ' ' + '<br><small>' + \
                 cls.cls.Starttime.strftime(TIME_FORMAT) + ' - ' + \
                 cls.cls.Endtime.strftime(TIME_FORMAT) + ' ' + \
                 classtype + ' ' + \
                 T('in') + ' ' + location + '</small>'


    no_thanks = A(T("No, I just want to attend this class."),
                  _href=URL('profile', 'classes'),
                  _class='btn btn-link')

    content = DIV(H3(XML(class_name)),
                  P(T('Would you like to make this a recurring booking?')),
                  DIV(form, _class='col-xs-12 col-xs-offset-1 col-md-4 col-md-offset-4'),
                  DIV(no_thanks, _class='col-md-12'),
                  _class='center')

    return dict(content=content)


def class_book_classcard_recurring_get_form(ccd):
    """
        :param ccd: Classcard object
        :return: form to allow setting enddate of recurring booking
    """
    max_date = datetime.date(2999, 1, 1)
    shop_classes_advance_booking_limit = get_sys_property('shop_classes_advance_booking_limit')
    if shop_classes_advance_booking_limit:
        max_date = TODAY_LOCAL + datetime.timedelta(days=int(shop_classes_advance_booking_limit))

    if ccd.classcard.Enddate:
        if ccd.classcard.Enddate < max_date:
            max_date = ccd.classcard.Enddate

    # If booking limit > enddate class card:
    # Max date = class card end date
    # Else max date = booking_limit
    #
    # print type(max_date)
    # print type(TODAY_LOCAL)
    # print type(ccd.classcard.Enddate)

    form = SQLFORM.factory(
        Field('recur_until', 'date',
              default=max_date,
              requires=IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                        minimum=TODAY_LOCAL,
                                        maximum=max_date),
              label=T('Recur booking until')),
        formstyle='bootstrap3_stacked',
        submit_button=T('Make recurring booking')
    )

    return form


@auth.requires_login()
def donate():
    """
        Donate page for shop
    """
    from openstudio.os_order import Order

    response.title= T('Shop')
    response.subtitle = T('Donate')
    response.view = 'shop/index.html'

    form = donate_get_form()

    sys_property_shop_text = 'shop_donations_shop_text'
    shop_text = XML(get_sys_property(sys_property_shop_text) or '')

    content = DIV(shop_text, form)

    if form.process().accepted:
        if 'description' in request.vars and 'amount' in request.vars:
            # Create order
            coID = db.customers_orders.insert(
                auth_customer_id=auth.user.id,
                Donation=True
            )

            order = Order(coID)
            order.order_item_add_donation(request.vars['amount'],
                                          request.vars['description'])

            if not web2pytest.is_running_under_test(request, request.application):
                # redirect to mollie for payment
                redirect(URL('mollie', 'order_pay', vars={'coID':coID}))


    return dict(content=content)


def donate_get_form(var=None):
    """
        Use SQLFORM.factory to create a donation form 
    """
    form = SQLFORM.factory(
        Field('amount', 'double',
            requires=IS_FLOAT_IN_RANGE(0,
                                       99999999,
                                       dot='.',
                                       error_message=T('Please enter an amount and use "." for decimals (if any)')),
            label=T('Amount in ') + CURRSYM),
        Field('description',
            requires=IS_NOT_EMPTY(),
            label=T('Description')),
        separator = '',
        formstyle = 'bootstrap',
        submit_button = T('Donate'))

    return form


def check_add_to_cart_requires_complete_profile(auID, _next=''):
    """
        Checks if a completed profile is required, if so and it isn't complete, redirect to the profile edit page
    """
    user = db.auth_user(auID)

    required_fields = [
        user.first_name,
        user.last_name,
        user.email,
        user.gender,
        user.date_of_birth,
        user.address,
        user.city,
        user.postcode,
        user.country,
        user.mobile
    ]

    for f in required_fields:
        if not f:
            session.flash = SPAN(
                T('To offer you the best service possible, we kindly ask you to complete the general information in your profile.'), BR(),
                T('After completing your profile information you will be redirected to the next step.')
            )
            redirect(URL('profile', 'me', vars={'_next': _next}))


    #TODO: The rest of the code...