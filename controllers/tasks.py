# -*- coding: utf-8 -*-

from general_helpers import max_string_length
from general_helpers import get_ajax_loader
from general_helpers import set_form_id_and_get_submit_button

from openstudio import TasksHelper

@auth.requires(auth.has_membership(group_id='Admins') or \
                auth.has_permission('read', 'tasks'))
def index():
    '''
        Main page for taks
    '''
    response.title = T("Tasks")
    response.view = 'general/only_content.html'

    session.customers_back = 'tasks_index'
    session.workshops_manage_back = 'tasks_index'

    tasks = DIV(LOAD('tasks', 'list_tasks.load',
                     vars=request.vars,
                     content=os_gui.get_ajax_loader()))

    content = tasks

    # Add permission
    add = ''
    permission = auth.has_membership(group_id='Admins') or \
                 auth.has_permission('create', 'tasks')
    if permission:
        #add = os_gui.get_button('add', url_add)
        th = TasksHelper()
        add = th.add_get_modal({})

    return dict(content=content, add=add)

@auth.requires(auth.has_membership(group_id='Admins') or \
                auth.has_permission('read', 'tasks'))
def list_tasks():
    '''
        Creates a list of tasks
    '''
    response.js = 'set_form_classes();' # otherwise user select isn't styled

    ## filter session variable begin
    if 'filter' in request.vars:
        session.tasks_index_filter = request.vars['filter']
    elif session.tasks_index_filter:
        pass
    else:
        session.tasks_index_filter = 'open'

    query = (db.tasks.id > 0) | \
            (db.tasks.auth_user_id == None)
    if session.tasks_index_filter == 'open':
        query &= (db.tasks.Finished == False)
    elif session.tasks_index_filter == 'unassigned':
        query &= (db.tasks.auth_user_id == None)
    elif session.tasks_index_filter == 'finished':
        query &= (db.tasks.Finished == True)
    ## filter session variable end

    ## User filter begin
    permission = auth.has_membership(group_id='Admins') or \
                 auth.has_permission('assign', 'tasks')
    if permission:
        if 'auth_user_id' in request.vars:
            auth_user_id = request.vars['auth_user_id']
            session.tasks_index_user_filter = auth_user_id
        elif session.tasks_index_user_filter:
            pass

        if session.tasks_index_user_filter and \
           session.tasks_index_filter != 'unassigned': # don't filter when it's empty string
            query &= (db.tasks.auth_user_id == session.tasks_index_user_filter)
    else:
        query &= (db.tasks.auth_user_id == auth.user.id)

    ## User filter end

    ## Customer filter begin
    if 'cuID' in request.vars:
        cuID = request.vars['cuID']
        query &= (db.tasks.auth_customer_id == cuID)
    else:
        cuID = ''

    ## Workshop filter begin
    if 'wsID' in request.vars:
        wsID = request.vars['wsID']
        query &= (db.tasks.workshops_id == wsID)
    else:
        wsID = ''

    ## Workshop filter end

    ## Pagination begin
    if 'page' in request.vars:
        try:
            page = int(request.vars['page'])
        except ValueError:
            page = 0
    else:
        page = 0

    items_per_page = 20
    limitby=(page*items_per_page,(page+1)*items_per_page+1)

    ## Pagination end

    onclick_remove = "return confirm('" + \
                     T('Do you really want to delete this task?') + \
                     "');"


    ## Put things in a table
    if session.tasks_index_filter == 'open':
        orderby=db.tasks.Duedate|\
                db.tasks.Priority|\
                db.tasks.Task
    else:
        orderby=~db.tasks.Duedate|\
                db.tasks.Priority|\
                db.tasks.Task

    header = list_tasks_get_header(cuID, wsID)
    table = TABLE(header,
                  _class='table table-hover table-striped table-condensed clear')

    rows = db(query).select(db.tasks.ALL,
                            limitby=limitby,
                            orderby=orderby)
    for i, row in enumerate(rows):
        if i >= items_per_page:
            continue
        repr_row = list(rows[i:i+1].render())[0]

        date_label_type = list_tasks_get_date_label_type(row)

        color_class = list_tasks_get_task_color(row)
        finished_class = list_tasks_get_task_finished_color(row)
        finished_class_text_decoration = list_tasks_get_task_finished_text_decoration(row)

        # Set variables for finished, edit and delete
        vars = { 'tID':row.id,
                 'cuID':cuID,
                 'wsID':wsID,
                 'page':request.vars['page']}

        # check permission to edit/delete tasks
        buttons = DIV(_class='btn-group pull-right')

        # edit
        permission = auth.has_membership(group_id='Admins') or \
                     auth.has_permission('update', 'tasks')
        if permission:
            edit = os_gui.get_button('edit',
                                     URL('edit', vars=vars),
                                     cid=request.cid)

            buttons.append(edit)

        # delete
        permission = auth.has_membership(group_id='Admins') or \
                     auth.has_permission('delete', 'tasks')
        if permission:
            delete = os_gui.get_button('delete_notext',
                           URL('delete', vars=vars, extension=''),
                           onclick=onclick_remove)
            buttons.append(delete)


        if row.auth_user_id is None:
            finished = ''
        else:
            finished = A(SPAN(_class='fa fa-check'),
                         _href=URL('finished', vars=vars),
                         _class='grey big_check',
                         cid=request.cid)

        # populate row
        description_id = 'task_' + unicode(row.id)
        table_row = TR(TD(finished, _class='btn_task_finished'),
                        TD(A(SPAN(_class='fa fa-angle-left grey pull-right'),
                             SPAN(max_string_length(row.Task, 36)),
                             _href='#' + description_id,
                             _title=row.Task,
                             _class=finished_class_text_decoration + ' ' + finished_class + ' task-title',
                             **{'_data-toggle':"collapse"}),
                           DIV(SPAN(row.Description, _class='grey small_font'),
                               _class='collapse',
                               _id=description_id),
                           _class='task'),
                        TD(os_gui.get_label(date_label_type, repr_row.Duedate), _class=finished_class),
                        TD(index_get_days(row), _class=finished_class), # days
                        TD(repr_row.Priority, _class=finished_class),
                        TD(repr_row.auth_user_id, _class=finished_class),
                        _class=finished_class)

        if not cuID and not wsID:
            customer_link = list_tasks_get_customers_link(
                repr_row.auth_customer_id,
                row.auth_customer_id)
            table_row.append(TD(customer_link)) # customer

            workshops_link = list_tasks_get_workshops_link(repr_row.workshops_id,
                                                           row.workshops_id)
            table_row.append(TD(workshops_link)) # workshops

        table_row.append(buttons)

        table.append(table_row)

    ## Pager begin
    navigation = ''
    url_previous = ''
    url_next = ''
    if len(rows) > items_per_page or page:
        previous = SPAN(_class='fa fa-chevron-left grey')
        if page:
            url_previous = URL(request.function, vars={'page':page-1})
            previous = A(SPAN(_class='fa fa-chevron-left'),
                         _href=url_previous,
                         cid=request.cid)

        nxt = SPAN(_class='fa fa-chevron-right grey')
        if len(rows) > items_per_page:
            url_next = URL(request.function, vars={'page':page+1})
            nxt = A(SPAN(_class='fa fa-chevron-right'),
                    _href=url_next,
                    cid=request.cid)


        navigation = os_gui.get_page_navigation_simple(url_previous, url_next, page + 1, request.cid)

    ## Pager End

    if cuID:
        url_add = URL('add', vars={'cuID':cuID}, extension='')
        add_vars = {'cuID':cuID}
    elif wsID:
        url_add = URL('add', vars={'wsID':wsID}, extension='')
        add_vars = {'wsID':wsID}
    else:
        url_add = URL('add', extension='')
        add_vars = {}

    # Add permission
    # add = ''
    # permission = auth.has_membership(group_id='Admins') or \
    #              auth.has_permission('create', 'tasks')
    # if permission:
    #     #add = os_gui.get_button('add', url_add)
    #     add = list_tasks_get_add(add_vars)

    # Status filter
    filter_form = list_tasks_get_filter(session.tasks_index_filter)

    # assign user permission
    user_form = ''
    permission = auth.has_membership(group_id='Admins') or \
                 auth.has_permission('assign', 'tasks')
    if permission:
        user_form = list_tasks_get_user_filter(session.tasks_index_user_filter)

    # put everything together
    content = DIV(DIV(DIV(user_form, _class='col-md-6'),
                      DIV(filter_form, _class='col-md-6'),
                      _class='row'),
                  DIV(DIV(table,
                          _class='col-md-12'),
                      _class='row'),
                  DIV(DIV(navigation,
                          _class='col-md-12'),
                      _class='row')
                  )

    return dict(content=content)


