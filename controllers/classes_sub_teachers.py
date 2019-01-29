# -*- coding: utf-8 -*-


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'classes_otc_sub_avail'))
def index():
    """
    Page to accept and decline substitution requests
    :return:
    """
    from openstudio.os_classes_otc_sub_availables import ClassesOTCSubAvailables

    response.title = T("Available sub teachers")
    response.subtitle = T("")
    response.view = 'general/only_content.html'

    ## Pagination begin
    if 'page' in request.vars:
        try:
            page = int(request.vars['page'])
        except ValueError:
            page = 0
    else:
        page = 0
    items_per_page = 11
    limitby=(page*items_per_page,(page+1)*items_per_page+1)
    ## Pagination end

    if 'Status' in request.vars:
        session.classes_subs_manage_status = request.vars['Status']
    elif not session.classes_subs_manage_status:
        session.classes_subs_manage_status = 'pending'

    subs_avail = ClassesOTCSubAvailables()
    result = subs_avail.list_formatted(
        session.classes_subs_manage_status,
        limitby
    )
    table = result['table']
    rows = result['rows']

    form = subs_avail.get_form_filter_status(
        session.classes_subs_manage_status
    )

    ## Pager begin
    navigation = ''
    url_previous = ''
    url_next = ''
    if len(rows) > items_per_page or page:
        previous = SPAN(_class='fa fa-chevron-left grey')
        if page:
            url_previous = URL(request.function, vars={'page':page-1})
            previous = A(SPAN(_class='fa fa-chevron-left'),
                         _href=url_previous)

        nxt = SPAN(_class='fa fa-chevron-right grey')
        if len(rows) > items_per_page:
            url_next = URL(request.function, vars={'page':page+1})
            nxt = A(SPAN(_class='fa fa-chevron-right'),
                    _href=url_next)

        navigation = os_gui.get_page_navigation_simple(url_previous, url_next, page + 1, request.cid)


    return dict(content=DIV(form, table, navigation))


def sub_request_get_return_url(var=None):
    return URL('subs_manage')


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('update', 'classes_otc_sub_avail'))
def accept():
    cotcsaID = request.vars['cotcsaID']

    # Accept this offer
    row = db.classes_otc_sub_avail(cotcsaID)
    row.Accepted = True
    row.update_record()

    # Set teacher as sub
    cotc = db.classes_otc(row.classes_otc_id)
    cotc.auth_teacher_id = row.auth_teacher_id
    cotc.update_record()

    # Reject all others
    query = (db.classes_otc_sub_avail.classes_otc_id == row.classes_otc_id) & \
            (db.classes_otc_sub_avail.id != cotcsaID)
    db(query).update(Accepted = False)

    db.classes_otc[row.classes_otc_id] = dict(Status = None)

    redirect(sub_request_get_return_url())


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('update', 'classes_otc_sub_avail'))
def decline():
    cotcsaID = request.vars['cotcsaID']

    db.classes_otc_sub_avail[cotcsaID] = dict(Accepted = False)

    redirect(sub_request_get_return_url())