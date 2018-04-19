# -*- coding: utf-8 -*-

import re
import string
import random
import pytz

from openstudio.os_gui import OsGui
from general_helpers import represent_validity_units
from general_helpers import represent_subscription_units

### Config ####
# -------------------------------------------------------------------------
# app configuration made easy. Look inside private/appconfig.ini
# -------------------------------------------------------------------------
from gluon.contrib.appconfig import AppConfig
# -------------------------------------------------------------------------
# once in production, remove reload=True to gain full speed
# -------------------------------------------------------------------------
myconf = AppConfig()


### Caching ###

if myconf.get('cache.cache') == 'redis':
    from gluon.contrib.redis_utils import RConn
    from gluon.contrib.redis_cache import RedisCache

    redis_host = str(myconf.get('cache.redis_host'))
    redis_port = str(myconf.get('cache.redis_port'))
    rconn = RConn(redis_host, redis_port)
    cache.redis = RedisCache(redis_conn=rconn, debug=True, with_lock=True)
    # use redis as cache
    cache.ram = cache.disk = cache.redis


#### Custom validators begin #####

class IS_IBAN(object):

    def __init__(self, error_message=T('Invalid IBAN')):
        self.error_message = error_message

    def __call__(self, value):
        # remove whitespace, before, after and in string
        value = value.strip()
        value = value.replace(' ', '')
        value = value.upper()
        try:
            # check if value == string
            if not isinstance(value, str):
                raise TypeError('Account number has to be a string')
            # we have a string, check if the first 2 letters are NL, otherwise
            # always pass for now
            if len(value) >= 2:  # we have something to validate
                first_letters = value[0:2]
                if first_letters.upper() == 'NL':  # check Dutch IBAN
                    if not self._is_dutch_iban(value):
                        raise ValueError('Invalid Dutch IBAN')

            return (value, None)
        except Exception as e:
            return (value, self.error_message)


    def formatter(self, value):
        """
            Always make it uppercase
        """
        return value.strip().upper()


    def _is_dutch_iban(self, value):
        """
            Checks if the value is a Dutch IBAN number
        """
        return_value = False
        if not len(value) == 18:  # validate length
            self.error_message = T('Dutch IBAN should be 18 characters')
            raise ValueError('Account number has wrong length')
        else:
            # perform validation
            first_4_letters = value[0:4]
            check_value = value[4:] + first_4_letters

            return_value = self._convert_to_integer_and_check_valid(
                check_value)

        return return_value


    def _convert_to_integer_and_check_valid(self, check_value):
        """
            Converts letters to integers, following IBAN specs
        """
        replace_map = {}
        for i, letter in enumerate(list(string.ascii_uppercase)):
            replace_map[letter] = unicode(i + 10)

        for k, v in replace_map.iteritems():
            check_value = check_value.replace(k, v)

        check_value = int(check_value)
        valid = check_value % 97  # mod 97

        if valid == 1:
            return_value = True
        else:
            self.error_message = T('IBAN validation failed')
            return_value = False

        return return_value


#### Custom validators end #######

