# -*- coding: utf-8 -*-

import datetime

from gluon import *
from general_helpers import max_string_length
from general_helpers import represent_validity_units



class School:
    def get_classcards(self, public_only=True):
        """
            :param public_only: Defines whether or not to show only public classcards, True by default
                                False means all cards are returned
            Returns classcards for school
        """
        db = current.db

        query = (db.school_classcards.Archived == False)
        if public_only:
            query &= (db.school_classcards.PublicCard == True)

        return db(query).select(db.school_classcards.ALL,
                                orderby=db.school_classcards.Trialcard |
                                        db.school_classcards.Name)


    def get_classcards_formatted(self,
                                 auth_user_id=None,
                                 public_only=True,
                                 per_row=3,
                                 link_type=None):
        """
            :param public_only: show only public cards - Default: True
            :param per_row: Number of cards in each row - Default 4. Allowed values: [3, 4]
            :param link_type: Specified what kind of link will be shown in the footer of each classcard.
                Allowed values: ['backend', 'shop']
                - backend adds a modal to choose date
                - shop adds a button to add the card to the shopping cart
            Returns classcards formatted in BS3 style

        """
        def get_validity(row):
            """
                takes a db.school_classcards() row as argument
            """
            validity = SPAN(unicode(row.Validity), ' ')

            validity_in = represent_validity_units(row.ValidityUnit, row)
            if row.Validity == 1:  # Cut the last 's"
                validity_in = validity_in[:-1]

            validity.append(validity_in)

            return validity

        from os_customer import Customer

        TODAY_LOCAL = current.TODAY_LOCAL
        os_gui = current.globalenv['os_gui']
        T = current.T

        customer_has_membership = False
        if auth_user_id:
            customer = Customer(auth_user_id)
            customer_has_membership = customer.has_membership_on_date(TODAY_LOCAL)

        if per_row == 3:
            card_class = 'col-md-4'
        elif per_row == 4:
            card_class = 'col-md-3'
        else:
            raise ValueError('Incompatible value: per_row has to be 3 or 4')

        rows = self.get_classcards(public_only=public_only)

        cards = DIV()
        display_row = DIV(_class='row')
        row_item = 0

        for i, row in enumerate(rows):
            repr_row = list(rows[i:i + 1].render())[0]

            card_name = max_string_length(row.Name, 37)
            validity = get_validity(row)

            card = DIV(
                DIV(
                    DIV(H3(card_name,
                           _class="widget-user-username"),
                        H4(repr_row.Price,
                           _class="widget-user-desc"),
                        # H5(repr_row.Description,
                        #    _class="widget-user-desc"),
                        _class="widget-user-header bg-aqua-active"
                    ),
                    DIV(DIV(repr_row.Description, _class='col-md-12'),
                            _class='box-body'),
                    DIV(
                        DIV(
                            DIV(
                                DIV(H5(validity,
                                        _class="description-header"),
                                    SPAN(T("Validity"), _class="description-text"),
                                    _class="description-block"
                                ),
                                _class="col-sm-4 border-right"
                            ),
                            DIV(
                                DIV(H5(repr_row.Classes,
                                        _class="description-header"),
                                    SPAN(T("Classes"), _class="description-text"),
                                    _class="description-block"
                                ),
                                _class="col-sm-4 border-right"
                            ),
                            DIV(
                                DIV(H5(self._get_classcards_formatted_button_to_cart(
                                        row.id,
                                        row.MembershipRequired,
                                        customer_has_membership
                                        ),
                                        _class="description-header"),
                                    SPAN(T(""), _class="description-text"),
                                    _class="description-block"
                                ),
                                _class="col-sm-4 border-right"
                            ),
                            _class="row"
                        ),
                        _class="box-footer",
                    ),
                    _class="box box-widget widget-user"
                ),
                _class=card_class
            )

            # card_content = TABLE(TR(TD(T('Validity')),
            #                         TD(validity)),
            #                      TR(TD(T('Classes')),
            #                         TD(repr_row.Classes)),
            #                      TR(TD(T('Price')),
            #                         TD(repr_row.Price)),
            #                      TR(TD(T('Description')),
            #                         TD(repr_row.Description or '')),
            #                      _class='table')
            #
            # if row.Trialcard:
            #     panel_class = 'box-success'
            # else:
            #     panel_class = 'box-primary'
            #
            # footer_content = ''
            # if link_type == 'shop':
            #     footer_content = self._get_classcards_formatted_button_to_cart(
            #         row.id,
            #         row.MembershipRequired,
            #         customer_has_membership
            #     )
            #
            # card = DIV(os_gui.get_box_table(card_name,
            #                                 card_content,
            #                                 panel_class,
            #                                 show_footer=True,
            #                                 footer_content=footer_content),
            #            _class=card_class)

            display_row.append(card)

            row_item += 1

            if row_item == per_row or i == (len(rows) - 1):
                cards.append(display_row)
                display_row = DIV(_class='row')

                row_item = 0

        return cards


    def _get_classcards_formatted_button_to_cart(self,
                                                 scdID,
                                                 membership_required,
                                                 customer_has_membership):
        """
            Get button to add card to shopping cart
        """
        os_gui = current.globalenv['os_gui']
        T = current.T

        if membership_required and not customer_has_membership:
            return A(SPAN(T("Membership required")),
                     _href=URL('shop', 'memberships'))

        return A(SPAN(os_gui.get_fa_icon('fa-shopping-cart fa-2x')),
                 _href=URL('classcard_add_to_cart', vars={'scdID': scdID}),
                 _class='')


    def _get_subscriptions_formatted_button_to_cart(self,
                                                    ssuID,
                                                    membership_required,
                                                    customer_has_membership,
                                                    customer_subscriptions_ids):
        """
            Get button to add card to shopping cart
        """
        os_gui = current.globalenv['os_gui']
        T = current.T

        if membership_required and not customer_has_membership:
            return A(SPAN(T("Membership required")),
                     _href=URL('shop', 'memberships'))

        if ssuID in customer_subscriptions_ids:
            return SPAN(
                SPAN(T("You have this subscription"), _class='bold'), ' ', XML('&bull;'), ' ',
                SPAN(A(T("View invoices"),
                       _href=URL('profile', 'invoices')))
            )

        return A(SPAN(os_gui.get_fa_icon('fa-shopping-cart'), ' ', T('Get this subscription')),
                 _href=URL('subscription_terms', vars={'ssuID': ssuID}))


    def get_subscriptions(self, public_only=True):
        """
            :param public: boolean, defines whether to show only public or all subscriptions
            :return: list of school_subscriptions
        """
        db = current.db

        query = (db.school_subscriptions.id > 0)

        if public_only:
            query &= (db.school_subscriptions.PublicSubscription == True)

        rows = db(query).select(db.school_subscriptions.ALL,
                                orderby=~db.school_subscriptions.SortOrder | db.school_subscriptions.Name)

        return rows


    def get_subscriptions_formatted(self,
                                    auth_customer_id=None,
                                    per_row=3,
                                    public_only=True,
                                    link_type='shop'):
        """
            :param public: boolean, defines whether to show only public or all subscriptions
            :return: list of school_subscriptions formatted for shop
        """
        from general_helpers import get_last_day_month
        from openstudio.os_school_subscription import SchoolSubscription
        from openstudio.os_customer import Customer


        T = current.T
        TODAY_LOCAL = current.TODAY_LOCAL
        os_gui = current.globalenv['os_gui']
        get_sys_property = current.globalenv['get_sys_property']

        customer_has_membership = False
        customer_subscriptions_ids = []
        if auth_customer_id:
            startdate = TODAY_LOCAL
            shop_subscriptions_start = get_sys_property('shop_subscriptions_start')
            if not shop_subscriptions_start == None:
                if shop_subscriptions_start == 'next_month':
                    startdate = get_last_day_month(TODAY_LOCAL) + datetime.timedelta(days=1)

            customer = Customer(auth_customer_id)
            customer_has_membership = customer.has_membership_on_date(startdate)
            customer_subscriptions_ids = customer.get_school_subscriptions_ids_on_date(startdate)

        if per_row == 3:
            card_class = 'col-md-4'
        elif per_row == 4:
            card_class = 'col-md-3'
        else:
            raise ValueError('Incompatible value: per_row has to be 3 or 4')

        rows = self.get_subscriptions(public_only=public_only)

        subscriptions = DIV()
        display_row = DIV(_class='row')
        row_item = 0

        for i, row in enumerate(rows):
            repr_row = list(rows[i:i + 1].render())[0]

            ssu = SchoolSubscription(row.id)
            name = max_string_length(row.Name, 33)

            classes = ''
            if row.Unlimited:
                classes = T('Unlimited')
            elif row.SubscriptionUnit == 'week':
                classes = SPAN(unicode(row.Classes) + ' / ' + T('Week'))
            elif row.SubscriptionUnit == 'month':
                classes = SPAN(unicode(row.Classes) + ' / ' + T('Month'))

            subscription_content = TABLE(TR(TD(T('Classes')),
                                            TD(classes)),
                                         TR(TD(T('Monthly')),
                                            TD(ssu.get_price_on_date(datetime.date.today()))),
                                         TR(TD(T('Description')),
                                            TD(row.Description or '')),
                                         _class='table')

            panel_class = 'box-primary'

            footer_content = ''
            if link_type == 'shop':
                footer_content = self._get_subscriptions_formatted_button_to_cart(
                    row.id,
                    row.MembershipRequired,
                    customer_has_membership,
                    customer_subscriptions_ids
                )

            subscription = DIV(os_gui.get_box_table(name,
                                                    subscription_content,
                                                    panel_class,
                                                    show_footer=True,
                                                    footer_content=footer_content),
                               _class=card_class)

            display_row.append(subscription)

            row_item += 1

            if row_item == per_row or i == (len(rows) - 1):
                subscriptions.append(display_row)
                display_row = DIV(_class='row')
                row_item = 0

        return subscriptions


    def _get_memberships_formatted_button_to_cart(self, smID):
        """
            Get button to add card to shopping cart
        """
        os_gui = current.globalenv['os_gui']
        T = current.T

        return A(SPAN(os_gui.get_fa_icon('fa-shopping-cart'), ' ', T('Get this membership')),
                 _href=URL('membership_terms', vars={'smID': smID}))


    def get_memberships(self, public_only=True):
        """
            :param public: boolean, defines whether to show only public or all memberships
            :return: list of school_memberships
        """
        db = current.db

        query = (db.school_memberships.id > 0)

        if public_only:
            query &= (db.school_memberships.PublicMembership == True)

        rows = db(query).select(db.school_memberships.ALL,
                                orderby=db.school_memberships.Name)

        return rows


    def get_memberships_formatted(self,
                                  per_row=3,
                                  public_only=True,
                                  link_type='shop'):
        """
            :param public: boolean, defines whether to show only public or all memberships
            :return: list of school_memberships formatted for shop
        """
        from openstudio.tools import OsTools
        from openstudio.os_school_membership import SchoolMembership

        os_gui = current.globalenv['os_gui']
        T = current.T
        os_tools = OsTools()

        if per_row == 3:
            card_class = 'col-md-4'
        elif per_row == 4:
            card_class = 'col-md-3'
        else:
            raise ValueError('Incompatible value: per_row has to be 3 or 4')

        rows = self.get_memberships(public_only=public_only)

        memberships = DIV()
        display_row = DIV(_class='row')
        row_item = 0

        for i, row in enumerate(rows):
            repr_row = list(rows[i:i + 1].render())[0]

            sm = SchoolMembership(row.id)
            name = max_string_length(row.Name, 33)

            validity = os_tools.format_validity(row.Validity, row.ValidityUnit)

            membership_content = TABLE(TR(TD(T('Validity')),
                                          TD(validity)),
                                       TR(TD(T('Price')),
                                          TD(sm.get_price_on_date(datetime.date.today()))),
                                       TR(TD(T('Description')),
                                          TD(row.Description or '')),
                                       _class='table')

            panel_class = 'box-primary'

            footer_content = ''
            if link_type == 'shop':
                footer_content = self._get_memberships_formatted_button_to_cart(row.id)

            membership = DIV(os_gui.get_box_table(
                name,
                membership_content,
                panel_class,
                show_footer=True,
                footer_content=footer_content),
                _class=card_class)

            display_row.append(membership)

            row_item += 1

            if row_item == per_row or i == (len(rows) - 1):
                memberships.append(display_row)
                display_row = DIV(_class='row')
                row_item = 0

        return memberships
