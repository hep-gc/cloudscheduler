from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id
import sys

# lno: CV - error code identifier.

def main(gvar, user_secret):
    if not gvar:
        gvar = {}
        if len(sys.argv) > 1:
            initialize_csv2_request(gvar, sys.argv[0], selections=sys.argv[1])
        else:
            initialize_csv2_request(gvar, sys.argv[0])
    
    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 401, unauthorized.',
        '/cloud/add/',
        server_user='invalid-unit-test', server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, None, 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'ctu1')),
        '/cloud/add/',
        server_user=ut_id(gvar, 'ctu1'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, None, 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'ctu2')),
        '/cloud/add/',
        server_user=ut_id(gvar, 'ctu2'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV03', 'invalid method "GET" specified.',
        '/cloud/add/',
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV04', 'no cloud name specified.',
        '/cloud/add/', form_data={'group': ut_id(gvar, 'ctg1')},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV04', 'no cloud name specified.',
        '/cloud/add/', form_data={'cloud_name': ut_id(gvar, 'cloud-invalid-unit-test'), 'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV00', 'cannot switch to invalid group "invalid-unit-test".',
        '/cloud/add/', form_data={'cloud_name': ut_id(gvar, 'cloud-invalid-unit-test'), 'group': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV00', 'cannot switch to invalid group "{}".'.format(ut_id(gvar, 'ctg2')),
        '/cloud/add/', form_data={'cloud_name': ut_id(gvar, 'cloud-invalid-unit-test'), 'group': ut_id(gvar, 'ctg2')},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV01', 'value specified for "cloud_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        '/cloud/add/', form_data={'cloud_name': 'Invalid-Unit-Test', 'group': ut_id(gvar, 'ctg1')},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV01', 'value specified for "cloud_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        '/cloud/add/', form_data={'cloud_name': 'invalid-unit-test-', 'group': ut_id(gvar, 'ctg1')},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV01', 'value specified for "cloud_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        '/cloud/add/', form_data={'cloud_name': 'invalid-unit-test!', 'group': ut_id(gvar, 'ctg1')},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV02', '"{}::{}" failed - (1364, "Field \'authurl\' doesn\'t have a default value").'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'cloud-invalid-unit-test')),
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': ut_id(gvar, 'cloud-invalid-unit-test')
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV02', '"{}::{}" failed - (1364, "Field \'project\' doesn\'t have a default value").'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'cloud-invalid-unit-test')),
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': ut_id(gvar, 'cloud-invalid-unit-test'),
            'authurl': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV02', '"{}::{}" failed - (1364, "Field \'username\' doesn\'t have a default value").'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'cloud-invalid-unit-test')),
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': ut_id(gvar, 'cloud-invalid-unit-test'),
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV02', '"{}::{}" failed - (1364, "Field \'password\' doesn\'t have a default value").'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'cloud-invalid-unit-test')),
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': ut_id(gvar, 'cloud-invalid-unit-test'),
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'username': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV02', '"{}::{}" failed - (1364, "Field \'region\' doesn\'t have a default value").'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'cloud-invalid-unit-test')),
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': ut_id(gvar, 'cloud-invalid-unit-test'),
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV02', '"{}::{}" failed - (1364, "Field \'cloud_type\' doesn\'t have a default value").'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'cloud-invalid-unit-test')),
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': ut_id(gvar, 'cloud-invalid-unit-test'),
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test',
            'region': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV01', 'value specified for "cloud_type" must be one of the following options: [\'amazon\', \'azure\', \'google\', \'local\', \'opennebula\', \'openstack\'].',
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': ut_id(gvar, 'cloud-invalid-unit-test'),
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test',
            'region': 'invalid-unit-test',
            'cloud_type': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV01', 'bad parameter "server_meta_ctl"',
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': ut_id(gvar, 'cloud-invalid-unit-test'),
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test',
            'region': 'invalid-unit-test',
            'cloud_type': 'local',
            'server_meta_ctl': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV01', 'bad parameter "instances_ctl"',
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': ut_id(gvar, 'cloud-invalid-unit-test'),
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test',
            'region': 'invalid-unit-test',
            'cloud_type': 'local',
            'instances_ctl': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV01', 'bad parameter "personality_ctl"',
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': ut_id(gvar, 'cloud-invalid-unit-test'),
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test',
            'region': 'invalid-unit-test',
            'cloud_type': 'local',
            'personality_ctl': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV01', 'bad parameter "image_meta_ctl"',
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': ut_id(gvar, 'cloud-invalid-unit-test'),
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test',
            'region': 'invalid-unit-test',
            'cloud_type': 'local',
            'image_meta_ctl': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV01', 'bad parameter "personality_size_ctl"',
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': ut_id(gvar, 'cloud-invalid-unit-test'),
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test',
            'region': 'invalid-unit-test',
            'cloud_type': 'local',
            'personality_size_ctl': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV01', 'value specified for "ram_ctl" must be a integer value.',
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': ut_id(gvar, 'cloud-invalid-unit-test'),
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test',
            'region': 'invalid-unit-test',
            'cloud_type': 'local',
            'ram_ctl': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV01', 'bad parameter "server_groups_ctl"',
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': ut_id(gvar, 'cloud-invalid-unit-test'),
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test',
            'region': 'invalid-unit-test',
            'cloud_type': 'local',
            'server_groups_ctl': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV01', 'bad parameter "security_group_rules_ctl"',
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': ut_id(gvar, 'cloud-invalid-unit-test'),
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test',
            'region': 'invalid-unit-test',
            'cloud_type': 'local',
            'security_group_rules_ctl': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV01', 'bad parameter "keypairs_ctl"',
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': ut_id(gvar, 'cloud-invalid-unit-test'),
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test',
            'region': 'invalid-unit-test',
            'cloud_type': 'local',
            'keypairs_ctl': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV01', 'bad parameter "security_groups_ctl"',
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': ut_id(gvar, 'cloud-invalid-unit-test'),
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test',
            'region': 'invalid-unit-test',
            'cloud_type': 'local',
            'security_groups_ctl': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV01', 'bad parameter "server_group_members_ctl"',
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': ut_id(gvar, 'cloud-invalid-unit-test'),
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test',
            'region': 'invalid-unit-test',
            'cloud_type': 'local',
            'server_group_members_ctl': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV01', 'bad parameter "floating_ips_ctl"',
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': ut_id(gvar, 'cloud-invalid-unit-test'),
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test',
            'region': 'invalid-unit-test',
            'cloud_type': 'local',
            'floating_ips_ctl': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV01', 'value specified for "cores_ctl" must be a integer value.',
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': ut_id(gvar, 'cloud-invalid-unit-test'),
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test',
            'region': 'invalid-unit-test',
            'cloud_type': 'local',
            'cores_ctl': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV01', 'value specified for "vm_keep_alive" must be a integer value.',
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': ut_id(gvar, 'cloud-invalid-unit-test'),
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test',
            'region': 'invalid-unit-test',
            'cloud_type': 'local',
            'vm_keep_alive': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV01', 'boolean value specified for "enabled" must be one of the following: true, false, yes, no, 1, or 0.',
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': ut_id(gvar, 'cloud-invalid-unit-test'),
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test',
            'region': 'invalid-unit-test',
            'cloud_type': 'local',
            'enabled': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV02', 'Data too long for column \'cloud_name\' at row 1',
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': 'cloudnametoolongtobeinsertedintodb',
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test',
            'region': 'invalid-unit-test',
            'cloud_type': 'local'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV01', 'value specified for "spot_price" must be a integer value.',
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': ut_id(gvar, 'cloud-invalid-unit-test'),
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test',
            'region': 'invalid-unit-test',
            'cloud_type': 'local',
            'spot_price': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV03', 'cloud add, "{}" failed - specified metadata_name "invalid-unit-test" does not exist.'.format(ut_id(gvar, 'cloud-invalid-unit-test'), ut_id(gvar, 'ctg1')),
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': ut_id(gvar, 'cloud-invalid-unit-test'),
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test',
            'region': 'invalid-unit-test',
            'cloud_type': 'local',
            'metadata_name': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV03', 'cloud add, "{}" failed - specified metadata_name "invalid-unit-test" does not exist.'.format(ut_id(gvar, 'cloud-invalid-unit-test'), ut_id(gvar, 'ctg1')),
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': ut_id(gvar, 'cloud-invalid-unit-test'),
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test',
            'region': 'invalid-unit-test',
            'cloud_type': 'local',
            'metadata_name.1': ut_id(gvar, 'cty1'),
            'metadata_name.2': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV03', 'cloud add, "{}" failed - metadata name "{}" was specified twice.'.format(ut_id(gvar, 'cloud-invalid-unit-test'), ut_id(gvar, 'cty1')),
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
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
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully added.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc5')),
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': ut_id(gvar, 'ctc5'),
            'authurl': 'unit-test-cloud-five.ca',
            'project': 'unit-test-cloud-five',
            'username': ut_id(gvar, 'ctu3'),
            'password': user_secret,
            'region': ut_id(gvar, 'ctc5-r'),
            'cloud_type': 'local',
            'vm_flavor': 'unit-test-cloud-five',
            'vm_image': 'unit-test-cloud-five',
            'enabled': 0,
            'vm_keep_alive': 10,
            'metadata_name': ut_id(gvar, 'cty1'),
            'spot_price': 10
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/list/',
        list='cloud_list', filter={'cloud_name': ut_id(gvar, 'ctc5')},
        values={
            'group_name': ut_id(gvar, 'ctg1'),
            'cloud_name': ut_id(gvar, 'ctc5'),
            'authurl': 'unit-test-cloud-five.ca',
            'project': 'unit-test-cloud-five',
            'username': ut_id(gvar, 'ctu3'),
            'region': ut_id(gvar, 'ctc5-r'),
            'cloud_type': 'local',
            'vm_flavor': 'unit-test-cloud-five',
            'vm_image': 'unit-test-cloud-five',
            'enabled': 0,
            'vm_keep_alive': 10,
            'group_exclusions': ut_id(gvar, 'cty1'),
            'spot_price': 10
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully added.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc6')),
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': ut_id(gvar, 'ctc6'),
            'authurl': 'unit-test-cloud-five.ca',
            'project': 'unit-test-cloud-five',
            'username': ut_id(gvar, 'ctu3'),
            'password': user_secret,
            'region': ut_id(gvar, 'ctc5-r'),
            'cloud_type': 'local',
            'metadata_name.1': ut_id(gvar, 'cty1'),
            'metadata_name.2': ut_id(gvar, 'cty2'),
            'metadata_name.3': ut_id(gvar, 'cty3')
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/list/',
        list='cloud_list', filter={'cloud_name': ut_id(gvar, 'ctc6')},
        values={
            'group_name': ut_id(gvar, 'ctg1'),
            'cloud_name': ut_id(gvar, 'ctc6'),
            'group_exclusions': ut_id(gvar, 'cty1,cty2,cty3')
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV02', 'Duplicate entry \'{}-{}\' for key \'PRIMARY\''.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc5')),
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': ut_id(gvar, 'ctc5'),
            'authurl': 'unit-test-cloud-five.ca',
            'project': 'unit-test-cloud-five',
            'username': ut_id(gvar, 'ctu3'),
            'password': user_secret,
            'region': ut_id(gvar, 'ctc5-r'),
            'cloud_type': 'local'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

if __name__ == "__main__":
    main(None)