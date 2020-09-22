#!/usr/bin/env python

"""py.test test cases to test OpenStudio.

These tests run based on webclient and need web2py server running.
"""
from populate_os_tables import populate_tax_rates
from populate_os_tables import populate_sys_organizations
from populate_os_tables import populate_customers
from populate_os_tables import populate_school_memberships
from populate_os_tables import populate_school_subscriptions
from populate_os_tables import populate_school_subscriptions_groups
from populate_os_tables import populate_school_classcards
from populate_os_tables import populate_school_classcards_groups


from gluon.contrib.populate import populate


def test_employee_delete(client, web2py):
    """
        Can we remove the employee status from a customer?
    """
    populate_customers(web2py)

    row = web2py.db.auth_user(1001)
    row.employee = True
    row.update_record()

    web2py.db.commit()

    url = '/school_properties/employee_delete?uID=1001'
    client.get(url)
    assert client.status == 200

    row = web2py.db.auth_user(1001)
    assert row.employee == False


def test_memberships(client, web2py):
    """
        Is the index page showing?
        Is the current price showing?
    """
    populate_school_memberships(web2py)

    url = '/school_properties/memberships'
    client.get(url)
    assert client.status == 200
    assert 'Memberships' in client.text

    sm = web2py.db.school_memberships(1)

    assert sm.Name in client.text
    assert str(sm.Price) in client.text


def test_membership_add(client, web2py):
    """
        Can we add a membership?
    """
    populate_tax_rates(web2py)

    url = '/school_properties/membership_add'
    client.get(url)
    assert client.status == 200
    assert 'New membership' in client.text

    data = dict(
        Name='Premium membership',
        Description='Premium member of the club',
        Price=40,
        tax_rates_id=1,
        Validity=12,
        ValidityUnit='months'
    )
    client.post(url, data=data)
    assert client.status == 200

    assert 'Memberships' in client.text # verify redirection
    assert data['Name'] in client.text

    assert web2py.db(web2py.db.school_memberships).count() == 1


def test_membership_edit(client, web2py):
    """
        Can we edit a membership?
    """
    populate_tax_rates(web2py)
    web2py.db.school_memberships.insert(
        Name='banana class',
        Price='1235',
        tax_rates_id=1,
    )
    web2py.db.commit()
    assert web2py.db(web2py.db.school_memberships).count() == 1

    url = '/school_properties/membership_edit?smID=1'
    client.get(url)
    assert client.status == 200
    assert 'Edit membership' in client.text

    data = dict(
        id=1,
        Name='Premium membership',
        Description='Premium member of the club',
        Price=40,
        tax_rates_id=1,
        Validity=12,
        ValidityUnit='months'
    )

    client.post(url, data=data)
    assert client.status == 200
    assert 'Membership' in client.text # verify redirection
    assert data['Name'] in client.text

    assert web2py.db(web2py.db.school_memberships).count() > 0


def test_school_subscriptions_index_and_current_price(client, web2py):
    """
        Is the index page showing?
        Is the current price showing?
    """
    web2py.db.school_subscriptions.insert(Name='banana class',
                                          NRofClasses='15')

    web2py.db.school_subscriptions_price.insert(
        school_subscriptions_id = 1,
        Startdate               = '2014-01-01',
        Price                   = 123456)
    web2py.db.commit()

    assert web2py.db(web2py.db.school_subscriptions).count() == 1
    assert web2py.db(web2py.db.school_subscriptions_price).count() == 1

    url = '/school_properties/subscriptions'
    client.get(url)
    assert client.status == 200
    assert 'Subscriptions' in client.text

    assert str(123456) in client.text


def test_school_subscriptions_show_organization(client, web2py):
    """
        Is the organization column showing when we have more than 1 organization
    """
    populate_sys_organizations(web2py, 3)
    populate_school_subscriptions(web2py)

    url = '/school_properties/subscriptions'
    client.get(url)
    assert client.status == 200

    assert 'Organization' in client.text


