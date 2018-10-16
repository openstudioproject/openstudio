#!/usr/bin/env python

"""py.test test cases to test OpenStudio.

These tests run based on webclient and need web2py server running.
"""

from gluon.contrib.populate import populate
from populate_os_tables import populate_customers
from populate_os_tables import populate_classes
from populate_os_tables import populate_workshops
from populate_os_tables import populate_workshops_messages
from populate_os_tables import populate_workshops_with_activity
from populate_os_tables import populate_workshops_products_customers
from populate_os_tables import populate_workshop_activity_overlapping_class
from populate_os_tables import populate_workshops_for_api_tests
from populate_os_tables import populate_customers_orders
from populate_os_tables import populate_customers_orders_items


def test_events_index(client, web2py):
    """
        Is the index page showing?
    """
    url = '/events/index'
    client.get(url)
    assert client.status == 200
    assert 'Events' in client.text


def test_event_add(client, web2py):
    """
        Can we add a event?
    """
    populate(web2py.db.school_locations, 1)

    url = '/events/event_add'
    client.get(url)
    assert client.status == 200

    data = dict(Name="Mysore_week",
                Startdate='2014-01-01',
                Enddate='2014-01-31',
                school_locations_id=1
                )
    client.post(url, data=data)
    assert client.status == 200
    assert 'Price incl. VAT' in client.text # verify redirection

    assert web2py.db(web2py.db.workshops).count() == 1

    # Check event_add_onaccept
    assert web2py.db(web2py.db.workshops_products).count() == 1
    fws_product = web2py.db.workshops_products(1)
    assert fws_product.FullWorkshop
    assert not fws_product.Deletable


def test_event_archive(client, web2py):
    """
        Is the archive function working?
    """
    populate_workshops(web2py)

    url = '/events/event_archive?wsID=1'
    # Archive
    client.get(url)
    assert client.status == 200
    assert 'Events' in client.text # verify redirection
    assert web2py.db.workshops(1).Archived == True

    # Unarchive (move to current)
    client.get(url)
    assert client.status == 200
    assert 'Events' in client.text # verify redirection
    assert not web2py.db.workshops(1).Archived


def test_event_edit(client, web2py):
    """
        Can we edit a event?
    """
    populate_workshops(web2py)

    url = '/events/event_edit?wsID=1'
    client.get(url)
    assert client.status == 200

    data = dict(id=1,
                Name="Mysore_week",
                Startdate='2014-01-01',
                Enddate='2014-12-31',
                Price='250'
                )
    client.post(url, data=data)
    assert client.status == 200
    assert 'Events' in client.text # verify redirection
    assert data['Name'] in client.text

    assert web2py.db(web2py.db.workshops).count() > 0


def test_event_duplicate(client, web2py):
    """
        Can we duplicate a event?
    """
    populate_workshops_for_api_tests(web2py)

    url = '/events/event_duplicate?wsID=1'
    client.get(url)
    assert client.status == 200

    # Check workshop info
    workshop = web2py.db.workshops(1)
    workshop_copy = web2py.db.workshops(2)

    assert workshop_copy.Name == workshop.Name + ' (Copy)'
    assert workshop_copy.Archived == workshop.Archived
    assert workshop_copy.Startdate == workshop.Startdate
    assert workshop_copy.Enddate == workshop.Enddate
    assert workshop_copy.Starttime == workshop.Starttime
    assert workshop_copy.Endtime == workshop.Endtime
    assert workshop_copy.Description == workshop.Description
    assert workshop_copy.PublicWorkshop == False
    assert workshop_copy.auth_teacher_id == workshop.auth_teacher_id
    assert workshop_copy.auth_teacher_id2 == workshop.auth_teacher_id2


    # check for 4 products & 4 activities
    query = (web2py.db.workshops_products.id>0)
    assert web2py.db(query).count() == 4
    query = (web2py.db.workshops_activities.id>0)
    assert web2py.db(query).count() == 4

    # Check activity info
    activity = web2py.db.workshops_activities(1)
    activity_copy = web2py.db.workshops_activities(3)

    assert activity_copy.Activity == activity.Activity
    assert activity_copy.Activitydate == activity.Activitydate
    assert activity_copy.school_locations_id == activity.school_locations_id
    assert activity_copy.Starttime == activity.Starttime
    assert activity_copy.Endtime == activity.Endtime
    assert activity_copy.Spaces == activity.Spaces
    assert activity_copy.auth_teacher_id == activity.auth_teacher_id
    assert activity_copy.auth_teacher_id2 == activity.auth_teacher_id2

    # Check product info
    product = web2py.db.workshops_products(1)
    product_copy = web2py.db.workshops_products(3)

    assert product_copy.FullWorkshop == product.FullWorkshop
    assert product_copy.Deletable == product.Deletable
    assert product_copy.PublicProduct == product.PublicProduct
    assert product_copy.Name == product.Name
    assert product_copy.Price == product.Price
    assert product_copy.tax_rates_id == product.tax_rates_id
    assert product_copy.ExternalShopURL == product.ExternalShopURL
    assert product_copy.AddToCartText == product.AddToCartText
    assert product_copy.Donation == product.Donation


