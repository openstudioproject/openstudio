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