def test_subscription_add(client, web2py):
    """
        Can we add a subscription?
    """
    url = '/school_properties/subscription_add'
    client.get(url)
    assert client.status == 200
    assert 'New subscription' in client.text

    data = dict(Name='1 Class a week',
                Classes='1',
                SubscriptionUnit='week',
                CancellationPeriod=1,
                CancellationPeriodUnit="month",
                ReconciliationClasses=0,
                SortOrder=0)
                #Unlimited='on')
    client.post(url, data=data)
    assert client.status == 200

    assert 'Subscriptions' in client.text # verify redirection
    assert data['Name'] in client.text

    assert web2py.db(web2py.db.school_subscriptions).count() == 1


def test_subscription_edit(client, web2py):
    """
        Can we edit a subscription?
    """
    web2py.db.school_subscriptions.insert(Name='banana class',
                                          Classes='15',
                                          SubscriptionUnit='week')
    web2py.db.commit()
    assert web2py.db(web2py.db.school_subscriptions).count() == 1

    url = '/school_properties/subscription_edit?ssuID=1'
    client.get(url)
    assert client.status == 200
    assert 'Edit subscription' in client.text

    data = dict(Name='1 Class a week',
                Classes='1',
                SubscriptionUnit='week',
                CancellationPeriod=1,
                CancellationPeriodUnit="month",
                ReconciliationClasses=0)
    client.post(url, data=data)
    assert client.status == 200
    assert 'Subscription' in client.text # verify redirection
    assert data['Name'] in client.text

    assert web2py.db(web2py.db.school_subscriptions).count() > 0


def test_subscriptions_prices(client, web2py):
    """
        Is the index page showing for subcriptions_prices?
    """
    populate_school_subscriptions(web2py)

    url = '/school_properties/subscriptions_prices?ssuID=1'
    client.get(url)
    assert client.status == 200
    assert 'Edit subscription' in client.text


def test_subscription_price_add(client, web2py):
    """
        Can we add a subscription price?
    """
    populate_tax_rates(web2py)
    web2py.db.school_subscriptions.insert(Name='banana class',
                                          NRofClasses='15')
    web2py.db.commit()

    assert web2py.db(web2py.db.school_subscriptions).count() == 1

    url = '/school_properties/subscription_price_add?ssuID=1'
    client.get(url)
    assert client.status == 200
    assert 'New subscription price' in client.text

    data = dict(Startdate    = '2014-01-01',
                Price        = 12345,
                tax_rates_id = 1)
    client.post(url, data=data)
    assert client.status == 200
    assert 'Edit subscription' in client.text # verify redirection
    assert str(data['Price']) in client.text

    assert web2py.db(web2py.db.school_subscriptions_price).count() == 1


def test_subscription_price_edit(client, web2py):
    """
        Can we edit a subscription price?
    """
    populate_tax_rates(web2py)
    web2py.db.school_subscriptions.insert(Name='banana class',
                                          NRofClasses='15')

    web2py.db.school_subscriptions_price.insert(
        school_subscriptions_id = 1,
        Startdate               = '2014-01-01',
        Price                   = 100,
        tax_rates_id            = 1)
    web2py.db.commit()

    assert web2py.db(web2py.db.school_subscriptions).count() == 1
    assert web2py.db(web2py.db.school_subscriptions_price).count() == 1

    url = '/school_properties/subscription_price_edit?ssuID=1&sspID=1'
    client.get(url)
    assert client.status == 200
    assert 'Edit subscription price' in client.text

    data = dict(id           = 1,
                Startdate    = '2014-01-01',
                Price        = 12345,
                tax_rates_id = 1)
    client.post(url, data=data)
    assert client.status == 200
    assert 'Edit subscription' in client.text # verify redirection

    assert str(data['Price']) in client.text

    assert web2py.db(web2py.db.school_subscriptions_price).count() == 1


