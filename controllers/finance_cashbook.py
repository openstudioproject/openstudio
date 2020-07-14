# -*- coding: utf-8 -*-
from decimal import Decimal

@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'accounting_cashbooks'))
def index():
    """

    :return:
    """
    response.title = T('Cash book')

    session.finance_expenses_add_edit_back = 'finance_cashbook_index'

    if 'jump_date' in request.vars:
        # Set date
        redirect(URL('set_date', vars={ "date": request.vars['jump_date'] }))
    elif session.finance_cashbook_date:
        date = session.finance_cashbook_date
    else:
        date = TODAY_LOCAL
        session.finance_cashbook_date = date

    response.subtitle = SPAN(
        T("Daily summary"), ': ',
        date.strftime(DATE_FORMAT)
    )
    response.view = 'general/only_content_no_box.html'

    debit = get_debit(date)
    debit_total = debit['total']

    credit = get_credit(date)
    credit_total = credit['total']

    balance = index_get_balance(debit_total, credit_total)

    content = DIV(
        balance,
        debit['column_content'],
        credit['column_content'],
        _class='row'
    )

    header_tools = DIV(
        index_get_form_jump(),
        get_day_chooser(date)
    )

    return dict(
        content=content,
        header_tools=header_tools
    )


def index_get_form_jump():
    """
        Returns a form to jump to a date
    """
    jump_date = session.finance_cashbook_date
    form_jump = SQLFORM.factory(
                Field('jump_date', 'date',
                      requires=IS_DATE_IN_RANGE(
                                format=DATE_FORMAT,
                                minimum=datetime.date(1900,1,1),
                                maximum=datetime.date(2999,1,1)),
                      default=jump_date,
                      label=T(""),
                      widget=os_datepicker_widget_small),
                submit_button=T('Go'),
                )

    submit_jump = form_jump.element('input[type=submit]')
    submit_jump['_class'] = 'full-width'

    form_jump = DIV(form_jump.custom.begin,
                    DIV(form_jump.custom.widget.jump_date,
                        DIV(form_jump.custom.submit,
                            _class='input-group-btn'),
                        _class='input-group'),
                    form_jump.custom.end,
                    _class='form_inline',
                    _id='cashbook_form_jump_date')

    return form_jump


def get_debit(date):
    """
    Populate the credit column
    :param date: datetime.date
    :return: dict['total'] & dict['column_content']
    """
    total = 0

    # Cash count opening balance
    count_opening = cash_count_get(date, 'opening')
    total += count_opening['total'] or 0

    # Additional items
    # additional_items = additional_items_get(date, 'debit')
    # total += additional_items['total']

    # Class balance (total revenue - teacher payments)
    classes_balance = get_debit_classes(date, 'balance')
    total += classes_balance['total'] or 0

    # Sold memberships
    sold_memberships = get_debit_memberships(date)
    total += sold_memberships['total'] or 0

    # Sold subscriptions
    sold_subscriptions = get_debit_subscriptions(date)
    total += sold_subscriptions['total'] or 0

    # Sold cards
    sold_cards = get_debit_classcards(date)
    total += sold_cards['total'] or 0

    # Sold drop-in using mollie
    sold_dropin_using_mollie = get_debit_mollie_dropin(date)
    total += sold_dropin_using_mollie.get(total, 0)

    # Sold products
    sold_products = get_debit_sales_summary(date)
    total += Decimal(sold_products['total'] or 0)

    # Sold custom products
    sold_custom_products = get_debit_sales_summary_custom(date)
    total += Decimal(sold_custom_products['total'] or 0)

    # Class teacher payments
    teacher_payments = get_debit_classes(date, 'teacher_payments')
    total += teacher_payments['total'] or 0


    column = DIV(
        H4(T("Income")),
        count_opening['box'],
        # additional_items['box'],
        classes_balance['box'],
        sold_memberships['box'],
        sold_subscriptions['box'],
        sold_cards['box'],
        sold_dropin_using_mollie.get('box', ""),
        sold_products['box'],
        sold_custom_products['box'],
        teacher_payments['box'],
        _class=' col-md-6'

    )

    return dict(
        total = total,
        column_content = column
    )