def test_pdf_show_template(client, web2py):
    """
        Test pdf export for events
    """
    ##
    # Get random url to setup session environment in OpenStudio
    ##
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_workshops_products_customers(web2py) # this function adds an activity & product

    wsID = 1
    url = '/events/pdf_template_show?wsID=' + unicode(wsID)
    client.get(url)
    assert client.status == 200

    ws = web2py.db.workshops(wsID)
    assert ws.Name in client.text
    assert ws.Description in client.text

    activity = web2py.db.workshops_activities(1)
    assert unicode(activity.Activitydate) in unicode(client.text, 'utf-8')
    assert activity.Starttime.strftime('%H:%M') in client.text

    product = web2py.db.workshops_products(1)
    assert unicode(product.Price) in unicode(client.text, "utf-8")


def test_activity_add(client, web2py):
    """
        Can we add a activity to a event?
    """
    populate_workshops(web2py, teachers=True)

    url = '/events/activity_add/1'
    client.get(url)
    assert client.status == 200
    assert 'name="Activity"' in client.text

    # is the event teacher predefined
    workshop = web2py.db.workshops(1)
    teacher  = web2py.db.auth_user(workshop.auth_teacher_id)
    teacher2 = web2py.db.auth_user(workshop.auth_teacher_id2)
    assert teacher.first_name.split(' ')[0] in client.text
    assert teacher2.first_name.split(' ')[0] in client.text

    data = dict(Activity="Cherries",
                Activitydate='2999-01-01',
                school_locations_id=1,
                Starttime='09:00:00',
                Endtime='23:00:00',
                Spaces='20')
    client.post(url, data=data)
    assert client.status == 200
    assert 'Event' in client.text # verify redirection back to workshop main page
    assert data['Activity'] in client.text # is the activity showing in the list?

    assert web2py.db(web2py.db.workshops_activities).count() == 1

    # Check updating of dates & times in workshop
    workshop = web2py.db.workshops(1)
    assert str(workshop.Enddate) == data['Activitydate']
    assert str(workshop.Endtime) == data['Endtime']


def test_activity_edit(client, web2py):
    """
        Can we edit an activity?
    """
    populate_workshops_with_activity(web2py)

    url = '/events/activity_edit/1'
    client.get(url)
    assert client.status == 200

    data = dict(id='1',
                Activity="Cherries",
                Activitydate='2999-01-01',
                Starttime='09:00:00',
                Endtime='11:12:00',
                Spaces='20',
                Price='250')
    client.post(url, data=data)
    assert client.status == 200
    # verify redirection back to workshop main page
    assert 'Activities' in client.text
    # is the activity showing in the list?
    assert data['Activity'] in client.text
    # check the db
    assert web2py.db(web2py.db.workshops_activities).count() > 0

    # Check updating of dates & times in workshop
    workshop = web2py.db.workshops(1)
    assert str(workshop.Enddate) == data['Activitydate']
    assert str(workshop.Endtime) == data['Endtime']