def get_country_codes():
    countries = [{"Name":"Afghanistan","Code":"AF"},{"Name":"Åland Islands","Code":"AX"},{"Name":"Albania","Code":"AL"},{"Name":"Algeria","Code":"DZ"},{"Name":"American Samoa","Code":"AS"},{"Name":"Andorra","Code":"AD"},{"Name":"Angola","Code":"AO"},{"Name":"Anguilla","Code":"AI"},{"Name":"Antarctica","Code":"AQ"},{"Name":"Antigua and Barbuda","Code":"AG"},{"Name":"Argentina","Code":"AR"},{"Name":"Armenia","Code":"AM"},{"Name":"Aruba","Code":"AW"},{"Name":"Australia","Code":"AU"},{"Name":"Austria","Code":"AT"},{"Name":"Azerbaijan","Code":"AZ"},{"Name":"Bahamas","Code":"BS"},{"Name":"Bahrain","Code":"BH"},{"Name":"Bangladesh","Code":"BD"},{"Name":"Barbados","Code":"BB"},{"Name":"Belarus","Code":"BY"},{"Name":"Belgium","Code":"BE"},{"Name":"Belize","Code":"BZ"},{"Name":"Benin","Code":"BJ"},{"Name":"Bermuda","Code":"BM"},{"Name":"Bhutan","Code":"BT"},{"Name":"Bolivia, Plurinational State of","Code":"BO"},{"Name":"Bonaire, Sint Eustatius and Saba","Code":"BQ"},{"Name":"Bosnia and Herzegovina","Code":"BA"},{"Name":"Botswana","Code":"BW"},{"Name":"Bouvet Island","Code":"BV"},{"Name":"Brazil","Code":"BR"},{"Name":"British Indian Ocean Territory","Code":"IO"},{"Name":"Brunei Darussalam","Code":"BN"},{"Name":"Bulgaria","Code":"BG"},{"Name":"Burkina Faso","Code":"BF"},{"Name":"Burundi","Code":"BI"},{"Name":"Cambodia","Code":"KH"},{"Name":"Cameroon","Code":"CM"},{"Name":"Canada","Code":"CA"},{"Name":"Cape Verde","Code":"CV"},{"Name":"Cayman Islands","Code":"KY"},{"Name":"Central African Republic","Code":"CF"},{"Name":"Chad","Code":"TD"},{"Name":"Chile","Code":"CL"},{"Name":"China","Code":"CN"},{"Name":"Christmas Island","Code":"CX"},{"Name":"Cocos (Keeling) Islands","Code":"CC"},{"Name":"Colombia","Code":"CO"},{"Name":"Comoros","Code":"KM"},{"Name":"Congo","Code":"CG"},{"Name":"Congo, the Democratic Republic of the","Code":"CD"},{"Name":"Cook Islands","Code":"CK"},{"Name":"Costa Rica","Code":"CR"},{"Name":"Côte d'Ivoire","Code":"CI"},{"Name":"Croatia","Code":"HR"},{"Name":"Cuba","Code":"CU"},{"Name":"Curaçao","Code":"CW"},{"Name":"Cyprus","Code":"CY"},{"Name":"Czech Republic","Code":"CZ"},{"Name":"Denmark","Code":"DK"},{"Name":"Djibouti","Code":"DJ"},{"Name":"Dominica","Code":"DM"},{"Name":"Dominican Republic","Code":"DO"},{"Name":"Ecuador","Code":"EC"},{"Name":"Egypt","Code":"EG"},{"Name":"El Salvador","Code":"SV"},{"Name":"Equatorial Guinea","Code":"GQ"},{"Name":"Eritrea","Code":"ER"},{"Name":"Estonia","Code":"EE"},{"Name":"Ethiopia","Code":"ET"},{"Name":"Falkland Islands (Malvinas)","Code":"FK"},{"Name":"Faroe Islands","Code":"FO"},{"Name":"Fiji","Code":"FJ"},{"Name":"Finland","Code":"FI"},{"Name":"France","Code":"FR"},{"Name":"French Guiana","Code":"GF"},{"Name":"French Polynesia","Code":"PF"},{"Name":"French Southern Territories","Code":"TF"},{"Name":"Gabon","Code":"GA"},{"Name":"Gambia","Code":"GM"},{"Name":"Georgia","Code":"GE"},{"Name":"Germany","Code":"DE"},{"Name":"Ghana","Code":"GH"},{"Name":"Gibraltar","Code":"GI"},{"Name":"Greece","Code":"GR"},{"Name":"Greenland","Code":"GL"},{"Name":"Grenada","Code":"GD"},{"Name":"Guadeloupe","Code":"GP"},{"Name":"Guam","Code":"GU"},{"Name":"Guatemala","Code":"GT"},{"Name":"Guernsey","Code":"GG"},{"Name":"Guinea","Code":"GN"},{"Name":"Guinea-Bissau","Code":"GW"},{"Name":"Guyana","Code":"GY"},{"Name":"Haiti","Code":"HT"},{"Name":"Heard Island and McDonald Islands","Code":"HM"},{"Name":"Holy See (Vatican City State)","Code":"VA"},{"Name":"Honduras","Code":"HN"},{"Name":"Hong Kong","Code":"HK"},{"Name":"Hungary","Code":"HU"},{"Name":"Iceland","Code":"IS"},{"Name":"India","Code":"IN"},{"Name":"Indonesia","Code":"ID"},{"Name":"Iran, Islamic Republic of","Code":"IR"},{"Name":"Iraq","Code":"IQ"},{"Name":"Ireland","Code":"IE"},{"Name":"Isle of Man","Code":"IM"},{"Name":"Israel","Code":"IL"},{"Name":"Italy","Code":"IT"},{"Name":"Jamaica","Code":"JM"},{"Name":"Japan","Code":"JP"},{"Name":"Jersey","Code":"JE"},{"Name":"Jordan","Code":"JO"},{"Name":"Kazakhstan","Code":"KZ"},{"Name":"Kenya","Code":"KE"},{"Name":"Kiribati","Code":"KI"},{"Name":"Korea, Democratic People's Republic of","Code":"KP"},{"Name":"Korea, Republic of","Code":"KR"},{"Name":"Kuwait","Code":"KW"},{"Name":"Kyrgyzstan","Code":"KG"},{"Name":"Lao People's Democratic Republic","Code":"LA"},{"Name":"Latvia","Code":"LV"},{"Name":"Lebanon","Code":"LB"},{"Name":"Lesotho","Code":"LS"},{"Name":"Liberia","Code":"LR"},{"Name":"Libya","Code":"LY"},{"Name":"Liechtenstein","Code":"LI"},{"Name":"Lithuania","Code":"LT"},{"Name":"Luxembourg","Code":"LU"},{"Name":"Macao","Code":"MO"},{"Name":"Macedonia, the Former Yugoslav Republic of","Code":"MK"},{"Name":"Madagascar","Code":"MG"},{"Name":"Malawi","Code":"MW"},{"Name":"Malaysia","Code":"MY"},{"Name":"Maldives","Code":"MV"},{"Name":"Mali","Code":"ML"},{"Name":"Malta","Code":"MT"},{"Name":"Marshall Islands","Code":"MH"},{"Name":"Martinique","Code":"MQ"},{"Name":"Mauritania","Code":"MR"},{"Name":"Mauritius","Code":"MU"},{"Name":"Mayotte","Code":"YT"},{"Name":"Mexico","Code":"MX"},{"Name":"Micronesia, Federated States of","Code":"FM"},{"Name":"Moldova, Republic of","Code":"MD"},{"Name":"Monaco","Code":"MC"},{"Name":"Mongolia","Code":"MN"},{"Name":"Montenegro","Code":"ME"},{"Name":"Montserrat","Code":"MS"},{"Name":"Morocco","Code":"MA"},{"Name":"Mozambique","Code":"MZ"},{"Name":"Myanmar","Code":"MM"},{"Name":"Namibia","Code":"NA"},{"Name":"Nauru","Code":"NR"},{"Name":"Nepal","Code":"NP"},{"Name":"Netherlands","Code":"NL"},{"Name":"New Caledonia","Code":"NC"},{"Name":"New Zealand","Code":"NZ"},{"Name":"Nicaragua","Code":"NI"},{"Name":"Niger","Code":"NE"},{"Name":"Nigeria","Code":"NG"},{"Name":"Niue","Code":"NU"},{"Name":"Norfolk Island","Code":"NF"},{"Name":"Northern Mariana Islands","Code":"MP"},{"Name":"Norway","Code":"NO"},{"Name":"Oman","Code":"OM"},{"Name":"Pakistan","Code":"PK"},{"Name":"Palau","Code":"PW"},{"Name":"Palestine, State of","Code":"PS"},{"Name":"Panama","Code":"PA"},{"Name":"Papua New Guinea","Code":"PG"},{"Name":"Paraguay","Code":"PY"},{"Name":"Peru","Code":"PE"},{"Name":"Philippines","Code":"PH"},{"Name":"Pitcairn","Code":"PN"},{"Name":"Poland","Code":"PL"},{"Name":"Portugal","Code":"PT"},{"Name":"Puerto Rico","Code":"PR"},{"Name":"Qatar","Code":"QA"},{"Name":"Réunion","Code":"RE"},{"Name":"Romania","Code":"RO"},{"Name":"Russian Federation","Code":"RU"},{"Name":"Rwanda","Code":"RW"},{"Name":"Saint Barthélemy","Code":"BL"},{"Name":"Saint Helena, Ascension and Tristan da Cunha","Code":"SH"},{"Name":"Saint Kitts and Nevis","Code":"KN"},{"Name":"Saint Lucia","Code":"LC"},{"Name":"Saint Martin (French part)","Code":"MF"},{"Name":"Saint Pierre and Miquelon","Code":"PM"},{"Name":"Saint Vincent and the Grenadines","Code":"VC"},{"Name":"Samoa","Code":"WS"},{"Name":"San Marino","Code":"SM"},{"Name":"Sao Tome and Principe","Code":"ST"},{"Name":"Saudi Arabia","Code":"SA"},{"Name":"Senegal","Code":"SN"},{"Name":"Serbia","Code":"RS"},{"Name":"Seychelles","Code":"SC"},{"Name":"Sierra Leone","Code":"SL"},{"Name":"Singapore","Code":"SG"},{"Name":"Sint Maarten (Dutch part)","Code":"SX"},{"Name":"Slovakia","Code":"SK"},{"Name":"Slovenia","Code":"SI"},{"Name":"Solomon Islands","Code":"SB"},{"Name":"Somalia","Code":"SO"},{"Name":"South Africa","Code":"ZA"},{"Name":"South Georgia and the South Sandwich Islands","Code":"GS"},{"Name":"South Sudan","Code":"SS"},{"Name":"Spain","Code":"ES"},{"Name":"Sri Lanka","Code":"LK"},{"Name":"Sudan","Code":"SD"},{"Name":"Suriname","Code":"SR"},{"Name":"Svalbard and Jan Mayen","Code":"SJ"},{"Name":"Swaziland","Code":"SZ"},{"Name":"Sweden","Code":"SE"},{"Name":"Switzerland","Code":"CH"},{"Name":"Syrian Arab Republic","Code":"SY"},{"Name":"Taiwan, Province of China","Code":"TW"},{"Name":"Tajikistan","Code":"TJ"},{"Name":"Tanzania, United Republic of","Code":"TZ"},{"Name":"Thailand","Code":"TH"},{"Name":"Timor-Leste","Code":"TL"},{"Name":"Togo","Code":"TG"},{"Name":"Tokelau","Code":"TK"},{"Name":"Tonga","Code":"TO"},{"Name":"Trinidad and Tobago","Code":"TT"},{"Name":"Tunisia","Code":"TN"},{"Name":"Turkey","Code":"TR"},{"Name":"Turkmenistan","Code":"TM"},{"Name":"Turks and Caicos Islands","Code":"TC"},{"Name":"Tuvalu","Code":"TV"},{"Name":"Uganda","Code":"UG"},{"Name":"Ukraine","Code":"UA"},{"Name":"United Arab Emirates","Code":"AE"},{"Name":"United Kingdom","Code":"GB"},{"Name":"United States","Code":"US"},{"Name":"United States Minor Outlying Islands","Code":"UM"},{"Name":"Uruguay","Code":"UY"},{"Name":"Uzbekistan","Code":"UZ"},{"Name":"Vanuatu","Code":"VU"},{"Name":"Venezuela, Bolivarian Republic of","Code":"VE"},{"Name":"Viet Nam","Code":"VN"},{"Name":"Virgin Islands, British","Code":"VG"},{"Name":"Virgin Islands, U.S.","Code":"VI"},{"Name":"Wallis and Futuna","Code":"WF"},{"Name":"Western Sahara","Code":"EH"},{"Name":"Yemen","Code":"YE"},{"Name":"Zambia","Code":"ZM"},{"Name":"Zimbabwe","Code":"ZW"}]
    country_codes = []
    for country in countries:
        country_codes.append([country['Code'], T(country['Name'])])

    return country_codes

