# -*- coding: utf-8 -*-

import datetime

from gluon import *


class Class:
    """
        Class that gathers useful functions for a class in OpenStudio
    """
    def __init__(self, clsID, date):
        self.clsID = clsID
        self.date = date

        db = current.db
        self.cls = db.classes(self.clsID)


    def get_name(self, pretty_date=False):
        """
            Returns class name formatted for general use
        """
        db = current.db
        T = current.T
        TIME_FORMAT = current.TIME_FORMAT
        DATE_FORMAT = current.DATE_FORMAT

        if pretty_date:
            date = self.date.strftime('%d %B %Y')
        else:
            date = self.date.strftime(DATE_FORMAT)


        record = self.cls
        location = db.school_locations[record.school_locations_id].Name
        classtype = db.school_classtypes[record.school_classtypes_id].Name
        class_name =  date + ' ' + \
                      record.Starttime.strftime(TIME_FORMAT) + ' - ' + \
                      classtype + ' ' + location

        return class_name


    def get_classtype_name(self):
        db = current.db
        return db.school_classtypes[self.cls.school_classtypes_id].Name


    def get_location_name(self):
        db = current.db
        return db.school_locations[self.cls.school_locations_id].Name


    def get_name_shop(self):
        """
            Returns class name formatted for use in customer profile and shop
        """
        db = current.db
        T = current.T
        TIME_FORMAT = current.TIME_FORMAT

        record = self.cls
        location = db.school_locations[record.school_locations_id].Name
        classtype = db.school_classtypes[record.school_classtypes_id].Name
        class_name =  self.date.strftime('%d %B %Y') + ' ' + '<br><small>' + \
                      record.Starttime.strftime(TIME_FORMAT) + ' - ' + \
                      record.Endtime.strftime(TIME_FORMAT) + ' ' + \
                      classtype + ' ' + \
                      T('in') + ' ' + location + '</small>'

        return class_name


    def get_info(self):
        """
        :return: dict containing class name values
        """
        db = current.db
        T = current.T
        TIME_FORMAT = current.TIME_FORMAT

        return dict(
            location = db.school_locations[self.cls.school_locations_id].Name,
            classtype = db.school_classtypes[self.cls.school_classtypes_id].Name,
            date = self.date.strftime('%d %B %Y'),
            start = self.cls.Starttime.strftime(TIME_FORMAT),
            end = self.cls.Endtime.strftime(TIME_FORMAT),
            teachers = self.get_teachers()
        )


    def get_prices(self):
        """
            Returns the price for a class
        """
        db = current.db

        query = (db.classes_price.classes_id == self.clsID) & \
                (db.classes_price.Startdate <= self.date) & \
                ((db.classes_price.Enddate >= self.date) |
                 (db.classes_price.Enddate == None))
        prices = db(query).select(db.classes_price.ALL,
                                  orderby=db.classes_price.Startdate)

        if prices:
            prices = prices.first()
            dropin = prices.Dropin or 0
            trial  = prices.Trial or 0
            dropin_membership = prices.DropinMembership or 0
            trial_membership = prices.TrialMembership or 0
            dropin_glaccount = prices.accounting_glaccounts_id_dropin
            trial_glaccount = prices.accounting_glaccounts_id_trial
            dropin_costcenter = prices.accounting_costcenters_id_dropin
            trial_costcenter = prices.accounting_costcenters_id_trial
            school_memberships_id = prices.school_memberships_id

            trial_tax = db.tax_rates(prices.tax_rates_id_trial)
            dropin_tax = db.tax_rates(prices.tax_rates_id_dropin)
            trial_tax_membership = db.tax_rates(prices.tax_rates_id_trial_membership)
            dropin_tax_membership = db.tax_rates(prices.tax_rates_id_dropin_membership)

            try:
                trial_tax_rates_id    = trial_tax.id
                dropin_tax_rates_id   = dropin_tax.id
                trial_tax_percentage  = trial_tax.Percentage
                dropin_tax_percentage = dropin_tax.Percentage
            except AttributeError:
                trial_tax_rates_id    = None
                dropin_tax_rates_id   = None
                trial_tax_percentage  = None
                dropin_tax_percentage = None

            try:
                trial_tax_rates_id_membership = trial_tax_membership.id
                dropin_tax_rates_id_membership = dropin_tax_membership.id
                trial_tax_percentage_membership = trial_tax_membership.Percentage
                dropin_tax_percentage_membership = dropin_tax_membership.Percentage
            except AttributeError:
                trial_tax_rates_id_membership = None
                dropin_tax_rates_id_membership = None
                trial_tax_percentage_membership = None
                dropin_tax_percentage_membership = None

        else:
            # Set default values
            dropin = 0
            trial  = 0
            trial_tax_rates_id    = None
            dropin_tax_rates_id   = None
            trial_tax_percentage  = None
            dropin_tax_percentage = None
            dropin_membership = 0
            trial_membership = 0
            trial_tax_rates_id_membership = None
            dropin_tax_rates_id_membership = None
            trial_tax_percentage_membership = None
            dropin_tax_percentage_membership = None
            dropin_glaccount = None
            trial_glaccount = None
            dropin_costcenter = None
            trial_costcenter = None
            school_memberships_id = None


        return dict(
            trial  = trial,
            dropin = dropin,
            trial_tax_rates_id = trial_tax_rates_id,
            dropin_tax_rates_id = dropin_tax_rates_id,
            trial_tax_percentage = trial_tax_percentage,
            dropin_tax_percentage = dropin_tax_percentage,
            trial_membership = trial_membership,
            dropin_membership = dropin_membership,
            trial_tax_rates_id_membership = trial_tax_rates_id_membership,
            dropin_tax_rates_id_membership = dropin_tax_rates_id_membership,
            trial_tax_percentage_membership = trial_tax_percentage_membership,
            dropin_tax_percentage_membership = dropin_tax_percentage_membership,
            dropin_glaccount = dropin_glaccount,
            trial_glaccount = trial_glaccount,
            dropin_costcenter = dropin_costcenter,
            trial_costcenter = trial_costcenter,
            school_memberships_id = school_memberships_id
        )


    def get_prices_customer(self, cuID, force_membership_price=False):
        """
            Returns the price for a class
            :param cuID: db.auth_user.id
            :return: dict of class prices
        """
        from openstudio.os_customer import Customer

        db = current.db
        customer = Customer(cuID)

        prices = self.get_prices()
        has_membership = False
        if prices['school_memberships_id']:
            has_membership = customer.has_given_membership_on_date(
                prices['school_memberships_id'],
                self.date
            )

        trial = prices['trial']
        trial_tax = db.tax_rates(prices['trial_tax_rates_id'])
        dropin = prices['dropin']
        dropin_tax = db.tax_rates(prices['dropin_tax_rates_id'])
        dropin_tax_rates_id = prices['dropin_tax_rates_id']
        dropin_tax_percentage = prices['dropin_tax_percentage']
        trial_tax_rates_id = prices['trial_tax_rates_id']
        trial_tax_percentage = prices['trial_tax_percentage']
        dropin_glaccount = prices['dropin_glaccount']
        trial_glaccount = prices['trial_glaccount']
        dropin_costcenter = prices['dropin_costcenter']
        trial_costcenter = prices['trial_costcenter']

        if prices['dropin_membership'] and (has_membership or force_membership_price):
            dropin = prices['dropin_membership']
            dropin_tax = db.tax_rates(prices['dropin_tax_rates_id_membership'])
            
        if prices['trial_membership'] and (has_membership or force_membership_price):
            trial = prices['trial_membership']
            trial_tax = db.tax_rates(prices['trial_tax_rates_id_membership'])

        try:
            dropin_tax_rates_id = dropin_tax.id
            dropin_tax_percentage = dropin_tax.Percentage
        except AttributeError:
            pass

        try:
            trial_tax_rates_id = trial_tax.id
            trial_tax_percentage = trial_tax.Percentage
        except AttributeError:
            pass

        return dict(
            trial = trial,
            dropin = dropin,
            trial_tax_rates_id = trial_tax_rates_id,
            dropin_tax_rates_id = dropin_tax_rates_id,
            trial_tax_percentage = trial_tax_percentage,
            dropin_tax_percentage = dropin_tax_percentage,
            dropin_glaccount = dropin_glaccount,
            dropin_costcenter = dropin_costcenter,
            trial_glaccount = trial_glaccount,
            trial_costcenter = trial_costcenter
        )


    def get_full(self, only_count_status=None):
        """
            Check whether or not this class is full
        """
        db = current.db
        spaces = self.cls.Maxstudents

        query = (db.classes_attendance.classes_id == self.clsID) & \
                (db.classes_attendance.ClassDate == self.date)
        if only_count_status:
            query &= (db.classes_attendance.BookingStatus == only_count_status)
        else:
            query &= (db.classes_attendance.BookingStatus != 'cancelled')

        filled = db(query).count()
        full = True if filled >= spaces else False

        return full


    def get_full_bookings_shop(self):
        """
            Check whether there are spaces left for online bookings
        """
        db = current.db

        spaces = self.cls.Maxstudents - self.cls.WalkInSpaces
        query = (db.classes_attendance.classes_id == self.clsID) & \
                (db.classes_attendance.ClassDate == self.date) & \
                (db.classes_attendance.online_booking == True) & \
                (db.classes_attendance.BookingStatus != 'cancelled')
        filled = db(query).count()

        full = True if filled >= spaces else False

        return full


    def get_invoice_order_description(self, attendance_type):
        """        
            :return: string with a description of the class 
        """
        DATE_FORMAT = current.DATE_FORMAT
        TIME_FORMAT = current.TIME_FORMAT

        db = current.db
        T  = current.T

        prices = self.get_prices()
        if attendance_type == 1:
            price = prices['trial']
            tax_rates_id = prices['trial_tax_rates_id']
            at = T('Trial')
        elif attendance_type == 2:
            price = prices['dropin']
            tax_rates_id = prices['dropin_tax_rates_id']
            at = T('Drop in')


        location =  db.school_locations(self.cls.school_locations_id)
        classtype = db.school_classtypes(self.cls.school_classtypes_id)

        description = self.date.strftime(DATE_FORMAT) + ' ' + \
                      self.cls.Starttime.strftime(TIME_FORMAT) + ' ' + \
                      classtype.Name + ' ' + \
                      location.Name + ' ' + \
                      '(' + at + ')'

        return description


    def add_to_shoppingcart(self, cuID, attendance_type=2):
        """
            Add a workshop product to the shopping cart of a customer
            attendance_type can be 1 for trial class or 2 for drop in class
        """
        db = current.db

        db.customers_shoppingcart.insert(
            auth_customer_id = cuID,
            classes_id = self.clsID,
            ClassDate = self.date,
            AttendanceType = attendance_type
        )


    def is_on_correct_weekday(self):
        """
            Checks if self.date.isoweekday() == self.cls.Week_day
        """
        if self.date.isoweekday() == self.cls.Week_day:
            return True
        else:
            return False


    def is_past(self):
        """
            Return True if NOW_LOCAL > Class start else return False
        """
        import pytz

        db = current.db
        now = current.NOW_LOCAL
        TIMEZONE = current.TIMEZONE

        cls_time = self.cls.Starttime

        class_dt = datetime.datetime(year=self.date.year,
                                     month=self.date.month,
                                     day=self.date.day,
                                     hour=cls_time.hour,
                                     minute=cls_time.minute)
        # localize the class datetime so it can be compared to now
        # class_dt = pytz.utc.localize(class_dt)
        class_dt = pytz.timezone(TIMEZONE).localize(class_dt)

        if class_dt < now:
            return True
        else:
            return False


    def is_cancelled(self):
        """
            Return True if the class is cancelled, else return False
        """
        db = current.db
        query = (db.classes_otc.classes_id == self.clsID) & \
                (db.classes_otc.ClassDate == self.date) & \
                (db.classes_otc.Status == 'cancelled')

        cancelled = True if db(query).count() else False
        return cancelled


    def is_holiday(self):
        """
            Return True if the class is within a holiday, else return False
        """
        db = current.db

        # Query school_holidays table to see if there's a holiday for this location
        left = [db.school_holidays_locations.on(db.school_holidays.id ==
                                                db.school_holidays_locations.school_holidays_id)]
        query = (db.school_holidays.Startdate <= self.date) & \
                (db.school_holidays.Enddate >= self.date) & \
                (db.school_holidays_locations.school_locations_id == self.cls.school_locations_id)

        rows = db(query).select(db.school_holidays.id,
                                left=left)

        holiday = True if len(rows) else False
        return holiday


    def is_taking_place(self):
        """
             Check if the class is not in past, cancelled or in a holiday
             Return True if not in past, cancelled or in holiday, else return False
        """
        correct_weekday = self.is_on_correct_weekday()
        past = self.is_past()
        cancelled = self.is_cancelled()
        holiday = self.is_holiday()

        if not past and not cancelled and not holiday and correct_weekday:
            return True
        else:
            return False


    def is_booked_by_customer(self, cuID):
        """
        :param cuID: db.auth_user.id
        :return: Boolean

        Check if the class is booked by this customer or not
        """
        db = current.db

        query = ((db.classes_attendance.BookingStatus == 'booked') |
                 (db.classes_attendance.BookingStatus == 'attending')) & \
                (db.classes_attendance.classes_id == self.clsID) & \
                (db.classes_attendance.ClassDate == self.date) & \
                (db.classes_attendance.auth_customer_id == cuID)

        rows = db(query).select(db.classes_attendance.id)
        if len(rows) > 0:
            return True
        else:
            return False


    def has_recurring_reservation_spaces(self):
        """
        Check whether a class has space for more recurring reservations
        :param date: datetime.date
        :return: Boolean
        """
        db = current.db

        spaces = self.cls.MaxReservationsRecurring

        query = (db.classes_reservation.classes_id == self.clsID) & \
                (db.classes_reservation.ResType == 'recurring') & \
                (db.classes_reservation.Startdate <= self.date) & \
                ((db.classes_reservation.Enddate >= self.date) |
                 (db.classes_reservation.Enddate == None))

        reservations = db(query).count()

        if reservations >= spaces:
            return False
        else:
            return True


    def get_trialclass_allowed_in_shop(self):
        """
        Check whether trial classes in the shop are allowed or not
        :return: Boolean
        """
        if self.cls.AllowShopTrial:
            return True
        else:
            return False


    def get_attendance_count(self):
        """
        :return: integer ; count of customers attending this class
        """
        db = current.db

        query = (db.classes_attendance.classes_id == self.clsID) & \
                (db.classes_attendance.ClassDate == self.date) & \
                (db.classes_attendance.BookingStatus != 'cancelled')

        return db(query).count()


    def get_attendance_count_paying_customers(self):
        """
        Return attendance count of paying customers

        - No subscription of type "Staff"
        - No complementary
        :return: attendance count of paying customers
        """
        db = current.db

        left = [
            db.customers_subscriptions.on(
                db.classes_attendance.customers_subscriptions_id ==
                db.customers_subscriptions.id
            ),
            db.school_subscriptions.on(
                db.customers_subscriptions.school_subscriptions_id ==
                db.school_subscriptions.id
            )
        ]

        query = (db.classes_attendance.classes_id == self.clsID) & \
                (db.classes_attendance.ClassDate == self.date) & \
                (db.classes_attendance.BookingStatus != 'cancelled') & \
                ((db.classes_attendance.AttendanceType.belongs([1, 2, 3, 6])) |
                 (db.classes_attendance.AttendanceType == None)) & \
                ((db.school_subscriptions.StaffSubscription == False) |
                 (db.school_subscriptions.StaffSubscription == None))

        rows = db(query).select(
            db.classes_attendance.id,
            db.school_subscriptions.id,
            left=left
        )

        return len(rows)


    def get_teachers(self):
        """
        Teachers for class
        :return:
        """
        T = current.T
        db = current.db

        error = False
        message = ''
        teacher = ''
        teacher2 = ''

        query = (db.classes_teachers.classes_id == self.clsID) & \
                ((db.classes_teachers.Startdate <= self.date) &
                 ((db.classes_teachers.Enddate >= self.date) |
                  (db.classes_teachers.Enddate == None)))
        rows = db(query).select(db.classes_teachers.ALL)

        teacher_sub = False
        teacher2_sub = False

        try:
            teachers = rows.first()

            cotc = db.classes_otc(
                classes_id = self.clsID,
                ClassDate = self.date
            )

            teacher = db.auth_user(teachers.auth_teacher_id)
            if cotc:
                if cotc.auth_teacher_id:
                    teacher = db.auth_user(cotc.auth_teacher_id)
                    teacher_sub = True

            teacher2 = teacher2 = db.auth_user(teachers.auth_teacher_id2)
            if cotc:
                if cotc.auth_teacher_id2:
                    teacher2 = db.auth_user(cotc.auth_teacher_id2)
                    teacher2_sub = True

        except AttributeError:
            # No teacher(s) found for this date
            error = True
            message = T("No teachers found for this date (") + str(self.date) + ")"

        return dict(
            error = error,
            message = message,
            teacher = teacher,
            teacher_sub = teacher_sub,
            teacher2 = teacher2,
            teacher2_sub = teacher2_sub
        )


    def get_regular_teacher_ids(self):
        """
        Teachers for class
        :return:
        """
        T = current.T
        db = current.db

        error = False
        message = ''
        auth_teacher_id = None
        auth_teacher_id2 = None

        query = (db.classes_teachers.classes_id == self.clsID) & \
                ((db.classes_teachers.Startdate <= self.date) &
                 ((db.classes_teachers.Enddate >= self.date) |
                  (db.classes_teachers.Enddate == None)))
        rows = db(query).select(db.classes_teachers.ALL)

        try:
            row = rows.first()
            auth_teacher_id = row.auth_teacher_id
            auth_teacher_id2 = row.auth_teacher_id2


        except AttributeError:
            # No teacher(s) found for this date
            error = True
            message = T("No teachers found for this date (") + str(self.date) + ")"

        return dict(
            error = error,
            message = message,
            auth_teacher_id = auth_teacher_id,
            auth_teacher_id2 = auth_teacher_id2
        )



    def get_teacher_payment(self):
        """
        Returns amount excl. VAT
        :return: { amount: float, tax_rates_id: db.tax_rates.id }
        """
        from .os_teacher import Teacher

        T = current.T
        db = current.db

        get_sys_property = current.globalenv['get_sys_property']

        tprt = get_sys_property('TeacherPaymentRateType')
        attendance_count = self.get_attendance_count()

        # Check if we have a payment, if not insert it with Status 'not_verified"
        tpc = db.teachers_payment_classes(
            classes_id = self.clsID,
            ClassDate = self.date
        )

        error = False
        data = ''

        teachers = self.get_teachers()
        if teachers['error']:
            error = True
            data = teachers['message']
        elif not attendance_count:
            error = True
            data = T("No customers attending this class")
        else:
            teacher_id = teachers['teacher'].id
            teacher = Teacher(teacher_id)

            #print teacher_id

            if tprt == 'fixed':
                # Get rate for this teacher
                default_rate = teacher.get_payment_fixed_rate_default()

                if not default_rate:
                    error = True
                    data = T("No default rate defined for this teacher")
                    # No default rate, not enough data to process

                else:
                    default_rates = teacher.get_payment_fixed_rate_default()
                    class_rates = teacher.get_payment_fixed_rate_classes_dict()

                    if not default_rates and not class_rates:
                        return None  # No rates set, not enough data to create invoice item

                    default_rate = default_rates.first()
                    rate = default_rate.ClassRate
                    tax_rates_id = default_rate.tax_rates_id

                    # Set price and tax rate
                    try:
                        class_prices = class_rates.get(int(self.clsID), False)
                        if class_prices:
                            rate = class_prices.ClassRate
                            tax_rates_id = class_prices.tax_rates_id
                    except (AttributeError, KeyError):
                        pass

                    if not tpc and rate:
                        tpcID = db.teachers_payment_classes.insert(
                            classes_id = self.clsID,
                            ClassDate = self.date,
                            auth_teacher_id = teacher_id,
                            Status = 'not_verified',
                            AttendanceCount = attendance_count,
                            ClassRate = rate,
                            RateType = 'fixed',
                            tax_rates_id = tax_rates_id,
                        )
                        tpc = db.teachers_payment_classes(tpcID)

                    elif tpc and rate:
                        tpc.AttendanceCount = attendance_count
                        tpc.ClassRate = rate
                        tpc.auth_teacher_id = teacher_id
                        tpc.teachers_payment_classes_list_id = None
                        tpc.RateType = 'fixed'
                        tpc.tax_rates_id = tax_rates_id
                        tpc.update_record()

                    self._get_teacher_payment_set_travel_allowance(tpc)
                    data = tpc


            elif tprt == 'attendance':
                # Get list for class type
                # print("attendance")
                attendance_count_paying_customers = self.get_attendance_count_paying_customers()
                cltID = self.cls.school_classtypes_id
                tpalst = db.teachers_payment_attendance_lists_school_classtypes(
                    school_classtypes_id=cltID
                )

                if tpalst:
                    # print("list found")
                    list_id = tpalst.teachers_payment_attendance_lists_id
                    list = db.teachers_payment_attendance_lists(1)
                    tax_rates_id = list.tax_rates_id

                    query = (db.teachers_payment_attendance_lists_rates.teachers_payment_attendance_lists_id == list_id) & \
                            (db.teachers_payment_attendance_lists_rates.AttendanceCount == attendance_count_paying_customers)

                    row = db(query).select(db.teachers_payment_attendance_lists_rates.Rate)

                    # print(row)

                    try:
                        rate = row.first().Rate
                    except AttributeError:
                        rate = 0

                    if not rate:
                        data = T("Rate is 0, unable to process payment")
                        error = True

                    if not tpc and rate:
                        tpcID = db.teachers_payment_classes.insert(
                            classes_id = self.clsID,
                            ClassDate = self.date,
                            auth_teacher_id = teacher_id,
                            Status = 'not_verified',
                            AttendanceCount = attendance_count,
                            ClassRate = rate,
                            RateType = 'attendance',
                            teachers_payment_attendance_list_id = list.id,
                            tax_rates_id = tax_rates_id,
                        )
                        tpc = db.teachers_payment_classes(tpcID)

                    elif tpc and rate:
                        tpc.AttendanceCount = attendance_count
                        tpc.ClassRate = rate
                        tpc.auth_teacher_id = teacher_id
                        tpc.RateType = 'attendance'
                        tpc.teachers_payment_attendance_list_id = list.id
                        tpc.tax_rates_id = tax_rates_id
                        tpc.update_record()
                        

                    if not error:
                        self._get_teacher_payment_set_travel_allowance(tpc)
                        data = tpc
                else:
                    data = T('No payment list defined for this class type')
                    error = True

        return {
            'data': data,
            'error': error
        }


    def _get_teacher_payment_set_travel_allowance(self, tpc_row):
        """
        set db.teachers_payment_classes travel allowance
        """
        from .os_class_schedule import ClassSchedule
        from .os_teacher import Teacher

        db = current.db

        if tpc_row and not tpc_row.Status == 'processed':
            cs = ClassSchedule(self.date,
                               filter_id_teacher=tpc_row.auth_teacher_id,
                               filter_id_school_location=self.cls.school_locations_id)

            class_start = datetime.datetime(
                self.date.year,
                self.date.month,
                self.date.day,
                self.cls.Starttime.hour,
                self.cls.Starttime.minute
            )

            # Add travel allowance if no class is found that ended 30 minutes before start of this class
            class_found = False
            rows = cs.get_day_rows()
            for row in rows:
                if not int(row.classes.id) == int(self.clsID):
                    checked_class_start = datetime.datetime(
                        self.date.year,
                        self.date.month,
                        self.date.day,
                        row.classes.Endtime.hour,
                        row.classes.Endtime.minute
                    )

                    checked_class_end = datetime.datetime(
                        self.date.year,
                        self.date.month,
                        self.date.day,
                        row.classes.Endtime.hour,
                        row.classes.Endtime.minute
                    )

                    consecutive = (
                            (checked_class_end + datetime.timedelta(minutes=30)) >= class_start and
                            checked_class_end <= class_start

                    )

                    if consecutive:
                        class_found = True

            if not class_found:
                # Add travel allowance, there is no class which ends within 30 min in same location
                teacher = Teacher(tpc_row.auth_teacher_id)

                travel_allowance = teacher.get_payment_travel_allowance_location(
                    self.cls.school_locations_id
                )
                if travel_allowance:
                    tpc_row.TravelAllowance = travel_allowance.TravelAllowance
                    tpc_row.tax_rates_id_travel_allowance = travel_allowance.tax_rates_id
                    tpc_row.update_record()
