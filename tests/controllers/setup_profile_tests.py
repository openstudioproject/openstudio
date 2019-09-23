# -*- coding: utf-8 -*-

def setup_profile_tests(web2py):
    """
        Adds the following to the db:
            A new user
            A new group
            Adds the user to the group
    """
    password = web2py.db.auth_user.password.validate('Password@1')[0]
    uid = 300
    gid = 300

    web2py.db.auth_user.insert(
        id=uid,
        first_name='openstudio',
        last_name='profile test',
        email='profile@openstudioproject.com',
        password=password,
        login_start='profile'
    )

    web2py.db.auth_group.insert(
        id=gid,
        role='profile test',
        description='profile test'
    )
    # add user to group
    web2py.auth.add_membership(gid, uid)

    web2py.db.commit()
