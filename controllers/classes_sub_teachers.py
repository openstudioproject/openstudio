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

    response.title = T('Classes')
    response.subtitle = T('Sub teachers')
    response.view = 'general/only_content.html'

    table = TABLE(
        THEAD(TR(TH(T('Status')),
                 TH(T('Date')),
                 TH(T('Time')),
                 TH(T('Location')),
                 TH(T('Class type')),
                 TH(T('Offers')),
                 TH(T('Sub teacher')),
                 TH())),
              _class='table'
    )

    rows = index_get_rows(TODAY_LOCAL)

    for i, row in enumerate(rows):
        repr_row = list(rows[i:i + 1].render())[0]

        clsID = row.classes.id
        date = row.classes_otc.ClassDate
        date_formatted = repr_row.classes_otc.ClassDate
        # result = classes_get_status(clsID, date)
        # status = result['status']
        # status_marker = TD(result['status_marker'],
        #                    _class='td_status_marker')

        status_label = os_gui.get_label(
            'danger', T("Sub requested")
        )
        if row.classes_otc.auth_teacher_id:
            status_label = os_gui.get_label(
                'success', T("Sub found")
            )

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
                _href=URL('offers', vars={'cotcID':row.classes_otc.id})
            )


        row_class = TR(
            TD(status_label),
            TD(date),
            TD(time),
            TD(location),
            TD(classtype),
            TD(available),
            TD(repr_row.classes_otc.auth_teacher_id),
            TD(edit),
            _class='os-schedule_class'
        )


        table.append(row_class)

    return dict(content=table)


def index_get_rows(date_from):
    """
        Return rows for classes_open
    """
    from openstudio.os_classes_otcs import ClassesOTCs

    cotcs = ClassesOTCs()
    rows = cotcs.get_sub_teacher_rows(date_from)

    return rows


@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'classes_otc_sub_avail'))
def offers():
    """
    Page to accept and decline substitution requests
    :return:
    """
    from openstudio.os_class import Class
    from openstudio.os_classes_otc_sub_availables import ClassesOTCSubAvailables

    cotcID = request.vars['cotcID']
    cotc = db.classes_otc(cotcID)
    cls = Class(cotc.classes_id, cotc.ClassDate)

    response.title = T("Sub offers")
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
    return URL('offers', vars={'cotcID': cotcID})


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