def get_credit(date):
    """
    Populate the credit column
    :param date: datetime.date
    :return: dict['total'] & dict['column_content']
    """
    total = 0

    # Cash count closing balance
    count_closing = cash_count_get(date, 'closing')
    total += count_closing['total']

    # Additional items
    expenses = get_credit_expenses(date)
    total += expenses['total']

    # Classes used on subscriptions
    subscriptions_used_classes = get_credit_subscriptions_classes_summary(date)
    total += subscriptions_used_classes['total']

    # Classes used on cards
    cards_used_classes = get_credit_classcards_used_classes_summary(date)
    total += cards_used_classes['total']

    # Mollie drop-in classes taken
    mollie_used_classes = get_credit_mollie_dropin_used_classes_summary(date)
    total += mollie_used_classes['total']

    # Non-cash payments
    non_cash_payments = get_credit_shop_sales_not_paid_with_cash(date)
    total += non_cash_payments['total']

    column = DIV(
        H4(T("Expenses")),
        count_closing['box'],
        expenses['box'],
        subscriptions_used_classes['box'],
        cards_used_classes['box'],
        mollie_used_classes['box'],
        non_cash_payments['box'],
        _class=' col-md-6'
    )

    return dict(
        total = total,
        column_content = column
    )


# def additional_items_get(date, booking_type):
#     """
#
#     :param date:
#     :return: dict
#     """
#     from openstudio.os_accounting_cashbooks_additional_items import AccountingCashbooksAdditionalItems
#
#     acai = AccountingCashbooksAdditionalItems()
#     result = acai.list_formatted(date, date, booking_type)
#     acai_debit_list = result['table']
#     acai_debit_total = result['total']
#
#     if booking_type == 'debit':
#         box_class = 'box-success'
#     elif booking_type == 'credit':
#         box_class = 'box-danger'
#
#     link_add = ''
#     if auth.has_membership(group_id='Admins') or \
#        auth.has_permission('create', 'accounting_cashbooks_additional_items'):
#         link_add = SPAN(
#             SPAN(XML(" &bull; "), _class='text-muted'),
#             A(T("Add item"),
#               _href=URL('additional_item_add', vars={'booking_type': booking_type}))
#         )
#
#
#     additional_items = DIV(
#         DIV(H3("Additional items", _class='box-title'),
#             link_add,
#             DIV(
#                 A(I(_class='fa fa-minus'),
#                   _href='#',
#                   _class='btn btn-box-tool',
#                   _title=T("Collapse"),
#                   **{'_data-widget': 'collapse'}),
#                 _class='box-tools pull-right'
#             ),
#             _class='box-header'),
#         DIV(acai_debit_list, _class='box-body no-padding'),
#         _class='box ' + box_class
#     )
#
#     return dict(
#         box = additional_items,
#         total = acai_debit_total
#     )


def index_get_balance(debit_total=0, credit_total=0):
    """

    :return:
    """
    balance = debit_total - credit_total
    balance_class = ''
    if balance < 0:
        balance_class = 'text-red bold'

    box = DIV(DIV(
        DIV(
            H3(T("Summary"), _class='box-title'),
            _class='box-header'
        ),
        DIV(DIV(DIV(DIV(H5(T("Income"), _class='description-header'),
                        SPAN(represent_decimal_as_amount(debit_total), _class='description-text'),
                        _class='description-block'),
                    _class='col-md-4 border-right'),
                DIV(DIV(H5(T("Expenses"), _class='description-header'),
                        SPAN(represent_decimal_as_amount(credit_total), _class='description-text'),
                        _class='description-block'),
                    _class='col-md-4 border-right'),
                DIV(DIV(H5(T("Balance"), _class='description-header'),
                        SPAN(represent_decimal_as_amount(balance), _class='description-text ' + balance_class),
                        _class='description-block'),
                    _class='col-md-4'),
                _class='row'),
            _class='box-footer'
        ),
        _class='box box-primary'
    ), _class='col-md-12')

    return box


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'accounting_cashbooks'))
def set_date():
    """
    Set date for cashbook
    :return:
    """
    from general_helpers import datestr_to_python

    date_formatted = request.vars['date']
    date = datestr_to_python(DATE_FORMAT, request.vars['date'])

    session.finance_cashbook_date = date

    redirect(URL('index'))