#country_codes = get_country_codes()

country_codes = cache.ram('sys_country_codes',
                           lambda: get_country_codes(),
                           time_expire=259200)


def cache_clear(var_one=None, var_two=None):
    """
        Clears all cache entries on disk & in ram
        # Takes arguments in case it's called from a crud form or SQLFORM.grid
    """
    cache.ram.clear()
    cache.disk.clear()


def cache_clear_customers_subscriptions(cuID):
    """
        Clears subscription cache entries on disk & in ram
    """
    cu_sub_regex = 'openstudio_customer_get_subscriptions_on_date_' + str(cuID) + '*'
    cache.ram.clear(regex=cu_sub_regex)
    cache.disk.clear(regex=cu_sub_regex)


def cache_clear_customers_classcards(cuID):
    """
        Clears subscription cache entries on disk & in ram
    """
    cu_cc_regex = 'openstudio_customer_get_classcards_' + str(cuID) + '*'
    cache.ram.clear(regex=cu_cc_regex)
    cache.disk.clear(regex=cu_cc_regex)


def cache_clear_classschedule(var_one=None, var_two=None):
    """
        Clears the class schedule cache 
        takes 2 dummy arguments in case it's called from a CRUD form or from SQLFORM.grid
    """
    class_schedule_regex = 'openstudio_classschedule_get_day_*'
    cache.ram.clear(regex = class_schedule_regex)
    cache.disk.clear(regex = class_schedule_regex)

    cache_clear_classschedule_api()


