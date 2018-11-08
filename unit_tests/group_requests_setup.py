from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, generate_secret
from sys import argv
import group_requests_cleanup

def main(gvar, user_secret):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv2_request(gvar, argv[0])
    if not user_secret:
        user_secret = generate_secret()

    group_requests_cleanup.main(gvar)

    # unprivileged user in no groups
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'gtu1')),
            '/user/add/', form_data={
                'username': ut_id(gvar, 'gtu1'),
                'password1': user_secret,
                'password2': user_secret,
                'cert_cn': '{} test user one'.format(ut_id(gvar, 'group'))
            }
        )

    # privileged user in no groups
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'gtu2')),
            '/user/add/', form_data={
                'username': ut_id(gvar, 'gtu2'),
                'password1': user_secret,
                'password2': user_secret,
                'cert_cn': '{} test user two'.format(ut_id(gvar, 'group')),
                'is_superuser': 1
            }
        )

    # group to be changed in group_update
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'gtg4')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'gtg4'),
            'condor_central_manager': 'unit-test-group-four.ca'
        }
    )

    # group to be changed in group_yaml_*
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'gtg5')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'gtg5'),
            'condor_central_manager': 'unit-test-group-five.ca',
        }
    )

    # group to be deleted in group_delete
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'gtg6')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'gtg6'),
            'condor_central_manager': 'unit-test-group-six.ca',
        }
    )

    # group with no users
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'gtg7')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'gtg7'),
            'condor_central_manager': 'unit-test-group-seven.ca',
        }
    )

    # unprivileged user in groups
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'gtu3')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'gtu3'),
            'password1': user_secret,
            'password2': user_secret,
            'cert_cn': '{} test user three'.format(ut_id(gvar, 'group')),
            'group_name.1': ut_id(gvar, 'gtg4'),
            'group_name.2': ut_id(gvar, 'gtg5')
        }
    )

    # privileged user in group gtg5,6
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'gtu5')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'gtu5'),
            'password1': user_secret,
            'password2': user_secret,
            'is_superuser': 1,
            'cert_cn': '{} test user five'.format(ut_id(gvar, 'group')),
            'group_name.1': ut_id(gvar, 'gtg4'),
            'group_name.2': ut_id(gvar, 'gtg5'),
        }
    )

    execute_csv2_request(
        gvar, 0, None, 'file "{}::{}" successfully added.'.format(ut_id(gvar, 'gtg5'), ut_id(gvar, 'gty4')),
        '/group/metadata-add/', form_data={
            'group': ut_id(gvar, 'gtg5'),
            'metadata_name': ut_id(gvar, 'gty4'),
            'metadata': '- example: yaml'
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, 'file "{}::{}" successfully added.'.format(ut_id(gvar, 'gtg5'), ut_id(gvar, 'gty5')),
        '/group/metadata-add/', form_data={
            'group': ut_id(gvar, 'gtg5'),
            'metadata_name': ut_id(gvar, 'gty5'),
            'metadata': '- example: yaml'
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, 'file "{}::{}" successfully added.'.format(ut_id(gvar, 'gtg5'), ut_id(gvar, 'gty5.yaml')),
        '/group/metadata-add/', form_data={
            'group': ut_id(gvar, 'gtg5'),
            'metadata_name': ut_id(gvar, 'gty5.yaml'),
            'metadata': '- example: yaml'
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    # metadata to be deleted in a cloud exception
    execute_csv2_request(
        gvar, 0, None, 'file "{}::{}" successfully added.'.format(ut_id(gvar, 'gtg5'), ut_id(gvar, 'gty6')),
        '/group/metadata-add/', form_data={
            'group': ut_id(gvar, 'gtg5'),
            'metadata_name': ut_id(gvar, 'gty6'),
            'metadata': '- example: yaml'
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    # unprivileged user to be added to groups
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'gtu4')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'gtu4'),
            'password1': user_secret,
            'password2': user_secret,
            'cert_cn': '{} test user four'.format(ut_id(gvar, 'group'))
        }
    )

    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully added.'.format(ut_id(gvar, 'gtg5'), ut_id(gvar, 'gtc1')),
        '/cloud/add/', form_data={
            'group': ut_id(gvar, 'gtg5'),
            'cloud_name': ut_id(gvar, 'gtc1'),
            'authurl': 'group-test-cloud-one.ca',
            'project': 'group-test-cloud-one',
            'username': ut_id(gvar, 'gtu3'),
            'password': user_secret,
            'region': ut_id(gvar, 'gtc1-r'),
            'cloud_type': 'local',
            'metadata_name': ut_id(gvar, 'gty6')
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

if __name__ == "__main__":
    main(None)
