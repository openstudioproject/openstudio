# -*- coding: utf-8 -*-

from general_helpers import max_string_length
from general_helpers import datestr_to_python
from general_helpers import set_form_id_and_get_submit_button

from openstudio.os_order import Order
from openstudio.os_invoice import Invoice
from openstudio.os_invoices import Invoices
from openstudio.os_customer import Customer


from decimal import Decimal, ROUND_HALF_UP

import io
import weasyprint
import openpyxl


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'customers_orders'))
def index():
    """
        Lists all orders
    """
    response.title = T('Shop')
    response.subtitle = T('Orders')
    response.view = 'general/only_content.html'

    session.customers_back = 'finance_orders'
    session.orders_edit_back = 'finance_orders'

    db.customers_orders.auth_customer_id.readable = True
    db.customers_orders.CustomerNote.readable = False
    db.invoices.id.readable=False

    query = (db.customers_orders.id > 0)

    fields = [
        db.customers_orders.id,
        db.customers_orders.auth_customer_id,
        db.customers_orders.DateCreated,
        db.customers_orders.Origin,
        db.customers_orders_amounts.TotalPriceVAT,
        db.customers_orders.Status,
        db.customers_orders.CustomerNote,
        db.invoices.id,
        db.invoices.InvoiceID,
        db.invoices.Status
    ]

    db.customers_orders.auth_customer_id.represent = lambda row, value: A(row.display_name,
                                                                          _href=URL('customers', 'edit', args=[row.id]))


    links = [
        index_get_link_deliver,
        index_get_link_note,
        lambda row: os_gui.get_button(
            'edit',
            URL('orders', 'edit', vars={'coID': row.customers_orders.id}),
            btn_size='',
            tooltip=T('View order'))
    ]

    left = [ db.customers_orders_amounts.on(db.customers_orders_amounts.customers_orders_id == db.customers_orders.id),
             db.invoices_customers_orders.on(db.invoices_customers_orders.customers_orders_id == db.customers_orders.id),
             db.invoices.on(db.invoices_customers_orders.invoices_id == db.invoices.id)]

    headers = {'customers_orders.id': T("Order #"),
               'customers_orders.DateCreated': T("Time")}

    delete_permission = auth.has_membership(group_id='Admins') or \
                        auth.has_permission('delete', 'customers_orders')

    grid = SQLFORM.grid(query,
        links=links,
        left=left,
        fields=fields,
        headers=headers,
        create=False,
        editable=False,
        details=False,
        searchable=False,
        deletable=delete_permission,
        csv=False,
        #maxtextlengths=maxtextlengths,
        orderby=~db.customers_orders.id,
        field_id=db.customers_orders.id,
        ui = grid_ui)
    grid.element('.web2py_counter', replace=None) # remove the counter
    grid.elements('span[title=Delete]', replace=None) # remove text from delete button


    return dict(content=grid,
                header_tools='')


def index_get_link_note(row):
    """
    Return a model + button in case a customer added a note
    """
    if row.customers_orders.CustomerNote:
        modal_content = SPAN(
            T("The customer added the following message to this order:"), BR(), BR(),
            XML(row.customers_orders.CustomerNote.replace('\n', "<br>"))
        )
        modal_class = "order_message_" + str(row.customers_orders.id)
        button_class = 'btn btn-default btn-sm'

        result = os_gui.get_modal(
            button_text = XML("<i class='fa fa-comment-o'></i>"),
            button_class = button_class,
            modal_title = T("Message for order #") + str(row.customers_orders.id),
            modal_content = modal_content,
            modal_class = modal_class
        )

        return SPAN(
            result['button'],
            result['modal']
        )

    else:
        return None



def index_get_link_deliver(row):
    """
        Return deliver link for index list of orders
    """
    link = ''
    if row.customers_orders.Status == 'awaiting_payment':
        confirm_msg = T("Are you sure you want to deliver this order?")
        onclick = "return confirm('" + confirm_msg + "');"

        link = A(os_gui.get_fa_icon('fa-cube'), ' ', T("Deliver"),
                 _href=URL('orders', 'deliver', vars={'coID':row.customers_orders.id}),
                 _title=T("Deliver order and create invoice for customer"),
                 _onclick=onclick)

    return link


