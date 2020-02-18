from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, sanity_requests, parameters_requests
from sys import argv

# lno: CV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv2_request(gvar, argv[0])

    # Bad requests.
    # 01 - 05
    sanity_requests(gvar, '/cloud/add/', ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctu3'), ut_id(gvar, 'ctg2'), ut_id(gvar, 'ctu1'))
    
    # 6 Omit form_data.
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud add request did not contain mandatory parameter "cloud_name".',
        '/cloud/add/', group=ut_id(gvar, 'ctg1'),
        server_user=ut_id(gvar, 'ctu3')
    )

    PARAMETERS = [
        # 07 Give an invalid parameter.
        # 08 Omit cloud_name.
        ('cloud_name', {
            # 09
            '': 'cloud add value specified for "cloud_name" must not be the empty string.',
            # 10
            'Invalid-Unit-Test': 'cloud add value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 11
            'invalid-unit--test': 'cloud add value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 12
            '-invalid-unit-test': 'cloud add value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 13
            'invalid-unit-test!': 'cloud add value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 14
            'cloud-name-that-is-too-long-for-the-database': 'Data too long for column \'cloud_name\' at row 1'
        }, 'invalid-unit-test'),
        # 15 Omit cloud_type.
        # 16
        ('cloud_type', {'invalid-unit-test': 'cloud add value specified for "cloud_type" must be one of the following options: [\'amazon\', \'azure\', \'google\', \'local\', \'opennebula\', \'openstack\'].'}, 'local'),
        # 17 Omit authurl.
        # 18
        ('authurl', {'': 'cloud add parameter "authurl" contains an empty string which is specifically disallowed.'}, 'invalid-unit-test'),
        # 19 Omit username.
        # 20
        ('username', {'': 'cloud add parameter "username" contains an empty string which is specifically disallowed.'}, 'invalid-unit-test'),
        # 21 Omit password.
        # 22
        ('password', {'': 'cloud add parameter "password" contains an empty string which is specifically disallowed.'}, 'invalid-unit-test'),
        # 23 Omit project.
        # 24
        ('project', {'': 'cloud add parameter "project" contains an empty string which is specifically disallowed.'}, 'invalid-unit-test'),
        # 25 Omit region.
        # 26
        ('region', {'': 'cloud add parameter "region" contains an empty string which is specifically disallowed.'}, 'invalid-unit-test'),
        # 27 Specify a parameter that is explicitly rejected.
        ('server_meta_ctl', {'invalid-unit-test': 'bad parameter "server_meta_ctl"'}),
        # 28
        ('ram_ctl', {'invalid-unit-test': 'cloud add value specified for "ram_ctl" must be an integer value.'}),
        # 29
        ('cores_ctl', {'invalid-unit-test': 'cloud add value specified for "cores_ctl" must be an integer value.'}),
        # 30
        ('vm_keep_alive', {'invalid-unit-test': 'cloud add value specified for "vm_keep_alive" must be an integer value.'}),
        # 31
        ('enabled', {'invalid-unit-test': 'cloud add boolean value specified for "enabled" must be one of the following: true, false, yes, no, 1, or 0.'}),
        # 32
        ('spot_price', {'invalid-unit-test': 'cloud add value specified for "spot_price" must be a floating point value.'}),
        # 33
        ('metadata_name', {'invalid-unit-test': 'cloud add, "invalid-unit-test" failed - specified metadata_name "invalid-unit-test" does not exist.'}),
        # 34
        ('vm_image', {'invalid-unit-test': 'cloud add, "invalid-unit-test" failed - specified item does not exist: vm_image=invalid-unit-test, group_name={}, cloud_name=invalid-unit-test.'.format(ut_id(gvar, 'ctg1'))}),
        # 35
        ('vm_flavor', {'invalid-unit-test': 'cloud add, "invalid-unit-test" failed - specified item does not exist: vm_flavor=invalid-unit-test, group_name={}, cloud_name=invalid-unit-test.'.format(ut_id(gvar, 'ctg1'))}),
        # 36
        ('vm_network', {'invalid-unit-test': 'cloud add, "invalid-unit-test" failed - specified item does not exist: vm_network=invalid-unit-test, group_name={}, cloud_name=invalid-unit-test.'.format(ut_id(gvar, 'ctg1'))}),
        # 37
        ('vm_keyname', {'invalid-unit-test': 'cloud add, "invalid-unit-test" failed - specified item does not exist: vm_keyname=invalid-unit-test, group_name={}, cloud_name=invalid-unit-test.'.format(ut_id(gvar, 'ctg1'))})
    ]

    parameters_requests(gvar, '/cloud/add/', ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctu3'), PARAMETERS)

    # Parameter combinations that do not fit well into the above format.
    # 38 Give two cloud names.
    execute_csv2_request(
        gvar, 1, 'CV', 'Operand should contain 1 column(s)',
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={
            'cloud_name.1': 'invalid-unit-test',
            'cloud_name.2': 'invalid-unit-test',
            'cloud_type': 'local',
            'authurl': 'invalid-unit-test',
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'region': 'invalid-unit-test',
            },
        server_user=ut_id(gvar, 'ctu3')
    )

    # 39
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud add, "invalid-unit-test" failed - specified metadata_name "invalid-unit-test" does not exist.',
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={
            'cloud_name': 'invalid-unit-test',
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test',
            'region': 'invalid-unit-test',
            'cloud_type': 'local',
            'metadata_name.1': ut_id(gvar, 'cty1'),
            'metadata_name.2': 'invalid-unit-test'
            },
        server_user=ut_id(gvar, 'ctu3')
    )

    # 40
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud add, "{}" failed - metadata name "{}" was specified twice.'.format(ut_id(gvar, 'cloud-invalid-unit-test'), ut_id(gvar, 'cty1')),
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={
            'cloud_name': ut_id(gvar, 'cloud-invalid-unit-test'),
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test',
            'region': 'invalid-unit-test',
            'cloud_type': 'local',
            'metadata_name.1': ut_id(gvar, 'cty1'),
            'metadata_name.2': ut_id(gvar, 'cty1'),
            },
        server_user=ut_id(gvar, 'ctu3')
    )

    # 41 Known to fail if run twice without setup or cleanup in between.
    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully added.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc5')),
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={
            'cloud_name': ut_id(gvar, 'ctc5'),
            'cloud_type': 'openstack',
            'priority': '31',
            'cacertificate': None,
            'user_domain_name': 'Default',
            'project_domain_name': '\'Default\'',
            'vm_flavor': '',
            'vm_image': '',
            'vm_keyname': '',
            'vm_network': '',
            'enabled': 0,
            'vm_keep_alive': -31,
            'metadata_name': ut_id(gvar, 'cty1'),
            'spot_price': 10,
            'cores_softmax': -1,
            **gvar['cloud_credentials']
            },
        server_user=ut_id(gvar, 'ctu3')
    )

    # 42 Ensure that 40 actually created a cloud.
    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/list/', group=ut_id(gvar, 'ctg1'),
        expected_list='cloud_list', list_filter={'cloud_name': ut_id(gvar, 'ctc5')},
        values={
            'group_name': ut_id(gvar, 'ctg1'),
            'cloud_name': ut_id(gvar, 'ctc5'),
            'authurl': gvar['cloud_credentials']['authurl'],
            'username': gvar['cloud_credentials']['username'],
            'region': gvar['cloud_credentials']['region'],
            'project': gvar['cloud_credentials']['project'],
            'cloud_type': 'openstack',
            'cloud_priority': 31,
            'cacertificate': None,
            'user_domain_name': 'Default',
            'project_domain_name': '\'Default\'',
            'vm_flavor': '',
            'vm_image': '',
            'vm_keyname': '',
            'vm_network': '',
            'enabled': 0,
            'vm_keep_alive': -31,
            'group_exclusions': ut_id(gvar, 'cty1'),
            'spot_price': 10,
            'cores_used': 0,
            'ram_used': 0
            },
        server_user=ut_id(gvar, 'ctu3')
    )

    # 43 Known to fail if run twice without setup or cleanup in between.
    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully added.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc6')),
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={
            'cloud_name': ut_id(gvar, 'ctc6'),
            'cloud_type': 'openstack',
            'metadata_name.1': ut_id(gvar, 'cty1'),
            'metadata_name.2': ut_id(gvar, 'cty2'),
            'metadata_name.3': ut_id(gvar, 'cty3'),
            **gvar['cloud_credentials']
            },
        server_user=ut_id(gvar, 'ctu3')
    )

    # 44 Ensure that 42 actually created a cloud.
    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/list/', group=ut_id(gvar, 'ctg1'),
        expected_list='cloud_list', list_filter={'cloud_name': ut_id(gvar, 'ctc6')},
        values={
            'group_name': ut_id(gvar, 'ctg1'),
            'cloud_name': ut_id(gvar, 'ctc6'),
            'group_exclusions': ut_id(gvar, 'cty1,cty2,cty3')
            },
        server_user=ut_id(gvar, 'ctu3')
    )

    # 45 Attempt to create a cloud that already exists.
    execute_csv2_request(
        gvar, 1, 'CV', 'Duplicate entry \'{}-{}\' for key \'PRIMARY\''.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc5')),
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={
            'cloud_name': ut_id(gvar, 'ctc5'),
            'region': 'invalid-unit-test',
            'cloud_type': 'local',
            **gvar['cloud_credentials']
            },
        server_user=ut_id(gvar, 'ctu3')
    )

if __name__ == "__main__":
    main(None)
