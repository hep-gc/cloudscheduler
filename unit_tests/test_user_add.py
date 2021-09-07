from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, sanity_requests
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
    sanity_requests(gvar, '/user/add/', ut_id(gvar, 'utg1'), ut_id(gvar, 'utu4'), ut_id(gvar, 'utg2'), ut_id(gvar, 'utu2'))

    # We cannot use parameters_requests() here because the mandatory-ness of passwords is complicated.
    # /user/add/ requests can specify either `password` or `password1` and `password2`. This means none of these three are really mandatory, and we will not get the appropriate 'missing mandatory parameter' message that parameters_requests() expects if one or all of them are missing. This then means we cannot use parameters_requests() to test `username`, because it will not send passwords with the usernames (and we don't want to assume the order that the server checks the parameters in).

    # 06 Attempt as an unprivileged user.
    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 403, forbidden.',
        '/user/add/', group=ut_id(gvar, 'utg1'),
        server_user=ut_id(gvar, 'utu3')
    )

    # 07
    execute_csv2_request(
        gvar, 1, 'UV', 'invalid method "GET" specified.',
        '/user/add/', group=ut_id(gvar, 'utg1'),
        server_user=ut_id(gvar, 'utu4')
    )

    # 08
    execute_csv2_request(
        gvar, 1, 'UV', 'request contained a bad parameter "invalid_unit_test".',
        '/user/add/', group=ut_id(gvar, 'utg1'), form_data={'invalid_unit_test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'utu4')
    )

    # 09 Omit username.
    execute_csv2_request(
        gvar, 1, 'UV', 'user add, request did not contain mandatory parameter "username".',
        '/user/add/', group=ut_id(gvar, 'utg1'), form_data={'password': gvar['user_secret']},
        server_user=ut_id(gvar, 'utu4')
    )

    # 10 Give two usernames.
    execute_csv2_request(
        gvar, 1, 'UV', 'user add, request contained a bad parameter "username.1".',
        '/user/add/', group=ut_id(gvar, 'utg1'), form_data={
            'username.1': 'invalid-unit-test-1',
            'username.2': 'invalid-unit-test-2',
            'password': gvar['user_secret']
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 11 Give an empty username.
    execute_csv2_request(
        gvar, 1, 'UV', 'user add, value specified for "username" must not be the empty string.',
        '/user/add/', group=ut_id(gvar, 'utg1'), form_data={
            'username': '',
            'password': gvar['user_secret']
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 12
    execute_csv2_request(
        gvar, 1, 'UV', 'user add, value specified for "username" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
        '/user/add/', group=ut_id(gvar, 'utg1'), form_data={
            'username': 'Invalid-unit-test',
            'password': gvar['user_secret']
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 13
    execute_csv2_request(
        gvar, 1, 'UV', 'user add, value specified for "username" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
        '/user/add/', group=ut_id(gvar, 'utg1'), form_data={
            'username': 'invalid-unit-test-',
            'password': gvar['user_secret']
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 14
    execute_csv2_request(
        gvar, 1, 'UV', 'user add, value specified for "username" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
        '/user/add/', group=ut_id(gvar, 'utg1'), form_data={
            'username': 'invalid-unit--test',
            'password': gvar['user_secret']
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 15
    execute_csv2_request(
        gvar, 1, 'UV', 'user add, value specified for "username" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
        '/user/add/', group=ut_id(gvar, 'utg1'), form_data={
            'username': 'invalid-unit-test!',
            'password': gvar['user_secret']
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 16
    execute_csv2_request(
        gvar, 1, 'UV', 'Data too long for column \'username\'',
        '/user/add/', group=ut_id(gvar, 'utg1'), form_data={
            'username': 'username-that-is-too-long-for-the-database',
            'password': gvar['user_secret']
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 17 Omit password.
    execute_csv2_request(
        gvar, 1, 'UV', 'Field \'password\' doesn\'t have a default value',
        '/user/add/', group=ut_id(gvar, 'utg1'), form_data={'username': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'utu4')
    )

    # 18 Give password.1 and password.2 (not to be confused with giving password1 and password2).
    execute_csv2_request(
        gvar, 1, 'UV', 'user add, request contained a bad parameter "password.1".',
        '/user/add/', group=ut_id(gvar, 'utg1'), form_data={
            'username': 'invalid-unit-test',
            'password.1': gvar['user_secret'],
            'password.2': gvar['user_secret']
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 19 Give an empty password.
    execute_csv2_request(
        gvar, 1, 'UV', 'user add, value specified for a password is less than 6 characters.',
        '/user/add/', group=ut_id(gvar, 'utg1'), form_data={
            'username': 'invalid-unit-test',
            'password': ''
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 20 Give a password that is too short.
    execute_csv2_request(
        gvar, 1, 'UV', 'user add, value specified for a password is less than 6 characters.',
        '/user/add/', group=ut_id(gvar, 'utg1'), form_data={
            'username': 'invalid-unit-test',
            'password': 'aA0'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 21 Give a password that is too weak.
    execute_csv2_request(
        gvar, 1, 'UV', 'value specified for a password is less then 16 characters, and does not contain a mixture of upper, lower, and numerics.',
        '/user/add/', group=ut_id(gvar, 'utg1'), form_data={
            'username': 'invalid-unit-test',
            'password': 'invalid'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 22
    execute_csv2_request(
        gvar, 1, 'UV', 'boolean value specified for "is_superuser" must be one of the following: true, false, yes, no, 1, or 0.',
        '/user/add/', group=ut_id(gvar, 'utg1'), form_data={
            'username': 'invalid-unit-test',
            'password': gvar['user_secret'],
            'is_superuser': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 23 Give password1.1 and password1.2.
    execute_csv2_request(
        gvar, 1, 'UV', 'user add, request contained a bad parameter "password1.1".',
        '/user/add/', group=ut_id(gvar, 'utg1'), form_data={
            'username': 'invalid-unit-test',
            'password1.1': 'invalid-unit-test',
            'password1.2': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 24
    execute_csv2_request(
        gvar, 1, 'UV', 'password update received a password but no verify password; both are required.',
        '/user/add/', group=ut_id(gvar, 'utg1'), form_data={
            'username': 'invalid-unit-test',
            'password1': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 25 Give password2.1 and password2.2.
    execute_csv2_request(
        gvar, 1, 'UV', 'user add, request contained a bad parameter "password2.1".',
        '/user/add/', group=ut_id(gvar, 'utg1'), form_data={
            'username': 'invalid-unit-test',
            'password2.1': 'invalid-unit-test',
            'password2.2': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 26
    execute_csv2_request(
        gvar, 1, 'UV', 'password update received a verify password but no password; both are required.',
        '/user/add/', group=ut_id(gvar, 'utg1'), form_data={
            'username': 'invalid-unit-test',
            'password2': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 27 Give empty passwords.
    execute_csv2_request(
        gvar, 1, 'UV', 'Field \'password\' doesn\'t have a default value.',
        '/user/add/', group=ut_id(gvar, 'utg1'), form_data={
            'username': 'invalid-unit-test',
            'password1': '',
            'password2': ''
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 28 Give passwords that are too short.
    execute_csv2_request(
        gvar, 1, 'UV', 'user add, value specified for a password is less than 6 characters.',
        '/user/add/', group=ut_id(gvar, 'utg1'), form_data={
            'username': 'invalid-unit-test',
            'password1': 'aA0',
            'password2': 'aA0'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 29 Give passwords that are too weak.
    execute_csv2_request(
        gvar, 1, 'UV', 'value specified for a password is less then 16 characters, and does not contain a mixture of upper, lower, and numerics.',
        '/user/add/', group=ut_id(gvar, 'utg1'), form_data={
            'username': 'invalid-unit-test',
            'password1': 'invalid',
            'password2': 'invalid'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 30 Give differing passwords.
    execute_csv2_request(
        gvar, 1, 'UV', 'values specified for passwords do not match.',
        '/user/add/', group=ut_id(gvar, 'utg1'), form_data={
            'username': 'invalid-unit-test',
            'password1': 'Abc123',
            'password2': '321cbA'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 31 Give group_name and group_name.1.
    execute_csv2_request(
        gvar, 1, 'UV', 'user add, request contained parameter "group_name.1" and parameter "group_name".',
        '/user/add/', group=ut_id(gvar, 'utg1'), form_data={
            'username': 'invalid-unit-test',
            'password': gvar['user_secret'],
            'group_name': ut_id(gvar, 'utg1'),
            'group_name.1': ut_id(gvar, 'utg1')
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 32
    execute_csv2_request(
        gvar, 1, 'UV', 'user add, parameter "group_name" contains an empty string which is specifically disallowed.',
        '/user/add/', group=ut_id(gvar, 'utg1'), form_data={
            'username': 'invalid-unit-test',
            'group_name': ''
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 33
    execute_csv2_request(
        gvar, 1, 'UV', 'specified group "invalid-unit-test" does not exist.',
        '/user/add/', group=ut_id(gvar, 'utg1'), form_data={
            'username': 'invalid-unit-test',
            'group_name': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 34
    execute_csv2_request(
        gvar, 1, 'UV', 'user add, "{}" failed - group "{}" was specified twice.'.format('invalid-unit-test', ut_id(gvar, 'utg1')),
        '/user/add/', group=ut_id(gvar, 'utg1'), form_data={
            'username': 'invalid-unit-test',
            'password': gvar['user_secret'],
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_name.2': ut_id(gvar, 'utg1')
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # Give parameters that are explicity rejected.
    # 35
    execute_csv2_request(
        gvar, 1, 'UV', 'request contained a rejected/bad parameter "join_date".',
        '/user/add/', group=ut_id(gvar, 'utg1'), form_data={
            'username': 'invalid-unit-test',
            'password': gvar['user_secret'],
            'join_date': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 36
    execute_csv2_request(
        gvar, 1, 'UV', 'request contained a rejected/bad parameter "active_group".',
        '/user/add/', group=ut_id(gvar, 'utg1'), form_data={
            'username': 'invalid-unit-test',
            'password': gvar['user_secret'],
            'active_group': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 37 Create a user using a single password.
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'utu10')),
        '/user/add/', group=ut_id(gvar, 'utg1'), form_data={
            'username': ut_id(gvar, 'utu10'),
            'password': gvar['user_secret'],
            'cert_cn': ut_id(gvar, 'user test user 10')
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 38 Ensure that utu10 was actually created.
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/', group=ut_id(gvar, 'utg1'),
        expected_list='user_list', list_filter={'username': ut_id(gvar, 'utu10')},
        values={
            'username': ut_id(gvar, 'utu10'),
            'cert_cn': ut_id(gvar, 'user test user 10'),
            'user_groups': None,
            'is_superuser': 0
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 39 Attempt to create a user that already exists.
    execute_csv2_request(
        gvar, 1, 'UV', 'username "{}" unavailable.'.format(ut_id(gvar, 'utu10')),
        '/user/add/', group=ut_id(gvar, 'utg1'), form_data={
            'username': ut_id(gvar, 'utu10'),
            'password': gvar['user_secret'],
            'cert_cn': ut_id(gvar, 'user test user 12')
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 40 Attempt to create a user with a common name that is already taken.
    execute_csv2_request(
        gvar, 1, 'UV', 'common name "{}" conflicts with registered user "{}".'.format(ut_id(gvar, 'user test user 10'), ut_id(gvar, 'utu10')),
        '/user/add/', group=ut_id(gvar, 'utg1'), form_data={
            'username': 'invalid-unit-test',
            'password': gvar['user_secret'],
            'cert_cn': ut_id(gvar, 'user test user 10')
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 41 Create a user using a password and confirmation.
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'utu11')),
        '/user/add/', group=ut_id(gvar, 'utg1'), form_data={
            'username': ut_id(gvar, 'utu11'),
            'password1': gvar['user_secret'],
            'password2': gvar['user_secret'],
            'cert_cn': ut_id(gvar, 'user test user 11'),
            'group_name': ut_id(gvar, 'utg1'),
            'is_superuser': 1
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 42 Ensure that utu11 was actually created and added to utg1.
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/', group=ut_id(gvar, 'utg1'),
        expected_list='user_list', list_filter={'username': ut_id(gvar, 'utu11')},
        values={
            'username': ut_id(gvar, 'utu11'),
            'cert_cn': ut_id(gvar, 'user test user 11'),
            'user_groups': ut_id(gvar, 'utg1'),
            'is_superuser': 1
        },
        server_user=ut_id(gvar, 'utu4')
    )

if __name__ == "__main__":
    main(None)
