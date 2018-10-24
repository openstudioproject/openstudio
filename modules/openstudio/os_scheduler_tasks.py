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

        T = current.T
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

        invoices_created = 0

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

            invoices_created += 1

        ##
        # For scheduled tasks db connection has to be committed manually
        ##
        db.commit()

        return T("Invoices created") + ': ' + unicode(invoices_created)


    def customers_exp_membership_check_subscriptions(self, year, month, description):
        """
            Checks if a subscription exceeds the expiration of a membership. If so it creates a new membership and an invoice for it for the customer
        """
        from general_helpers import get_last_day_month
        from datetime import timedelta
        from os_invoice import Invoice
        from os_school_membership import SchoolMembership
        from os_customer_membership import CustomerMembership

        T = current.T
        db = current.db
        DATE_FORMAT = current.DATE_FORMAT

        # db.test_scheduler_print_data.insert(task_message='task starts')
        # db.commit()

        year = int(year)
        month = int(month)

        firstdaythismonth = datetime.date(year, month, 1)
        lastdaythismonth  = get_last_day_month(firstdaythismonth)

        rows = db().select(db.customers_memberships.ALL,
                           db.customers_subscriptions.ALL,
                           db.school_subscriptions.id,
                           db.school_subscriptions.MembershipRequired,
                           left=(db.customers_subscriptions.on(db.customers_subscriptions.auth_customer_id == db.customers_memberships.auth_customer_id),
                                db.school_subscriptions.on(db.school_subscriptions.id == db.customers_subscriptions.school_subscriptions_id)))
        invoices_created = 0

        for row in rows:
            if row.customers_memberships.Enddate <= lastdaythismonth:

                if row.customers_subscriptions.Enddate > lastdaythismonth:

                    if row.school_subscriptions.MembershipRequired == True:

                        membership = row.customers_memberships.school_memberships_id

                        membership_row = db.school_memberships(id= membership)

                        sm = SchoolMembership(membership)
                        startdate = row.customers_memberships.Enddate + timedelta(days=1)

                        enddate = sm.sell_to_customer_get_enddate(row.customers_memberships.Enddate)
                        cmID = db.customers_memberships.insert(
                            auth_customer_id = row.customers_memberships.auth_customer_id,
                            school_memberships_id= row.customers_memberships.school_memberships_id,
                            Startdate = startdate,
                            Enddate = enddate,
                            payment_methods_id = row.customers_memberships.payment_methods_id
                        )
                        db.commit()
                        cm = CustomerMembership(cmID)
                        cm.set_date_id_and_barcode()
                        invoices_created += 1
                        sm.sell_to_customer_create_invoice(cmID)

                        # # Check if price exists and > 0:
                        # if sm.get_price_on_date(startdate):
                        #     period_start = startdate
                        #     period_end = enddate
                        #
                        #     igpt = db.invoices_groups_product_types(ProductType='membership')
                        #
                        #     iID = db.invoices.insert(
                        #         invoices_groups_id=igpt.invoices_groups_id,
                        #         Description=cm.get_name(),
                        #         MembershipPeriodStart=period_start,
                        #         MembershipPeriodEnd=period_end,
                        #         Status='sent'
                        #     )
                        #
                        #     invoice = Invoice(iID)
                        #     invoice.link_to_customer(cm.row.auth_customer_id)
                        #     invoice.item_add_membership(
                        #         cmID,
                        #         period_start,
                        #         period_end
                        #     )
                        #
                        #     return iID
                        # else:
                        #     return None


        ##
        # For scheduled tasks db connection has to be committed manually
        ##
        db.commit()

        return T("Invoices created") + ': ' + unicode(invoices_created)
