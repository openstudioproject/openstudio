#!/usr/bin/env python

'''py.test test cases to test OpenStudio.

These tests run based on webclient and need web2py server running.
'''

from gluon.contrib.populate import populate

from populate_os_tables import populate_customers
from populate_os_tables import populate_sys_organizations
from populate_os_tables import populate_postcode_groups
from populate_os_tables import populate_settings_shop_links
from populate_os_tables import populate_settings_shop_customers_profile_announcements


def test_system_organizations(client, web2py):
    '''
        Is the list of organizations working?
    '''
    populate_sys_organizations(web2py)

    url = '/settings/system_organizations'
    client.get(url)
    assert client.status == 200

    so = web2py.db.sys_organizations(1)
    assert so.Name in client.text


def test_system_organization_add(client, web2py):
    '''
        Can we add an organization?
    '''
    url = '/settings/system_organization_add'
    client.get(url)
    assert client.status == 200

    data = {
        'Name':'New organization',
        'Address':'Address',
        'Phone':'0612345678',
        'Email':'test@openstudioproject.com',
        'Registration':'reg',
        'TaxRegistration':'taxreg',
        'TermsConditionsURL':'http://www.google.nl'
    }

    client.post(url, data=data)
    assert client.status == 200
    assert data['Name'] in client.text

    # Check if thte first organization added will automatically be set as the default.
    so = web2py.db.sys_organizations(1)
    assert so.DefaultOrganization == True


def test_system_organization_edit(client, web2py):
    """
        Can we edit an organization?
    """
    populate_sys_organizations(web2py)

    url = '/settings/system_organization_edit?soID=1'
    client.get(url)
    assert client.status == 200

    data = {
        'id':'1',
        'Name':'Edit organization',
        'Address':'Address',
        'Phone':'0612345678',
        'Email':'test@openstudioproject.com',
        'Registration':'reg',
        'TaxRegistration':'taxreg',
        'TermsConditionsURL':'http://www.google.nl'
    }

    client.post(url, data=data)
    assert client.status == 200
    assert data['Name'] in client.text


def test_shop_settings_general(client, web2py):
    '''
        Is the shop general settings page working?
    '''
    url = '/settings/shop_settings'
    client.get(url)
    assert client.status == 200

    data = {'shop_header_logo_url':'http://www.groningen.nl'}
    client.post(url, data=data)
    assert client.status == 200

    assert data['shop_header_logo_url'] in client.text

    assert web2py.db(web2py.db.sys_properties.Property == 'shop_header_logo_url').count() == 1

    url = '/shop/index'
    client.get(url)
    assert data['shop_header_logo_url'] in client.text


def test_shop_customers_profile_announcements(client, web2py):
    '''
        Is the shop profile announcements page working?
    '''
    populate_settings_shop_customers_profile_announcements(web2py)

    url = '/settings/shop_customers_profile_announcements'
    client.get(url)
    assert client.status == 200


def test_shop_customers_profile_announcement_add(client, web2py):
    '''
        Can we add a new link?
    '''
    url = '/settings/shop_customers_profile_announcement_add'
    client.get(url)
    assert client.status == 200

    data = {'PublicAnnouncement':'on',
            'Title':'Mango',
            'Announcement':'Hello world!',
            'Startdate':'2014-01-01'}

    client.post(url, data=data)
    assert client.status == 200

    assert data['Title'] in client.text


def test_shop_customers_profile_announcement_edit(client, web2py):
    '''
        Can we edit a link?
    '''
    populate_settings_shop_customers_profile_announcements(web2py)

    url = '/settings/shop_customers_profile_announcement_edit?cpaID=1'
    client.get(url)
    assert client.status == 200

    data = {'id':1,
            'PublicAnnouncement':'on',
            'Title':'OMGubuntu',
            'Announcement':'http://www.omgubuntu.co.uk/'}

    client.post(url, data=data)
    assert client.status == 200

    assert data['Title'] in client.text


def test_shop_links(client, web2py):
    '''
        Is the list of links working?
    '''
    populate_settings_shop_links(web2py)
    url = '/settings/shop_links'
    client.get(url)
    assert client.status == 200

    link = web2py.db.shop_links(1)
    assert link['Name'] in client.text


def test_shop_link_add(client, web2py):
    '''
        Can we add a new link?
    '''
    url = '/settings/shop_link_add'
    client.get(url)
    assert client.status == 200

    data = {'Name':'OMGubuntu',
            'URL':'http://www.omgubuntu.co.uk/'}

    client.post(url, data=data)
    assert client.status == 200

    assert data['Name'] in client.text


def test_shop_link_edit(client, web2py):
    '''
        Can we edit a link?
    '''
    populate_settings_shop_links(web2py)

    url = '/settings/shop_link_edit?slID=1'
    client.get(url)
    assert client.status == 200

    data = {'id':1,
            'Name':'OMGubuntu',
            'URL':'http://www.omgubuntu.co.uk/'}

    client.post(url, data=data)
    assert client.status == 200

    assert data['Name'] in client.text


