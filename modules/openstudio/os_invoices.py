# -*- coding: utf-8 -*-

import datetime


from gluon import *

class Invoices:
    """
        This class holds functions related to multiple invoices
    """
    def _add_get_form_permissions_check(self):
        """
            Check if the currently logged in user is allowed to create
            invoices
        """
        auth = current.auth
        if not (auth.has_membership(group_id='Admins') or
                auth.has_permission('create', 'invoices')):
            redirect(URL('default', 'user', args=['not_authorized']))


    def _add_get_form_set_default_values_customer(self, customer):
        """
        :param customer: Customer object
        :return: None
        """
        db = current.db
        address = ''
        if customer.row.address:
            address = ''.join([address, customer.row.address, '\n'])
        if customer.row.city:
            address = ''.join([address, customer.row.city, ' '])
        if customer.row.postcode:
            address = ''.join([address, customer.row.postcode, '\n'])
        if customer.row.country:
            address = ''.join([address, customer.row.country])

        db.invoices.CustomerCompany.default = customer.row.company
        db.invoices.CustomerName.default = customer.row.full_name
        db.invoices.CustomerAddress.default = address


    def _add_get_form_enable_minimal_fields(self):
        """
            Only enable the bare minimum of fields
        """
        db = current.db

        for field in db.invoices:
            field.readable=False
            field.writable=False

        db.invoices.invoices_groups_id.readable = True
        db.invoices.invoices_groups_id.writable = True
        db.invoices.Description.readable = True
        db.invoices.Description.writable = True


    def _add_get_form_enable_subscription_fields(self, csID):
        """
            Enable fields required for subscriptions
        """
        from os_customer_subscription import CustomerSubscription

        db = current.db

        cs = CustomerSubscription(csID)
        db.invoices.payment_methods_id.default = cs.payment_methods_id
        db.invoices.SubscriptionYear.readable = True
        db.invoices.SubscriptionYear.writable = True
        db.invoices.SubscriptionMonth.readable = True
        db.invoices.SubscriptionMonth.writable = True


    def _add_get_form_enable_membership_fields(self, cmID):
        """
        Enable fields required for customer memberships

        :param cmID: db.customers_memberships.id
        :return: None
        """
        from openstudio.os_customer_membership import CustomerMembership

        db = current.db

        cm = CustomerMembership(cmID)
        db.invoices.payment_methods_id.default = cm.row.payment_methods_id
        db.invoices.MembershipPeriodStart.readable = True
        db.invoices.MembershipPeriodStart.writable = True
        db.invoices.MembershipPeriodEnd.readable = True
        db.invoices.MembershipPeriodEnd.writable = True


    def add_get_form(self, cuID,
                           csID = None,
                           cmID = None,
                           full_width = True):
        """
            Returns add form for an invoice
        """
        from os_customer import Customer
        from os_invoice import Invoice

        self._add_get_form_permissions_check()

        db = current.db
        T  = current.T

        customer = Customer(cuID)
        self._add_get_form_set_default_values_customer(customer)
        self._add_get_form_enable_minimal_fields()
        if csID:
            self._add_get_form_enable_subscription_fields(csID)
        if cmID:
            self._add_get_form_enable_membership_fields(cmID)

        form = SQLFORM(db.invoices, formstyle='bootstrap3_stacked')

        elements = form.elements('input, select, textarea')
        for element in elements:
            element['_form'] = "invoice_add"

        form_element = form.element('form')
        form['_id'] = 'invoice_add'

        if form.process().accepted:
            iID = form.vars.id
            invoice = Invoice(iID) # This sets due date and Invoice (calls invoice.on_create() #
            invoice.link_to_customer(cuID)
            self._add_reset_list_status_filter()

            if csID:
                invoice.link_to_customer_subscription(csID)
                invoice.item_add_subscription(
                    form.vars.SubscriptionYear,
                    form.vars.SubscriptionMonth
                )

            if cmID:
                invoice.item_add_membership(
                    cmID,
                    form.vars.MembershipPeriodStart,
                    form.vars.MembershipPeriodEnd
                )

            redirect(URL('invoices', 'edit', vars={'iID':iID}))


        # So the grids display the fields normally
        for field in db.invoices:
            field.readable=True

        return form


    def add_get_modal(self, crud_form):
        """
            Returns add modal for new invoice
        """
        T = current.T
        os_gui = current.globalenv['os_gui']
        gen_passwd = current.globalenv['generate_password']

        modal_class = gen_passwd()
        button_text = XML(SPAN(SPAN(_class='fa fa-plus'), ' ',
                          T("Add")))
        result = os_gui.get_modal(button_text=button_text,
                                  button_title=T("Add invoice"),
                                  modal_title=T("Add invoice"),
                                  modal_content=crud_form,
                                  modal_footer_content=os_gui.get_submit_button('invoice_add'),
                                  modal_class=modal_class,
                                  button_class='btn-sm')

        button = SPAN(result['button'], result['modal'])

        return dict(button=button, modal_class=modal_class)


    def _add_reset_list_status_filter(self):
        """
            Reset session variable that holds status for filter
        """
        session = current.session
        session.invoices_list_status = None


    def _list_set_status_filter(self):
        """
            Sets session variable that holds the status for the filter
        """
        request = current.request
        session = current.session
        # status definitions
        if 'status' in request.vars:
            session.invoices_list_status = request.vars['status']
        elif session.invoices_list_status:
            pass
        else:
            session.invoices_list_status = 'all'


    def list_get_status_filter(self):
        """
            Returns the filter for Invoice statuses
        """
        self._list_set_status_filter()

        invoice_statuses = current.globalenv['invoice_statuses']
        invoice_statuses.append(['overdue', current.T('Overdue')])

        session = current.session

        form = SQLFORM.factory(
            Field('status',
                default=session.invoices_list_status,
                requires=IS_IN_SET(invoice_statuses,
                                   zero=current.T('All statuses')))
        )

        form = form.element('form')
        form['_class'] = 'no-margin-top no-margin-bottom'

        select = form.element('#no_table_status')
        select['_onchange'] = 'this.form.submit();'

        #TODO: The pull-right class causes it to not work on mobile, should be reworked to show up
        # should be reworked nicely without the pull-right at some point.
        form = DIV(form.custom.begin,
                   form.custom.widget.status,
                   form.custom.end,
                   _class='pull-right',
                   _id='invoices_status_filter')

        return form


    def represent_invoice_for_list(self, iID,
                                         invoice_id,
                                         repr_status,
                                         status,
                                         payment_methods_id):
        """
            Represent invoice for lists
            invoice_id and status should come from a rendered row (repr_row)
        """
        os_gui = current.globalenv['os_gui']

        payment = self.represent_invoice_for_list_get_payment(iID, status, payment_methods_id)

        invoice = DIV(repr_status,
                      os_gui.get_button(
                            'noicon',
                            URL('invoices', 'edit', vars={'iID':iID},
                                extension=''),
                            title=invoice_id,
                            btn_size = 'btn-sm',
                            btn_class = 'btn-link'), BR(),
                      payment)

        return invoice


    def represent_invoice_for_list_get_payment(self, iID, status, payment_methods_id):
        """
            Get add payment modal when no payment is found, or just
            show the information for the payments found.
        """
        db = current.db
        os_gui = current.globalenv['os_gui']
        T = current.T

        query = (db.invoices_payments.invoices_id == iID)
        rows = db(query).select(db.invoices_payments.ALL)

        # show payments
        payments = DIV()
        for row in rows.render():
            payments.append(SPAN(
                row.PaymentDate, ': ',
                row.Amount,
                BR(),
                _class = 'grey small_font'
            ))

        if status == 'sent':
            if payment_methods_id == 3: # direct debit
                payments.append(SPAN(T('Direct debit'), _class='grey small_font'))
            else:
                # show add payment
                content = LOAD('invoices', 'payment_add.load', ajax=True,
                                vars={'iID':iID})

                invoice = db.invoices(iID)
                title = current.T('Add payment for invoice') + ' #' + \
                        invoice.InvoiceID

                button_text = XML(SPAN(
                    SPAN(_class='fa fa-credit-card'), ' ',
                    current.T('Add payment'),
                    _class='small_font grey'
                ))

                form_id = 'form_payment_add_' + unicode(iID)

                result = os_gui.get_modal(button_text=button_text,
                                          button_title=current.T("Add payment"),
                                          modal_title=title,
                                          modal_content=content,
                                          modal_footer_content=os_gui.get_submit_button(form_id),
                                          modal_class='form_payment_add_' + unicode(iID),
                                          button_class='btn-xs invoice_list_add_payment')

                payments.append(SPAN(result['button'], result['modal']))

        return payments


    def list_invoices(self,
                      cuID=None,
                      csID=None,
                      cmID=None,
                      search_enabled=False,
                      group_filter_enabled=False,
                      only_teacher_credit_invoices=False,
                      only_employee_claim_credit_invoices=False):
        db = current.db
        auth = current.auth
        session = current.session
        grid_ui = current.globalenv['grid_ui']
        DATE_FORMAT = current.DATE_FORMAT
        from general_helpers import datestr_to_python
        from openstudio.os_gui import OsGui
        os_gui = OsGui()

        T = current.T

        session.invoices_invoice_payment_add_back = None

        # disable unused fields
        db.invoices.id.readable = False
        db.invoices.invoices_groups_id.readable = False
        db.invoices.Footer.readable = False
        db.invoices.Note.readable = False
        db.invoices.Terms.readable = False
        db.invoices.TeacherPayment.readable = False
        db.invoices.EmployeeClaim.readable = False

        links = [dict(header=T("Balance"),
                      body=self._list_invoices_get_balance),
                 lambda row: os_gui.get_label('primary', T('Teacher inv')) if row.invoices.TeacherPayment else '',
                 self._list_invoices_get_buttons]
        left = [db.invoices_amounts.on(db.invoices_amounts.invoices_id ==
                                       db.invoices.id),
                db.invoices_customers.on(
                    db.invoices_customers.invoices_id == db.invoices.id),
                db.invoices_customers_subscriptions.on(
                    db.invoices_customers_subscriptions.invoices_id ==
                    db.invoices.id),
                db.invoices_customers_memberships.on(
                    db.invoices_customers_memberships.invoices_id ==
                    db.invoices.id)
                ]

        fields = [db.invoices.Status,
                  db.invoices.InvoiceID,
                  db.invoices.Description,
                  db.invoices.DateCreated,
                  db.invoices.DateDue,
                  db.invoices_amounts.TotalPriceVAT,
                  db.invoices.TeacherPayment]

        query = (db.invoices.id > 0)
        # Status filter
        query = self._list_invoices_get_status_query(query)
        if search_enabled:
            query = self._list_invoices_get_search_query(query)
        if group_filter_enabled:
            query = self._list_invoices_get_groups_query(query)
        if only_teacher_credit_invoices:
            query &= (db.invoices.TeacherPayment == True)
        if only_employee_claim_credit_invoices:
            query &= (db.invoices.EmployeeClaim == True)

        # General list, list for customer or list for subscription
        if not cuID and not csID:
            # list all invoices
            fields.insert(2, db.invoices.CustomerListName)

        if cuID:
            query &= (db.invoices_customers.auth_customer_id == cuID)
        if cmID:
            query &= (db.invoices_customers_memberships.customers_memberships_id == cmID)
        if csID:
            query &= (db.invoices_customers_subscriptions.customers_subscriptions_id == csID)
            fields.insert(3, db.invoices.SubscriptionMonth)
            fields.insert(4, db.invoices.SubscriptionYear)

        delete_permission = auth.has_membership(group_id='Admins') or \
                            auth.has_permission('delete', 'invoices')

        grid = SQLFORM.grid(query,
                            links=links,
                            left=left,
                            field_id=db.invoices.id,
                            fields=fields,
                            create=False,
                            editable=False,
                            details=False,
                            searchable=False,
                            deletable=delete_permission,
                            csv=False,
                            # maxtextlengths=maxtextlengths,
                            orderby=~db.invoices.id,
                            ui=grid_ui)
        grid.element('.web2py_counter', replace=None)  # remove the counter
        grid.elements('span[title=Delete]', replace=None)  # remove text from delete button

        form_search = ''
        content = DIV()
        if search_enabled:
            #response.js = 'set_form_classes();' # we're no longer in a loaded component
            request = current.request
            if 'search' in request.vars:
                session.invoices_list_invoices_search = request.vars['search']
                # date_created_from = datestr_to_python(DATE_FORMAT, request.vars['date_created_from'])
                # session.invoices_list_invoices_date_created_from = date_created_from
                try:
                    date_created_from = datestr_to_python(DATE_FORMAT, request.vars['date_created_from'])
                    session.invoices_list_invoices_date_created_from = date_created_from
                except (ValueError, AttributeError):
                    session.invoices_list_invoices_date_created_from = None
                try:
                    date_created_until = datestr_to_python(DATE_FORMAT, request.vars['date_created_until'])
                    session.invoices_list_invoices_date_created_until = date_created_until
                except (ValueError, AttributeError):
                    session.invoices_list_invoices_date_created_until = None
                try:
                    date_due_from = datestr_to_python(DATE_FORMAT, request.vars['date_due_from'])
                    session.invoices_list_invoices_date_due_from = date_due_from
                except (ValueError, AttributeError):
                    session.invoices_list_invoices_date_due_from = None
                try:
                    date_due_until = datestr_to_python(DATE_FORMAT, request.vars['date_due_until'])
                    session.invoices_list_invoices_date_due_until = date_due_until
                except (ValueError, AttributeError):
                    session.invoices_list_invoices_date_due_until = None

                keys = ['search', 'date_created_from', 'date_created_until', 'date_due_from', 'date_due_until']
                for key in keys:
                    try:
                        del request.vars[key]
                    except KeyError:
                        pass

                # redirect to update page
                redirect(URL(vars=request.vars))

            form_search = self._list_invoices_get_form_search()
            content.append(form_search)

        form_groups = ''
        if group_filter_enabled:
            if 'invoices_groups_id' in request.vars:
                session.invoices_list_invoices_group = request.vars['invoices_groups_id']

                try:
                    del request.vars['invoices_groups_id']
                except KeyError:
                    pass

                # redirect to update page
                redirect(URL(vars=request.vars))

        # always add the grid
        content.append(grid)
        return content


    def _list_invoices_get_form_search(self):
        """
            Returns search form for invoices page
        """
        T = current.T
        session = current.session
        DATE_FORMAT = current.DATE_FORMAT

        form = SQLFORM.factory(
            Field('search',
                  default=session.invoices_list_invoices_search,
                  label=T('')),
            Field('date_created_from', 'date',
                  requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                                        minimum=datetime.date(1900, 1, 1),
                                                        maximum=datetime.date(2999, 1, 1))),
                  # ),
                  default=session.invoices_list_invoices_date_created_from),
            Field('date_created_until', 'date',
                  requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                                        minimum=datetime.date(1900, 1, 1),
                                                        maximum=datetime.date(2999, 1, 1))),
                  # ),
                  default=session.invoices_list_invoices_date_created_until),
            Field('date_due_from', 'date',
                  requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                                        minimum=datetime.date(1900, 1, 1),
                                                        maximum=datetime.date(2999, 1, 1))),
                  # ),
                  default=session.invoices_list_invoices_date_due_from),
            Field('date_due_until', 'date',
                  requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                                        minimum=datetime.date(1900, 1, 1),
                                                        maximum=datetime.date(2999, 1, 1))),
                  # ),
                  default=session.invoices_list_invoices_date_due_until),
            submit_button=T('Go')
        )

        search = form.element('#no_table_search')
        search['_class'] += ' margin-right'
        search['_placeholder'] = T("Invoice #")

        btn_clear = A(T("Clear"),
                      _href=URL('invoices', 'list_invoices_clear_search',
                                vars={'search_enabled': True}),
                      _title=T("Clear search"),
                      _class='btn btn-default')

        form = DIV(
            DIV(
                form.custom.begin,
                DIV(LABEL(T('Search')), BR(), form.custom.widget.search, _class='col-md-2'),
                DIV(DIV(DIV(LABEL(T('Date from')), BR(), form.custom.widget.date_created_from, _class='col-md-2'),
                        DIV(LABEL(T('Date until')), BR(), form.custom.widget.date_created_until, _class='col-md-2'),
                        DIV(LABEL(T('Due from')), BR(), form.custom.widget.date_due_from, _class='col-md-2'),
                        DIV(LABEL(T('Due until')), BR(), form.custom.widget.date_due_until, _class='col-md-2'),
                        DIV(LABEL(T('Filter')), BR(), form.custom.submit, btn_clear, _class='col-md-3'),
                        _class='row'),
                    _class='col-md-8'),
                form.custom.end,
                _class='row'),
        )

        return form

    def _list_invoices_get_status_query(self, query):
        """
            Returns status query
        """
        db = current.db
        session = current.session

        if session.invoices_list_status == 'draft':
            query &= (db.invoices.Status == 'draft')
        if session.invoices_list_status == 'sent':
            query &= (db.invoices.Status == 'sent')
        if session.invoices_list_status == 'paid':
            query &= (db.invoices.Status == 'paid')
        if session.invoices_list_status == 'cancelled':
            query &= (db.invoices.Status == 'cancelled')
        if session.invoices_list_status == 'overdue':
            query &= (db.invoices.Status == 'sent')
            query &= (db.invoices.DateDue < datetime.date.today())

        return query


    def _list_invoices_get_search_query(self, query):
        """
            Adds search for invoice number to query
        """
        db = current.db
        session = current.session

        if session.invoices_list_invoices_search:
            search = session.invoices_list_invoices_search.strip()
            query &= (db.invoices.InvoiceID.like('%' + search + '%'))

        if session.invoices_list_invoices_date_created_from:
            query &= (db.invoices.DateCreated >= session.invoices_list_invoices_date_created_from)

        if session.invoices_list_invoices_date_created_until:
            query &= (db.invoices.DateCreated <= session.invoices_list_invoices_date_created_until)

        if session.invoices_list_invoices_date_due_from:
            query &= (db.invoices.DateDue >= session.invoices_list_invoices_date_due_from)

        if session.invoices_list_invoices_date_due_until:
            query &= (db.invoices.DateDue <= session.invoices_list_invoices_date_due_until)

        return query


    def _list_invoices_get_groups_query(self, query):
        """
            Adds filter for invoice group to query
        """
        if session.invoices_list_invoices_group:
            query &= (db.invoices.invoices_groups_id == session.invoices_list_invoices_group)


    def _list_invoices_get_buttons(self, row):
        """
            Group all links for invoices into .btn-group
        """
        auth = current.auth
        os_gui = current.globalenv['os_gui']
        T = current.T

        iID = row.invoices.id
        modals = SPAN()
        links = DIV(_class='btn-group')
        buttons = SPAN(links, modals)

        if auth.has_membership(group_id='Admins') or \
                auth.has_permission('create', 'invoices_payments'):
            links.append(self._list_invoices_get_link_add_payment(iID))

            #result = self._list_invoices_get_link_add_payment(iID)
            #links.append(result['button'])
            #modals.append(result['modal'])

        if auth.has_membership(group_id='Admins') or \
                auth.has_permission('read', 'invoices'):
            pdf = os_gui.get_button('print',
                                    URL('invoices', 'pdf', vars={'iID': iID}))
            links.append(pdf)

        # if auth.has_membership(group_id='Admins') or \
        #    auth.has_permission('read', 'auth_user'):
        #     customer = os_gui.get_button('user',
        #         URL('customers', 'edit', args=row.invoices.auth_customer_id,
        #             extension=''))
        #     links.append(customer)

        if auth.has_membership(group_id='Admins') or \
                auth.has_permission('update', 'invoices'):
            edit = os_gui.get_button('edit',
                                     URL('invoices', 'edit', vars={'iID': iID}, extension=''),
                                     tooltip=T('Edit Invoice'))
            links.append(edit)


        # if auth.has_membership(group_id='Admins') or \
        #         auth.has_permission('create', 'invoices'):
        #     duplicate = os_gui.get_button('duplicate',
        #                              URL('invoices', 'duplicate', vars={'iID': iID}, extension=''),
        #                                   # title= T("Duplicate"),
        #                              tooltip=T('Duplicate Invoice'))
        #     links.append(duplicate)

        return buttons


    def _list_invoices_get_balance(self, row):
        """
            Retuns the balance for an invoice
        """
        from os_invoice import Invoice

        iID = row.invoices.id
        invoice = Invoice(iID)

        return invoice.get_balance(formatted=True)


    def _list_invoices_get_link_add_payment(self, iID):
        """
            Returns an button and modal to add a payment for an invoice
        """
        T = current.T
        os_gui = current.globalenv['os_gui']

        button = os_gui.get_button('credit-card',
                                   URL('invoices', 'payment_add', vars={'iID':iID}),
                                   tooltip=T('Add payment'))

        return button
