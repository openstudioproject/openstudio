# -*- coding: utf-8 -*-

'''
    py.test test cases to test OpenStudio module os_workshops.
    These tests run based on webclient and need web2py server running.
'''

from gluon.contrib.populate import populate
from populate_os_tables import populate_customers
from populate_os_tables import populate_classes
from populate_os_tables import populate_workshops
from populate_os_tables import populate_workshops_with_activity
from populate_os_tables import populate_workshops_products_customers
from populate_os_tables import populate_workshop_activity_overlapping_class


def test_wh_get_customer_info(client, web2py):
    '''
        Tests the get_cutomer_info function from the WorkshopHelper class
        This function is used in workshops/products_get_customer so the output
        of that function is checked
    '''
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_workshops_products_customers(web2py)

    url = '/events/tickets_list_customers?wsID=1&wspID=1'
    client.get(url)
    assert client.status == 200

    # check if the labels for the checkboxes are present
    assert 'no_table_WorkshopInfo' in client.text