def test_subscriptions_groups(client, web2py):
    """
        Can we list subscription groups?
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_school_subscriptions_groups(web2py)

    url = '/school_properties/subscriptions_groups'
    client.get(url)
    assert client.status == 200

    ##
    # Check listing of groups
    ##
    group_1 = web2py.db.school_subscriptions_groups(1)
    assert group_1.Name in client.text

    ##
    # Check listing of groups in subscription
    ##
    ssu = web2py.db.school_subscriptions(1)
    assert ssu.Name in client.text


def test_subscriptions_groups_add(client, web2py):
    """
        Can we add a subscriptions group?
    """
    url = '/school_properties/subscriptions_group_add'
    client.get(url)
    assert client.status == 200

    data = {
        'Name': 'Tropical fruits',
        'Description': 'Are delicious'
    }

    client.post(url, data=data)
    assert client.status == 200

    assert data['Name'] in client.text

    assert web2py.db(web2py.db.school_subscriptions_groups).count() == 1


def test_subscriptions_groups_edit(client, web2py):
    """
        Can we add a subscriptions group?
    """
    url = '/school_properties/subscriptions_groups'
    client.get(url)
    assert client.status == 200

    populate_school_subscriptions_groups(web2py)

    data = {
        'id':1,
        'Name': 'Tropical fruits',
        'Description': 'Are delicious'
    }

    url = '/school_properties/subscriptions_group_edit?ssgID=1'
    client.get(url)
    assert client.status == 200

    client.post(url, data=data)
    assert client.status == 200

    assert data['Name'] in client.text

    group = web2py.db.school_subscriptions_groups(1)
    assert group.Name == data['Name']


def test_subscriptions_groups_delete(client, web2py):
    """
        Can we delete a subscription group?
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_school_subscriptions_groups(web2py)

    url = '/school_properties/subscriptions_groups_delete?ssgID=1'
    client.get(url)
    assert client.status == 200

    query = (web2py.db.school_subscriptions_groups.id == 1)
    assert web2py.db(query).count() == 0


def test_subscriptions_groups_subscriptions(client, web2py):
    """
        Is the list of current subscriptions in a group showing correctly?
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_school_subscriptions_groups(web2py)

    url = '/school_properties/subscriptions_group_subscriptions?ssgID=1'
    client.get(url)
    assert client.status == 200

    query = (web2py.db.school_subscriptions_groups_subscriptions.school_subscriptions_groups_id == 1)
    rows = web2py.db(query).select(web2py.db.school_subscriptions_groups_subscriptions.school_subscriptions_id)
    for row in rows:
        assert web2py.db.school_subscriptions(row.school_subscriptions_id).Name in client.text


def test_subscriptions_groups_subscriptions_add(client, web2py):
    """
        Can we add subscriptions to a subscriptions group?
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_school_subscriptions_groups(web2py)

    current_count = web2py.db(
        web2py.db.school_subscriptions_groups_subscriptions.school_subscriptions_groups_id == 1).count()

    url = '/school_properties/subscriptions_group_subscription_add?ssgID=1'
    client.get(url)
    assert client.status == 200

    data = {
        'school_subscriptions_id': 5
    }

    url = '/school_properties/subscriptions_group_subscription_add?ssgID=1'
    client.post(url, data=data)
    assert client.status == 200

    new_count = web2py.db(
        web2py.db.school_subscriptions_groups_subscriptions.school_subscriptions_groups_id == 1).count()

    assert new_count == current_count + 1

    ##
    # Check that subscriptions already in the group aren't in the drop down list anymore
    ##
    client.get(url)
    assert client.status == 200

    query = (web2py.db.school_subscriptions_groups_subscriptions.school_subscriptions_groups_id == 1)
    rows = web2py.db(query).select(web2py.db.school_subscriptions_groups_subscriptions.school_subscriptions_id)
    for row in rows:
        assert not web2py.db.school_subscriptions(row.school_subscriptions_id).Name in client.text


def test_school_classcards_index(client, web2py):
    """
        Is the index page showing?
    """
    url = '/school_properties/classcards'
    client.get(url)
    assert client.status == 200
    assert 'Class cards' in client.text


def test_school_classcards_show_organization(client, web2py):
    """
        Is the organization column showing when we have more than 1 organization
    """
    populate_sys_organizations(web2py, 3)
    populate_school_classcards(web2py, 5)

    url = '/school_properties/classcards'
    client.get(url)
    assert client.status == 200

    assert 'Organization' in client.text



def test_classcard_add(client, web2py):
    """
        Can we add a class card?
    """
    populate_tax_rates(web2py)

    url = '/school_properties/classcard_add'
    client.get(url)
    assert client.status == 200
    assert 'New class card' in client.text

    data = dict(Name='Regular card',
                Description='test',
                Price=125,
                tax_rates_id=1,
                Classes=10,
                Validity=3,
                ValidityUnit='months')
    client.post(url, data=data)
    assert client.status == 200
    assert 'Class cards' in client.text # verify redirection
    assert data['Name'] in client.text

    assert web2py.db(web2py.db.school_classcards).count() == 1


