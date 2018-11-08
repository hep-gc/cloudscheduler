from unit_test_common import execute_csv2_command, execute_csv2_request, initialize_csv2_request, ut_id, generate_secret
from sys import argv
import cli_requests_cleanup

def main(gvar, user_secret):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv2_request(gvar, argv[0])
    if not user_secret:
        user_secret = generate_secret()
    
    cli_requests_cleanup.main(gvar)

    # unprivileged user in no groups
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'clu1')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'clu1'),
            'password1': user_secret,
            'password2': user_secret,
            'cert_cn': ut_id(gvar, 'command line user one')
        }
    )
    
    # privileged user in no groups
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'clu2')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'clu2'),
            'password1': user_secret,
            'password2': user_secret,
            'cert_cn': ut_id(gvar, 'command line user two'),
            'is_superuser': 1
        }
    )

    # user for unprivleged tests
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/add/', form_data={
            'username': ut_id(gvar, 'test'),
            'password1': user_secret,
            'password2': user_secret,
            'cert_cn': ut_id(gvar, 'test'),
            'is_superuser': 0,
        }
    )

    # group with users
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'clg1')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'clg1'),
            'condor_central_manager': 'unit-test-group-one.ca',
            'username.1': ut_id(gvar, '')[:-1],
            'username.2': ut_id(gvar, 'test'),
        }
    )

    # group without users
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'clg2')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'clg2'),
            'condor_central_manager': 'unit-test-group-two.ca'
        }
    )

    # group to be deleted without users
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'clg3')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'clg3'),
            'condor_central_manager': 'unit-test-group-three.ca'
        }
    )

    # group to be deleted with users
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'clg4')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'clg4'),
            'condor_central_manager': 'unit-test-group-four.ca'
        }
    )

    # unprivileged user in clg1
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'clu3')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'clu3'),
            'password1': user_secret,
            'password2': user_secret,
            'cert_cn': ut_id(gvar, 'command line user three'),
            'group_name.1': ut_id(gvar, 'clg1')
        }
    )
    
    # privileged user in clg1
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'clu4')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'clu4'),
            'password1': user_secret,
            'password2': user_secret,
            'cert_cn': ut_id(gvar, 'command line user four'),
            'is_superuser': 1,
            'group_name.1': ut_id(gvar, 'clg1'),
            'group_name.2': ut_id(gvar, 'clg4')
        }
    )

    # user to be deleted in no groups
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'clu5')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'clu5'),
            'password': user_secret,
            'cert_cn': ut_id(gvar, 'command line user five')
        }
    )

    # user to be deleted in groups
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'clu6')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'clu6'),
            'password': user_secret,
            'cert_cn': ut_id(gvar, 'command line user six'),
            'group_name': ut_id(gvar, 'clg1')
        }
    )

    # user to be updated
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'clu7')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'clu7'),
            'password': user_secret,
            'cert_cn': ut_id(gvar, 'command line user seven')
        }
    )

    # cloud to be deleted
    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc1')),
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'clg1'),
            'cloud_name': ut_id(gvar, 'clc1'),
            'authurl': 'unit-test-cloud-one.ca',
            'project': 'unit-test-cloud-one',
            'username': ut_id(gvar, 'clc1'),
            'password': 'unit-test-cloud-one',
            'region': ut_id(gvar, 'clc1-r'),
            'cloud_type': 'local'
        }
    )

    # cloud to be deleted
    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc3')),
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'clg1'),
            'cloud_name': ut_id(gvar, 'clc3'),
            'authurl': 'unit-test-cloud-three.ca',
            'project': 'unit-test-cloud-three',
            'username': ut_id(gvar, 'clc3'),
            'password': 'unit-test-cloud-three',
            'region': ut_id(gvar, 'clc3-r'),
            'cloud_type': 'local'
        }
    )

    # cloud to be listed and edited
    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2')),
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'clg1'),
            'cloud_name': ut_id(gvar, 'clc2'),
            'authurl': 'unit-test-cloud-two.ca',
            'project': 'unit-test-cloud-two',
            'username': ut_id(gvar, 'clc2'),
            'password': 'unit-test-cloud-two',
            'region': ut_id(gvar, 'clc2-r'),
            'cloud_type': 'local'
        }
    )

    # group metadata to be deleted
    execute_csv2_request(
        gvar, 0, None, 'file "{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clm1')),
        '/group/metadata-add/', form_data={
            'group': ut_id(gvar, 'clg1'),
            'metadata_name': ut_id(gvar, 'clm1'),
            'metadata': '- example: yaml'
        }
    )

    # group metadata to be edited
    execute_csv2_request(
        gvar, 0, None, 'file "{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clm2')),
        '/group/metadata-add/', form_data={
            'group': ut_id(gvar, 'clg1'),
            'metadata_name': ut_id(gvar, 'clm2'),
            'metadata': '- example: yaml'
        }
    )

    execute_csv2_request(
        gvar, 0, None, 'file "{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clm2.yaml')),
        '/group/metadata-add/', form_data={
            'group': ut_id(gvar, 'clg1'),
            'metadata_name': ut_id(gvar, 'clm2.yaml'),
            'metadata': '- example: yaml'
        }
    )

    execute_csv2_request(
        gvar, 0, None, 'file "{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clm3')),
        '/group/metadata-add/', form_data={
            'group': ut_id(gvar, 'clg1'),
            'metadata_name': ut_id(gvar, 'clm3'),
            'metadata': '- example: yaml'
        }
    )

    # cloud metadata to be deleted
    execute_csv2_request(
        gvar, 0, None, 'cloud metadata file "{}::{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2'), ut_id(gvar, 'clm1')),
        '/cloud/metadata-add/', form_data={
            'cloud_name': ut_id(gvar, 'clc2'),
            'metadata_name': ut_id(gvar, 'clm1'),
            'metadata': '- example: yes'
        }
    )

    execute_csv2_request(
        gvar, 0, None, 'cloud metadata file "{}::{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2'), ut_id(gvar, 'clm3')),
        '/cloud/metadata-add/', form_data={
            'cloud_name': ut_id(gvar, 'clc2'),
            'metadata_name': ut_id(gvar, 'clm3'),
            'metadata': '- example: yes'
        }
    )

    # cloud metadata to be edited
    execute_csv2_request(
        gvar, 0, None, 'cloud metadata file "{}::{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2'), ut_id(gvar, 'clm2')),
        '/cloud/metadata-add/', form_data={
            'cloud_name': ut_id(gvar, 'clc2'),
            'metadata_name': ut_id(gvar, 'clm2'),
            'metadata': '- example: yes'
        }
    )

    execute_csv2_request(
        gvar, 0, None, 'cloud metadata file "{}::{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2'), ut_id(gvar, 'clm2.yaml')),
        '/cloud/metadata-add/', form_data={
            'cloud_name': ut_id(gvar, 'clc2'),
            'metadata_name': ut_id(gvar, 'clm2.yaml'),
            'metadata': '- example: yes'
        }
    )
    
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'defaults', 'set', '-s', 'unit-test-un', '-su', ut_id(gvar, 'test'), '-spw', user_secret]
    )

if __name__ == "__main__":
    main(None)
