# -*- coding: utf-8 -*-

import datetime
from decimal import Decimal, ROUND_HALF_UP

from gluon import *


class Receipt:
    """
    Class that contains functions for a receipt
    """
    def __init__(self, rID):
        """
        Init function for an receipt
        """
        db = current.db

        self.receipts_id = rID
        self.row = db.receipts(rID)

        # New receipt?
        query = (db.receipts_amounts.receipts_id == self.receipts_id)
        if not db(query).count():
            self.on_create()


    def on_create(self):
        """
        functions to be called when creating an receipt
        """
        self._insert_amounts()


    def on_update(self):
        """
        functions to be called when updating an receipt or receipt items
        """
        pass


    def _set_updated_at(self):
        """
        Set db.receipts.Updated_at to current time (UTC)
        """
        self.row.Updated_at = datetime.datetime.now()
        self.row.update_record()


    def _insert_amounts(self):
        """
            Insert amounts row for receipt, without data
        """
        db = current.db
        db.receipts_amounts.insert(receipts_id = self.receipts_id)


    def set_amounts(self):
        """
            Set subtotal, vat and total incl vat
        """
        db = current.db
        # set sums
        sum_subtotal = db.receipts_items.TotalPrice.sum()
        sum_vat = db.receipts_items.VAT.sum()
        sum_totalvat = db.receipts_items.TotalPriceVAT.sum()

        # get info from db
        query = (db.receipts_items.receipts_id == self.receipts_id)
        rows = db(query).select(sum_subtotal,
                                sum_vat,
                                sum_totalvat)

        sums = rows.first()
        subtotal = sums[sum_subtotal]
        vat      = sums[sum_vat]
        total    = sums[sum_totalvat]

        if subtotal is None:
            subtotal = 0
        if vat is None:
            vat = 0
        if total is None:
            total = 0

        # check what to do
        amounts = db.receipts_amounts(receipts_id = self.receipts_id)
        if amounts:
            # update current row
            amounts.TotalPrice    = subtotal
            amounts.VAT           = vat
            amounts.TotalPriceVAT = total
            amounts.Paid          = total
            amounts.update_record()
        else:
            # insert new row
            db.receipts_amounts.insert(
                receipts_id   = self.receipts_id,
                TotalPrice    = subtotal,
                VAT           = vat,
                TotalPriceVAT = total,
                Paid          = paid,
                Balance       = balance)


        self.on_update()


    def get_amounts(self):
        """
            Get subtotal, vat and total incl vat
        """
        db = current.db

        amounts = db.receipts_amounts(receipts_id = self.receipts_id)

        return amounts


    def get_amounts_tax_rates(self, formatted=False):
        """
            Returns vat for each tax rate as list sorted by tax rate percentage
            format: [ [ Name, Amount ] ]
        """
        db = current.db
        iID = self.receipts_id
        CURRSYM = current.globalenv['CURRSYM']

        amounts_vat = []
        rows = db().select(db.tax_rates.id, db.tax_rates.Name,
                           orderby=db.tax_rates.Percentage)
        for row in rows:
            sum = db.receipts_items.VAT.sum()
            query = (db.receipts_items.receipts_id == iID) & \
                    (db.receipts_items.tax_rates_id == row.id)

            result = db(query).select(sum).first()

            if not result[sum] is None:
                if formatted:
                    amount = SPAN(CURRSYM, ' ', format(result[sum], '.2f'))
                else:
                    amount = result[sum]
                amounts_vat.append({'Name'   : row.Name,
                                    'Amount' : amount})

        return amounts_vat


    def get_studio_info(self):
        """
        :return: dict with studio info
        """
        ORGANIZATIONS = current.globalenv['ORGANIZATIONS']

        try:
            organization = ORGANIZATIONS[ORGANIZATIONS['default']]

            company_name = organization['Name']
            company_address = organization['Address']
            company_email = organization['Email'] or ''
            company_phone = organization['Phone'] or ''
            company_registration = organization['Registration'] or ''
            company_tax_registration = organization['TaxRegistration'] or ''
        except KeyError:
            company_name = ''
            company_address = ''
            company_email = ''
            company_phone = ''
            company_registration = ''
            company_tax_registration = ''

        return dict(
            name = company_name,
            address = company_address,
            email = company_email,
            phone = company_phone,
            registration = company_registration,
            tax_registration = company_tax_registration,
        )


    def get_item_next_sort_nr(self):
        """
            Returns the next item number for an receipt
            use to set sorting when adding an item
        """
        db = current.db
        query = (db.receipts_items.receipts_id == self.receipts_id)

        return db(query).count() + 1


    def get_receipt_items_rows(self):
        """
            :return: db.customers_orders_items rows for order
        """
        db = current.db

        query = (db.receipts_items.receipts_id == self.receipts_id)
        rows = db(query).select(db.receipts_items.ALL,
                                orderby=db.receipts_items.Sorting)

        return rows


    def get_payment_method(self):
        """
        :return: db.payment_methods_row for receipt
        """
        db = current.db

        if self.receipts.payment_methods_id:
            return db.payment_methods(self.receipt.payment_methods_id)
        else:
            return None
        
        
    def item_add_product_variant(self, pvID, quantity):
        """
        
        :return: 
        """
        db = current.db
        
        sorting = self.get_item_next_sort_nr()
        variant = db.shop_products_variants(pvID)
        product = db.shop_products(variant.shop_products_id)
        
        riID = db.receipts_items.insert(
            receipts_id = self.receipts_id,
            Sorting = sorting,
            ProductName = product.Name,
            Description = variant.Name,
            Quantity = quantity,
            Price = variant.Price,
            tax_rates_id = variant.tax_rates_id,
            accounting_glaccounts_id=product.accounting_glaccounts_id,
            accounting_costcenters_id=product.accounting_costcenters_id
        )

        self.set_amounts()

        return riID


    def item_add_from_invoice_item(self, item):
        """

        :param item: gluon.dal.row object of db.invoices_items
        :return:
        """
        db = current.db

        sorting = self.get_item_next_sort_nr()

        riID = db.receipts_items.insert(
            receipts_id=self.receipts_id,
            Sorting=sorting,
            ProductName=item.ProductName,
            Description=item.Description,
            Quantity=item.Quantity,
            Price=item.Price,
            tax_rates_id=item.tax_rates_id,
            accounting_glaccounts_id=item.accounting_glaccounts_id,
            accounting_costcenters_id=item.accounting_costcenters_id
        )

        self.set_amounts()


    def get_print_display(self):
        """
            Print friendly display of a receipt
        """
        from openstudio.os_sys_organization import SysOrganization

        get_sys_property = current.globalenv['get_sys_property']
        ORGANIZATIONS = current.globalenv['ORGANIZATIONS']

        response = current.response

        template = get_sys_property(
            'branding_default_template_receipts'
        ) or 'receipts/default.html' # Set default
        template_file = 'templates/' + template

        so = SysOrganization(ORGANIZATIONS['default'])
        organization = so.row

        html = response.render(template_file,
                               dict(organization=organization,
                                    receipt=self.row,
                                    receipt_info=self._get_print_display_receipt_info(),
                                    items=self._get_print_display_format_items(),
                                    logo=self._get_print_display_get_logo()))

        return html


    def _get_print_display_receipt_info(self):
        """
        :return:
        """
        T = current.T
        DATETIME_FORMAT = current.DATETIME_FORMAT

        header = THEAD(TR(
            TD(T("Helped by")),
            TD(T("Receipt")),
            TD(T("Time")),
        ))

        data = TR(
            TD(self.row.Created_by or ''),
            TD(self.row.id),
            TD(self.row.Created_at.strftime(DATETIME_FORMAT)),
        )

        table = TABLE(
            header,
            data
        )

        return table


    def _get_print_display_format_items(self):
        """
        :param items: gluon.dal.rows object of db.receipts_items
        :return: html table
        """
        from tools import OsTools

        T = current.T
        db = current.db
        os_tools = OsTools()
        currency = os_tools.get_sys_property('Currency')
        amounts_total = self.get_amounts()
        amounts_vat = self.get_amounts_tax_rates()

        items_header = THEAD(TR(
            TH(T("Product")),
            TH(T("Qty")),
            TH(T("Total"), _class="header-total"),
        ))
        table = TABLE(items_header)

        for item in self.get_receipt_items_rows():
            table.append(TR(
                TD(item.ProductName, BR(),
                   SPAN(item.Description, _class='item-description')),
                TD(item.Quantity),
                TD(format(item.TotalPriceVAT, ".2f"))
            ))

        items_footer = TFOOT()

        amounts = [[T('Total'), amounts_total.TotalPriceVAT]]

        for tax_rate in amounts_vat:
            amounts.append([tax_rate['Name'], tax_rate['Amount']])

        amounts.append([T('Sub total'), amounts_total.TotalPrice])

        for i, amount in enumerate(amounts):
            if i == 0:
                celltype = TH
            else:
                celltype = TD
            items_footer.append(TR(
            celltype(amount[0], _class='bold'),
            celltype(currency),
            celltype(SPAN(format(amount[1], '.2f'),
                    _class='bold pull-right')),
            )
        )

        # Payment method
        pm = db.payment_methods(self.row.payment_methods_id)

        items_footer.append(TR(
          TD(T("Payment method")),
          TD(pm.Name, _colspan="2")
        ))

        table.append(items_footer)

        return table


    def _get_print_display_get_logo(var=None):
        """
            Returns logo for template
        """
        import os

        request = current.request

        branding_logo = os.path.join(request.folder,
                                     'static',
                                     'plugin_os-branding',
                                     'logos',
                                     'branding_logo_receipts.png')
        if os.path.isfile(branding_logo):
            abs_url = URL('static', 'plugin_os-branding/logos/branding_logo_receipts.png',
                          scheme=True,
                          host=True)
            logo_img = IMG(_src=abs_url)
        else:
            logo_img = ''

        return logo_img


    #
    # def item_add_classcard(self, ccdID):
    #     """
    #         :param ccdID: Add customer classcard to receipt
    #         :return: None
    #     """
    #     from os_customer_classcard import CustomerClasscard
    #
    #     db = current.db
    #     T  = current.T
    #
    #     classcard = CustomerClasscard(ccdID)
    #
    #     # add item to receipt
    #     next_sort_nr = self.get_item_next_sort_nr()
    #     price = classcard.price
    #
    #     iiID = db.receipts_items.insert(
    #         receipts_id=self.receipts_id,
    #         ProductName=T("Class card"),
    #         Description=classcard.name.decode('utf-8') + u' (' + T("Class card") + u' ' + unicode(ccdID) + u')',
    #         Quantity=1,
    #         Price=price,
    #         Sorting=next_sort_nr,
    #         tax_rates_id=classcard.school_classcard.tax_rates_id,
    #         GLAccount=classcard.glaccount
    #     )
    #
    #     # This calls self.on_update()
    #     self.set_amounts()
    #
    #     return iiID
    #
    #