def test_activity_delete(client, web2py):
    """
        Can we delete an activity and are the dates & times for the db.workshops_record updated?
    """
    populate_workshops_for_api_tests(web2py)

    url = '/events/activity_delete/1/2'
    client.get(url)
    assert client.status == 200

    # Check number of records in table
    assert web2py.db(web2py.db.workshops_activities).count() == 1

    # Check updating of workshop datetime info
    workshop = web2py.db.workshops(1)
    activity = web2py.db.workshops_activities(1)

    assert workshop.Startdate == activity.Activitydate
    assert workshop.Enddate   == activity.Activitydate
    assert workshop.Starttime == activity.Starttime
    assert workshop.Endtime   == activity.Endtime


def test_activity_duplicate(client, web2py):
    """
        Is the duplication working?
    """
    populate_workshops_with_activity(web2py)

    url = '/events/activity_duplicate/1'
    client.get(url)
    assert client.status == 200
    assert 'duplicated' in client.text # is the flash message showing
    assert web2py.db(web2py.db.workshops_activities).count() == 2
    assert web2py.db.workshops_activities(1).Activity + u' (Copy)' == web2py.db.workshops_activities(2).Activity


def test_product_customer_update_info(client, web2py):
    """
        Test as JSON
        Is the attendance info ajaj backend working?
    """
    populate_workshops_with_activity(web2py)
    populate_customers(web2py, 1)
    web2py.db.workshops_products_customers.insert(workshops_products_id = 1,
                                                  auth_customer_id      = 1001)
    web2py.db.commit()

    url = '/events/ticket_customer_update_info.json'
    data = dict(id='1',
                WorkshopInfo='on')
    client.post(url, data=data)
    assert client.status == 200
    assert 'success' in client.text

    assert web2py.db.workshops_products_customers(1).WorkshopInfo == True

    # unset info and payment confirmation.
    url = '/events/ticket_customer_update_info.json'
    data = dict(id='1')
    client.post(url, data=data)
    assert client.status == 200
    assert 'success' in client.text

    assert web2py.db.workshops_products_customers(1).WorkshopInfo == False


def test_product_add(client, web2py):
    """
        Test if we can add a new product
    """
    populate_workshops_with_activity(web2py)

    url = '/events/ticket_add/1'
    client.get(url)
    assert client.status == 200
    data = dict(Name='Bananas',
                Price='300',
                tax_rates_id=1,
                Description='Great with almonds when frozen and blended'
                )
    client.post(url, data=data)
    assert client.status == 200

    # Verify redirection to ticket_activities
    assert "Activities included" in client.text
    # make sure something was added to the db
    assert web2py.db(web2py.db.workshops_products).count > 1


def test_ticket_edit(client, web2py):
    """
        Test if we can edit a ticket
    """
    populate_workshops_with_activity(web2py)

    url = '/events/ticket_edit/1'
    client.get(url)
    assert client.status == 200
    data = dict(id=1,
                Name='Bananas',
                tax_rates_id=1,
                Price='300',
                Description='Great with almonds when frozen and blended'
                )
    client.post(url, data=data)
    assert client.status == 200
    # check if we're at manage
    assert "Tickets" in client.text
    assert data['Name'] in client.text
    # make sure something was added to the db
    assert web2py.db(web2py.db.workshops_products).count > 1


def test_ticket_duplicate(client, web2py):
    """
        Can we duplicate a event ticket?
    """
    populate_workshops_with_activity(web2py)

    url = '/events/ticket_duplicate?wspID=1'
    client.get(url)
    assert client.status == 200

    wsp_1 = web2py.db.workshops_products(1)
    wsp_2 = web2py.db.workshops_products(2)

    assert wsp_1.workshops_id == wsp_2.workshops_id
    assert wsp_2.FullWorkshop == False
    assert wsp_2.Deletable == True
    assert wsp_2.PublicProduct == False
    assert wsp_1.Name in wsp_2.Name
    assert wsp_1.Price == wsp_2.Price
    assert wsp_1.tax_rates_id == wsp_2.tax_rates_id
    assert wsp_1.Description == wsp_2.Description
    assert wsp_1.ExternalShopURL == wsp_2.ExternalShopURL
    assert wsp_1.AddToCartText == wsp_2.AddToCartText
    assert wsp_1.Donation == wsp_2.Donation

    # Check some activities have been added for workshop product
    assert web2py.db(web2py.db.workshops_products_activities.workshops_products_id == 2).count() > 0