def get_day_chooser(date):
    """
    Set day for cashbook
    :param date: datetime.date
    :return: HTML prev/next buttons
    """
    yesterday = (date - datetime.timedelta(days=1)).strftime(DATE_FORMAT)
    tomorrow = (date + datetime.timedelta(days=1)).strftime(DATE_FORMAT)

    link = 'set_date'
    url_prev = URL(link, vars={'date': yesterday})
    url_next = URL(link, vars={'date': tomorrow})
    url_today = URL(link, vars={'date': TODAY_LOCAL.strftime(DATE_FORMAT)})

    today = ''
    if date != TODAY_LOCAL:
        today = A(os_gui.get_fa_icon('fa fa-calendar-o'), ' ', T("Today"),
                 _href=url_today,
                 _class='btn btn-default')

    previous = A(I(_class='fa fa-angle-left'),
                 _href=url_prev,
                 _class='btn btn-default')
    nxt = A(I(_class='fa fa-angle-right'),
            _href=url_next,
            _class='btn btn-default')

    return DIV(previous, today, nxt, _class='btn-group pull-right')


def index_return_url(var=None):
    return URL('index')


@auth.requires_login()
def cash_count_add():
    """
    Set opening balance
    """
    from openstudio.os_forms import OsForms

    count_type = request.vars['count_type']
    date = session.finance_cashbook_date

    if count_type == 'opening':
        count_type = T("opening")
    elif count_type == 'closing':
        count_type = T("closing")

    response.title = T('Cash book')
    response.subtitle = SPAN(
        T("Daily summary"), ': ',
        date.strftime(DATE_FORMAT), ' - ',
        T("Set %s count") % count_type

    )
    response.view = 'general/only_content.html'

    return_url = index_return_url()

    db.accounting_cashbooks_cash_count.CountDate.default = date
    db.accounting_cashbooks_cash_count.CountType.default = count_type

    os_forms = OsForms()
    result = os_forms.get_crud_form_create(
        db.accounting_cashbooks_cash_count,
        return_url,
        message_record_created=T("Saved")
    )

    form = result['form']
    back = os_gui.get_button('back', return_url)

    content = form

    return dict(content=content,
                save=result['submit'],
                back=back)


@auth.requires_login()
def cash_count_edit():
    """
    Set opening balance
    """
    from openstudio.os_forms import OsForms

    ccID = request.vars['ccID']

    date = session.finance_cashbook_date
    cc = db.accounting_cashbooks_cash_count(ccID)
    if cc.CountType == 'opening':
        count_type = T("opening")
    elif cc.CountType == 'closing':
        count_type = T("closing")

    response.title = T('Cash book')
    response.subtitle = SPAN(
        T("Daily summary"), ': ',
        date.strftime(DATE_FORMAT), ' - ',
        T("Edit %s count") % count_type

    )
    response.view = 'general/only_content.html'

    return_url = index_return_url()

    os_forms = OsForms()
    result = os_forms.get_crud_form_update(
        db.accounting_cashbooks_cash_count,
        return_url,
        ccID,
        message_record_updated=T("Saved"),
    )

    form = result['form']
    back = os_gui.get_button('back', return_url)

    content = form

    return dict(content=content,
                save=result['submit'],
                back=back)


@auth.requires_login()
def additional_item_add():
    """
    Set opening balance
    """
    from openstudio.os_forms import OsForms

    date = session.finance_cashbook_date
    db.accounting_cashbooks_additional_items.BookingDate.default = date

    booking_type = request.vars['booking_type']
    if booking_type == 'credit':
        db.accounting_cashbooks_additional_items.BookingType.default = 'credit'
        subtitle_type = T("Income")
    elif booking_type == 'debit':
        db.accounting_cashbooks_additional_items.BookingType.default = 'debit'
        subtitle_type = T("Expense")

    response.title = T('Cash book')
    response.subtitle = SPAN(
        T("Daily summary"), ': ',
        date.strftime(DATE_FORMAT), ' - ',
        T("Add %s item") % subtitle_type
    )
    response.view = 'general/only_content.html'

    return_url = index_return_url()


    os_forms = OsForms()
    result = os_forms.get_crud_form_create(
        db.accounting_cashbooks_additional_items,
        return_url,
        message_record_created=T("Saved")
    )

    form = result['form']
    back = os_gui.get_button('back', return_url)

    content = form

    return dict(content=content,
                save=result['submit'],
                back=back)


@auth.requires_login()
def additional_item_edit():
    """
    Set opening balance
    """
    from openstudio.os_forms import OsForms

    acaiID = request.vars['acaiID']

    date = session.finance_cashbook_date

    item = db.accounting_cashbooks_additional_items(acaiID)

    booking_type = item.BookingType
    if booking_type == 'credit':
        subtitle_type = T("Income")
    elif booking_type == 'debit':
        subtitle_type = T("Expense")

    response.title = T('Cash book')
    response.subtitle = SPAN(
        T("Daily summary"), ': ',
        date.strftime(DATE_FORMAT), ' - ',
        T("Edit %s item") % subtitle_type

    )
    response.view = 'general/only_content.html'

    return_url = index_return_url()

    os_forms = OsForms()
    result = os_forms.get_crud_form_update(
        db.accounting_cashbooks_additional_items,
        return_url,
        acaiID,
        message_record_updated=T("Saved"),
    )

    form = result['form']
    back = os_gui.get_button('back', return_url)

    content = form

    return dict(content=content,
                save=result['submit'],
                back=back)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('delete', 'accounting_cashbooks_additional_items'))
