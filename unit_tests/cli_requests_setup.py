from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, generate_secret
from sys import argv
import cli_requests_cleanup

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)
    if not gvar['user_secret']:
        gvar['user_secret'] = generate_secret()
    
    cli_requests_cleanup.main(gvar)

    # unprivileged user in no groups
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'clu1')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'clu1'),
            'password1': gvar['user_secret'],
            'password2': gvar['user_secret'],
            'cert_cn': ut_id(gvar, 'command-line-user-1')
        }
    )
    
    # privileged user in no groups
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'clu2')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'clu2'),
            'password1': gvar['user_secret'],
            'password2': gvar['user_secret'],
            'cert_cn': ut_id(gvar, 'command-line-user-2'),
            'is_superuser': 1
        }
    )

    # group with users
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'clg1')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'clg1'),
            'htcondor_fqdn': gvar['user_settings']['server-address'],
        }
    )

    # group without users
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'clg2')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'clg2'),
            'htcondor_fqdn': gvar['user_settings']['server-address'],
        }
    )

    # group to be updated and for users to be added to
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'clg3')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'clg3'),
            'htcondor_fqdn': gvar['user_settings']['server-address']
        }
    )

    # group to be deleted with users
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'clg4')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'clg4'),
            'htcondor_fqdn': gvar['user_settings']['server-address']
        }
    )

    # unprivileged user in clg1
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'clu3')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'clu3'),
            'password1': gvar['user_secret'],
            'password2': gvar['user_secret'],
            'cert_cn': ut_id(gvar, 'command-line-user-3'),
            'group_name.1': ut_id(gvar, 'clg1')
        }
    )
    
    # privileged user in clg1
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'clu4')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'clu4'),
            'password1': gvar['user_secret'],
            'password2': gvar['user_secret'],
            'cert_cn': ut_id(gvar, 'command-line-user-4'),
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
            'password': gvar['user_secret'],
            'cert_cn': ut_id(gvar, 'command-line-user-5')
        }
    )

    # user to be deleted in groups
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'clu6')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'clu6'),
            'password': gvar['user_secret'],
            'cert_cn': ut_id(gvar, 'command-line-user-6'),
            'group_name': ut_id(gvar, 'clg1')
        }
    )

    # user to be updated
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'clu7')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'clu7'),
            'password': gvar['user_secret'],
            'cert_cn': ut_id(gvar, 'command-line-user-7')
        }
    )

    # cloud to be deleted
    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc1')),
        '/cloud/add/', group=ut_id(gvar, 'clg1'), form_data={
            'cloud_name': ut_id(gvar, 'clc1'),
            'cloud_type': 'openstack',
            **gvar['cloud_credentials']
        },
        server_user=ut_id(gvar, 'clu4')
    )

    # cloud to be listed and edited
    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2')),
        '/cloud/add/', group=ut_id(gvar, 'clg1'), form_data={
            'cloud_name': ut_id(gvar, 'clc2'),
            'cloud_type': 'openstack',
            **gvar['cloud_credentials']
        },
        server_user=ut_id(gvar, 'clu4')
    )

    # Cloud to be added to an alias in cli_alias_update.
    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc3')),
        '/cloud/add/', group=ut_id(gvar, 'clg1'), form_data={
            'cloud_name': ut_id(gvar, 'clc3'),
            'cloud_type': 'openstack',
            **gvar['cloud_credentials']
        },
        server_user=ut_id(gvar, 'clu4')
    )

    # Alias to be listed. Should always exist and contain clc2.
    execute_csv2_request(
        gvar, 0, None, 'cloud alias "{}.{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'cla1')),
        '/alias/add/', group=ut_id(gvar, 'clg1'), form_data={
            'alias_name': ut_id(gvar, 'cla1'),
            'cloud_name': ut_id(gvar, 'clc2')
        },
        server_user=ut_id(gvar, 'clu4')
    )

    # Alias to be updated and deleted.
    execute_csv2_request(
        gvar, 0, None, 'cloud alias "{}.{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'cla2')),
        '/alias/add/', group=ut_id(gvar, 'clg1'), form_data={
            'alias_name': ut_id(gvar, 'cla2'),
            'cloud_name': ut_id(gvar, 'clc2')
        },
        server_user=ut_id(gvar, 'clu4')
    )


    # group metadata to be deleted
    execute_csv2_request(
        gvar, 0, None, 'file "{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clm1')),
        '/group/metadata-add/', group=ut_id(gvar, 'clg1'), form_data={
            'metadata_name': ut_id(gvar, 'clm1'),
            'metadata': '- example: yaml'
        },
        server_user=ut_id(gvar, 'clu4')
    )

    # group metadata to be edited
    execute_csv2_request(
        gvar, 0, None, 'file "{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clm2')),
        '/group/metadata-add/', group=ut_id(gvar, 'clg1'), form_data={
            'metadata_name': ut_id(gvar, 'clm2'),
            'metadata': '- example: yaml'
        },
        server_user=ut_id(gvar, 'clu4')
    )

    execute_csv2_request(
        gvar, 0, None, 'file "{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clm2.yaml')),
        '/group/metadata-add/', group=ut_id(gvar, 'clg1'), form_data={
            'metadata_name': ut_id(gvar, 'clm2.yaml'),
            'metadata': '- example: yaml'
        },
        server_user=ut_id(gvar, 'clu4')
    )

    execute_csv2_request(
        gvar, 0, None, 'file "{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clm3')),
        '/group/metadata-add/', group=ut_id(gvar, 'clg1'), form_data={
            'metadata_name': ut_id(gvar, 'clm3'),
            'metadata': '- example: yaml'
        },
        server_user=ut_id(gvar, 'clu4')
    )

    # cloud metadata to be deleted
    execute_csv2_request(
        gvar, 0, None, 'cloud metadata file "{}::{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2'), ut_id(gvar, 'clm1')),
        '/cloud/metadata-add/', group=ut_id(gvar, 'clg1'), form_data={
            'cloud_name': ut_id(gvar, 'clc2'),
            'metadata_name': ut_id(gvar, 'clm1'),
            'metadata': '- example: yes'
        },
        server_user=ut_id(gvar, 'clu4')
    )

    execute_csv2_request(
        gvar, 0, None, 'cloud metadata file "{}::{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2'), ut_id(gvar, 'clm3')),
        '/cloud/metadata-add/', group=ut_id(gvar, 'clg1'), form_data={
            'cloud_name': ut_id(gvar, 'clc2'),
            'metadata_name': ut_id(gvar, 'clm3'),
            'metadata': '- example: yes'
        },
        server_user=ut_id(gvar, 'clu4')
    )

    # cloud metadata to be edited
    execute_csv2_request(
        gvar, 0, None, 'cloud metadata file "{}::{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2'), ut_id(gvar, 'clm2')),
        '/cloud/metadata-add/', group=ut_id(gvar, 'clg1'), form_data={
            'cloud_name': ut_id(gvar, 'clc2'),
            'metadata_name': ut_id(gvar, 'clm2'),
            'metadata': '- example: yes'
        },
        server_user=ut_id(gvar, 'clu4')
    )

    execute_csv2_request(
        gvar, 0, None, 'cloud metadata file "{}::{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2'), ut_id(gvar, 'clm2.yaml')),
        '/cloud/metadata-add/', group=ut_id(gvar, 'clg1'), form_data={
            'cloud_name': ut_id(gvar, 'clc2'),
            'metadata_name': ut_id(gvar, 'clm2.yaml'),
            'metadata': '- example: yes'
        },
        server_user=ut_id(gvar, 'clu4')
    )

if __name__ == "__main__":
    main(None)
