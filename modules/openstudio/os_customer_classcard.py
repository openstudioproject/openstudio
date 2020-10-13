# -*- coding: utf-8 -*-

from gluon import *


class CustomerClasscard:
    """
        Customer classcard
    """

    def __init__(self, ccdID):
        """
            Set some initial values
        """
        db = current.db

        self.ccdID = ccdID
        self.classcard = db.customers_classcards(ccdID)
        self.scdID = self.classcard.school_classcards_id
        self.school_classcard = db.school_classcards(self.scdID)

        self.price = self.school_classcard.Price
        self.name = self.school_classcard.Name
        self.classes = self.school_classcard.Classes
        self.unlimited = self.school_classcard.Unlimited
        self.cuID = self.classcard.auth_customer_id


    def get_name(self):
        """
            Returns name of classcard
        """
        return self.school_classcard.Name


    def get_auth_customer_id(self):
        """
            Returns auth_customer_id
        """
        return self.classcard.auth_customer_id


    def get_tax_rate_percentage(self):
        """
            Returns the tax rate percentage for a card
            Returns None if nothing is set
        """
        db = current.db

        trID = self.school_classcard.tax_rates_id
        if not trID:
            return None

        tax_rate = db.tax_rates(trID)

        return tax_rate.Percentage


    def get_rows_classes_taken(self):
        """
            Returns rows of classes taken on this card
        """
        db = current.db

        fields = [
            db.classes_attendance.id,
            db.classes_attendance.ClassDate,
            db.classes.id,
            db.classes.school_locations_id,
            db.classes.school_classtypes_id,
            db.classes.Starttime
        ]

        orderby_sql = 'clatt.ClassDate'

        query = """
        SELECT clatt.id,
               clatt.ClassDate,
               cla.id,
               CASE WHEN cotc.school_locations_id IS NOT NULL
                    THEN cotc.school_locations_id
                    ELSE cla.school_locations_id
               END AS school_locations_id,
               CASE WHEN cotc.school_classtypes_id IS NOT NULL
                    THEN cotc.school_classtypes_id
                    ELSE cla.school_classtypes_id
               END AS school_classtypes_id,
               CASE WHEN cotc.Starttime IS NOT NULL
                    THEN cotc.Starttime
                    ELSE cla.Starttime
               END AS Starttime
        FROM classes_attendance clatt
        LEFT JOIN classes cla on cla.id = clatt.classes_id
        LEFT JOIN
            ( SELECT id,
                     classes_id,
                     ClassDate,
                     Status,
                     school_locations_id,
                     school_classtypes_id,
                     Starttime,
                     Endtime,
                     auth_teacher_id,
                     teacher_role,
                     auth_teacher_id2,
                     teacher_role2
              FROM classes_otc ) cotc
            ON clatt.classes_id = cotc.classes_id AND clatt.ClassDate = cotc.ClassDate
        WHERE clatt.customers_classcards_id = {ccdID}
        ORDER BY {orderby_sql}
        """.format(orderby_sql=orderby_sql,
                   ccdID=self.ccdID)

        rows = db.executesql(query, fields=fields)

        return rows


    def get_classes_available(self):
        """
        :return: boolean, classes available on card or not
        """
        if self.unlimited:
            return True
        else:
            classes_remaining = self.get_classes_remaining()
            return classes_remaining > 0


    def get_classes_remaining(self):
        """
            :return: Remaining classes
        """
        db = current.db

        if self.unlimited:
            return 'unlimited'

        query = (db.classes_attendance.customers_classcards_id == self.ccdID) & \
                (db.classes_attendance.BookingStatus != 'cancelled')
        used = db(query).count()

        total = self.classes or 0

        return total - used


    def get_classes_remaining_formatted(self):
        """
            :return: Representation of remaining classes
        """
        db = current.db
        T = current.T

        remaining = self.get_classes_remaining()

        if remaining == 'unlimited':
            remaining = T('Unlimited')

        text = T("Classes")
        if remaining == 1:
           text = T("Class")

        return SPAN(str(remaining), ' ', text, ' ', T("remaining"))


    def get_classes_taken(self):
        """

        :return: Count number of classes taken on this card
        """
        db = current.db

        query = (db.classes_attendance.customers_classcards_id == self.ccdID) & \
                (db.classes_attendance.BookingStatus != 'cancelled')

        return db(query).count()


    def set_classes_taken(self):
        """
        :return: Update the number of classes taken
        """
        self.classcard.ClassesTaken = self.get_classes_taken()
        self.classcard.update_record()


    def _get_allowed_classes_format(self, class_ids):
        """
            :param class_ids: list of db.classes.id
            :return: html table
        """
        T = current.T
        db = current.db
        TODAY_LOCAL = current.TODAY_LOCAL

        query = (db.classes.AllowAPI == True) & \
                (db.classes.id.belongs(class_ids)) & \
                (db.classes.Startdate <= TODAY_LOCAL) & \
                ((db.classes.Enddate == None) |
                 (db.classes.Enddate >= TODAY_LOCAL))
        rows = db(query).select(db.classes.ALL,
                                orderby=db.classes.Week_day|db.classes.Starttime|db.classes.school_locations_id)

        header = THEAD(TR(TH(T('Day')),
                          TH(T('Time')),
                          TH(T('Location')),
                          TH(T('Class'))))
        table = TABLE(header, _class='table table-striped table-hover')
        for i, row in enumerate(rows):
            repr_row = list(rows[i:i + 1].render())[0]

            tr = TR(TD(repr_row.Week_day),
                    TD(repr_row.Starttime, ' - ', repr_row.Endtime),
                    TD(repr_row.school_locations_id),
                    TD(repr_row.school_classtypes_id))

            table.append(tr)

        return table


    # def get_allowed_classes_enrollment(self, public_only=True, formatted=False):
    #     """
    #         :return: return: list of db.classes.db that are allowed to be enrolled in using this subscription
    #     """
    #     permissions = self.get_class_permissions(public_only=public_only)
    #     class_ids = []
    #     for clsID in permissions:
    #         try:
    #             if permissions[clsID]['Enroll']:
    #                 class_ids.append(clsID)
    #         except KeyError:
    #             pass
    #
    #     if not formatted:
    #         return class_ids
    #     else:
    #         return self._get_allowed_classes_format(class_ids)


    def get_allowed_classes_booking(self, public_only=True, formatted=False):
        """
            :return: return: list of db.classes.db that are allowed to be booked using this subscription
        """
        permissions = self.get_class_permissions(public_only=public_only)
        class_ids = []
        for clsID in permissions:
            try:
                if permissions[clsID]['ShopBook']:
                    class_ids.append(clsID)
            except KeyError:
                pass


        if not formatted:
            return class_ids
        else:
            return self._get_allowed_classes_format(class_ids)


    def get_allowed_classes_attend(self, public_only=True, formatted=False):
        """
            :return: return list of db.classes that are allowed to be attended using this subscription
        """
        permissions = self.get_class_permissions(public_only=public_only)
        class_ids = []
        for clsID in permissions:
            try:
                if permissions[clsID]['Attend']:
                    class_ids.append(clsID)
            except KeyError:
                pass


        if not formatted:
            return class_ids
        else:
            return self._get_allowed_classes_format(class_ids)


    def _get_class_permissions_format(self, permissions):
        """
            :param permissions: dictionary of class permissions
            :return: html table
        """
        T = current.T
        db = current.db
        os_gui = current.globalenv['os_gui']
        TODAY_LOCAL = current.TODAY_LOCAL

        class_ids = []
        for clsID in permissions:
            class_ids.append(clsID)

        query = (db.classes.AllowAPI == True) & \
                (db.classes.id.belongs(class_ids)) & \
                (db.classes.Startdate <= TODAY_LOCAL) & \
                ((db.classes.Enddate == None) |
                 (db.classes.Enddate >= TODAY_LOCAL))
        rows = db(query).select(db.classes.ALL,
                                orderby=db.classes.Week_day|db.classes.Starttime|db.classes.school_locations_id)

        header = THEAD(TR(TH(T('Day')),
                          TH(T('Time')),
                          TH(T('Location')),
                          TH(T('Class')),
                          #TH(T('Enroll')),
                          TH(T('Book in advance')),
                          TH(T('Attend'))))

        table = TABLE(header, _class='table table-striped table-hover')
        green_check = SPAN(os_gui.get_fa_icon('fa-check'), _class='text-green')

        for i, row in enumerate(rows):
            repr_row = list(rows[i:i + 1].render())[0]

            class_permission = permissions[row.id]
            enroll = class_permission.get('Enroll', '')
            shopbook = class_permission.get('ShopBook', '')
            attend = class_permission.get('Attend', '')

            if enroll:
                enroll = green_check

            if shopbook:
                shopbook = green_check

            if attend:
                attend = green_check

            tr = TR(TD(repr_row.Week_day),
                    TD(repr_row.Starttime, ' - ', repr_row.Endtime),
                    TD(repr_row.school_locations_id),
                    TD(repr_row.school_classtypes_id),
                    #TD(enroll),
                    TD(shopbook),
                    TD(attend))

            table.append(tr)

        return table


    def get_class_permissions(self, public_only=True, formatted=False):
        """
            :return: return list of class permissons (clsID: enroll, book in shop, attend)
        """
        db = current.db

        # get groups for classcard
        query = (db.school_classcards_groups_classcards.school_classcards_id == self.scdID)
        rows = db(query).select(db.school_classcards_groups_classcards.school_classcards_groups_id)

        group_ids = []
        for row in rows:
            group_ids.append(row.school_classcards_groups_id)


        # get permissions for classcard group
        left = [db.classes.on(db.classes_school_classcards_groups.classes_id == db.classes.id)]
        query = (db.classes_school_classcards_groups.school_classcards_groups_id.belongs(group_ids))

        if public_only:
            query &= (db.classes.AllowAPI == True)

        rows = db(query).select(db.classes_school_classcards_groups.ALL,
                                left=left)

        permissions = {}
        for row in rows:
            clsID = row.classes_id
            if clsID not in permissions:
                permissions[clsID] = {}

            if row.Enroll:
                permissions[clsID]['Enroll'] = True
            if row.ShopBook:
                permissions[clsID]['ShopBook'] = True
            if row.Attend:
                permissions[clsID]['Attend'] = True

        if not formatted:
            return permissions
        else:
            return self._get_class_permissions_format(permissions)


    def customer_has_required_membership_on_date(self, date):
        """
        Check if the customer this card is linked to has the required membership to be able to check-in to classes
        :param date: datetime.date - date on which to check for the required classcard
        :return: Boolean; True if the customer has the required membership or no membership is defined. Otherwise false.
        """
        from .os_customer import Customer

        if not self.school_classcard.school_memberships_id:
            return True

        customer = Customer(self.classcard.auth_customer_id)

        memberships = customer.get_memberships_on_date(date)
        if not memberships:
            return False

        return_value = False
        for membership in memberships:
            if membership.id == self.school_classcard.school_memberships_id:
                return_value = True
                break

        return return_value
