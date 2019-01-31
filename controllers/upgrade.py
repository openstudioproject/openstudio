# -*- coding: utf-8 -*-

from general_helpers import max_string_length
from general_helpers import get_ajax_loader

from openstudio.os_workshop_product import WorkshopProduct
from openstudio.os_invoice import Invoice

from os_upgrade import set_version


def to_login(var=None):
    redirect(URL('default', 'user', args=['login']))


def index():
    """
        This function executes commands needed for upgrades to new versions
    """
    # first check if a version is set
    if not db.sys_properties(Property='Version'):
        db.sys_properties.insert(Property='Version',
                                 PropertyValue=0)
        db.sys_properties.insert(Property='VersionRelease',
                                 PropertyValue=0)

    # check if a version is set and get it
    if db.sys_properties(Property='Version'):
        version = float(db.sys_properties(Property='Version').PropertyValue)

        if version < 2019.02:
            print version
            upgrade_to_201902()
            session.flash = T("Upgraded db to 2019.02")
        else:
            session.flash = T('Already up to date')

        # always renew permissions for admin group after update
        set_permissions_for_admin_group()

    set_version()

    ##
    # clear cache
    ##
    cache.ram.clear(regex='.*')

    # Back to square one
    to_login()


def upgrade_to_201902():
    """
        Upgrade operations to 2019.02
    """
    ##
    # Update invoice links
    ##
    define_invoices_classes_attendance()
    define_invoices_customers_memberships()
    define_invoices_customers_subscriptions()
    define_invoices_workshops_products_customers()
    define_invoices_customers_classcards()
    define_invoices_employee_claims()
    define_invoices_teachers_payment_classes()

    # Classes attendance
    query = (db.invoices_classes_attendance.id > 0)
    rows = db(query).select(db.invoices_classes_attendance.ALL)
    for row in rows:
        query = (db.invoices_items.invoices_id == row.invoices_id)
        item_rows = db(query).select(db.invoices_items.id)
        item_row = item_rows.first()

        db.invoices_items_classes_attendance.insert(
            invoices_items_id = item_row.id,
            classes_attendance_id = row.classes_attendance_id
        )

    # Customer subscriptions
    query = (db.invoices_customers_subscriptions.id > 0)
    rows = db(query).select(db.invoices_customers_subscriptions.ALL)
    for row in rows:
        query = (db.invoices_items.invoices_id == row.invoices_id)
        item_rows = db(query).select(db.invoices_items.id)
        item_row = item_rows.first()

        db.invoices_items_customers_subscriptions.insert(
            invoices_items_id = item_row.id,
            customers_subscriptions_id = row.customers_subscriptions_id
        )

    # Customer class cards
    query = (db.invoices_customers_classcards.id > 0)
    rows = db(query).select(db.invoices_customers_classcards.ALL)
    for row in rows:
        query = (db.invoices_items.invoices_id == row.invoices_id)
        item_rows = db(query).select(db.invoices_items.id)
        item_row = item_rows.first()

        db.invoices_items_customers_classcards.insert(
            invoices_items_id = item_row.id,
            customers_classcards_id = row.customers_classcards_id
        )

    # Customer memberships
    query = (db.invoices_customers_memberships.id > 0)
    rows = db(query).select(db.invoices_customers_memberships.ALL)
    for row in rows:
        query = (db.invoices_items.invoices_id == row.invoices_id)
        item_rows = db(query).select(db.invoices_items.id)
        item_row = item_rows.first()

        db.invoices_items_customers_memberships.insert(
            invoices_items_id = item_row.id,
            customers_memberships_id = row.customers_memberships_id
        )

    # Customer event tickets
    query = (db.invoices_workshops_products_customers.id > 0)
    rows = db(query).select(db.invoices_workshops_products_customers.ALL)
    for row in rows:
        query = (db.invoices_items.invoices_id == row.invoices_id)
        item_rows = db(query).select(db.invoices_items.id)
        item_row = item_rows.first()

        db.invoices_items_workshops_products_customers.insert(
            invoices_items_id = item_row.id,
            workshops_products_customers_id = row.workshops_products_customers_id
        )

    # Employee claims
    query = (db.invoices_employee_claims.id > 0)
    rows = db(query).select(db.invoices_employee_claims.ALL)
    for row in rows:
        query = (db.invoices_items.invoices_id == row.invoices_id)
        item_rows = db(query).select(db.invoices_items.id)
        item_row = item_rows.first()

        db.invoices_items_employee_claims.insert(
            invoices_items_id = item_row.id,
            employee_claims_id = row.employee_claims_id
        )

    # Teacher payment classes
    query = (db.invoices_teachers_payment_classes.id > 0)
    rows = db(query).select(db.invoices_teachers_payment_classes.ALL)
    for row in rows:
        query = (db.invoices_items.invoices_id == row.invoices_id)
        item_rows = db(query).select(db.invoices_items.id)
        item_row = item_rows.first()

        db.invoices_items_teachers_payment_classes.insert(
            invoices_items_id = item_row.id,
            teachers_payment_classes_id = row.teachers_payment_classes_id
        )


    ##
    # Set default value for db.school_subscriptions.MinDuration
    ##
    query = (db.school_subscriptions.MinDuration == None)
    db(query).update(MinDuration=1)


    ##
    # Insert email templates
    ##
    # Teacher sub offer declined
    db.sys_email_templates.insert(
        Name = 'teacher_sub_offer_declined',
        Title = T('Teacher sub offer declined'),
        Description = '',
        TemplateContent = """
<p>Dear {teacher_name},<br /><br /></p>
<p>As we have been able to fill the sub request for the class above, we would like to inform you that we won't be making use of your offer to teach this class.<br /><br /></p>
<p>We thank you for your offer and hope to be able to use your services again in the future.</p>"""
    )
    # Teacher sub offer accepted
    db.sys_email_templates.insert(
        Name='teacher_sub_offer_accepted',
        Title=T('Teacher sub offer accepted'),
        Description='',
        TemplateContent="""
<p>Dear {teacher_name},<br /><br /></p>
<p>Thank you for taking over the class mentioned above. We're counting on you!</p>"""
    )
    # Teachers sub requests daily summary
    db.sys_email_templates.insert(
        Name = 'teacher_sub_requests_daily_summary',
        Title = T('Teacher sub requests daily summary'),
        Description = '',
        TemplateContent = """"""
    )