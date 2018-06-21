from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id
import sys

def main(gvar):
    if not gvar:
        gvar = {}
        if len(sys.argv) > 1:
            initialize_csv2_request(gvar, sys.argv[0], selections=sys.argv[1])
        else:
            initialize_csv2_request(gvar, sys.argv[0])

    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 401, unauthorized.',
        '/cloud/metadata-add/',
        server_user='invalid-unit-test', server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, None, 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'ctu1')),
        '/cloud/metadata-add/',
        server_user=ut_id(gvar, 'ctu1'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, None, 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'ctu2')),
        '/cloud/metadata-add/',
        server_user=ut_id(gvar, 'ctu2'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV20', 'cloud metadata_add, invalid method "GET" specified.',
        '/cloud/metadata-add/',
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        '/cloud/metadata-add/', form_data={'group': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, None, 'cannot switch to invalid group "{}".'.format(ut_id(gvar, 'ctg2')),
        '/cloud/metadata-add/', form_data={'group': ut_id(gvar, 'ctg2')},
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV21', 'cloud metadata_add, no cloud name specified.',
        '/cloud/metadata-add/', form_data={'group': ut_id(gvar, 'ctg1')},
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV21', 'cloud metadata_add, no cloud name specified.',
        '/cloud/metadata-add/', form_data={'metadata_name': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV21', 'cloud metadata_add, no cloud name specified.',
        '/cloud/metadata-add/', form_data={'cloud_name': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV18', 'cloud metadata-add request contained a bad parameter "invalid-unit-test".',
        '/cloud/metadata-add/', form_data={
            'cloud_name': 'invalid-unit-test',
            'metadata_name': 'invalid-unit-test',
            'invalid-unit-test': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV18', 'value specified for "cloud_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        '/cloud/metadata-add/', form_data={
            'cloud_name': 'Invalid-unit-test',
            'metadata_name': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV18', 'value specified for "cloud_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        '/cloud/metadata-add/', form_data={
            'cloud_name': 'invalid-unit-test-',
            'metadata_name': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV18', 'value specified for "cloud_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        '/cloud/metadata-add/', form_data={
            'cloud_name': 'invalid-unit-test!',
            'metadata_name': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV18', 'value specified for "metadata_name" must be all lower case.',
        '/cloud/metadata-add/', form_data={
            'cloud_name': 'invalid-unit-test',
            'metadata_name': 'Invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV18', 'boolean value specified for "enabled" must be one of the following: true, false, yes, no, 1, or 0.',
        '/cloud/metadata-add/', form_data={
            'cloud_name': 'invalid-unit-test',
            'metadata_name': 'invalid-unit-test',
            'enabled': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV18', 'value specified for "mime_type" must be one of the following options: [\'cloud-config\', \'ucernvm-config\'].',
        '/cloud/metadata-add/', form_data={
            'cloud_name': 'invalid-unit-test',
            'metadata_name': 'invalid-unit-test',
            'mime_type': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV18', 'yaml value specified for "metadata (metadata_name)" is invalid - scanner error',
        '/cloud/metadata-add/', form_data={
            'cloud_name': 'invalid-unit-test',
            'metadata_name': 'invalid-unit-test.yaml',
            'metadata': 'foo: somebody said I should put a colon here: so I did'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV19', 'Field \'metadata\' doesn\'t have a default value',
        '/cloud/metadata-add/', form_data={
            'cloud_name': 'invalid-unit-test',
            'metadata_name': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV18', 'value specified for "priority" must be a integer value.',
        '/cloud/metadata-add/', form_data={
            'cloud_name': 'invalid-unit-test',
            'metadata_name': 'invalid-unit-test',
            'metadata': 'invalid-unit-test',
            'priority': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'CV##', 'cloud doesn\'t exist',
        '/cloud/metadata-add/', form_data={
            'cloud_name': 'invalid-unit-test',
            'metadata_name': 'invalid-unit-test',
            'metadata': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 0, None, 'cloud metadata file "{}::{}::{}" successfully added.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc3'), ut_id(gvar, 'cty1')),
        '/cloud/metadata-add/', form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'metadata_name': ut_id(gvar, 'cty1'),
            'metadata': 'foo: somebody said I should put a colon here: so I did'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 0, None, 'cloud metadata file "{}::{}::{}" successfully added.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc3'), ut_id(gvar, 'cty1.yaml')),
        '/cloud/metadata-add/', form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'metadata_name': ut_id(gvar, 'cty1.yaml'),
            'metadata': '- example: yes'
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

if __name__ == "__main__":
    main(None)