def additional_item_delete():
    """
    Delete cashbook item
    :return:
    """
    acaiID = request.vars['acaiID']

    query = (db.accounting_cashbooks_additional_items.id == acaiID)
    db(query).delete()

    redirect(index_return_url())


def cash_count_get(date, count_type):
    """

    :param date: datetime.date
    :param count_type: 'opening' or 'closing'
    :return:
    """
    from general_helpers import max_string_length

    if count_type == 'opening':
        box_class = 'box-success'
        box_title = T("Opening cash count")
        msg_not_set = T("Opening balance not set")
    elif count_type == 'closing':
        box_class = 'box-danger'
        box_title = T("Closing cash count")
        msg_not_set = T("closing balance not set")

    row = db.accounting_cashbooks_cash_count(
        CountDate = session.finance_cashbook_date,
        CountType = count_type
    )
    if row:
        total = row.Amount
        au = db.auth_user(row.auth_user_id)
        header = THEAD(TR(
            TH(T("Set by")),
            TH(T("Amount")),
        ))

        box_body = DIV(
            TABLE(
                header,
                TR(TD(A(au.display_name,
                        _href=URL('customers', 'edit', args=[au.id]))),
                   TH(represent_decimal_as_amount(total))),
                _class='table table-striped table-hover'
                ),
        _class='box-body no-padding')

        note = ""
        if row.Note:
            note = XML(row.Note.replace('\n', '<br>'))

        box_footer = DIV(
            note,
            _class='box-footer text-muted'
        )
    else:
        total = 0
        box_body = DIV(msg_not_set, _class='box-body')
        box_footer = ''


    link = ''
    link_vars = {'count_type': count_type}
    if not row:
        permission = auth.has_membership(group_id='Admins') or \
                     auth.has_permission('create', 'accounting_cashbooks_cash_count')
        link_url = 'cash_count_add'
    else:
        permission = auth.has_membership(group_id='Admins') or \
                     auth.has_permission('update', 'accounting_cashbooks_cash_count')
        link_url = 'cash_count_edit'
        link_vars['ccID'] = row.id

    if permission:
        link = SPAN(
            SPAN(XML(" &bull; "), _class='text-muted'),
            A(T("Set balance"),
              _href=URL(link_url, vars=link_vars))
        )

    box = DIV(
        DIV(H3(box_title, _class='box-title'),
            link,
            DIV(A(I(_class='fa fa-minus'),
                _href='#',
                _class='btn btn-box-tool',
                _title=T("Collapse"),
                **{'_data-widget': 'collapse'}),
                _class='box-tools pull-right'),
            _class='box-header'),
        box_body,
        box_footer,
        _class='box ' + box_class,
    )

    return dict(
        box = box,
        total = total
    )


