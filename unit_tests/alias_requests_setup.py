from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id
from sys import argv
import alias_requests_cleanup

def main(gvar):

    # 01 - 04
    alias_requests_cleanup.main(gvar)

    # 05 Unprivileged user in atg1.
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'atu1')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'atu1'),
            'password2': gvar['user_secret'],
            'password1': gvar['user_secret'],
            'cert_cn': '{} test user 1'.format(ut_id(gvar, 'alias'))
        }
    )

    # 06 Unprivileged user in no groups.
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'atu2')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'atu2'),
            'password2': gvar['user_secret'],
            'password1': gvar['user_secret'],
            'cert_cn': '{} test user 2'.format(ut_id(gvar, 'alias'))
        }
    )

    # 07 Group containing atu1.
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'atg1')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'atg1'),
            'htcondor_fqdn': gvar['fqdn'],
            'username.1': ut_id(gvar, 'atu1')
        }
    )

    # 08 Group containing no users.
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'atg2')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'atg2'),
            'htcondor_fqdn': gvar['fqdn']
        }
    )

    # 09 Cloud to create aliases for.
    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully added.'.format(ut_id(gvar, 'atg1'), ut_id(gvar, 'atc1')),
        '/cloud/add/', group=ut_id(gvar, 'atg1'), form_data={
            'cloud_name': ut_id(gvar, 'atc1'),
            'cloud_type': 'openstack',
            **gvar['cloud_credentials']
        },
        server_user=ut_id(gvar, 'atu1')
    )

    # 10 Cloud to create aliases for.
    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully added.'.format(ut_id(gvar, 'atg1'), ut_id(gvar, 'atc2')),
        '/cloud/add/', group=ut_id(gvar, 'atg1'), form_data={
            'cloud_name': ut_id(gvar, 'atc2'),
            'cloud_type': 'openstack',
            **gvar['cloud_credentials']
        },
        server_user=ut_id(gvar, 'atu1')
    )

    # 11 Alias to be listed. Should always exist and contain atc1.
    execute_csv2_request(
        gvar, 0, None, 'cloud alias "{}.{}" successfully added.'.format(ut_id(gvar, 'atg1'), ut_id(gvar, 'ata1')),
        '/alias/add/', group=ut_id(gvar, 'atg1'), form_data={
            'alias_name': ut_id(gvar, 'ata1'),
            'cloud_name': ut_id(gvar, 'atc1')
        },
        server_user=ut_id(gvar, 'atu1')
    )

    # 12 Alias to be updated and deleted.
    execute_csv2_request(
        gvar, 0, None, 'cloud alias "{}.{}" successfully added.'.format(ut_id(gvar, 'atg1'), ut_id(gvar, 'ata2')),
        '/alias/add/', group=ut_id(gvar, 'atg1'), form_data={
            'alias_name': ut_id(gvar, 'ata2'),
            'cloud_name': ut_id(gvar, 'atc1')
        },
        server_user=ut_id(gvar, 'atu1')
    )

if __name__ == '__main__':
    main(initialize_csv2_request(selections=argv[1] if len(argv) > 1 else ''))
