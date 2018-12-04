# -*- coding: utf-8 -*-

import datetime
from populate_os_tables import populate_customers_with_subscriptions


def test_automation_customers_memberships_renew_expired(client, web2py):
    """
        Can we create subscription invoices for a month?
    """
    from populate_os_tables import populate_customers_with_memberships
    import datetime

    # from openstudio/os_customer_membership import CustomerMembership
    # Get random url to initialize OpenStudio environment
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_customers_with_subscriptions(web2py, 1)
    populate_customers_with_memberships(web2py, customers_populated=True)

    memberships_count = web2py.db(web2py.db.customers_memberships).count()

    url = '/test_automation_customer_memberships/' + \
          'test_memberships_renew_expired' + \
          '?month=1&year=2014'
    client.get(url)
    assert client.status == 200

    # Get membership
    previous_membership = web2py.db.customers_memberships(1)
    new_id = memberships_count + 1
    new_membership = web2py.db.customers_memberships(new_id)

    # Check membership
    assert new_membership.Startdate == previous_membership.Enddate + datetime.timedelta(days=1)
    assert new_membership.Note == 'Renewal for membership 1'

    # Check invoice
    invcm = web2py.db.invoices_customers_memberships(customers_memberships_id = new_id)
    invoice = web2py.db.invoices(invcm.invoices_id)

    assert invoice.Status == 'sent'

    query = (web2py.db.invoices_items.invoices_id == invoice.id)
    rows = web2py.db(query).select(web2py.db.invoices_items.ALL)
    for row in rows:
        assert "Membership" in row.ProductName
        assert unicode(new_membership.Startdate) in row.Description
        assert unicode(new_membership.Enddate) in row.Description
