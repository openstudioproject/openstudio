# coding: utf8

from openstudio.os_mail import OsMail
from openstudio.os_workshops_helper import WorkshopsHelper


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('update', 'workshops_mail_customers'))
def message():
    '''
        Function to display a message
    '''
    if request.extension != 'load':
        response.view = 'general/only_content.html'

    category = request.vars['category']
    modals = DIV()
    content = ''
    msgID = None
    sent = True


    if category == 'workshops':
        msgID = session.workshops_msgID
        wsID = request.vars['wsID']
        ws_sent = message_count_sent_workshop_customers(msgID, wsID)

    if msgID:
        m = db.messages(msgID)

        infobar = ''
        if not ws_sent == True:
            result = message_get_workshops_sent(m, wsID, ws_sent)
            infobar = result['infobar']
            modals.append(result['modal'])

        header = DIV(SPAN(m.created_at.strftime(DATETIME_FORMAT),
                          _class='small_font grey right'),
                     H4(B(m.msg_subject)),
                     _class='message_header')
        body = DIV(XML(m.msg_content),
                   _class='message_body')

        content = DIV(header, infobar, body, modals)

    return dict(content=content)


def message_count_sent_workshop_customers(msgID, wsID):
    '''
        Returns count of total customers for a workshop and of how many
        received the message
    '''
    # Get list of all customers with email for a workshop
    wh = WorkshopsHelper()
    customers_all = wh.get_all_workshop_customers(wsID, ids_only=True)

    # Get count of all customers to whom the message was sent successfully
    query = (db.customers_messages.messages_id == msgID) & \
            (db.customers_messages.Status == 'sent')
    rows = db(query).select(db.customers_messages.auth_customer_id,
                            distinct=True)
    customers_sent = []
    for row in rows:
        customers_sent.append(row.auth_customer_id)

    difference = set(customers_all).difference(set(customers_sent))  # customers to whom this mail wasn't sent yet


    if len(difference) == 0:
        rvalue = True
    else:
        failed = len(difference)
        rvalue = {'sent'  : len(customers_sent),
                  'fail'  : failed,
                  'total' : len(customers_all)}

    return rvalue


def message_get_workshops_sent(m, wsID, ws_sent=None):
    '''
        Returns an alert with a modal to show a list of customers to whom
        the message hasn't been sent yet.
    '''
    # get modal to show list of customers and sent status
    modal_title = m.msg_subject
    modal_content = LOAD('messages', 'message_get_workshops_customers_reached.load',
                         ajax=True,
                         vars={'msgID':m.id,
                               'wsID' :wsID})

    #btn_icon = SPAN(SPAN(_class='glyphicon glyphicon-envelope'), ' ',
    #                T('Details'))

    result = os_gui.get_modal(button_text=T("Details"),
                              modal_title=modal_title,
                              modal_content=modal_content,
                              modal_class='sent_details',
                              modal_size='lg',
                              button_class='btn-sm btn-link')

    info_msg = SPAN()
    info_msg.append(T("This message hasn't been sent to "))
    info_msg.append(unicode(ws_sent['fail']))
    info_msg.append(T(" customers. "))
    #info_msg.append(A(B(T("Details")),
                      #_href='#',
                      #_class='alert-link'))
    info_msg.append(result['button'])
    info = os_gui.get_alert('info', info_msg)
    infobar = DIV(info,
                  _class='message_info')

    return dict(infobar=infobar,
                modal=result['modal'])

