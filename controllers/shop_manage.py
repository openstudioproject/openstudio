# -*- coding: utf-8 -*-

from general_helpers import set_form_id_and_get_submit_button

@auth.requires(auth.has_membership(group_id='Admins') or
               auth.has_permission('read', 'shop_manage_workflow'))
def workflow():
    '''
        Settings to control shop workflows
    '''
    response.title = T('Shop')
    response.subtitle = T('Workflow')
    response.view = 'general/only_content.html'

    shop_requires_complete_profile = get_sys_property('shop_requires_complete_profile')
    shop_classes_advance_booking_limit = get_sys_property('shop_classes_advance_booking_limit')
    shop_classes_cancellation_limit = get_sys_property('shop_classes_cancellation_limit')
    shop_subscriptions_start = get_sys_property('shop_subscriptions_start')

    form = SQLFORM.factory(
        Field('shop_requires_complete_profile', 'boolean',
              default=shop_requires_complete_profile,
              label=T('Orders require complete profiles'),
              comment=T('Require complete profiles before customers can place an order')),
        Field('shop_classes_advance_booking_limit', 'integer',
              default=shop_classes_advance_booking_limit,
              requires=IS_INT_IN_RANGE(0, 1099),
              label=T('Classes advance booking limit in days'),
              comment=T("Number of days in advance customers will be able to book classes")),
        Field('shop_classes_cancellation_limit', 'integer',
              default=shop_classes_cancellation_limit,
              requires=IS_INT_IN_RANGE(0, 745),
              label=T('Classes cancellation limit in hours'),
              comment=T("Number of hours before a class starts a booking can be cancelled while returning credit")),
        Field('shop_subscriptions_start',
              default=shop_subscriptions_start,
              requires=IS_IN_SET([
                  ['today', T('Today')],
                  ['next_month', T('First day of next month')]],
                  zero=None),
              label=T('Subscriptions start date'),
              comment=T("Set the default start date for subscriptions in the shop")),
        submit_button=T("Save"),
        separator=' ',
        formstyle='bootstrap3_stacked'
    )

    result = set_form_id_and_get_submit_button(form, 'MainForm')
    form = result['form']
    submit = result['submit']

    if form.process().accepted:
        # check shop require complete profiles
        shop_requires_complete_profile = request.vars['shop_requires_complete_profile']
        row = db.sys_properties(Property='shop_requires_complete_profile')
        if not row:
            db.sys_properties.insert(Property='shop_requires_complete_profile',
                                     PropertyValue=shop_requires_complete_profile)
        else:
            row.PropertyValue = shop_requires_complete_profile
            row.update_record()

        # check shop_classes_advance_booking_limit
        shop_classes_advance_booking_limit = request.vars['shop_classes_advance_booking_limit']
        row = db.sys_properties(Property='shop_classes_advance_booking_limit')
        if not row:
            db.sys_properties.insert(Property='shop_classes_advance_booking_limit',
                                     PropertyValue=shop_classes_advance_booking_limit)
        else:
            row.PropertyValue = shop_classes_advance_booking_limit
            row.update_record()

        # check shop_classes_cancellation_limit
        shop_classes_cancellation_limit = request.vars['shop_classes_cancellation_limit']
        row = db.sys_properties(Property='shop_classes_cancellation_limit')
        if not row:
            db.sys_properties.insert(Property='shop_classes_cancellation_limit',
                                     PropertyValue=shop_classes_cancellation_limit)
        else:
            row.PropertyValue = shop_classes_cancellation_limit
            row.update_record()

        # check shop_subscriptions_start
        shop_subscriptions_start = request.vars['shop_subscriptions_start']
        row = db.sys_properties(Property='shop_subscriptions_start')
        if not row:
            db.sys_properties.insert(Property='shop_subscriptions_start',
                                     PropertyValue=shop_subscriptions_start)
        else:
            row.PropertyValue = shop_subscriptions_start
            row.update_record()

        # Clear cache
        cache_clear_sys_properties()
        # User feedback
        session.flash = T('Saved')
        # reload so the user sees how the values are stored in the db now
        redirect(URL('workflow'))

    content = DIV(DIV(form, _class='col-md-6'),
                  _class='row')


    return dict(content=content,
                back='',
                menu='',
                save=submit)