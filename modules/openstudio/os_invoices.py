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
        from os_teacher import Teacher
        from os_teachers import Teachers

        # Get list of teachers
        teachers = Teachers()
        teacher_classes = teachers.get_teachers_list_classes_in_month(year, month)

        #print teacher_classes

        for teID in teacher_classes:
            teacher = Teacher(teID)
            default_rate = teacher.get_payment_fixed_rate_default()
            class_rates = teacher.get_payment_fixed_rate_classes_dict()

            print default_rate

            if not default_rate and not class_rates:
                continue # No rates set, not enough data to create invoice

            print class_rates

            for classes in teacher_classes[teID]:
                print classes
                for row in classes:
                    print row
                    print row.classes.id
                # Check if id in class rates

            print teID
            print '#####################'






        # Get classes
        # Get default rate
        # for each class:
            # If specific rate:
                # pay specific rate
            # else:
                # pay default rate
