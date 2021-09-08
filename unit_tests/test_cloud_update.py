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

    # 01 - 05
    sanity_requests(gvar, '/cloud/update/', ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctu1'), ut_id(gvar, 'ctg2'), ut_id(gvar, 'ctu2'))

    parameters = {
        # 06 Send a GET request.
        # 07 Give an invalid parameter.
        # 08 Omit cloud_name.
        # 09 Give two cloud_names.
        'cloud_name': {'valid': ut_id(gvar, 'ctc3'), 'test_cases': {
            # 10
            '': 'cloud update value specified for "cloud_name" must not be the empty string.',
            # 11
            'Invalid-unit-test': 'cloud update value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 12
            'invalid-unit-test-': 'cloud update value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 13
            'invalid-unit-test!': 'cloud update value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
        }, 'mandatory': True},
        # 14 Give two authurls.
        # 15
        'authurl': {'valid': gvar['cloud_credentials']['authurl'], 'test_cases': {'': 'parameter "authurl" contains an empty string which is specifically disallowed.'}},
        # 16 Give two usernames.
        # 17
        'username': {'valid': gvar['cloud_credentials']['username'], 'test_cases': {'': 'insufficient credentials to establish openstack v3 session, check if missing any user/project info'}},
        # 18 Give two passwords.
        # 19
        'password': {'valid': gvar['cloud_credentials']['password'], 'test_cases': {'': 'insufficient credentials to establish openstack v3 session, check if missing any user/project info'}},
        # 20 Give two projects.
        # 21
        'project': {'valid': gvar['cloud_credentials']['project'], 'test_cases': {'': 'parameter "project" contains an empty string which is specifically disallowed.'}},
        # 22 Give two regions.
        # 23
        'region': {'valid': gvar['cloud_credentials']['region'], 'test_cases': {'': 'parameter "region" contains an empty string which is specifically disallowed.'}},
        # 24 Give two cloud_types.
        # 25
        'cloud_type': {'valid': 'local', 'test_cases': {'invalid-unit-test': 'value specified for "cloud_type" must be one of the following options: [\'amazon\', \'local\', \'openstack\'].'}},
        # 26 Give two enableds.
        # 27
        'enabled': {'valid': 0, 'test_cases': {'invalid-unit-test': 'boolean value specified for "enabled" must be one of the following: true, false, yes, no, 1, or 0.'}},
        # 28 Give two vm_keep_alives.
        # 29
        'vm_keep_alive': {'valid': 0, 'test_cases': {'invalid-unit-test': 'value specified for "vm_keep_alive" must be an integer value.'}},
        # 30 Give two spot_prices.
        # 31
        'spot_price': {'valid': 0.0, 'test_cases': {'invalid-unit-test': 'cloud update value specified for "spot_price" must be a floating point value.'}},
        # 32 Give both metadata_name and metadata_name.1.
        # 33
        'metadata_name': {'valid': ut_id(gvar, 'cty2'), 'test_cases': {'invalid-unit-test': 'cloud update, "{}" failed - specified metadata_name "invalid-unit-test" does not exist.'.format(ut_id(gvar, 'ctc3'))}, 'array_field': True},
        # 34 Give two metdata_options.
        # 35
        'metadata_option': {'valid': 'add', 'test_cases': {'invalid-unit-test': 'value specified for "metadata_option" must be one of the following options: [\'add\', \'delete\'].'}},
        # 36 Give two vm_images.
        # 37
        'vm_image': {'valid': '', 'test_cases': {'invalid-unit-test': 'cloud update, "{0}" failed - specified item does not exist: vm_image=invalid-unit-test, group_name={1}, cloud_name={0}.'.format(ut_id(gvar, 'ctc3'), ut_id(gvar, 'ctg1'))}},
        # 38 Give two vm_flavors.
        # 39
        'vm_flavor': {'valid': '', 'test_cases': {'invalid-unit-test': 'cloud update, "{0}" failed - specified item does not exist: vm_flavor=invalid-unit-test, group_name={1}, cloud_name={0}.'.format(ut_id(gvar, 'ctc3'), ut_id(gvar, 'ctg1'))}},
        # 40 Give two vm_networks.
        # 41
        'vm_network': {'valid': '', 'test_cases': {'invalid-unit-test': 'cloud update, "{0}" failed - specified item does not exist: vm_network=invalid-unit-test, group_name={1}, cloud_name={0}.'.format(ut_id(gvar, 'ctc3'), ut_id(gvar, 'ctg1'))}},
        # 42 Give two vm_keynames.
        # 43
        'vm_keyname': {'valid': '', 'test_cases': {'invalid-unit-test': 'cloud update, "{0}" failed - specified item does not exist: vm_keyname=invalid-unit-test, group_name={1}, cloud_name={0}.'.format(ut_id(gvar, 'ctc3'), ut_id(gvar, 'ctg1'))}}
    }

    parameters_requests(gvar, '/cloud/update/', ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctu1'), parameters)

    # 44 Ensure that metadata_option by itself does not qualify as a field to update.
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud update must specify at least one field to update',
        '/cloud/update/', group=ut_id(gvar, 'ctg1'), form_data={'cloud_name': ut_id(gvar, 'ctc3'), 'metadata_option': 'add'},
        server_user=ut_id(gvar, 'ctu1')
    )

    # 45 Attempt to implicitly add metadata that does not exist.
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud update, "{}" failed - specified metadata_name "invalid-unit-test" does not exist.'.format(ut_id(gvar, 'ctc3')),
        '/cloud/update/', group=ut_id(gvar, 'ctg1'), form_data={'cloud_name': ut_id(gvar, 'ctc3'), 'metadata_name': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu1')
    )

    # 46 Attempt to delete non-existent metadata.
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud update, "{}" failed - specified metadata_name "invalid-unit-test" does not exist.'.format(ut_id(gvar, 'ctc3')),
        '/cloud/update/', group=ut_id(gvar, 'ctg1'), form_data={'cloud_name': ut_id(gvar, 'ctc3'), 'metadata_name': 'invalid-unit-test', 'metadata_option': 'delete'},
        server_user=ut_id(gvar, 'ctu1')
    )

    # 47 Ensures that values are as expected before executing requests that are expected to succeed. Known to fail if run twice without setup / cleanup in between.
    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/list/', group=ut_id(gvar, 'ctg1'), expected_list='cloud_list', list_filter={'group_name': ut_id(gvar, 'ctg1'), 'cloud_name': ut_id(gvar, 'ctc3')},
        values={
            'authurl': gvar['cloud_credentials']['authurl'],
            'cacertificate': None,
            'cascading_vm_flavor': None,
            'cascading_vm_image': None,
            'cascading_vm_keep_alive': 0,
            'cascading_vm_keyname': None,
            'cascading_vm_network': None,
            'cascading_vm_security_groups': None,
            'cloud_priority': 0,
            'cloud_type': 'openstack',
            'cores_ctl': -1,
            'cores_foreign': '0',
            'cores_native': '0',
            'cores_softmax': -1,
            'enabled': 1,
            'flavor_exclusions': None,
            'group_exclusions': None,
            # We would check metadata_names here, but their order is unpredictable as far as I know.
            'project': gvar['cloud_credentials']['project'],
            'project_domain_id': '',
            'project_domain_name': 'Default',
            'ram_ctl': -1,
            'ram_foreign': '0',
            'ram_native': '0',
            'region': gvar['cloud_credentials']['region'],
            'spot_price': -1.0,
            'user_domain_id': '',
            'user_domain_name': 'Default',
            'username': gvar['cloud_credentials']['username'],
            'vm_flavor': '',
            'vm_image': '',
            'vm_keep_alive': 0,
            'vm_keyname': None,
            'vm_network': '',
            'vm_security_groups': None
            },
        server_user=ut_id(gvar, 'ctu1')
    )

    # 48 Update several values and explicitly add one metadata.
    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully updated.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc3')),
        '/cloud/update/', group=ut_id(gvar, 'ctg1'), form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'ram_ctl': 5,
            'cores_ctl': 5,
            'vm_flavor': '',
            'vm_image': '',
            'vm_keep_alive': 10,
            'vm_keyname': '',
            'vm_network': '',
            'spot_price': 1,
            'metadata_name': ut_id(gvar, 'cty1'),
            'metadata_option': 'add'
            },
        server_user=ut_id(gvar, 'ctu1')
    )

    # 49 Ensure that 48 updated correctly. Known to fail if one's cloud_credentials (in ~/cloudscheduler/unit_tests/credentials.yaml) are invalid.
    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/list/', group=ut_id(gvar, 'ctg1'), expected_list='cloud_list', list_filter={'group_name': ut_id(gvar, 'ctg1'), 'cloud_name': ut_id(gvar, 'ctc3')},
        values={
            'ram_ctl': 5,
            'cores_ctl': 5,
            'vm_keep_alive': 10,
            'vm_flavor': '',
            'vm_image': '',
            'vm_keyname': '',
            'vm_network': '',
            'spot_price': 1,
            'group_exclusions': ut_id(gvar, 'cty1')
            },
        server_user=ut_id(gvar, 'ctu1')
    )

    # 50 Implicitly add one metadata.
    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully updated.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc3')),
        '/cloud/update/', group=ut_id(gvar, 'ctg1'), form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'metadata_name': ut_id(gvar, 'cty2')
            },
        server_user=ut_id(gvar, 'ctu1')
    )

    # 51 Ensure that 50 added metadata.
    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/list/', group=ut_id(gvar, 'ctg1'), expected_list='cloud_list', list_filter={'group_name': ut_id(gvar, 'ctg1'), 'cloud_name': ut_id(gvar, 'ctc3')},
        values={'group_exclusions': ut_id(gvar, 'cty1,cty2')},
        server_user=ut_id(gvar, 'ctu1')
    )

    # 52 Delete one metadata.
    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully updated.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc3')),
        '/cloud/update/', group=ut_id(gvar, 'ctg1'), form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'metadata_name': ut_id(gvar, 'cty2'),
            'metadata_option': 'delete'
            },
        server_user=ut_id(gvar, 'ctu1')
    )

    # 53 Ensure that 52 deleted metadata.
    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/list/', group=ut_id(gvar, 'ctg1'), expected_list='cloud_list', list_filter={'group_name': ut_id(gvar, 'ctg1'), 'cloud_name': ut_id(gvar, 'ctc3')},
        values={'group_exclusions': ut_id(gvar, 'cty1')},
        server_user=ut_id(gvar, 'ctu1')
    )
    
    # 54 Explicitly add a metadata.
    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully updated.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc3')),
        '/cloud/update/', group=ut_id(gvar, 'ctg1'), form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'metadata_name': ut_id(gvar, 'cty1'),
            'metadata_option': 'add'
            },
        server_user=ut_id(gvar, 'ctu1')
    )

    # 55 Ensure that 54 added metadata.
    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/list/', group=ut_id(gvar, 'ctg1'), expected_list='cloud_list', list_filter={'cloud_name': ut_id(gvar, 'ctc3')},
        values={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'group_name': ut_id(gvar, 'ctg1'),
            'group_exclusions': ut_id(gvar, 'cty1')
            },
        server_user=ut_id(gvar, 'ctu1')
    )

    # 56 Implicitly add metadata.
    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully updated.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc3')),
        '/cloud/update/', group=ut_id(gvar, 'ctg1'), form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'metadata_name': ut_id(gvar, 'cty2'),
            },
        server_user=ut_id(gvar, 'ctu1')
    )

    # 57 Ensure that 58 added metadata.
    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/list/', group=ut_id(gvar, 'ctg1'), expected_list='cloud_list', list_filter={'group_name': ut_id(gvar, 'ctg1'), 'cloud_name': ut_id(gvar, 'ctc3')},
        values={'group_exclusions': ut_id(gvar, 'cty1,cty2')},
        server_user=ut_id(gvar, 'ctu1')
    )

if __name__ == "__main__":
    main(None)