def test_classcard_edit(client, web2py):
    """
        Can we edit a classcard?
    """
    populate_tax_rates(web2py)

    web2py.db.school_classcards.insert(Name='Gorilla card',
                                       Description='test',
                                       Price='125',
                                       tax_rates_id=1,
                                       Classes='1000',
                                       Validity='3',
                                       ValidityUnit='months')
    web2py.db.commit()
    assert web2py.db(web2py.db.school_classcards).count() == 1

    url = '/school_properties/classcard_edit/1'
    client.get(url)
    assert client.status == 200
    assert 'Edit class card' in client.text

    data = dict(id=1,
                Name='Regular card',
                Description='test',
                Price='125',
                tax_rates_id=1,
                Classes='10',
                Validity='3',
                ValidityUnit='months')
    client.post(url, data=data)
    assert client.status == 200
    assert 'Class cards' in client.text # verify redirection
    assert data['Name'] in client.text

    assert web2py.db(web2py.db.school_classcards).count() == 1
    
    
def test_classcardss_groups(client, web2py):
    """
        Can we list classcard groups?
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_school_classcards_groups(web2py)

    url = '/school_properties/classcards_groups'
    client.get(url)
    assert client.status == 200

    ##
    # Check listing of groups
    ##
    group_1 = web2py.db.school_classcards_groups(1)
    assert group_1.Name in client.text

    ##
    # Check listing of groups in classcard
    ##
    sc = web2py.db.school_classcards(1)
    assert sc.Name in client.text


def test_classcards_groups_add(client, web2py):
    """
        Can we add a classcards group?
    """
    url = '/school_properties/classcards_group_add'
    client.get(url)
    assert client.status == 200

    data = {
        'Name': 'Tropical fruits',
        'Description': 'Are delicious'
    }

    client.post(url, data=data)
    assert client.status == 200

    assert data['Name'] in client.text

    assert web2py.db(web2py.db.school_classcards_groups).count() == 1


def test_classcards_groups_edit(client, web2py):
    """
        Can we add a classcards group?
    """
    url = '/school_properties/classcards_groups'
    client.get(url)
    assert client.status == 200

    populate_school_classcards_groups(web2py)

    data = {
        'id':1,
        'Name': 'Tropical fruits',
        'Description': 'Are delicious'
    }

    url = '/school_properties/classcards_group_edit?scgID=1'
    client.get(url)
    assert client.status == 200

    client.post(url, data=data)
    assert client.status == 200

    assert data['Name'] in client.text

    group = web2py.db.school_classcards_groups(1)
    assert group.Name == data['Name']


def test_classcards_groups_delete(client, web2py):
    """
        Can we delete a classcard group?
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_school_classcards_groups(web2py)

    url = '/school_properties/classcards_groups_delete?scgID=1'
    client.get(url)
    assert client.status == 200

    query = (web2py.db.school_classcards_groups.id == 1)
    assert web2py.db(query).count() == 0


