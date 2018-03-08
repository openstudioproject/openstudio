# -*- coding: utf-8 -*-
# this file is released under public domain and you can use it without limitations

if auth.user:
    ##
    # Don't allow disabled users to log in, log them back out straight away
    ##
    if not auth.user.enabled:
        auth.messages.logged_out = T('Invalid login')
        auth.logout()

    ##
    # Untrash trashed user when the user logs in
    ##
    if auth.user.trashed == True:
        au = db.auth_user(auth.user.id)
        au.trashed = False
        au.update_record()

