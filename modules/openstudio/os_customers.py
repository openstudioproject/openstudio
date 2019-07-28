# -*- coding: utf-8 -*-

import datetime

from gluon import *


class Customers:
    """
        This clas sontains functions for multiple customers
    """

    def list_activity_after_date(self, date):
        """
            :param: date: datetime.date
            :return: List of all records in auth_user with activity
        """
        db = current.db
        query = """
SELECT au.id, 
	   au.first_name, 
       au.last_name,
       au.display_name, 
       au.email, 
       au.last_login, 
       au.created_on, 
       cs.count_cs,
       ccd.count_ccd,
       wsp.count_event_tickets,
       cn.count_notes,
       clatt.count_classes,
       co.count_orders,
       ic.count_invoices
FROM auth_user au
LEFT JOIN ( SELECT auth_customer_id, COUNT(id) as count_cs
		    FROM customers_subscriptions
		    WHERE Enddate > '{date}' OR Enddate IS NULL
			GROUP BY auth_customer_id ) AS cs ON cs.auth_customer_id = au.id
LEFT JOIN ( SELECT auth_customer_id, COUNT(id) AS count_ccd
		    FROM customers_classcards
		    WHERE Enddate > '{date}' OR Enddate IS NULL 
            GROUP BY auth_customer_id ) AS ccd ON ccd.auth_customer_id = au.id
LEFT JOIN ( SELECT auth_customer_id, COUNT(id) AS count_event_tickets
			FROM workshops_products_customers
			WHERE CreatedOn > '{date}'
            GROUP BY auth_customer_id) AS wsp ON wsp.auth_customer_id = au.id
LEFT JOIN ( SELECT auth_customer_id, COUNT(id) AS count_notes
			FROM customers_notes
			WHERE NoteDate > '{date}'
            GROUP BY auth_customer_id) AS cn ON cn.auth_customer_id = au.id
LEFT JOIN ( SELECT auth_customer_id, COUNT(id) AS count_classes 
			FROM classes_attendance
			WHERE ClassDate > '{date}'
			GROUP BY auth_customer_id) clatt ON clatt.auth_customer_id = au.id
LEFT JOIN ( SELECT auth_customer_id, COUNT(ID) as count_orders
			FROM customers_orders
            WHERE DateCreated > '{date}'
            GROUP BY auth_customer_id) co ON co.auth_customer_id = au.id
LEFT JOIN ( SELECT ic.auth_customer_id, COUNT(ic.id) as count_invoices
			FROM invoices_customers ic
            LEFT JOIN invoices ON ic.invoices_id = invoices.id
            WHERE invoices.DateCreated > '{date}'
            GROUP BY ic.auth_customer_id) ic ON ic.auth_customer_id = au.id
WHERE (au.last_login < '{date}' OR au.last_login IS NULL) AND
      au.created_on < '{date}' AND
      au.employee = 'F' AND 
      au.teacher = 'F' AND
      au.id > 1
        """.format(date=date)

        return db.executesql(query)

    def list_inactive_after_date(self, date):
        """
        :param date: datetime.date
        :return: list of customers inactive after date
        """
        from general_helpers import datestr_to_python

        records = self.list_activity_after_date(date)

        inactive = []
        for record in records:
            last_login = record[5].date() if record[5] else None
            created_on = record[6].date()

            if (created_on < date and
                    (last_login is None or last_login < date) and
                    (record[7] is None and
                     record[8] is None and
                     record[9] is None and
                     record[10] is None and
                     record[11] is None and
                     record[12] is None and
                     record[13] is None
                    )):
                inactive.append(record)

        return inactive

    def delete_inactive_after_date(self, date):
        """
        :param date: datetime.date
        :return: Integer - count of customers deleted
        """
        db = current.db

        records = self.list_inactive_after_date(date)
        ids = [record[0] for record in records]

        query = (db.auth_user.id.belongs(ids))
        db(query).delete()

        return len(records)

    def list_inactive_after_date_formatted(self, date):
        """
            :param date: datetime.date
            :return: dict(table=Table listing inactive customers,
                          count=number of inactive customers)
        """
        T = current.T
        DATE_FORMAT = current.DATE_FORMAT

        records = self.list_inactive_after_date(date)

        header = THEAD(TR(
            TH(T("ID")),
            TH(T("Customer")),
            TH(T("Email")),
            TH(T("Last Login")),
            TH(T("Created")),
            TH(T("Subscriptions")),
            TH(T("Classcards")),
            TH(T("Events")),
            TH(T("Notes")),
            TH(T("Classes")),
            TH(T("Orders")),
            TH(T("Invoices")),
        ))

        table = TABLE(header, _class="table table-striped table-hover small_font")
        for record in records:
            cuID = record[0]
            last_login = record[5]
            try:
                record[5].strftime(DATE_FORMAT)
            except AttributeError:
                last_login = 'None'

            customer_link = A(
                record[3],
                _href=URL('customers', 'edit', args=record[0]),
                _target="_blank"
            )

            table.append(TR(
                TD(cuID),
                TD(customer_link),
                TD(record[4]),
                TD(last_login),
                TD(record[6].strftime(DATE_FORMAT)),
                TD(record[7]),
                TD(record[8]),
                TD(record[9]),
                TD(record[10]),
                TD(record[11]),
                TD(record[12]),
                TD(record[13]),
            ))

        return dict(table=table, count=len(records))

    def classes_add_get_form_date(self, cuID, date):
        """
            Get date form
        """
        T = current.T
        DATE_FORMAT = current.DATE_FORMAT
        os_datepicker_widget = current.globalenv['os_datepicker_widget']

        form = SQLFORM.factory(
            Field('date', 'date',
                  requires=IS_DATE_IN_RANGE(format=DATE_FORMAT,
                                            minimum=datetime.date(1900, 1, 1),
                                            maximum=datetime.date(2999, 1, 1)),
                  default=date,
                  widget=os_datepicker_widget),
            separator='',
            submit_button=T('Go'))

        input_date = form.element('#no_table_date')
        # input_date.attributes['_onchange'] = "this.form.submit();"

        submit = form.element('input[type=submit]')

        delta = datetime.timedelta(days=1)
        date_prev = (date - delta).strftime(DATE_FORMAT)
        date_next = (date + delta).strftime(DATE_FORMAT)

        url_prev = URL(vars={'cuID': cuID,
                             'teID': cuID,
                             'date': date_prev})
        url_next = URL(vars={'cuID': cuID,
                             'teID': cuID,
                             'date': date_next})

        previous = A(I(_class='fa fa-angle-left'),
                     _href=url_prev,
                     _class='btn btn-default')
        nxt = A(I(_class='fa fa-angle-right'),
                _href=url_next,
                _class='btn btn-default')

        chooser = DIV(previous, nxt, _class='btn-group pull-right')

        form_styled = DIV(form.custom.begin,
                          DIV(B('Show classes on '),
                              form.custom.widget.date,
                              _class='col-md-3'),
                          DIV(BR(),
                              form.custom.submit,
                              chooser,
                              _class='col-md-9 no-padding-left'),
                          form.custom.end,
                          _class='row')

        return {'form': form,
                'form_styled': form_styled}


    def classes_add_get_list(self, date, list_type, cuID=None, teID=None):
        """
            Get list of classes for a date
            list_type is expected to be in
            [ 'attendance', 'reservations', 'tp_fixed_rate' ]
        """
        from .os_attendance_helper import AttendanceHelper
        from .os_class_schedule import ClassSchedule
        from .os_gui import OsGui

        T = current.T
        db = current.db
        os_gui = OsGui()
        DATE_FORMAT = current.DATE_FORMAT
        session = current.session

        if list_type == 'attendance':
            session.classes_attendance_signin_back = 'cu_classes_attendance'
            ah = AttendanceHelper()
            # links = [ lambda row: ah.get_signin_buttons(row.classes.id, date, cuID) ]

        if session.classes_schedule_sort == 'location':
            orderby = db.school_locations.Name | db.classes.Starttime
        elif session.classes_schedule_sort == 'starttime':
            orderby = db.classes.Starttime | db.school_locations.Name
        else:
            orderby = db.school_locations.Name | db.classes.Starttime

        filter_id_teacher = None
        if list_type == 'tp_fixed_rate':
            filter_id_teacher = cuID
        cs = ClassSchedule(date,
                           sorting=orderby,
                           filter_id_teacher=filter_id_teacher)
        classes = cs.get_day_list()

        header = THEAD(TR(TH(T('Time')),
                          TH(T('Location')),
                          TH(T('Class')),
                          TH(),
                          TH()  # buttons
                          ))
        table = TABLE(header, _class='table table-striped table-hover')
        for c in classes:
            status = self._classes_add_get_list_get_cancelled_holiday(c)
            buttons = ''

            if list_type == 'reservations':
                buttons = self._classes_reservation_add_get_button(c['ClassesID'])
            elif list_type == 'attendance' and status == '':
                buttons = os_gui.get_button('noicon',
                                            URL('customers', 'classes_attendance_add_booking_options',
                                                vars={'cuID': cuID,
                                                      'clsID': c['ClassesID'],
                                                      'date': date.strftime(DATE_FORMAT)}),
                                            title='Check in',
                                            _class='pull-right')
            elif list_type == 'tp_fixed_rate':
                buttons = os_gui.get_button(
                    'noicon',
                    URL('teachers',
                        'payment_fixed_rate_class',
                        vars={'teID': teID,
                              'clsID': c['ClassesID']}),
                    title=T('Set rate'),
                    _class='pull-right'
                )

            tr = TR(
                TD(c['Starttime'], ' - ', c['Endtime']),
                TD(c['Location']),
                TD(c['ClassType']),
                TD(status),
                TD(buttons)
            )

            table.append(tr)

        return table

    def _classes_reservation_add_get_button(self, clsID):
        """
            Returns add button for a customer to add a reservation
        """
        from .os_customer import Customer
        from .os_gui import OsGui
        os_gui = OsGui()

        session = current.session
        DATE_FORMAT = current.DATE_FORMAT

        date = session.customers_classes_reservation_add_vars['date']
        date_formatted = date.strftime(DATE_FORMAT)
        cuID = session.customers_classes_reservation_add_vars['cuID']
        customer = Customer(cuID)

        add = os_gui.get_button('add', URL('classes', 'reservation_add_choose',
                                           vars={'cuID': cuID,
                                                 'clsID': clsID,
                                                 'date': date_formatted}),
                                btn_size='btn-sm',
                                _class="pull-right")

        return add

    def _classes_add_get_list_get_cancelled_holiday(self, c):
        """
            Returns class or holiday description when a class is cancelled
            :param: class from ClassSchedule.get_day_list()
        """
        T = current.T
        status = ''

        if c['Cancelled']:
            status = SPAN(T('Cancelled'), ' ', SPAN(c['CancelledDescription'], _class='grey'))

        if c['Holiday']:
            status = SPAN(T('Holiday'), ' ', SPAN(c['HolidayDescription'], _class='grey'))

        return status


    # def get_add_modal(self,
    #                   button_text='Add',
    #                   button_class='btn-sm',
    #                   redirect_vars={}):
    #     """
    #         Returns button and modal for an add button
    #     """
    #     os_gui = current.globalenv['os_gui']
    #
    #     add = LOAD('customers', 'add.load', ajax=True, vars=redirect_vars)
    #
    #     button_text = XML(SPAN(I(_class='fa fa-plus'), ' ',
    #                            current.T(button_text)))
    #
    #     if 'teacher' in redirect_vars:
    #         modal_title = current.T('Add teacher')
    #     elif 'employee' in redirect_vars:
    #         modal_title = current.T('Add employee')
    #     else:
    #         modal_title = current.T('Add customer')
    #
    #     result = os_gui.get_modal(button_text=button_text,
    #                               modal_title=modal_title,
    #                               modal_content=add,
    #                               modal_footer_content=os_gui.get_submit_button('customer_add'),
    #                               modal_class='customers_add_new_modal',
    #                               button_class=button_class)
    #
    #     return result
    #
    
    def get_add(self,
                button_text=None,
                btn_size='btn-sm',
                redirect_vars={}):
        """
        :return: Returns an html add button for an account
        """
        from openstudio.os_gui import OsGui

        os_gui = OsGui()

        add = os_gui.get_button(
            'add',
            URL('customers', 'add', vars=redirect_vars),
            _class='pull-right',
            btn_size=btn_size,
            title=button_text
        )
        
        return add
    

    def get_credits_balance(self, date, include_reconciliation_classes=False):
        """
        :param date: datetime.date
        :return: Dictionary of customerID's containing current balance and total of reconcilliation credits allowed
        by all subscriptions a customer has on given date
        """
        db = current.db

        query = '''SELECT cs.id, 
                          cs.auth_customer_id, 
                          ssu.Name, 
                          ssu.ReconciliationClasses, 
                          cs.Startdate, 
                          cs.Enddate,
                          IFNULL((( SELECT SUM(csc.MutationAmount)
                                    FROM customers_subscriptions_credits csc
                                    WHERE csc.customers_subscriptions_id = cs.id AND
	                                csc.MutationType = 'add') - 
                                  ( SELECT SUM(csc.MutationAmount)
                                    FROM customers_subscriptions_credits csc
                                    WHERE csc.customers_subscriptions_id = cs.id AND
	                                csc.MutationType = 'sub')), 0) AS credits
                          FROM customers_subscriptions cs
                          LEFT JOIN 
                            school_subscriptions ssu ON cs.school_subscriptions_id = ssu.id
                          WHERE (cs.Startdate <= '{date}' AND (cs.Enddate >= '{date}' OR cs.Enddate IS NULL))
                          ORDER BY cs.Startdate'''.format(date=date)

        result = db.executesql(query)

        data = {}
        for record in result:
            # add current balance
            try:
                data[record[1]] += record[6]
            except KeyError:
                data[record[1]] = record[6]

            if include_reconciliation_classes:
                # add recon credits
                data[record[1]] += record[3]

        return data