# def list_tasks_get_add(add_vars):
#     '''
#         Returns add button and modal
#     '''
#     modal_content = DIV(
#         LOAD('tasks', 'add.load',
#              vars=add_vars,
#              ajax_trap=True,
#              content=os_gui.get_ajax_loader()))
#
#     modal_title = T("Add Task")
#
#     button_text = os_gui.get_modal_button_icon( 'add', T("Add") )
#     result = os_gui.get_modal(
#             button_text   = button_text,
#             button_class  = 'btn-sm',
#             modal_title   = modal_title,
#             modal_content = modal_content,
#             #modal_size    = '',
#             modal_class   = 'modal_add_task'
#           )
#     add = SPAN(result['button'], result['modal'])
#
#     return add


@auth.requires(auth.has_membership(group_id='Admins') or \
                auth.has_permission('read', 'tasks'))
def list_tasks_today():
    '''
        Shows a list of tasks for today
    '''
    query = (db.tasks.auth_user_id == auth.user.id) & \
            (db.tasks.Duedate <= datetime.date.today()) & \
            (db.tasks.Finished == False)

    header = list_tasks_get_header(today=True)

    table = TABLE(header,
                  _class='table table-hover table-condensed')

    rows = db(query).select(db.tasks.ALL,
                            orderby=db.tasks.Duedate|\
                                    db.tasks.Priority|\
                                    db.tasks.Task)
    for i, row in enumerate(rows):
        repr_row = list(rows[i:i+1].render())[0]

        date_label_type = list_tasks_get_date_label_type(row)

        color_class = list_tasks_get_task_color(row)
        finished_class = list_tasks_get_task_finished_color(row)
        finished_class_text_decoration = list_tasks_get_task_finished_text_decoration(row)

        vars = {'tID':row.id,
                'today':True}
        finished = A(SPAN(_class='fa fa-check'),
                     _href=URL('tasks', 'finished', vars=vars),
                     _class='grey',
                     cid=request.cid)

        description_id = 'task_' + unicode(row.id)
        table_row = TR(TD(finished, _class='btn_task_finished'),
                        TD(A(SPAN(max_string_length(row.Task, 36),
                                  _title=row.Task),
                             _href='#' + description_id,
                             _class=finished_class_text_decoration + ' ' + finished_class,
                             **{'_data-toggle':"collapse"}),
                           DIV(SPAN(row.Description, _class='grey small_font'),
                               _class='collapse',
                               _id=description_id),
                           _class='task'),
                        TD(os_gui.get_label(date_label_type, repr_row.Duedate)),
                        TD(index_get_days(row)), # days
                        TD(repr_row.Priority),
                        TD(list_tasks_get_customers_link(
                            repr_row.auth_customer_id,
                            row.auth_customer_id)),
                        TD(list_tasks_get_workshops_link(repr_row.workshops_id,
                                                         row.workshops_id)),
                        _class=finished_class)

        table.append(table_row)

    if len(rows):

        content = DIV(DIV(H3(T("To-do"), _class="box-title"),
                                   DIV(A(I(_class='fa fa-minus'),
                                         _href='#',
                                         _class='btn btn-box-tool',
                                         _title=T("Collapse"),
                                         **{'_data-widget': 'collapse'}),
                                       _class='box-tools pull-right'),
                                   _class='box-header with-border'),
                               DIV(table, _class='box-body'),
                               DIV(A(T("All tasks"),
                                     _href=URL('tasks', 'index', extension='')),
                                   _class='box-footer text-center'),
                               _class='box box-success')

    else:
        content = ''

    return dict(content=content)