@auth.requires(auth.has_membership(group_id='Admins') or \
                auth.has_permission('read', 'customers_orders'))
def edit():
    """
        :return: shows order
    """
    response.title = T('Order #') + request.vars['coID']
    response.subtitle = T('Edit')
    response.view = 'general/only_content.html'

    coID = request.vars['coID']

    order = Order(coID)
    cuID = order.order.auth_customer_id
    customer = Customer(cuID)
    # Info table
    info = TABLE(THEAD(TR(TH(T('Customer')),
                          TH(T('Ordered on')),
                          TH(T('Status')),
                          )),
                 _class='table')

    # Display status
    for field in db.customers_orders:
        field.readable = False
        field.writable = False

    db.customers_orders.Status.readable = True
    db.customers_orders.Status.writable = True

    crud.messages.record_updated = T('Saved')
    form = crud.update(db.customers_orders, coID)

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']

    form = DIV(XML('<form id="MainForm" action="#" enctype="multipart/form-data" method="post">'),
               form.custom.widget.Status,
               form.custom.end)

    #status = form

    # status = represent_customers_orders_status(order.order.Status, order.order)
    # Display ordered on
    ordered_on = represent_datetime(order.order.DateCreated, order.order)
    customer_link = A(customer.get_name(),
                      _href=URL('customers', 'edit', args=customer.row.id))
    info.append(TR(
        TD(customer_link),
        TD(ordered_on),
        TD(form)
    ))

    # Info content
    content = DIV(DIV(info, _class='col-md-8 no-padding-left'))

    # Display items
    rows = order.get_order_items_rows()

    header = THEAD(TR(TH(T('Product')),
                      TH(T('Description')),
                      TH(SPAN(T('Amount incl. VAT'), _class='right')),
                      TH(T("G/L Account")),
                      TH(T("Cost center")),
                      TH(),
                        )
                     )
    table = TABLE(header, _class='table table-striped table-hover order-items')


    for i, row in enumerate(rows):
        repr_row = list(rows[i:i + 1].render())[0]

        table.append(TR(
            TD(repr_row.customers_orders_items.ProductName),
            TD(repr_row.customers_orders_items.Description),
            TD(SPAN(repr_row.customers_orders_items.TotalPriceVAT, _class='right')),
            TD(repr_row.customers_orders_items.accounting_glaccounts_id),
            TD(repr_row.customers_orders_items.accounting_costcenters_id),
            TD(),
        ))

    # Display totals
    amounts = order.get_amounts()

    footer = TFOOT(TR(TD(),
                    TD(B(T('Subtotal'))),
                    TD(SPAN(CURRSYM, ' ', format(amounts.TotalPrice, '.2f'), _class='bold right')),
                    TD()
                    ),
                  TR(TD(),
                    TD(B(T('VAT'))),
                    TD(SPAN(CURRSYM, ' ', format(amounts.VAT, '.2f'), _class='bold right')),
                    TD()
                    ),
                  TR(TD(),
                    TD(B(T('Total'))),
                    TD(SPAN(CURRSYM, ' ', format(amounts.TotalPriceVAT, '.2f'), _class='bold right')),
                    TD()
                    ))
    table.append(footer)

    content.append(table)

    # Customer message
    customer_message = ''
    if order.order.CustomerNote:
        customer_message = DIV(
            B(T('Customer message')), BR(), BR(),
            XML(order.order.CustomerNote.replace("\n", "<br>")),
        )
    content.append(customer_message)

    back = os_gui.get_button('back', edit_get_return_url(cuID))

    return dict(content=content, back=back, save=submit)


def edit_get_return_url(cuID):
    """
        Returns back url for customers orders
    """
    url = URL('orders', 'index')

    if session.orders_edit_back == 'customers_orders':
        return URL('customers', 'orders', vars={'cuID':cuID})

    return url


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('update', 'customers_orders'))
def deliver():
    """
        Deliver selected order
    """
    coID = request.vars['coID']

    order = Order(coID)
    order.deliver()

    session.flash = SPAN(T('Delivered order '),
                         A('#', coID,
                           _href=URL('orders', 'edit', vars={'coID':coID})))

    redirect(URL('orders', 'index'))