# -*- coding: utf-8 -*-

import datetime
import os

from gluon import *

class OsMail:
    def get_email_template(self, template):
        """
        :param template: str - template name
        :return: str - template
        """
        web2pytest = current.globalenv['web2pytest']
        request = current.request

        db = current.db
        cache = current.cache

        if web2pytest.is_running_under_test(request, request.application):
            caching = None
        else:
            caching = (cache.ram, 300)

        # Get template and cache query for 5 minutes
        query = (db.sys_email_templates.Name == template)
        rows = db(query).select(
            db.sys_email_templates.ALL,
            cache = caching
        )

        try:
            return rows.first().TemplateContent
        except AttributeError:
            # Catch NoneType exceptions
            return None


    def send_notification(self,
                          sys_notification,
                          customers_orders_id=None):
        """
        :param msg_html: html message
        :param msg_subject: email subject
        :param email: address
        :return: boolean: True if send, False if error sending
        """
        T = current.T
        MAIL = current.mail

        emails = self._send_notification_get_email_addresses(sys_notification)
        message = self.render_sys_notification(
            sys_notification,
            customers_orders_id = customers_orders_id,
        )

        if sys_notification == 'order_created':
            msg_subject = T("New order")

        status_report = []
        for email in emails:
            status_report = MAIL.send(
                to=email,
                subject=msg_subject,
                message=message
            )

        return status_report


    def send_and_archive(self, msgID, cuID): # Used to be 'mail_customer()'
        """
            Send a message to a customer
            returns True when a mail is sent and False when it failed
        """
        db = current.db
        MAIL = current.mail

        customer = db.auth_user(cuID)
        message = db.messages(msgID)

        check = MAIL.send(
            to=customer.email,
            subject=message.msg_subject,
            reply_to=None, # If reply_to is omitted, then mail.settings.sender is used
            message=message.msg_content
        )

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


    def send(self, message_html, message_subject, auth_user_id):
        """
        Send mail without logging to an account

        returns True if sending mail is successful, False otherwise

        :param message_html: message content
        :param cuID: auth_user.id
        :return: boolean
        """
        db = current.db
        MAIL = current.mail

        account = db.auth_user(auth_user_id)

        result = MAIL.send(
            to=account.email,
            subject=message_subject,
            reply_to=None, # If reply_to is omitted, then mail.settings.sender is used
            message=message_html
        )

        return result


    def _send_notification_get_email_addresses(self, sys_notification):
        """
        :param sys_notification: db.sys_notification.Notification
        :return: list of email addresses
        """
        db = current.db

        notification = db.sys_notifications(Notification=sys_notification)

        emails = []
        query = (db.sys_notifications_email.sys_notifications_id == notification.id)
        rows = db(query).select(db.sys_notifications_email.ALL)
        for row in rows:
            emails.append(row.Email)

        return emails


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
                                  _cellpadding="0", _cellspacing="0", _border="0", _width="47%", _style="width:67%;", _align="left"),
                            TABLE(TR(TD(TABLE(TR(TD(value_right, # right column
                                                    _align="right", _style="font-family: Arial, sans-serif; color: #333333; font-size: 16px;  " + font_weight)),
                                              _cellpadding="0", _cellspacing="0", _border="0", _width="100%"),
                                        _style="padding: 0 0 10px 0;")),
                                  _cellpadding="0", _cellspacing="0", _border="0", _width="47%", _style="width:33%;", _align="right"),
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
            Be aware that this function has to be able to run from scheduler,
             in that case no request, etc. are available
            :param template_content: html template code from db.sys_properties
            :param invoices_id: db.invoices_payments_id
            :return: mail body for failed recurring payment
        """
        db = current.db
        T = current.T
        DATE_FORMAT = current.DATE_FORMAT

        # get hostname
        sys_hostname = None
        row = db.sys_properties(Property='sys_hostname')
        if row:
            sys_hostname = row.PropertyValue

        # TODO: Add to manual & button on page available variables;
        return XML(template_content.format(
            link_profile_invoices=URL('profile', 'invoices', scheme=True, host=sys_hostname))
        )


    def _render_email_template_teacher_sub_offer(self, template_content, classes_otc_sub_avail_id):
        """

        :param classes_otc_sub_avail_id:
        :return: mail body for declined class sub request
        """
        from openstudio.os_class import Class
        from openstudio.os_teacher import Teacher

        db = current.db
        T = current.T
        DATE_FORMAT = current.DATE_FORMAT
        TIME_FORMAT = current.TIME_FORMAT

        cotcsa = db.classes_otc_sub_avail(classes_otc_sub_avail_id)
        teacher = Teacher(cotcsa.auth_teacher_id)
        cotc = db.classes_otc(cotcsa.classes_otc_id)
        cls = Class(cotc.classes_id, cotc.ClassDate)

        class_info = TABLE(
            TR(TH(T('Date'), _align="right"),
               TD(cotc.ClassDate.strftime(DATE_FORMAT), _align="left")),
            TR(TH(T('Time'), _align="right"),
               TD(cls.cls.Starttime.strftime(TIME_FORMAT), ' - ',
                  cls.cls.Endtime.strftime(TIME_FORMAT), _align="left")),
            TR(TH(T('Location'), _align="right"),
               TD(cls.get_location_name(), _align="left")),
            TR(TH(T('Class'), _align="right"),
               TD(cls.get_classtype_name(), _align="left")),
            _cellspacing="0", _cellpadding='5px', _width='100%', border="0"
        )

        content = XML(
            template_content.format(
                teacher_name = teacher.get_first_name()
            )
        )

        return dict(
            content = content,
            description = class_info
        )


    def _render_email_template_teacher_sub_requests_daily_summary(self, template_content, auth_user_id):
        """
        :param template_content:
        :param auth_user_id:
        :return:
        """
        from openstudio.os_class import Class
        from openstudio.os_teacher import Teacher
        from openstudio.tools import OsTools
        from openstudio.os_classes_otcs import ClassesOTCs

        db = current.db
        T = current.T
        os_tools = OsTools()
        cotcs = ClassesOTCs()
        teacher = Teacher(auth_user_id)
        DATE_FORMAT = current.DATE_FORMAT
        TIME_FORMAT = current.TIME_FORMAT
        error = False
        error_msg = ''

        date_from = current.TODAY_LOCAL + datetime.timedelta(days=1)
        date_until = date_from + datetime.timedelta(days=45)

        # G get list of allowed class types
        query = (db.teachers_classtypes.auth_user_id == auth_user_id)
        classtype_rows = db(query).select(db.teachers_classtypes.ALL)
        ct_ids = []
        for row in classtype_rows:
            ct_ids.append(int(row.school_classtypes_id))

        open_classes_for_teacher = 0
        open_classes = ''
        description = ''
        if ct_ids:
            sys_hostname = os_tools.get_sys_property('sys_hostname')
            description = XML(
                template_content.format(
                    teacher_name = teacher.get_first_name(),
                    link_employee_portal = URL('ep', 'index', scheme='https', host=sys_hostname)
                )
            )

            open_classes = TABLE(THEAD(TR(
                TH(T("Date"), _align="left"),
                TH(T("Time"), _align="left"),
                TH(T("Location"), _align="left"),
                TH(T("Class"), _align="left"),
                # TH(),
            )), _cellspacing="0", _cellpadding='5px', _width='100%', border="0")

            # Get Open classes in the next 45 days
            rows = cotcs.get_sub_teacher_rows(
                date_from,
                date_until,
                school_classtypes_ids=ct_ids,
                only_open=True
            )

            for i, row in enumerate(rows):
                repr_row = list(rows[i:i + 1].render())[0]

                date = row.classes_otc.ClassDate
                clsID = row.classes.id
                cls = Class(clsID, date)
                regular_teachers = cls.get_regular_teacher_ids()

                if regular_teachers['auth_teacher_id'] == auth_user_id:
                    continue

                open_classes.append(TR(
                    TD(repr_row.classes_otc.ClassDate, _align="left"),
                    TD(repr_row.classes.Starttime, _align="left"),
                    TD(repr_row.classes.school_locations_id, _align="left"),
                    TD(repr_row.classes.school_classtypes_id, _align="left"),
                    # TD('Actions here?'),
                ))

                open_classes_for_teacher += 1

        if not open_classes_for_teacher:
            error = True
            error_msg = T("No upcoming classes with subs required found for this teacher")


        return dict(
            content = open_classes,
            description = description,
            error = error,
            error_msg = error_msg
        )


    def _render_email_template_teacher_sub_request_open_reminder(self, template_content, cotcID):
        """
        Render mail template for teacher no sub found yet reminders
        :param cotcID: db.classes_otc.id
        :return: html - mail body for reminder
        """
        from openstudio.os_class import Class

        T = current.T
        db = current.db
        DATE_FORMAT = current.DATE_FORMAT
        TIME_FORMAT = current.TIME_FORMAT

        error = False
        error_msg = ''

        cotc = db.classes_otc(cotcID)

        cls = Class(cotc.classes_id, cotc.ClassDate)
        regular_teachers = cls.get_regular_teacher_ids()
        teacher_name = ''
        if not regular_teachers['error']:
            auth_teacher_id = regular_teachers['auth_teacher_id']
            teacher = db.auth_user(auth_teacher_id)
            teacher_name = teacher.first_name

        class_info = TABLE(
            TR(TH(T('Date'), _align="right"),
               TD(cotc.ClassDate.strftime(DATE_FORMAT), _align="left")),
            TR(TH(T('Time'), _align="right"),
               TD(cls.cls.Starttime.strftime(TIME_FORMAT), ' - ',
                  cls.cls.Endtime.strftime(TIME_FORMAT), _align="left")),
            TR(TH(T('Location'), _align="right"),
               TD(cls.get_location_name(), _align="left")),
            TR(TH(T('Class'), _align="right"),
               TD(cls.get_classtype_name(), _align="left")),
            _cellspacing="0", _cellpadding='5px', _width='100%', border="0"
        )

        description = class_info
        content = XML(
            template_content.format(
                teacher_name = teacher_name,
            )
        )

        return dict(
            error = error,
            error_msg = error_msg,
            content=content,
            description=description
        )


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


        image = IMG(_src=URL('default', 'download', ws.picture, scheme=True, host=True),
                    _style="max-width:500px")

        return dict(
            content=DIV(
                image, BR(), BR(),
                XML(content)
            ),
            description=description
        )


    def render_email_template(self,
                              email_template,
                              title='',
                              subject='',
                              description='',
                              comments='',
                              template_content=None,
                              auth_user_id=None,
                              customers_orders_id=None,
                              invoices_id=None,
                              invoices_payments_id=None,
                              classes_otc_id=None,
                              classes_otc_sub_avail_id=None,
                              workshops_products_customers_id=None,
                              return_html=False):
        """
            Renders default email template
            uses the render function from gluon.template instead of response.render
            response throws a RestrictedError when run from the scheduler or shell...
            and we do want scheduled emails to be rendered :)
        """
        # from gluon.template import parse_template
        from gluon.template import render

        db = current.db
        T = current.T
        DATETIME_FORMAT = current.DATETIME_FORMAT
        error = False
        error_msg = ''

        request = current.request

        logo = self._render_email_template_get_logo()

        template_name = 'default.html'
        template_path = os.path.join(request.folder, 'views', 'templates', 'email')
        # Get template
        if template_content is None:
            # Get email template from db
            template_content = self.get_email_template(email_template)

        # Render template
        if email_template == 'order_received':
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

        elif email_template == 'order_delivered':
            subject = T('Order delivered')
            # do some pre-processing to show the correct order info
            content = self._render_email_template_order(template_content, customers_orders_id)

        elif email_template == 'payment_recurring_failed':
            subject = T('Recurring payment failed')
            content = self._render_email_template_payment_recurring_failed(template_content)

        elif email_template == 'teacher_sub_requests_daily_summary':
            result = self._render_email_template_teacher_sub_requests_daily_summary(
                template_content,
                auth_user_id
            )
            title = T("Daily summary - open classes")
            description = result['description']
            content = result['content']
            error = result['error']
            error_msg = result['error_msg']

        elif email_template == 'teacher_sub_request_open_reminder':
            result = self._render_email_template_teacher_sub_request_open_reminder(
                template_content,
                classes_otc_id
            )
            title = T("A friendly reminder")
            description = result['description']
            content = result['content']
            error = result['error']
            error_msg = result['error_msg']

        elif email_template == 'teacher_sub_offer_declined':
            result = self._render_email_template_teacher_sub_offer(
                template_content,
                classes_otc_sub_avail_id
            )
            title = T("Substitute offer declined")
            description = result['description']
            content = result['content']

        elif email_template == 'teacher_sub_offer_accepted':
            result = self._render_email_template_teacher_sub_offer(
                template_content,
                classes_otc_sub_avail_id
            )
            title = T("Thank you for teaching this class")
            description = result['description']
            content = result['content']

        elif email_template == 'workshops_info_mail':
            wspc = db.workshops_products_customers(workshops_products_customers_id)
            wsp = db.workshops_products(wspc.workshops_products_id)
            ws = db.workshops(wsp.workshops_id)
            subject = ws.Name
            title = ws.Name
            result = self._render_email_workshops_info_mail(wspc, wsp, ws)
            content = result['content']
            description = result['description']
            
        elif (email_template == 'sys_verify_email' or
              email_template == 'sys_reset_password'):
            template_name = 'default_simple.html'
            content = XML(template_content)
            subject = subject

        else:
            template_name = 'default.html'
            content = XML(template_content)
            subject = subject

        footer = XML(self.get_email_template('sys_email_footer'))

        template = os.path.join(
            template_path,
            template_name
        )

        context = dict(
            logo = logo,
            title = title,
            description = description,
            content = content,
            comments = comments,
            footer = footer,
            request = request
        )

        html_message = render(
            filename = template,
            path = template_path,
            context = context
        )

        if return_html:
            return dict(
                html_message = html_message,
                error = error,
                error_msg = error_msg
            )
        else:
            msgID = db.messages.insert(
                msg_content = html_message,
                msg_subject = subject
            )

            return msgID


    def render_sys_notification(self,
                                sys_notification,
                                title='',
                                subject='',
                                description='',
                                comments='',
                                customers_orders_id=None,
                                invoices_id=None,
                                invoices_payments_id=None,
                                workshops_products_customers_id=None):
        """
        Render notification email

        :param sys_notifications_id: db.sys_notifications.id
        :param title: Email title
        :param subject: Email subject
        :param description: Email description
        :param comments: Email comments
        :param customers_orders_id: db.customers_orders.id
        :param invoices_id: db.invoices.id
        :param invoices_payments_id: db.invoices_payments.id
        :param workshops_products_customers_id: db.workshops_products_customers.id
        :return: html message for sys_notification
        """
        from gluon.template import render

        T = current.T
        db = current.db
        request = current.request
        DATETIME_FORMAT = current.DATETIME_FORMAT

        logo = self._render_email_template_get_logo()

        if sys_notification == 'order_created':
            from os_order import Order
            order = Order(customers_orders_id)

            notification = db.sys_notifications(Notification='order_created')

            # title
            title = notification.NotificationTitle

            # description
            au = db.auth_user()

            description = DIV(
                T('A new order has been received:'), BR(), BR(),
                TABLE(
                    TR(
                        TD(B(T('Order'))),
                        TD(A('#', order.order.id,
                             _href=URL('orders', 'edit',
                                       vars={'coID':order.order.id},
                                       scheme=True,
                                       host=True),
                             )
                           )
                    ),
                    TR(
                        TD(B(T('Order status'))),
                        TD(order.order.Status)
                    ),
                    TR(
                        TD(B(T('Order date'))),
                        TD(order.order.DateCreated)
                    ),
                    TR(
                        TD(B(T('Customer'))),
                        TD(A(order.get_customer_name(),
                             _href=URL('customers', 'edit',
                                       args=order.order.auth_customer_id,
                                       scheme=True,
                                       host=True)
                             )
                           ),
                    ),
                    TR(
                        TD(B(T('CustomerID'))),
                        TD(order.order.auth_customer_id),
                    )
                )
            )

            # content
            template_content = notification.NotificationTemplate
            content = self._render_email_template_order(template_content, customers_orders_id)

            # Check for order message
            if order.order.CustomerNote:
                comments = DIV(
                    T("The customer provided the following message with the order:"), BR(), BR(),
                    XML(order.order.CustomerNote.replace('\n', '<br>'))
                )

        context = dict(
            logo=logo,
            title=title,
            description=description,
            content=content,
            comments=comments,
            footer='',
            request=request
        )

        template_name = 'default.html'
        template_path = os.path.join(request.folder, 'views', 'templates', 'email')
        template = os.path.join(
            template_path,
            template_name
        )

        message = render(
            filename = template,
            path = template_path,
            context = context
        )


        return message


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
            logo_img = IMG(_src=abs_url,
                           **{'_style': "max-width: 220px;"})

        else:
            logo_img = ''

        return logo_img


