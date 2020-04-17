from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, sanity_requests, parameters_requests
from sys import argv

# lno: UV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)
    
    # 01 - 05
    sanity_requests(gvar, '/user/delete/', ut_id(gvar, 'utg1'), ut_id(gvar, 'utu4'), ut_id(gvar, 'utg2'), ut_id(gvar, 'utu2'))

    # 06 Attempt as an unprivileged user.
    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 403, forbidden.',
        '/user/delete/', group=ut_id(gvar, 'utg1'),
        server_user=ut_id(gvar, 'utu3')
    )

    parameters = {
        # 07 Give an invalid parameter.
        # 08 Omit username.
        # 09 Give two usernames.
        'username': {'valid': ut_id(gvar, 'utu5'), 'test_cases': {
            # 10
            '': 'user delete, value specified for "username" must not be the empty string.',
            # 11
            'invalid-unit-Test': 'user delete, value specified for "username" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 12
            'invalid-unit-test-': 'user delete, value specified for "username" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 13
            'invalid-unit-test!': 'user delete, value specified for "username" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 14
            'invalid-unit-test': 'the request did not match any rows.'
        }, 'mandatory': True},
    }

    parameters_requests(gvar, '/user/delete/', ut_id(gvar, 'utg1'), ut_id(gvar, 'utu4'), parameters)

    # 15
    execute_csv2_request(
        gvar, 1, None, 'request contained superfluous parameter "password".',
        '/user/delete/', group=ut_id(gvar, 'utg1'), form_data={
            'username': ut_id(gvar, 'utu5'),
            'password': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 16
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully deleted.'.format(ut_id(gvar, 'utu5')),
        '/user/delete/', group=ut_id(gvar, 'utg1'), form_data={'username': ut_id(gvar, 'utu5')},
        server_user=ut_id(gvar, 'utu4')
    )

if __name__ == "__main__":
    main(None)
