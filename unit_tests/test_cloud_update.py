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

    # 01 - 05
    sanity_requests(gvar, '/cloud/update/', ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctu3'), ut_id(gvar, 'ctg2'), ut_id(gvar, 'ctu1'))

    # 06
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud update request did not contain mandatory parameter "cloud_name".',
        '/cloud/update/', group=ut_id(gvar, 'ctg1'),
        server_user=ut_id(gvar, 'ctu3')
    )

    PARAMETERS = [
        # 07 Give an invalid parameter.
        # 08 Omit cloud_name.
        ('cloud_name', {
            # 09
            '': 'cloud update value specified for "cloud_name" must not be the empty string.',
            # 10
            'Invalid-unit-test': 'cloud update value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 11
            'invalid-unit-test-': 'cloud update value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 12
            'invalid-unit-test!': 'cloud update value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
        }, 'invalid-unit-test'),
        # 13
        ('authurl', {'': 'parameter "authurl" contains an empty string which is specifically disallowed.'}),
        # 14
        ('username', {'': 'parameter "username" contains an empty string which is specifically disallowed.'}),
        # 15
        ('password', {'': 'parameter "password" contains an empty string which is specifically disallowed.'}),
        # 16
        ('project', {'': 'parameter "project" contains an empty string which is specifically disallowed.'}),
        # 17
        ('region', {'': 'parameter "region" contains an empty string which is specifically disallowed.'}),
        # 18
        ('cloud_type', {'invalid-unit-test': 'value specified for "cloud_type" must be one of the following options: [\'amazon\', \'azure\', \'google\', \'local\', \'opennebula\', \'openstack\'].'}),
        # 19
        ('enabled', {'invalid-unit-test': 'boolean value specified for "enabled" must be one of the following: true, false, yes, no, 1, or 0.'}),
        # 20
        ('vm_keep_alive', {'invalid-unit-test': 'value specified for "vm_keep_alive" must be an integer value.'}),
        # 21
        ('spot_price', {'invalid-unit-test': 'cloud update value specified for "spot_price" must be a floating point value.'}),
        ('metadata_option', {
            # 22
            'invalid-unit-test': 'value specified for "metadata_option" must be one of the following options: [\'add\', \'delete\'].'
        }),
        # 23
        ('vm_image', {'invalid-unit-test': 'cloud update, "{}" failed - specified item does not exist: vm_image=invalid-unit-test, group_name={}, cloud_name=invalid-unit-test.'.format(ut_id(gvar, 'ctc3'), ut_id(gvar, 'ctg1'))}),
        # 24
        ('vm_flavor', {'invalid-unit-test': 'cloud update, "{}" failed - specified item does not exist: vm_flavor=invalid-unit-test, group_name={}, cloud_name=invalid-unit-test.'.format(ut_id(gvar, 'ctc3'), ut_id(gvar, 'ctg1'))}),
        # 25
        ('vm_network', {'invalid-unit-test': 'cloud update, "{}" failed - specified item does not exist: vm_network=invalid-unit-test, group_name={}, cloud_name=invalid-unit-test.'.format(ut_id(gvar, 'ctc3'), ut_id(gvar, 'ctg1'))}),
        # 26
        ('vm_keyname', {'invalid-unit-test': 'cloud update, "{}" failed - specified item does not exist: vm_keyname=invalid-unit-test, group_name={}, cloud_name=invalid-unit-test.'.format(ut_id(gvar, 'ctc3'), ut_id(gvar, 'ctg1'))})
    ]

    parameters_requests(gvar, '/cloud/update/', ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctu3'), PARAMETERS)

    # 27 Ensure that metadata_option by itself does not qualify as a field to update.
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud update must specify at least one field to update',
        '/cloud/update/', group=ut_id(gvar, 'ctg1'), form_data={'cloud_name': ut_id(gvar, 'ctc3'), 'metadata_option': 'add'},
        server_user=ut_id(gvar, 'ctu3')
    )

    # 28 Attempt to implicitly add metadata that does not exist.
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud update, "{}" failed - specified metadata_name "invalid-unit-test" does not exist.'.format(ut_id(gvar, 'ctc3')),
        '/cloud/update/', group=ut_id(gvar, 'ctg1'), form_data={'cloud_name': ut_id(gvar, 'ctc3'), 'metadata_name': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu3')
    )

    # 29 Attempt to delete non-existent metadata.
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud update, "{}" failed - specified metadata_name "invalid-unit-test" does not exist.'.format(ut_id(gvar, 'ctc3')),
        '/cloud/update/', group=ut_id(gvar, 'ctg1'), form_data={'cloud_name': ut_id(gvar, 'ctc3'), 'metadata_name': 'invalid-unit-test', 'metadata_option': 'delete'},
        server_user=ut_id(gvar, 'ctu3')
    )

    # 30 Ensures that values are as expected before executing requests that are expected to succeed. Known to fail if run twice without setup / cleanup in between.
    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/list/', group=ut_id(gvar, 'ctg1'), expected_list='cloud_list', list_filter={'group_name': ut_id(gvar, 'ctg1'), 'cloud_name': ut_id(gvar, 'ctc3')},
        values={
            'cloud_priority': 0,
            'spot_price': -1.0,
            'vm_flavor': '',
            'vm_image': '',
            'vm_keep_alive': 0,
            'vm_keyname': None,
            'vm_network': '',
            'vm_security_groups': None,
            'cascading_vm_flavor': None,
            'cascading_vm_image': None,
            'cascading_vm_keep_alive': 0,
            'cascading_vm_keyname': None,
            'cascading_vm_network': None,
            'cascading_vm_security_groups': None,
            'authurl': 'unit-test-cloud-three.ca',
            'project_domain_name': "'Default'",
            'project_domain_id': '',
            'project': 'unit-test-cloud-three',
            'user_domain_name': 'Default',
            'user_domain_id': '',
            'username': ut_id(gvar, 'ctu3'),
            'cacertificate': None,
            'region': ut_id(gvar, 'ctc3-r'),
            'cloud_type': 'local',
            'cores_ctl': -1,
            'cores_softmax': -1,
            'cores_max': 0,
            'cores_used': 0,
            'cores_foreign': '0',
            'cores_native': '0',
            'ram_ctl': -1,
            'ram_max': 0,
            'ram_used': 0,
            'ram_foreign': '0',
            'ram_native': '0',
            'instances_max': 0,
            'instances_used': 0,
            'floating_ips_max': 0,
            'floating_ips_used': 0,
            'security_groups_max': 0,
            'security_groups_used': 0,
            'server_groups_max': 0,
            'server_groups_used': 0,
            'image_meta_max': 0,
            'keypairs_max': 0,
            'personality_max': 0,
            'personality_size_max': 0,
            'security_group_rules_max': 0,
            'server_group_members_max': 0,
            'server_meta_max': 0,
            'cores_idle': '0',
            'ram_idle': '0',
            'flavor_exclusions': None,
            'flavor_names': None,
            'group_exclusions': None,
            },
        server_user=ut_id(gvar, 'ctu3')
    )

    # 31 Update several values and explicitly add one metadata.
    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully updated.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc3')),
        '/cloud/update/', group=ut_id(gvar, 'ctg1'), form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'authurl': 'updated-value',
            'project': 'updated-value',
            'username': 'updated-value',
            'password': 'updated-value',
            'cacertificate': 'updated-value',
            'region': 'updated-value',
            'user_domain_name': 'updated-value',
            'project_domain_name': 'updated-value',
            'cloud_type': 'local',
            'ram_ctl': 5,
            'cores_ctl': 5,
            'enabled': 0,
            'vm_flavor': '',
            'vm_image': '',
            'vm_keep_alive': 10,
            'vm_keyname': '',
            'vm_network': '',
            'spot_price': 1,
            'metadata_name': ut_id(gvar, 'cty1'),
            'metadata_option': 'add'
            },
        server_user=ut_id(gvar, 'ctu3')
    )

    # 32 Ensure that 31 updated correctly.
    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/list/', group=ut_id(gvar, 'ctg1'), expected_list='cloud_list', list_filter={'group_name': ut_id(gvar, 'ctg1'), 'cloud_name': ut_id(gvar, 'ctc3')},
        values={
            'authurl': 'updated-value',
            'project': 'updated-value',
            'username': 'updated-value',
            'cacertificate': 'updated-value',
            'region': 'updated-value',
            'user_domain_name': 'updated-value',
            'project_domain_name': 'updated-value',
            'cloud_type': 'local',
            'ram_ctl': 5,
            'cores_ctl': 5,
            'enabled': 0,
            'vm_keep_alive': 10,
            'vm_flavor': '',
            'vm_image': '',
            'vm_keyname': '',
            'vm_network': '',
            'spot_price': 1,
            'group_exclusions': ut_id(gvar, 'cty1')
            },
        server_user=ut_id(gvar, 'ctu3')
    )

    # 33 Implicitly add one metadata.
    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully updated.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc3')),
        '/cloud/update/', group=ut_id(gvar, 'ctg1'), form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'metadata_name': ut_id(gvar, 'cty2')
            },
        server_user=ut_id(gvar, 'ctu3')
    )

    # 34 Ensure that 33 added metadata.
    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/list/', group=ut_id(gvar, 'ctg1'), expected_list='cloud_list', list_filter={'group_name': ut_id(gvar, 'ctg1'), 'cloud_name': ut_id(gvar, 'ctc3')},
        values={'group_exclusions': ut_id(gvar, 'cty1,cty2')},
        server_user=ut_id(gvar, 'ctu3')
    )

    # 35 Delete one metadata.
    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully updated.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc3')),
        '/cloud/update/', group=ut_id(gvar, 'ctg1'), form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'metadata_name': ut_id(gvar, 'cty2'),
            'metadata_option': 'delete'
            },
        server_user=ut_id(gvar, 'ctu3')
    )

    # 36 Ensure that 35 deleted metadata.
    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/list/', group=ut_id(gvar, 'ctg1'), expected_list='cloud_list', list_filter={'group_name': ut_id(gvar, 'ctg1'), 'cloud_name': ut_id(gvar, 'ctc3')},
        values={'group_exclusions': ut_id(gvar, 'cty1')},
        server_user=ut_id(gvar, 'ctu3')
    )
    
    # 37 Explicitly add two metadata, one of which the cloud already has.
    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully updated.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc3')),
        '/cloud/update/', group=ut_id(gvar, 'ctg1'), form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            # Given in reverse alphabetic order so we can check that the server sorts them as expected.
            'metadata_name.1': ut_id(gvar, 'cty2'),
            'metadata_name.2': ut_id(gvar, 'cty1'),
            'metadata_option': 'add'
            },
        server_user=ut_id(gvar, 'ctu3')
    )

    # 38 Ensure that 37 added metadata.
    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/list/', group=ut_id(gvar, 'ctg1'), expected_list='cloud_list', list_filter={'cloud_name': ut_id(gvar, 'ctc3')},
        values={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'group_name': ut_id(gvar, 'ctg1'),
            'group_exclusions': ut_id(gvar, 'cty1,cty2')
            },
        server_user=ut_id(gvar, 'ctu3')
    )

    # 39 Delete two metadata.
    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully updated.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc3')),
        '/cloud/update/', group=ut_id(gvar, 'ctg1'), form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'metadata_name.1': ut_id(gvar, 'cty1'),
            'metadata_name.2': ut_id(gvar, 'cty2'),
            'metadata_option': 'delete'
            },
        server_user=ut_id(gvar, 'ctu3')
    )

    # 40 Ensure that 39 deleted metadata.
    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/list/', group=ut_id(gvar, 'ctg1'), expected_list='cloud_list', list_filter={'group_name': ut_id(gvar, 'ctg1'), 'cloud_name': ut_id(gvar, 'ctc3')},
        values={'group_exclusions': None},
        server_user=ut_id(gvar, 'ctu3')
    )

    # 41 Implicitly add two metadata.
    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully updated.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc3')),
        '/cloud/update/', group=ut_id(gvar, 'ctg1'), form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'metadata_name.1': ut_id(gvar, 'cty1'),
            'metadata_name.2': ut_id(gvar, 'cty2'),
            },
        server_user=ut_id(gvar, 'ctu3')
    )

    # 42 Ensure that 41 added metadata.
    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/list/', group=ut_id(gvar, 'ctg1'), expected_list='cloud_list', list_filter={'group_name': ut_id(gvar, 'ctg1'), 'cloud_name': ut_id(gvar, 'ctc3')},
        values={'group_exclusions': ut_id(gvar, 'cty1,cty2')},
        server_user=ut_id(gvar, 'ctu3')
    )

if __name__ == "__main__":
    main(None)
