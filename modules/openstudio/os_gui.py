# -*- coding: utf-8 -*-
"""
    This file holds mail related classes
"""

# Import all helpers, etc.
from gluon import *

class OsGui:
    """
        This class contains all helper functions for the OpenStudio UI
    """
    def get_button(self,
                   button_type,
                   url,
                   tooltip="",
                   title='',
                   _class='',
                   _id='',
                   _style='',
                   _target='',
                   _disabled=False,
                   onclick=None,
                   cid=None,
                   btn_size='btn-sm',
                   btn_class='btn-default'):
        """
            This function returns a button of type "button_type" and redirects to url "url".
            See below for supported button types
            The tooltip argument can be used to specify text shown when the mouse hovers over the button
        """
        if button_type == 'add':
            title = title or current.T('Add')
            icon = "fa fa-plus"
        elif button_type == 'add_class':
            title = current.T("Add class")
            icon = "fa fa-plus"
        elif button_type == 'accept':
            title = title
            icon = 'fa fa-check'
        elif button_type == 'archive':
            title = current.T('')
            icon = 'fa fa-archive'
        elif button_type == 'astronaut':
            title = title
            icon = 'fa fa-grav'
        elif button_type == 'barcode':
            icon = 'fa fa-barcode'
        elif button_type == 'edit':
            title = title
            icon = "fa fa-pencil"
        elif button_type == 'edit_notext':
            title = ''
            icon = "fa fa-pencil"
        elif button_type == 'edit_custom':
            title = current.T(title)
            icon = "fa fa-pencil"
        elif button_type == 'delete':
            title = current.T("Delete")
            icon = "fa fa-times"
        elif button_type == 'delete_notext':
            btn_class='btn-danger'
            title = current.T("")
            icon = "fa fa-times"
        elif button_type == 'cancel':
            title = title
            icon = 'fa fa-ban'
        elif button_type == 'cancel_notext':
            title = current.T('')
            icon = 'fa fa-ban'
        elif button_type == 'calendar_notext':
            title = current.T('')
            icon = 'fa fa-calendar-o'
        elif button_type == 'ok_notext':
            title = current.T('')
            icon = 'fa fa-check'
        elif button_type == 'list_notext':
            title = current.T('')
            icon = 'fa fa-list'
        elif button_type == 'pending':
            title = title
            icon = 'fa fa-hourglass2'
        elif button_type == 'user_notext':
            title = current.T('')
            icon = 'fa fa-user'
        elif button_type == 'user':
            title = title
            icon = 'fa fa-user'
        elif button_type == 'back':
            title = current.T("Back") if not title else title
            icon = "fa fa-arrow-left"
            btn_class = 'btn-back'
        elif button_type == 'back_bs':
            title = current.T("Back") if not title else title
            icon = "fa fa-arrow-left"
        elif button_type == 'duplicate':
            title = title
            tooltip = current.T("Duplicate")
            icon = 'fa fa-clone'
        elif button_type == 'list_to_teacher':
            title = current.T("List to teacher")
            icon = 'fa fa-envelope-open-o'
        elif button_type == 'next_no_text':
            title = ''
            icon = 'fa fa-arrow-right'
        elif button_type == 'previous_no_text':
            title = ''
            icon = 'fa fa-arrow-left'
        elif button_type == 'list':
            title = title
            icon = 'fa fa-list'
        elif button_type == 'download':
            title = title
            icon = 'fa fa-cloud-download'
        elif button_type == 'credit-card':
            title = title
            icon = 'fa fa-credit-card'
        elif button_type == 'file':
            title = title
            icon  = 'fa fa-file-o'
        elif button_type == 'print':
            title = title
            icon  = 'fa fa-print'
        elif button_type == 'repeat':
            title = title
            icon = 'fa fa-repeat'
        elif button_type == 'search':
            title = title
            icon  = 'fa fa-search'
        elif button_type == 'shopping-cart':
            title = title
            icon = self.get_icon('shopping-cart')
        elif button_type == 'ticket':
            title = title
            icon = 'fa fa-ticket'
        elif button_type == 'noicon':
            title = title
            icon = ''

        else:
            title = current.T("Invalid button type, please check...")
            icon = ''

        if _class:
            _class = "btn" + ' ' + btn_class + ' ' + btn_size + ' ' + _class
        else:
            _class = "btn" + ' ' + btn_class + ' ' +  btn_size

        if not cid:
            button = A(SPAN(_class=icon), ' ',
                       title,
                       _class=_class,
                       _id=_id,
                       _href=url,
                       _onclick=onclick,
                       _title=tooltip,
                       _style=_style,
                       _target=_target)
        else:
            button = A(SPAN(_class=icon), ' ',
                       title,
                       _class=_class,
                       _id=_id,
                       _href=url,
                       _onclick=onclick,
                       _title=tooltip,
                       _style=_style,
                       _target=_target,
                       cid=cid)

        if _disabled:
            button['_disabled'] = 'disabled'
            button['_href'] = '#'
            button['_onclick'] = ''

        return button


    def get_submit_button(self, form_id, btn_size=''):
        """
        :param form_id: string
        :return: INPUT()
        """
        T = current.T

        return INPUT(_type='submit',
                     _value=T('Save'),
                     _class='btn btn-primary ' + btn_size,
                     _form=form_id)


    def get_modal_button_icon(self, button_type,
                                    button_text = ''):
        """
            Returns modal button text and icon for use with modals
        """

        if button_type == 'add':
            btn_icon = SPAN(_class='fa fa-plus')
        if button_type == 'credit-card':
            btn_icon = SPAN(_class='fa fa-credit-card')

        button = SPAN(btn_icon, ' ', button_text)

        return XML(button)


    def _get_modal_button(self,
                          button_text,
                          button_class,
                          button_id,
                          modal_class,
                          button_title = ''):
        """
            Returns a button that can be used to access the modal
        """
        button_xml = '<button type="button" class="btn btn-default '
        if button_class:
            button_xml += button_class
        button_xml += '" '
        if button_id:
            button_xml += ' id="' + button_id + '" '
        if button_title:
            try:
                button_xml += ' title="' + button_title + '" '
            except:
                button_xml += ' title="' + button_title + '" '
        button_xml += 'data-toggle="modal" data-target=".' + modal_class + '"> '
        try:
            button_xml += button_text
        except AttributeError:
            # button_xml might be XML() or other object that doesn't have a decode method
            button_xml += button_text
        button_xml += '</button>'
        return XML(button_xml)


    def _get_modal_button_close(self, close_id):
        """
            Returns a close button for the modal
        """
        button_xml = '<button type="button" class="close" '
        if close_id:
            button_xml += ' id="' + close_id + '" '
        button_xml += 'data-dismiss="modal" aria-label="Close">'
        button_xml += '<span aria-hidden="true">×</span></button>'
        return XML(button_xml)


    def get_modal(self,
                  button_text='',
                  button_id='',
                  button_class='',
                  button_title='',
                  close_id='',
                  modal_title='',
                  modal_content='',
                  modal_footer_content='',
                  modal_class='',
                  modal_id='',
                  modal_size=''):
        """
            This method returns a modal with button
        """
        button = self._get_modal_button(button_text,
                                        button_class,
                                        button_id,
                                        modal_class,
                                        button_title)
        button_close = self._get_modal_button_close(close_id)

        modal_size_class = 'modal-dialog'
        if modal_size == 'sm':
            modal_size_class += ' modal-sm'
        elif modal_size == 'lg':
            modal_size_class += ' modal-lg'

        modal_class = 'modal fade ' + modal_class

        btn_close = XML("""<button type="button" class="btn btn-default pull-left btn-modal-close" data-dismiss="modal">Close</button>""")

        modal = DIV(DIV(DIV(DIV(button_close,
                                H4(modal_title, _class='modal-title'),
                                _class='modal-header'),
                                DIV(modal_content, _class='modal-body'),
                                DIV(btn_close, modal_footer_content, _class='modal-footer'),
                            _class='modal-content'),
                    _class=modal_size_class),
                _class=modal_class,
                _id=modal_id,
                _tabindex='-1',
                _role='dialog',
                )

        return {'modal':modal,
                'button':button}


    def get_box_table(self,
                      title,
                      table,
                      box_class='box-primary',
                      show_footer=False,
                      footer_content=''):
        """
        :param title: Box title
        :param table: html table
        :param box_class: box class
        :return: div box
        """
        footer = ''
        if show_footer:
            footer = DIV(footer_content,
                         _class='box box-footer')

        return DIV(DIV(H3(title, _class='box-title'),
                   _class='box-header'),
                   DIV(table, _class='box-body no-padding'),
                   footer,
                   _class='box ' + box_class)


    def get_box(self,
                title,
                content,
                box_class='box-primary',
                box_tools='',
                with_border=False,
                show_footer=False,
                footer_padding=True,
                footer_content=''):
        """
        :param title: Box title
        :param table: html table
        :param box_class: box class
        :return: div box
        """
        header_class = 'box-header'
        if with_border:
            header_class += ' with-border'

        footer_class = 'box-footer'
        if not footer_padding:
            footer_class += ' no-padding'

        footer = ''
        if show_footer:
            footer = DIV(footer_content,
                         _class=footer_class)

        return DIV(DIV(H3(title, _class='box-title'),
                   DIV(box_tools, _class='box-tools pull-right'),
                   _class=header_class),
                   DIV(content, _class='box-body'),
                   footer,
                   _class='box ' + box_class)


    def get_panel_table(self,
                        title,
                        table,
                        panel_class='panel-primary',
                        div_class='',
                        show_footer=False,
                        footer_content=''):
        """
            Returns a panel with a table as content
        """
        _class = 'panel ' + panel_class + ' ' + div_class

        footer = ''
        if show_footer:
            footer = DIV(footer_content, _class='panel-footer')

        panel = DIV(DIV(H3(title, _class='panel-title'),
                    _class='panel-heading'),
                    table,
                    footer,
                _class=_class)

        return panel


    def get_panel(self, title,
                        content,
                        panel_class='panel-primary',
                        div_class=''):
        """
            Returns a panel with a regular content
        """
        _class = 'panel ' + panel_class + ' ' + div_class

        panel = DIV(DIV(H3(title, _class='panel-title'),
                    _class='panel-heading'),
                    DIV(content, _class='panel-body'),
                _class=_class)

        return panel

    def get_panel_no_title(self, content,
                                 panel_class='panel-default',
                                 div_class=''):
        """
            Returns a panel with regular content, but without a title/header
        """
        _class = 'panel ' + panel_class + ' ' + div_class

        panel = DIV(DIV(content, _class='panel-body'),
                _class=_class)

        return panel


    # def get_direct_chat(self, messages):
    #     """
    #         :param messages: [ [message, subject, datetime], ... ]
    #         :return: direct message layout
    #     """
    #     pass


    # def get_direct_chat_input_form(self):
    #     """
    #         :return: html form
    #     """
    #

        #         < div
        #
        #         class ="input-group" >
        #
        #         < input
        #         type = "text"
        #         name = "message"
        #         placeholder = "Type Message ..."
        #
        #         class ="form-control" >
        #
        #         < span
        #
        #         class ="input-group-btn" >
        #
        #         < button
        #         type = "button"
        #
        #         class ="btn btn-danger btn-flat" > Send < / button >
        #
        #         < / span >
        #
        # < / div >



    def get_form_group(self, label, widget):
        """
            Returns bootstrap input group
        """
        return DIV(LABEL(label), widget, _class='form-group')


    def get_badge(self, value):
        """
            Returns a span with a badge class
        """
        _class = 'badge'

        return SPAN(value, _class=_class)


    def get_label(self, label_type, value, title=''):
        """
            Returns a span with a badge class
        """
        _class = 'label '
        if label_type == 'default':
            _class += 'label-default'
        elif label_type == 'primary':
            _class += 'label-primary'
        elif label_type == 'success':
            _class += 'label-success'
        elif label_type == 'warning':
            _class += 'label-warning'
        elif label_type == 'danger':
            _class += 'label-danger'
        elif label_type == 'info':
            _class += 'label-info'

        return SPAN(value, _class=_class, _title=title)


    def get_os_label(self, label_color, value):
        """
            Returns a label with an OpenStudio color,
            but font remains the same, just bg with corners
        """
        _class = 'os_label '
        if label_color == 'purple':
            _class += 'bg_purple'
        if label_color == 'blue':
            _class += "bg_light_blue"
        if label_color == 'yellow':
            _class += "bg_yellow"

        if value:
            label = SPAN(value, _class=_class)
        else:
            label = ''

        return label


    def get_alert(self, alert_type, content, icon='', dismissable=True):
        """
            Returns a div with the alert class
        """
        _class = 'alert '
        if alert_type == 'success':
            _class += 'alert-success'
        elif alert_type == 'info':
            _class += 'alert-info'
        elif alert_type == 'warning':
            _class += 'alert-warning'
        elif alert_type == 'danger':
            _class += 'alert-danger'

        if icon == 'info':
            icon = SPAN(SPAN(_class='glyphicon glyphicon-info-sign'), ' ')

        if dismissable:
            _class += ' alert-dismissable'
            btn = XML("""<button type="button" class="close" data-dismiss="alert"
                          aria-label="Close">
                          <span aria-hidden="true">&times;</span></button>""")
            alert = DIV(btn, icon, content, _class=_class, _role='alert')
        else:
            alert =  DIV(icon, content, _class=_class, _role='alert')

        return alert


    def get_ajax_loader(self, message=current.T('Loading...')):
        """
            Returns a loader for AJAX/AJAJ
        """
        img = IMG(_src=URL('static',
                           'plugin_os-images/loader/ajax_loader_small.gif'),
                  _alt='Ajaj loader image')

        #spinner = I(_class='fa fa-circle-o-notch fa-spin fa-2x fa-fw blue')

        return DIV(img, message, _class='ajax_loader')


    def get_archived_radio_buttons(self, state, _class='pull-right'):
        """
            state is expected to be 'current' or 'archive'
        """
        from gluon import current

        if state == 'current':
            value = True
            current_class = 'btn-primary'
        else:
            value = False
            current_class = 'btn-default'
        input_current = INPUT(value=value,
                              _type='radio',
                              _name='show_archive',
                              _value='current',
                              _onchange="this.form.submit();",
                              _id='radio_current')

        if state == 'archive':
            value = True
            archive_class = 'btn-primary'
        else:
            value = False
            archive_class = 'btn-default'
        input_archive = INPUT(_type='radio',
                              _name='show_archive',
                              _value='archive',
                              _id='radio_archive',
                              _onchange="this.form.submit();",
                              value=value)

        current_text = current.T('Current')
        archived_text = current.T('Archive')

        current = LABEL(current_text, input_current,
                        _class='btn btn-sm ' + current_class)
        archived = LABEL(archived_text, input_archive,
                         _class='btn btn-sm ' + archive_class)

        return FORM(DIV(current,
                        archived,
                        _class='btn-group',
                         **{'_data-toggle':'buttons'}),
                    _class=_class)


    def get_radio_buttons_form(self,
                               state,
                               buttons,
                               name           = 'filter',
                               selected_class = 'btn-primary',
                               form_class     = 'pull-right'):
        """
            Returns radio form for all buttons, which is expected to be a
            list or tuple of lists. Eg.
            [ ['button1_name', 'Button1 text'],
              ['button2_name', 'Button2 text'] ]

            If state matches one of the button names, it gets the
        """
        default_class = 'btn-default'

        labels = DIV(_class='btn-group',
                     **{'_data-toggle':'buttons'})
        for button, text in buttons:
            _class = 'btn btn-sm '
            if state == button:
                value = True
                _class += selected_class
            else:
                value = False
                _class += 'btn-default'
            input_radio = INPUT(value=value,
                                _type='radio',
                                _name=name,
                                _value=button,
                                _onchange="this.form.submit();",
                                _id='radio_current')

            label = LABEL(text, input_radio, _class=_class)
            labels.append(label)

        form = FORM(labels, _class=form_class)

        return form


    def get_dropdown_menu(self,
                          links,
                          btn_text,
                          btn_size='',
                          btn_icon='',
                          btn_class='btn-default',
                          menu_class=''):
        """
            Returns drop down menu with configurable text.
            Links is expected to be a list links
        """

        button = '<button class="btn '
        button += btn_class + ' '
        button += btn_size + ' dropdown-toggle" '
        button += 'type="button" data-toggle="dropdown" '
        button += 'aria-haspopup="true" aria-expanded="true"> '
        # if btn_icon == 'actions':
        #     button += '<i class="fa fa-circle-thin"></i>'
        if btn_icon == 'download':
            button += '<i class="fa fa-cloud-download"></i>'
        if btn_icon == 'menu-hamburger':
            button += '<i class="fa fa-bars"></i>'
        if btn_icon == 'option-horizontal':
            button += '<span class="glyphicon glyphicon-option-horizontal"></span>'
        if btn_icon == 'option-vertical':
            button += '<span class="glyphicon glyphicon-option-vertical"></span>'
        if btn_icon == 'pencil':
            button += '<span class="' + self.get_icon('pencil') + '"></span>'
        if btn_icon == 'user':
            button += '<span class="fa fa-user"></span>'
        if btn_icon == 'wrench':
            button += '<span class="fa fa-wrench"></span>'
        if btn_text and btn_icon:
            button += ' ' # space between icon and text on left side of text
        button += btn_text
        button += ' '
        button += '<span class="caret"></span></button>'

        button = XML(button)

        ul = UL(_class='dropdown-menu')
        for link in links:
            if type(link) is list:
                ul.append(LI(link[1], _class='dropdown-header'))
            elif link == 'divider':
                ul.append(LI(_class='divider'))
            else:
                ul.append(LI(link))

        dd_menu = DIV(button,
                      ul,
                      _class='dropdown' + ' ' + menu_class)

        return dd_menu


    def get_submenu(self,
                    pages,
                    page,
                    horizontal=False,
                    justified='',
                    htype='', # tabs or pills
                    _id='',
                    _class=''):
        """
            This function returns a submenu based on the list pages which
            is in the following format:
            [ page, title, url ]
            when page matches pages[n][0] the menu whill receive an extra tag to
            indicate it's active
        """
        submenu_class = "os-submenu"
        if horizontal:
            submenu_class = "os-submenu-horizontal"
            if htype == 'tabs':
                justified_class = ''
                if justified:
                    justified_class = 'nav-justified'
                menu = UL(_class='nav nav-tabs ' + justified_class)
            else:
                menu = UL(_class='nav nav-pills')
            for p in pages:
                active = ''
                if p[0] == page:
                    active = 'active'

                if not isinstance(p[2], list):
                    menu.append(
                        LI(
                            A(p[1], _href=p[2]),
                            _class=active,
                            _role="presentation"
                        )
                    )
                else:
                    dropdown = UL(_class="dropdown-menu")
                    for link in p[2]:
                        try:
                            target = link[3]
                        except IndexError:
                             target = ''

                        dropdown.append(
                            LI(
                                A(
                                    link[1],
                                    _href=link[2],
                                    _target=target
                                  )
                            )
                        )

                    menu.append(
                        LI(
                            A(
                                p[1], '...',
                                SPAN(_class='caret'),
                                _href="#",
                                _class="dropdown-toggle",
                                **{'_data-toggle': 'dropdown',
                                   'role': 'button',
                                   'aria-haspopup': 'true',
                                   'aria-expanded': 'false'}
                            ),
                            dropdown,
                            _class=active,
                            _role="presentation"
                        )
                    )
        else:
            menu = []
            for p in pages:
                active = False
                if p[0] == page:
                    active = True
                menu.append([p[1], active, p[2]])

            menu = MENU(menu,
                        li_first='',
                        li_last='',
                        _class=submenu_class,
                        _id=_id)

        return menu


    def get_widget_time(self, field, value):
        """
            Returns a time widget that doesn't show seconds
        """
        return SQLFORM.widgets.string.widget(field, value.strftime('%H:%M') \
                if value and isinstance(value, datetime.time) else '', _class='time')


    def get_popover_button(self, content,
                          title='',
                          position='top',
                          btn_size='',
                          btn_class='',
                          btn_icon='',
                          btn_text=''):
        """
            Returns a button with a popover
            Position can be 'top', 'right', 'buttom', 'left'
        """
        button = '<button class="btn btn-default '
        if btn_class:
            button += ' ' + btn_class + ' '
        button += btn_size + '" '
        button += 'data-container="body" data-toggle="popover" '
        button += 'data-placement="' + position + '" '
        button += 'data-trigger="focus" '
        if title:
            button += 'title="' + title + '" '
        button += 'data-content="' + content + '">'
        if btn_icon == 'info':
            button += '<span class="glyphicon glyphicon-info-sign"></class>'
        button += btn_text
        button += ' </button>'

        button = XML(button)

        return button


    def get_page_navigation_simple(self, url_previous, url_next, current_page, cid=None):
        """
        @param url_previous: url for previous page
        @param url_next: url for next page
        @param current_page: number of current page (int)
        @return: Bootstrap compatible next/previous page browser
        """
        li_previous = LI(A(I(_class='fa fa-chevron-left'), _class='not-clickable'))
        li_next = LI(A(I(_class='fa fa-chevron-right'), _class='not-clickable'))

        if url_previous:
            li_previous =  LI(A(SPAN(_class='fa fa-chevron-left'),
                                _href=url_previous,
                                cid=cid))

        if url_next:
            li_next = LI(A(SPAN(_class='fa fa-chevron-right'),
                                _href=url_next,
                                cid=cid))

        nav = """
        <nav aria-label="Page navigation">
            <ul class="pagination">
                {li_previous}
                <li>
                    <a href="#">Page {current_page}</a>
                </li>
                {li_next}
            </ul>
        </nav>

        """.format(li_previous=li_previous,
                   li_next=li_next,
                   current_page=str(current_page))

        return XML(nav)


    def get_info_icon(self, title='tooltip',
                             position='top',
                             btn_size='',
                             btn_class='',
                             btn_icon='',
                             btn_text=''):
        """
            Returns a button with a tooltip
            Position can be 'top', 'right', 'buttom', 'left'
        """
        button = '<span class="grey big_font glyphicon glyphicon-info-sign'
        if btn_class:
            button += ' ' + btn_class + ' '
        button += btn_size + '" '
        button += 'data-toggle="tooltip" '
        button += 'data-placement="' + position + '" '
        if title:
            button += 'title="' + title + '" '
        button += '>'
        button += btn_text
        button += ' </span>'

        button = XML(button)

        return button


    def get_icon(self, icon):
        """
            All newly built functions should use this function to get icons
            This function centralizes all icon definitions on one place
        """
        if icon == 'education':
            return 'glyphicon glyphicon-education'
        elif icon == 'pencil':
            return 'fa fa-pencil'
        elif icon == 'plane':
            return 'glyphicon glyphicon-plane'
        elif icon == 'plus':
            return 'fa fa-plus'
        elif icon == 'remove':
            return 'fa fa-times'
        elif icon == 'shopping-cart':
            return 'glyphicon glyphicon-shopping-cart'


    def get_fa_icon(self, icon):
        _class = 'fa ' + icon

        return I(_class=_class)


    def get_month_chooser(self, page, set_month_url, year, month):
        """
            Returns month chooser for overview
        """
        if month == 1:
            prev_month = 12
            prev_year  = year - 1
        else:
            prev_month = month - 1
            prev_year  = year

        if month == 12:
            next_month = 1
            next_year  = year + 1
        else:
            next_month = month + 1
            next_year  = year

        url_prev = URL(set_month_url, vars={'month':prev_month,
                                            'year' :prev_year,
                                            'back' :page})

        url_next = URL(set_month_url, vars={'month':next_month,
                                            'year' :next_year,
                                            'back' :page})

        previous = A(I(_class='fa fa-angle-left'),
                     _href=url_prev,
                     _class='btn btn-default')
        nxt = A(I(_class='fa fa-angle-right'),
                _href=url_next,
                _class='btn btn-default')

        return DIV(previous, nxt, _class='btn-group pull-right')


    def max_string_length(self, string, length):
        """
            Cuts string to desired length, if longer, cuts and replaces last 3
            characters with "..."
        """
        if string is None:
            return_value = ''
        elif len(string) > length:
            return_value = string[:length - 3] + "..."
        else:
            return_value = string

        return return_value