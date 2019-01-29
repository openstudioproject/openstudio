# -*- coding: utf-8 -*-


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'classes_open'))
def index():
    """
        List all open classes. Initially list 25, list 25 more each time
        more is clicked
    """
    from general_helpers import classes_get_status
    from general_helpers import max_string_length
    from general_helpers import class_get_teachers

    response.title = T('Open classes')
    response.subtitle = T('Sub teachers required')
    response.view = 'general/only_content.html'

    table = TABLE(
        THEAD(TR(TH(''), # status marker
                 TH(T('Date')),
                 TH(T('Location')),
                 TH(T('Class type')),
                 TH(T('Time')),
                 TH())),
              _class='table'
    )

    rows = index_get_rows(TODAY_LOCAL)

    for i, row in enumerate(rows):
        repr_row = list(rows[i:i + 1].render())[0]

        clsID = row.classes.id
        date = row.classes_otc.ClassDate
        date_formatted = repr_row.classes_otc.ClassDate
        result = classes_get_status(clsID, date)
        status = result['status']
        status_marker = TD(result['status_marker'],
                           _class='td_status_marker')

        location = max_string_length(repr_row.classes.school_locations_id, 15)
        classtype = max_string_length(repr_row.classes.school_classtypes_id, 24)
        time = SPAN(repr_row.classes.Starttime, ' - ', repr_row.classes.Endtime)
        teachers = class_get_teachers(clsID, date)

        vars = {'clsID':clsID,
                'date':date_formatted}

        reservations = A(T('Reservations'),
                         _href=URL('reservations', vars=vars))

        status = A(T('Status'), _href=URL('status', vars=vars))


        tools = DIV(_class='os-schedule_links')

        edit = ''
        if auth.has_membership(group_id='Admins') or \
            auth.has_permission('update', 'classes_otc'):
            edit = os_gui.get_button('edit',
                                     URL('classes', 'class_edit_on_date',
                                         vars={'clsID':clsID,
                                               'date' :date_formatted}),
                                     _class='pull-right')

        row_class = TR(status_marker,
                       TD(date),
                       TD(location),
                       TD(classtype),
                       TD(time),
                       TD(edit),
                       _class='os-schedule_class')


        table.append(row_class)

    return dict(content=table)


def index_get_rows(from_date):
    """
        Return rows for classes_open
    """
    fields = [
        db.classes_otc.id,
        db.classes_otc.ClassDate,
        db.classes_otc.Status,
        db.classes.id,
        db.classes.school_locations_id,
        db.classes.school_classtypes_id,
        db.classes.Starttime,
        db.classes.Endtime
    ]

    query = """
    SELECT cotc.id,
           cotc.ClassDate,
           cotc.Status,
           cla.id,
           CASE WHEN cotc.school_locations_id IS NOT NULL
                THEN cotc.school_locations_id
                ELSE cla.school_locations_id
                END AS school_locations_id,
           CASE WHEN cotc.school_classtypes_id IS NOT NULL
                THEN cotc.school_classtypes_id
                ELSE cla.school_classtypes_id
                END AS school_classtypes_id,
           CASE WHEN cotc.Starttime IS NOT NULL
                THEN cotc.Starttime
                ELSE cla.Starttime
                END AS Starttime,
           CASE WHEN cotc.Endtime IS NOT NULL
                THEN cotc.Endtime
                ELSE cla.Endtime
                END AS Endtime
    FROM classes_otc cotc
    LEFT JOIN classes cla on cla.id = cotc.classes_id
    WHERE cotc.ClassDate >= '{date}' AND cotc.Status = 'open'
    ORDER BY cotc.ClassDate, Starttime
    """.format(date=from_date)

    rows = db.executesql(query, fields=fields)

    return rows



@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'classes_otc_sub_avail'))
def available():
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


def available_get_return_url(var=None):
    return URL('available')


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('update', 'classes_otc_sub_avail'))
def available_accept():
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
def available():
    cotcsaID = request.vars['cotcsaID']

    db.classes_otc_sub_avail[cotcsaID] = dict(Accepted = False)

    redirect(sub_request_get_return_url())

