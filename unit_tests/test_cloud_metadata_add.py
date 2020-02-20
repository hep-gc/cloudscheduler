from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, sanity_requests, parameters_requests
from sys import argv

# lno: CV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)

    # 01 - 05
    sanity_requests(gvar, '/cloud/metadata-add/', ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctu3'), ut_id(gvar, 'ctg2'), ut_id(gvar, 'ctu1'))

    # 06
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud metadata-add request did not contain mandatory parameters "cloud_name" and "metadata_name".',
        '/cloud/metadata-add/', group=ut_id(gvar, 'ctg1'),
        server_user=ut_id(gvar, 'ctu3')
    )

    PARAMETERS = [
        # 07 Give an invalid parameter.
        # 08 Omit cloud_name.
        ('cloud_name', {
            # 09
            '': 'cloud metadata-add value specified for "cloud_name" must not be the empty string.',
            # 10
            'Invalid-unit-test': 'cloud metadata-add value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 11
            'invalid-unit--test': 'cloud metadata-add value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 12
            'invalid-unit-test-': 'cloud metadata-add value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 13
            'invalid-unit-test!': 'cloud metadata-add value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 14
            'invalid-unit-test': 'cloud name  "invalid-unit-test" does not exist.'
        }, 'invalid-unit-test'),
        # 15 Omit metadata_name.
        ('metadata_name', {
            # 16
            '': 'cloud metadata-add value specified for "metadata_name" must not be the empty string.',
            # 17
            'invalid-unit-test-': 'cloud metadata-add value specified for "metadata_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.'
        }, 'invalid-unit-test'),
        # 18
        ('enabled', {'invalid-unit-test': 'boolean value specified for "enabled" must be one of the following: true, false, yes, no, 1, or 0.'}),
        # 19
        ('mime_type', {'invalid-unit-test': 'value specified for "mime_type" must be one of the following options: [\'cloud-config\', \'ucernvm-config\'].'}),
        # 20
        ('priority', {'invalid-unit-test': 'value specified for "priority" must be an integer value.'})
    ]

    parameters_requests(gvar, '/cloud/metadata-add/', ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctu3'), PARAMETERS)

    # Parameter combinations that do not fit the above pattern.
    # 21
    execute_csv2_request(
        gvar, 1, None, 'Data too long for column \'metadata_name\'',
        '/cloud/metadata-add/', group=(ut_id(gvar, 'ctg1')),
        form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'metadata_name': 'metadata-name-that-is-too-long-for-the-database_____________________',
            'metadata': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3')
    )

    # 22
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud metadata-add yaml value specified for "metadata (metadata_name)" is invalid - scanner error',
        '/cloud/metadata-add/', group=(ut_id(gvar, 'ctg1')),
        form_data={
            'cloud_name': 'invalid-unit-test',
            'metadata_name': 'invalid-unit-test.yaml',
            'metadata': 'invalid: unit: test'
        },
        server_user=ut_id(gvar, 'ctu3')
    )

    # 23
    execute_csv2_request(
        gvar, 1, 'CV', 'Field \'metadata\' doesn\'t have a default value',
        '/cloud/metadata-add/', group=(ut_id(gvar, 'ctg1')),
        form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'metadata_name': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu3')
    )

    # 24 Add metadata properly.
    execute_csv2_request(
        gvar, 0, None, 'cloud metadata file "{}::{}::{}" successfully added.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc3'), ut_id(gvar, 'cty1')),
        '/cloud/metadata-add/', group=(ut_id(gvar, 'ctg1')),
        form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'metadata_name': ut_id(gvar, 'cty1'),
            'metadata': 'unit-test: unit-test'
        },
        server_user=ut_id(gvar, 'ctu3')
    )

    # 25 Attempt to add the metadata added in 23 again.
    execute_csv2_request(
        gvar, 1, 'CV', 'Duplicate entry \'{}-{}-{}\' for key \'PRIMARY\''.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc3'), ut_id(gvar, 'cty1')),
        '/cloud/metadata-add/', group=(ut_id(gvar, 'ctg1')),
        form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'metadata_name': ut_id(gvar, 'cty1'),
            'metadata': 'unit-test: unit-test'
        },
        server_user=ut_id(gvar, 'ctu3')
    )

    # 26 Add YAML metadata properly.
    execute_csv2_request(
        gvar, 0, None, 'cloud metadata file "{}::{}::{}" successfully added.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc3'), ut_id(gvar, 'cty1.yaml')),
        '/cloud/metadata-add/', group=(ut_id(gvar, 'ctg1')),
        form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'metadata_name': ut_id(gvar, 'cty1.yaml'),
            'metadata': '- example: yes'
        },
        server_user=ut_id(gvar, 'ctu3')
    )

if __name__ == "__main__":
    main(None)
