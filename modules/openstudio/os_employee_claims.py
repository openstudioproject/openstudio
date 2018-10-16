# -*- coding: utf-8 -*-

import datetime

from gluon import *


class EmployeeClaims:
    """
        Class that gathers useful functions for db.employee_claims
    """
    def get_rows(self,
                 status='pending',
                 sorting='time',
                 formatted=False,
                 all=False,
                 items_per_page = 100,
                 page = 0):

        db = current.db

        limitby = None
        if not all:
            limitby = (page * items_per_page, (page + 1) * items_per_page + 1)

        if sorting == 'time':
            orderby = ~db.employee_claims.ClaimDate
        elif sorting == 'employee':
            orderby = db.employee_claims.auth_user_id

        query = (db.employee_claims.Status == status)

        rows = db(query).select(
            orderby=orderby,
            limitby=limitby
        )

        if not formatted:
            return rows
        else:
            return self.rows_to_table(rows, status, items_per_page, page)


    def rows_to_table(self, rows, status, items_per_page, page):
        """
        turn rows object into an html table
        :param rows: gluon.dal.rows with all fields of db.teachers_payment_classes
        and db.classes
        :return: html table
        """
        import uuid
        from os_gui import OsGui

        T = current.T
        auth = current.auth
        os_gui = OsGui()

        header = THEAD(TR(
            TH('Claim #'),
            TH(T("Employee")),
            TH(T("Date")),
            TH(T("Description")),
            TH(T("Amount")),
            TH(T("Quantity")),
            TH(T("Attachment")),
            # TH(T("Attendance")),
            # TH(T("Payment")),
            # TH(os_gui.get_fa_icon('fa-subway')),
            TH() # Actions
        ))

        table = TABLE(header, _class="table table-striped table-hover small_font")

        permissions = auth.has_membership(group_id='Admins') or \
               auth.has_permission('update', 'employee_claims')

        for i, row in enumerate(rows):
            repr_row = list(rows[i:i + 1].render())[0]
            buttons=''
            if permissions:

                if status == 'pending':
                    buttons = self._rows_to_table_get_pending_buttons(row, os_gui)
                elif status == 'accepted':
                    buttons = self._rows_to_table_get_accepted_buttons(row, os_gui)
                elif status == 'rejected':
                    buttons = self._rows_to_table_get_rejected_buttons(row, os_gui)
            tr = TR(
                TD(row.id),
                TD(repr_row.auth_user_id),
                TD(repr_row.ClaimDate),
                TD(repr_row.Description),
                TD(repr_row.Amount),
                TD(repr_row.Quantity),
                TD(self._rows_to_table_get_attachment(row, os_gui, uuid)),
                TD(buttons)
            )

            table.append(tr)

        pager = self._rows_to_table_get_navigation(rows, items_per_page, page)

        return DIV(table, pager)


    def _rows_to_table_get_attachment(self, row, os_gui, uuid):
        """
        Display claim attachments in a modal
        """
        if not row.Attachment:
            return ''

        T = current.T

        attachment_url = URL('default', 'download', row.Attachment)
        modal_class = str(uuid.uuid4())

        modal_content = DIV(
            IMG(_src=attachment_url),
            _class='ec_modal_attachment_content'
        )

        title = T('Attachment for claim #{id}'.format(id=row.id))

        footer_content = os_gui.get_button(
            'download',
            attachment_url,
            btn_size='',
            title=T("Download")
        )

        result = os_gui.get_modal(
            button_text=T('View'),
            button_class='btn-sm',
            button_title=title,
            modal_title=title,
            modal_content=modal_content,
            modal_footer_content=footer_content,
            modal_class=modal_class,
            modal_size='lg'
        )

        return SPAN(
            result['button'],
            result['modal']
        )


    def _rows_to_table_get_navigation(self, rows, items_per_page, page):
        from os_gui import OsGui

        os_gui = OsGui()
        request = current.request

        # Navigation
        previous = ''
        url_previous = None
        if page:
            url_previous = URL(args=[page - 1], vars=request.vars)
            previous = A(SPAN(_class='glyphicon glyphicon-chevron-left'),
                         _href=url_previous)

        nxt = ''
        url_next = None
        if len(rows) > items_per_page:
            url_next = URL(args=[page + 1], vars=request.vars)
            nxt = A(SPAN(_class='glyphicon glyphicon-chevron-right'),
                    _href=url_next)

        navigation = os_gui.get_page_navigation_simple(url_previous, url_next, page + 1)

        if previous or nxt:
            pass
        else:
            navigation = ''

        return DIV(navigation)



    def _rows_to_table_get_pending_buttons(self, row, os_gui):
        """
            Returns buttons for schedule
            - one button group for edit & attendance buttons
            - separate button for delete
        """
        T = current.T
        # DATE_FORMAT = current.DATE_FORMAT
        # buttons = DIV(_class='pull-right')


        links = []
        links.append(['header', T('Actions')])

        links.append(A(os_gui.get_fa_icon('fa-check'), T("Accept"),
                       _href=URL( 'employee_claims_accept',
                                 vars={'ecID': row.id}),
                       _class='text-green'
                       ))
        links.append('divider')

        links.append(A(os_gui.get_fa_icon('fa-ban'), T("Reject"),
                       _href=URL('employee_claims_reject',
                                 vars={'ecID': row.id}),
                       _class='text-red',
                       ))


        ec_menu = os_gui.get_dropdown_menu(
            links=links,
            btn_text=T('Actions'),
            btn_size='btn-sm',
            btn_icon='actions',
            menu_class='btn-group pull-right')

        return DIV(ec_menu, _class='pull-right')


    def _rows_to_table_get_accepted_buttons(self, row, os_gui):
        """
            Returns buttons for schedule
            - one button group for edit & attendance buttons
            - separate button for delete
        """
        T = current.T
        DATE_FORMAT = current.DATE_FORMAT
        buttons = DIV(_class='pull-right')


        links = []
        links.append(['header', T('Actions')])

        links.append(A(os_gui.get_fa_icon('fa-ban'), T("Reject"),
                       _href=URL( 'employee_claims_reject',
                                 vars={'ecID': row.id}),
                       _class='text-red'))
        links.append('divider')

        links.append(A(os_gui.get_fa_icon('fa-hourglass-2'), T("Pending"),
                       _href=URL('employee_claims_pending',
                                 vars={'ecID': row.id}),
                       _class=''))


        ec_menu = os_gui.get_dropdown_menu(
            links=links,
            btn_text=T('Actions'),
            btn_size='btn-sm',
            btn_icon='actions',
            menu_class='btn-group pull-right')

        return DIV(ec_menu, _class='pull-right')


    def _rows_to_table_get_rejected_buttons(self, row, os_gui):
        """
            Returns buttons for schedule
            - one button group for edit & attendance buttons
            - separate button for delete
        """
        T = current.T
        DATE_FORMAT = current.DATE_FORMAT
        buttons = DIV(_class='pull-right')


        links = []
        links.append(['header', T('Actions')])

        links.append(A(os_gui.get_fa_icon('fa-check'), T("Accept"),
                       _href=URL( 'employee_claims_accept',
                                 vars={'ecID': row.id}),
                       _class='text-green'))
        links.append('divider')

        links.append(A(os_gui.get_fa_icon('fa-hourglass-2'), T("Pending"),
                       _href=URL('employee_claims_pending',
                                 vars={'ecID': row.id}),
                       _class=''))


        ec_menu = os_gui.get_dropdown_menu(
            links=links,
            btn_text=T('Actions'),
            btn_size='btn-sm',
            btn_icon='actions',
            menu_class='btn-group pull-right')

        return DIV(ec_menu, _class='pull-right')


    def get_pending(self, page=0, formatted=False):
        """
        All classes not
        :return: gluon.dal.rows or html table
        """
        return self.get_rows(
            status='pending',
            formatted=formatted,
            page=page
        )


    def get_accepted(self, page=0, formatted=False):
        """
        All classes verified
        :return: gluon.dal.rows or html table
        """
        return self.get_rows(
            status='accepted',
            formatted=formatted,
            page=page
        )


    def get_rejected(self, page=0, formatted=False):
        """
        All processed classes
        :param formatted: Bool
        :return: gluon.dal.rows or html table
        """
        return self.get_rows(
            status='rejected',
            formatted=formatted,
            page=page
        )


    def get_processed(self, page=0, formatted=False):
        """
        All processed classes
        :param formatted: Bool
        :return: gluon.dal.rows or html table
        """
        return self.get_rows(
            status='processed',
            formatted=formatted,
            page=page
        )


    def accept_all(self):
        """
        Change status of all not_verified classes to verified
        :return: Int - number of classes where status has been changed to verified
        """
        db = current.db
        auth = current.auth

        query = (db.employee_claims.Status == 'pending')
        updated = db(query).update(
            Status = 'accepted',
            VerifiedBy = auth.user.id,
            VerifiedOn = datetime.datetime.now()
        )

        return updated


    def process_accepted(self):
        """
        Create credit invoices for verified classes
        :return:
        """
        from os_invoice import Invoice
        from os_employee_claim import EmployeeClaim

        T = current.T
        db = current.db

        # Sort verified classes by employee
        rows = self.get_rows(
            status='accepted',
            sorting='employee',
            formatted=False,
            all=True
        )

        print rows

        # previous_teacher = None
        # current_teacher = None
        processed = 0
        invoices_created = 0
        # For each employee, create credit invoice and add all accepted claims
        for i, row in enumerate(rows):
            epID = row.auth_user_id
            if i == 0 or not previous_employee == epID:
                current_employee = epID

                igpt = db.invoices_groups_product_types(ProductType='employee_claims')
                iID = db.invoices.insert(
                    invoices_groups_id=igpt.invoices_groups_id,
                    EmployeeClaim=True,
                    Description=T('Claims'),
                    Status='sent'
                )

                invoice = Invoice(iID)
                invoice.link_to_customer(epID)

                invoices_created += 1

            ecID = row.id
            invoice.item_add_employee_claim_credit_payment(ecID)


            # Set status processed
            ec = EmployeeClaim(ecID)
            ec.set_status_processed()

            previous_employee = current_employee
            processed += 1

        # Calculate total

        return processed

