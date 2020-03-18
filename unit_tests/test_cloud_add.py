from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, sanity_requests, parameters_requests
from sys import argv

# lno: CV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)

    # Bad requests.
    # 01 - 05
    sanity_requests(gvar, '/cloud/add/', ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctu1'), ut_id(gvar, 'ctg2'), ut_id(gvar, 'ctu2'))
    
    parameters = {
        # 06 Send a GET request.
        # 07 Give an invalid parameter.
        # 08 Omit cloud_name.
        # 09 Give two cloud_names.
        'cloud_name': {'valid': 'invalid-unit-test', 'test_cases': {
            # 10
            '': 'cloud add value specified for "cloud_name" must not be the empty string.',
            # 11
            'Invalid-Unit-Test': 'cloud add value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 12
            'invalid-unit--test': 'cloud add value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 13
            '-invalid-unit-test': 'cloud add value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 14
            'invalid-unit-test!': 'cloud add value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 15
            'cloud-name-that-is-too-long-for-the-database': 'Data too long for column \'cloud_name\' at row 1',
            # 16 Attempt to create a cloud that already exists.
            ut_id(gvar, 'ctc2'): 'Duplicate entry \'{}-{}\' for key \'PRIMARY\''.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc2'))
        }, 'mandatory': True},
        # 17 Omit cloud_type.
        # 18 Give two cloud_types.
        # 19
        'cloud_type': {'valid': 'local', 'test_cases': {'invalid-unit-test': 'cloud add value specified for "cloud_type" must be one of the following options: [\'amazon\', \'azure\', \'google\', \'local\', \'opennebula\', \'openstack\'].'}, 'mandatory': True},
        # 20 Omit authurl.
        # 21 Give two authurls.
        # 22
        'authurl': {'valid': gvar['cloud_credentials']['authurl'], 'test_cases': {'': 'cloud add parameter "authurl" contains an empty string which is specifically disallowed.'}, 'mandatory': True},
        # 23 Omit username.
        # 24 Give two usernames.
        # 25
        'username': {'valid': gvar['cloud_credentials']['username'], 'test_cases': {'': 'cloud add parameter "username" contains an empty string which is specifically disallowed.'}, 'mandatory': True},
        # 26 Omit password.
        # 27 Give two passwords.
        # 28
        'password': {'valid': gvar['cloud_credentials']['password'], 'test_cases': {'': 'cloud add parameter "password" contains an empty string which is specifically disallowed.'}, 'mandatory': True},
        # 29 Omit project.
        # 30 Give two projects.
        # 31
        'project': {'valid': gvar['cloud_credentials']['project'], 'test_cases': {'': 'cloud add parameter "project" contains an empty string which is specifically disallowed.'}, 'mandatory': True},
        # 32 Omit region.
        # 33 Give two regions.
        # 34
        'region': {'valid': gvar['cloud_credentials']['region'], 'test_cases': {'': 'cloud add parameter "region" contains an empty string which is specifically disallowed.'}, 'mandatory': True},
        # 35 Give two ram_ctls.
        # 36
        'ram_ctl': {'valid': 0, 'test_cases': {'invalid-unit-test': 'cloud add value specified for "ram_ctl" must be an integer value.'}},
        # 37 Give two cores_ctls.
        # 38
        'cores_ctl': {'valid': 0, 'test_cases': {'invalid-unit-test': 'cloud add value specified for "cores_ctl" must be an integer value.'}},
        # 39 Give two vm_keep_alives.
        # 40
        'vm_keep_alive': {'valid': 0, 'test_cases': {'invalid-unit-test': 'cloud add value specified for "vm_keep_alive" must be an integer value.'}},
        # 41 Give two enableds.
        # 42
        'enabled': {'valid': 0, 'test_cases': {'invalid-unit-test': 'cloud add boolean value specified for "enabled" must be one of the following: true, false, yes, no, 1, or 0.'}},
        # 43 Give two spot_prices.
        # 44
        'spot_price': {'valid': 0.0, 'test_cases': {'invalid-unit-test': 'cloud add value specified for "spot_price" must be a floating point value.'}},
        # 45 Give metadata_name and metadata_name.1.
        # 46
        'metadata_name': {'valid': '', 'test_cases': {'invalid-unit-test': 'cloud add, "invalid-unit-test" failed - specified metadata_name "invalid-unit-test" does not exist.'}, 'array_field': True},
        # 47 Give two vm_images.
        # 48
        'vm_image': {'valid': '', 'test_cases': {'invalid-unit-test': 'cloud add, "invalid-unit-test" failed - specified item does not exist: vm_image=invalid-unit-test, group_name={}, cloud_name=invalid-unit-test.'.format(ut_id(gvar, 'ctg1'))}},
        # 49 Give two vm_flavors.
        # 50
        'vm_flavor': {'valid': '', 'test_cases': {'invalid-unit-test': 'cloud add, "invalid-unit-test" failed - specified item does not exist: vm_flavor=invalid-unit-test, group_name={}, cloud_name=invalid-unit-test.'.format(ut_id(gvar, 'ctg1'))}},
        # 51 Give two vm_networks.
        # 52
        'vm_network': {'valid': '', 'test_cases': {'invalid-unit-test': 'cloud add, "invalid-unit-test" failed - specified item does not exist: vm_network=invalid-unit-test, group_name={}, cloud_name=invalid-unit-test.'.format(ut_id(gvar, 'ctg1'))}},
        # 53 Give two vm_keynames.
        # 54
        'vm_keyname': {'valid': '', 'test_cases': {'invalid-unit-test': 'cloud add, "invalid-unit-test" failed - specified item does not exist: vm_keyname=invalid-unit-test, group_name={}, cloud_name=invalid-unit-test.'.format(ut_id(gvar, 'ctg1'))}}
    }

    parameters_requests(gvar, '/cloud/add/', ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctu1'), parameters)

    # Parameter combinations that do not fit well into the above format.
    # 55 Known to fail if run twice without setup or cleanup in between.
    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully added.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc5')),
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={
            'cloud_name': ut_id(gvar, 'ctc5'),
            'cloud_type': 'openstack',
            'priority': '31',
            'cacertificate': None,
            'user_domain_name': 'Default',
            'project_domain_name': 'Default',
            'enabled': 1,
            'vm_keep_alive': -31,
            'metadata_name': ut_id(gvar, 'cty1'),
            'spot_price': 10,
            'cores_softmax': -1,
            **gvar['cloud_credentials']
            },
        server_user=ut_id(gvar, 'ctu1')
    )

    # 56 Ensure that 40 actually created a cloud.
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
            'project_domain_name': 'Default',
            'enabled': 1,
            'vm_keep_alive': -31,
            'group_exclusions': ut_id(gvar, 'cty1'),
            'spot_price': 10,
            },
        server_user=ut_id(gvar, 'ctu1')
    )

    # 57 Known to fail if run twice without setup or cleanup in between.
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
        server_user=ut_id(gvar, 'ctu1')
    )

    # 58 Ensure that 42 actually created a cloud.
    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/list/', group=ut_id(gvar, 'ctg1'),
        expected_list='cloud_list', list_filter={'cloud_name': ut_id(gvar, 'ctc6')},
        values={
            'group_name': ut_id(gvar, 'ctg1'),
            'cloud_name': ut_id(gvar, 'ctc6'),
            'group_exclusions': ut_id(gvar, 'cty1,cty2,cty3')
            },
        server_user=ut_id(gvar, 'ctu1')
    )

if __name__ == "__main__":
    main(None)
