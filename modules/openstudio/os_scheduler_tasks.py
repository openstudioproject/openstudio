# -*- coding: utf-8 -*-

"""
The OsScheduler class will hold all tasks that should run in the background (for now)
When it gets bit, let's split it into multiple files.

Naming:

Roughly stick to:
db_table.action.info_about_what_task_does

"""

import datetime
from gluon import *

class OsSchedulerTasks:

    def customers_subscriptions_create_invoices_for_month(self, year, month, description):
        """
            Actually create invoices for subscriptions for a given month
        """
        from general_helpers import get_last_day_month
        from os_invoice import Invoice

        db = current.db
        DATE_FORMAT = current.DATE_FORMAT

        year = int(year)
        month = int(month)

        firstdaythismonth = datetime.date(year, month, 1)
        lastdaythismonth  = get_last_day_month(firstdaythismonth)

        csap = db.customers_subscriptions_alt_prices

        fields = [
            db.customers_subscriptions.id,
            db.customers_subscriptions.auth_customer_id,
            db.customers_subscriptions.school_subscriptions_id,
            db.customers_subscriptions.Startdate,
            db.customers_subscriptions.Enddate,
            db.customers_subscriptions.payment_methods_id,
            db.school_subscriptions.Name,
            db.school_subscriptions_price.Price,
            db.school_subscriptions_price.tax_rates_id,
            db.tax_rates.Percentage,
            db.customers_subscriptions_paused.id,
            db.invoices.id,
            csap.id,
            csap.Amount,
            csap.Description
        ]

        rows = db.executesql(
            """
                SELECT cs.id,
                       cs.auth_customer_id,
                       cs.school_subscriptions_id,
                       cs.Startdate,
                       cs.Enddate,
                       cs.payment_methods_id,
                       ssu.Name,
                       ssp.Price,
                       ssp.tax_rates_id,
                       tr.Percentage,
                       csp.id,
                       i.invoices_id,
                       csap.id,
                       csap.Amount,
                       csap.Description
                FROM customers_subscriptions cs
                LEFT JOIN auth_user au
                 ON au.id = cs.auth_customer_id
                LEFT JOIN school_subscriptions ssu
                 ON cs.school_subscriptions_id = ssu.id
                LEFT JOIN
                 (SELECT id,
                         school_subscriptions_id,
                         Startdate,
                         Enddate,
                         Price,
                         tax_rates_id
                  FROM school_subscriptions_price
                  WHERE Startdate <= '{firstdaythismonth}' AND
                        (Enddate >= '{firstdaythismonth}' OR Enddate IS NULL)) ssp
                 ON ssp.school_subscriptions_id = ssu.id
                LEFT JOIN tax_rates tr
                 ON ssp.tax_rates_id = tr.id
                LEFT JOIN
                 (SELECT id,
                         customers_subscriptions_id
                  FROM customers_subscriptions_paused
                  WHERE Startdate <= '{firstdaythismonth}' AND
                        (Enddate >= '{firstdaythismonth}' OR Enddate IS NULL)) csp
                 ON cs.id = csp.customers_subscriptions_id
                LEFT JOIN
                 (SELECT ics.id,
                         ics.invoices_id,
                         ics.customers_subscriptions_id
                  FROM invoices_customers_subscriptions ics
                  LEFT JOIN invoices on ics.invoices_id = invoices.id
                  WHERE invoices.SubscriptionYear = {year} AND invoices.SubscriptionMonth = {month}) i
                 ON i.customers_subscriptions_id = cs.id
                LEFT JOIN
                 (SELECT id,
                         customers_subscriptions_id,
                         Amount,
                         Description
                  FROM customers_subscriptions_alt_prices
                  WHERE SubscriptionYear = {year} AND SubscriptionMonth = {month}) csap
                 ON csap.customers_subscriptions_id = cs.id
                WHERE cs.Startdate <= '{lastdaythismonth}' AND
                      (cs.Enddate >= '{firstdaythismonth}' OR cs.Enddate IS NULL) AND
                      ssp.Price <> 0 AND
                      ssp.Price IS NOT NULL AND
                      au.trashed = 'F'
            """.format(firstdaythismonth=firstdaythismonth,
                       lastdaythismonth =lastdaythismonth,
                       year=year,
                       month=month),
          fields=fields)

        igpt = db.invoices_groups_product_types(ProductType = 'subscription')
        igID = igpt.invoices_groups_id


        # Alright, time to create some invoices
        for row in rows:
            if row.invoices.id:
                # an invoice already exists, do nothing
                continue
            if row.customers_subscriptions_paused.id:
                # the subscription is paused, don't create an invoice
                continue
            if row.customers_subscriptions_alt_prices.Amount == 0:
                # Don't create an invoice if there's an alt price for the subscription with amount 0.
                continue

            csID = row.customers_subscriptions.id
            cuID = row.customers_subscriptions.auth_customer_id
            pmID = row.customers_subscriptions.payment_methods_id

            subscr_name = row.school_subscriptions.Name

            if row.customers_subscriptions_alt_prices.Description:
                inv_description = row.customers_subscriptions_alt_prices.Description
            else:
                inv_description = description

            if row.customers_subscriptions.Startdate > firstdaythismonth:
                period_begin = row.customers_subscriptions.Startdate
            else:
                period_begin = firstdaythismonth

            period_end = lastdaythismonth
            if row.customers_subscriptions.Enddate:
                if row.customers_subscriptions.Enddate >= firstdaythismonth and \
                   row.customers_subscriptions.Enddate < lastdaythismonth:
                    period_end = row.customers_subscriptions.Enddate


            item_description = period_begin.strftime(DATE_FORMAT) + ' - ' + \
                               period_end.strftime(DATE_FORMAT)

            iID = db.invoices.insert(
                invoices_groups_id = igID,
                payment_methods_id = pmID,
                SubscriptionYear = year,
                SubscriptionMonth = month,
                Description = inv_description,
                Status = 'sent'
            )

            # create object to set Invoice# and due date
            invoice = Invoice(iID)
            invoice.link_to_customer(cuID)
            invoice.link_to_customer_subscription(csID)
            invoice.item_add_subscription(year, month)
            invoice.set_amounts()

        ##
        # For scheduled tasks db connection has to be committed manually
        ##
        db.commit()
