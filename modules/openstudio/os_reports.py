# -*- coding: utf-8 -*-

import datetime

from gluon import *


class Reports:
    def get_rows_classcards_sold_in_month(self, year, month):
        """
        returns
        :return:
        """
        db = current.db

        date = datetime.date(year, month, 1)
        firstdaythismonth = date
        next_month = date.replace(day=28) + datetime.timedelta(days=4)  # this will never fail
        lastdaythismonth = next_month - datetime.timedelta(days=next_month.day)


        query = (db.customers_classcards.Startdate >= firstdaythismonth) & \
                (db.customers_classcards.Startdate <= lastdaythismonth) & \
                (db.school_classcards.Trialcard == False)

        rows = db(query).select(
            db.auth_user.id,
            db.auth_user.trashed,
            db.auth_user.thumbsmall,
            db.auth_user.birthday,
            db.auth_user.first_name,
            db.auth_user.last_name,
            db.auth_user.display_name,
            db.auth_user.email,
            db.auth_user.date_of_birth,
            db.customers_classcards.id,
            db.customers_classcards.Startdate,
            db.customers_classcards.Enddate,
            db.customers_classcards.school_classcards_id,
            db.school_classcards.Name,
            db.school_classcards.Classes,
            db.school_classcards.Price,
            db.school_classcards.Unlimited,
            left=[db.auth_user.on(db.auth_user.id == \
                                  db.customers_classcards.auth_customer_id),
                  db.school_classcards.on(
                      db.customers_classcards.school_classcards_id == \
                      db.school_classcards.id)],
            orderby=~db.customers_classcards.Startdate | ~db.auth_user.display_name
        )

        return rows

    def get_query_subscriptions_new_in_month(self,
                                             date,
                                             filter_school_locations_id=None):
        """
            Returns query for new subscriptions
        """
        firstdaythismonth = datetime.date(date.year, date.month, 1)
        next_month = date.replace(day=28) + datetime.timedelta(days=4)  # this will never fail
        lastdaythismonth = next_month - datetime.timedelta(days=next_month.day)

        where_school_locations_id = ''
        if filter_school_locations_id:
            where_school_locations_id = " AND cu.school_locations_id = %s" % filter_school_locations_id

        query = """SELECT cu.id,
                          cu.trashed,
                          cu.thumbsmall,
                          cu.birthday,
                          cu.first_name,
                          cu.last_name,
                          cu.display_name,
                          cu.date_of_birth,
                          cu.email,
                          csu.school_subscriptions_id,
                          csu.startdate,
                          csu.payment_methods_id
                   FROM auth_user cu
                   LEFT JOIN
                       (SELECT auth_customer_id,
                               startdate,
                               enddate,
                               school_subscriptions_id,
                               payment_methods_id
                        FROM customers_subscriptions
                        GROUP BY auth_customer_id) csu
                   ON cu.id = csu.auth_customer_id
                   LEFT JOIN school_subscriptions ssu
                   ON ssu.id = csu.school_subscriptions_id
                   ,
                   (SELECT min(startdate) startdate,
                                          auth_customer_id
                    FROM customers_subscriptions
                    GROUP BY auth_customer_id) chk
                   WHERE chk.startdate = csu.startdate AND
                         chk.auth_customer_id = csu.auth_customer_id AND
                         csu.startdate >= '{firstdaythismonth}' AND csu.startdate <= '{lastdaythismonth}'
                         {where_school_locations_id}
                   ORDER BY csu.startdate DESC,
                            cu.display_name
                            """.format(firstdaythismonth=firstdaythismonth,
                                           lastdaythismonth=lastdaythismonth,
                                           where_school_locations_id=where_school_locations_id)
        return query


    def get_query_subscriptions_stopped_in_month(self,
                                                 date,
                                                 filter_school_locations_id=None):
        """
            Returns query for new subscriptions
        """
        firstdaythismonth = datetime.date(date.year, date.month, 1)
        next_month = date.replace(day=28) + datetime.timedelta(days=4)  # this will never fail
        lastdaythismonth = next_month - datetime.timedelta(days=next_month.day)

        where_school_locations_id = ''
        if filter_school_locations_id:
            where_school_locations_id = " AND cu.school_locations_id = %s" % filter_school_locations_id

        query = """SELECT cu.id,
                          cu.trashed,
                          cu.thumbsmall,
                          cu.birthday,
                          cu.display_name,
                          cu.date_of_birth,
                          csu.school_subscriptions_id,
                          csu.enddate
                   FROM auth_user cu
                   LEFT JOIN
                       (SELECT auth_customer_id,
                               startdate,
                               enddate,
                               school_subscriptions_id
                        FROM customers_subscriptions) csu
                   ON cu.id = csu.auth_customer_id
                   LEFT JOIN school_subscriptions ssu
                   ON ssu.id = csu.school_subscriptions_id,
                       (SELECT max(startdate) startdate,
                               auth_customer_id
                        FROM customers_subscriptions
                        GROUP BY auth_customer_id) chk
                   WHERE chk.startdate = csu.startdate AND
                         csu.auth_customer_id = chk.auth_customer_id AND
                         csu.enddate >= '{firstdaythismonth}' AND csu.enddate <= '{lastdaythismonth}'
                         AND csu.enddate IS NOT NULL
                         {where_school_locations_id}
                    ORDER BY ssu.Name,
                             cu.display_name
                             DESC""".format(firstdaythismonth=firstdaythismonth,
                                            lastdaythismonth=lastdaythismonth,
                                            where_school_locations_id=where_school_locations_id)
        return query


    def get_subscriptions_online_in_month_rows(self, date):
        """
        Return rows for subscriptions coming from the shop in a given month
        where date is a day in the selected month
        :param date:
        :return:
        """
        from ..general_helpers import get_last_day_month

        db = current.db

        first_of_month = datetime.date(date.year, date.month, 1)
        end_of_month = get_last_day_month(first_of_month)

        query = (
            (db.customers_subscriptions.Startdate >= first_of_month) &
            (db.customers_subscriptions.Startdate <= end_of_month) &
            (db.customers_subscriptions.Origin == "SHOP") &
            (db.customers_subscriptions.payment_methods_id == 3)
        )

        left = [
            db.auth_user.on(
                db.customers_subscriptions.auth_customer_id ==
                db.auth_user.id
            )
        ]

        return db(query).select(
            db.customers_subscriptions.ALL,
            db.auth_user.id,
            db.auth_user.trashed,
            db.auth_user.thumbsmall,
            db.auth_user.birthday,
            db.auth_user.first_name,
            db.auth_user.last_name,
            db.auth_user.display_name,
            db.auth_user.date_of_birth,
            db.auth_user.email,
            left=left,
            orderby=db.customers_subscriptions.Startdate
        )


    def get_day_mollie_dropin_classes_sold_summary_day(self, date):
        """
        Returns summary of drop-in classes bought using mollie for a given date
        :param: date: datetime.date
        :return:
        """
        db = current.db

        query = (db.invoices_payments.payment_methods_id == 100) & \
                (db.invoices_payments.PaymentDate == date) & \
                (db.customers_orders_items.classes_id != None) & \
                ((db.customers_orders_items.AttendanceType == 1) |
                 (db.customers_orders_items.AttendanceType == 2))

        left = [
            db.invoices.on(db.invoices.id == db.invoices_payments.invoices_id),
            db.invoices_customers_orders.on(db.invoices_customers_orders.invoices_id == db.invoices.id),
            db.customers_orders_items.on(db.invoices_customers_orders.customers_orders_id ==
                                         db.customers_orders_items.customers_orders_id)
        ]

        count = db.invoices_payments.Amount.count()

        rows = db(query).select(
            db.invoices_payments.Amount,
            count,
            left=left,
            groupby=db.invoices_payments.Amount
        )

        return rows


    def get_day_mollie_dropin_classes_taken_summary_day(self, date):
        """
        Returns summary of drop-in classes bought using mollie for a given date
        :param: date: datetime.date
        :return:
        """
        db = current.db

        query = (db.invoices_payments.payment_methods_id == 100) & \
                (db.classes_attendance.ClassDate == date)

        left = [
            db.invoices.on(db.invoices.id == db.invoices_payments.invoices_id),
            db.invoices_items.on(db.invoices_items.invoices_id == db.invoices.id),
            db.invoices_items_classes_attendance.on(db.invoices_items_classes_attendance.invoices_items_id ==
                                                    db.invoices_items.id),
            db.classes_attendance.on(db.invoices_items_classes_attendance.classes_attendance_id ==
                                     db.classes_attendance.id)
        ]

        count = db.invoices_payments.Amount.count()

        rows = db(query).select(
            db.invoices_payments.Amount,
            count,
            left=left,
            groupby=db.invoices_payments.Amount
        )

        return rows


    def get_classes_revenue_summary_day(self, date, booking_status):
        """

        :param date:
        :return:
        """
        from .os_class import Class
        from .os_class_schedule import ClassSchedule

        # Get class schedule for days
        cs = ClassSchedule(date, attendance_count=booking_status)
        schedule = cs.get_day_list()

        revenue = {
            'data': [],
            'revenue_total': 0,
            'teacher_payments': 0,
            'balance': 0
        }


        for cls in schedule:
            clsID = cls['ClassesID']
            # Get revenue for each class
            class_revenue = self.get_class_revenue_summary(clsID, date, booking_status=booking_status)

            cls_object = Class(clsID, date)
            teacher_payment = cls_object.get_teacher_payment()
            if not teacher_payment['error']:
                tp_amount = teacher_payment['data']['ClassRate']
            else:
                tp_amount = 0

            cls['ClassesID'] = clsID
            cls['RevenueTotal'] = class_revenue['total']['amount']
            cls['TeacherPayment'] = tp_amount
            cls['Balance'] = (cls['RevenueTotal'] - cls['TeacherPayment'])
            cls['Teachers'] = cls_object.get_teachers()

            revenue['revenue_total'] += cls['RevenueTotal']
            revenue['teacher_payments'] += cls['TeacherPayment']
            revenue['balance'] += cls['Balance']

            revenue['data'].append(cls)

        return revenue


    def get_class_revenue_summary(self, clsID, date, booking_status, quick_stats=True):
        """
        :param subscription_quick_stats: Boolean - use db.school_subscriptions.QuickStatsAmount or not
        :return:
        """
        from .os_class import Class

        cls = Class(clsID, date)
        class_prices = cls.get_prices()

        # print class_prices
        # print type(class_prices['trial_membership'])
        # print type(class_prices['trial'])

        data = {
            'subscriptions': {},
            'staff_subscriptions': {},
            'classcards': {},
            'dropin': {
                'membership': {
                    'count': 0,
                    'amount': class_prices['dropin_membership']
                },
                'no_membership': {
                    'count': 0,
                    'amount': class_prices['dropin']
                }
            },
            'trial': {
                'membership': {
                    'count': 0,
                    'amount': class_prices['trial_membership']
                },
                'no_membership': {
                    'count': 0,
                    'amount': class_prices['trial']
                }
            },
            'complementary': {
                'count': 0,
                'amount': 0
            },
            'reconcile_later': {
                'count': 0,
                'amount': 0
            },
            'total': {
                'count_unpaid': 0,
                'count_paid': 0,
                'count_total': 0,
                'amount': 0
            }
        }

        rows = self.get_class_revenue_rows(clsID, date, booking_status=booking_status)
        for i, row in enumerate(rows):
            repr_row = list(rows[i:i + 1].render())[0]

            ex_vat = 0
            vat = 0
            in_vat = 0
            description = ''
            if row.classes_attendance.AttendanceType is None:
                # Subscription
                name = row.school_subscriptions.Name
                amount = row.school_subscriptions.QuickStatsAmount or 0
                data['total']['amount'] += amount

                if row.school_subscriptions.StaffSubscription:
                    # Staff
                    if data['staff_subscriptions'].get(name, False):
                        data['staff_subscriptions'][name]['count'] += 1
                        data['staff_subscriptions'][name]['total'] = \
                            data['staff_subscriptions'][name]['count'] * amount
                    else:
                        data['staff_subscriptions'][name] = {
                            'count': 1,
                            'total': amount,
                            'amount': amount
                        }

                    data['total']['count_unpaid'] += 1
                else:
                    # Customers
                    if data['subscriptions'].get(name, False):
                        data['subscriptions'][name]['count'] += 1
                        data['subscriptions'][name]['total'] = \
                            data['subscriptions'][name]['count'] * amount
                    else:
                        data['subscriptions'][name] = {
                            'count': 1,
                            'total': amount,
                            'amount': amount
                        }

                    data['total']['count_paid'] += 1

            elif row.classes_attendance.AttendanceType == 1:
                # Trial
                if row.classes_attendance.CustomerMembership:
                    data['trial']['membership']['count'] += 1
                    data['total']['amount'] += data['trial']['membership']['amount']
                else:
                    data['trial']['no_membership']['count'] += 1
                    data['total']['amount'] += data['trial']['no_membership']['amount']

                data['total']['count_paid'] += 1

            elif row.classes_attendance.AttendanceType == 2:
                # Dropin
                if row.classes_attendance.CustomerMembership:
                    data['dropin']['membership']['count'] += 1
                    data['total']['amount'] += data['dropin']['membership']['amount']
                else:
                    data['dropin']['no_membership']['count'] += 1
                    data['total']['amount'] += data['dropin']['no_membership']['amount']

                data['total']['count_paid'] += 1

            elif row.classes_attendance.AttendanceType == 3:
                # Class card
                name = row.school_classcards.Name
                if not row.school_classcards.Unlimited:
                    import decimal
                    try:
                        amount = row.school_classcards.Price / row.school_classcards.Classes
                    except decimal.DivisionByZero:
                        amount = 0
                else:
                    amount = row.school_classcards.QuickStatsAmount or 0
                if data['classcards'].get(name, False):
                    data['classcards'][name]['count'] += 1
                    data['classcards'][name]['total'] = \
                        data['classcards'][name]['count'] * amount
                else:
                    data['classcards'][name] = {
                        'count': 1,
                        'total': amount,
                        'amount': amount
                    }

                data['total']['amount'] += amount
                data['total']['count_paid'] += 1

            elif row.classes_attendance.AttendanceType == 4:
                # Complementary
                data['complementary']['count'] += 1
                data['total']['count_unpaid'] += 1

            elif row.classes_attendance.AttendanceType == 6:
                # Reconcile later
                data['reconcile_later']['count'] += 1
                data['total']['count_paid'] += 1

            data['total']['count_total'] += 1


        return data


    def get_class_revenue_summary_formatted(self, clsID, date, booking_status, quick_stats=True):
        """
        Format output from self.get_class_revenue_summary
        :param clsID: db.classes.id
        :param date: datetime.date
        :param quickstats: boolean
        :return: html table
        """
        from .os_class import Class
        from general_helpers import max_string_length
        from decimal import Decimal, ROUND_HALF_UP

        T = current.T
        represent_decimal_as_amount = current.globalenv['represent_decimal_as_amount']

        revenue = self.get_class_revenue_summary(
            clsID=clsID,
            date=date,
            booking_status=booking_status,
            quick_stats=quick_stats
        )

        header = THEAD(TR(
            TH(T('Type')),
            TH(T('Customers')),
            TH(T('Guests & staff')),
            TH(T('Attendance')),
            TH(T('Amount')),
            TH(T('Total')),
        ))

        trial_without_membership = TR(
            TD(T('Trial without membership')),
            TD(revenue['trial']['no_membership']['count']),
            TD(0),
            TD(revenue['trial']['no_membership']['count']),
            TD(represent_decimal_as_amount(revenue['trial']['no_membership']['amount'])),
            TD(represent_decimal_as_amount(
                revenue['trial']['no_membership']['amount'] * revenue['trial']['no_membership']['count']
            )),
        )

        trial_with_membership =  TR(
            TD(T('Trial with membership')),
            TD(revenue['trial']['membership']['count']),
            TD(0),
            TD(revenue['trial']['membership']['count']),
            TD(represent_decimal_as_amount(revenue['trial']['membership']['amount'])),
            TD(represent_decimal_as_amount(
                revenue['trial']['membership']['amount'] * revenue['trial']['membership']['count']
            )),
        )

        dropin_without_membership = TR(
            TD(T('Drop-in without membership')),
            TD(revenue['dropin']['no_membership']['count']),
            TD(0),
            TD(revenue['dropin']['no_membership']['count']),
            TD(represent_decimal_as_amount(revenue['dropin']['no_membership']['amount'])),
            TD(represent_decimal_as_amount(
                revenue['dropin']['no_membership']['amount'] * revenue['dropin']['no_membership']['count']
            )),
        )

        dropin_with_membership =  TR(
            TD(T('Drop-in with membership')),
            TD(revenue['dropin']['membership']['count']),
            TD(0),
            TD(revenue['dropin']['membership']['count']),
            TD(represent_decimal_as_amount(revenue['dropin']['membership']['amount'])),
            TD(represent_decimal_as_amount(
                revenue['dropin']['membership']['amount'] * revenue['dropin']['membership']['count']
            )),
        )

        table_revenue = TABLE(
            header,
            trial_without_membership,
            trial_with_membership,
            dropin_without_membership,
            dropin_with_membership,
            _class='table table-striped table-hover'
        )

        # subscriptions
        for s in sorted(revenue['subscriptions']):
            amount = revenue['subscriptions'][s]['amount']
            count = revenue['subscriptions'][s]['count']

            table_revenue.append(TR(
                TD(max_string_length(s, 42)),
                TD(count),
                TD(0),
                TD(count),
                TD(represent_decimal_as_amount(amount)),
                TD(represent_decimal_as_amount(amount * count))
            ))

        # staff subscriptions
        for s in sorted(revenue['staff_subscriptions']):
            amount = revenue['staff_subscriptions'][s]['amount']
            count = revenue['staff_subscriptions'][s]['count']

            table_revenue.append(TR(
                TD(max_string_length(s, 42)),
                TD(0),
                TD(count),
                TD(count),
                TD(represent_decimal_as_amount(amount)),
                TD(represent_decimal_as_amount(amount * count))
            ))

        # class cards
        for c in sorted(revenue['classcards']):
            amount = revenue['classcards'][c]['amount']
            count = revenue['classcards'][c]['count']

            table_revenue.append(TR(
                TD(max_string_length(c, 42)),
                TD(count),
                TD(0),
                TD(count),
                TD(represent_decimal_as_amount(amount)),
                TD(represent_decimal_as_amount(amount * count))
            ))

        # Complementary
        table_revenue.append(TR(
            TD(T('Complementary')),
            TD(0),
            TD(revenue['complementary']['count']),
            TD(revenue['complementary']['count']),
            TD(),
            TD(),
        ))

        # Reconcile later
        table_revenue.append(TR(
            TD(T('Reconcile later')),
            TD(revenue['reconcile_later']['count']),
            TD(0),
            TD(revenue['reconcile_later']['count']),
            TD(),
            TD(),
        ))

        # Total
        footer = TFOOT(TR(
            TH(T('Total')),
            TH(revenue['total']['count_paid']),
            TH(revenue['total']['count_unpaid']),
            TH(revenue['total']['count_total']),
            TH(),
            TH(represent_decimal_as_amount(revenue['total']['amount'])),
        ))

        table_revenue.append(footer)

        ##
        # table total
        ##
        cls = Class(clsID, date)
        teacher_payment = cls.get_teacher_payment()
        # print(teacher_payment)
        if not teacher_payment['error']:
            tp_amount = teacher_payment['data']['ClassRate']
            tp_display = represent_decimal_as_amount(tp_amount)
        else:
            tp_amount = 0
            tp_display = teacher_payment['data']

        header = THEAD(TR(
            TH(T('Description')),
            TH(T('Amount')),
        ))

        attendance = TR(
            TD(T('Attendance')),
            TD(represent_decimal_as_amount(revenue['total']['amount']))
        )

        teacher_payment = TR(
            TD(T('Teacher payment')),
            TD(tp_display)
        )

        total = represent_decimal_as_amount(revenue['total']['amount'] - tp_amount)
        footer = TFOOT(TR(
            TH(T('Total')),
            TH(total)
        ))

        table_total = TABLE(
            header,
            attendance,
            teacher_payment,
            footer,
            _class='table table-striped table-hover'
        )


        return dict(
            table_revenue=table_revenue,
            table_total=table_total
        )


    def get_class_revenue_summary_pdf(self, clsID, date, booking_status, quick_stats=True):
        """
        :param clsID: db.classes.id
        :param date: datetime.date
        :param quick_stats: bool
        :return: BytesIO object containing PDF file for summary export
        """
        import io
        import weasyprint

        html = self._get_class_revenue_summary_pdf_template(clsID, date, booking_status, quick_stats)

        stream = io.BytesIO()
        workshop = weasyprint.HTML(string=html).write_pdf(stream)

        return stream


    def _get_class_revenue_summary_pdf_template(self, clsID, date, booking_status, quick_stats=True):
        """
            Print friendly display of a Workshop
        """
        from general_helpers import max_string_length
        from .os_class import Class

        get_sys_property = current.globalenv['get_sys_property']
        represent_decimal_as_amount = current.globalenv['represent_decimal_as_amount']
        response = current.response

        template = get_sys_property('branding_default_template_class_revenue') or 'class_revenue/default.html'
        template_file = 'templates/' + template

        # tables = self.get_class_revenue_summary_formatted(clsID, date)
        cls = Class(clsID, date)

        teacher_payment = cls.get_teacher_payment()

        html = response.render(template_file,
                               dict(class_info = cls.get_info(),
                                    revenue=self.get_class_revenue_summary(clsID, date, booking_status, quick_stats),
                                    teacher_payment=teacher_payment,
                                    logo=self._get_class_revenue_summary_pdf_template_get_logo(),
                                    max_string_length=max_string_length,
                                    represent_decimal_as_amount=represent_decimal_as_amount,
                                ))

        return html


    def _get_class_revenue_summary_pdf_template_get_logo(self):
        """
            Returns logo for pdf template
        """
        import os

        request = current.request

        branding_logo = os.path.join(request.folder,
                                     'static',
                                     'plugin_os-branding',
                                     'logos',
                                     'branding_logo_invoices.png')
        if os.path.isfile(branding_logo):
            abs_url = URL('static', 'plugin_os-branding/logos/branding_logo_invoices.png',
                          scheme=True,
                          host=True)

            # abs_url = '%s://%s/%s/%s' % (request.env.wsgi_url_scheme,
            #                              request.env.http_host,
            #                              'static',
            #                              'plugin_os-branding/logos/branding_logo_invoices.png')
            logo_img = IMG(_src=abs_url)

        else:
            logo_img = ''

        return logo_img


    def get_class_revenue_rows(self, clsID, date, booking_status):
        """
        :param clsID: db.classes.id
        :param date: Class date
        :param booking_status: "attending", "booked", "attending_and_booked"
        :return: All customers attending a class (db.customers_attendance.ALL & db.customers_subscriptions.ALL)
        """
        db = current.db

        left = [db.customers_classcards.on(
                    db.customers_classcards.id == db.classes_attendance.customers_classcards_id),
                db.school_classcards.on(
                    db.customers_classcards.school_classcards_id == db.school_classcards.id
                ),
                db.customers_subscriptions.on(
                    db.customers_subscriptions.id == db.classes_attendance.customers_subscriptions_id),
                db.school_subscriptions.on(
                    db.customers_subscriptions.school_subscriptions_id == db.school_subscriptions.id
                ),
                db.auth_user.on(db.classes_attendance.auth_customer_id == db.auth_user.id),
        ]
        query = (db.classes_attendance.classes_id == clsID) & \
                (db.classes_attendance.ClassDate == date)

        if booking_status == "attending":
            query &= (db.classes_attendance.BookingStatus == "attending")
        elif booking_status == "booked":
            query &= (db.classes_attendance.BookingStatus == "booked")
        elif booking_status == "attending_and_booked":
            query &= (db.classes_attendance.BookingStatus != 'cancelled')

        rows = db(query).select(db.auth_user.ALL,
                                db.classes_attendance.ALL,
                                db.customers_subscriptions.ALL,
                                db.school_subscriptions.ALL,
                                db.customers_classcards.ALL,
                                db.school_classcards.ALL,
                                left=left,
                                orderby=db.auth_user.display_name)

        return rows


    def get_class_revenue_classcard(self, row):
        """
            :param row: row from db.classes_attendance with left join on db.customers_subscriptions
            :return: Revenue for class taken on a card
        """
        db = current.db

        from .os_customer_classcard import CustomerClasscard
        from .os_invoice import Invoice

        ccdID = row.classes_attendance.customers_classcards_id
        classcard = CustomerClasscard(ccdID)

        left = [
            db.invoices_items.on(
                db.invoices_items_customers_classcards.invoices_items_id ==
                db.invoices_items.id
            )
        ]
        query = (db.invoices_items_customers_classcards.customers_classcards_id == ccdID)
        rows = db(query).select(db.invoices_items.ALL,
                                left=left)

        if not rows:
            revenue_in_vat = 0
            revenue_ex_vat = 0
            revenue_vat = 0
        else:
            row = rows.first()
            invoice = Invoice(row.invoices_id)
            amounts = invoice.get_amounts()

            price_in_vat = amounts.TotalPriceVAT
            price_ex_vat = amounts.TotalPrice

            # Divide by classes taken on card
            if classcard.unlimited:
                # Count all classes taken on card
                    query = (db.classes_attendance.customers_classcards_id == ccdID)
                    count_classes = db(query).count()

                    revenue_in_vat = price_in_vat / count_classes
                    revenue_ex_vat = price_ex_vat / count_classes
                    revenue_vat = revenue_in_vat - revenue_ex_vat
            else:
                revenue_in_vat = price_in_vat / classcard.classes
                revenue_ex_vat = price_ex_vat / classcard.classes
                revenue_vat = revenue_in_vat - revenue_ex_vat

        return dict(revenue_in_vat=revenue_in_vat,
                    revenue_ex_vat=revenue_ex_vat,
                    revenue_vat=revenue_vat)


    def classcards_sold_summary_rows(self, date_from, date_until):
        """
        List cards sold, grouped by card name

        :param date_from: datetime.date
        :param date_until: datetime.date
        :return:
        """
        db = current.db

        left = [
            db.school_classcards.on(
                db.customers_classcards.school_classcards_id ==
                db.school_classcards.id
            )
        ]

        count = db.school_classcards.id.count()

        query = (db.customers_classcards.Startdate >= date_from) & \
                (db.customers_classcards.Startdate <= date_until)

        rows = db(query).select(db.school_classcards.Name,
                                db.school_classcards.Price,
                                count,
                                left=left,
                                groupby=db.school_classcards.Name,
                                orderby=db.school_classcards.Name)

        return rows


    def subscriptions_sold_on_date_summary_rows(self, date):
        """
        List school subscriptions sold, grouped by subscription

        :param date_from: datetime.date
        :param date_until: datetime.date
        :return:
        """
        db = current.db

        fields = [
            db.school_subscriptions.id,
            db.school_subscriptions.Name,
            db.invoices_items.TotalPriceVAT,
            db.school_subscriptions.CountSold
        ]

        sql = '''
            SELECT ssu.id,
                   ssu.Name,
                   ii.TotalPriceVAT,
                   COUNT(ssu.id)
            FROM invoices_items ii
            LEFT JOIN invoices i ON ii.invoices_id = i.id
            LEFT JOIN invoices_items_customers_subscriptions iics ON iics.invoices_items_id = ii.id
            LEFT JOIN customers_subscriptions cs ON iics.customers_subscriptions_id = cs.id
            LEFT JOIN school_subscriptions ssu ON cs.school_subscriptions_id = ssu.id
            WHERE i.DateCreated = "{date}" 
                AND iics.id IS NOT NULL
            GROUP BY ssu.id, ii.TotalPriceVAT
        '''.format(date=date)

        rows = db.executesql(sql, fields=fields)

        return rows


    def memberships_sold_summary_rows(self, date_from, date_until):
        """
        List memberships sold, grouped by membership name

        :param date_from: datetime.date
        :param date_until: datetime.date
        :return:
        """
        db = current.db

        left = [
            db.school_memberships.on(
                db.customers_memberships.school_memberships_id ==
                db.school_memberships.id
            )
        ]

        count = db.school_memberships.id.count()

        query = (db.customers_memberships.Startdate >= date_from) & \
                (db.customers_memberships.Startdate <= date_until)

        rows = db(query).select(db.school_memberships.Name,
                                db.school_memberships.Price,
                                count,
                                left=left,
                                groupby=db.school_memberships.Name,
                                orderby=db.school_memberships.Name)

        return rows


    def shop_sales_summary(self, date_from, date_until):
        """
        List product sales, grouped by product variant

        :param date_from: datetime.date
        :param date_until: datetime.date
        :return:
        """
        db = current.db

        if date_from == date_until:
            # This is required because we're comparing to a date time field
            # For a DT field, the format becomes yyyy-mm-dd 00:00:00 when only supplying a date
            date_until = date_until + datetime.timedelta(days=1)

        query = '''
SELECT SUM(spv.Price * shs.Quantity),
       ag.Name
FROM shop_sales shs
LEFT JOIN shop_sales_products_variants shspv ON shspv.shop_sales_id = shs.id
LEFT JOIN shop_products_variants spv ON shspv.shop_products_variants_id = spv.id
LEFT JOIN shop_products sp ON spv.shop_products_id = sp.id
LEFT JOIN accounting_glaccounts ag ON sp.accounting_glaccounts_id = ag.id
WHERE shs.CreatedOn >= '{date_from}' AND shs.CreatedOn < '{date_until}'
GROUP BY ag.Name
ORDER BY ag.Name
        '''.format(
            date_from=date_from,
            date_until=date_until
        )

        records = db.executesql(query)

        return records


    def shop_sales_custom(self, date_from, date_until):
        """
        List product sales, grouped by product variant

        :param date_from: datetime.date
        :param date_until: datetime.date
        :return:
        """
        db = current.db

        if date_from == date_until:
            # This is required because we're comparing to a date time field
            # For a DT field, the format becomes yyyy-mm-dd 00:00:00 when only supplying a date
            date_until = date_until + datetime.timedelta(days=1)

        query = (db.receipts.CreatedOn >= date_from) & \
                (db.receipts.CreatedOn <= date_until) & \
                (db.receipts_items.Custom == True)

        left = [
            db.receipts.on(db.receipts_items.receipts_id == db.receipts.id)
        ]

        rows = db(query).select(
            db.receipts_items.ALL,
            left=left,
            orderby=db.receipts_items.ProductName
        )

        return rows


    def shop_sales_not_paid_with_cash_summary(self, date_from, date_until):
        """

        :param date_from: datetime.date
        :param date_until: datetime.date
        :return:
        """
        db = current.db

        if date_from == date_until:
            # This is required because we're comparing to a date time field
            # For a DT field, the format becomes yyyy-mm-dd 00:00:00 when only supplying a date
            date_until = date_until + datetime.timedelta(days=1)

        sum_not_paid_using_cash = 0

        left = [
            db.receipts_amounts.on(
                db.receipts_amounts.receipts_id ==
                db.receipts.id
            ),
            db.payment_methods.on(
                db.receipts.payment_methods_id ==
                db.payment_methods.id
            )
        ]

        query = (db.receipts.CreatedOn >= date_from) & \
                (db.receipts.CreatedOn <= date_until) & \
                (db.receipts.payment_methods_id != 1) # method 1 == cash

        sum = db.receipts_amounts.TotalPriceVAT.sum()
        rows = db(query).select(
            db.payment_methods.id,
            db.payment_methods.Name,
            sum,
            left=left,
            groupby=db.receipts.payment_methods_id,
            orderby=db.payment_methods.Name
        )

        return rows

    def shop_sales_mollie_summary(self, date_from, date_until):
        """

        :param date_from: datetime.date
        :param date_until: datetime.date
        :return:
        """
        db = current.db

        sum_paid_using_mollie = 0

        left = [
            db.payment_methods.on(
                db.invoices_payments.payment_methods_id ==
                db.payment_methods.id
            )
        ]

        query = (db.invoices_payments.PaymentDate >= date_from) & \
                (db.invoices_payments.PaymentDate <= date_until) & \
                (db.invoices_payments.payment_methods_id == 100) # method 100 = Mollie

        sum = db.invoices_payments.Amount.sum()
        rows = db(query).select(sum, left=left)

        if rows:
            row = rows.first()
            sum_paid_using_mollie = row[sum]

        return sum_paid_using_mollie or 0


    def classes_attendance_classcards_quickstats_summary(self, date_from, date_until):
        """

        :param date_from: datetime.date
        :param date_until: datetime.date
        :return:
        """
        db = current.db

        left = [
            # Cards
            db.customers_classcards.on(
                db.classes_attendance.customers_classcards_id ==
                db.customers_classcards.id
            ),
            db.school_classcards.on(
                db.customers_classcards.school_classcards_id ==
                db.school_classcards.id
            )
        ]

        count = db.school_classcards.id.count()

        # Important; don't just change the status. The Cashbook depends on the status attending by default.
        # If the status needs to change, the cashbook needs to be able to specify only attending.
        query = (db.classes_attendance.ClassDate >= date_from) & \
                (db.classes_attendance.ClassDate <= date_until) & \
                (db.classes_attendance.customers_classcards_id != None) & \
                (db.classes_attendance.BookingStatus == "attending")

        rows = db(query).select(
            db.school_classcards.id,
            db.school_classcards.Name,
            db.school_classcards.QuickStatsAmount,
            db.school_classcards.Classes,
            db.school_classcards.Price,
            db.school_classcards.Unlimited,
            count,
            left=left,
            groupby=db.school_classcards.id,
            orderby=db.school_classcards.Name
        )

        return rows


    def classes_attendance_subscriptions_quickstats_summary(self, date_from, date_until):
        """

        :param date_from: datetime.date
        :param date_until: datetime.date
        :return:
        """
        db = current.db

        left = [
            # Subscriptions
            db.customers_subscriptions.on(
                db.classes_attendance.customers_subscriptions_id ==
                db.customers_subscriptions.id
            ),
            db.school_subscriptions.on(
                db.customers_subscriptions.school_subscriptions_id ==
                db.school_subscriptions.id
            ),
        ]

        count = db.school_subscriptions.id.count()

        # Important; don't just change the status. The Cashbook depends on the status attending by default.
        # If the status needs to change, the cashbook needs to be able to specify only attending.
        query = (db.classes_attendance.ClassDate >= date_from) & \
                (db.classes_attendance.ClassDate <= date_until) & \
                (db.classes_attendance.customers_subscriptions_id != None) & \
                (db.classes_attendance.BookingStatus == "attending")

        rows = db(query).select(
            db.school_subscriptions.id,
            db.school_subscriptions.Name,
            db.school_subscriptions.QuickStatsAmount,
            count,
            left=left,
            groupby=db.school_subscriptions.id,
            orderby=db.school_subscriptions.Name
        )

        return rows


    def get_tax_summary_rows(self, date_from, date_until):
        """
        Return invoice items in period grouped by tax_rates_id
        :param date_from: datetime.date
        :param date_until: datetime.date
        :return: gluon.dal.rows object
        """
        db = current.db

        query = (db.invoices.DateCreated >= date_from) & \
                (db.invoices.DateCreated <= date_until)

        left = (
            db.invoices_items.on(
                db.invoices_items.invoices_id ==
                db.invoices.id
            ),
        )

        sum_total = db.invoices_items.TotalPriceVAT.sum()
        sum_subtotal = db.invoices_items.TotalPrice.sum()
        sum_vat = db.invoices_items.VAT.sum()

        rows = db(query).select(
            db.invoices_items.tax_rates_id,
            sum_subtotal,
            sum_vat,
            sum_total,
            left=left,
            groupby=db.invoices_items.tax_rates_id,
            orderby=db.invoices.InvoiceID
        )

        return dict(
            rows=rows,
            sum_subtotal=sum_subtotal,
            sum_total=sum_total,
            sum_vat=sum_vat
        )


    def get_tax_summary_detail_rows(self, tax_rates_id, date_from, date_until):
        """
        Return invoice items in period grouped by tax_rates_id
        :param tax_rates_id: db.tax_rates.id
        :param date_from: datetime.date
        :param date_until: datetime.date
        :return: gluon.dal.rows object
        """
        db = current.db

        query = (db.invoices_items.tax_rates_id == tax_rates_id) & \
                (db.invoices.DateCreated >= date_from) & \
                (db.invoices.DateCreated <= date_until)

        left = (
            db.invoices_items.on(
                db.invoices_items.invoices_id ==
                db.invoices.id
            ),
            db.invoices_customers.on(
                db.invoices.id ==
                db.invoices_customers.invoices_id
            ),
            db.auth_user.on(
                db.invoices_customers.auth_customer_id ==
                db.auth_user.id
            )
        )

        rows = db(query).select(
            db.invoices.ALL,
            db.invoices_items.ALL,
            db.auth_user.display_name,
            db.auth_user.id,
            left=left,
            orderby=db.invoices.InvoiceID
        )

        return rows


    def get_invoices_open_on_date(self, date):
        """
        List open invoices on date
        :return:
        """
        db = current.db

        fields = [
            db.invoices.id,
            db.invoices.Status,
            db.invoices.InvoiceID,
            db.invoices.DateCreated,
            db.invoices_amounts.TotalPriceVAT,
            db.invoices_amounts.Paid,
            db.invoices_amounts.Balance,
            db.auth_user.id,
            db.auth_user.display_name
        ]

        query = '''
	SELECT i.id,
		   i.Status,
		   i.InvoiceID,
		   i.DateCreated,
		   ia.TotalPriceVAT,
		   ip.TotalPaid,
		   ia.TotalPriceVAT - ip.TotalPaid AS Balance,
		   au.id,
		   au.display_name
	FROM invoices i
	LEFT JOIN invoices_amounts ia ON ia.invoices_id = i.id
	LEFT JOIN invoices_customers ic ON ic.invoices_id = i.id
	LEFT JOIN auth_user au ON ic.auth_customer_id = au.id 
	LEFT JOIN (
		SELECT invoices_id,
			   SUM(Amount) AS TotalPaid
		FROM invoices_payments
		WHERE PaymentDate <= '{date}'
		GROUP BY invoices_id
		) ip ON ip.invoices_id = i.id
	WHERE i.DateCreated <= '{date}' 
		  AND ((i.Status = 'paid') OR (i.Status = 'sent'))
		  AND (
		    # Credit invoices
		    (ia.TotalPriceVAT < 0
			 AND ((ROUND(ip.TotalPaid, 2) > ROUND(ia.TotalPriceVAT, 2))
			      OR (ip.TotalPaid IS NULL))) 
			OR
			# Regular invoices
			 (ia.TotalPriceVAT > 0
			  AND ((ROUND(ip.TotalPaid, 2) < ROUND(ia.TotalPriceVAT, 2))
			  OR (ip.TotalPaid IS NULL)))
		   )
		'''.format(date=date)

        rows = db.executesql(query, fields=fields)

        return rows