def list_tasks_get_date_label_type(row):
    '''
    Return color for a date label
    '''
    duedate = row.Duedate
    today = TODAY_LOCAL

    if duedate == today and not row.Finished:
        color_class = 'success'
    elif duedate < today and not row.Finished:
        color_class = 'danger'
    elif row.Finished:
        color_class = 'default'
    else:
        color_class = 'primary'

    return color_class


def list_tasks_get_task_color(row):
    '''
        Returns color for a task
    '''

    duedate = row.Duedate
    today = datetime.date.today()

    if duedate == today and not row.Finished:
        color_class = 'green'
    elif duedate < today and not row.Finished:
        color_class = 'red'
    else:
        color_class = 'default-color'

    return color_class


def list_tasks_get_task_finished_color(row):
    '''
        If a task is finished, return the line-through class
    '''
    finished_class = ''
    if row.Finished:
        finished_class = 'grey'

    return finished_class

def list_tasks_get_task_finished_text_decoration(row):
    '''
        If a task is finished, return the line-through class
    '''
    finished_class = ''
    if row.Finished:
        finished_class = 'line-through'

    return finished_class


def list_tasks_get_customers_link(cust_name, cuID):
    '''
        Returns link for a customer
    '''
    link = ''
    if cuID:
        link = A(max_string_length(cust_name, 22),
                 _title=cust_name,
                 _href=URL('customers', 'edit', args=cuID,
                           extension=''))
    return link


