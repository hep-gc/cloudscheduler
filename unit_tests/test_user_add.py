from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id
from sys import argv

# lno: UV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv2_request(gvar, argv[0])

    # 01
    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 401, unauthorized.',
        '/user/add/',
        server_user='invalid-unit-test'
    )

    # 02
    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 403, forbidden.',
        '/user/add/',
        server_user=ut_id(gvar, 'utu1')
    )

    # 03
    execute_csv2_request(
        gvar, 1, 'UV', 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'utu2')),
        '/user/add/',
        server_user=ut_id(gvar, 'utu2')
    )

    # 04
    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 403, forbidden.',
        '/user/add/',
        server_user=ut_id(gvar, 'utu3')
    )

    # 05
    execute_csv2_request(
        gvar, 1, 'UV', 'invalid method "GET" specified.',
        '/user/add/',
        server_user=ut_id(gvar, 'utu4')
    )

    # 06
    execute_csv2_request(
        gvar, 1, 'UV', 'cannot switch to invalid group "invalid-unit-test".',
        '/user/add/', group='invalid-unit-test',
        server_user=ut_id(gvar, 'utu4')
    )

    # 07
    execute_csv2_request(
        gvar, 1, 'UV', 'cannot switch to invalid group "{}".'.format(ut_id(gvar, 'utg2')),
        '/user/add/', group=ut_id(gvar, 'utg2'),
        server_user=ut_id(gvar, 'utu4')
    )

    # 08
    execute_csv2_request(
        gvar, 1, 'UV', 'request contained a bad parameter "invalid-unit-test".',
        '/user/add/', form_data={'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'utu4')
    )

    # 09
    execute_csv2_request(
        gvar, 1, 'UV', 'value specified for "username" must be all lower case.',
        '/user/add/'
, form_data={'username': 'Invalid-unit-test'},
        server_user=ut_id(gvar, 'utu4')
    )

    # 10
    execute_csv2_request(
        gvar, 1, 'UV', 'Data too long for column \'username\' at row 1',
        '/user/add/'
, form_data={
            'username': 'thisisausernamethatistoolongtobei',
            'password': gvar['user_secret'],
            'cert_cn': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 11
    execute_csv2_request(
        gvar, 1, 'UV', 'Field \'password\' doesn\'t have a default value',
        '/user/add/'
, form_data={
            'username': ut_id(gvar, 'user-invalid-unit-test')
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 12
    execute_csv2_request(
        gvar, 1, 'UV', 'boolean value specified for "is_superuser" must be one of the following: true, false, yes, no, 1, or 0.',
        '/user/add/'
, form_data={
            'is_superuser': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 13
    execute_csv2_request(
        gvar, 1, 'UV', 'value specified for a password is less than 6 characters.',
        '/user/add/'
, form_data={
            'username': ut_id(gvar, 'user-invalid-unit-test'),
            'password': 'test'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 14
    execute_csv2_request(
        gvar, 1, 'UV', 'value specified for a password is less then 16 characters, and does not contain a mixture of upper, lower, and numerics.',
        '/user/add/'
, form_data={
            'username': ut_id(gvar, 'user-invalid-unit-test'),
            'password': 'invalid'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 15
    execute_csv2_request(
        gvar, 1, 'UV', 'password update received a password but no verify password; both are required.',
        '/user/add/'
, form_data={
            'username': ut_id(gvar, 'user-invalid-unit-test'),
            'password1': 'test'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 16
    execute_csv2_request(
        gvar, 1, 'UV', 'password update received a verify password but no password; both are required.',
        '/user/add/'
, form_data={
            'username': ut_id(gvar, 'user-invalid-unit-test'),
            'password2': 'test'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 17
    execute_csv2_request(
        gvar, 1, 'UV', 'value specified for a password is less than 6 characters.',
        '/user/add/'
, form_data={
            'username': ut_id(gvar, 'user-invalid-unit-test'),
            'password1': 'test',
            'password2': 'test'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 18
    execute_csv2_request(
        gvar, 1, 'UV', 'value specified for a password is less then 16 characters, and does not contain a mixture of upper, lower, and numerics.',
        '/user/add/'
, form_data={
            'username': ut_id(gvar, 'user-invalid-unit-test'),
            'password1': 'invalid',
            'password2': 'invalid'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 19
    execute_csv2_request(
        gvar, 1, 'UV', 'values specified for passwords do not match.',
        '/user/add/'
, form_data={
            'username': ut_id(gvar, 'user-invalid-unit-test'),
            'password1': 'Abc123',
            'password2': '321cbA'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 20
    execute_csv2_request(
        gvar, 1, 'UV', 'empty string',
        '/user/add/'
, form_data={
            'username': '',
            'password': gvar['user_secret']
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 21
    execute_csv2_request(
        gvar, 1, 'UV', 'request contained a rejected/bad parameter "join_date".',
        '/user/add/'
, form_data={
            'username': ut_id(gvar, 'user-invalid-unit-test'),
            'password': gvar['user_secret'],
            'join_date': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 22
    execute_csv2_request(
        gvar, 1, 'UV', 'request contained a rejected/bad parameter "active_group".',
        '/user/add/'
, form_data={
            'username': ut_id(gvar, 'user-invalid-unit-test'),
            'password': gvar['user_secret'],
            'active_group': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 23
    execute_csv2_request(
        gvar, 1, 'UV', 'specified group "invalid-unit-test" does not exist.',
        '/user/add/'
, form_data={
            'username': ut_id(gvar, 'user-invalid-unit-test'),
            'group_name': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 24
    execute_csv2_request(
        gvar, 1, 'UV', 'request contained a bad parameter "condor_central_manager".',
        '/user/add/'
, form_data={
            'username': ut_id(gvar, 'user-invalid-unit-test'),
            'condor_central_manager': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 25
    execute_csv2_request(
        gvar, 1, 'UV', 'user add, "{}" failed - group "{}" was specified twice.'.format(ut_id(gvar, 'user-invalid-unit-test'), ut_id(gvar, 'utg1')),
        '/user/add/'
, form_data={
            'username': ut_id(gvar, 'user-invalid-unit-test'),
            'password': gvar['user_secret'],
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_name.2': ut_id(gvar, 'utg1')
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 26
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'utu10')),
        '/user/add/'
, form_data={
            'username': ut_id(gvar, 'utu10'),
            'password': gvar['user_secret'],
            'cert_cn': ut_id(gvar, 'user test user 10')
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 27
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        expected_list='user_list', list_filter={'username': ut_id(gvar, 'utu10')},
        values={
            'username': ut_id(gvar, 'utu10'),
            'cert_cn': ut_id(gvar, 'user test user 10'),
            'user_groups': None,
            'is_superuser': 0
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 28
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'utu11')),
        '/user/add/'
, form_data={
            'username': ut_id(gvar, 'utu11'),
            'password1': gvar['user_secret'],
            'password2': gvar['user_secret'],
            'cert_cn': ut_id(gvar, 'user test user 11')
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 29
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        expected_list='user_list', list_filter={'username': ut_id(gvar, 'utu11')},
        values={
            'username': ut_id(gvar, 'utu11'),
            'cert_cn': ut_id(gvar, 'user test user 11'),
            'user_groups': None,
            'is_superuser': 0
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 30
    execute_csv2_request(
        gvar, 1, 'UV', 'username "{}" unavailable.'.format(ut_id(gvar, 'utu10')),
        '/user/add/'
, form_data={
            'username': ut_id(gvar, 'utu10'),
            'password': gvar['user_secret'],
            'cert_cn': ut_id(gvar, 'user test user 12')
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 31
    execute_csv2_request(
        gvar, 1, 'UV', 'common name "{}" conflicts with registered user "{}".'.format(ut_id(gvar, 'user test user 10'), ut_id(gvar, 'utu10')),
        '/user/add/'
, form_data={
            'username': ut_id(gvar, 'utu12'),
            'password': gvar['user_secret'],
            'cert_cn': ut_id(gvar, 'user test user 10')
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 32
    execute_csv2_request(
        gvar, 1, 'UV', 'common name "{0}" conflicts with registered user "{0}".'.format(ut_id(gvar, 'utu10')),
        '/user/add/'
, form_data={
            'username': ut_id(gvar, 'utu12'),
            'password': gvar['user_secret'],
            'cert_cn': ut_id(gvar, 'utu10')
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 33
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'utu12')),
        '/user/add/'
, form_data={
            'username': ut_id(gvar, 'utu12'),
            'password': gvar['user_secret'],
            'group_name': ut_id(gvar, 'utg1')
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 34
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        expected_list='user_list', list_filter={'username': ut_id(gvar, 'utu12')},
        values={
            'username': ut_id(gvar, 'utu12'),
            'user_groups': ut_id(gvar, 'utg1'),
            'is_superuser': 0
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 35
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'utu13')),
        '/user/add/'
, form_data={
            'username': ut_id(gvar, 'utu13'),
            'password': gvar['user_secret'],
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_name.2': ut_id(gvar, 'utg2')
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 36
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        expected_list='user_list', list_filter={'username': ut_id(gvar, 'utu13')},
        values={
            'username': ut_id(gvar, 'utu13'),
            'user_groups': ut_id(gvar, 'utg1,utg2'),
            'is_superuser': 0
        },
        server_user=ut_id(gvar, 'utu4')
    )

if __name__ == "__main__":
    main(None)
