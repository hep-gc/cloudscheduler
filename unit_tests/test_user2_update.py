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
        gvar, 1, 'UV18', 'cannot switch to invalid group "invalid-unit-test".',
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
    
    


if __name__ == "__main__":
    main(None)