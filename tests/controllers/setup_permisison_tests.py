# -*- coding: utf-8 -*-

def setup_permission_tests(web2py):
    '''
        Adds the following to the db:
            A new user
            A new group
            Adds the user to the group
    '''
    password = web2py.db.auth_user.password.validate('password')[0]
    uid = 200
    gid = 200

    web2py.db.auth_user.insert(id=uid,
                               first_name='openstudio',
                               last_name='permissions test',
                               email='support@openstudioproject.com',
                               password=password)
    web2py.db.auth_group.insert(id=gid,
                                role='auth test',
                                description='auth test')
    # add user to group
    web2py.auth.add_membership(gid, uid)

    web2py.db.commit()