def list_tasks_get_workshops_link(ws_name, wsID):
    '''
        Returns link for a customer
    '''
    link = ''
    if wsID:
        link = A(max_string_length(ws_name, 22),
                 _title=ws_name,
                 _href=URL('events', 'tickets', vars={'wsID':wsID},
                           extension=''))

    return link


def list_tasks_get_header(cuID=None, wsID=None, today=False):
    '''
        returns header for table
    '''
    header_class = 'header'

    if cuID or wsID:
        header = THEAD(TR(TH(), # check
                         TH(T('Task')),
                         #TH(T('Description')),
                         TH(T('Due date')),
                         TH(T('Days')),
                         TH(T('Priority')),
                         TH(T('Assigned to')),
                         TH(),# buttons
                         _class=header_class))
    elif today:
        header = THEAD(TR(TH(), # check
                        TH(T('Task')),
                        #TH(T('Description')),
                        TH(T('Due date')),
                        TH(T('Days')),
                        TH(T('Priority')),
                        TH(T('Customer')),
                        TH(T('Event')),
                        _class=header_class))
    else:
        header = THEAD(TR(TH(), # check
                        TH(T('Task')),
                        #TH(T('Description')),
                        TH(T('Due date')),
                        TH(T('Days')),
                        TH(T('Priority')),
                        TH(T('Assigned to')),
                        TH(T('Customer')),
                        TH(T('Event')),
                        TH(), # buttons
                        _class=header_class))
    return header


