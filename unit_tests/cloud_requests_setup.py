from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id
import sys
import cloud_requests_cleanup

def main(gvar):
    if not gvar:
        gvar = {}
        if len(sys.argv) > 1:
            initialize_csv2_request(gvar, sys.argv[0], selections=sys.argv[1])
        else:
            initialize_csv2_request(gvar, sys.argv[0])
    
    cloud_requests_cleanup.main(gvar)

    # unprivileged user in no groups
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'ctu1')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'ctu1'),
            'password1': 'Abc123',
            'password2': 'Abc123',
            'cert_cn': '{} test user one'.format(ut_id(gvar, 'cloud'))
        }
    )
    
    # privileged user in no groups
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'ctu2')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'ctu2'),
            'password1': 'Abc123',
            'password2': 'Abc123',
            'cert_cn': '{} test user two'.format(ut_id(gvar, 'cloud')),
            'is_superuser': 1
        }
    )

    # group with users
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'ctg1')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'ctg1'),
            'condor_central_manager': 'unit-test-group-one.ca'
        }
    )

    # group without users
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'ctg2')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'ctg2'),
            'condor_central_manager': 'unit-test-group-two.ca'
        }
    )

    # unprivileged user in ctg1
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'ctu3')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'ctu3'),
            'password1': 'Abc123',
            'password2': 'Abc123',
            'cert_cn': '{} test user three'.format(ut_id(gvar, 'cloud')),
            'group_name.1': ut_id(gvar, 'ctg1')
        }
    )
    
    # privileged user in ctg1
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'ctu4')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'ctu4'),
            'password1': 'Abc123',
            'password2': 'Abc123',
            'cert_cn': '{} test user four'.format(ut_id(gvar, 'cloud')),
            'is_superuser': 1,
            'group_name.1': ut_id(gvar, 'ctg1')
        }
    )

    # cloud to be deleted in test_cloud_delete
    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully added.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc1')),
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': ut_id(gvar, 'ctc1'),
            'authurl': 'unit-test-cloud-one.ca',
            'project': 'unit-test-cloud-one',
            'username': ut_id(gvar, 'ctu3'),
            'password': 'Abc123',
            'region': ut_id(gvar, 'ctc1-r'),
            'cloud_type': 'unit-test-cloud-one-type'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    # cloud to be listed in test_cloud_list
    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully added.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc2')),
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': ut_id(gvar, 'ctc2'),
            'authurl': 'unit-test-cloud-two.ca',
            'project': 'unit-test-cloud-two',
            'username': ut_id(gvar, 'ctu3'),
            'password': 'Abc123',
            'region': ut_id(gvar, 'ctc2-r'),
            'cloud_type': 'unit-test-cloud-two-type'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    # cloud to be listed in test_cloud_update
    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully added.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc3')),
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'ctg1'),
            'cloud_name': ut_id(gvar, 'ctc3'),
            'authurl': 'unit-test-cloud-three.ca',
            'project': 'unit-test-cloud-three',
            'username': ut_id(gvar, 'ctu3'),
            'password': 'Abc123',
            'region': ut_id(gvar, 'ctc3-r'),
            'cloud_type': 'unit-test-cloud-three-type'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

if __name__ == "__main__":
    main(None)