def test_shop_link_display_in_shop(client, web2py):
    '''
        Is a link actually showing in the shop?
    '''
    populate_settings_shop_links(web2py)

    url = '/shop/index'
    client.get(url)
    assert client.status == 200

    link = web2py.db.shop_links(1)
    assert link['Name'] in client.text
    assert link['URL'] in client.text


def test_financial_invoices_groups_index(client, web2py):
    '''
        Is the index page showing?
    '''
    url = '/settings/financial_invoices_groups'
    client.get(url)
    assert client.status == 200
    assert 'Groups' in client.text


def test_financial_invoices_group_add(client, web2py):
    '''
        Can we add a direct debit category?
    '''
    url = '/settings/financial_invoices_group_add'
    client.get(url)
    assert client.status == 200
    assert 'New invoice group' in client.text

    data = dict(Name='Invoices default',
                NextID=1,
                DueDays=30,
                InvoicePrefix='INV')
    client.post(url, data=data)
    assert client.status == 200

    # check redirection
    assert 'Groups' in client.text
    assert data['Name'] in client.text

    '''
        There'll be 2 groups, one is added by the OpenStudio setup() function
    '''
    assert web2py.db(web2py.db.invoices_groups).count() == 2


def test_financial_invoices_group_edit(client, web2py):
    '''
        Can we edit a invoice group?
    '''
    populate(web2py.db.invoices_groups, 1)
    assert web2py.db(web2py.db.invoices_groups).count() == 1

    url = '/settings/financial_invoices_group_edit?igID=1'
    client.get(url)
    assert client.status == 200
    assert 'Edit invoice group' in client.text

    data = dict(id=1,
                Name='Invoices',
                NextID=1,
                DueDays=30,
                InvoicePrefix='INV')
    client.post(url, data=data)
    assert client.status == 200
    assert 'Groups' in client.text # verify redirection
    assert data['Name'] in client.text

    assert web2py.db(web2py.db.invoices_groups).count() > 0


def test_financial_invoices_group_archive(client, web2py):
    '''
        Can we archive a invoice group?
    '''
    # add one to archive
    web2py.db.invoices_groups.insert(
        Name='Invoices',
        NextID=1,
        InvoicePrefix='INV')
    web2py.db.commit()
    assert web2py.db(web2py.db.invoices_groups).count() == 1

    url = '/settings/financial_invoices_group_archive?igID=1'
    client.get(url)
    assert client.status == 200
    assert 'Groups' in client.text

    # count archived payment methods: should be one now
    assert web2py.db(web2py.db.invoices_groups.Archived == True).count() == 1


def test_financial_dd_categories_index(client, web2py):
    '''
        Is the index page showing?
    '''
    url = '/settings/financial_dd_categories'
    client.get(url)
    assert client.status == 200
    assert 'Direct debit categories' in client.text


def test_financial_dd_categories_add(client, web2py):
    '''
        Can we add a direct debit category?
    '''
    url = '/settings/financial_dd_category_add'
    client.get(url)
    assert client.status == 200
    assert 'New direct debit category' in client.text

    data = dict(Name='Invoices',
                 CategoryType='1')
    client.post(url, data=data)
    assert client.status == 200
    assert 'Direct debit categories' in client.text
    assert data['Name'] in client.text

    assert web2py.db(web2py.db.payment_categories).count() == 1


def test_financial_dd_categories_edit(client, web2py):
    '''
        Can we edit a direct debit category?
    '''
    populate(web2py.db.payment_categories, 1)
    assert web2py.db(web2py.db.payment_categories).count() == 1

    url = '/settings/financial_dd_category_edit/1'
    client.get(url)
    assert client.status == 200
    assert 'Edit direct debit category' in client.text

    data = dict(id=1,
                Name='Invoices',
                CategoryType='1')
    client.post(url, data=data)
    assert client.status == 200
    assert 'Direct debit categories' in client.text # verify redirection
    assert data['Name'] in client.text

    assert web2py.db(web2py.db.payment_categories).count() > 0



def test_financial_dd_category_archive(client, web2py):
    '''
        Can we archive a direct debit category?
    '''
    # add one to archive
    populate(web2py.db.payment_categories, 1)
    assert web2py.db(web2py.db.payment_categories).count() == 1
    web2py.db.commit()

    url = '/settings/financial_dd_category_archive?pcID=1'
    client.get(url)
    assert client.status == 200
    assert 'Direct debit categories' in client.text

    # count archived payment methods: should be one now
    assert web2py.db(web2py.db.payment_categories.Archived == True).count() == 1



def test_financial_payment_methods_index(client, web2py):
    '''
        Is the index page showing?
    '''
    url = '/settings/financial_payment_methods'
    client.get(url)
    assert client.status == 200
    assert 'Payment methods' in client.text

    # check OpenStudio generated default methods
    assert 'Cash' in client.text
    assert 'Wire transfer' in client.text
    assert 'Direct debit' in client.text


