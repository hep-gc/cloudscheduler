from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, sanity_requests, parameters_requests
from sys import argv

# lno: UV - error code identifier.

def main(gvar):
    
    # 01 - 05
    sanity_requests(gvar, '/user/update/', ut_id(gvar, 'utg1'), ut_id(gvar, 'utu4'), ut_id(gvar, 'utg2'), ut_id(gvar, 'utu2'))

    parameters = {
        # 06 Send a GET request.
        # 07 Give an invalid parameter.
        # 08 Omit username.
        # 09 Give two usernames.
        'username': {'valid': ut_id(gvar, 'utu6'), 'test_cases': {
            # 10
            '': 'user update, value specified for "username" must not be the empty string.',
            # 11
            'invalid-unit-Test': 'user update, value specified for "username" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 12
            'invalid-unit-test-': 'user update, value specified for "username" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 13
            'invalid-unit-test!': 'user update, value specified for "username" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 14 Do not specify any fields to update.
            ut_id(gvar, 'utu6'): 'must specify at least one field to update.'
        }, 'mandatory': True},
        # 15 Give password.1 and password.2 (not to be confused with password1 and password2).
        'password': {'valid': gvar['user_secret'], 'test_cases': {
            # 16
            'inv': 'value specified for a password is less than 6 characters.',
            # 17
            'invalid': 'value specified for a password is less then 16 characters, and does not contain a mixture of upper, lower, and numerics.'
        }},
        # 18 Give both group_name and group_name.1.
        'group_name': {'valid': ut_id(gvar, 'utg1'), 'test_cases': {
            # 19
            '': 'user update, parameter "group_name" contains an empty string which is specifically disallowed.',
            # 20
            'invalid-unit-test': 'specified group "invalid-unit-test" does not exist.'
        }, 'array_field': True},
        # 21 Give two group_options.
        'group_option': {'valid': 'add', 'test_cases': {
            # 22
            'invalid-unit-test': 'value specified for "group_option" must be one of the following options: [\'add\', \'delete\'].',
            # 23 group_option by itself should not count as a field to update.
            'add': 'must specify at least one field to update.'
        }},
        # 24 Give two cert_cns.
        'cert_cn': {'valid': 'invalid-unit-test', 'test_cases': {
            # 25
            ut_id(gvar, 'utu3'): 'common name "{0}" conflicts with registered user "{0}".'.format(ut_id(gvar, 'utu3')),
            # 26
            ut_id(gvar, 'user test user three'): 'common name "{}" conflicts with registered user "{}".'.format(ut_id(gvar, 'user test user three'), ut_id(gvar, 'utu3'))
        }},
        # 27 Give two is_superusers.
        # 28
        'is_superuser': {'valid': 0, 'test_cases': {'invalid-unit-test': 'boolean value specified for "is_superuser" must be one of the following: true, false, yes, no, 1, or 0.'}}
    }

    parameters_requests(gvar, '/user/update/', ut_id(gvar, 'utg1'), ut_id(gvar, 'utu4'), parameters)

    # 29 Attempt to update a non-existent user.
    execute_csv2_request(
        gvar, 1, 'UV', 'the request did not match any rows.',
        '/user/update/', group=ut_id(gvar, 'utg1'), form_data={
            'username': 'invalid-unit-test',
            # We must specify a field to update.
            'cert_cn': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 30 Give a single password that is too short.
    execute_csv2_request(
        gvar, 1, 'UV', 'password update received a password but no verify password; both are required.',
        '/user/update/', group=ut_id(gvar, 'utg1'), form_data={'password1': 'test'},
        server_user=ut_id(gvar, 'utu4')
    )

    # 31 Give a single password that is too weak.
    execute_csv2_request(
        gvar, 1, 'UV', 'password update received a verify password but no password; both are required.',
        '/user/update/', group=ut_id(gvar, 'utg1'), form_data={'password2': 'test'},
        server_user=ut_id(gvar, 'utu4')
    )

    # 32 Give a password with confirmation that is too short.
    execute_csv2_request(
        gvar, 1, 'UV', 'value specified for a password is less than 6 characters.',
        '/user/update/', group=ut_id(gvar, 'utg1'), form_data={
            'password1': 'test',
            'password2': 'test'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 33 Give a password with confirmation that is too weak.
    execute_csv2_request(
        gvar, 1, 'UV', 'value specified for a password is less then 16 characters, and does not contain a mixture of upper, lower, and numerics.',
        '/user/update/', group=ut_id(gvar, 'utg1'), form_data={
            'password1': 'invalid',
            'password2': 'invalid'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 34 Give differing passwords.
    execute_csv2_request(
        gvar, 1, 'UV', 'values specified for passwords do not match.',
        '/user/update/', group=ut_id(gvar, 'utg1'), form_data={
            'password1': 'Abc123',
            'password2': '321cbA'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 35 Attempt to change a static value.
    execute_csv2_request(
        gvar, 1, 'UV', 'request contained a rejected/bad parameter "join_date".',
        '/user/update/', group=ut_id(gvar, 'utg1'), form_data={
            'username': ut_id(gvar, 'utu6'),
            'join_date': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 36
    execute_csv2_request(
        gvar, 1, 'UV', 'request contained a rejected/bad parameter "active_group".',
        '/user/update/', group=ut_id(gvar, 'utg1'), form_data={
            'username': ut_id(gvar, 'utu6'),
            'active_group': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 37
    execute_csv2_request(
        gvar, 1, 'UV', 'request contained a bad parameter "htcondor_fqdn".',
        '/user/update/', group=ut_id(gvar, 'utg1'), form_data={
            'username': 'invalid-unit-test',
            'htcondor_fqdn': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 38
    execute_csv2_request(
        gvar, 1, 'UV', 'user update, "{}" failed - group "{}" was specified twice.'.format(ut_id(gvar, 'utu6'), ut_id(gvar, 'utg1')),
        '/user/update/', group=ut_id(gvar, 'utg1'), form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_name.2': ut_id(gvar, 'utg1')
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 39 Attempt to add to a non-existent group.
    execute_csv2_request(
        gvar, 1, 'UV', 'specified group "invalid-unit-test" does not exist.',
        '/user/update/', group=ut_id(gvar, 'utg1'), form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_option': 'delete',
            'group_name': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 40 Implicitly add the user to one group.
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'utu6')),
        '/user/update/', group=ut_id(gvar, 'utg1'), form_data={
            'username': ut_id(gvar, 'utu6'),
            'cert_cn': ut_id(gvar, 'user-test-user-six'),
            'group_name': ut_id(gvar, 'utg1')
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 41
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/', group=ut_id(gvar, 'utg1'),
        expected_list='user_list', list_filter={'username': ut_id(gvar, 'utu6')},
        values={'user_groups': ut_id(gvar, 'utg1'), 'cert_cn': ut_id(gvar, 'user-test-user-six')},
        server_user=ut_id(gvar, 'utu4')
    )

    # 42 Implicitly add the user to two groups.
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'utu6')),
        '/user/update/', group=ut_id(gvar, 'utg1'), form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_name.2': ut_id(gvar, 'utg2')
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 43 Ensure that utu6 was added to utg1 and utg2.
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/', group=ut_id(gvar, 'utg1'),
        expected_list='user_list', list_filter={'username': ut_id(gvar, 'utu6')},
        values={'username': ut_id(gvar, 'utu6'), 'user_groups': ut_id(gvar, 'utg1,utg2')},
        server_user=ut_id(gvar, 'utu4')
    )

    # 44 Explicitly remove the user from a group.
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'utu6')),
        '/user/update/', group=ut_id(gvar, 'utg1'), form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_name': ut_id(gvar, 'utg2'),
            'group_option': 'delete'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 45 Ensure that utu6 was removed from utg2.
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/', group=ut_id(gvar, 'utg1'),
        expected_list='user_list', list_filter={'username': ut_id(gvar, 'utu6')},
        values={'username': ut_id(gvar, 'utu6'), 'user_groups': ut_id(gvar, 'utg1')},
        server_user=ut_id(gvar, 'utu4')
    )

    # 46 Explicitly add the user to one group.
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'utu6')),
        '/user/update/', group=ut_id(gvar, 'utg1'), form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_name': ut_id(gvar, 'utg2'),
            'group_option': 'add'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 47 Ensure that utu6 was added to utg2.
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/', group=ut_id(gvar, 'utg1'),
        expected_list='user_list', list_filter={'username': ut_id(gvar, 'utu6')},
        values={'username': ut_id(gvar, 'utu6'), 'user_groups': ut_id(gvar, 'utg1,utg2')},
        server_user=ut_id(gvar, 'utu4')
    )

    # 48 Explicitly remove the user from two groups, and revert to original state (so that setup / cleanup is not necessary between runs).
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'utu6')),
        '/user/update/', group=ut_id(gvar, 'utg1'), form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_name.2': ut_id(gvar, 'utg2'),
            'group_option': 'delete'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 49 Ensure that utu6 was removed from utg1 and utg2.
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/', group=ut_id(gvar, 'utg1'),
        expected_list='user_list', list_filter={'username': ut_id(gvar, 'utu6')},
        values={'username': ut_id(gvar, 'utu6'), 'user_groups': None},
        server_user=ut_id(gvar, 'utu4')
    )

if __name__ == "__main__":
    main(initialize_csv2_request(selections=argv[1] if len(argv) > 1 else ''))
