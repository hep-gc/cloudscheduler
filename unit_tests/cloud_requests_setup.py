from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, generate_secret
from sys import argv
import cloud_requests_cleanup

def main(gvar, user_secret):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv2_request(gvar, argv[0])
    if not user_secret:
        user_secret = generate_secret()
    
    cloud_requests_cleanup.main(gvar)

    # 07 unprivileged user in no groups
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'ctu1')),
        '/user/add/'
, form_data={
            'username': ut_id(gvar, 'ctu1'),
            'password1': user_secret,
            'password2': user_secret,
            'cert_cn': '{} test user one'.format(ut_id(gvar, 'cloud'))
        }
    )
    
    # 08 privileged user in no groups
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'ctu2')),
        '/user/add/'
, form_data={
            'username': ut_id(gvar, 'ctu2'),
            'password1': user_secret,
            'password2': user_secret,
            'cert_cn': '{} test user two'.format(ut_id(gvar, 'cloud')),
            'is_superuser': 1
        }
    )

    # 09 group with users
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'ctg1')),
        '/group/add/'
, form_data={
            'group_name': ut_id(gvar, 'ctg1'),
            'htcondor_fqdn': 'unit-test-group-one.ca'
        }
    )

    # 10 group without users
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'ctg2')),
        '/group/add/'
, form_data={
            'group_name': ut_id(gvar, 'ctg2'),
            'htcondor_fqdn': 'unit-test-group-two.ca'
        }
    )

    # 11 unprivileged user in ctg1
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'ctu3')),
        '/user/add/'
, form_data={
            'username': ut_id(gvar, 'ctu3'),
            'password1': user_secret,
            'password2': user_secret,
            'cert_cn': '{} test user three'.format(ut_id(gvar, 'cloud')),
            'group_name.1': ut_id(gvar, 'ctg1')
        }
    )
    
    # 12 privileged user in ctg1
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'ctu4')),
        '/user/add/'
, form_data={
            'username': ut_id(gvar, 'ctu4'),
            'password1': user_secret,
            'password2': user_secret,
            'cert_cn': '{} test user four'.format(ut_id(gvar, 'cloud')),
            'is_superuser': 1,
            'group_name.1': ut_id(gvar, 'ctg1')
        }
    )

    # 13 cloud to be deleted in test_cloud_delete
    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully added.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc1')),
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={
            'cloud_name': ut_id(gvar, 'ctc1'),
            'authurl': 'unit-test-cloud-one.ca',
            'project': 'unit-test-cloud-one',
            'username': ut_id(gvar, 'ctu3'),
            'password': user_secret,
            'region': ut_id(gvar, 'ctc1-r'),
            'cloud_type': 'local'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 14 cloud to be listed in test_cloud_list
    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully added.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc2')),
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={
            'cloud_name': ut_id(gvar, 'ctc2'),
            'authurl': 'unit-test-cloud-two.ca',
            'project': 'unit-test-cloud-two',
            'username': ut_id(gvar, 'ctu3'),
            'password': user_secret,
            'region': ut_id(gvar, 'ctc2-r'),
            'cloud_type': 'local',
            'priority': 0,
            'cacertificate': None,
            'user_domain_name': 'Default',
            'project_domain_name': '\'Default\'',
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 15 cloud to be changed in test_cloud_update, test_cloud_metadata_add, test_cloud_metadata_delete
    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully added.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc3')),
        '/cloud/add/', group=ut_id(gvar, 'ctg1'), form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'authurl': 'unit-test-cloud-three.ca',
            'project': 'unit-test-cloud-three',
            'username': ut_id(gvar, 'ctu3'),
            'password': user_secret,
            'region': ut_id(gvar, 'ctc3-r'),
            'cloud_type': 'local',
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 16 metadata to be deleted in test_cloud_metadata_delete
    execute_csv2_request(
        gvar, 0, None, 'cloud metadata file "{}::{}::{}" successfully added.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc3'), ut_id(gvar, 'cty2')),
        '/cloud/metadata-add/'
, form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'metadata_name': ut_id(gvar, 'cty2'),
            'metadata': '- example: yes'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 17 metadata to be updated in test_cloud_metadata_update
    execute_csv2_request(
        gvar, 0, None, 'cloud metadata file "{}::{}::{}" successfully added.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc3'), ut_id(gvar, 'cty3')),
        '/cloud/metadata-add/'
, form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'metadata_name': ut_id(gvar, 'cty3'),
            'metadata': '- example: yes'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 18 metadata to be updated in test_cloud_metadata_update
    execute_csv2_request(
        gvar, 0, None, 'cloud metadata file "{}::{}::{}" successfully added.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc3'), ut_id(gvar, 'cty3.yaml')),
        '/cloud/metadata-add/'
, form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'metadata_name': ut_id(gvar, 'cty3.yaml'),
            'metadata': '- example: yes'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 19 metadata to be fetched in test_cloud_metadata_fetch and test_cloud_metadata_list
    execute_csv2_request(
        gvar, 0, None, 'cloud metadata file "{}::{}::{}" successfully added.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc2'), ut_id(gvar, 'cty1')),
        '/cloud/metadata-add/'
, form_data={
            'cloud_name': ut_id(gvar, 'ctc2'),
            'metadata_name': ut_id(gvar, 'cty1'),
            'metadata': '- example: yes'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 20
    execute_csv2_request(
        gvar, 0, None, 'file "{}::{}" successfully added.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'cty1')),
        '/group/metadata-add/', group=ut_id(gvar, 'ctg1'), form_data={
            'metadata_name': ut_id(gvar, 'cty1'),
            'metadata': '- example: yaml'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 21 group metadata for metadata exceptions in test_cloud_add and test_cloud_update
    execute_csv2_request(
        gvar, 0, None, 'file "{}::{}" successfully added.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'cty2')),
        '/group/metadata-add/', group=ut_id(gvar, 'ctg1'), form_data={
            'metadata_name': ut_id(gvar, 'cty2'),
            'metadata': '- example: yaml'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 22
    execute_csv2_request(
        gvar, 0, None, 'file "{}::{}" successfully added.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'cty3')),
        '/group/metadata-add/', group=ut_id(gvar, 'ctg1'), form_data={
            'metadata_name': ut_id(gvar, 'cty3'),
            'metadata': '- example: yaml'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

if __name__ == "__main__":
    main(None)
