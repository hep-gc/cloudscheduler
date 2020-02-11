from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, generate_secret
from sys import argv
import alias_requests_cleanup

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv1_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv1_request(gvar, argv[0])
    if not gvar['user_secret']:
        gvar['user_secret'] = generate_secret()

    alias_requests_cleanup.main(gvar)

    # 04 Unprivileged user in atg1.
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'atu1')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'atu1'),
            'password2': gvar['user_secret'],
            'password1': gvar['user_secret'],
            'cert_cn': '{} test user 1'.format(ut_id(gvar, 'alias'))
        }
    )

    # 05 Unprivileged user in no groups.
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'atu2')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'atu2'),
            'password2': gvar['user_secret'],
            'password1': gvar['user_secret'],
            'cert_cn': '{} test user 2'.format(ut_id(gvar, 'alias'))
        }
    )

    # 06 Group containing atu1.
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'atg1')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'atg1'),
            'htcondor_fqdn': 'alias-test-group-1.ca',
            'username.1': ut_id(gvar, 'atu1')
        }
    )

    # Group containing no users.
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'atg2')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'atg2'),
            'htcondor_fqdn': 'alias-test-group-2.ca'
        }
    )

    # Cloud to create aliases for.
    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully added.'.format(ut_id(gvar, 'atg1'), ut_id(gvar, 'atc1')),
        '/cloud/add/', group=ut_id(gvar, 'atg1'), form_data={
            'cloud_name': ut_id(gvar, 'atc1'),
            'cloud_type': 'local',
            'authurl': 'alias-test-cloud-1.ca',
            'project': ut_id(gvar, 'atp1'),
            'region': ut_id(gvar, 'atr1'),
            'username': ut_id(gvar, 'atu1'),
            'password': gvar['user_secret']
        },
        server_user=ut_id(gvar, 'atu1')
    )

    # Cloud to create aliases for.
    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully added.'.format(ut_id(gvar, 'atg1'), ut_id(gvar, 'atc2')),
        '/cloud/add/', group=ut_id(gvar, 'atg1'), form_data={
            'cloud_name': ut_id(gvar, 'atc2'),
            'cloud_type': 'local',
            'authurl': 'alias-test-cloud-2.ca',
            'project': ut_id(gvar, 'atp2'),
            'region': ut_id(gvar, 'atr2'),
            'username': ut_id(gvar, 'atu1'),
            'password': gvar['user_secret']
        },
        server_user=ut_id(gvar, 'atu1')
    )

    # Alias to be deleted.
    execute_csv2_request(
        gvar, 0, None, 'cloud alias "{}.{}" successfully added.'.format(ut_id(gvar, 'atg1'), ut_id(gvar, 'atc1a1')),
        '/alias/add/', group=ut_id(gvar, 'atg1'), form_data={
            'cloud_name': ut_id(gvar, 'atc1'),
            'alias_name': ut_id(gvar, 'atc1a1')
        },
        server_user=ut_id(gvar, 'atu1')
    )

if __name__ == '__main__':
    main(None)
