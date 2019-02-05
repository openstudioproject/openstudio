# -*- coding: utf-8 -*-

import datetime

from populate_os_tables import prepare_classes
from populate_os_tables import prepare_classes_teacher_classtypes
from populate_os_tables import populate_define_sys_email_reminders

def test_email_reminders_teachers_sub_request_open(client, web2py):
    """
    Check if a mail is rendered and sent
    """
    prepare_classes(web2py)
    populate_define_sys_email_reminders(web2py)

    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    cotcID = web2py.db.classes_otc.insert(
        classes_id = 1,
        ClassDate = tomorrow,
        Status = 'open'
    )
    web2py.db.commit()

    url = '/test_os_scheduler_tasks/email_reminders_teachers_sub_request_open'
    client.get(url)
    assert client.status == 200

    assert "Sent mails: 1" in client.text


def test_email_teachers_sub_requests_daily_summary(client, web2py):
    """
    Check if a mail is rendered and sent
    """
    prepare_classes(web2py)
    populate_define_sys_email_reminders(web2py)

    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    cotcID = web2py.db.classes_otc.insert(
        classes_id = 1,
        ClassDate = tomorrow,
        Status = 'open'
    )
    web2py.db.commit()

    url = '/test_os_scheduler_tasks/email_teachers_sub_requests_daily_summary'
    client.get(url)
    assert client.status == 200

    # No classtypes defined for teachers
    assert "Sent mails: 0" in client.text

    # Define classtypes and check again
    prepare_classes_teacher_classtypes(web2py)
    client.get(url)
    assert client.status == 200

    assert "Sent mails: 1" in client.text