def get_debit_classes(date, list_type='balance'):
    """
    return a box and total of class profit or class revenue
    :param list_type: one of 'revenue' or 'teacher_payments'
    :param date: datetime.date
    :return:
    """
    from general_helpers import max_string_length
    from openstudio.os_reports import Reports

    reports = Reports()
    revenue = reports.get_classes_revenue_summary_day(session.finance_cashbook_date)

    if list_type == 'balance':
        total = revenue['balance']
        box_title = T("Class balance")
    elif list_type == 'teacher_payments':
        total = revenue['teacher_payments']
        box_title = T("Teacher payments")

    header = THEAD(TR(
        TH(T("Time")),
        TH(T("Location")),
        TH(T("Classtype")),
        TH(T("Attendance")),
        TH(T("Amount")),
    ))

    table = TABLE(header, _class='table table-striped table-hover')
    for cls in revenue['data']:
        class_vars = {"clsID": cls["ClassesID"], "date": date.strftime(DATE_FORMAT)}
        
        if list_type == 'balance':
            amount = represent_decimal_as_amount(cls['Balance'])
        elif list_type == 'teacher_payments':
            amount = A(
                represent_decimal_as_amount(cls['TeacherPayment']),
                _href=URL("classes", "revenue",
                          vars=class_vars),
                _target="_blank"
            )

        teachers = cls['Teachers']
        if not 'teacher' in teachers or cls['Teachers']['error']:
            teacher = T("No teacher")
        else:
            sub = T(" (sub)") if teachers['teacher_sub'] else ""
            teacher = teachers['teacher'].display_name + sub

        tr = TR(
            TD(cls['Starttime']),
            TD(max_string_length(cls['Location'], 18)),
            TD(max_string_length(cls['ClassType'], 18), BR(),
               SPAN(max_string_length(teacher, 28),
                    _class="text-muted text_small"),
                    _title=teacher
               ),
            TD(A(cls['CountAttendance'],
                 _href=URL("classes", "attendance", vars=class_vars),
                 _target="_blank")),
            TD(amount)
        )

        table.append(tr)

    # Footer total
    table.append(TFOOT(TR(
        TH(),
        TH(),
        TH(),
        TH(T('Total')),
        TH(represent_decimal_as_amount(total))
    )))

    box = DIV(
        DIV(H3(box_title, _class='box-title'),
            DIV(A(I(_class='fa fa-minus'),
                _href='#',
                _class='btn btn-box-tool',
                _title=T("Collapse"),
                **{'_data-widget': 'collapse'}),
                _class='box-tools pull-right'),
            _class='box-header'),
        DIV(table, _class='box-body no-padding'),
        _class='box box-success',
    )

    return dict(
        box = box,
        total = total
    )


def get_debit_mollie_dropin(date):
    """

    :param date: datetime.date
    :return:
    """
    from openstudio.os_reports import Reports

    reports = Reports()

    total = 0
    count = db.invoices_payments.Amount.count()
    rows = reports.get_day_mollie_dropin_classes_sold_summary_day(date)

    header = THEAD(TR(
        TH(T("# Sold")),
        TH(T("Price")),
        TH(T("Total")),
    ))

    table = TABLE(header, _class='table table-striped table-hover')
    for row in rows:
        nr_sold = row[count]
        row_total = row.invoices_payments.Amount * nr_sold

        table.append(TR(
            TD(nr_sold),
            TD(represent_decimal_as_amount(row.invoices_payments.Amount)),
            TD(represent_decimal_as_amount(row_total))
        ))

        total += row_total

    # cards sold footer
    table.append(TFOOT(TR(
        TH(),
        TH(T("Total")),
        TH(represent_decimal_as_amount(total))
    )))

    box = DIV(
        DIV(H3(T("Drop-in classes bought with Mollie"), _class='box-title'),
            DIV(A(I(_class='fa fa-minus'),
                _href='#',
                _class='btn btn-box-tool',
                _title=T("Collapse"),
                **{'_data-widget': 'collapse'}),
                _class='box-tools pull-right'),
            _class='box-header'),
        DIV(table, _class='box-body no-padding'),
        _class='box box-success',
    )

    return dict(
        box = box,
        total = total
    )


def get_debit_classcards(date):
    """

    :param date: datetime.date
    :return:
    """
    from openstudio.os_reports import Reports

    reports = Reports()

    total = 0
    count = db.school_classcards.id.count()
    rows = reports.classcards_sold_summary_rows(date, date)

    header = THEAD(TR(
        TH(T("Card")),
        TH(T("# Sold")),
        TH(T("Price")),
        TH(T("Total")),
    ))

    table = TABLE(header, _class='table table-striped table-hover')
    for row in rows:
        cards_sold = row[count]
        row_total = row.school_classcards.Price * cards_sold

        table.append(TR(
            TD(row.school_classcards.Name),
            TD(cards_sold),
            TD(represent_decimal_as_amount(row.school_classcards.Price)),
            TD(represent_decimal_as_amount(row_total))
        ))

        total += row_total

    # cards sold footer
    table.append(TFOOT(TR(
        TH(),
        TH(),
        TH(T("Total")),
        TH(represent_decimal_as_amount(total))
    )))

    box = DIV(
        DIV(H3(T("Cards"), _class='box-title'),
            DIV(A(I(_class='fa fa-minus'),
                _href='#',
                _class='btn btn-box-tool',
                _title=T("Collapse"),
                **{'_data-widget': 'collapse'}),
                _class='box-tools pull-right'),
            _class='box-header'),
        DIV(table, _class='box-body no-padding'),
        _class='box box-success',
    )

    return dict(
        box = box,
        total = total
    )


