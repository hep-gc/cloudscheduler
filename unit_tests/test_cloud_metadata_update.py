from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, sanity_requests, parameters_requests
from sys import argv

# lno: CV - error code identifier.

def main(gvar):

    # 01 - 05
    sanity_requests(gvar, '/cloud/metadata-update/', ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctu1'), ut_id(gvar, 'ctg2'), ut_id(gvar, 'ctu2'))

    parameters = {
        # 06 Submit a GET request.
        # 07 Give an invalid parameter.
        # 08 Omit cloud_name.
        # 09 Give two cloud_names.
        'cloud_name': {'valid': ut_id(gvar, 'ctc3'), 'test_cases': {
            # 10
            '': 'cloud metadata-update value specified for "cloud_name" must not be the empty string.',
            # 11
            'Invalid-unit-test': 'cloud metadata-update value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 12
            'invalid-unit-test-': 'cloud metadata-update value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 13
            'invalid-unit-test!': 'cloud metadata-update value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.'
        }, 'mandatory': True},
        # 14 Omit metadata_name.
        # 15 Give two metadata_names.
        'metadata_name': {'valid': ut_id(gvar, 'cty3'), 'test_cases': {
            # 16
            '': 'cloud metadata-update value specified for "metadata_name" must not be the empty string.',
            # 17
            'invalid-unit-test!': 'cloud metadata-update value specified for "metadata_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.'
        }, 'mandatory': True},
        # 18
        # 19 Give two enableds.
        'enabled': {'valid': 0, 'test_cases': {'invalid-unit-test': 'boolean value specified for "enabled" must be one of the following: true, false, yes, no, 1, or 0.'}},
        # 20
        # 21 Give two mime_types.
        'mime_type': {'valid': 'cloud-config', 'test_cases': {'invalid-unit-test': 'value specified for "mime_type" must be one of the following options: [\'cloud-config\', \'ucernvm-config\'].'}},
        # 22
        # 23 Give two priorities.
        'priority': {'valid': 0, 'test_cases': {'invalid-unit-test': 'value specified for "priority" must be an integer value.'}}
    }

    parameters_requests(gvar, '/cloud/metadata-update/', ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctu1'), parameters)

    # 24
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud-metadata-update must specify at least one field to update.',
        '/cloud/metadata-update/', group=ut_id(gvar, 'ctg1'),
        form_data={
            'cloud_name': 'invalid-unit-test',
            'metadata_name': 'invalid-unit-test' 
        },
        server_user=ut_id(gvar, 'ctu1')
    )

    # 25 Attempt to update non-existent metadata.
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud metadata-update "{}::invalid-unit-test::invalid-unit-test" failed - the request did not match any rows.'.format(ut_id(gvar, 'ctg1')),
        '/cloud/metadata-update/', group=ut_id(gvar, 'ctg1'),
        form_data={
            'cloud_name': 'invalid-unit-test',
            'metadata_name': 'invalid-unit-test',
            # We need to specify at least one field to update.
            'priority': 1
        },
        server_user=ut_id(gvar, 'ctu1')
    )

    # 26 Attempt to give incorrectly formatted YAML metadata.
    execute_csv2_request(
        gvar, 1, 'CV', 'yaml value specified for "metadata (metadata_name)" is invalid - scanner error',
        '/cloud/metadata-update/', group=ut_id(gvar, 'ctg1'),
        form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'metadata_name': ut_id(gvar, 'cty3.yaml'),
            'metadata': 'foo: this is invalid: yaml'
        },
        server_user=ut_id(gvar, 'ctu1')
    )

    # 27 Ensure that YAML formatting is not enforced on all metadata and that correct parameters are accepted.
    execute_csv2_request(
        gvar, 0, None, 'cloud metadata file "{}::{}::{}" successfully  updated.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc3'), ut_id(gvar, 'cty3')),
        '/cloud/metadata-update/', group=ut_id(gvar, 'ctg1'),
        form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'metadata_name': ut_id(gvar, 'cty3'),
            'metadata': 'foo: this is invalid: yaml',
            'priority': 1,
            'mime_type': 'ucernvm-config',
            'enabled': 'false'
        },
        server_user=ut_id(gvar, 'ctu1')
    )

    # 28 Give correct YAML metadata.
    execute_csv2_request(
        gvar, 0, None, 'cloud metadata file "{}::{}::{}" successfully  updated.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc3'), ut_id(gvar, 'cty3.yaml')),
        '/cloud/metadata-update/', group=ut_id(gvar, 'ctg1'),
        form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'metadata_name': ut_id(gvar, 'cty3.yaml'),
            'metadata': '- foo: this is valid yaml'
        },
        server_user=ut_id(gvar, 'ctu1')
    )

if __name__ == "__main__":
    main(initialize_csv2_request(selections=argv[1] if len(argv) > 1 else ''))