def cache_clear_classschedule_api(var_one=None, var_two=None):
    """
        Clears the class schedule api cache
        takes 2 dummy arguments in case it's called from a CRUD form or from SQLFORM.grid
    """
    api_schedule_regex = 'openstudio_api_schedule_get_*'
    cache.ram.clear(regex=api_schedule_regex)
    cache.disk.clear(regex=api_schedule_regex)


def cache_clear_classschedule_trend(var_one=None, var_two=None):
    """
        Clears the class schedule trend column cache
        takes 2 dummy arguments in case it's called from a CRUD form or from SQLFORM.grid
    """
    trend_regex = 'openstudio_classschedule_trend_*'
    cache.ram.clear(regex = trend_regex)
    cache.disk.clear(regex = trend_regex)


def cache_clear_sys_properties():
    """
        Clears the sys_properties keys in cache
        :return: None
    """
    sprop_regex = 'openstudio_system_property_*'
    cache.ram.clear(regex = sprop_regex)
    cache.disk.clear(regex = sprop_regex)


def cache_clear_menu_backend():
    """
        Clears the backend menu's in cache
    """
    menu_regex = 'openstudio_menu_backend_*'
    cache.ram.clear(regex = menu_regex)
    cache.disk.clear(regex = menu_regex)


def cache_clear_workshops(var_one=None, var_two=None):
    """
        Clears the workshops cache
        # accepts two vars to the function can be called from SQLFORM.grid ondelete or crud functions
    """
    workshops_regex = 'openstudio_workshops_*'
    cache.ram.clear(regex = workshops_regex)
    cache.disk.clear(regex = workshops_regex)


