from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id
from sys import argv

# lno: CV - error code identifier.

def main(gvar, user_secret):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv2_request(gvar, argv[0])
    
    # 1
    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 401, unauthorized.',
        '/cloud/metadata-delete/',
        server_user='invalid-unit-test', server_pw=user_secret
    )

    # 2
    execute_csv2_request(
        gvar, 1, None, 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'ctu1')),
        '/cloud/metadata-delete/',
        server_user=ut_id(gvar, 'ctu1'), server_pw=user_secret
    )

    # 3
    execute_csv2_request(
        gvar, 1, None, 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'ctu2')),
        '/cloud/metadata-delete/',
        server_user=ut_id(gvar, 'ctu2'), server_pw=user_secret
    )

    # 4
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud metadata-delete request did not contain mandatory parameters "cloud_name" and "metadata_name".',
        '/cloud/metadata-delete/',
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 5
    execute_csv2_request(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        '/cloud/metadata-delete/', group='invalid-unit-test',
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 6
    execute_csv2_request(
        gvar, 1, None, 'cannot switch to invalid group "{}".'.format(ut_id(gvar, 'ctg2')),
        '/cloud/metadata-delete/', group=ut_id(gvar, 'ctg2'),
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 7
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud metadata-delete request did not contain mandatory parameters "cloud_name" and "metadata_name".',
        '/cloud/metadata-delete/', group=ut_id(gvar, 'ctg1'),
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 8
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud metadata-delete request did not contain mandatory parameter "metadata_name".',
        '/cloud/metadata-delete/', form_data={'cloud_name': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 9
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud metadata-delete request did not contain mandatory parameter "cloud_name".',
        '/cloud/metadata-delete/', form_data={'metadata_name': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 10
    execute_csv2_request(
        gvar, 1, 'CV', 'value specified for "cloud_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        '/cloud/metadata-delete/', form_data={
            'cloud_name': 'Invalid-unit-test',
            'metadata_name': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 11
    execute_csv2_request(
        gvar, 1, 'CV', 'value specified for "metadata_name" must be all lower case.',
        '/cloud/metadata-delete/', form_data={
            'cloud_name': 'invalid-unit-test',
            'metadata_name': 'Invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 12
    execute_csv2_request(
        gvar, 1, 'CV', 'the request did not match any rows.',
        '/cloud/metadata-delete/', form_data={
            'cloud_name': 'invalid-unit-test',
            'metadata_name': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 13
    execute_csv2_request(
        gvar, 0, None, 'cloud metadata file "{}::{}::{}" successfully deleted.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc3'), ut_id(gvar, 'cty2')),
        '/cloud/metadata-delete/', form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'metadata_name': ut_id(gvar, 'cty2')
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

if __name__ == "__main__":
    main(None)
