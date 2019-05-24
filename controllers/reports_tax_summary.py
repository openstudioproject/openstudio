# -*- coding: utf-8 -*-

# from general_helpers import datestr_to_python
# from general_helpers import get_label
# from general_helpers import get_submenu
# from general_helpers import get_months_list
# from general_helpers import get_last_day_month
# from general_helpers import get_classname
# from general_helpers import User_helpers
# from general_helpers import Memo_links
# from general_helpers import class_get_teachers
# from general_helpers import max_string_length
# from general_helpers import iso_to_gregorian
# from general_helpers import classes_get_status
# from general_helpers import set_form_id_and_get_submit_button
#
# from gluon.tools import prettydate
#
# from openstudio.os_classcards_helper import ClasscardsHelper
# from openstudio.os_class import Class
# from openstudio.os_class_schedule import ClassSchedule
# from openstudio.os_attendance_helper import AttendanceHelper
# from openstudio.os_reports import Reports
# from openstudio.os_invoice import Invoice
# from openstudio.os_invoices import Invoices
# from openstudio.os_school_subscription import SchoolSubscription
# from openstudio.os_customer_classcard import CustomerClasscard
#
# import datetime
# import operator
# import cStringIO
# import openpyxl


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('read', 'reports_tax_summary'))
def index():
    """
        Main page for reports tax summary controller
    """
    index_process_request_vars()
    form = index_get_form(TODAY_LOCAL.year, TODAY_LOCAL.month)

    show_current_month = A(
        T("Current month"),
        _href=URL('index_show_current_month'),
        _class='btn btn-default'
    )

    header_tools = SPAN(
        show_current_month
    )

    return dict(
        form=form['form'],
        content="content here :)",
        submit=form['submit'],
        header_tools=header_tools

    )


def index_process_request_vars(var=None):
    """
        This function takes the request.vars as a argument and
    """
    today = TODAY_LOCAL
    if 'year' in request.vars:
        year = int(request.vars['year'])
    elif not session.reports_tax_summary_index_year is None:
        year = session.reports_tax_summary_index_year
    else:
        year = today.year
    session.reports_tax_summary_index_year = year
    if 'month' in request.vars:
        month = int(request.vars['month'])
    elif not session.reports_tax_summary_index_month is None:
        month = session.reports_tax_summary_index_month
    else:
        month = today.month
    session.reports_tax_summary_index_month = month

    # if 'school_locations_id' in request.vars:
    #     slID = request.vars['school_locations_id']
    # elif not session.reports_tax_summary_index_school_locations_id is None:
    #     slID = session.reports_tax_summary_index_school_locations_id
    # else:
    #     slID = None
    # session.reports_tax_summary_index_school_locations_id = slID

    # session.reports_tax_summary_index = request.function


def index_get_form(year, month):
    """
    Get month chooser form for index
    """
    from general_helpers import get_months_list
    from general_helpers import set_form_id_and_get_submit_button

    months = get_months_list()

    form = SQLFORM.factory(
        Field('month',
              requires=IS_IN_SET(months, zero=None),
              default=month,
              label=T("Month")),
        Field('year', 'integer',
              default=year,
              label=T("Year")),
        # Field('school_locations_id', db.school_locations,
        #       requires=IS_IN_DB(db(loc_query),
        #                         'school_locations.id',
        #                         '%(Name)s',
        #                         zero=T("All locations")),
        #       default=session.reports_tax_summary_index_school_locations_id,
        #       represent=lambda value, row: locations_dict.get(value, T("No location")),
        #       label=T("Location")),
        formstyle='bootstrap3_stacked',
        submit_button=T("Run report")
    )

    return set_form_id_and_get_submit_button(form, 'MainForm')

# helpers start

def subscriptions_get_menu(page=None):
    pages = [
        (['subscriptions_overview', T('Subscriptions overview'), URL('reports',"subscriptions_overview")]),
        (['subscriptions_new', T('New subscriptions'), URL('reports',"subscriptions_new")]),
        (['subscriptions_stopped', T('Stopped subscriptions'), URL('reports',"subscriptions_stopped")]),
        (['subscriptions_paused', T('Paused subscriptions'), URL('reports',"subscriptions_paused")]),
        (['subscriptions_alt_prices', T('Alt. prices'), URL('reports',"subscriptions_alt_prices")]),
        ]

    horizontal = True
    if request.user_agent()['is_mobile']:
        horizontal = False

    return os_gui.get_submenu(pages,
                              page,
                              horizontal=horizontal,
                              htype='tabs')

