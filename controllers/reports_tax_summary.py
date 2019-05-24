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


def index():
    """
        Main page for reports tax summary controller
    """
    return dict(
        form="form",
        content="content here :)"
    )


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

