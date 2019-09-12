# -*- coding: utf-8 -*-
"""
    This file holds OpenStudio MailChimp class
"""

from gluon import *
from mailchimp3 import MailChimp
from mailchimp3.mailchimpclient import MailChimpError

class OsMailChimp():
    """
        MailChimp
    """
    def get_client(self):
        """
            :return: mailchimp3 object
        """
        get_sys_property = current.globalenv['get_sys_property']

        mailchimp_api_key = get_sys_property('mailchimp_api_key')
        mailchimp_username = get_sys_property('mailchimp_username')

        if mailchimp_api_key and mailchimp_username:
            mailchimp = MailChimp(mc_api=mailchimp_api_key,
                                  mc_user=mailchimp_username)
        else:
            mailchimp = False

        return mailchimp


    def list_member_add(self, list_id, cuID):
        """
            Add a member to a list
        """
        T = current.T

        from .os_customer import Customer
        customer = Customer(cuID)
        subscriber_hash = customer.get_email_hash('md5')

        mailchimp = self.get_client()

        try:
            mailchimp.lists.members.create_or_update(
                list_id=list_id,
                subscriber_hash=subscriber_hash,
                data = {
                    'email_address': customer.row.email,
                    'status': 'subscribed',
                    'status_if_new': 'pending',
                    'merge_fields': {
                        'FNAME': customer.row.first_name,
                        'LNAME': customer.row.last_name,
                    }
                }
            )
            message = T('Subscription successful, please check your inbox')
        except MailChimpError as e:
            message = DIV(
                T("We encountered an error while trying to subscribe you to this list."), BR(),
                T("Please try again later or contact us when the error persists.")
            )

            # try:
            #     import json
            #     error_data = json.loads(str(e.replace("'", '"')))
            #
            #     message.append(
            #         SPAN(BR(),
            #              T("Details:"), BR(),
            #              type(e),
            #              str(e),
            #              error_data['title']
            #             #  e.title,
            #             # e
            #             # mc_error_data['detail']
            #         )
            #     )
            # except AttributeError:
            #     pass

        return message


    def list_member_delete(self, list_id, cuID):
        """
            Delete a member from a list
        """
        from .os_customer import Customer

        T = current.T
        customer = Customer(cuID)

        mailchimp = self.get_client()

        error = False
        message = T('Successfully unsubscribed from list')
        try:
            mailchimp.lists.members.delete(
                list_id=list_id,
                subscriber_hash=customer.get_email_hash('md5')
            )
        except MailChimpError as e:
            error = True
            message = DIV(
                T("We encountered an error while trying to unsubscribe you from this list."), BR(),
                T("Please try again later or contact us when the error persists."),
            )

        return dict(error=error, message=message)


    def get_mailing_lists(self):
        """
            returns gluon.dal.rows object containing rows from db.mailing_lists
        """
        db = current.db

        query = (db.mailing_lists.MailChimpListID != None)
        rows = db(query).select(db.mailing_lists.ALL,
                                orderby=db.mailing_lists.Name)

        return rows


    def get_mailing_list_customer_subscription_status(self, mailchimp, list_id, cuID):
        """
        :param: mailchimp: MailChimp object (mailchimp3)
        :param cuID: db.auth_user.id
        :return: boolean
        """

        import hashlib
        from .os_customer import Customer

        customer = Customer(cuID)
        subscriber_hash = customer.get_email_hash('md5')
        try:
            member =  mailchimp.lists.members.get(list_id=list_id,
                                                  subscriber_hash=subscriber_hash)
            return member['status']
        except MailChimpError as e:
            return 'error'


    def get_mailing_lists_customer_display(self, cuID):
        """
        :param cuID: db.auth_user.id
        :return:
        """
        from .os_gui import OsGui
        T = current.T
        os_gui = OsGui()

        mailchimp = self.get_client()
        if not mailchimp:
            return T("Unable to load mailing lists, please contact your studio.")

        rows = self.get_mailing_lists()

        header = THEAD(TR(
            TH(T('List')),
            TH(T('Description')),
            TH(T('Frequency')),
            TH(T('Status')),
            TH()
        ))

        table = TABLE(header, _class='table table-striped table-hover')
        for row in rows:
            list_id = row.MailChimpListID
            status = self.get_mailing_list_customer_subscription_status(
                mailchimp,
                list_id,
                cuID
            )

            tr = TR(
                TD(row.Name),
                TD(XML(row.Description)),
                TD(row.Frequency),
                TD(self.get_mailing_list_customer_display_status(
                    status,
                    os_gui
                )),
                TD(self.get_mailing_list_customer_display_buttons(
                    status,
                    list_id,
                    os_gui
                ))
            )
            table.append(tr)

        return table


    def get_mailing_list_customer_display_status(self, status, os_gui):
        """
        :param status: mailchimp subsription status
        :param os_gui: OsGui object
        :return: label describing list subscription status
        """
        T = current.T

        if status == 'subscribed':
            label_type = 'success'
            label_text = T('Subscribed')
        elif status == 'pending':
            label_type = 'primary'
            label_text = T('Awaiting confirmation')
        else:
            label_type = 'default'
            label_text = T('Not subscribed')

        return os_gui.get_label(label_type, label_text)


    def get_mailing_list_customer_display_buttons(self, status, list_id, os_gui):
        """
        :param status: mailchimp subsription status
        :param os_gui: OsGui object
        :return: label describing list subscription status
        """
        T = current.T

        button = ''
        label = ''
        onclick = "return confirm('" + \
            T('Do you really wish to unsubscribe from this list?') \
                         + "');"
        unsubscribe = os_gui.get_button(
            'noicon',
            URL('mailchimp', 'unsubscribe', vars={'list_id': list_id}),
            btn_class='btn-link',
            btn_size = '',
            title=T('Unsubscribe'),
            onclick=onclick
        )

        if status == 'error' or status == 'cleaned' or status == 'unsubscribed':
            button = os_gui.get_button(
                'noicon',
                URL('mailchimp', 'subscribe',
                    vars={'list_id': list_id},
                    extension=''),
                title=T('Subscribe'),
                btn_class='btn-success'
            )
        elif status == 'subscribed' or status == 'pending':
            button = unsubscribe

        return DIV(button, _class='pull-right')




