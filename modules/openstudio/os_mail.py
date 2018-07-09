# -*- coding: utf-8 -*-

import os

from gluon import *

class OsMail:
    def send_html_to_addess(self, msg_html, msg_subject, email):
        """
        :param msg_html: html message
        :param msg_subject: email subject
        :param email: address
        :return: boolean: True if send, False if error sending
        """
        MAIL = current.globalenv['MAIL']

        status_report = mail.send(
            to=email,
            subject=msg_subject,
            message=msg_html
        )

        return status_report


    def send(self, msgID, cuID): # Used to be 'mail_customer()'
        """
            Send a message to a customer
            returns True when a mail is sent and False when it failed
        """
        db = current.db
        MAIL = current.globalenv['MAIL']

        customer = db.auth_user(cuID)
        message = db.messages(msgID)

        check = MAIL.send(
        to=customer.email,
        subject=message.msg_subject,
        # If reply_to is omitted, then mail.settings.sender is used
        reply_to=None,
        message=message.msg_content)

        if check:
            status = 'sent'
            rvalue = True
        else:
            status = 'fail'
            rvalue = False
        db.customers_messages.insert(auth_customer_id = cuID,
                                     messages_id      = msgID,
                                     Status           = status)

        return rvalue


    def _render_email_template_order(self, template_content, customers_orders_id):
        """
            :param customers_orders_id:
            :return: mail body for order_received & order_delivered
        """
        def get_row(value_left, value_right, first=False, total=False):
            border = ''
            font_weight = ''
            if first:
                border = "border-top: 1px dashed #aaaaaa;"

            if total:
                border = "border-top: 1px solid #eaeaea; border-bottom: 1px dashed #aaaaaa;"
                font_weight = "font-weight:bold;"

            tr = TR(TD(
                TABLE(TR(TD(TABLE(TR(TD(TABLE(TR(TD(value_left, # left column
                                                    _align="left", _style="font-family: Arial, sans-serif; color: #333333; font-size: 16px; " + font_weight)),
                                              _cellpadding="0", _cellspacing="0", _border="0", _width="100%"),
                                        _style="padding: 0 0 10px 0;")),
                                  _cellpadding="0", _cellspacing="0", _border="0", _width="47%", _style="width:47%;", _align="left"),
                            TABLE(TR(TD(TABLE(TR(TD(value_right, # right column
                                                    _align="right", _style="font-family: Arial, sans-serif; color: #333333; font-size: 16px;  " + font_weight)),
                                              _cellpadding="0", _cellspacing="0", _border="0", _width="100%"),
                                        _style="padding: 0 0 10px 0;")),
                                  _cellpadding="0", _cellspacing="0", _border="0", _width="47%", _style="width:47%;", _align="right"),
                            _valign="top", _class="mobile-wrapper")),
                      _cellspacing="0", _cellpadding="0", _border="0", _width="100%"),
                _style="padding: 10px 0 0 0; " + border))

            return tr

        from os_order import Order

        T = current.T
        DATETIME_FORMAT = current.DATETIME_FORMAT
        represent_float_as_amount = current.globalenv['represent_float_as_amount']

        order = Order(customers_orders_id)
        item_rows = order.get_order_items_rows()
        order_items = TABLE(_border="0", _cellspacing="0", _cellpadding="0", _width="100%", _style="max-width: 500px;", _class="responsive-table")
        for i, row in enumerate(item_rows):
            repr_row = list(item_rows[i:i + 1].render())[0]

            first = False
            if i == 0:
                first = True

            tr = get_row(SPAN(row.ProductName, ' ', row.Description), repr_row.TotalPriceVAT, first)
            order_items.append(tr)

        # add total row
        amounts = order.get_amounts()
        total_row = get_row(T('Total'), represent_float_as_amount(amounts.TotalPriceVAT), total=True)
        order_items.append(total_row)

        # TODO: Add to manual & button on page available variables;

        return XML(template_content.format(order_id=order.order.id,
                                           order_date=order.order.DateCreated.strftime(DATETIME_FORMAT),
                                           order_status=order.order.Status,
                                           order_items=order_items,
                                           link_profile_orders=URL('profile', 'orders', scheme=True, host=True),
                                           link_profile_invoices=URL('profile', 'invoices', scheme=True, host=True)))


    def _render_email_template_payment_recurring_failed(self, template_content):
        """
            :param template_content: html template code from db.sys_properties
            :param invoices_id: db.invoices_payments_id
            :return: mail body for invoice
        """
        db = current.db
        T = current.T
        DATE_FORMAT = current.DATE_FORMAT

        # TODO: Add to manual & button on page available variables;
        return XML(template_content.format(link_profile_invoices=URL('profile', 'invoices', scheme=True, host=True)))


    def _render_email_workshops_info_mail(self, wspc, wsp, ws):
        """
        :param template_content: Mail content
        :param workshops_products_id: db.workshops_products.id
        :return: mail body for workshop
        """
        from os_customer import Customer

        db = current.db
        T = current.T
        DATE_FORMAT = current.DATE_FORMAT
        TIME_FORMAT = current.TIME_FORMAT
        customer = Customer(wspc.auth_customer_id)

        try:
            time_info = TR(TH(T('Date')),
                           TD(ws.Startdate.strftime(DATE_FORMAT), ' ', ws.Starttime.strftime(TIME_FORMAT), ' - ',
                              ws.Enddate.strftime(DATE_FORMAT), ' ', ws.Endtime.strftime(TIME_FORMAT),
                              _align="left"))
        except AttributeError:
            time_info = ''

        description = TABLE(TR(TH(T('Ticket')),
                               TD(wsp.Name, _align="left")),
                            time_info,
                            _cellspacing="0", _cellpadding='5px', _width='100%', border="0")

        wsm = db.workshops_mail(workshops_id=ws.id)
        try:
            content = wsm.MailContent
        except AttributeError:
            content = ''


        image = IMG(_src=URL('default', 'download', ws.picture, scheme=True, host=True))

        return dict(content=DIV(image, BR(), BR(), XML(content)), description=description)


    def render_email_template(self,
                              email_template,
                              title='',
                              subject='',
                              description='',
                              comments='',
                              template_content=None,
                              customers_orders_id=None,
                              invoices_id=None,
                              invoices_payments_id=None,
                              workshops_products_customers_id=None,
                              return_html=False):
        """
            Renders default email template
        """
        db = current.db
        T = current.T
        DATETIME_FORMAT = current.DATETIME_FORMAT

        get_sys_property = current.globalenv['get_sys_property']
        request = current.request
        response = current.globalenv['response']

        logo = self._render_email_template_get_logo()

        template = os.path.join(request.folder, 'views', 'templates/email/default.html')
        if template_content is None:
            # Get email template from settings
            template_content = get_sys_property(email_template)

        if email_template == 'email_template_order_received':
            subject = T('Order received')
            # do some pre-processing to show the correct order info
            content = self._render_email_template_order(template_content, customers_orders_id)

            # Check for order message
            from os_order import Order
            order = Order(customers_orders_id)
            if order.order.CustomerNote:
                comments = DIV(
                    T("We received the following message with your order:"), BR(), BR(),
                    XML(order.order.CustomerNote.replace('\n', '<br>'))
                )
                
        elif email_template == 'email_template_order_delivered':
            subject = T('Order delivered')
            # do some pre-processing to show the correct order info
            content = self._render_email_template_order(template_content, customers_orders_id)

        elif email_template == 'email_template_payment_recurring_failed':
            subject = T('Recurring payment failed')
            content = self._render_email_template_payment_recurring_failed(template_content)

        elif email_template == 'workshops_info_mail':
            wspc = db.workshops_products_customers(workshops_products_customers_id)
            wsp = db.workshops_products(wspc.workshops_products_id)
            ws = db.workshops(wsp.workshops_id)
            subject = ws.Name
            title = ws.Name
            result = self._render_email_workshops_info_mail(wspc, wsp, ws)
            content = result['content']
            description = result['description']

        elif (email_template == 'email_template_sys_verify_email' or
              email_template == 'email_template_sys_reset_password'):
            template = os.path.join(request.folder, 'views', 'templates/email/default_simple.html')
            content = XML(template_content)
            subject = subject

        elif email_template == 'sys_notification_order_created':
            return_html = True
            content = self._render_email_template_order(template_content, customers_orders_id)

            # Check for order message
            from os_order import Order
            order = Order(customers_orders_id)
            if order.order.CustomerNote:
                comments = DIV(
                    T("We received the following message with your order:"), BR(), BR(),
                    XML(order.order.CustomerNote.replace('\n', '<br>'))
                )
        else:
            template = os.path.join(request.folder, 'views', 'templates/email/default.html')
            content = XML(template_content)
            subject = subject

        footer = XML(get_sys_property('email_template_sys_footer'))

        message =  response.render(template,
                                   dict(logo=logo,
                                        title=title,
                                        description=description,
                                        content=content,
                                        comments=comments,
                                        footer=footer))

        if return_html:
            return message
        else:
            msgID = db.messages.insert(
                msg_content = message,
                msg_subject = subject
            )

            return msgID


    def _render_email_template_get_logo(self):
        """
            Returns logo for email template
        """
        request = current.request

        branding_logo = os.path.join(request.folder,
                                     'static',
                                     'plugin_os-branding',
                                     'logos',
                                     'branding_logo_invoices.png')
        if os.path.isfile(branding_logo):
            abs_url = '%s://%s/%s/%s' % (request.env.wsgi_url_scheme,
                                         request.env.http_host,
                                         'static',
                            'plugin_os-branding/logos/branding_logo_invoices.png')
            logo_img = IMG(_src=abs_url)

        else:
            logo_img = ''

        return logo_img