def test_classcards_groups_classcards(client, web2py):
    """
        Is the list of current classcards in a group showing correctly?
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_school_classcards_groups(web2py)

    url = '/school_properties/classcards_group_classcards?scgID=1'
    client.get(url)
    assert client.status == 200

    query = (web2py.db.school_classcards_groups_classcards.school_classcards_groups_id == 1)
    rows = web2py.db(query).select(web2py.db.school_classcards_groups_classcards.school_classcards_id)
    for row in rows:
        assert web2py.db.school_classcards(row.school_classcards_id).Name in client.text


def test_classcards_groups_classcards_add(client, web2py):
    """
        Can we add classcards to a classcards group?
    """
    url = '/default/user/login'
    client.get(url)
    assert client.status == 200

    populate_school_classcards_groups(web2py)

    current_count = web2py.db(
        web2py.db.school_classcards_groups_classcards.school_classcards_groups_id == 1).count()

    url = '/school_properties/classcards_group_classcard_add?scgID=1'
    client.get(url)
    assert client.status == 200

    data = {
        'school_classcards_id': 5
    }

    url = '/school_properties/classcards_group_classcard_add?scgID=1'
    client.post(url, data=data)
    assert client.status == 200

    new_count = web2py.db(
        web2py.db.school_classcards_groups_classcards.school_classcards_groups_id == 1).count()

    assert new_count == current_count + 1

    ##
    # Check that classcards already in the group aren't in the drop down list anymore
    ##
    client.get(url)
    assert client.status == 200

    query = (web2py.db.school_classcards_groups_classcards.school_classcards_groups_id == 1)
    rows = web2py.db(query).select(web2py.db.school_classcards_groups_classcards.school_classcards_id)
    for row in rows:
        assert not web2py.db.school_classcards(row.school_classcards_id).Name in client.text


def test_school_levels_index(client, web2py):
    """
        Is the index page showing?
    """
    url = '/school_properties/levels'
    client.get(url)
    assert client.status == 200
    assert 'Practice levels' in client.text


def test_school_level_add(client, web2py):
    """
        Can we add a school_level?
    """
    url = '/school_properties/level_add'
    client.get(url)
    assert client.status == 200
    assert 'New practice level' in client.text

    data = dict(Name='Beginner')
    client.post(url, data=data)
    assert client.status == 200
    assert 'Practice levels' in client.text # verify redirection
    assert data['Name'] in client.text

    assert web2py.db(web2py.db.school_levels).count() == 1


def test_school_level_edit(client, web2py):
    """
        Can we edit a school_level?
    """
    populate(web2py.db.school_levels, 1)
    assert web2py.db(web2py.db.school_levels).count() == 1

    url = '/school_properties/level_edit/1'
    client.get(url)
    assert client.status == 200
    assert 'Edit practice level' in client.text

    data = dict(id=1,
                Name='Beginner')
    client.post(url, data=data)
    assert client.status == 200
    assert 'Practice levels' in client.text # verify redirection
    assert data['Name'] in client.text

    assert web2py.db(web2py.db.school_levels).count() > 0

def test_discovery_index(client, web2py):
    """
        Is the index page showing?
    """
    url = '/school_properties/discovery'
    client.get(url)
    assert client.status == 200
    assert 'Discovery' in client.text

def test_discovery_add(client, web2py):
    """
        Can we add a way of discovery?
    """
    url = '/school_properties/discovery_add'
    client.get(url)
    assert client.status == 200
    assert 'New way of discovery' in client.text

    data = dict(Name='Google')
    client.post(url, data=data)
    assert client.status == 200
    assert 'Discovery' in client.text # verify redirection
    assert data['Name'] in client.text

    assert web2py.db(web2py.db.school_discovery).count() == 1

def test_discovery_edit(client, web2py):
    """
        Can we edit a way of discovery?
    """
    populate(web2py.db.school_discovery, 1)
    assert web2py.db(web2py.db.school_discovery).count() == 1

    url = '/school_properties/discovery_edit/1'
    client.get(url)
    assert client.status == 200
    assert 'Edit way of discovery' in client.text

    data = dict(id=1,
                Name='Google')
    client.post(url, data=data)
    assert client.status == 200
    assert 'Discovery' in client.text # verify redirection
    assert data['Name'] in client.text

    assert web2py.db(web2py.db.school_discovery).count() > 0

def test_classtypes_index(client, web2py):
    """
        Is the index page showing?
    """
    url = '/school_properties/classtypes'
    client.get(url)
    assert client.status == 200
    assert 'Class types' in client.text

def test_classtype_add(client, web2py):
    """
        Can we add a classtype?
    """
    url = '/school_properties/classtype_add'
    client.get(url)
    assert client.status == 200
    assert 'New class type' in client.text

    data = dict(Name='Mysore style')
    client.post(url, data=data)
    assert client.status == 200
    assert 'Class types' in client.text # verify redirection
    assert data['Name'] in client.text

    assert web2py.db(web2py.db.school_classtypes).count() == 1

def test_classtype_edit(client, web2py):
    """
        Can we edit a classtype?
    """
    populate(web2py.db.school_classtypes, 1)
    assert web2py.db(web2py.db.school_classtypes).count() == 1

    url = '/school_properties/classtype_edit/1'
    client.get(url)
    assert client.status == 200
    assert 'Edit class type' in client.text

    data = dict(id=1,
                Name='Mysore style')
    client.post(url, data=data)
    assert client.status == 200
    assert 'Class types' in client.text # verify redirection
    assert data['Name'] in client.text

    assert web2py.db(web2py.db.school_classtypes).count() > 0

def test_locations_index(client, web2py):
    """
        Is the index page showing?
    """
    url = '/school_properties/locations'
    client.get(url)
    assert client.status == 200
    assert 'Locations' in client.text

def test_location_add(client, web2py):
    """
        Can we add a location?
    """
    url = '/school_properties/location_add'
    client.get(url)
    assert client.status == 200
    assert 'New location' in client.text

    data = dict(Name='Maastricht')
    client.post(url, data=data)
    assert client.status == 200
    assert 'Locations' in client.text # verify redirection
    assert data['Name'] in client.text

    assert web2py.db(web2py.db.school_locations).count() == 1

def test_location_edit(client, web2py):
    """
        Can we edit a location?
    """
    populate(web2py.db.school_locations, 1)
    assert web2py.db(web2py.db.school_locations).count() == 1

    url = '/school_properties/location_edit/1'
    client.get(url)
    assert client.status == 200
    assert 'Edit location' in client.text

    data = dict(id=1,
                Name='Maastricht')
    client.post(url, data=data)
    assert client.status == 200
    assert 'Locations' in client.text # verify redirection
    assert data['Name'] in client.text

    assert web2py.db(web2py.db.school_locations).count() > 0

def test_language_index(client, web2py):
    """
        Is the index page showing?
    """
    url = '/school_properties/languages'
    client.get(url)
    assert client.status == 200
    assert 'Languages' in client.text

def test_languages_add(client, web2py):
    """
        Can we add a language?
    """
    url = '/school_properties/language_add'
    client.get(url)
    assert client.status == 200
    assert 'New language' in client.text

    data = dict(Name='Dutch')
    client.post(url, data=data)
    assert client.status == 200
    assert 'Languages' in client.text # verify redirection
    assert data['Name'] in client.text

    assert web2py.db(web2py.db.school_languages).count() == 1

def test_language_edit(client, web2py):
    """
        Can we edit a language?
    """
    web2py.db.school_languages.insert(Name="Dutch")
    web2py.db.commit()
    assert web2py.db(web2py.db.school_languages).count() == 1

    url = '/school_properties/language_edit/1'
    client.get(url)
    assert client.status == 200
    assert 'Edit language' in client.text

    data = dict(id=1,
                Name='English')
    client.post(url, data=data)
    assert client.status == 200
    assert 'Languages' in client.text # verify redirection
    assert data['Name'] in client.text

    assert web2py.db(web2py.db.school_languages).count() > 0

def test_shifts_index(client, web2py):
    """
        Is the index page showing?
    """
    url = '/school_properties/shifts'
    client.get(url)
    assert client.status == 200
    assert 'Shifts' in client.text

def test_shifts_add(client, web2py):
    """
        Can we add a shift?
    """
    url = '/school_properties/shifts_add'
    client.get(url)
    assert client.status == 200
    assert 'New shift' in client.text

    data = dict(Name='Deskwork')
    client.post(url, data=data)
    assert client.status == 200
    assert 'Shifts' in client.text # verify redirection
    assert data['Name'] in client.text

    assert web2py.db(web2py.db.school_shifts).count() == 1

def test_shifts_edit(client, web2py):
    """
        Can we edit a language?
    """
    web2py.db.school_shifts.insert(Name="Deskwork")
    web2py.db.commit()
    assert web2py.db(web2py.db.school_shifts).count() == 1

    url = '/school_properties/shifts_edit?ssID=1'
    client.get(url)
    assert client.status == 200
    assert 'Edit shift' in client.text

    data = dict(id=1,
                Name='Peeling bananas')
    client.post(url, data=data)
    assert client.status == 200
    assert 'Shifts' in client.text # verify redirection
    assert data['Name'] in client.text

    assert web2py.db(web2py.db.school_shifts).count() > 0
    