# -*- coding: utf-8 -*-

import datetime

from gluon import *


class Reports:
    def get_query_subscriptions_new_in_month(self, date):
        """
            Returns query for new subscriptions
        """
        firstdaythismonth = datetime.date(date.year, date.month, 1)
        next_month = date.replace(day=28) + datetime.timedelta(days=4)  # this will never fail
        lastdaythismonth = next_month - datetime.timedelta(days=next_month.day)

        query = """SELECT cu.id,
                          cu.archived,
                          cu.thumbsmall,
                          cu.birthday,
                          cu.display_name,
                          cu.date_of_birth,
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
                   ORDER BY ssu.Name,
                            cu.display_name
                            DESC""".format(firstdaythismonth=firstdaythismonth,
                                           lastdaythismonth=lastdaythismonth)
        return query


    def get_class_revenue_summary(self, clsID, date, quick_stats=True):
        """
        :param subscription_quick_stats: Boolean - use db.school_subscriptions.QuickStatsAmount or not
        :return:
        """
        from os_class import Class

        cls = Class(clsID, date)
        class_prices = cls.get_prices()

        data = {
            'subscriptions': {},
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
            'total': {
                'count': 0,
                'amount': 0
            }
        }

        rows = self.get_class_revenue_rows(clsID, date)
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

                data['total']['amount'] += amount

            elif row.classes_attendance.AttendanceType == 1:
                # Trial
                if row.classes_attendance.CustomerMembership:
                    data['trial']['membership']['count'] += 1
                    data['total']['amount'] += data['trial']['membership']['amount']
                else:
                    data['trial']['no_membership']['count'] += 1
                    data['total']['amount'] += data['trial']['no_membership']['amount']

            elif row.classes_attendance.AttendanceType == 2:
                # Dropin
                if row.classes_attendance.CustomerMembership:
                    data['dropin']['membership']['count'] += 1
                    data['total']['amount'] += data['dropin']['membership']['amount']
                else:
                    data['dropin']['no_membership']['count'] += 1
                    data['total']['amount'] += data['dropin']['no_membership']['amount']

            elif row.classes_attendance.AttendanceType == 3:
                # Class card
                name = row.school_classcards.Name
                if not row.school_classcards.Unlimited:
                    amount = row.school_classcards.Price / row.school_classcards.Classes
                else:
                    revenue = get_class_revenue_classcard(row)
                    amount = revenue['total_revenue_in_vat']
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

            elif row.classes_attendance.AttendanceType == 4:
                # Complementary
                data['complementary']['count'] += 1

            data['total']['count'] += 1


        return data


    def get_class_revenue_summary_formatted(self, clsID, date, quick_stats=True):
        """
        Format output from self.get_class_revenue_summary
        :param clsID: db.classes.id
        :param date: datetime.date
        :param quickstats: boolean
        :return: html table
        """
        from os_class import Class

        T = current.T
        represent_float_as_amount = current.globalenv['represent_float_as_amount']

        revenue = self.get_class_revenue_summary(
            clsID=clsID,
            date=date,
            quick_stats=quick_stats
        )

        header = THEAD(TR(
            TH(T('Type')),
            TH(T('Amount')),
            TH(T('Attendance count')),
            TH(T('Total')),
        ))

        trial_without_membership = TR(
            TD(T('Trial without membership')),
            TD(represent_float_as_amount(revenue['trial']['no_membership']['amount'])),
            TD(revenue['trial']['no_membership']['count']),
            TD(represent_float_as_amount(
                revenue['trial']['no_membership']['amount'] * revenue['trial']['no_membership']['count']
            )),
        )

        trial_with_membership =  TR(
            TD(T('Trial with membership')),
            TD(represent_float_as_amount(revenue['trial']['membership']['amount'])),
            TD(revenue['trial']['membership']['count']),
            TD(represent_float_as_amount(
                revenue['trial']['membership']['amount'] * revenue['trial']['membership']['count']
            )),
        )

        dropin_without_membership = TR(
            TD(T('Drop-in without membership')),
            TD(represent_float_as_amount(revenue['dropin']['no_membership']['amount'])),
            TD(revenue['dropin']['no_membership']['count']),
            TD(represent_float_as_amount(
                revenue['dropin']['no_membership']['amount'] * revenue['dropin']['no_membership']['count']
            )),
        )

        dropin_with_membership =  TR(
            TD(T('Drop-in with membership')),
            TD(represent_float_as_amount(revenue['dropin']['membership']['amount'])),
            TD(revenue['dropin']['membership']['count']),
            TD(represent_float_as_amount(
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
                TD(s),
                TD(represent_float_as_amount(amount)),
                TD(count),
                TD(represent_float_as_amount(amount * count))
            ))

        # class cards
        for c in sorted(revenue['classcards']):
            amount = revenue['classcards'][c]['amount']
            count = revenue['classcards'][c]['count']

            table_revenue.append(TR(
                TD(c),
                TD(represent_float_as_amount(amount)),
                TD(count),
                TD(represent_float_as_amount(amount * count))
            ))

        # Complementary
        table_revenue.append(TR(
            TD(T('Complementary')),
            TD(),
            TD(revenue['complementary']['count']),
            TD(),
        ))

        # Total
        footer = TFOOT(TR(
            TH(T('Total')),
            TH(),
            TH(revenue['total']['count']),
            TH(represent_float_as_amount(revenue['total']['amount'])),
        ))

        table_revenue.append(footer)

        ##
        # table total
        ##
        cls = Class(clsID, date)
        teacher_payment = cls.get_teacher_payment()
        if not teacher_payment['error']:
            tp_amount = teacher_payment['data']['ClassRate']
            tp_display = represent_float_as_amount(tp_amount)
        else:
            tp_amount = 0
            tp_display = teacher_payment['data']

        header = THEAD(TR(
            TH(T('Description')),
            TH(T('Amount')),
        ))

        attendance = TR(
            TD(T('Attendance')),
            TD(represent_float_as_amount(revenue['total']['amount']))
        )

        teacher_payment = TR(
            TD(T('Teacher payment')),
            TD(tp_display)
        )

        total = represent_float_as_amount(revenue['total']['amount'] - tp_amount)
        footer = TR(
            TH(T('Total')),
            TH(total)
        )

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


    def get_class_revenue_summary_pdf(self, clsID, date, quick_stats=True):
        """
        :param clsID: db.classes.id
        :param date: datetime.date
        :param quick_stats: bool
        :return: cStringIO object containing PDF file for summary export
        """
        import cStringIO
        import weasyprint

        html = self.get_class_revenue_summary_pdf_template(clsID, date, quick_stats)

        stream = cStringIO.StringIO()
        workshop = weasyprint.HTML(string=html).write_pdf(stream)

        return stream


    def _get_class_revenue_summary_pdf_template(self, clsID, date, quick_stats=True):
        """
            Print friendly display of a Workshop
        """
        #TODO: import Class and get name

        get_sys_property = current.globalenv['get_sys_property']
        response = current.response

        template = get_sys_property('branding_default_template_class_revenue') or 'class_revenue/default.html'
        template_file = 'templates/' + template

        tables = self.get_class_revenue_summary_formatted(clsID, date)

        html = response.render(template_file,
                               dict(title=cls.get_name()
                                    table_revenue=tables['table_revenue'],
                                    table_total=tables['table_total'],
                                    logo=self._get_class_revenue_summary_pdf_template_get_logo()))

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


    def get_class_revenue_rows(self, clsID, date):
        """
        :param clsID: db.classes.id
        :param date: Class date
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
                (db.classes_attendance.ClassDate == date) & \
                (db.classes_attendance.BookingStatus != 'cancelled')
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
        from os_invoice import Invoice

        ccdID = row.classes_attendance.customers_classcards_id
        classcard = CustomerClasscard(ccdID)

        query = (db.invoices_customers_classcards.customers_classcards_id == ccdID)
        rows = db(query).select(db.invoices_customers_classcards.ALL)

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

