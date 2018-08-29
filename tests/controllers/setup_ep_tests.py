# -*- coding: utf-8 -*-

def setup_ep_tests(web2py):
    """
        Adds the following to the db:
            A new user
            A new group
            Adds the user to the group
    """
    password = web2py.db.auth_user.password.validate('password')[0]
    uid = 400
    gid = 400

    web2py.db.auth_user.insert(id=uid,
                               teacher=True,
                               first_name='openstudio',
                               last_name='ep test',
                               email='ep@openstudioproject.com',
                               password=password,
                               login_start='ep')
    web2py.db.auth_group.insert(id=gid,
                                role='ep test',
                                description='ep test')
    # add user to group
    web2py.auth.add_membership(gid, uid)

    web2py.db.commit()
