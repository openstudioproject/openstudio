# -*- coding: utf-8 -*-

from gluon import *

class OsForms:
    def set_form_id_and_get_submit_button(self, form, form_id):
        """
            :param form: html form
            :param form_id: form id to be set
            :return: form with id and submit button
        """
        form_element = form.element('form')
        form['_id'] = form_id

        elements = form.elements('input, select, textarea')
        for element in elements:
            element['_form'] = form_id

        submit = form.element('input[type=submit]')

        return dict(form=form, submit=submit)


    def get_crud_form_create(self,
                             db_table,
                             return_url,
                             submit_button='',
                             onaccept=[],
                             formstyle="bootstrap3_stacked",
                             form_id="MainForm",
                             ):
        """
            Return a crud form to add a record to the database
        """
        T = current.globalenv['T']
        crud = current.globalenv['crud']

        crud.messages.submit_button = submit_button or T("Save")
        crud.messages.record_created = T("Saved")
        crud.settings.create_next = return_url
        crud.settings.create_onaccept = onaccept
        crud.settings.formstyle = formstyle
        form = crud.create(db_table)

        result = self.set_form_id_and_get_submit_button(form, form_id)
        # This contains ['form'] and ['submit']
        return result


    def get_crud_form_update(self,
                             db_table,
                             return_url,
                             record_id,
                             submit_button='',
                             onaccept=[],
                             formstyle="bootstrap3_stacked",
                             form_id="MainForm"
                             ):
        """
            Return a crud form to add a record to the database
        """
        T = current.globalenv['T']
        crud = current.globalenv['crud']

        crud.messages.submit_button = submit_button or T("Save")
        crud.messages.record_updated = T("Saved")
        crud.settings.update_next = return_url
        crud.settings.update_onaccept = onaccept
        crud.settings.formstyle = formstyle
        form = crud.update(db_table, record_id)

        result = self.set_form_id_and_get_submit_button(form, form_id)
        # This contains ['form'] and ['submit']
        return result


    def get_month_year_form(self, year=None, month=None, submit_button=''):
        """
            :return: month & year form
        """
        from general_helpers import get_months_list
        months = get_months_list()

        # Set default values
        T = current.T
        TODAY_LOCAL = current.globalenv['TODAY_LOCAL']
        if not year:
            year = TODAY_LOCAL.year
        if not month:
            month = TODAY_LOCAL.month
        if not submit_button:
            submit_button = T('Submit')


        form = SQLFORM.factory(
            Field('month',
                  requires=IS_IN_SET(months, zero=None),
                  default=month,
                  label=T("Month")),
            Field('year', 'integer',
                  default=year,
                  label=T("Year")),
            submit_button=submit_button,
            formstyle='bootstrap3_stacked'
        )

        # form.attributes['_name'] = 'form_select_date'
        # form.attributes['_class'] = 'overview_form_select_date'

        input_month = form.element('select[name=month]')
        # input_month.attributes['_onchange'] = "this.form.submit();"

        input_year = form.element('input[name=year]')
        # input_year.attributes['_onchange'] = "this.form.submit();"
        input_year.attributes['_type'] = 'number'
        # input_year.attributes['_class']    = 'input_margins'

        form.element('input[name=year]')

        result = self.set_form_id_and_get_submit_button(form, 'MainForm')


        return dict(form = result['form'],
                    submit = result['submit'])
