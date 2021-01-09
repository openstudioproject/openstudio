# -*- coding: utf-8 -*-

from openstudio.os_scheduler_tasks import OsSchedulerTasks


@auth.requires(auth.user.id == 1)
def test_extend_validity():
    """
    Function to expose class & method used by scheduler task
    to create monthly invoices
    """
    if ( not web2pytest.is_running_under_test(request, request.application)
         and not auth.has_membership(group_id='Admins') ):
        redirect(URL('default', 'user', args=['not_authorized']))


    ost = OsSchedulerTasks()

    valid_on = request.vars['valid_on']
    days_to_add = request.vars['days_to_add']

    return ost.customers_classcards_extend_validity(valid_on, days_to_add)


@auth.requires(auth.user.id == 1)
def test_fix_extend_validity_with_bad_query():
    """
    Function to correct extended validity
    :return:
    """
    from general_helpers import datestr_to_python

    valid_on = request.vars['valid_on']
    dont_process_after = request.vars['dont_process_after']
    days_to_subtract = request.vars['days_to_subtract']

    db = current.db
    DATE_FORMAT = current.DATE_FORMAT
    # convert input string to date obj
    valid_on = datestr_to_python(DATE_FORMAT, valid_on)
    dont_process_after = datestr_to_python(DATE_FORMAT, dont_process_after)

    left = [
        db.school_classcards.on(db.customers_classcards.school_classcards_id ==
                                db.school_classcards.id)
    ]

    query = (
        (db.customers_classcards.Enddate >= valid_on) &
        (db.customers_classcards.Startdate < dont_process_after) &
        (db.customers_classcards.ClassesTaken < db.school_classcards.Classes)
    )

    nr_cards_updated = 0
    rows = db(query).select(db.customers_classcards.ALL)

    for row in rows:
        row.Enddate = row.Enddate - datetime.timedelta(days=int(days_to_subtract))
        row.update_record()

        nr_cards_updated += 1

    return "Subtracted the expiration date for %s cards" % nr_cards_updated