from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id
from sys import argv

# lno: CV - error code identifier.

def main(gvar, user_secret):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv2_request(gvar, argv[0])
    
    # 01
    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 401, unauthorized.',
        '/cloud/update/',
        server_user='invalid-unit-test', server_pw=user_secret
    )

    # 02
    execute_csv2_request(
        gvar, 1, None, 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'ctu1')),
        '/cloud/update/',
        server_user=ut_id(gvar, 'ctu1'), server_pw=user_secret
    )

    # 03
    execute_csv2_request(
        gvar, 1, None, 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'ctu2')),
        '/cloud/update/',
        server_user=ut_id(gvar, 'ctu2'), server_pw=user_secret
    )

    # 04
    execute_csv2_request(
        gvar, 1, 'CV', 'invalid method "GET" specified.',
        '/cloud/update/',
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 05
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud update request did not contain mandatory parameter "cloud_name".',
        '/cloud/update/'
, form_data={'cloud_type': 'local'},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 06
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud update request contained a bad parameter "invalid-unit-test".',
        '/cloud/update/'
, form_data={'cloud_name': 'invalid-unit-test', 'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 07
    execute_csv2_request(
        gvar, 1, 'CV', 'cannot switch to invalid group "invalid-unit-test".',
        '/cloud/update/', group='invalid-unit-test', form_data={'cloud_name': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 08
    execute_csv2_request(
        gvar, 1, 'CV', 'cannot switch to invalid group "{}".'.format(ut_id(gvar, 'ctg2')),
        '/cloud/update/', group=ut_id(gvar, 'ctg2'), form_data={'cloud_name': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 09
    execute_csv2_request(
        gvar, 1, 'CV', 'value specified for "cloud_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        '/cloud/update/', group=ut_id(gvar, 'ctg1'), form_data={'cloud_name': 'Invalid-Unit-Test'},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 10
    execute_csv2_request(
        gvar, 1, 'CV', 'value specified for "cloud_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        '/cloud/update/', group=ut_id(gvar, 'ctg1'), form_data={'cloud_name': 'invalid-unit-test-'},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 11
    execute_csv2_request(
        gvar, 1, 'CV', 'value specified for "cloud_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        '/cloud/update/', group=ut_id(gvar, 'ctg1'), form_data={'cloud_name': 'invalid-unit-test!'},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 12
    execute_csv2_request(
        gvar, 1, 'CV', 'value specified for "cloud_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        '/cloud/update/', group=ut_id(gvar, 'ctg1'), form_data={'cloud_name': 'invalid-unit-test!'},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 13
    execute_csv2_request(
        gvar, 1, 'CV', 'value specified for "cloud_type" must be one of the following options: [\'amazon\', \'azure\', \'google\', \'local\', \'opennebula\', \'openstack\'].',
        '/cloud/update/', group=ut_id(gvar, 'ctg1'), form_data={'cloud_name': ut_id(gvar, 'ctc3'), 'cloud_type': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 14
    execute_csv2_request(
        gvar, 1, 'CV', 'boolean value specified for "enabled" must be one of the following: true, false, yes, no, 1, or 0.',
        '/cloud/update/', group=ut_id(gvar, 'ctg1'), form_data={'cloud_name': ut_id(gvar, 'ctc3'), 'enabled': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 15
    execute_csv2_request(
        gvar, 1, 'CV', 'value specified for "vm_keep_alive" must be an integer value.',
        '/cloud/update/', group=ut_id(gvar, 'ctg1'), form_data={'cloud_name': ut_id(gvar, 'ctc3'), 'vm_keep_alive': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 16
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud update value specified for "spot_price" must be a floating point value.',
        '/cloud/update/', group=ut_id(gvar, 'ctg1'), form_data={'cloud_name': ut_id(gvar, 'ctc3'), 'spot_price': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 17
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud update, "{}" failed - specified metadata_name "invalid-unit-test" does not exist.'.format(ut_id(gvar, 'ctc3')),
        '/cloud/update/', group=ut_id(gvar, 'ctg1'), form_data={'cloud_name': ut_id(gvar, 'ctc3'), 'metadata_name': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 18
    execute_csv2_request(
        gvar, 1, 'CV', 'value specified for "metadata_option" must be one of the following options: [\'add\', \'delete\'].',
        '/cloud/update/', group=ut_id(gvar, 'ctg1'), form_data={'cloud_name': ut_id(gvar, 'ctc3'), 'metadata_option': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 19
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud update must specify at least one field to update',
        '/cloud/update/', group=ut_id(gvar, 'ctg1'), form_data={'cloud_name': ut_id(gvar, 'ctc3'), 'metadata_option': 'add'},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 20
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud update must specify at least one field to update',
        '/cloud/update/', group=ut_id(gvar, 'ctg1'), form_data={'cloud_name': ut_id(gvar, 'ctc3'), 'metadata_option': 'delete'},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 21
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud update, "{}" failed - specified metadata_name "invalid-unit-test" does not exist.'.format(ut_id(gvar, 'ctc3')),
        '/cloud/update/', group=ut_id(gvar, 'ctg1'), form_data={'cloud_name': ut_id(gvar, 'ctc3'), 'metadata_name': 'invalid-unit-test', 'metadata_option': 'add'},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 22
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud update, "{}" failed - specified metadata_name "invalid-unit-test" does not exist.'.format(ut_id(gvar, 'ctc3')),
        '/cloud/update/', group=ut_id(gvar, 'ctg1'), form_data={'cloud_name': ut_id(gvar, 'ctc3'), 'metadata_name': 'invalid-unit-test', 'metadata_option': 'delete'},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 23
    execute_csv2_request(
        gvar, 1, 'CV', 'parameter "authurl" contains an empty string which is specifically disallowed.',
        '/cloud/update/', group=ut_id(gvar, 'ctg1'), form_data={'cloud_name': ut_id(gvar, 'ctc3'), 'authurl': ''},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 24
    execute_csv2_request(
        gvar, 1, 'CV', 'parameter "project" contains an empty string which is specifically disallowed.',
        '/cloud/update/', group=ut_id(gvar, 'ctg1'), form_data={'cloud_name': ut_id(gvar, 'ctc3'), 'project': ''},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 25
    execute_csv2_request(
        gvar, 1, 'CV', 'parameter "username" contains an empty string which is specifically disallowed.',
        '/cloud/update/', group=ut_id(gvar, 'ctg1'), form_data={'cloud_name': ut_id(gvar, 'ctc3'), 'username': ''},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 26
    execute_csv2_request(
        gvar, 1, 'CV', 'parameter "password" contains an empty string which is specifically disallowed.',
        '/cloud/update/', group=ut_id(gvar, 'ctg1'), form_data={'cloud_name': ut_id(gvar, 'ctc3'), 'password': ''},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 27
    execute_csv2_request(
        gvar, 1, 'CV', 'parameter "region" contains an empty string which is specifically disallowed.',
        '/cloud/update/', group=ut_id(gvar, 'ctg1'), form_data={'cloud_name': ut_id(gvar, 'ctc3'), 'region': ''},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 28
    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/list/', group=ut_id(gvar, 'ctg1'), list='cloud_list', filter={'cloud_name': ut_id(gvar, 'ctc3')},
        values={
            'group_name': ut_id(gvar, 'ctg1'),
            'cloud_name': ut_id(gvar, 'ctc3'),
            'enabled': 1,
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
            'keyname': None,
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
            'metadata_names': '%s,%s,%s' % (ut_id(gvar, 'cty2'), ut_id(gvar, 'cty3'), ut_id(gvar, 'cty3.yaml')),
            },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 29
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
            'metadata_name': ut_id(gvar, 'cty1')
            },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 30
    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/list/', group=ut_id(gvar, 'ctg1'), list='cloud_list', filter={'cloud_name': ut_id(gvar, 'ctc3')},
        values={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'group_name': ut_id(gvar, 'ctg1'),
            'authurl': 'updated-value',
            'project': 'updated-value',
            'username': 'updated-value',
            'cacertificate': 'updated-value',
            'region': 'updated-value',
            'user_domain_name': 'updated-value',
            'project_domain_name': 'updated-value',
            'cloud_type': 'local',
            'enabled': 0,
            'vm_keep_alive': 10,
            'vm_flavor': '',
            'vm_image': '',
            'vm_keyname': '',
            'vm_network': '',
            'spot_price': 1,
            'group_exclusions': ut_id(gvar, 'cty1')
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 31
    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully updated.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc3')),
        '/cloud/update/', group=ut_id(gvar, 'ctg1'), form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'metadata_name': ut_id(gvar, 'cty1'),
            'metadata_option': 'delete'
            },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 32
    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/list/', group=ut_id(gvar, 'ctg1'), list='cloud_list', filter={'cloud_name': ut_id(gvar, 'ctc3')},
        values={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'group_name': ut_id(gvar, 'ctg1'),
            'group_exclusions': None
            },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )
    
    # 33
    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully updated.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc3')),
        '/cloud/update/', group=ut_id(gvar, 'ctg1'), form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'metadata_name.1': ut_id(gvar, 'cty1'),
            'metadata_name.2': ut_id(gvar, 'cty2'),
            'metadata_name.3': ut_id(gvar, 'cty3')
            },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 34
    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/list/', group=ut_id(gvar, 'ctg1'), list='cloud_list', filter={'cloud_name': ut_id(gvar, 'ctc3')},
        values={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'group_name': ut_id(gvar, 'ctg1'),
            'group_exclusions': ut_id(gvar, 'cty1,cty2,cty3')
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 35
    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully updated.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc3')),
        '/cloud/update/', group=ut_id(gvar, 'ctg1'), form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'metadata_name.1': ut_id(gvar, 'cty1'),
            'metadata_name.2': ut_id(gvar, 'cty2'),
            'metadata_name.3': ut_id(gvar, 'cty3'),
            'metadata_option': 'delete'
            },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 36
    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/list/', group=ut_id(gvar, 'ctg1'), list='cloud_list', filter={'cloud_name': ut_id(gvar, 'ctc3')},
        values={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'group_name': ut_id(gvar, 'ctg1'),
            'group_exclusions': None
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 37
    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully updated.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc3')),
        '/cloud/update/', group=ut_id(gvar, 'ctg1'), form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'metadata_name': ut_id(gvar, 'cty3'),
            'metadata_option': 'add'
            },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 38
    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/list/', group=ut_id(gvar, 'ctg1'), list='cloud_list', filter={'cloud_name': ut_id(gvar, 'ctc3')},
        values={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'group_name': ut_id(gvar, 'ctg1'),
            'group_exclusions': ut_id(gvar, 'cty3')
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 39
    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully updated.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc3')),
        '/cloud/update/', group=ut_id(gvar, 'ctg1'), form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'metadata_name.1': ut_id(gvar, 'cty2'),
            'metadata_name.2': ut_id(gvar, 'cty1'),
            'metadata_option': 'add'
            },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 40
    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/list/', group=ut_id(gvar, 'ctg1'), list='cloud_list', filter={'cloud_name': ut_id(gvar, 'ctc3')},
        values={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'group_name': ut_id(gvar, 'ctg1'),
            'group_exclusions': ut_id(gvar, 'cty1,cty2,cty3')
            },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 41
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud update, "{0}" failed - specified item does not exist: vm_image=invalid-unit-test, group_name={1}, cloud_name={0}.'.format(ut_id(gvar, 'ctc3'), ut_id(gvar, 'ctg1')),
        '/cloud/update/', group=ut_id(gvar, 'ctg1'), form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'vm_image': 'invalid-unit-test',
            },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 42
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud update, "{0}" failed - specified item does not exist: vm_flavor=invalid-unit-test, group_name={1}, cloud_name={0}.'.format(ut_id(gvar, 'ctc3'), ut_id(gvar, 'ctg1')),
        '/cloud/update/', group=ut_id(gvar, 'ctg1'), form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'vm_flavor': 'invalid-unit-test',
            },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 43
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud update, "{0}" failed - specified item does not exist: vm_network=invalid-unit-test, group_name={1}, cloud_name={0}.'.format(ut_id(gvar, 'ctc3'), ut_id(gvar, 'ctg1')),
        '/cloud/update/', group=ut_id(gvar, 'ctg1'), form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'vm_network': 'invalid-unit-test',
            },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 45
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud update, "{0}" failed - specified item does not exist: vm_keyname=invalid-unit-test, group_name={1}, cloud_name={0}.'.format(ut_id(gvar, 'ctc3'), ut_id(gvar, 'ctg1')),
        '/cloud/update/', group=ut_id(gvar, 'ctg1'), form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'vm_keyname': 'invalid-unit-test',
            },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

if __name__ == "__main__":
    main(None)