def cache_clear_school_subscriptions(var_one=None, var_two=None):
    """
        Clears the school subscriptions cache
        # accepts two vars to the function can be called from SQLFORM.grid ondelete or crud functions
    """
    school_subscriptions_regex = 'openstudio_school_subcriptions_api_*'
    cache.ram.clear(regex = school_subscriptions_regex)
    cache.disk.clear(regex = school_subscriptions_regex)

    # Clear all customer subscriptions, as the cache also stores some school subscription info
    cu_sub_regex = 'openstudio_customer_get_subscriptions_on_date_*'
    cache.ram.clear(regex=cu_sub_regex)
    cache.disk.clear(regex=cu_sub_regex)


def cache_clear_school_classcards(var_one=None, var_two=None):
    """
        Clears the school classcards cache
        # accepts two vars to the function can be called from SQLFORM.grid ondelete or crud functions
    """
    school_classcards_regex = 'openstudio_school_classcards_api_*'
    cache.ram.clear(regex = school_classcards_regex)
    cache.disk.clear(regex = school_classcards_regex)


def cache_clear_school_teachers(var_one=None, var_two=None):
    """
        Clears the school teachers (API) cache
        # accepts two vars to the function can be called from SQLFORM.grid ondelete or crud functions
    """
    school_teachers_api_regex = 'openstudio_school_teachers_api_get'
    cache.ram.clear(regex = school_teachers_api_regex)
    cache.disk.clear(regex = school_teachers_api_regex)


def cache_clear_school_classtypes(var_one=None, var_two=None):
    """
        Clears the school teachers (API) cache
        # accepts two vars to the function can be called from SQLFORM.grid ondelete or crud functions
    """
    school_teachers_api_regex = 'openstudio_school_teachers_api_get'
    cache.ram.clear(regex = school_teachers_api_regex)
    cache.disk.clear(regex = school_teachers_api_regex)


def cache_clear_sys_organizations(var_one=None, var_two=None):
    """
        Clears the workshops cache
        # accepts two vars to the function can be called from SQLFORM.grid ondelete or crud functions
    """
    sys_org_regex = 'openstudio_sys_organizations*'
    cache.ram.clear(regex = sys_org_regex)
    cache.disk.clear(regex = sys_org_regex)


def set_sys_property(property, value):
    """
    :param property: string - name of sys property
    :return: None
    """
    row = db.sys_properties(Property=property)
    if not row:
        db.sys_properties.insert(Property=property,
                                 PropertyValue=value)
    else:
        row.PropertyValue = value
        row.update_record()

    # Clear cache
    cache_clear_sys_properties()


def _get_sys_property(value=None, value_type=None):
    """
        Returns the value of a property in db.sys_properties
    """
    property_value = None
    row = db.sys_properties(Property=value)
    if row:
        property_value = row.PropertyValue

    if value_type:
        try:
            return value_type(property_value)
        except:
            pass

    return property_value


