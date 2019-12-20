from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id
from sys import argv

# lno: GV - error code identifier.

def main(gvar, user_secret):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv2_request(gvar, argv[0])
    
    # 01
    execute_csv2_request(
        gvar, 1, 'GV', 'invalid method "GET" specified.',
        '/group/add/'
    )

    # 02
    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 403, forbidden.',
        '/group/add/',
        server_user=ut_id(gvar, 'gtu1'), server_pw=user_secret
    )

    # 03
    execute_csv2_request(
        gvar, 1, None, 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'gtu2')),
        '/group/add/',
        server_user=ut_id(gvar, 'gtu2'), server_pw=user_secret
    )

    # 04
    execute_csv2_request(
        gvar, 1, 'GV', 'cannot switch to invalid group "invalid-unit-test".',
        '/group/add/?invalid-unit-test'
    )

    # 05
    execute_csv2_request(
        gvar, 1, 'GV', 'request did not contain mandatory parameter "group_name".',
        '/group/add/', form_data={'htcondor_fqdn': 'invalid-unit-test'}
    )

    # 06
    execute_csv2_request(
        gvar, 1, 'GV', 'Data too long for column \'group_name\' at row 1',
        '/group/add/', form_data={'group_name': ut_id(gvar, 'group-invalid-unit-test-too-long')}
    )

    # 07
    execute_csv2_request(
        gvar, 1, 'GV', 'request contained a bad parameter "invalid-unit-test".',
        '/group/add/', form_data={'invalid-unit-test': 'invalid-unit-test'}
    )

    # 08
    execute_csv2_request(
        gvar, 1, 'GV', 'value specified for "group_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        '/group/add/', form_data={'group_name': 'Invalid-Unit-Test'}
    )

    # 09
    execute_csv2_request(
        gvar, 1, 'GV', 'value specified for "group_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        '/group/add/', form_data={'group_name': 'invalid-unit-test-'}
    )

    # 10
    execute_csv2_request(
        gvar, 1, 'GV', 'value specified for "group_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        '/group/add/', form_data={'group_name': 'invalid!unit!test'}
    )

    # 11
    execute_csv2_request(
        gvar, 1, 'GV', 'Data too long for column \'group_name\' at row 1',
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'thisisagroupnametoolongtoinsertintothedatabasethisisagroupnametoolongtoinsertintothedatabasethisisagroupnametoolongtoinsertintothedatabase'),
            'htcondor_fqdn': 'invalid-unit-test'
        }
    )

    # 12
    execute_csv2_request(
        gvar, 1, 'GV', 'value specified for "group_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        '/group/add/', form_data={
            'group_name': '',
            'htcondor_fqdn': 'invalid-unit-test'
        }
    )


    # 13
    execute_csv2_request(
        gvar, 1, 'GV', 'parameter "htcondor_fqdn" contains an empty string which is specifically disallowed.',
        '/group/add/', form_data={
            'group_name': 'invalid-unit-test',
            'htcondor_fqdn': ''
        }
    )

    # 14
    execute_csv2_request(
        gvar, 1, 'GV', 'specified user "invalid-unit-test" does not exist.',
        '/group/add/', form_data={
            'username.1': 'invalid-unit-test',
            'group_name': ut_id(gvar, 'group-invalid-unit-test'),
            'htcondor_fqdn': 'invalid-unit-test'
        }
    )

    # 15
    execute_csv2_request(
        gvar, 1, 'GV', 'value specified for "user_option" must be one of the following options: [\'add\', \'delete\'].',
        '/group/add/', form_data={
            'user_option': 'invalid-unit-test',
            'group_name': ut_id(gvar, 'group-invalid-unit-test'),
            'htcondor_fqdn': 'invalid-unit-test'
        }
    )

    # 16
    execute_csv2_request(
        gvar, 1, 'GV', 'group add, "{}" failed - user "{}" was specified twice.'.format(ut_id(gvar, 'group-invalid-unit-test'), ut_id(gvar, 'gtu3')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'group-invalid-unit-test'),
            'username.1': ut_id(gvar, 'gtu3'),
            'username.2': ut_id(gvar, 'gtu3'),
            'htcondor_fqdn': 'invalid-unit-test'
        }
    )

    # 17
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'gtg1')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'gtg1'),
            'username.1': ut_id(gvar, 'gtu3'),
            'htcondor_fqdn': 'group-unit-test-one.ca'
        }
    )

    # 18
    execute_csv2_request(
        gvar, 0, None, None,
        '/group/list/?{}'.format(ut_id(gvar, 'gtg1')),
        list='group_list', filter={'group_name': ut_id(gvar, 'gtg1')},
        values={'group_name': ut_id(gvar, 'gtg1'), 'htcondor_fqdn': 'group-unit-test-one.ca', 'htcondor_container_hostname': None, 'htcondor_other_submitters': None, 'metadata_names': 'default.yaml.j2'}
    )

    # 19
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'gtu3')},
        values={'username': ut_id(gvar, 'gtu3'), 'user_groups': ut_id(gvar, 'gtg1,gtg4,gtg5')}
    )

    # 20
    execute_csv2_request(
        gvar, 1, 'GV', '"{0}" failed - (1062, "Duplicate entry \'{0}\' for key \'PRIMARY\'").'.format(ut_id(gvar, 'gtg1')),
        '/group/add/', form_data={'group_name': ut_id(gvar, 'gtg1'), 'htcondor_fqdn': 'invalid-unit-test'}
    )

    # 21
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'gtg2')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'gtg2'),
            'htcondor_fqdn': 'unit-test-group-two.ca'
        }
    )

    # 22
    execute_csv2_request(
        gvar, 0, None, None,
        '/group/list/?{}'.format(ut_id(gvar, 'gtg2')),
        list='group_list', filter={'group_name': ut_id(gvar, 'gtg2')},
        values={'group_name': ut_id(gvar, 'gtg2'), 'htcondor_fqdn': 'unit-test-group-two.ca', 'htcondor_container_hostname': None, 'htcondor_other_submitters': None, 'metadata_names': 'default.yaml.j2'}
    )

    # 23
    execute_csv2_request(
        gvar, 1, 'GV', 'group add value specified for "job_cpus" must be an integer value.',
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'gtg3'),
            'htcondor_fqdn': 'unit-test-group-three.ca',
            'job_cpus': 'invalid-unit-test'
        }
    )

    # 24
    execute_csv2_request(
        gvar, 1, 'GV', 'group add value specified for "job_ram" must be an integer value.',
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'gtg3'),
            'htcondor_fqdn': 'unit-test-group-three.ca',
            'job_ram': 'invalid-unit-test'
        }
    )

    # 25
    execute_csv2_request(
        gvar, 1, 'GV', 'group add value specified for "job_disk" must be an integer value.',
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'gtg3'),
            'htcondor_fqdn': 'unit-test-group-three.ca',
            'job_disk': 'invalid-unit-test'
        }
    )

    # 26
    execute_csv2_request(
        gvar, 1, 'GV', 'request contained a rejected/bad parameter "job_scratch".',
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'gtg3'),
            'htcondor_fqdn': 'unit-test-group-three.ca',
            'job_scratch': 'invalid-unit-test'
        }
    )

    # 27
    execute_csv2_request(
        gvar, 1, 'GV', 'group add value specified for "job_swap" must be an integer value.',
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'gtg3'),
            'htcondor_fqdn': 'unit-test-group-three.ca',
            'job_swap': 'invalid-unit-test'
        }
    )

    # 28
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'gtg3')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'gtg3'),
            'htcondor_fqdn': 'unit-test-group-three.ca',
            'job_cpus': 1,
            'job_ram': 1,
            'job_disk': 1,
            'job_swap': 1,
            'vm_flavor': '',
            'vm_image': '',
            'vm_keyname': '',
            'vm_network': '',
        }
    )

    # 29
    execute_csv2_request(
        gvar, 1, 'GV', 'group add, "{0}" failed - specified item does not exist: vm_image=invalid-unit-test, group_name={0}.'.format(ut_id(gvar, 'invalid-unit-test')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'invalid-unit-test'),
            'htcondor_fqdn': 'invalid-unit-test.ca',
            'vm_image': 'invalid-unit-test',
        }
    )

    # 30
    execute_csv2_request(
        gvar, 1, 'GV', 'group add, "{0}" failed - specified item does not exist: vm_flavor=invalid-unit-test, group_name={0}.'.format(ut_id(gvar, 'invalid-unit-test')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'invalid-unit-test'),
            'htcondor_fqdn': 'invalid-unit-test.ca',
            'vm_flavor': 'invalid-unit-test',
        }
    )

    # 31
    execute_csv2_request(
        gvar, 1, 'GV', 'group add, "{0}" failed - specified item does not exist: vm_network=invalid-unit-test, group_name={0}.'.format(ut_id(gvar, 'invalid-unit-test')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'invalid-unit-test'),
            'htcondor_fqdn': 'invalid-unit-test.ca',
            'vm_network': 'invalid-unit-test',
        }
    )

    # 32
    execute_csv2_request(
        gvar, 1, 'GV', 'group add, "{0}" failed - specified item does not exist: vm_keyname=invalid-unit-test, group_name={0}.'.format(ut_id(gvar, 'invalid-unit-test')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'invalid-unit-test'),
            'htcondor_fqdn': 'invalid-unit-test.ca',
            'vm_keyname': 'invalid-unit-test',
        }
    )

if __name__ == "__main__":
    main(None)
