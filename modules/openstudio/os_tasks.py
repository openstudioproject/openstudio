# -*- coding: utf-8 -*-
from gluon import *

class Tasks:
    def add_get_modal(self, add_vars):
        '''
            Returns add button and modal
        '''
        T = current.T
        os_gui = current.globalenv['os_gui']

        modal_content = DIV(
            LOAD('tasks', 'add.load',
                 vars=add_vars,
                 ajax_trap=True,
                 content=os_gui.get_ajax_loader()))

        modal_title = T("Add Task")

        button_text = os_gui.get_modal_button_icon('add', T("Add"))
        result = os_gui.get_modal(
            button_text=button_text,
            button_class='pull-right btn-sm',
            modal_title=modal_title,
            modal_content=modal_content,
            modal_footer_content=os_gui.get_submit_button('task_add'),
            # modal_size    = '',
            modal_class='modal_add_task'
        )
        add = SPAN(result['button'], result['modal'])

        return add
