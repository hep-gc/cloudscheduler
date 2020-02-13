from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, sanity_requests, parameters_requests
from sys import argv

# lno: CV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv2_request(gvar, argv[0])

    # 01 - 05
    sanity_requests(gvar, '/cloud/metadata-update/', ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctu3'), ut_id(gvar, 'ctg2'), ut_id(gvar, 'ctu1'))

    # 06
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud metadata-update request did not contain mandatory parameters "cloud_name" and "metadata_name".',
        '/cloud/metadata-update/', group=ut_id(gvar, 'ctg1'),
        server_user=ut_id(gvar, 'ctu3')
    )

    PARAMETERS = [
        # 07 Give an invalid parameter.
        # 08 Omit cloud_name.
        ('cloud_name', {
            # 09
            '': 'cloud metadata-update value specified for "cloud_name" must not be the empty string.',
            # 10
            'Invalid-unit-test': 'cloud metadata-update value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 11
            'invalid-unit-test-': 'cloud metadata-update value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 12
            'invalid-unit-test!': 'cloud metadata-update value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
        }, 'invalid-unit-test'),
        # 13 Omit metadata_name.
        ('metadata_name', {
            # 14
            '': 'cloud metadata-update value specified for "metadata_name" must not be the empty string.',
            # 15
            'invalid-unit-test!': 'cloud metadata-update value specified for "metadata_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.'
        }, 'invalid-unit-test'),
        # 16
        ('enabled', {'invalid-unit-test': 'boolean value specified for "enabled" must be one of the following: true, false, yes, no, 1, or 0.'}),
        # 17
        ('mime_type', {'invalid-unit-test': 'value specified for "mime_type" must be one of the following options: [\'cloud-config\', \'ucernvm-config\'].'}),
        # 18
        ('priority', {'invalid-unit-test': 'value specified for "priority" must be an integer value.'})
    ]

    parameters_requests(gvar, '/cloud/metadata-update/', ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctu3'), PARAMETERS)

    # 19
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud-metadata-update must specify at least one field to update.',
        '/cloud/metadata-update/', group=ut_id(gvar, 'ctg1'),
        form_data={
            'cloud_name': 'invalid-unit-test',
            'metadata_name': 'invalid-unit-test' 
        },
        server_user=ut_id(gvar, 'ctu3')
    )

    # 20 Attempt to update non-existent metadata.
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud metadata-update "grobertson-ctg1::invalid-unit-test::invalid-unit-test" failed - the request did not match any rows.',
        '/cloud/metadata-update/', group=ut_id(gvar, 'ctg1'),
        form_data={
            'cloud_name': 'invalid-unit-test',
            'metadata_name': 'invalid-unit-test',
            # We need to specify at least one field to update.
            'priority': 1
        },
        server_user=ut_id(gvar, 'ctu3')
    )

    # 21 Attempt to give incorrectly formatted YAML metadata.
    execute_csv2_request(
        gvar, 1, 'CV', 'yaml value specified for "metadata (metadata_name)" is invalid - scanner error',
        '/cloud/metadata-update/', group=ut_id(gvar, 'ctg1'),
        form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'metadata_name': ut_id(gvar, 'cty3.yaml'),
            'metadata': 'foo: this is invalid: yaml'
        },
        server_user=ut_id(gvar, 'ctu3')
    )

    # 22 Ensure that YAML formatting is not enforced on all metadata and that correct parameters are accepted.
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
        server_user=ut_id(gvar, 'ctu3')
    )

    # 23 Give correct YAML metadata.
    execute_csv2_request(
        gvar, 0, None, 'cloud metadata file "{}::{}::{}" successfully  updated.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc3'), ut_id(gvar, 'cty3.yaml')),
        '/cloud/metadata-update/', group=ut_id(gvar, 'ctg1'),
        form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'metadata_name': ut_id(gvar, 'cty3.yaml'),
            'metadata': '- foo: this is valid yaml'
        },
        server_user=ut_id(gvar, 'ctu3')
    )

if __name__ == "__main__":
    main(None)