def get_sys_property(value=None, value_type=None):
    """
    :param value: db.sys_properties.Property
    :param value_type: Python data type eg. int
    :return: db.sys_properties.PropertyValue
    """
    cache_key = 'openstudio_system_property_' + value

    # Don't cache when running tests
    if web2pytest.is_running_under_test(request, request.application):
        sprop = _get_sys_property(value, value_type)
    else:
        sprop = cache.ram(cache_key,
                          lambda: _get_sys_property(value, value_type),
                          time_expire=CACHE_LONG)

    return sprop


def set_genders():
    return [['F', T('Female')],
            ['M', T('Male')],
            ['X', T('Other')]]


def set_payment_statuses():
    """
        Return list of payment statuses to use in OpenStudio
    """
    statuses = [['paid', T("Paid")],
                ['open', T("Open")],
                ['overdue', T("Overdue")],
                ['cancelled', T("Cancelled")]
                ]

    return statuses


def set_message_statuses():
    """
        Returns a list of message statuses to use in OpenStudio
    """
    statuses = [['sent', T("Sent")],
                ['fail', T("Failed")],
                ]

    return statuses


def set_invoice_statuses():
    """
        Returns a list of invoice statuses to use in OpenStudio
    """
    statuses = [['draft', T("Draft")],
                ['sent', T("Sent")],
                ['paid', T("Paid")],
                ['cancelled', T("Cancelled")]]

    return statuses


def set_order_statuses():
    """
        Returns a list of order statuses to use in OpenStudio
    """
    statuses = [ [ 'received', T('Received') ],
                 [ 'awaiting_payment', T('Awaiting payment') ],
                 [ 'paid', T('Paid') ],
                 [ 'processing', T('Processing') ],
                 [ 'delivered', T('Delivered') ],
                 [ 'cancelled', T('Cancelled') ] ]

    return statuses


def set_teachers_roles():
    """
        return tuple for teacher roles
    """
    teachers_roles = [[0, T("Normal")],
                      [1, T("Subteacher")],
                      [2, T("Assistant")],
                      [3, T("Karma")]]

    return teachers_roles


def get_invoices_groups_product_types():
    """
        Returns a list of invoices_groups_categories
    """
    categories = [ ['subscription', T('Subscriptions')],
                   ['classcard'   , T('Class cards')],
                   ['dropin'      , T('Drop in classes')],
                   ['trial'       , T('Trial classes')],
                   ['wsp'         , T('Workshop products')],
                   ['shop'        , T('OpenStudio shop (All sales from the shop will go into this group)')] ]

    return categories


def set_validity_units():
    """
        Returns a list of validity times
    """
    validity_units = [ ['days', T('Days')],
                       ['weeks', T('Weeks')],
                       ['months', T('Months')] ]

    return validity_units


def set_subscription_units():
    """
        Returns a list of validity times
    """
    validity_units = [ ['week', T('Week')],
                       ['month', T('Month')] ]

    return validity_units


def set_booking_statuses():
    """
        Returns a list of classes_attendance booking statuses
    """
    booking_statuses = [ ['booked', T('Booked')],
                         ['attending', T('Attending')],
                         ['cancelled', T('Cancelled')] ]

    return booking_statuses


def represent_gender(value, row):
    """
        Helper to represent genders
    """
    return_value = ''
    for gender in GENDERS:
        if value == gender[0]:
            return_value = gender[1]
            break

    return return_value


def compute_birthday(row):
    try:
        dob = row.date_of_birth
    except AttributeError:
        try:
            dob = row.auth_user.date_of_birth
        except AttributeError:
            dob = None


    if not dob is None:
        return datetime.date(1900, dob.month, dob.day)
    else:
        return None


def generate_password(length=30):
    """
        Function to generate a random password.
        Keys are auto generated to increase security.
    """
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    passwd = ''.join(random.SystemRandom().choice(chars)
                     for _ in xrange(length))

    return passwd


def LTE_MENU(menu, _class, li_class, ul_class):
    lte_menu = MENU(menu, _class=_class, li_class=li_class, ul_class=ul_class)
    lte_menu['_data-widget'] = "tree"

    return lte_menu

CACHE_LONG = myconf.get('cache.max_cache_time') # 3 days
GENDERS = set_genders()
VALIDITY_UNITS = set_validity_units()
SUBSCRIPTION_UNITS = set_subscription_units()
teachers_roles = set_teachers_roles()
payment_statuses = set_payment_statuses()
message_statuses = set_message_statuses()
invoice_statuses = set_invoice_statuses()
order_statuses = set_order_statuses()
booking_statuses = set_booking_statuses()


os_gui = OsGui()
