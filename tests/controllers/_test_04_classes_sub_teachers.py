import datetime

from populate_os_tables import prepare_classes
from populate_os_tables import prepare_classes_otc_subs_avail


def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)



def test_index(client, web2py):
    """
        Check if classes appear on the classes_open list
    """
    prepare_classes(web2py)
    assert web2py.db(web2py.db.classes).count() >= 1

    # get 2 mondays later than today
    delta = datetime.timedelta(days=7)
    today = datetime.date.today()
    next_monday = next_weekday(today, 0) # 0 = Monday, 1=Tuesday, 2=Wednesday...
    monday_after_that = next_monday + delta

    web2py.db.classes_otc.insert(
        Status = 'open',
        classes_id = 1,
        ClassDate = next_monday
    )
    web2py.db.classes_otc.insert(
        Status = 'open',
        classes_id = 1,
        ClassDate = monday_after_that,
        school_locations_id = 2,
        school_classtypes_id = 2
    )
    web2py.db.classes_otc.insert(
        Status = 'open',
        classes_id = 1,
        ClassDate = '2014-01-06'
    )

    web2py.db.commit()

    assert web2py.db(web2py.db.classes_otc.Status == 'open').count() == 3

    # get the page
    url = '/classes_sub_teachers/index'
    client.get(url)
    assert client.status == 200

    # past open classes shouldn't be shown
    assert '2014-01-06' not in client.text
    # future ones should be shown
    assert unicode(next_monday) in client.text
    assert unicode(monday_after_that) in client.text

    # check location & classtype from classes_otc
    location = web2py.db.school_locations(2).Name.split(' ')[0]
    assert location in client.text
    classtype = web2py.db.school_classtypes(2).Name.split(' ')[0]
    assert classtype in client.text


def test_offers(client, web2py):
    """
    Manage sub requests
    """
    prepare_classes_otc_subs_avail(web2py, accepted=None)

    url = '/classes_sub_teachers/offers?cotcID=1'
    client.get(url)
    assert client.status == 200

    cotcsa = web2py.db.classes_otc_sub_avail(1)
    cotc = web2py.db.classes_otc(cotcsa.classes_otc_id)

    assert unicode(cotc.ClassDate) in client.text

#
# def test_subs_manage_processed(client, web2py):
#     """
#     Manage sub requests
#     """
#     prepare_classes_otc_subs_avail(web2py, accepted=True)
#
#     url = '/classes/subs_manage?Status=processed'
#     client.get(url)
#     assert client.status == 200
#
#     cotcsa = web2py.db.classes_otc_sub_avail(1)
#     cotc = web2py.db.classes_otc(cotcsa.classes_otc_id)
#
#     assert unicode(cotc.ClassDate) in client.text


def test_sub_teacher_accept(client, web2py):
    """
    Are cotcsa rows accepted correctly?
    """
    prepare_classes_otc_subs_avail(web2py, accepted=None)

    url = '/classes_sub_teachers/sub_teacher_accept?cotcsaID=1'
    client.get(url)
    assert client.status == 200

    cotcsa = web2py.db.classes_otc_sub_avail(1)
    assert cotcsa.Accepted == True


def test_sub_teacher_decline(client, web2py):
    """
    Are cotcsa rows declined correctly?
    """
    prepare_classes_otc_subs_avail(web2py, accepted=None)

    url = '/classes_sub_teachers/sub_teacher_decline?cotcsaID=1'
    client.get(url)
    assert client.status == 200

    cotcsa = web2py.db.classes_otc_sub_avail(1)
    assert cotcsa.Accepted == False