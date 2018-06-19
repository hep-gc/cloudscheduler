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
        '/cloud/update/',
        server_user='invalid-unit-test', server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, None, 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'ctu1')),
        '/cloud/update/',
        server_user=ut_id(gvar, 'ctu1'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, None, 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'ctu2')),
        '/cloud/update/',
        server_user=ut_id(gvar, 'ctu2'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV15', 'invalid method "GET" specified.',
        '/cloud/update/',
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV16', 'no cloud name specified.',
        '/cloud/update/', form_data={'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV12', 'cannot switch to invalid group "invalid-unit-test".',
        '/cloud/update/', form_data={'cloud_name': 'invalid-unit-test', 'group': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV12', 'cannot switch to invalid group "{}".'.format(ut_id(gvar, 'ctg2')),
        '/cloud/update/', form_data={'cloud_name': 'invalid-unit-test', 'group': ut_id(gvar, 'ctg2')},
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV13', 'value specified for "cloud_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        '/cloud/update/', form_data={'cloud_name': 'Invalid-Unit-Test', 'group': ut_id(gvar, 'ctg1')},
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV13', 'value specified for "cloud_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        '/cloud/update/', form_data={'cloud_name': 'invalid-unit-test-', 'group': ut_id(gvar, 'ctg1')},
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV13', 'value specified for "cloud_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        '/cloud/update/', form_data={'cloud_name': 'invalid-unit-test!', 'group': ut_id(gvar, 'ctg1')},
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV13', 'cloud update request contained a bad parameter "invalid-unit-test".',
        '/cloud/update/', form_data={'cloud_name': 'invalid-unit-test', 'group': ut_id(gvar, 'ctg1'), 'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/list/', form_data={'group': ut_id(gvar, 'ctg1')},
        list='cloud_list', filter={'cloud_name': ut_id(gvar, 'ctc3')},
        values={'server_meta_max': 0, 'server_group_members_max': 0, 'cores_native': 0, 'floating_ips_max': 0, 'authurl': 'unit-test-cloud-three.ca', 'project_domain_name': 'Default', 'cloud_type': 'unit-test-cloud-three-type', 'image_meta_max': 0, 'cacertificate': None, 'ram_ctl': -1, 'region': 'jodiew-ctc3-r', 'keyname': None, 'ram_native': 0, 'username': 'jodiew-ctu3', 'metadata_names': None, 'instances_max': 0, 'personality_size_max': 0, 'cores_max': 0, 'keypairs_max': 0, 'cores_foreign': 0, 'ram_foreign': 0, 'server_groups_max': 0, 'user_domain_name': 'Default', 'project': 'unit-test-cloud-three', 'ram_used': 0, 'cores_used': 0, 'server_groups_used': 0, 'security_groups_max': 0, 'cloud_name': 'jodiew-ctc3', 'personality_max': 0, 'instances_used': 0, 'ram_max': 0, 'group_name': 'jodiew-ctg1', 'security_group_rules_max': 0, 'cores_ctl': -1, 'floating_ips_used': 0, 'security_groups_used': 0},
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully updated.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc3')),
        '/cloud/update/', form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'group': ut_id(gvar, 'ctg1'),
            'authurl': 'updated-value',
            'project': 'updated-value',
            'username': 'updated-value',
            'password': 'updated-value',
            'keyname': 'updated-value',
            'cacertificate': 'updated-value',
            'region': 'updated-value',
            'user_domain_name': 'updated-value',
            'project_domain_name': 'updated-value',
            'cloud_type': 'updated-value',
            'server_meta_ctl': 5,
            'instances_ctl': 5,
            'personality_ctl': 5,
            'image_meta_ctl': 5,
            'personality_size_ctl': 5,
            'ram_ctl': 5,
            'server_groups_ctl': 5,
            'security_group_rules_ctl': 5,
            'keypairs_ctl': 5,
            'security_groups_ctl': 5,
            'server_group_members_ctl': 5,
            'floating_ips_ctl': 5,
            'cores_ctl': 5
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/list/', form_data={'group': ut_id(gvar, 'ctg1')},
        list='cloud_list', filter={'cloud_name': ut_id(gvar, 'ctc3')},
        values={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'group_name': ut_id(gvar, 'ctg1'),
            'authurl': 'updated-value',
            'project': 'updated-value',
            'username': 'updated-value',
            'keyname': 'updated-value',
            'cacertificate': 'updated-value',
            'region': 'updated-value',
            'user_domain_name': 'updated-value',
            'project_domain_name': 'updated-value',
            'cloud_type': 'updated-value'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

if __name__ == "__main__":
    main(None)