def test_ticket_delete_full_wsp_error(client, web2py):
    """
        Test whether we get an error when trying to delete a full ws ticket
    """
    populate_workshops_with_activity(web2py)

    url = '/events/ticket_delete?wsID=1&wspID=1'
    client.get(url)
    assert client.status == 200

    assert web2py.db(web2py.db.workshops_products).count > 0


def test_ticket_delete(client, web2py):
    """
        Test if we can delete a regular ticket
    """
    populate_workshops_with_activity(web2py)
    populate(web2py.db.workshops_products, 1)

    url = '/events/ticket_delete?wsID=1&wspID=2'
    client.get(url)
    assert client.status == 200

    # we inserted an extra product, so now there should only be one
    assert web2py.db(web2py.db.workshops_products).count() == 1


def test_ticket_activities_add(client, web2py):
    """
        Test if we can add activities to a ticket
    """
    populate_workshops_with_activity(web2py)

    url = '/events/ticket_activities?wsID=1&wspID=1'
    client.get(url)
    assert client.status == 200

    data = {'1':'on'}
    client.post(url, data=data)
    assert client.status == 200
    assert web2py.db(web2py.db.workshops_products_activities).count() == 1


def test_ticket_activities_remove(client, web2py):
    """
        Test if we can remove activities from a ticket
    """
    populate_workshops_with_activity(web2py)
    web2py.db.workshops_products_activities.insert(
        workshops_products_id = 1,
        workshops_activities_id = 1)
    web2py.db.commit()

    url = '/events/ticket_activities?wsID=1&wspID=1'
    client.get(url)
    assert client.status == 200

    data = {'1': None}
    client.post(url, data=data)
    assert client.status == 200

    assert web2py.db(web2py.db.workshops_products_activities).count() == 0


# def test_product_sell(client, web2py):
#     """
#         Test that the first customer is listed
#     """
#     populate_workshops_with_activity(web2py)
#     populate_customers(web2py, 1)
#
#     url = '/events/product_sell?wsID=1&wspID=1'
#     client.get(url)
#     assert client.status == 200
#
#     customer = web2py.db.auth_user(1001)
#     assert 'Search' in client.text


def test_ticket_sell_to_customer_create_invoice_and_cancel_orders_when_sold_out(client, web2py):
    """
        Test if we can sell a ticket to a customer and if an invoice is created
    """
    populate_workshops_with_activity(web2py)
    populate_customers(web2py, 1)
    populate_customers_orders(web2py)
    populate_customers_orders_items(web2py, workshops_products=True)


    url = '/events/ticket_sell_to_customer?cuID=1001&wsID=1&wspID=1'
    client.get(url)
    assert client.status == 200

    assert web2py.db(web2py.db.workshops_products_customers).count() == 1

    assert web2py.db(web2py.db.invoices).count() == 1

    invoice = web2py.db.invoices(1)
    assert invoice.invoices_groups_id == 100

    inv_wsp = web2py.db.invoices_workshops_products_customers(1)
    assert inv_wsp.workshops_products_customers_id == 1

    # check invoice amount
    price   = web2py.db.workshops_products(1).Price
    amounts = web2py.db.invoices_amounts(1)
    assert amounts.TotalPriceVAT == price

    # check if all orders get cancelled
    assert web2py.db(web2py.db.customers_orders.Status == 'cancelled').count() > 0

    # Check that a mail is sent (or at least it tried)
    assert web2py.db(web2py.db.messages).count() == 1
    assert web2py.db(web2py.db.customers_messages).count() == 1


def test_ticket_sell_to_customer_AutoSendInfoMail_False(client, web2py):
    """
        Test if we can sell a ticket to a customer and if an invoice is created
    """
    populate_workshops_with_activity(web2py)
    populate_customers(web2py, 1)
    populate_customers_orders(web2py)
    populate_customers_orders_items(web2py, workshops_products=True)

    ws = web2py.db.workshops(1)
    ws.AutoSendInfoMail = False
    ws.update_record()

    web2py.db.commit()

    url = '/events/ticket_sell_to_customer?cuID=1001&wsID=1&wspID=1'
    client.get(url)
    assert client.status == 200

    assert web2py.db(web2py.db.workshops_products_customers).count() == 1

    # Check that a mail is not sent
    assert web2py.db(web2py.db.messages).count() == 0
    assert web2py.db(web2py.db.customers_messages).count() == 0


