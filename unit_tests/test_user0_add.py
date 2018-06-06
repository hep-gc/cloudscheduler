from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id
import sys

def main(gvar):
    if not gvar:
        gvar = {}
        if len(sys.argv) > 1:
            initialize_csv2_request(gvar, sys.argv[0], selections=sys.argv[1])
        else:
            initialize_csv2_request(gvar, sys.argv[0])
    
    execute_csv2_request(
        gvar, 1, 'UV07', 'user add, invalid method "GET" specified.',
        '/user/add/'
        )

    execute_csv2_request(
        gvar, 1, 'UV00', 'cannot switch to invalid group "invalid-unit-test".',
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

if __name__ == "__main__":
    main(None)