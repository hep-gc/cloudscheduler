from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id
import sys

def main(gvar):
    if not gvar:
        gvar = {}
        if len(sys.argv) > 1:
            initialize_csv2_request(gvar, sys.argv[0], selections=sys.argv[1])
        else:
            initialize_csv2_request(gvar, sys.argv[0])
    
    # invaid group
    execute_csv2_request(
        gvar, 1, 'UV08', 'cannot switch to invalid group "invalid-unit-test".',
        '/user/delete/', form_data={
            'username': ut_id(gvar, 'utu1'),
            'group': 'invalid-unit-test'
            }
        )

    # validate input fields
    execute_csv2_request(
        gvar, 1, 'UV09', 'value specified for "username" must be all lower case.',
        '/user/delete/', form_data={'username': ut_id(gvar, 'UTu1')}
        )

    execute_csv2_request(
        gvar, 1, 'UV09', 'value specified for a password is less than 6 characters.',
        '/user/delete/', form_data={'password': '1'}
        )
    
    execute_csv2_request(
        gvar, 1, 'UV09', 'value specified for a password is less then 16 characters, and does not contain a mixture of upper, lower, and numerics.',
        '/user/delete/', form_data={'password': 'abcdef'}
        )

    execute_csv2_request(
        gvar, 1, 'UV09', 'value specified for a password is less then 16 characters, and does not contain a mixture of upper, lower, and numerics.',
        '/user/delete/', form_data={'password': 'AaBbCc'}
        )

    execute_csv2_request(
        gvar, 1, 'UV09', 'password update received a password but no verify password; both are required.',
        '/user/delete/', form_data={'password1': 'AaBb123'}
        )

    execute_csv2_request(
        gvar, 1, 'UV09', 'password update received a verify password but no password; both are required.',
        '/user/delete/', form_data={'password2': 'AaBb123'}
        )

    execute_csv2_request(
        gvar, 1, 'UV09', 'values specified for passwords do not match.',
        '/user/delete/', form_data={'password1': 'AaBb123', 'password2': 'aAbB321'}
        )

    execute_csv2_request(
        gvar, 1, 'UV09', 'request did not contain mandatory parameter "username".',
        '/user/delete/', form_data={'password': 'AaBb123'}
        )

    # deleting a user that doesn't exist should fail
    execute_csv2_request(
        gvar, 1, 'UV11', '"%s" failed - the request did not match any rows.' % ut_id(gvar, 'utu8'),
        '/user/delete/', form_data={'username': ut_id(gvar, 'utu8')}
        )

    execute_csv2_request(
        gvar, 1, 'UV12', 'invalid method "GET" specified',
        '/user/delete/'
        )

    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully deleted.'.format(ut_id(gvar, 'utu1')),
        '/user/delete/', form_data={'username': ut_id(gvar, 'utu1')}
        )


if __name__ == "__main__":
    main(None)