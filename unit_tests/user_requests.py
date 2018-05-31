#!/usr/bin/env python3
"""
Unit tests.
"""

from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id
import sys

def main(gvar):
    if not gvar:
        gvar = {}
        if len(sys.argv) > 1:
            initialize_csv2_request(gvar, sys.argv[0], selections=sys.argv[1])
        else:
            initialize_csv2_request(gvar, sys.argv[0])




    #### User Add.

    execute_csv2_request(
        gvar, 1, 'UV07', 'user add, invalid method "GET" specified.',
        '/user/add/'
        )

    execute_csv2_request(
        gvar, 1, 'UV00', 'cannnot switch to invalid group "invalid-unit-test".',
        '/user/add/', form_data={'username': ut_id(gvar, 'UTu1'), 'password': '1', 'cert_cn': '%s test user one' % ut_id(gvar, 'unit'), 'group': 'invalid-unit-test'}
        )

    execute_csv2_request(
        gvar, 1, 'UV01', 'must be all lower case.',
        '/user/add/', form_data={'username': ut_id(gvar, 'UTu1'), 'password': 'Abc123', 'cert_cn': '%s test user one' % ut_id(gvar, 'unit')}
        )

    execute_csv2_request(
        gvar, 1, 'UV01', 'user add, password update received a password but no verify password; both are required.',
        '/user/add/', form_data={'username': ut_id(gvar, 'utu1'), 'password1': '1', 'cert_cn': '%s test user one' % ut_id(gvar, 'unit')}
        )

    execute_csv2_request(
        gvar, 1, 'UV01', 'user add, password update received a verify password but no password; both are required.',
        '/user/add/', form_data={'username': ut_id(gvar, 'utu1'), 'password2': '1', 'cert_cn': '%s test user one' % ut_id(gvar, 'unit')}
        )

    execute_csv2_request(
        gvar, 1, 'UV01', 'user add, value specified for a password is less than 6 characters.',
        '/user/add/', form_data={'username': ut_id(gvar, 'utu1'), 'password1': '1', 'password2': '2', 'cert_cn': '%s test user one' % ut_id(gvar, 'unit')}
        )

    execute_csv2_request(
        gvar, 1, 'UV01', 'user add, value specified for a password is less then 16 characters, and does not contain a mixture of upper, lower, and numerics.',
        '/user/add/', form_data={'username': ut_id(gvar, 'utu1'), 'password1': '123456', 'password2': '234567', 'cert_cn': '%s test user one' % ut_id(gvar, 'unit')}
        )

    execute_csv2_request(
        gvar, 1, 'UV01', 'user add, value specified for a password is less then 16 characters, and does not contain a mixture of upper, lower, and numerics.',
        '/user/add/', form_data={'username': ut_id(gvar, 'utu1'), 'password1': 'AB3456', 'password2': '234567', 'cert_cn': '%s test user one' % ut_id(gvar, 'unit')}
        )

    execute_csv2_request(
        gvar, 1, 'UV01', 'user add, values specified for passwords do not match.',
        '/user/add/', form_data={'username': ut_id(gvar, 'utu1'), 'password1': 'this password is longer than 16 characters', 'password2': 'and so is this password', 'cert_cn': '%s test user one' % ut_id(gvar, 'unit')}
        )

    execute_csv2_request(
        gvar, 0, None, 'user "%s" successfully added.' % ut_id(gvar, 'utu1'),
        '/user/add/', form_data={'username': ut_id(gvar, 'utu1'), 'password1': 'AaBbCc123', 'password2': 'AaBbCc123', 'cert_cn': '%s test user one' % ut_id(gvar, 'unit')}
        )

    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu1')}, values={'cert_cn': '%s test user one' % ut_id(gvar, 'unit'), 'user_groups': None, 'is_superuser': 0}
        )

    execute_csv2_request(
        gvar, 1, 'UV02', 'username "%s" unavailable.' % ut_id(gvar, 'utu1'),
        '/user/add/', form_data={'username': ut_id(gvar, 'utu1'), 'password1': 'AaBbCc123', 'password2': 'AaBbCc123', 'cert_cn': '%s test user one' % ut_id(gvar, 'unit')}
        )

    execute_csv2_request(
        gvar, 1, 'UV03', 'username "%s" conflicts with a registered common name.' % ut_id(gvar, 'utu2'),
        '/user/add/', form_data={'username': ut_id(gvar, 'utu2'), 'password1': 'AaBbCc123', 'password2': 'AaBbCc123', 'cert_cn': ut_id(gvar, 'utu1'), 'is_superuser': True}
        )

    execute_csv2_request(
        gvar, 1, 'UV03', 'username "%s" conflicts with a registered common name.' % ut_id(gvar, 'utu2'),
        '/user/add/', form_data={'username': ut_id(gvar, 'utu2'), 'password1': 'AaBbCc123', 'password2': 'AaBbCc123', 'cert_cn': '%s test user one' % ut_id(gvar, 'unit'), 'is_superuser': True}
        )

    execute_csv2_request(
        gvar, 1, 'UV05', "Incorrect integer value: 'invalid-unit-test' for column 'is_superuser'",
        '/user/add/', form_data={'username': ut_id(gvar, 'utu2'), 'password1': 'AaBbCc123', 'password2': 'AaBbCc123', 'cert_cn': '%s test user two' % ut_id(gvar, 'unit'), 'is_superuser': 'invalid-unit-test'}
        )

    execute_csv2_request(
        gvar, 0, None, 'user "%s" successfully added.' % ut_id(gvar, 'utu2'),
        '/user/add/', form_data={'username': ut_id(gvar, 'utu2'), 'password1': 'AaBbCc123', 'password2': 'AaBbCc123', 'cert_cn': '%s test user two' % ut_id(gvar, 'unit'), 'is_superuser': True}
        )

    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu2')}, values={'cert_cn': '%s test user two' % ut_id(gvar, 'unit'), 'user_groups': None, 'is_superuser': 1}
        )

    execute_csv2_request(
        gvar, 2, None, 'server "unit-test", HTTP response code 403, forbidden.',
        '/user/add/', form_data={'username': ut_id(gvar, 'utu3'), 'password1': 'AaBbCc123', 'password2': 'AaBbCc123', 'cert_cn': '%s test user three' % ut_id(gvar, 'unit'), 'is_superuser': True, 'group_name': ut_id(gvar, 'utg4')},
        server_user=ut_id(gvar, 'utu2'), server_pw='AaBbCc123'
        )

    execute_csv2_request(
        gvar, 1, 'UV04', 'user add, "%s" failed - specified group "%s" does not exist.' % (ut_id(gvar, 'utu3'), ut_id(gvar, 'utg4')),
        '/user/add/', form_data={'username': ut_id(gvar, 'utu3'), 'password1': 'AaBbCc123', 'password2': 'AaBbCc123', 'cert_cn': '%s test user three' % ut_id(gvar, 'unit'), 'is_superuser': True, 'group_name': ut_id(gvar, 'utg4')}
        )

    execute_csv2_request(
        gvar, 0, None, 'user "%s" successfully added.' % ut_id(gvar, 'utu3') ,
        '/user/add/', form_data={'username': ut_id(gvar, 'utu3'), 'password1': 'AaBbCc123', 'password2': 'AaBbCc123', 'cert_cn': '%s test user three' % ut_id(gvar, 'unit'), 'is_superuser': True, 'group_name': ut_id(gvar, 'utg1')}
        )

    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu3')}, values={'cert_cn': '%s test user three' % ut_id(gvar, 'unit'), 'user_groups': ut_id(gvar, 'utg1'), 'is_superuser': 1}
        )

    execute_csv2_request(
        gvar, 0, None, 'user "%s" successfully added.' % ut_id(gvar, 'utu4'),
        '/user/add/', form_data={'username': ut_id(gvar, 'utu4'), 'password1': 'AaBbCc123', 'password2': 'AaBbCc123', 'cert_cn': '%s test user four' % ut_id(gvar, 'unit'), 'is_superuser': True, 'group_name': ut_id(gvar, 'utg2')}
        )

    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu4')}, values={'cert_cn': '%s test user four' % ut_id(gvar, 'unit'), 'user_groups': ut_id(gvar, 'utg2'), 'is_superuser': 1}
        )

    execute_csv2_request(
        gvar, 0, None, 'user "%s" successfully added.' % ut_id(gvar, 'utu5'),
        '/user/add/', form_data={'username': ut_id(gvar, 'utu5'), 'password1': 'AaBbCc123', 'password2': 'AaBbCc123', 'cert_cn': '%s test user five' % ut_id(gvar, 'unit'), 'is_superuser': True, 'group_name.2': ut_id(gvar, 'utg3'), 'group_name.1': ut_id(gvar, 'utg1')}
        )

    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu5')}, values={'cert_cn': '%s test user five' % ut_id(gvar, 'unit'), 'user_groups': ut_id(gvar, 'utg1,utg3'), 'is_superuser': 1}
        )

    execute_csv2_request(
        gvar, 1, 'UV06', 'user group-add "{0}.[\'{1}\', \'{1}\']" failed - (1062, "Duplicate entry \'{0}-{1}\' for key \'PRIMARY\'").'.format(ut_id(gvar, 'utu6'), ut_id(gvar, 'utg3')),
        '/user/add/', form_data={'username': ut_id(gvar, 'utu6'), 'password1': 'AaBbCc123', 'password2': 'AaBbCc123', 'cert_cn': '%s test user six' % ut_id(gvar, 'unit'), 'is_superuser': True, 'group_name.2': ut_id(gvar, 'utg3'), 'group_name.1': ut_id(gvar, 'utg3')}
        )

    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu6')}, values={'cert_cn': '%s test user six' % ut_id(gvar, 'unit'), 'user_groups': ut_id(gvar, 'utg3'), 'is_superuser': 1}
        )





    #### Unprivileged User tests.

    execute_csv2_request(
        gvar, 2, None, 'server "unit-test", HTTP response code 401, unauthorized.',
        '/user/add/', form_data={'username': ut_id(gvar, 'utu7'), 'password1': 'AaBbCc123', 'password2': 'AaBbCc123', 'cert_cn': '%s test user seven' % ut_id(gvar, 'unit')},
        server_user=ut_id(gvar, 'utu0'), server_pw='AaBbCc123'
        )

    execute_csv2_request(
        gvar, 2, None, 'server "unit-test", HTTP response code 403, forbidden.',
        '/user/add/', form_data={'username': ut_id(gvar, 'utu7'), 'password1': 'AaBbCc123', 'password2': 'AaBbCc123', 'cert_cn': '%s test user seven' % ut_id(gvar, 'unit')},
        server_user=ut_id(gvar, 'utu1'), server_pw='AaBbCc123'
        )

    execute_csv2_request(
        gvar, 2, None, 'server "unit-test", HTTP response code 403, forbidden.',
        '/user/update/', form_data={'username': ut_id(gvar, 'utu7'), 'password1': 'AaBbCc124', 'password2': 'AaBbCc124', 'cert_cn': '%s test user seventeen' % ut_id(gvar, 'unit')},
        server_user=ut_id(gvar, 'utu1'), server_pw='AaBbCc123'
        )

    execute_csv2_request(
        gvar, 2, None, 'server "unit-test", HTTP response code 403, forbidden.',
        '/user/update/', form_data={'username': ut_id(gvar, 'utu7'), 'group_name': ut_id(gvar,'utg1')},
        server_user=ut_id(gvar, 'utu1'), server_pw='AaBbCc123'
        )
    execute_csv2_request(
        gvar, 2, None, 'server "unit-test", HTTP response code 403, forbidden.',
        '/user/update/', form_data={'username': ut_id(gvar, 'utu7'), 'group_name': []},
        server_user=ut_id(gvar, 'utu1'), server_pw='AaBbCc123'
        )

    execute_csv2_request(
        gvar, 2, None, 'server "unit-test", HTTP response code 403, forbidden.',
        '/user/delete/', form_data={'username': ut_id(gvar, 'utu7')},
        server_user=ut_id(gvar, 'utu1'), server_pw='AaBbCc123'
        )

    execute_csv2_request(
        gvar, 2, None, 'server "unit-test", HTTP response code 403, forbidden.',
        '/user/list/',
        server_user=ut_id(gvar, 'utu1'), server_pw='AaBbCc123'
        )

    execute_csv2_request(
        gvar, 1, 'UV17', 'user "%s" is not a member of any group.' % ut_id(gvar, "utu1"),
        '/user/settings/',
        server_user=ut_id(gvar, 'utu1'), server_pw='AaBbCc123'
        )

    execute_csv2_request(
        gvar, 1, 'UV16', 'user update, invalid method "GET" specified.',
        '/user/settings/',
        server_user=ut_id(gvar, 'utu3'), server_pw='AaBbCc123'
        )

    execute_csv2_request(
        gvar, 1, 'UV15', 'user update, value specified for a password is less than 6 characters.',
        '/user/settings/', form_data={'password': 'abc'},
        server_user=ut_id(gvar, 'utu3'), server_pw='AaBbCc123'
        )

    execute_csv2_request(
        gvar, 1, 'UV15', 'user update, value specified for a password is less then 16 characters, and does not contain a mixture of upper, lower, and numerics.',
        '/user/settings/', form_data={'password': 'abc123'},
        server_user=ut_id(gvar, 'utu3'), server_pw='AaBbCc123'
        )

    execute_csv2_request(
        gvar, 1, 'UV15', 'user update, password update received a password but no verify password; both are required.',
        '/user/settings/', form_data={'password1': 'abc123'},
        server_user=ut_id(gvar, 'utu3'), server_pw='AaBbCc123'
        )

    execute_csv2_request(
        gvar, 1, 'UV15', 'user update, password update received a verify password but no password; both are required.',
        '/user/settings/', form_data={'password2': 'abc123'},
        server_user=ut_id(gvar, 'utu3'), server_pw='AaBbCc123'
        )

    execute_csv2_request(
        gvar, 1, 'UV15', 'user update, value specified for a password is less then 16 characters, and does not contain a mixture of upper, lower, and numerics.',
        '/user/settings/', form_data={'password1': 'abc123', 'password2': 'abc123'},
        server_user=ut_id(gvar, 'utu3'), server_pw='AaBbCc123'
        )

    execute_csv2_request(
        gvar, 1, 'UV15', 'user update, values specified for passwords do not match.',
        '/user/settings/', form_data={'password1': 'Abc123', 'password2': 'abc123'},
        server_user=ut_id(gvar, 'utu3'), server_pw='AaBbCc123'
        )

    execute_csv2_request(
        gvar, 0, None, 'user "%s" successfully updated.' % ut_id(gvar, 'utu3'),
        '/user/settings/', form_data={'password1': 'Abc123', 'password2': 'Abc123'},
        server_user=ut_id(gvar, 'utu3'), server_pw='AaBbCc123'
        )

    execute_csv2_request(
        gvar, 2, None, 'server "unit-test", HTTP response code 401, unauthorized.',
        '/user/settings/', form_data={'password1': 'Abc123', 'password2': 'Abc123'},
#       server_user=ut_id(gvar, 'utu3'), server_pw='Abc123'
        server_user=ut_id(gvar, 'utu3'), server_pw='AaBbCc123'
        )




    #### User Update.

    execute_csv2_request(
        gvar, 1, 'UV18', 'cannnot switch to invalid group "invalid-unit-test".',
        '/user/update/', form_data={'username': ut_id(gvar, 'UTu1'), 'password': '1', 'cert_cn': '%s test user one' % ut_id(gvar, 'unit'), 'group': 'invalid-unit-test'}
        )

    execute_csv2_request(
        gvar, 2, None, 'server "unit-test", HTTP response code 403, forbidden.',
        '/user/update/', form_data={'username': ut_id(gvar, 'utu3'), 'password1': 'AaBbCc123', 'password2': 'AaBbCc123', 'cert_cn': '%s test user three' % ut_id(gvar, 'unit'), 'is_superuser': True, 'group_name': ut_id(gvar, 'utg4')},
        server_user=ut_id(gvar, 'utu2'), server_pw='AaBbCc123'
        )

    execute_csv2_request(
        gvar, 1, 'UV23', 'user update, invalid method "GET" specified.',
        '/user/update/'
        )

    execute_csv2_request(
        gvar, 1, 'UV19', 'must be all lower case.',
        '/user/update/', form_data={'username': ut_id(gvar, 'UTu1'), 'password': 'Abc123', 'cert_cn': '%s test user one' % ut_id(gvar, 'unit')}
        )

    execute_csv2_request(
        gvar, 1, 'UV19', 'user update, password update received a password but no verify password; both are required.',
        '/user/update/', form_data={'username': ut_id(gvar, 'utu1'), 'password1': '1', 'cert_cn': '%s test user one' % ut_id(gvar, 'unit')}
        )

    execute_csv2_request(
        gvar, 1, 'UV19', 'user update, password update received a verify password but no password; both are required.',
        '/user/update/', form_data={'username': ut_id(gvar, 'utu1'), 'password2': '1', 'cert_cn': '%s test user one' % ut_id(gvar, 'unit')}
        )

    execute_csv2_request(
        gvar, 1, 'UV19', 'user update, value specified for a password is less than 6 characters.',
        '/user/update/', form_data={'username': ut_id(gvar, 'utu1'), 'password1': '1', 'password2': '2', 'cert_cn': '%s test user one' % ut_id(gvar, 'unit')}
        )

    execute_csv2_request(
        gvar, 1, 'UV19', 'user update, value specified for a password is less then 16 characters, and does not contain a mixture of upper, lower, and numerics.',
        '/user/update/', form_data={'username': ut_id(gvar, 'utu1'), 'password1': '123456', 'password2': '234567', 'cert_cn': '%s test user one' % ut_id(gvar, 'unit')}
        )

    execute_csv2_request(
        gvar, 1, 'UV19', 'user update, value specified for a password is less then 16 characters, and does not contain a mixture of upper, lower, and numerics.',
        '/user/update/', form_data={'username': ut_id(gvar, 'utu1'), 'password1': 'AB3456', 'password2': '234567', 'cert_cn': '%s test user one' % ut_id(gvar, 'unit')}
        )

    execute_csv2_request(
        gvar, 1, 'UV19', 'user update, values specified for passwords do not match.',
        '/user/update/', form_data={'username': ut_id(gvar, 'utu1'), 'password1': 'this password is longer than 16 characters', 'password2': 'and so is this password', 'cert_cn': '%s test user one' % ut_id(gvar, 'unit')}
        )

    execute_csv2_request(
        gvar, 1, 'UV21', 'user update, "%s" failed - the request did not match any rows.' % ut_id(gvar, 'utu0'),
        '/user/update/', form_data={'username': ut_id(gvar, 'utu0'), 'is_superuser': 'invalid-unit-test'}
        )

    execute_csv2_request(
        gvar, 1, 'UV21', "Incorrect integer value: 'invalid-unit-test' for column 'is_superuser'",
        '/user/update/', form_data={'username': ut_id(gvar, 'utu1'), 'is_superuser': 'invalid-unit-test'}
        )

    execute_csv2_request(
        gvar, 0, None, 'user "%s" successfully updated.' % ut_id(gvar, 'utu1'),
        '/user/update/', form_data={'username': ut_id(gvar, 'utu1'), 'password1': 'AaBbCc123', 'password2': 'AaBbCc123', 'group_name.1': ut_id(gvar, 'utg3'), 'group_name.3': ut_id(gvar, 'utg2'), 'group_name.2': ut_id(gvar, 'utg1')}
        )

    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu1')}, values={'cert_cn': '%s test user one' % ut_id(gvar, 'unit'), 'user_groups': ut_id(gvar, 'utg1,utg2,utg3'), 'is_superuser': 0}
        )

    execute_csv2_request(
        gvar, 0, None, 'user "%s" successfully updated.' % ut_id(gvar, 'utu1'),
        '/user/update/', form_data={'username': ut_id(gvar, 'utu1'), 'password1': 'AaBbCc123', 'password2': 'AaBbCc123', 'group_name.1': ut_id(gvar, 'utg2')}
        )

    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu1')}, values={'cert_cn': '%s test user one' % ut_id(gvar, 'unit'), 'user_groups': ut_id(gvar, 'utg2'), 'is_superuser': 0}
        )

    execute_csv2_request(
        gvar, 0, None, 'user "%s" successfully updated.' % ut_id(gvar, 'utu1'),
        '/user/update/', form_data={'username': ut_id(gvar, 'utu1'), 'password1': 'AaBbCc123', 'password2': 'AaBbCc123', 'group_name.1': ut_id(gvar, 'utg2')}
        )

    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu1')}, values={'cert_cn': '%s test user one' % ut_id(gvar, 'unit'), 'user_groups': ut_id(gvar, 'utg2'), 'is_superuser': 0}
        )

    #### User Group Add and Delete.

    execute_csv2_request(
        gvar, 0, None, None,
        '/user/delete/', form_data={'username': ut_id(gvar, 'utu1')}
        )

    # adding a group to a user that doesn't exit should fail
    execute_csv2_request(
        gvar, 1, 'UV21', 'user update, "%s" failed - the request did not match any rows.' % ut_id(gvar, 'utu1'),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu1'),
            'group_name.1': ut_id(gvar, 'utg1')
            }
        )

    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu1')},
        values={'user_groups': None}
        )

    # adding a user with a group that doesn't exist should fail
    execute_csv2_request(
        gvar, 1, 'UV04', 'user add, "{}" failed - specified group "{}" does not exist.'.format(ut_id(gvar, 'utu1'), ut_id(gvar, 'utg4')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'utu1'),
            'password1': 'AaBbCc123',
            'password2': 'AaBbCc123',
            'group_name.1': ut_id(gvar, 'utg4'),
            'cert_cn': '%s test user one' % ut_id(gvar, 'unit')
            }
        )

    # adding a user with a list of groups, one which doesn't exist should fail
    execute_csv2_request(
        gvar, 1, 'UV04', 'user add, "{}" failed - specified group "{}" does not exist.'.format(ut_id(gvar, 'utu1'), ut_id(gvar, 'utg4')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'utu1'),
            'password1': 'AaBbCc123',
            'password2': 'AaBbCc123',
            'group_name.1': ut_id(gvar, 'utg2'),
            'group_name.2': ut_id(gvar, 'utg3'),
            'group_name.3': ut_id(gvar, 'utg4'),
            'cert_cn': '%s test user one' % ut_id(gvar, 'unit')
            }
        )

    # adding a user with a list of valid groups should succeed
    execute_csv2_request(
        gvar, 0, None, 'user "%s" successfully added.' % ut_id(gvar, 'utu1'),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'utu1'),
            'password1': 'AaBbCc123',
            'password2': 'AaBbCc123',
            'group_name.1': ut_id(gvar, 'utg2'),
            'group_name.2': ut_id(gvar, 'utg3'),
            'cert_cn': '%s test user one' % ut_id(gvar, 'unit')
            }
        )

    # user added with group list should be associated with those groups
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu1')},
        values={'user_groups': '{},{}'.format(ut_id(gvar, 'utg2'), ut_id(gvar, 'utg3'))}
        )

    execute_csv2_request(
        gvar, 0, None, None,
        '/user/delete/', form_data={'username': ut_id(gvar, 'utu1')}
        )
    
    # adding a user with no groups should succeed
    execute_csv2_request(
        gvar, 0, None, 'user "%s" successfully added.' % ut_id(gvar, 'utu1'),
        '/user/add/', form_data={'username': ut_id(gvar, 'utu1'), 'password1': 'AaBbCc123', 'password2': 'AaBbCc123', 'cert_cn': '%s test user one' % ut_id(gvar, 'unit')}
        )

    # user added with no groups shouldn't have any groups
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu1')},
        values={'user_groups': None, 'is_superuser': 0}
        )

    # adding a group that doesn't exist should fail
    execute_csv2_request(
        gvar, 1, 'UV20', 'user update, "{}" failed - specified group "{}" does not exist.'.format(ut_id(gvar, 'utu1'), ut_id(gvar, 'utg4')),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu1'),
            'group_name.1': ut_id(gvar, 'utg4')
            } 
        )

    # failed update shouldn't add any groups
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu1')},
        values={'user_groups': None}
        )

    # adding a group that exists should succeed
    execute_csv2_request(
        gvar, 0, None, 'user "%s" successfully updated.' % ut_id(gvar, 'utu1'),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu1'),
            'group_name.1': ut_id(gvar, 'utg1')
            }
        )

    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu1')},
        values={'user_groups': ut_id(gvar, 'utg1')}
        )

    # adding a list of groups where one doesn't exist should fail
    execute_csv2_request(
        gvar, 1, 'UV20', 'user update, "{}" failed - specified group "{}" does not exist.'.format(ut_id(gvar, 'utu1'), ut_id(gvar, 'utg4')),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu1'),
            'group_name.1': ut_id(gvar, 'utg2'),
            'group_name.2': ut_id(gvar, 'utg4')
            }
        )

    # failed update shouldn't add any groups, valid or not
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu1')},
        values={'user_groups': ut_id(gvar, 'utg1')}
        )

    # adding a list of valid groups should succeed
    execute_csv2_request(
        gvar, 0, None, 'user "%s" successfully updated.' % ut_id(gvar, 'utu1'),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu1'),
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_name.2': ut_id(gvar, 'utg2'),
            'group_name.3': ut_id(gvar, 'utg3')
            }
        )

    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu1')},
        values={'user_groups': '{},{},{}'.format(ut_id(gvar, 'utg1'), ut_id(gvar, 'utg2'), ut_id(gvar, 'utg3'))}
        )

    # removing a group from a list should succeed
    execute_csv2_request(
        gvar, 0, None, 'user "%s" successfully updated.' % ut_id(gvar, 'utu1'),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu1'),
            'group_name.1': ut_id(gvar, 'utg2'),
            'group_name.2': ut_id(gvar, 'utg3')
            }
        )
    
    # TODO: Failing - expect the utg1 group to be removed as not in list above
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu1')},
        values={'user_groups': '{},{}'.format(ut_id(gvar, 'utg2'), ut_id(gvar, 'utg3'))}
        )

    # removing all groups from a user should succeed
    execute_csv2_request(
        gvar, 0, None, 'user "%s" successfully updated.' % ut_id(gvar, 'utu1'),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu1'),
            'group_name': None,
            }
        )

    # groups should be removed
    # TODO: Failing - expect no user groups as none were specified in the update
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu1')},
        values={'user_groups': None}
        )



    #### User Delete.


if __name__ == "__main__":
    main(None)

