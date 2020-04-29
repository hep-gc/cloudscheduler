from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, sanity_requests, parameters_requests
from sys import argv

# lno: GV - error code identifier.

def main(gvar):

    # 01 - 05
    sanity_requests(gvar, '/group/update/', ut_id(gvar, 'gtg4'), ut_id(gvar, 'gtu5'), ut_id(gvar, 'gtg7'), ut_id(gvar, 'gtu2'))

    # 06 Attempt as an unprivileged user.
    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 403, forbidden.',
        '/group/update/', group=ut_id(gvar, 'gtg4'), form_data={
            'group_name': ut_id(gvar, 'gtg4'),
            # The fqdn has this value already, but it still counts as updating.
            'htcondor_fqdn': gvar['fqdn']
        },
        server_user=ut_id(gvar, 'gtu3')
    )

    parameters = {
        # 07 Send a GET request.
        # 08 Give an invalid parameter.
        # 09 Omit metadata_name.
        # 10 Give two metadata_names.
        'group_name': {'valid': ut_id(gvar, 'gtg4'), 'test_cases': {
            # 11
            '': 'group update value specified for "group_name" must not be the empty string.',
            # 12
            'invalid-unit-Test': 'group update value specified for "group_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 13
            'invalid-unit-test-': 'group update value specified for "group_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 14
            'invalid-unit-test!': 'group update value specified for "group_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
        }, 'mandatory': True},
        # 15 Give two htcondor_fqdns.
        'htcondor_fqdn': {'valid': gvar['fqdn'], 'test_cases': {}},
        # 16 Give two user_options.
        # 17
        'user_option': {'valid': 'add', 'test_cases': {'': 'value specified for "user_option" must be one of the following options: [\'add\', \'delete\'].'}},
        # 18 Give both username and username.1.
        'username': {'valid': ut_id(gvar, 'gtu4'), 'test_cases': {}, 'array_field': True}
    }

    parameters_requests(gvar, '/group/update/', ut_id(gvar, 'gtg4'), ut_id(gvar, 'gtu5'), parameters)

    # 19 Attempt to modify a group that does not exist.
    execute_csv2_request(
        gvar, 1, 'GV', 'the request did not match any rows.',
        '/group/update/', group=ut_id(gvar, 'gtg4'), form_data={
            'group_name': 'invalid-unit-test',
            # We must specify at least one field to update.
            'htcondor_fqdn': gvar['fqdn']
        },
        server_user=ut_id(gvar, 'gtu5')
    )

    # 20
    execute_csv2_request(
        gvar, 1, 'GV', 'group update, "{}" failed - user "{}" was specified twice.'.format(ut_id(gvar, 'gtg4'), ut_id(gvar, 'gtu4')),
        '/group/update/', group=ut_id(gvar, 'gtg4'),
        form_data={
            'group_name': ut_id(gvar, 'gtg4'),
            'username.1': ut_id(gvar, 'gtu4'),
            'username.2': ut_id(gvar, 'gtu4')
        },
        server_user=ut_id(gvar, 'gtu5')
    )

    # 21
    execute_csv2_request(
        gvar, 1, 'GV', 'group update must specify at least one field to update.',
        '/group/update/', group=ut_id(gvar, 'gtg4'), form_data={'group_name': ut_id(gvar, 'gtg4')},
        server_user=ut_id(gvar, 'gtu5')
    )

    # 22 Ensure that user_option by itself does not qualify as a field to update.
    execute_csv2_request(
        gvar, 1, 'GV', 'group update must specify at least one field to update.',
        '/group/update/', group=ut_id(gvar, 'gtg4'), form_data={'group_name': ut_id(gvar, 'gtg4'), 'user_option': 'add'},
        server_user=ut_id(gvar, 'gtu5')
    )

    # 23
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully updated.'.format(ut_id(gvar, 'gtg4')),
        '/group/update/', group=ut_id(gvar, 'gtg4'), form_data={
            'group_name': ut_id(gvar, 'gtg4'),
            # The fqdn has this value already, but it still counts as updating.
            'htcondor_fqdn': gvar['fqdn']
        },
        server_user=ut_id(gvar, 'gtu5')
    )

    # 24
    execute_csv2_request(
        gvar, 1, 'GV', 'specified user "invalid-unit-test" does not exist.',
        '/group/update/', group=ut_id(gvar, 'gtg4'),
        form_data={
            'group_name': ut_id(gvar, 'gtg4'),
            'username.1': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'gtu5')
    )

    # 25
    execute_csv2_request(
        gvar, 0, None, None,
        '/group/list/', group=ut_id(gvar, 'gtg4'),
        expected_list='group_list', list_filter={'group_name': ut_id(gvar, 'gtg4')},
        values={'htcondor_fqdn': gvar['fqdn']},
        server_user=ut_id(gvar, 'gtu5')
    )

    # 26
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully updated.'.format(ut_id(gvar, 'gtg4')),
        '/group/update/', group=ut_id(gvar, 'gtg4'),
        form_data={
            'group_name': ut_id(gvar, 'gtg4'),
            'username.1': ut_id(gvar, 'gtu4')
        },
        server_user=ut_id(gvar, 'gtu5')
    )

    # 27
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/', group=ut_id(gvar, 'gtg4'),
        expected_list='user_list', list_filter={'username': ut_id(gvar, 'gtu4')},
        values={'user_groups': ut_id(gvar, 'gtg4')},
        server_user=ut_id(gvar, 'gtu5')
    )

    # 28 Remove gtu4 (and all others) from gtg4
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully updated.'.format(ut_id(gvar, 'gtg4')),
        '/group/update/', group=ut_id(gvar, 'gtg4'),
        form_data={
            'group_name': ut_id(gvar, 'gtg4'),
            'username': ''
        },
        server_user=ut_id(gvar, 'gtu5'), html=True
    )

    # 29 Verify that gtu4 was actually removed from gtg4.
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/', group=ut_id(gvar, 'gtg5'),
        expected_list='user_list', list_filter={'username': ut_id(gvar, 'gtu4')},
        values={'user_groups': None},
        server_user=ut_id(gvar, 'gtu5')
    )

    # 30
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully updated.'.format(ut_id(gvar, 'gtg4')),
        '/group/update/', group=ut_id(gvar, 'gtg5'),
        form_data={
            'group_name': ut_id(gvar, 'gtg4'),
            'username.1': ut_id(gvar, 'gtu4')
        },
        server_user=ut_id(gvar, 'gtu5'), html=True
    )

    # 31
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/', group=ut_id(gvar, 'gtg5'),
        expected_list='user_list', list_filter={'username': ut_id(gvar, 'gtu4')},
        values={'user_groups': ut_id(gvar, 'gtg4')},
        server_user=ut_id(gvar, 'gtu5')
    )

    # 32
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully updated.'.format(ut_id(gvar, 'gtg4')),
        '/group/update/', group=ut_id(gvar, 'gtg5'),
        form_data={
            'group_name': ut_id(gvar, 'gtg4'),
            'username.1': ut_id(gvar, 'gtu5')
        },
        server_user=ut_id(gvar, 'gtu5'), html=True
    )

    # 33 Ensure that 27 actually replaced gtu4 with gtu5 in gtg4 (and gtu4 is therefore not in any groups).
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/', group=ut_id(gvar, 'gtg5'),
        expected_list='user_list', list_filter={'username': ut_id(gvar, 'gtu4')},
        values={'user_groups': None},
        server_user=ut_id(gvar, 'gtu5')
    )

    # 34 We want to check that 27 added gtu5 to gtg4, but if group_add has been run since the last setup, it will have added gtu5 to gtg1.
    # So we remove all users from gtg1, but ignore any error if gtg1 doesn't exist.
    execute_csv2_request(
        gvar, None, None, None,
        '/group/update/', group=ut_id(gvar, 'gtg5'),
        form_data={
            'group_name': ut_id(gvar, 'gtg1'),
            'username': ''
        },
        server_user=ut_id(gvar, 'gtu5'), html=True
    )

    # 35 Now we can assume that gtu5 is in only gtg4 and gtg5.
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/', group=ut_id(gvar, 'gtg5'),
        expected_list='user_list', list_filter={'username': ut_id(gvar, 'gtu5')},
        values={'user_groups': ut_id(gvar, 'gtg4,gtg5')},
        server_user=ut_id(gvar, 'gtu5')
    )

    # 36
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully updated.'.format(ut_id(gvar, 'gtg4')),
        '/group/update/', group=ut_id(gvar, 'gtg5'),
        form_data={
            'group_name': ut_id(gvar, 'gtg4'),
            'username.1': ut_id(gvar, 'gtu4'),
            'username.2': ut_id(gvar, 'gtu5')
        },
        server_user=ut_id(gvar, 'gtu5'), html=True
    )

    # 37
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/', group=ut_id(gvar, 'gtg5'),
        expected_list='user_list', list_filter={'username': ut_id(gvar, 'gtu4')},
        values={'user_groups': ut_id(gvar, 'gtg4')},
        server_user=ut_id(gvar, 'gtu5')
    )

    # 38
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/', group=ut_id(gvar, 'gtg5'),
        expected_list='user_list', list_filter={'username': ut_id(gvar, 'gtu5')},
        values={'user_groups': ut_id(gvar, 'gtg4,gtg5')},
        server_user=ut_id(gvar, 'gtu5')
    )

if __name__ == "__main__":
    main(initialize_csv2_request(selections=argv[1] if len(argv) > 1 else ''))