#
# @auth.requires(auth.has_membership(group_id='Admins') or \
#                auth.has_permission('update', 'workshops_mail_customers'))
# def message_get_workshops_customers_reached():
#     '''
#         Returns a list of sent messages to customers
#     '''
#     msgID = request.vars['msgID']
#     wsID = request.vars['wsID']
#
#     # get successful sent rows
#     query = (db.customers_messages.messages_id == msgID) & \
#             (db.customers_messages.Status == 'sent')
#     rows = db(query).select(db.customers_messages.auth_customer_id)
#     customers_sent = []
#     for row in rows:
#         customers_sent.append(row.auth_customer_id)
#
#     # get list of all customers attending workshop
#     helper = WorkshopsHelper()
#     customers_all = helper.get_all_workshop_customers(wsID, ids_only=True)
#     difference = set(customers_all).difference(set(customers_sent)) # customers to whom this mail wasn't sent yet
#
#     content = DIV()
#     # get rows for display
#     table = TABLE(_class='table table-hover')
#     table.append(TR(TH(''),
#                     TH(T('Customer')),
#                     TH(T('Status')),
#                     TH(T('Sent at')),
#                     TH(),
#                     _class='header'))
#
#     # Add customers to whom the message hasn't been sent yet
#     query = (db.auth_user.id.belongs(difference))
#     rows = db(query).select(db.auth_user.id,
#                             db.auth_user.trashed,
#                             db.auth_user.thumbsmall,
#                             db.auth_user.birthday,
#                             db.auth_user.display_name,
#                             orderby=db.auth_user.display_name)
#     for i, row in enumerate(rows):
#         repr_row = list(rows[i:i+1].render())[0]
#
#         send = A(T("Send"),
#                  _href=URL('message_send_to_customer',
#                            vars={'cuID': row.id,
#                                  'msgID': msgID}),
#                  cid=request.cid)
#
#         table.append(TR(TD(repr_row.thumbsmall,
#                            _class='os-customer_image_td'),
#                         TD(row.display_name),
#                         TD(),
#                         TD(T('Not yet')),
#                         TD(send),
#                         ))
#
#     # Add customers to whom the message has been sent
#     left = [ db.auth_user.on(db.customers_messages.auth_customer_id == \
#                              db.auth_user.id) ]
#     query = (db.customers_messages.messages_id == msgID)
#     rows = db(query).select(db.customers_messages.ALL,
#                             db.auth_user.id,
#                             db.auth_user.trashed,
#                             db.auth_user.thumbsmall,
#                             db.auth_user.birthday,
#                             db.auth_user.display_name,
#                             left=left,
#                             orderby=~db.customers_messages.Created_at)
#
#
#     for i, row in enumerate(rows):
#         resend = ''
#         if row.customers_messages.Status == 'fail' and \
#            not row.customers_messages.auth_customer_id in customers_sent:
#             resend = A(T("Resend"),
#                        _href=URL('message_send_to_customer',
#                                  vars={'cuID': row.auth_user.id,
#                                        'msgID': msgID}),
#                        cid=request.cid)
#
#         repr_row = list(rows[i:i+1].render())[0]
#
#         customers_name = SPAN(row.auth_user.display_name)
#         table.append(TR(TD(repr_row.auth_user.thumbsmall,
#                            _class='os-customer_image_td'),
#                         TD(customers_name),
#                         TD(repr_row.customers_messages.Status),
#                         TD(repr_row.customers_messages.Created_at),
#                         TD(resend),
#                         ))
#
#     content.append(table)
#
#     return dict(content=content)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('update', 'workshops_mail_customers'))
def message_send_to_customer():
    '''
        Send mail to customer
        request.vars['cuID'] is expected to be the customers id
        request.vars['msgID'] is expected to be the messages id
    '''
    cuID = request.vars['cuID']
    msgID = request.vars['msgID']

    osmail = OsMail()
    osmail.send(msgID, cuID)

    redirect(URL('message_get_workshops_customers_reached',
                 vars={'msgID':msgID}))


def test_osmail_render_template():
    """
        function to be used when testing rendering of OsMail messages
    """
    if not web2pytest.is_running_under_test(request, request.application) and not auth.has_membership(group_id='Admins'):
        redirect(URL('default', 'user', args=['not_authorized']))

    email_template = request.vars['email_template']
    invoices_id = request.vars['invoices_id']
    customers_orders_id = request.vars['customers_orders_id']
    invoices_payments_id = request.vars['invoices_payments_id']

    os_mail = OsMail()
    rendered_message = T('template not found...')
    if email_template == 'email_template_payment_recurring_failed':
        pass
    elif email_template == 'email_template_order_received' or email_template == 'email_template_order_delivered':
        rendered_message = os_mail.render_email_template(
            email_template,
            customers_orders_id = customers_orders_id,
            return_html = True
        )
    elif email_template == 'email_template_sys_reset_password':
        rendered_message = os_mail.render_email_template(email_template,
                                                         return_html = True)

    return rendered_message