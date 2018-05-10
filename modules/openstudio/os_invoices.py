# -*- coding: utf-8 -*-
"""
    This file holds OpenStudio Invoices class
"""

from gluon import *

class Invoices:
    """
        This class holds functions related to multiple invoices
    """
    def batch_generate_teachers_invoices(self, year, month):
        """
        :return: Int - number of generated invoices
        """
        from general_helpers import NRtoMonth
        from os_teacher import Teacher
        from os_teachers import Teachers
        from openstudio import Invoice

        db = current.globalenv['db']
        T = current.T

        # Get list of teachers
        teachers = Teachers()
        result = teachers.get_teachers_list_classes_in_month(year, month)

        #print teacher_classes
        invoices_created = 0

        for teID in result:
            teacher_classes = result[teID]['classes']
            number_of_classes = result[teID]['classes_count']
            if not number_of_classes:
                continue

            teacher = Teacher(teID)
            default_rate = teacher.get_payment_fixed_rate_default()

            if not default_rate:
                continue # No default rate, not enough data to create invoice

            # Check if we have an invoice already, if so, skip
            query = (db.invoices_customers.auth_customer_id == teID) & \
                    (db.invoices.TeacherPaymentMonth == month) & \
                    (db.invoices.TeacherPaymentYear == year) & \
                    (db.invoices_customers.invoices_id == db.invoices.id)

            if db(query).count():
                continue

            # Create invoice
            invoices_created += 1
            igpt = db.invoices_groups_product_types(ProductType='teacher_payments')
            iID = db.invoices.insert(
                invoices_groups_id=igpt.invoices_groups_id,
                TeacherPayment=True,
                TeacherPaymentMonth=month,
                TeacherPaymentYear=year,
                Description=T('Classes') + ' ' + NRtoMonth(month) + ' ' + unicode(year),
                Status='sent'
            )

            invoice = Invoice(iID)
            invoice.link_to_customer(teID)

            for date, rows in teacher_classes.iteritems():
                for row in rows:
                    invoice.item_add_teacher_class_credit_payment(
                        row.classes.id,
                        date
                    )

        return invoices_created