def get_debit_subscriptions(date):
    """

    :param date: datetime.date
    :return:
    """
    from general_helpers import max_string_length
    from openstudio.os_reports import Reports

    reports = Reports()

    total = 0
    rows = reports.subscriptions_sold_on_date_summary_rows(date)

    header = THEAD(TR(
        TH(T("Subscription")),
        TH(T("# Sold")),
        TH(T("Price")),
        TH(T("Total")),
    ))

    table = TABLE(header, _class='table table-striped table-hover')
    for row in rows:
        subscriptions_sold = row.school_subscriptions.CountSold or 0
        row_total = (row.invoices_items.TotalPriceVAT or 0) * subscriptions_sold

        table.append(TR(
            TD(max_string_length(row.school_subscriptions.Name, 40)),
            TD(subscriptions_sold),
            TD(represent_decimal_as_amount(row.invoices_items.TotalPriceVAT)),
            TD(represent_decimal_as_amount(row_total))
        ))

        total += row_total

    # cards sold footer
    table.append(TFOOT(TR(
        TH(),
        TH(),
        TH(T("Total")),
        TH(represent_decimal_as_amount(total))
    )))

    box = DIV(
        DIV(H3(T("Subscriptions"), _class='box-title'),
            DIV(A(I(_class='fa fa-minus'),
                _href='#',
                _class='btn btn-box-tool',
                _title=T("Collapse"),
                **{'_data-widget': 'collapse'}),
                _class='box-tools pull-right'),
            _class='box-header'),
        DIV(table, _class='box-body no-padding'),
        _class='box box-success',
    )

    return dict(
        box = box,
        total = total
    )


def get_debit_memberships(date):
    """

    :param date: datetime.date
    :return:
    """
    from openstudio.os_reports import Reports

    reports = Reports()

    total = 0
    count = db.school_memberships.id.count()
    rows = reports.memberships_sold_summary_rows(date, date)

    header = THEAD(TR(
        TH(T("Membership")),
        TH(T("# Sold")),
        TH(T("Price")),
        TH(T("Total")),
    ))

    table = TABLE(header, _class='table table-striped table-hover')
    for row in rows:
        cards_sold = row[count]
        row_total = row.school_memberships.Price * cards_sold

        table.append(TR(
            TD(row.school_memberships.Name),
            TD(cards_sold),
            TD(represent_decimal_as_amount(row.school_memberships.Price)),
            TD(represent_decimal_as_amount(row_total))
        ))

        total += row_total

    # cards sold footer
    table.append(TFOOT(TR(
        TH(),
        TH(),
        TH(T("Total")),
        TH(represent_decimal_as_amount(total))
    )))

    box = DIV(
        DIV(H3(T("Memberships"), _class='box-title'),
            DIV(A(I(_class='fa fa-minus'),
                _href='#',
                _class='btn btn-box-tool',
                _title=T("Collapse"),
                **{'_data-widget': 'collapse'}),
                _class='box-tools pull-right'),
            _class='box-header'),
        DIV(table, _class='box-body no-padding'),
        _class='box box-success',
    )

    return dict(
        box = box,
        total = total
    )


def get_debit_sales_summary(date):
    """

    :param date: datetime.date
    :return:
    """
    from general_helpers import max_string_length
    from openstudio.os_reports import Reports

    reports = Reports()

    total = 0
    records = reports.shop_sales_summary(date, date)

    header = THEAD(TR(
        TH(T("G/L Account")),
        TH(T("Total")),
    ))

    table = TABLE(header, _class='table table-striped table-hover')
    for record in records:

        table.append(TR(
            TD(record[1]),
            TD(represent_float_as_amount(record[0])),
        ))

        total += record[0]

    # cards sold footer
    table.append(TFOOT(TR(
        TH(T("Total")),
        TH(represent_float_as_amount(total))
    )))

    box = DIV(
        DIV(H3(T("Shop sales by G/L Account"), _class='box-title'),
            DIV(A(I(_class='fa fa-minus'),
                _href='#',
                _class='btn btn-box-tool',
                _title=T("Collapse"),
                **{'_data-widget': 'collapse'}),
                _class='box-tools pull-right'),
            _class='box-header'),
        DIV(table, _class='box-body no-padding'),
        _class='box box-success',
    )

    return dict(
        box = box,
        total = total
    )


