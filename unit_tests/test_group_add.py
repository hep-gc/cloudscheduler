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
    sanity_requests(gvar, '/group/add/', ut_id(gvar, 'gtg5'), ut_id(gvar, 'gtu5'), ut_id(gvar, 'gtg7'), ut_id(gvar, 'gtu2'))

    # 06 Attempt as an unprivileged user.
    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 403, forbidden.',
        '/group/add/',
        server_user=ut_id(gvar, 'gtu3')
    )

    PARAMETERS = [
        # 07 Give an invalid parameter.
        # 08 Omit group_name.
        ('group_name', {
            # 09
            '': 'group add value specified for "group_name" must not be the empty string.',
            # 10
            'Invalid-Unit-Test': 'group add value specified for "group_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 11
            'invalid-unit--test': 'group add value specified for "group_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 12
            '-invalid-unit-test': 'group add value specified for "group_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 13
            'invalid-unit-test!': 'group add value specified for "group_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 14
            'group-name-that-is-too-long-for-the-database': 'Data too long for column \'group_name\' at row 1'
        }, 'invalid-unit-test'),
        # 15
        ('htcondor_fqdn', {'': 'parameter "htcondor_fqdn" contains an empty string which is specifically disallowed.'}),
        # 16
        ('username.1', {'invalid-unit-test': 'specified user "invalid-unit-test" does not exist.'}),
        # 17
        ('user_option', {'invalid-unit-test': 'value specified for "user_option" must be one of the following options: [\'add\', \'delete\'].'}),
        # 18
        ('job_cpus', {'invalid-unit-test': 'group add value specified for "job_cpus" must be an integer value.'}),
        # 19
        ('job_ram', {'invalid-unit-test': 'group add value specified for "job_ram" must be an integer value.'}),
        # 20
        ('job_disk', {'invalid-unit-test': 'group add value specified for "job_disk" must be an integer value.'}),
        # 21
        ('job_swap', {'invalid-unit-test': 'group add value specified for "job_swap" must be an integer value.'}),
        # 22
        ('job_scratch', {'invalid-unit-test': 'request contained a rejected/bad parameter "job_scratch".'}),
        # 23
        ('vm_image', {'invalid-unit-test': 'group add, "invalid-unit-test" failed - specified item does not exist: vm_image=invalid-unit-test, group_name=invalid-unit-test.'}),
        # 24
        ('vm_flavor', {'invalid-unit-test': 'group add, "invalid-unit-test" failed - specified item does not exist: vm_flavor=invalid-unit-test, group_name=invalid-unit-test.'}),
        # 25
        ('vm_network', {'invalid-unit-test': 'group add, "invalid-unit-test" failed - specified item does not exist: vm_network=invalid-unit-test, group_name=invalid-unit-test.'}),
        # 26
        ('vm_keyname', {'invalid-unit-test': 'group add, "invalid-unit-test" failed - specified item does not exist: vm_keyname=invalid-unit-test, group_name=invalid-unit-test.'})
    ]

    parameters_requests(gvar, '/group/add/', ut_id(gvar, 'gtg5'), ut_id(gvar, 'gtu5'), PARAMETERS)

    # Parameter combinations that do not fit the above format.
    #
    execute_csv2_request(
        gvar, 1, 'GV', 'Operand should contain 1 column(s)',
        '/group/add/', form_data={
            'group_name.1': 'invalid-unit-test-1',
            'group_name.2': 'invalid-unit-test-2',
            'htcondor_fqdn': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'gtu5')
    )

    # 27
    execute_csv2_request(
        gvar, 1, 'GV', 'group add, "{}" failed - user "{}" was specified twice.'.format(ut_id(gvar, 'group-invalid-unit-test'), ut_id(gvar, 'gtu3')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'group-invalid-unit-test'),
            'username.1': ut_id(gvar, 'gtu3'),
            'username.2': ut_id(gvar, 'gtu3'),
            'htcondor_fqdn': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'gtu5')
    )

    # 28
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'gtg1')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'gtg1'),
            'username.1': ut_id(gvar, 'gtu5'),
            'htcondor_fqdn': gvar['fqdn']
        },
        server_user=ut_id(gvar, 'gtu5')
    )

    # 29 Verify that 17 actually added a group.
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

    # 30 Verify that the user was updated correctly.
    execute_csv2_request(
        gvar, 0, None, None, '/user/list/',
        expected_list='user_list', list_filter={'username': ut_id(gvar, 'gtu5')},
        values={'username': ut_id(gvar, 'gtu5'), 'user_groups': ut_id(gvar, 'gtg1,gtg4,gtg5')},
        server_user=ut_id(gvar, 'gtu5')
    )

    # 20
    execute_csv2_request(
        gvar, 1, 'GV', '"{0}" failed - (1062, "Duplicate entry \'{0}\' for key \'PRIMARY\'").'.format(ut_id(gvar, 'gtg1')),
        '/group/add/', form_data={'group_name': ut_id(gvar, 'gtg1'), 'htcondor_fqdn': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'gtu5')
    )

    # 21 Verify that users don't need to be given.
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'gtg2')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'gtg2'),
            'htcondor_fqdn': gvar['fqdn'],
        },
        server_user=ut_id(gvar, 'gtu5')
    )

    # 22 Verify that 21 actually created a group
    execute_csv2_request(
        gvar, 0, None, None,
        '/group/list/',
        expected_list='group_list', list_filter={'group_name': ut_id(gvar, 'gtg2')},
        values={'group_name': ut_id(gvar, 'gtg2'),
            'htcondor_fqdn': gvar['fqdn'],
            'htcondor_container_hostname': None,
            'htcondor_other_submitters': None,
            'metadata_names': 'default.yaml.j2'
        },
        server_user=ut_id(gvar, 'gtu5')
    )

    # 28
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'gtg3')),
        '/group/add/', form_data={
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
