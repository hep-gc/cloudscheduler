from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id
from sys import argv

# lno: UV - error code identifier.

def main(gvar, user_secret):
    if not gvar:
        gvar = {'mnomonic': 'UV'}
        if len(argv) > 1:
            initialize_csv2_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv2_request(gvar, argv[0])

    # 01
    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 401, unauthorized.',
        '/user/add/',
        server_user='invalid-unit-test', server_pw=user_secret
    )

    # 02
    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 403, forbidden.',
        '/user/add/',
        server_user=ut_id(gvar, 'utu1'), server_pw=user_secret
    )

    # 03
    execute_csv2_request(
        gvar, 1, 'UV00', 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'utu2')),
        '/user/add/',
        server_user=ut_id(gvar, 'utu2'), server_pw=user_secret
    )

    # 04
    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 403, forbidden.',
        '/user/add/',
        server_user=ut_id(gvar, 'utu3'), server_pw=user_secret
    )

    # 05
    execute_csv2_request(
        gvar, 1, 'UV06', 'invalid method "GET" specified.',
        '/user/add/'
    )

    # 06
    execute_csv2_request(
        gvar, 1, 'UV00', 'cannot switch to invalid group "invalid-unit-test".',
        '/user/add/', form_data={'group': 'invalid-unit-test'}
    )

    # 07
    execute_csv2_request(
        gvar, 1, 'UV00', 'cannot switch to invalid group "{}".'.format(ut_id(gvar, 'utg2')),
        '/user/add/', form_data={'group': ut_id(gvar, 'utg2')}
    )

    # 08
    execute_csv2_request(
        gvar, 1, 'UV01', 'request contained a bad parameter "invalid-unit-test".',
        '/user/add/', form_data={'invalid-unit-test': 'invalid-unit-test'}
    )

    # 09
    execute_csv2_request(
        gvar, 1, 'UV01', 'value specified for "username" must be all lower case.',
        '/user/add/', form_data={'username': 'Invalid-unit-test'}
    )

    # 10
    execute_csv2_request(
        gvar, 1, 'UV04', 'Data too long for column \'username\' at row 1',
        '/user/add/', form_data={
            'username': 'thisisausernamethatistoolongtobei',
            'password': user_secret,
            'cert_cn': 'invalid-unit-test'
        }
    )

    # 11
    execute_csv2_request(
        gvar, 1, 'UV04', 'Field \'password\' doesn\'t have a default value',
        '/user/add/', form_data={
            'username': ut_id(gvar, 'user-invalid-unit-test')
        }
    )

    # 12
    execute_csv2_request(
        gvar, 1, 'UV01', 'boolean value specified for "is_superuser" must be one of the following: true, false, yes, no, 1, or 0.',
        '/user/add/', form_data={
            'is_superuser': 'invalid-unit-test'
        }
    )

    # 13
    execute_csv2_request(
        gvar, 1, 'UV01', 'value specified for a password is less than 6 characters.',
        '/user/add/', form_data={
            'username': ut_id(gvar, 'user-invalid-unit-test'),
            'password': 'test'
        }
    )

    # 14
    execute_csv2_request(
        gvar, 1, 'UV01', 'value specified for a password is less then 16 characters, and does not contain a mixture of upper, lower, and numerics.',
        '/user/add/', form_data={
            'username': ut_id(gvar, 'user-invalid-unit-test'),
            'password': 'invalid'
        }
    )

    # 15
    execute_csv2_request(
        gvar, 1, 'UV01', 'password update received a password but no verify password; both are required.',
        '/user/add/', form_data={
            'username': ut_id(gvar, 'user-invalid-unit-test'),
            'password1': 'test'
        }
    )

    # 16
    execute_csv2_request(
        gvar, 1, 'UV01', 'password update received a verify password but no password; both are required.',
        '/user/add/', form_data={
            'username': ut_id(gvar, 'user-invalid-unit-test'),
            'password2': 'test'
        }
    )

    # 17
    execute_csv2_request(
        gvar, 1, 'UV01', 'value specified for a password is less than 6 characters.',
        '/user/add/', form_data={
            'username': ut_id(gvar, 'user-invalid-unit-test'),
            'password1': 'test',
            'password2': 'test'
        }
    )

    # 18
    execute_csv2_request(
        gvar, 1, 'UV01', 'value specified for a password is less then 16 characters, and does not contain a mixture of upper, lower, and numerics.',
        '/user/add/', form_data={
            'username': ut_id(gvar, 'user-invalid-unit-test'),
            'password1': 'invalid',
            'password2': 'invalid'
        }
    )

    # 19
    execute_csv2_request(
        gvar, 1, 'UV01', 'values specified for passwords do not match.',
        '/user/add/', form_data={
            'username': ut_id(gvar, 'user-invalid-unit-test'),
            'password1': 'Abc123',
            'password2': '321cbA'
        }
    )

    # 20
    execute_csv2_request(
        gvar, 1, 'UV01', 'empty string',
        '/user/add/', form_data={
            'username': '',
            'password': user_secret
        }
    )

    # 21
    execute_csv2_request(
        gvar, 1, 'UV01', 'request contained a rejected/bad parameter "join_date".',
        '/user/add/', form_data={
            'username': ut_id(gvar, 'user-invalid-unit-test'),
            'password': user_secret,
            'join_date': 'invalid-unit-test'
        }
    )

    # 22
    execute_csv2_request(
        gvar, 1, 'UV01', 'request contained a rejected/bad parameter "active_group".',
        '/user/add/', form_data={
            'username': ut_id(gvar, 'user-invalid-unit-test'),
            'password': user_secret,
            'active_group': 'invalid-unit-test'
        }
    )

    # 23
    execute_csv2_request(
        gvar, 1, 'UV03', 'specified group "invalid-unit-test" does not exist.',
        '/user/add/', form_data={
            'username': ut_id(gvar, 'user-invalid-unit-test'),
            'group_name': 'invalid-unit-test'
        }
    )

    # 24
    execute_csv2_request(
        gvar, 1, 'UV01', 'request contained a bad parameter "condor_central_manager".',
        '/user/add/', form_data={
            'username': ut_id(gvar, 'user-invalid-unit-test'),
            'condor_central_manager': 'invalid-unit-test'
        }
    )

    # 25
    execute_csv2_request(
        gvar, 1, 'UV03', 'user add, "{}" failed - group "{}" was specified twice.'.format(ut_id(gvar, 'user-invalid-unit-test'), ut_id(gvar, 'utg1')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'user-invalid-unit-test'),
            'password': user_secret,
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_name.2': ut_id(gvar, 'utg1')
        }
    )

    # 26
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'utu10')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'utu10'),
            'password': user_secret,
            'cert_cn': ut_id(gvar, 'user test user 10')
        }
    )

    # 27
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

    # 28
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'utu11')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'utu11'),
            'password1': user_secret,
            'password2': user_secret,
            'cert_cn': ut_id(gvar, 'user test user 11')
        }
    )

    # 29
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

    # 30
    execute_csv2_request(
        gvar, 1, 'UV02', 'username "{}" unavailable.'.format(ut_id(gvar, 'utu10')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'utu10'),
            'password': user_secret,
            'cert_cn': ut_id(gvar, 'user test user 12')
        }
    )

    # 31
    execute_csv2_request(
        gvar, 1, 'UV02', 'common name "{}" conflicts with registered user "{}".'.format(ut_id(gvar, 'user test user 10'), ut_id(gvar, 'utu10')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'utu12'),
            'password': user_secret,
            'cert_cn': ut_id(gvar, 'user test user 10')
        }
    )

    # 32
    execute_csv2_request(
        gvar, 1, 'UV02', 'common name "{0}" conflicts with registered user "{0}".'.format(ut_id(gvar, 'utu10')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'utu12'),
            'password': user_secret,
            'cert_cn': ut_id(gvar, 'utu10')
        }
    )

    # 33
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'utu12')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'utu12'),
            'password': user_secret,
            'group_name': ut_id(gvar, 'utg1')
        }
    )

    # 34
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

    # 35
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'utu13')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'utu13'),
            'password': user_secret,
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_name.2': ut_id(gvar, 'utg2')
        }
    )

    # 36
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
