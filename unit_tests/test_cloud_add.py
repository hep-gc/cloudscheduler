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
    
    # 1
    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 401, unauthorized.',
        '/cloud/add/?"{}"'.format(ut_id(gvar, 'ctg1')),
        server_user='invalid-unit-test', server_pw=user_secret
    )

    # 2
    execute_csv2_request(
        gvar, 1, None, 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'ctu1')),
        '/cloud/add/?"{}"'.format(ut_id(gvar, 'ctg1')),
        server_user=ut_id(gvar, 'ctu1'), server_pw=user_secret
    )

    # 3
    execute_csv2_request(
        gvar, 1, None, 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'ctu2')),
        '/cloud/add/?"{}"'.format(ut_id(gvar, 'ctg1')),
        server_user=ut_id(gvar, 'ctu2'), server_pw=user_secret
    )

    # 4
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud add request did not contain mandatory parameter "cloud_name".',
        '/cloud/add/?{}'.format(ut_id(gvar, 'ctg1')),
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 5
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud add request did not contain mandatory parameter "cloud_name".',
        '/cloud/add/', group=ut_id(gvar, 'ctg1'),
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 6
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud add request contained a bad parameter "invalid-unit-test".',
        '/cloud/add/', group=ut_id(gvar, 'ctg1'),
        form_data={'cloud_name': ut_id(gvar, 'cloud-invalid-unit-test'), 'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 7
    execute_csv2_request(
        gvar, 1, 'CV', 'cannot switch to invalid group "invalid-unit-test".',
        '/cloud/add/', group='invalid-unit-test', form_data={'cloud_name': ut_id(gvar, 'cloud-invalid-unit-test')},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 8
    execute_csv2_request(
        gvar, 1, 'CV', 'cannot switch to invalid group "{}".'.format(ut_id(gvar, 'ctg2')),
        '/cloud/add/', group=ut_id(gvar, 'ctg2'), form_data={'cloud_name': ut_id(gvar, 'cloud-invalid-unit-test')},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 9
    execute_csv2_request(
        gvar, 1, 'CV', 'value specified for "cloud_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={'cloud_name': 'Invalid-Unit-Test'},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 10
    execute_csv2_request(
        gvar, 1, 'CV', 'value specified for "cloud_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={'cloud_name': 'invalid-unit-test-'},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 11
    execute_csv2_request(
        gvar, 1, 'CV', 'value specified for "cloud_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={'cloud_name': 'invalid-unit-test!'},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 12
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud add request did not contain mandatory (but not empty) parameter "authurl".',
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={'cloud_name': ut_id(gvar, 'cloud-invalid-unit-test')},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 13
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud add request did not contain mandatory (but not empty) parameter "project".',
            '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={
            'cloud_name': ut_id(gvar, 'cloud-invalid-unit-test'),
            'authurl': 'invalid-unit-test'
            },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 14
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud add request did not contain mandatory (but not empty) parameter "username".',
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={
            'cloud_name': ut_id(gvar, 'cloud-invalid-unit-test'),
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test'
            },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 15
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud add request did not contain mandatory (but not empty) parameter "password".',
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={
            'cloud_name': ut_id(gvar, 'cloud-invalid-unit-test'),
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'username': 'invalid-unit-test'
            },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 16
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud add request did not contain mandatory (but not empty) parameter "region".',
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={
            'cloud_name': ut_id(gvar, 'cloud-invalid-unit-test'),
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test'
            },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 17
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud add request did not contain mandatory (but not empty) parameter "cloud_type".',
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={
            'cloud_name': ut_id(gvar, 'cloud-invalid-unit-test'),
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test',
            'region': 'invalid-unit-test'
            },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 18
    execute_csv2_request(
        gvar, 1, 'CV', 'value specified for "cloud_type" must be one of the following options: [\'amazon\', \'azure\', \'google\', \'local\', \'opennebula\', \'openstack\'].',
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={
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

    # 19
    execute_csv2_request(
        gvar, 1, 'CV', 'value specified for "cloud_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={
            'cloud_name': '',
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test',
            'region': 'invalid-unit-test',
            'cloud_type': 'local',
            },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 20
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud add mandatory parameter "authurl" contains an empty string which is specifically disallowed.',
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={
            'cloud_name': ut_id(gvar, 'cloud-invalid-unit-test'),
            'authurl': '',
            'project': 'invalid-unit-test',
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test',
            'region': 'invalid-unit-test',
            'cloud_type': 'local',
            },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 21
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud add mandatory parameter "project" contains an empty string which is specifically disallowed.',
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={
            'cloud_name': ut_id(gvar, 'cloud-invalid-unit-test'),
            'authurl': 'invalid-unit-test',
            'project': '',
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test',
            'region': 'invalid-unit-test',
            'cloud_type': 'local',
            },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 22
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud add mandatory parameter "username" contains an empty string which is specifically disallowed.',
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={
            'cloud_name': ut_id(gvar, 'cloud-invalid-unit-test'),
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'username': '',
            'password': 'invalid-unit-test',
            'region': 'invalid-unit-test',
            'cloud_type': 'local',
            },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 23
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud add mandatory parameter "password" contains an empty string which is specifically disallowed.',
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={
            'cloud_name': ut_id(gvar, 'cloud-invalid-unit-test'),
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'username': 'invalid-unit-test',
            'password': '',
            'region': 'invalid-unit-test',
            'cloud_type': 'local',
            },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 24
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud add mandatory parameter "region" contains an empty string which is specifically disallowed.',
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={
            'cloud_name': ut_id(gvar, 'cloud-invalid-unit-test'),
            'authurl': 'invalid-unit-test',
            'project': 'invalid-unit-test',
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test',
            'region': '',
            'cloud_type': 'local',
            },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 25
    execute_csv2_request(
        gvar, 1, 'CV', 'bad parameter "server_meta_ctl"',
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={
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

    # 26
    execute_csv2_request(
        gvar, 1, 'CV', 'bad parameter "instances_ctl"',
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={
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

    # 27
    execute_csv2_request(
        gvar, 1, 'CV', 'bad parameter "personality_ctl"',
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={
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

    # 28
    execute_csv2_request(
        gvar, 1, 'CV', 'bad parameter "image_meta_ctl"',
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={
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

    # 29
    execute_csv2_request(
        gvar, 1, 'CV', 'bad parameter "personality_size_ctl"',
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={
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

    # 30
    execute_csv2_request(
        gvar, 1, 'CV', 'value specified for "ram_ctl" must be an integer value.',
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={
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

    # 31
    execute_csv2_request(
        gvar, 1, 'CV', 'bad parameter "server_groups_ctl"',
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={
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

    # 32
    execute_csv2_request(
        gvar, 1, 'CV', 'bad parameter "security_group_rules_ctl"',
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={
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

    # 33
    execute_csv2_request(
        gvar, 1, 'CV', 'bad parameter "keypairs_ctl"',
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={
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

    # 34
    execute_csv2_request(
        gvar, 1, 'CV', 'bad parameter "security_groups_ctl"',
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={
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

    # 35
    execute_csv2_request(
        gvar, 1, 'CV', 'bad parameter "server_group_members_ctl"',
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={
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

    # 36
    execute_csv2_request(
        gvar, 1, 'CV', 'bad parameter "floating_ips_ctl"',
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={
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

    # 37
    execute_csv2_request(
        gvar, 1, 'CV', 'value specified for "cores_ctl" must be an integer value.',
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={
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

    # 38
    execute_csv2_request(
        gvar, 1, 'CV', 'value specified for "vm_keep_alive" must be an integer value.',
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={
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

    # 39
    execute_csv2_request(
        gvar, 1, 'CV', 'boolean value specified for "enabled" must be one of the following: true, false, yes, no, 1, or 0.',
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={
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

    # 40
    execute_csv2_request(
        gvar, 1, 'CV', 'Data too long for column \'cloud_name\' at row 1',
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={
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

    # 41
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud add value specified for "spot_price" must be a floating point value.',
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={
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

    # 42
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud add, "{}" failed - specified metadata_name "invalid-unit-test" does not exist.'.format(ut_id(gvar, 'cloud-invalid-unit-test')),
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={
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

    # 43
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud add, "{}" failed - specified metadata_name "invalid-unit-test" does not exist.'.format(ut_id(gvar, 'cloud-invalid-unit-test')),
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={
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

    # 44
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
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 45
    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully added.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc5')),
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={
            'cloud_name': ut_id(gvar, 'ctc5'),
            'authurl': 'unit-test-cloud-five.ca',
            'project': 'unit-test-cloud-five',
            'username': ut_id(gvar, 'ctu3'),
            'password': user_secret,
            'region': ut_id(gvar, 'ctc5-r'),
            'cloud_type': 'local',
            'vm_flavor': '',
            'vm_image': '',
            'vm_keyname': '',
            'vm_network': '',
            'enabled': 0,
            'vm_keep_alive': 10,
            'metadata_name': ut_id(gvar, 'cty1'),
            'spot_price': 10
            },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 46
    # Ensure that 45 actually created a cloud.
    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/list/', group=ut_id(gvar, 'ctg1'),
        list='cloud_list', filter={'cloud_name': ut_id(gvar, 'ctc5')},
        values={
            'group_name': ut_id(gvar, 'ctg1'),
            'cloud_name': ut_id(gvar, 'ctc5'),
            'authurl': 'unit-test-cloud-five.ca',
            'project': 'unit-test-cloud-five',
            'username': ut_id(gvar, 'ctu3'),
            'region': ut_id(gvar, 'ctc5-r'),
            'cloud_type': 'local',
            'vm_flavor': '',
            'vm_image': '',
            'vm_keyname': '',
            'vm_network': '',
            'enabled': 0,
            'vm_keep_alive': 10,
            'group_exclusions': ut_id(gvar, 'cty1'),
            'spot_price': 10
            },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 47
    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully added.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc6')),
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={
            'cloud_name': ut_id(gvar, 'ctc6'),
            'authurl': 'unit-test-cloud-six.ca',
            'project': 'unit-test-cloud-six',
            'username': ut_id(gvar, 'ctu3'),
            'password': user_secret,
            'region': ut_id(gvar, 'ctc6-r'),
            'cloud_type': 'local',
            'vm_flavor': '',
            'vm_image': '',
            'vm_keyname': '',
            'vm_network': '',
            'metadata_name.1': ut_id(gvar, 'cty1'),
            'metadata_name.2': ut_id(gvar, 'cty2'),
            'metadata_name.3': ut_id(gvar, 'cty3')
            },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 48
    # Ensure that 47 actually created a cloud.
    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/list/', group=ut_id(gvar, 'ctg1'),
        list='cloud_list', filter={'cloud_name': ut_id(gvar, 'ctc6')},
        values={
            'group_name': ut_id(gvar, 'ctg1'),
            'cloud_name': ut_id(gvar, 'ctc6'),
            'group_exclusions': ut_id(gvar, 'cty1,cty2,cty3')
            },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 49
    execute_csv2_request(
        gvar, 1, 'CV', 'Duplicate entry \'{}-{}\' for key \'PRIMARY\''.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc5')),
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={
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

    # 50
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud add, "{0}" failed - specified item does not exist: vm_image=invalid-unit-test, group_name={1}, cloud_name={0}.'.format(ut_id(gvar, 'invalid-unit-test'), ut_id(gvar, 'ctg1')),
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={
            'cloud_name': ut_id(gvar, 'invalid-unit-test'),
            'authurl': 'unit-test-cloud-seven.ca',
            'project': 'unit-test-cloud-seven',
            'username': ut_id(gvar, 'ctu3'),
            'password': user_secret,
            'region': ut_id(gvar, 'ctc7-r'),
            'cloud_type': 'local',
            'vm_image': 'invalid-unit-test',
            },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 51
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud add, "{0}" failed - specified item does not exist: vm_flavor=invalid-unit-test, group_name={1}, cloud_name={0}.'.format(ut_id(gvar, 'invalid-unit-test'), ut_id(gvar, 'ctg1')),
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={
            'cloud_name': ut_id(gvar, 'invalid-unit-test'),
            'authurl': 'unit-test-cloud-seven.ca',
            'project': 'unit-test-cloud-seven',
            'username': ut_id(gvar, 'ctu3'),
            'password': user_secret,
            'region': ut_id(gvar, 'ctc7-r'),
            'cloud_type': 'local',
            'vm_flavor': 'invalid-unit-test',
            },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 52
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud add, "{0}" failed - specified item does not exist: vm_network=invalid-unit-test, group_name={1}, cloud_name={0}.'.format(ut_id(gvar, 'invalid-unit-test'), ut_id(gvar, 'ctg1')),
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={
            'cloud_name': ut_id(gvar, 'invalid-unit-test'),
            'authurl': 'unit-test-cloud-seven.ca',
            'project': 'unit-test-cloud-seven',
            'username': ut_id(gvar, 'ctu3'),
            'password': user_secret,
            'region': ut_id(gvar, 'ctc7-r'),
            'cloud_type': 'local',
            'vm_network': 'invalid-unit-test',
            },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 53
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud add, "{0}" failed - specified item does not exist: vm_keyname=invalid-unit-test, group_name={1}, cloud_name={0}.'.format(ut_id(gvar, 'invalid-unit-test'), ut_id(gvar, 'ctg1')),
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={
            'cloud_name': ut_id(gvar, 'invalid-unit-test'),
            'authurl': 'unit-test-cloud-seven.ca',
            'project': 'unit-test-cloud-seven',
            'username': ut_id(gvar, 'ctu3'),
            'password': user_secret,
            'region': ut_id(gvar, 'ctc7-r'),
            'cloud_type': 'local',
            'vm_keyname': 'invalid-unit-test',
            },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

if __name__ == "__main__":
    main(None)