def test_ticket_resend_info_mail(client, web2py):
    """
        Is the function to (re)send an info mail working?
    """
    ##
    # Get random url to setup session environment in OpenStudio
    ##
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_workshops_products_customers(web2py) # this function adds an activity & product

    url = '/events/ticket_resend_info_mail?wspcID=1'
    client.get(url)
    assert client.status == 200

    query = (web2py.db.messages.id > 0)
    assert web2py.db(query).count() == 1


def test_ticket_sell_to_customer_waitinglist(client, web2py):
    """
        Test if we can sell a ticket to a customer
    """
    populate_workshops_with_activity(web2py)
    populate_customers(web2py, 1)

    url = '/events/ticket_sell_to_customer?cuID=1001&wsID=1&wspID=1&waiting=True'
    client.get(url)
    assert client.status == 200

    assert web2py.db.workshops_products_customers(1).Waitinglist == True


def test_ticket_remove_customer_from_waitinglist(client, web2py):
    """
        Test if we can remove a customer from the waitinglist and add them
        to the regular list
    """
    populate_workshops_with_activity(web2py)
    populate_customers(web2py, 1)
    web2py.db.workshops_products_customers.insert(
        workshops_products_id = 1,
        auth_customer_id = 1001,
        Waitinglist = True)
    web2py.db.commit()

    url = '/events/ticket_remove_customer_from_waitinglist?wsID=1&wsp_cuID=1'
    client.get(url)
    assert client.status == 200

    # check there are no products customers left with waitinglist = True in db
    query = (web2py.db.workshops_products_customers.Waitinglist == True)
    assert web2py.db(query).count() == 0


def test_ticket_delete_customer(client, web2py):
    """
        Can we delete a customer from a ticket and is the invoice cancelled?
    """
    ##
    # Get random url to setup session environment in OpenStudio
    ##
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_workshops_products_customers(web2py)

    query = (web2py.db.workshops_products_customers.id > 0)
    count_before = web2py.db(query).count()

    url = '/events/ticket_delete_customer?wsID=1&wsp_cuID=2'
    client.get(url)
    assert client.status == 200

    count_after = web2py.db(query).count()
    assert count_before == count_after + 1

    ##
    # Check that the invoice status has been set to cancelled
    ##
    query = (web2py.db.invoices.Status == 'cancelled')
    assert web2py.db(query).count() == 1


def test_ticket_list_customers_fullWS(client, web2py):
    """
        Test listing of full workshop customers for a ticket
    """
    populate_workshops_with_activity(web2py)
    populate_customers(web2py, 1)
    web2py.db.workshops_products_customers.insert(workshops_products_id = 1,
                                                  auth_customer_id = 1001)
    web2py.db.commit()

    url = '/events/tickets_list_customers?wsID=1&wspID=1'
    client.get(url)
    assert client.status == 200

    assert 'Full event' in client.text


def test_tickets_list_customers(client, web2py):
    """
        Test listing of customers for a ticket
        Also check if the right label is displayed (should have ticket name)
    """
    ##
    # Get random url to setup session environment in OpenStudio
    ##
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_workshops_products_customers(web2py)

    url = '/events/tickets_list_customers?wsID=1&wspID=2'
    client.get(url)
    assert client.status == 200

    product = web2py.db.workshops_products(2)
    assert product.Name.split(' ')[0] in client.text


def test_activity_update_attendance(client, web2py):
    """
        Test if a record is inserted into workshops_activities_customers
    """
    ##
    # Get random url to setup session environment in OpenStudio
    ##
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_workshops_products_customers(web2py)

    # add
    url = '/events/activity_update_attendance.json'
    data = {'attending': 'on',
            'cuID'     : 1001,
            'wsaID'    : 1 }
    client.post(url, data=data)
    assert client.status == 200

    assert web2py.db(web2py.db.workshops_activities_customers).count() == 1

    # remove
    url = '/events/activity_update_attendance.json'
    data = {'cuID'     : 1001,
            'wsaID'    : 1 }
    client.post(url, data=data)
    assert client.status == 200

    assert web2py.db(web2py.db.workshops_activities_customers).count() == 0


