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
        '/user/update/', form_data={'username': ut_id(gvar, 'utu7'), 'group_name': ut_id(gvar, 'utg1')},
        server_user=ut_id(gvar, 'utu1'), server_pw='AaBbCc123'
        )
    execute_csv2_request(
        gvar, 2, None, 'server "unit-test", HTTP response code 403, forbidden.',
        '/user/update/', form_data={'username': ut_id(gvar, 'utu7'), 'group_name': None},
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
        server_user=ut_id(gvar, 'utu3'), server_pw='AaBbCc123'
        )

    execute_csv2_request(
        gvar, 1, 'UV17', 'cannot switch to invalid group "invalid-unit-test".',
        '/user/settings/', form_data={'group': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'utu3'), server_pw='Abc123'
        )

if __name__ == "__main__":
    main(None)