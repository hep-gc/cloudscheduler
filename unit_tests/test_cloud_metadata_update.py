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
        '/cloud/metadata-update/',
        server_user='invalid-unit-test', server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, None, 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'ctu1')),
        '/cloud/metadata-update/',
        server_user=ut_id(gvar, 'ctu1'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, None, 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'ctu2')),
        '/cloud/metadata-update/',
        server_user=ut_id(gvar, 'ctu2'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV31', 'cloud metadata_update, invalid method "GET" specified.',
        '/cloud/metadata-update/',
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        '/cloud/metadata-update/', form_data={'group': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, None, 'cannot switch to invalid group "{}".'.format(ut_id(gvar, 'ctg2')),
        '/cloud/metadata-update/', form_data={'group': ut_id(gvar, 'ctg2')},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV29', 'cloud metadata-update request did not contain mandatory parameter "cloud_name".',
        '/cloud/metadata-update/', form_data={'group': ut_id(gvar, 'ctg1')},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV29', 'cloud metadata-update request did not contain mandatory parameter "cloud_name".',
        '/cloud/metadata-update/', form_data={'metadata_name': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV29', 'cloud metadata-update request did not contain mandatory parameter "metadata_name".',
        '/cloud/metadata-update/', form_data={'cloud_name': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV29', 'cloud metadata-update request contained a bad parameter "invalid-unit-test".',
        '/cloud/metadata-update/', form_data={
            'cloud_name': 'invalid-unit-test',
            'metadata_name': 'invalid-unit-test',
            'invalid-unit-test': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV29', 'value specified for "cloud_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        '/cloud/metadata-update/', form_data={
            'cloud_name': 'Invalid-unit-test',
            'metadata_name': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV29', 'value specified for "cloud_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        '/cloud/metadata-update/', form_data={
            'cloud_name': 'invalid-unit-test-',
            'metadata_name': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV29', 'value specified for "cloud_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        '/cloud/metadata-update/', form_data={
            'cloud_name': 'invalid-unit-test!',
            'metadata_name': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV29', 'value specified for "metadata_name" must be all lower case.',
        '/cloud/metadata-update/', form_data={
            'cloud_name': 'invalid-unit-test',
            'metadata_name': 'Invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV29', 'boolean value specified for "enabled" must be one of the following: true, false, yes, no, 1, or 0.',
        '/cloud/metadata-update/', form_data={
            'cloud_name': 'invalid-unit-test',
            'metadata_name': 'invalid-unit-test',
            'enabled': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV29', 'value specified for "mime_type" must be one of the following options: [\'cloud-config\', \'ucernvm-config\'].',
        '/cloud/metadata-update/', form_data={
            'cloud_name': 'invalid-unit-test',
            'metadata_name': 'invalid-unit-test',
            'mime_type': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV30', 'the request did not match any rows.',
        '/cloud/metadata-update/', form_data={
            'cloud_name': 'invalid-unit-test',
            'metadata_name': 'invalid-unit-test',
            'priority': 1
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV30', 'the request did not match any rows.',
        '/cloud/metadata-update/', form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'metadata_name': 'invalid-unit-test',
            'priority': 1
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV30', 'You have an error in your SQL syntax',
        '/cloud/metadata-update/', form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'metadata_name': ut_id(gvar, 'cty3')
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV29', 'yaml value specified for "metadata (metadata_name)" is invalid - scanner error',
        '/cloud/metadata-update/', form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'metadata_name': ut_id(gvar, 'cty3.yaml'),
            'metadata': 'foo: this is invalid: yaml'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'CV29', 'value specified for "priority" must be a integer value.',
        '/cloud/metadata-update/', form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'metadata_name': ut_id(gvar, 'cty3.yaml'),
            'priority': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, 'cloud metadata file "{}::{}::{}" successfully  updated.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc3'), ut_id(gvar, 'cty3')),
        '/cloud/metadata-update/', form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'metadata_name': ut_id(gvar, 'cty3'),
            'metadata': 'foo: this is invalid: yaml'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, 'cloud metadata file "{}::{}::{}" successfully  updated.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc3'), ut_id(gvar, 'cty3.yaml')),
        '/cloud/metadata-update/', form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'metadata_name': ut_id(gvar, 'cty3.yaml'),
            'metadata': '- foo: this is valid yaml'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, 'cloud metadata file "{}::{}::{}" successfully  updated.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc3'), ut_id(gvar, 'cty3.yaml')),
        '/cloud/metadata-update/', form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'metadata_name': ut_id(gvar, 'cty3.yaml'),
            'priority': 1
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, 'cloud metadata file "{}::{}::{}" successfully  updated.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc3'), ut_id(gvar, 'cty3.yaml')),
        '/cloud/metadata-update/', form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'metadata_name': ut_id(gvar, 'cty3.yaml'),
            'mime_type': 'ucernvm-config'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, 'cloud metadata file "{}::{}::{}" successfully  updated.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc3'), ut_id(gvar, 'cty3.yaml')),
        '/cloud/metadata-update/', form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'metadata_name': ut_id(gvar, 'cty3.yaml'),
            'enabled': 'false'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

if __name__ == "__main__":
    main(None)
