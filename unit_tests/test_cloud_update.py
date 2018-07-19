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
        '/cloud/update/',
        server_user='invalid-unit-test', server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, None, 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'ctu1')),
        '/cloud/update/',
        server_user=ut_id(gvar, 'ctu1'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, None, 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'ctu2')),
        '/cloud/update/',
        server_user=ut_id(gvar, 'ctu2'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV37', 'invalid method "GET" specified.',
        '/cloud/update/',
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV35', 'cloud update request did not contain mandatory parameter "cloud_name".',
        '/cloud/update/', form_data={'cloud_type': 'local'},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV35', 'cloud update request contained a bad parameter "invalid-unit-test".',
        '/cloud/update/', form_data={'cloud_name': 'invalid-unit-test', 'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV34', 'cannot switch to invalid group "invalid-unit-test".',
        '/cloud/update/', form_data={'cloud_name': 'invalid-unit-test', 'group': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV34', 'cannot switch to invalid group "{}".'.format(ut_id(gvar, 'ctg2')),
        '/cloud/update/', form_data={'cloud_name': 'invalid-unit-test', 'group': ut_id(gvar, 'ctg2')},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV35', 'value specified for "cloud_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        '/cloud/update/', form_data={'cloud_name': 'Invalid-Unit-Test', 'group': ut_id(gvar, 'ctg1')},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV35', 'value specified for "cloud_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        '/cloud/update/', form_data={'cloud_name': 'invalid-unit-test-', 'group': ut_id(gvar, 'ctg1')},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV35', 'value specified for "cloud_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        '/cloud/update/', form_data={'cloud_name': 'invalid-unit-test!', 'group': ut_id(gvar, 'ctg1')},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV35', 'value specified for "cloud_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        '/cloud/update/', form_data={'cloud_name': 'invalid-unit-test!', 'group': ut_id(gvar, 'ctg1')},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV35', 'value specified for "cloud_type" must be one of the following options: [\'amazon\', \'azure\', \'google\', \'local\', \'opennebula\', \'openstack\'].',
        '/cloud/update/', form_data={'cloud_name': ut_id(gvar, 'ctc3'), 'group': ut_id(gvar, 'ctg1'), 'cloud_type': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV35', 'boolean value specified for "enabled" must be one of the following: true, false, yes, no, 1, or 0.',
        '/cloud/update/', form_data={'cloud_name': ut_id(gvar, 'ctc3'), 'group': ut_id(gvar, 'ctg1'), 'enabled': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV35', 'value specified for "vm_keep_alive" must be a integer value.',
        '/cloud/update/', form_data={'cloud_name': ut_id(gvar, 'ctc3'), 'group': ut_id(gvar, 'ctg1'), 'vm_keep_alive': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV35', 'value specified for "spot_price" must be a integer value.',
        '/cloud/update/', form_data={'cloud_name': ut_id(gvar, 'ctc3'), 'group': ut_id(gvar, 'ctg1'), 'spot_price': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV03', 'cloud update, "{}" failed - specified metadata_name "invalid-unit-test" does not exist.'.format(ut_id(gvar, 'ctc3')),
        '/cloud/update/', form_data={'cloud_name': ut_id(gvar, 'ctc3'), 'group': ut_id(gvar, 'ctg1'), 'metadata_name': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV35', 'value specified for "metadata_option" must be one of the following options: [\'add\', \'delete\'].',
        '/cloud/update/', form_data={'cloud_name': ut_id(gvar, 'ctc3'), 'group': ut_id(gvar, 'ctg1'), 'metadata_option': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV23', 'cloud update must specify at least one field to update',
        '/cloud/update/', form_data={'cloud_name': ut_id(gvar, 'ctc3'), 'group': ut_id(gvar, 'ctg1'), 'metadata_option': 'add'},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV23', 'cloud update must specify at least one field to update',
        '/cloud/update/', form_data={'cloud_name': ut_id(gvar, 'ctc3'), 'group': ut_id(gvar, 'ctg1'), 'metadata_option': 'delete'},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV03', 'cloud update, "{}" failed - specified metadata_name "invalid-unit-test" does not exist.'.format(ut_id(gvar, 'ctc3')),
        '/cloud/update/', form_data={'cloud_name': ut_id(gvar, 'ctc3'), 'group': ut_id(gvar, 'ctg1'), 'metadata_name': 'invalid-unit-test', 'metadata_option': 'add'},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV03', 'cloud update, "{}" failed - specified metadata_name "invalid-unit-test" does not exist.'.format(ut_id(gvar, 'ctc3')),
        '/cloud/update/', form_data={'cloud_name': ut_id(gvar, 'ctc3'), 'group': ut_id(gvar, 'ctg1'), 'metadata_name': 'invalid-unit-test', 'metadata_option': 'delete'},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/list/', form_data={'group': ut_id(gvar, 'ctg1')},
        list='cloud_list', filter={'cloud_name': ut_id(gvar, 'ctc3')},
        values={
            'user_domain_name': 'Default',
            'project': 'unit-test-cloud-three',
            'vm_image': None,
            'username': ut_id(gvar, 'ctu3'),
            'cores_ctl': -1,
            'vm_flavor': 'NULL',
            'vm_keep_alive': None,
            'group_exclusions': None,
            'cloud_type': 'local',
            'spot_price': None,
            'authurl': 'unit-test-cloud-three.ca',
            'keyname': None,
            'cloud_name': ut_id(gvar, 'ctc3'),
            'project_domain_name': 'Default',
            'cacertificate': None,
            'ram_ctl': -1,
            'group_name': ut_id(gvar, 'ctg1'),
            'enabled': 1,
            'region': ut_id(gvar, 'ctc3-r')
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
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
            'cloud_type': 'local',
            'ram_ctl': 5,
            'cores_ctl': 5,
            'enabled': 0,
            'vm_keep_alive': 10,
            'vm_flavor': 'updated-value',
            'vm_image': 'updated-value',
            'spot_price': 1,
            'metadata_name': ut_id(gvar, 'cty1')
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
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
            'cloud_type': 'local',
            'enabled': 0,
            'vm_keep_alive': 10,
            'vm_flavor': 'updated-value',
            'vm_image': 'updated-value',
            'spot_price': 1,
            'group_exclusions': ut_id(gvar, 'cty1')
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully updated.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc3')),
        '/cloud/update/', form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'group': ut_id(gvar, 'ctg1'),
            'metadata_name': ut_id(gvar, 'cty1'),
            'metadata_option': 'delete'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/list/', form_data={'group': ut_id(gvar, 'ctg1')},
        list='cloud_list', filter={'cloud_name': ut_id(gvar, 'ctc3')},
        values={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'group_name': ut_id(gvar, 'ctg1'),
            'group_exclusions': None
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )
    
    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully updated.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc3')),
        '/cloud/update/', form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'group': ut_id(gvar, 'ctg1'),
            'metadata_name.1': ut_id(gvar, 'cty1'),
            'metadata_name.2': ut_id(gvar, 'cty2'),
            'metadata_name.3': ut_id(gvar, 'cty3')
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/list/', form_data={'group': ut_id(gvar, 'ctg1')},
        list='cloud_list', filter={'cloud_name': ut_id(gvar, 'ctc3')},
        values={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'group_name': ut_id(gvar, 'ctg1'),
            'group_exclusions': ut_id(gvar, 'cty1,cty2,cty3')
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully updated.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc3')),
        '/cloud/update/', form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'group': ut_id(gvar, 'ctg1'),
            'metadata_name.1': ut_id(gvar, 'cty1'),
            'metadata_name.2': ut_id(gvar, 'cty2'),
            'metadata_name.3': ut_id(gvar, 'cty3'),
            'metadata_option': 'delete'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/list/', form_data={'group': ut_id(gvar, 'ctg1')},
        list='cloud_list', filter={'cloud_name': ut_id(gvar, 'ctc3')},
        values={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'group_name': ut_id(gvar, 'ctg1'),
            'group_exclusions': None
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully updated.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc3')),
        '/cloud/update/', form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'group': ut_id(gvar, 'ctg1'),
            'metadata_name': ut_id(gvar, 'cty3'),
            'metadata_option': 'add'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/list/', form_data={'group': ut_id(gvar, 'ctg1')},
        list='cloud_list', filter={'cloud_name': ut_id(gvar, 'ctc3')},
        values={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'group_name': ut_id(gvar, 'ctg1'),
            'group_exclusions': ut_id(gvar, 'cty3')
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully updated.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc3')),
        '/cloud/update/', form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'group': ut_id(gvar, 'ctg1'),
            'metadata_name.1': ut_id(gvar, 'cty2'),
            'metadata_name.2': ut_id(gvar, 'cty1'),
            'metadata_option': 'add'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/list/', form_data={'group': ut_id(gvar, 'ctg1')},
        list='cloud_list', filter={'cloud_name': ut_id(gvar, 'ctc3')},
        values={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'group_name': ut_id(gvar, 'ctg1'),
            'group_exclusions': ut_id(gvar, 'cty1,cty2,cty3')
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

if __name__ == "__main__":
    main(None)