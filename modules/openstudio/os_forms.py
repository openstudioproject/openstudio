# -*- coding: utf-8 -*-

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