def get_debit_sales_summary_custom(date):
    """

    :param date: datetime.date
    :return:
    """
    from general_helpers import max_string_length
    from openstudio.os_reports import Reports

    reports = Reports()

    total = 0
    rows = reports.shop_sales_custom(date, date)

    header = THEAD(TR(
        TH(T("Item")),
        TH(T("Description")),
        TH(T("Total")),
    ))

    table = TABLE(header, _class='table table-striped table-hover')
    for row in rows:
        table.append(TR(
            TD(row.ProductName),
            TD(max_string_length(row.Description, 40),
               _title=row.Description),
            TD(represent_decimal_as_amount(row.TotalPriceVAT)),
        ))

        total += row.TotalPriceVAT

    # cards sold footer
    table.append(TFOOT(TR(
        TH(T("Total")),
        TH(),
        TH(represent_decimal_as_amount(total))
    )))

    box = DIV(
        DIV(H3(T("Shop sales - custom items"), _class='box-title'),
            DIV(A(I(_class='fa fa-minus'),
                _href='#',
                _class='btn btn-box-tool',
                _title=T("Collapse"),
                **{'_data-widget': 'collapse'}),
                _class='box-tools pull-right'),
            _class='box-header'),
        DIV(table, _class='box-body no-padding'),
        _class='box box-success',
    )

    return dict(
        box = box,
        total = total
    )


def get_credit_mollie_dropin_used_classes_summary(date):
    """

    :param date: datetime.date
    :return:
    """
    from general_helpers import max_string_length
    from openstudio.os_reports import Reports

    reports = Reports()

    total = 0
    count = db.invoices_payments.Amount.count()
    rows = reports.get_day_mollie_dropin_classes_taken_summary_day(date)

    header = THEAD(TR(
        TH(T("Classes taken")),
        TH(T("Class amount")),
        TH(T("Total")),
    ))

    table = TABLE(header, _class='table table-striped table-hover')

    for row in rows:
        classes_taken = row[count]
        row_total = row.invoices_payments.Amount * classes_taken

        table.append(TR(
            TD(classes_taken),
            TD(represent_decimal_as_amount(row.invoices_payments.Amount)),
            TD(represent_decimal_as_amount(row_total))
        ))

        total += row_total

    # cards sold footer
    table.append(TFOOT(TR(
        TH(),
        TH(T("Total")),
        TH(represent_decimal_as_amount(total))
    )))

    box = DIV(
        DIV(H3(T("Drop-in classes taken (bought with Mollie)"), _class='box-title'),
            DIV(A(I(_class='fa fa-minus'),
                _href='#',
                _class='btn btn-box-tool',
                _title=T("Collapse"),
                **{'_data-widget': 'collapse'}),
                _class='box-tools pull-right'),
            _class='box-header'),
        DIV(table, _class='box-body no-padding'),
        _class='box box-danger',
    )

    return dict(
        box = box,
        total = total
    )

def get_credit_classcards_used_classes_summary(date):
    """

    :param date: datetime.date
    :return:
    """
    from general_helpers import max_string_length
    from openstudio.os_reports import Reports

    reports = Reports()

    total = 0
    count = db.school_classcards.id.count()
    rows = reports.classes_attendance_classcards_quickstats_summary(date, date)

    header = THEAD(TR(
        TH(T("Card")),
        TH(T("Classes taken")),
        TH(T("Class amount")),
        TH(T("Total")),
    ))

    table = TABLE(header, _class='table table-striped table-hover')

    for row in rows:
        classes_taken = row[count]
        if not row.school_classcards.Unlimited:
            import decimal
            try:
                class_price = row.school_classcards.Price / row.school_classcards.Classes
            except decimal.DivisionByZero:
                class_price = 0
        else:
            class_price = row.school_classcards.QuickStatsAmount or 0
        row_total = class_price * classes_taken

        table.append(TR(
            TD(max_string_length(row.school_classcards.Name, 46)),
            TD(classes_taken),
            TD(represent_decimal_as_amount(class_price)),
            TD(represent_decimal_as_amount(row_total))
        ))

        total += row_total

    # cards sold footer
    table.append(TFOOT(TR(
        TH(),
        TH(),
        TH(T("Total")),
        TH(represent_decimal_as_amount(total))
    )))

    box = DIV(
        DIV(H3(T("Classes taken using cards"), _class='box-title'),
            DIV(A(I(_class='fa fa-minus'),
                _href='#',
                _class='btn btn-box-tool',
                _title=T("Collapse"),
                **{'_data-widget': 'collapse'}),
                _class='box-tools pull-right'),
            _class='box-header'),
        DIV(table, _class='box-body no-padding'),
        _class='box box-danger',
    )

    return dict(
        box = box,
        total = total
    )