def test_financial_payment_method_add(client, web2py):
    '''
        Can we add a payment method?
    '''
    url = '/settings/financial_payment_method_add'
    client.get(url)
    assert client.status == 200
    assert 'New payment method' in client.text

    data = dict(Name='PIN')
    client.post(url, data=data)
    assert client.status == 200
    assert 'Payment methods' in client.text
    assert data['Name'] in client.text

    assert web2py.db(web2py.db.payment_methods).count() == 5


def test_financial_payment_method_edit(client, web2py):
    '''
        Can we edit a payment method?
    '''
    # Get URL first so the default payment methods (id 1 - 3) get generated
    url = '/settings/financial_payment_methods'
    client.get(url)
    assert client.status == 200

    populate(web2py.db.payment_methods, 1)
    assert web2py.db(web2py.db.payment_methods).count() == 5
    web2py.db.commit()

    url = '/settings/financial_payment_method_edit/101'
    client.get(url)
    assert client.status == 200
    assert 'Edit payment method' in client.text

    data = dict(id   = 101,
                Name ='PIN')
    client.post(url, data=data)
    assert client.status == 200
    assert 'Payment methods' in client.text # verify redirection
    assert data['Name'] in client.text

    assert web2py.db(web2py.db.payment_methods).count() == 5


def test_financial_payment_method_archive(client, web2py):
    '''
        Can we archive a payment method?
    '''
    # Get URL first so the default payment methods (id 1 - 3) get generated
    url = '/settings/financial_payment_methods'
    client.get(url)
    assert client.status == 200

    # add one extra to archive
    populate(web2py.db.payment_methods, 1)
    assert web2py.db(web2py.db.payment_methods).count() == 5
    web2py.db.commit()

    url = '/settings/financial_payment_method_archive?pmID=101'
    client.get(url)
    assert client.status == 200
    assert 'Payment methods' in client.text

    # count archived payment methods: should be one now
    assert web2py.db(web2py.db.payment_methods.Archived == True).count() == 1


def test_financial_invoices_groups_setup(client, web2py):
    '''
        Is the setup function working and inserting '100' for all
        groups?
    '''
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    products = [ 'subscription',
                 'classcard',
                 'dropin',
                 'trial',
                 'wsp' ]

    for product in products:
        query = (web2py.db.invoices_groups_product_types.ProductType == product) & \
                (web2py.db.invoices_groups_product_types.invoices_groups_id == 100)
        count = web2py.db(query).count()

        assert count == 1


def test_financial_invoices_groups_default_edit(client, web2py):
    '''
        Can we edit the default invoice group for a product type?
    '''
    name = 'ChocolateShake'
    web2py.db.invoices_groups.insert(
        id = 200,
        Archived = False,
        Name     = name
    )
    web2py.db.commit()

    url = '/settings/financial_invoices_groups_default_edit?igptID=1&product=subscription&product_name=Subscriptions'
    client.get(url)
    assert client.status == 200

    data = {
        'id'                 : 1,
        'invoices_groups_id' : 200
    }

    client.post(url, data=data)
    assert client.status == 200
    assert name in client.text


    igpt = web2py.db.invoices_groups_product_types(1)
    assert igpt.invoices_groups_id == 200


def test_access_api_users_index(client, web2py):
    '''
        Can we list the API users?
    '''
    web2py.db.sys_api_users.insert(ActiveUser=True,
                                   Username='magicdesign',
                                   APIKey='1234567890',
                                   Description='magic design user')
    web2py.db.commit()

    url = '/settings/access_api_users'
    client.get(url)
    assert client.status == 200
    assert 'API users' in client.text
    assert 'magicdesign' in client.text

def test_access_api_user(client, web2py):
    '''
        Can we add an api user?
    '''
    url = '/settings/access_api_user_add'
    client.get(url)
    assert client.status == 200
    assert 'New API user' in client.text

    data = dict(Username='magicdesign',
                 Description='Magic design user')
    client.post(url, data=data)
    assert client.status == 200
    assert 'API users' in client.text # verify redirection
    assert data['Username'] in client.text

    assert web2py.db(web2py.db.sys_api_users).count() == 1

    # check whether a key was generated
    api_key = web2py.db.sys_api_users(1).APIKey
    assert api_key != '' and not api_key is None

    ## check whether a new key can be generated
    url = '/settings/access_api_user_generate_new_key/1'
    client.get(url)
    assert client.status == 200
    # check redirection
    assert 'API users' in client.text
    # check whether a new key was generated
    api_new_key = web2py.db.sys_api_users(1).APIKey
    assert api_key != api_new_key

    ## check whether deactivating and activating again works
    # check current state (should be active by default)
    assert web2py.db.sys_api_users(1).ActiveUser == True
    # change the state
    url='/settings/access_api_user_change_active_state/1'
    client.get(url)
    assert client.status == 200
    assert 'API users' in client.text
    assert web2py.db.sys_api_users(1).ActiveUser == False
    # change the state back
    url='/settings/access_api_user_change_active_state/1'
    client.get(url)
    assert client.status == 200
    assert 'API users' in client.text
    assert web2py.db.sys_api_users(1).ActiveUser == True
