from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id
import sys

def main(gvar):
    if not gvar:
        gvar = {}
        if len(sys.argv) > 1:
            initialize_csv2_request(gvar, sys.argv[0], selections=sys.argv[1])
        else:
            initialize_csv2_request(gvar, sys.argv[0])
    
    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 401, unauthorized.',
        '/cloud/add/',
        server_user='invalid-unit-test', server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, None, 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'ctu1')),
        '/cloud/add/',
        server_user=ut_id(gvar, 'ctu1'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, None, 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'ctu2')),
        '/cloud/add/',
        server_user=ut_id(gvar, 'ctu2'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV03', 'invalid method "GET" specified.',
        '/cloud/add/',
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV04', 'no cloud name specified.',
        '/cloud/add/', form_data={'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV00', 'cannot switch to invalid group "invalid-unit-test".',
        '/cloud/add/', form_data={'cloud_name': 'invalid-unit-test', 'group': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV00', 'cannot switch to invalid group "{}".'.format(ut_id(gvar, 'ctg2')),
        '/cloud/add/', form_data={'cloud_name': 'invalid-unit-test', 'group': ut_id(gvar, 'ctg2')},
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV01', 'value specified for "cloud_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        '/cloud/add/', form_data={'cloud_name': 'Invalid-Unit-Test', 'group': ut_id(gvar, 'ctg1')},
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV01', 'value specified for "cloud_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        '/cloud/add/', form_data={'cloud_name': 'invalid-unit-test-', 'group': ut_id(gvar, 'ctg1')},
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV01', 'value specified for "cloud_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        '/cloud/add/', form_data={'cloud_name': 'invalid-unit-test!', 'group': ut_id(gvar, 'ctg1')},
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV02', '"{}::invalid-unit-test" failed - (1364, "Field \'authurl\' doesn\'t have a default value").'.format(ut_id(gvar, 'ctg1')),
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV02', '"{}::invalid-unit-test" failed - (1364, "Field \'project\' doesn\'t have a default value").'.format(ut_id(gvar, 'ctg1')),
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': 'invalid-unit-test',
            'authurl': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV02', '"{}::invalid-unit-test" failed - (1364, "Field \'username\' doesn\'t have a default value").'.format(ut_id(gvar, 'ctg1')),
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': 'invalid-unit-test',
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV02', '"{}::invalid-unit-test" failed - (1364, "Field \'password\' doesn\'t have a default value").'.format(ut_id(gvar, 'ctg1')),
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': 'invalid-unit-test',
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'username': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV02', '"{}::invalid-unit-test" failed - (1364, "Field \'region\' doesn\'t have a default value").'.format(ut_id(gvar, 'ctg1')),
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': 'invalid-unit-test',
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV02', '"{}::invalid-unit-test" failed - (1364, "Field \'cloud_type\' doesn\'t have a default value").'.format(ut_id(gvar, 'ctg1')),
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': 'invalid-unit-test',
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test',
            'region': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV01', 'value specified for "cloud_type" must be one of the following options: [\'amazon\', \'azure\', \'google\', \'local\', \'opennebula\', \'openstack\'].',
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': 'invalid-unit-test',
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test',
            'region': 'invalid-unit-test',
            'cloud_type': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV02', 'Incorrect integer value: \'invalid-unit-test\' for column \'server_meta_ctl\' at row 1',
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': 'invalid-unit-test',
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test',
            'region': 'invalid-unit-test',
            'cloud_type': 'local',
            'server_meta_ctl': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV02', 'Incorrect integer value: \'invalid-unit-test\' for column \'instances_ctl\' at row 1',
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': 'invalid-unit-test',
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test',
            'region': 'invalid-unit-test',
            'cloud_type': 'local',
            'instances_ctl': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV02', 'Incorrect integer value: \'invalid-unit-test\' for column \'personality_ctl\' at row 1',
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': 'invalid-unit-test',
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test',
            'region': 'invalid-unit-test',
            'cloud_type': 'local',
            'personality_ctl': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV02', 'Incorrect integer value: \'invalid-unit-test\' for column \'image_meta_ctl\' at row 1',
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': 'invalid-unit-test',
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test',
            'region': 'invalid-unit-test',
            'cloud_type': 'local',
            'image_meta_ctl': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV02', 'Incorrect integer value: \'invalid-unit-test\' for column \'personality_size_ctl\' at row 1',
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': 'invalid-unit-test',
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test',
            'region': 'invalid-unit-test',
            'cloud_type': 'local',
            'personality_size_ctl': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV02', 'Incorrect integer value: \'invalid-unit-test\' for column \'ram_ctl\' at row 1',
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': 'invalid-unit-test',
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test',
            'region': 'invalid-unit-test',
            'cloud_type': 'local',
            'ram_ctl': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV02', 'Incorrect integer value: \'invalid-unit-test\' for column \'server_groups_ctl\' at row 1',
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': 'invalid-unit-test',
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test',
            'region': 'invalid-unit-test',
            'cloud_type': 'local',
            'server_groups_ctl': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV02', 'Incorrect integer value: \'invalid-unit-test\' for column \'security_group_rules_ctl\' at row 1',
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': 'invalid-unit-test',
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test',
            'region': 'invalid-unit-test',
            'cloud_type': 'local',
            'security_group_rules_ctl': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV02', 'Incorrect integer value: \'invalid-unit-test\' for column \'keypairs_ctl\' at row 1',
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': 'invalid-unit-test',
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test',
            'region': 'invalid-unit-test',
            'cloud_type': 'local',
            'keypairs_ctl': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV02', 'Incorrect integer value: \'invalid-unit-test\' for column \'security_groups_ctl\' at row 1',
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': 'invalid-unit-test',
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test',
            'region': 'invalid-unit-test',
            'cloud_type': 'local',
            'security_groups_ctl': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV02', 'Incorrect integer value: \'invalid-unit-test\' for column \'server_group_members_ctl\' at row 1',
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': 'invalid-unit-test',
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test',
            'region': 'invalid-unit-test',
            'cloud_type': 'local',
            'server_group_members_ctl': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV02', 'Incorrect integer value: \'invalid-unit-test\' for column \'floating_ips_ctl\' at row 1',
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': 'invalid-unit-test',
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test',
            'region': 'invalid-unit-test',
            'cloud_type': 'local',
            'floating_ips_ctl': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV02', 'Incorrect integer value: \'invalid-unit-test\' for column \'cores_ctl\' at row 1',
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': 'invalid-unit-test',
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test',
            'region': 'invalid-unit-test',
            'cloud_type': 'local',
            'cores_ctl': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
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
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully added.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc5')),
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': ut_id(gvar, 'ctc5'),
            'authurl': 'unit-test-cloud-five.ca',
            'project': 'unit-test-cloud-five',
            'username': ut_id(gvar, 'ctu3'),
            'password': 'Abc123',
            'region': ut_id(gvar, 'ctc5-r'),
            'cloud_type': 'local'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV02', 'Duplicate entry \'{}-{}\' for key \'PRIMARY\''.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc5')),
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': ut_id(gvar, 'ctc5'),
            'authurl': 'unit-test-cloud-five.ca',
            'project': 'unit-test-cloud-five',
            'username': ut_id(gvar, 'ctu3'),
            'password': 'Abc123',
            'region': ut_id(gvar, 'ctc5-r'),
            'cloud_type': 'local'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

if __name__ == "__main__":
    main(None)