def list_tasks_get_user_filter(auth_user_id=None):
    '''
        returns form to filter users in tasks list
    '''
    auth_user_query = (db.auth_user.id > 1) & \
                      (db.auth_user.trashed == False) & \
                      ((db.auth_user.teacher == True) |
                       (db.auth_user.employee == True))

    form = SQLFORM.factory(
        Field('auth_user_id', db.auth_user,
            requires=IS_IN_DB(db(auth_user_query),
                              'auth_user.id',
                              '%(display_name)s',
                              zero=T("All users")),
            default=auth_user_id))

    select = form.element('select[name="auth_user_id"')
    select.attributes['_onchange'] = "this.form.submit();"

    form = DIV(form.custom.begin,
               form.custom.widget.auth_user_id,
               form.custom.end,
               _class='right',
               _id='tasks_user_filter')

    return form


def add_edit_delete_get_return_url(var=None):
    '''
        return return url for edit pages
    '''
    cuID = request.vars['cuID']
    wsID = request.vars['wsID']
    if cuID:
        return_url = URL('customers', 'tasks', vars={'cuID':cuID})
    elif wsID:
        return_url = URL('events', 'tasks', vars={'wsID':wsID})
    else:
        return_url = URL('index')

    return return_url


@auth.requires_login()
def add():
    """
        This function shows an add page for a task
    """
    cuID = request.vars['cuID']
    wsID = request.vars['wsID']
    if cuID:
        db.tasks.auth_customer_id.default = cuID
    elif wsID:
        db.tasks.workshops_id.default = wsID

    permission = auth.has_membership(group_id='Admins') or \
                 auth.has_permission('assign', 'tasks')
    if not permission:
        db.tasks.auth_user_id.writable = False

    return_url = URL('add_edit_redirect',
                     vars=request.vars,
                     extension='')

    crud.messages.submit_button = T("Save")
    crud.messages.record_created = T("Added task")
    crud.settings.create_next = return_url
    #crud.settings.formstyle = 'bootstrap3_inline'
    form = crud.create(db.tasks)

    form_id = "task_add"
    form_element = form.element('form')
    form['_id'] = form_id

    elements = form.elements('input, select, textarea')
    for element in elements:
        element['_form'] = form_id

    # Make table inputs full width
    table = form.element('table')
    table['_class'] = 'full-width'

    #back = os_gui.get_button('back', return_url)

    return dict(content=form)


@auth.requires(auth.has_membership(group_id='Admins') or \
               auth.has_permission('create', 'tasks'))
def add_edit_redirect():
    '''
        Redirect back to list of tasks, to escape add modal
    '''
    return_url = add_edit_delete_get_return_url()

    return redirect(return_url, client_side=True)


@auth.requires_login()
def edit():
    """
        This function shows an edit page for a task
        request.vars['tID'] is expected to be tasks.id
    """
    # call js for styling the form
    response.js = 'set_form_classes();'

    tID = request.vars['tID']

    permission = auth.has_membership(group_id='Admins') or \
                 auth.has_permission('assign', 'tasks')
    if not permission:
        db.tasks.auth_user_id.writable = False

    return_url = URL('add_edit_redirect',
                   vars=request.vars,
                   extension='')


    crud.messages.submit_button = T("Save")
    crud.messages.record_updated = T("Saved task")
    crud.settings.update_next = return_url
    crud.settings.update_deletable = False
    form = crud.update(db.tasks, tID)

    result = set_form_id_and_get_submit_button(form, 'task_edit')
    form = result['form']
    submit = result['submit']

    cancel = os_gui.get_button('noicon', return_url, title=T('Cancel'), btn_size='')
    table = form.element('table')
    table.append(TR(TD(),
                    TD(cancel, DIV(submit, _class='pull-right'))))

    title = H4(T('Edit task'))


    return dict(content=DIV(title, form))


def finished_delete_get_redirect_url(var=None):
    '''
        return redirect url for delete and finished functions
    '''
    cuID = request.vars['cuID']
    wsID = request.vars['wsID']
    page = request.vars['page']
    if cuID:
        redirect(URL('list_tasks',
                     vars={'cuID':cuID,
                           'page':page}))
    if wsID:
        redirect(URL('list_tasks',
                     vars={'wsID':wsID,
                           'page':page}))
    else:
        redirect(URL('list_tasks', vars={'page':page}))


