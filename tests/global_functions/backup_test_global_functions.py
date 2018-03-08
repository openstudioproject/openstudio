#!/usr/bin/env python

'''py.test test cases to test global functions on people application.
'''


def test_my_model_function(web2py):
    '''Test a function defined in your models dir.
    '''

    assert web2py.my_sample_function('here') == 'here'