def test_activity_list_customers(client, web2py):
    """
        Test wether a full workshop customer and a customer for another
        ticket show up in the list of an activity with the correct label
    """
    ##
    # Get random url to setup session environment in OpenStudio
    ##
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_workshops_products_customers(web2py)

    url = '/events/activity_list_customers?wsID=1&wsaID=1'
    client.get(url)
    assert client.status == 200

    # Full workshop label (label-primary)
    assert '<span class="label label-primary">' in client.text
    # ticket label (default)
    assert '<span class="label label-default">' in client.text



def test_ticket_cancel_customer(client, web2py):
    """
        Test if a customer can be cancelled
    """
    ##
    # Get random url to setup session environment in OpenStudio
    ##
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_workshops_products_customers(web2py)

    url = '/events/ticket_cancel_customer?wsID=1&wsp_cuID=1'
    client.get(url)
    assert client.status == 200

    query = (web2py.db.workshops_products_customers.Cancelled == True)
    assert web2py.db(query).count() == 1

    # Check cancelled invoice
    query = (web2py.db.invoices.Status == 'cancelled')
    assert web2py.db(query).count() == 1


def test_overlapping_classes_get_count_all(client, web2py):
    """
        Test if a span badge with correct count is on the manage page
    """
    populate_workshop_activity_overlapping_class(web2py)

    url = '/events/activities?wsID=1'
    client.get(url)
    assert client.status == 200

    assert '<span class="badge">1</span>' in client.text

def test_overlapping_classes(client, web2py):
    """
        Test list of overlapping classes
    """
    populate_workshop_activity_overlapping_class(web2py)

    url = '/events/overlapping_classes?wsID=1'
    client.get(url)
    assert client.status == 200

    # if we have a td with this class, we know the list isn't empty
    assert '<td class="td_status_marker">' in client.text


def test_overlapping_classes_cancel_all(client, web2py):
    """
        Check if the cancel all overlapping classes function works
    """
    populate_workshop_activity_overlapping_class(web2py)

    url = '/events/overlapping_classes_cancel_all?wsID=1'
    client.get(url)
    assert client.status == 200

    # make sure the correct entry is in db.classes_cancelled
    query = (web2py.db.classes_otc.classes_id == 1) & \
            (web2py.db.classes_otc.ClassDate == '2014-01-06') & \
            (web2py.db.classes_otc.Status == 'cancelled')

    assert web2py.db(query).count() == 1


def test_stats_revenue(client, web2py):
    """
        Check if the total count for the revenue stats is correct
    """
    ##
    # Get random url to setup session environment in OpenStudio
    ##
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_workshops_products_customers(web2py)

    url = '/events/stats?wsID=1'
    client.get(url)
    assert client.status == 200

    sum = web2py.db.invoices_amounts.TotalPriceVAT.sum()
    rows = web2py.db().select(sum)
    amount = rows.first()[sum]

    total = format(amount, '.2f')
    assert total in client.text


def test_stats_top10cities(client, web2py):
    """
        Make sure the cities of 2 customers are listed
    """
    ##
    # Get random url to setup session environment in OpenStudio
    ##
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_workshops_products_customers(web2py)

    url = '/events/stats?wsID=1'
    client.get(url)
    assert client.status == 200

    city_cu1 = web2py.db.auth_user(id=1001).city.split(' ')[0]
    city_cu2 = web2py.db.auth_user(id=1002).city.split(' ')[0]

    assert city_cu1 in client.text
    assert city_cu2 in client.text

def test_get_subtitle(client, web2py):
    """
        Are the start and enddate in the subtitle?
    """
    populate_workshops(web2py)

    url = '/events/activities?wsID=1'
    client.get(url)
    assert client.status == 200

    workshop = web2py.db.workshops(1)
    sd = workshop.Startdate
    ed = workshop.Enddate
    date = unicode(sd) + ' - ' + unicode(ed)
    assert date in client.text