@auth.requires(auth.has_membership(group_id='Admins') or \
                auth.has_permission('delete', 'tasks'))
def delete():
    '''
        Deletes a task
    '''
    tID = request.vars['tID']
    cuID = request.vars['cuID']

    query = (db.tasks.id == tID)
    db(query).delete()

    return_url = finished_delete_get_redirect_url()
    redirect(return_url)



@auth.requires(auth.has_membership(group_id='Admins') or \
                auth.has_permission('update', 'tasks'))
def finished():
    '''
        Mark a task as finished
    '''
    tID = request.vars['tID']
    task = db.tasks(tID)

    task.Finished = not task.Finished
    task.update_record()

    if task.Finished:
        session.flash = T("Finished task")
    else:
        session.flash = T("Opened task")

    if 'today' in request.vars: # redirect to list_tasks_today
        redirect(URL('list_tasks_today'))
    else:
        redirect(finished_delete_get_redirect_url())


def index_get_days(row):
    '''
        Returns number of days remaining or past for a task
    '''
    duedate = row.Duedate
    today = datetime.date.today()
    delta = duedate - today

    return delta.days


def list_tasks_get_filter(state, _class='pull-right tasks-status-filter'):
    '''
        state is expected to be 'all' 'finished' or 'open'
    '''
    if state == 'all':
        value = True
        all_class = 'btn-primary'
    else:
        value = False
        all_class = 'btn-default'
    input_all = INPUT(value=value,
                      _type='radio',
                      _name='filter',
                      _value='all',
                      _onchange="this.form.submit();",
                      _id='radio_all')

    if state == 'open':
        value = True
        open_class = 'btn-primary'
    else:
        value = False
        open_class = 'btn-default'
    input_open = INPUT(_type='radio',
                       _name='filter',
                       _value='open',
                       _id='radio_open',
                       _onchange="this.form.submit();",
                       value=value)

    if state == 'unassigned':
        value = True
        unassigned_class = 'btn-danger'
    else:
        value = False
        unassigned_class = 'btn-default'
    input_unassigned = INPUT(_type='radio',
                             _name='filter',
                             _value='unassigned',
                             _id='radio_unassigned',
                             _onchange="this.form.submit();",
                             value=value)

    if state == 'finished':
        value = True
        finished_class = 'btn-success'
    else:
        value = False
        finished_class = 'btn-default'
    input_finished = INPUT(_type='radio',
                           _name='filter',
                           _value='finished',
                           _id='radio_finished',
                           _onchange="this.form.submit();",
                           value=value)

    # unassigned count
    badge = ''
    query = (db.tasks.auth_user_id == None)
    wsID = request.vars['wsID']
    if wsID:
        query &= (db.tasks.workshops_id == wsID)
    cuID = request.vars['cuID']
    if cuID:
        query &= (db.tasks.auth_customer_id == cuID)
    count = db(query).count()
    if count > 0:
        badge = os_gui.get_badge(unicode(count))

    all_text        = T('All')
    open_text       = T('Open')
    unassigned_text = SPAN(T('Unassigned'), ' ', SPAN(badge, _color='grey'))
    finished_text   = T('Finished')


    radio_all = LABEL(all_text, input_all,
                      _class='btn ' + all_class)
    radio_open = LABEL(open_text, input_open,
                       _class='btn ' + open_class)
    radio_unassigned = LABEL(unassigned_text, input_unassigned,
                             _class='btn ' + unassigned_class)
    radio_finished = LABEL(finished_text, input_finished,
                           _class='btn ' + finished_class)


    return FORM(DIV(radio_open,
                    radio_finished,
                    radio_unassigned,
                    radio_all,
                    _class='btn-group',
                     **{'_data-toggle':'buttons'}),
                _class=_class)
