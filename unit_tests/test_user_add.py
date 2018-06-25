from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id
import sys

def main(gvar, user_secret):
    if not gvar:
        gvar = {}
        if len(sys.argv) > 1:
            initialize_csv2_request(gvar, sys.argv[0], selections=sys.argv[1])
        else:
            initialize_csv2_request(gvar, sys.argv[0])

    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 401, unauthorized.',
        '/user/add/',
        server_user='invalid-unit-test', server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 403, forbidden.',
        '/user/add/',
        server_user=ut_id(gvar, 'utu1'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'UV13', 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'utu2')),
        '/user/add/',
        server_user=ut_id(gvar, 'utu2'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 403, forbidden.',
        '/user/add/',
        server_user=ut_id(gvar, 'utu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'UV07', 'invalid method "GET" specified.',
        '/user/add/'
    )

    execute_csv2_request(
        gvar, 1, 'UV00', 'cannot switch to invalid group "invalid-unit-test".',
        '/user/add/', form_data={'group': 'invalid-unit-test'}
    )

    execute_csv2_request(
        gvar, 1, 'UV00', 'cannot switch to invalid group "{}".'.format(ut_id(gvar, 'utg2')),
        '/user/add/', form_data={'group': ut_id(gvar, 'utg2')}
    )

    execute_csv2_request(
        gvar, 1, 'UV01', 'request contained a bad parameter "invalid-unit-test".',
        '/user/add/', form_data={'invalid-unit-test': 'invalid-unit-test'}
    )

    execute_csv2_request(
        gvar, 1, 'UV01', 'value specified for "username" must be all lower case.',
        '/user/add/', form_data={'username': 'Invalid-unit-test'}
    )

    execute_csv2_request(
        gvar, 1, 'UV05', 'Data too long for column \'username\' at row 1',
        '/user/add/', form_data={
            'username': 'thisisausernamethatistoolongtobei',
            'password': user_secret,
            'cert_cn': 'invalid-unit-test'
        }
    )

    execute_csv2_request(
        gvar, 1, 'UV05', 'Field \'password\' doesn\'t have a default value',
        '/user/add/', form_data={
            'username': 'invalid-unit-test'
        }
    )

    execute_csv2_request(
        gvar, 1, 'UV01', 'request did not contain mandatory parameter "username".',
        '/user/add/', form_data={
            'is_superuser': 'invalid-unit-test'
        }
    )

    execute_csv2_request(
        gvar, 1, 'UV05', 'Incorrect integer value: \'invalid-unit-test\' for column \'is_superuser\' at row 1',
        '/user/add/', form_data={
            'username': 'invalid-unit-test',
            'password': user_secret,
            'is_superuser': 'invalid-unit-test'
        }
    )

    execute_csv2_request(
        gvar, 1, 'UV01', 'value specified for a password is less than 6 characters.',
        '/user/add/', form_data={
            'username': 'invalid-unit-test',
            'password': 'test'
        }
    )

    execute_csv2_request(
        gvar, 1, 'UV01', 'value specified for a password is less then 16 characters, and does not contain a mixture of upper, lower, and numerics.',
        '/user/add/', form_data={
            'username': 'invalid-unit-test',
            'password': 'invalid'
        }
    )

    execute_csv2_request(
        gvar, 1, 'UV01', 'password update received a password but no verify password; both are required.',
        '/user/add/', form_data={
            'username': 'invalid-unit-test',
            'password1': 'test'
        }
    )

    execute_csv2_request(
        gvar, 1, 'UV01', 'password update received a verify password but no password; both are required.',
        '/user/add/', form_data={
            'username': 'invalid-unit-test',
            'password2': 'test'
        }
    )

    execute_csv2_request(
        gvar, 1, 'UV01', 'value specified for a password is less than 6 characters.',
        '/user/add/', form_data={
            'username': 'invalid-unit-test',
            'password1': 'test',
            'password2': 'test'
        }
    )

    execute_csv2_request(
        gvar, 1, 'UV01', 'value specified for a password is less then 16 characters, and does not contain a mixture of upper, lower, and numerics.',
        '/user/add/', form_data={
            'username': 'invalid-unit-test',
            'password1': 'invalid',
            'password2': 'invalid'
        }
    )

    execute_csv2_request(
        gvar, 1, 'UV01', 'values specified for passwords do not match.',
        '/user/add/', form_data={
            'username': 'invalid-unit-test',
            'password1': 'Abc123',
            'password2': '321cbA'
        }
    )

    execute_csv2_request(
        gvar, 1, 'UV##', 'bad parameter',
        '/user/add/', form_data={
            'username': 'invalid-unit-test',
            'password': user_secret,
            'join_date': 'invalid-unit-test'
        }
    )

    execute_csv2_request(
        gvar, 1, 'UV##', 'bad parameter',
        '/user/add/', form_data={
            'username': 'invalid-unit-test',
            'password': user_secret,
            'active_group': 'invalid-unit-test'
        }
    )

    execute_csv2_request(
        gvar, 1, 'UV04', 'specified group "invalid-unit-test" does not exist.',
        '/user/add/', form_data={
            'username': 'invalid-unit-test',
            'group_name': 'invalid-unit-test'
        }
    )

    execute_csv2_request(
        gvar, 1, 'UV01', 'request contained a bad parameter "condor_central_manager".',
        '/user/add/', form_data={
            'username': 'invalid-unit-test',
            'condor_central_manager': 'invalid-unit-test'
        }
    )

    execute_csv2_request(
        gvar, 1, 'UV06', 'Duplicate entry \'invalid-unit-test-{}\' for key \'PRIMARY\''.format(ut_id(gvar, 'utg1')),
        '/user/add/', form_data={
            'username': 'invalid-unit-test',
            'password': user_secret,
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_name.2': ut_id(gvar, 'utg1')
        }
    )

    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'utu10')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'utu10'),
            'password': user_secret,
            'cert_cn': ut_id(gvar, 'user test user 10')
        }
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu10')},
        values={
            'username': ut_id(gvar, 'utu10'),
            'cert_cn': ut_id(gvar, 'user test user 10'),
            'user_groups': None,
            'is_superuser': 0
        }
    )

    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'utu11')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'utu11'),
            'password1': user_secret,
            'password2': user_secret,
            'cert_cn': ut_id(gvar, 'user test user 11')
        }
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu11')},
        values={
            'username': ut_id(gvar, 'utu11'),
            'cert_cn': ut_id(gvar, 'user test user 11'),
            'user_groups': None,
            'is_superuser': 0
        }
    )

    execute_csv2_request(
        gvar, 1, 'UV02', 'username "{}" unavailable.'.format(ut_id(gvar, 'utu10')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'utu10'),
            'password': user_secret,
            'cert_cn': ut_id(gvar, 'user test user 12')
        }
    )

    execute_csv2_request(
        gvar, 1, 'UV03', 'username "{}" conflicts with a registered common name.'.format(ut_id(gvar, 'utu12')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'utu12'),
            'password': user_secret,
            'cert_cn': ut_id(gvar, 'user test user 10')
        }
    )

    execute_csv2_request(
        gvar, 1, 'UV03', 'username "{}" conflicts with a registered common name.'.format(ut_id(gvar, 'utu12')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'utu12'),
            'password': user_secret,
            'cert_cn': ut_id(gvar, 'utu10')
        }
    )

    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'utu12')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'utu12'),
            'password': user_secret,
            'group_name': ut_id(gvar, 'utg1')
        }
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu12')},
        values={
            'username': ut_id(gvar, 'utu12'),
            'user_groups': ut_id(gvar, 'utg1'),
            'is_superuser': 0
        }
    )

    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'utu13')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'utu13'),
            'password': user_secret,
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_name.2': ut_id(gvar, 'utg2')
        }
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu13')},
        values={
            'username': ut_id(gvar, 'utu13'),
            'user_groups': ut_id(gvar, 'utg1,utg2'),
            'is_superuser': 0
        }
    )

if __name__ == "__main__":
    main(None)