from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id
import sys
import group_requests_cleanup

def main(gvar):
    if not gvar:
        gvar = {}
        if len(sys.argv) > 1:
            initialize_csv2_request(gvar, sys.argv[0], selections=sys.argv[1])
        else:
            initialize_csv2_request(gvar, sys.argv[0])
    
    group_requests_cleanup.main(gvar)

    # unprivileged user in no groups
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'gtu1')),
            '/user/add/', form_data={
                'username': ut_id(gvar, 'gtu1'),
                'password1': 'Abc123',
                'password2': 'Abc123',
                'cert_cn': '{} test user one'.format(ut_id(gvar, 'group'))
            }
        )
    
    # privileged user in no groups
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'gtu2')),
            '/user/add/', form_data={
                'username': ut_id(gvar, 'gtu2'),
                'password1': 'Abc123',
                'password2': 'Abc123',
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

    # unprivileged user in group gtg5
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'gtu3')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'gtu3'),
            'password1': 'Abc123',
            'password2': 'Abc123',
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
            'password1': 'Abc123',
            'password2': 'Abc123',
            'is_superuser': 1,
            'cert_cn': '{} test user five'.format(ut_id(gvar, 'group')),
            'group_name.1': ut_id(gvar, 'gtg4'),
            'group_name.2': ut_id(gvar, 'gtg5'),
            'group_name.3': ut_id(gvar, 'gtg6')
        }
    )
    
    execute_csv2_request(
        gvar, 0, None, 'file "{}::{}" successfully added.'.format(ut_id(gvar, 'gtg5'), ut_id(gvar, 'gty4')),
        '/group/metadata-add/', form_data={
            'group': ut_id(gvar, 'gtg5'),
            'metadata_name': ut_id(gvar, 'gty4'),
            'metadata': '- example: yaml'
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 0, None, 'file "{}::{}" successfully added.'.format(ut_id(gvar, 'gtg5'), ut_id(gvar, 'gty5')),
        '/group/metadata-add/', form_data={
            'group': ut_id(gvar, 'gtg5'),
            'metadata_name': ut_id(gvar, 'gty5'),
            'metadata': '- example: yaml'
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 0, None, 'file "{}::{}" successfully added.'.format(ut_id(gvar, 'gtg5'), ut_id(gvar, 'gty5.yaml')),
        '/group/metadata-add/', form_data={
            'group': ut_id(gvar, 'gtg5'),
            'metadata_name': ut_id(gvar, 'gty5.yaml'),
            'metadata': '- example: yaml'
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw='Abc123'
    )
    
    # unprivileged user to be added to groups
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'gtu4')),
            '/user/add/', form_data={
                'username': ut_id(gvar, 'gtu4'),
                'password1': 'Abc123',
                'password2': 'Abc123',
                'cert_cn': '{} test user four'.format(ut_id(gvar, 'group'))
            }
        )

if __name__ == "__main__":
    main(None)