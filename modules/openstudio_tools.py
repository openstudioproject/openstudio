# -*- coding: utf-8 -*-

from gluon import *


class OsArchiver:
    def parse_request_vars(self, rvars, sesssion_var):
        """
        :param rvars: request.vars
        :return: Boolean
        True when archived record should be shown, False when not
        """
        show = 'current'

        if 'show_archive' in rvars:
            show = request.vars['show_archive']
            session.school_discovery_show = show
            if show == 'current':
                query = (db.school_discovery.Archived == False)
            elif show == 'archive':
                query = (db.school_discovery.Archived == True)
        elif session.school_discovery_show == 'archive':
            query = (db.school_discovery.Archived == True)
        else:
            session.school_discovery_show = show

        return show_archived


    def archive(self,
                db_table,
                record_id,
                error_message,
                return_url):
        """
        :param db_table: table from db
        :param record_id: id of table
        :param error_message: message to display when operation fails
        :param return_url: URL to send user to after operation
        :return: None
        """
        T = current.globalenv['T']
        session = current.globalenv['session']

        if not record_id:
            session.flash = error_message
        else:
            row = db_table(record_id)

            if row.Archived:
                session.flash = T('Moved to current')
            else:
                session.flash = T('Archived')

            row.Archived = not row.Archived
            row.update_record()

        redirect(return_url)


class OsSession:
    def get_request_var_or_session(self,
                                   r_var,
                                   default_value,
                                   session_parameter):
        """
        :param var: variable to search for in request.vars
        :param session_parameter: name of session parameter
        :return: variable when in session.vars, session var when parameter
        found in session otherwise use the default value
        """
        request = current.globalenv['request']
        session = current.globalenv['session']

        if r_var in request.vars:
            value = request.vars[r_var]
        elif session_parameter and not session[session_parameter] is None:
            value = session[session_parameter]
        else:
            value = default_value

        # Set session parameter
        if session_parameter:
            session[session_parameter] = value

        return value