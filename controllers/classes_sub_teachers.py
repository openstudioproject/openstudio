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
                 TH(T('Time')),
                 TH(T('Class type')),
                 TH(T('# Teachers available')),
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

        available = ''
        if auth.has_membership(group_id='Admins') or \
           auth.has_permission('read', 'classes_otc_sub_avail'):
            available = A(
                row.classes_otc.CountSubsAvailable,
                _href=URL('available', vars={'cotcID':row.classes_otc.id})
            )


        row_class = TR(status_marker,
                       TD(date),
                       TD(location),
                       TD(time),
                       TD(classtype),
                       TD(available),
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
        db.classes_otc.CountSubsAvailable,
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
           COUNT(cotcsa.classes_otc_id),
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
    LEFT JOIN classes_otc_sub_avail cotcsa on cotcsa.classes_otc_id = cotc.id
    WHERE cotc.ClassDate >= '{date}' AND cotc.Status = 'open'
    GROUP BY cotc.id
    ORDER BY cotc.ClassDate, Starttime
    """.format(date=from_date)

    rows = db.executesql(query, fields=fields)

    print db._lastsql[0]

    return rows



@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'classes_otc_sub_avail'))
def available():
    """
    Page to accept and decline substitution requests
    :return:
    """
    from openstudio.os_class import Class
    from openstudio.os_classes_otc_sub_availables import ClassesOTCSubAvailables

    cotcID = request.vars['cotcID']
    cotc = db.classes_otc(cotcID)
    cls = Class(cotc.classes_id, cotc.ClassDate)

    response.title = T("Available sub teachers")
    response.subtitle = cls.get_name()
    response.view = 'general/only_content.html'

    subs_avail = ClassesOTCSubAvailables()
    table = subs_avail.list_formatted(cotcID)

    back = os_gui.get_button(
        'back',
        URL('index')
    )

    return dict(
        content=table,
        back=back
    )


def available_get_return_url(cotcID):
    return URL('available', vars={'cotcID': cotcID})


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('update', 'classes_otc_sub_avail'))
def sub_teacher_accept():
    """
    Accept teachers' offer to sub class
    :return:
    """
    from openstudio.os_classes_otc_sub_available import ClassesOTCSubAvailable

    cotcsaID = request.vars['cotcsaID']

    cotcsa = ClassesOTCSubAvailable(cotcsaID)
    cotcsa.accept()

    session.flash = T("Accepted teacher")

    row = db.classes_otc_sub_avail(cotcsaID)
    redirect(available_get_return_url(row.classes_otc_id))


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('update', 'classes_otc_sub_avail'))
def sub_teacher_decline():
    """
    Decline teachers' offer to sub this class
    :return:
    """
    from openstudio.os_classes_otc_sub_available import ClassesOTCSubAvailable

    cotcsaID = request.vars['cotcsaID']

    cotcsa = ClassesOTCSubAvailable(cotcsaID)
    cotcsa.decline()

    session.flash = T("Declined teacher")

    row = db.classes_otc_sub_avail(cotcsaID)
    redirect(available_get_return_url(row.classes_otc_id))