def get_credit_expenses(date):
    """

    :param date:
    :return: dict
    """
    from openstudio.os_accounting_expenses import AccountingExpenses

    ae = AccountingExpenses()
    result = ae.list_formatted_simple(date, date)
    table = result['table']
    total = result['total']

    link_add = ''
    if auth.has_membership(group_id='Admins') or \
       auth.has_permission('create', 'accounting_expenses'):
        link_add = SPAN(
            SPAN(XML(" &bull; "), _class='text-muted'),
            A(T("Add expense"),
              _href=URL('finance_expenses', 'add'))
        )


    expenses = DIV(
        DIV(H3("Additional expenses", _class='box-title'),
            link_add,
            DIV(
                A(I(_class='fa fa-minus'),
                  _href='#',
                  _class='btn btn-box-tool',
                  _title=T("Collapse"),
                  **{'_data-widget': 'collapse'}),
                _class='box-tools pull-right'
            ),
            _class='box-header'),
        DIV(table, _class='box-body no-padding'),
        _class='box box-danger'
    )

    return dict(
        box = expenses,
        total = total
    )


def get_credit_subscriptions_classes_summary(date):
    """

    :param date: datetime.date
    :return:
    """
    from general_helpers import max_string_length
    from openstudio.os_reports import Reports

    reports = Reports()

    total = 0
    count = db.school_subscriptions.id.count()
    rows = reports.classes_attendance_subscriptions_quickstats_summary(date, date)

    header = THEAD(TR(
        TH(T("Subscription")),
        TH(T("Classes")),
        TH(T("Class amount")),
        TH(T("Total")),
    ))

    table = TABLE(header, _class='table table-striped table-hover')
    for row in rows:
        classes_taken = row[count]
        class_price = row.school_subscriptions.QuickStatsAmount or 0
        row_total = class_price * classes_taken

        table.append(TR(
            TD(max_string_length(row.school_subscriptions.Name, 46)),
            TD(classes_taken),
            TD(represent_decimal_as_amount(class_price)),
            TD(represent_decimal_as_amount(row_total))
        ))

        total += row_total

    # cards sold footer
    table.append(TFOOT(TR(
        TH(),
        TH(),
        TH(T("Total")),
        TH(represent_decimal_as_amount(total))
    )))

    box = DIV(
        DIV(H3(T("Classes taken using subscriptions"), _class='box-title'),
            DIV(A(I(_class='fa fa-minus'),
                _href='#',
                _class='btn btn-box-tool',
                _title=T("Collapse"),
                **{'_data-widget': 'collapse'}),
                _class='box-tools pull-right'),
            _class='box-header'),
        DIV(table, _class='box-body no-padding'),
        _class='box box-danger',
    )

    return dict(
        box = box,
        total = total
    )


def get_credit_shop_sales_not_paid_with_cash(date):
    """

    :param date: datetime.date
    :return:
    """
    from general_helpers import max_string_length
    from openstudio.os_reports import Reports

    reports = Reports()

    total = 0

    # non cash payments from receipts
    rows = reports.shop_sales_not_paid_with_cash_summary(date, date)
    sum = db.receipts_amounts.TotalPriceVAT.sum()
    # online mollie payments from invoice_payments
    amount_paid_using_mollie = reports.shop_sales_mollie_summary(date, date)

    header = THEAD(TR(
        TH(T("Payment method")),
        TH(T("Amount")),
    ))

    table = TABLE(header, _class='table table-striped table-hover')
    table.append(TR(
        TD(T("Mollie (online shop)")),
        TD(represent_decimal_as_amount(amount_paid_using_mollie)),
    ))

    for row in rows:
        amount = row[sum]
        total += amount

        table.append(TR(
            TD(row.payment_methods.Name),
            TD(represent_decimal_as_amount(amount)),
        ))

    table.append(TFOOT(TR(
        TH(T("Total")),
        TH(represent_decimal_as_amount(total)),
    )))

    box = DIV(
        DIV(H3(T("Non cash sales payments"), _class='box-title'),
            DIV(A(I(_class='fa fa-minus'),
                _href='#',
                _class='btn btn-box-tool',
                _title=T("Collapse"),
                **{'_data-widget': 'collapse'}),
                _class='box-tools pull-right'),
            _class='box-header'),
        DIV(table, _class='box-body no-padding'),
        _class='box box-danger',
    )

    return dict(
        box = box,
        total = total
    )

