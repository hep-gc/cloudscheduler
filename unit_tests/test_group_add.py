from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, sanity_requests, parameters_requests
from sys import argv

# lno: GV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)
    
    # 01 - 05
    sanity_requests(gvar, '/group/add/', ut_id(gvar, 'gtg4'), ut_id(gvar, 'gtu5'), ut_id(gvar, 'gtg7'), ut_id(gvar, 'gtu2'))

    # 06 Attempt as an unprivileged user.
    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 403, forbidden.',
        '/group/add/', group=ut_id(gvar, 'gtg4'),
        server_user=ut_id(gvar, 'gtu3')
    )

    parameters = {
        # 07 Send a GET request.
        # 08 Give an invalid parameter.
        # 09 Omit group_name.
        # 10 Give two group_names.
        'group_name': {'valid': 'invalid-unit-test', 'test_cases': {
            # 11
            '': 'group add value specified for "group_name" must not be the empty string.',
            # 12
            'Invalid-Unit-Test': 'group add value specified for "group_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 13
            'invalid-unit--test': 'group add value specified for "group_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 14
            '-invalid-unit-test': 'group add value specified for "group_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 15
            'invalid-unit-test!': 'group add value specified for "group_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 16
            'group-name-that-is-too-long-for-the-database': 'Data too long for column \'group_name\' at row 1'
        }, 'mandatory': True},
        # 17 Give two htcondor_fqdns.
        'htcondor_fqdn': {'valid': gvar['fqdn'], 'test_cases': {}},
        # 18 Give username and username.1.
        # 19
        'username': {'valid': ut_id(gvar, 'gtu5'), 'test_cases': {'invalid-unit-test': 'specified user "invalid-unit-test" does not exist.'}, 'array_field': True},
        # 20 Give two user_options.
        # 21
        'user_option': {'valid': 'add', 'test_cases': {'invalid-unit-test': 'value specified for "user_option" must be one of the following options: [\'add\', \'delete\'].'}},
        # 22 Give two job_cpus.
        # 23
        'job_cpus': {'valid': 0, 'test_cases': {'invalid-unit-test': 'group add value specified for "job_cpus" must be an integer value.'}},
        # 24 Give two job_rams.
        # 25
        'job_ram': {'valid': 0, 'test_cases': {'invalid-unit-test': 'group add value specified for "job_ram" must be an integer value.'}},
        # 26 Give two job_disks.
        # 27
        'job_disk': {'valid': 0, 'test_cases': {'invalid-unit-test': 'group add value specified for "job_disk" must be an integer value.'}},
        # 28 Give two job_swaps.
        # 29
        'job_swap': {'valid': 0, 'test_cases': {'invalid-unit-test': 'group add value specified for "job_swap" must be an integer value.'}},
        # 30 Give two vm_images.
        # 31
        'vm_image': {'valid': '', 'test_cases': {'invalid-unit-test': 'group add, "invalid-unit-test" failed - specified item does not exist: vm_image=invalid-unit-test, group_name=invalid-unit-test.'}},
        # 32 Give two vm_flavors.
        # 33
        'vm_flavor': {'valid': '', 'test_cases': {'invalid-unit-test': 'group add, "invalid-unit-test" failed - specified item does not exist: vm_flavor=invalid-unit-test, group_name=invalid-unit-test.'}},
        # 34 Give two vm_networks.
        # 35
        'vm_network': {'valid': '', 'test_cases': {'invalid-unit-test': 'group add, "invalid-unit-test" failed - specified item does not exist: vm_network=invalid-unit-test, group_name=invalid-unit-test.'}},
        # 36 Give two vm_keynames.
        # 37
        'vm_keyname': {'valid': '', 'test_cases': {'invalid-unit-test': 'group add, "invalid-unit-test" failed - specified item does not exist: vm_keyname=invalid-unit-test, group_name=invalid-unit-test.'}}
    }

    parameters_requests(gvar, '/group/add/', ut_id(gvar, 'gtg4'), ut_id(gvar, 'gtu5'), parameters)

    # Parameter combinations that do not fit the above format.
    # 38
    execute_csv2_request(
        gvar, 1, 'GV', 'request contained a rejected/bad parameter "job_scratch".',
        '/group/add/', group=ut_id(gvar, 'gtg4'), form_data={
            'group_name': 'invalid-unit-test',
            'htcondor_fqdn': gvar['fqdn'],
            'job_scratch': 0
        },
        server_user=ut_id(gvar, 'gtu5')
    )

    # 39
    execute_csv2_request(
        gvar, 1, 'GV', 'group add, "{}" failed - user "{}" was specified twice.'.format(ut_id(gvar, 'group-invalid-unit-test'), ut_id(gvar, 'gtu3')),
        '/group/add/', group=ut_id(gvar, 'gtg4'), form_data={
            'group_name': ut_id(gvar, 'group-invalid-unit-test'),
            'username.1': ut_id(gvar, 'gtu3'),
            'username.2': ut_id(gvar, 'gtu3'),
            'htcondor_fqdn': gvar['fqdn']
        },
        server_user=ut_id(gvar, 'gtu5')
    )

    # 40
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'gtg1')),
        '/group/add/', group=ut_id(gvar, 'gtg4'), form_data={
            'group_name': ut_id(gvar, 'gtg1'),
            'username.1': ut_id(gvar, 'gtu5'),
            'htcondor_fqdn': gvar['fqdn']
        },
        server_user=ut_id(gvar, 'gtu5')
    )

    # 41 Verify that 28 actually added a group.
    execute_csv2_request(
        gvar, 0, None, None,
        '/group/list/', group=ut_id(gvar, 'gtg1'),
        expected_list='group_list', list_filter={'group_name': ut_id(gvar, 'gtg1')},
        values={
            'htcondor_fqdn': gvar['fqdn'],
            'htcondor_container_hostname': None,
            'htcondor_other_submitters': None,
            'metadata_names': 'default.yaml.j2'
        },
        server_user=ut_id(gvar, 'gtu5')
    )

    # 42 Verify that the user was updated correctly.
    execute_csv2_request(
        gvar, 0, None, None, '/user/list/', group=ut_id(gvar, 'gtg4'),
        expected_list='user_list', list_filter={'username': ut_id(gvar, 'gtu5')},
        values={'username': ut_id(gvar, 'gtu5'), 'user_groups': ut_id(gvar, 'gtg1,gtg4,gtg5')},
        server_user=ut_id(gvar, 'gtu5')
    )

    # 43
    execute_csv2_request(
        gvar, 1, 'GV', '"{0}" failed - (1062, "Duplicate entry \'{0}\' for key \'PRIMARY\'").'.format(ut_id(gvar, 'gtg1')),
        '/group/add/', group=ut_id(gvar, 'gtg4'), form_data={
            'group_name': ut_id(gvar, 'gtg1'),
            'htcondor_fqdn': gvar['fqdn']
        },
        server_user=ut_id(gvar, 'gtu5')
    )

    # 44 Verify that users don't need to be given.
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'gtg2')),
        '/group/add/', group=ut_id(gvar, 'gtg4'), form_data={
            'group_name': ut_id(gvar, 'gtg2'),
            'htcondor_fqdn': gvar['fqdn'],
        },
        server_user=ut_id(gvar, 'gtu5')
    )

    # 45 Verify that 21 actually created a group
    execute_csv2_request(
        gvar, 0, None, None,
        '/group/list/', group=ut_id(gvar, 'gtg4'),
        expected_list='group_list', list_filter={'group_name': ut_id(gvar, 'gtg2')},
        values={'group_name': ut_id(gvar, 'gtg2'),
            'htcondor_fqdn': gvar['fqdn'],
            'htcondor_container_hostname': None,
            'htcondor_other_submitters': None,
            'metadata_names': 'default.yaml.j2'
        },
        server_user=ut_id(gvar, 'gtu5')
    )

    # 46
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'gtg3')),
        '/group/add/', group=ut_id(gvar, 'gtg4'), form_data={
            'group_name': ut_id(gvar, 'gtg3'),
            'htcondor_fqdn': gvar['fqdn'],
            'job_cpus': 1,
            'job_ram': 1,
            'job_disk': 1,
            'job_swap': 1,
            'vm_flavor': '',
            'vm_image': '',
            'vm_keyname': '',
            'vm_network': '',
        },
        server_user=ut_id(gvar, 'gtu5')
    )

if __name__ == "__main__":
    main(None)
