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
    sanity_requests(gvar, '/cloud/metadata-add/', ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctu1'), ut_id(gvar, 'ctg2'), ut_id(gvar, 'ctu2'))

    parameters = {
        # 06 Send GET request.
        # 07 Give an invalid parameter.
        # 08 Omit cloud_name.
        # 09 Give two cloud_names.
        'cloud_name': {'valid': ut_id(gvar, 'ctc2'), 'test_cases': {
            # 10
            '': 'cloud metadata-add value specified for "cloud_name" must not be the empty string.',
            # 11
            'Invalid-unit-test': 'cloud metadata-add value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 12
            'invalid-unit--test': 'cloud metadata-add value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 13
            'invalid-unit-test-': 'cloud metadata-add value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 14
            'invalid-unit-test!': 'cloud metadata-add value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 15
            'invalid-unit-test': 'cloud name  "invalid-unit-test" does not exist.'
        }, 'mandatory': True},
        # 16 Omit metadata_name.
        # 17 Give two metadata_names.
        'metadata_name': {'valid': ut_id(gvar, 'cty4'), 'test_cases': {
            # 18
            '': 'cloud metadata-add value specified for "metadata_name" must not be the empty string.',
            # 19
            'invalid-unit-test-': 'cloud metadata-add value specified for "metadata_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.'
        }, 'mandatory': True},
        # 20
        # 21 Give two enableds.
        'enabled': {'valid': 0, 'test_cases': {'invalid-unit-test': 'boolean value specified for "enabled" must be one of the following: true, false, yes, no, 1, or 0.'}},
        # 22
        # 23 Give two mime_types.
        'mime_type': {'valid': 'cloud-config', 'test_cases': {'invalid-unit-test': 'value specified for "mime_type" must be one of the following options: [\'cloud-config\', \'ucernvm-config\'].'}},
        # 24
        # 25 Give two priorities.
        'priority': {'valid': 0, 'test_cases': {'invalid-unit-test': 'value specified for "priority" must be an integer value.'}}
    }

    parameters_requests(gvar, '/cloud/metadata-add/', ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctu1'), parameters)

    # Parameter combinations that do not fit the above pattern.
    # 26
    execute_csv2_request(
        gvar, 1, None, 'Data too long for column \'metadata_name\'',
        '/cloud/metadata-add/', group=(ut_id(gvar, 'ctg1')),
        form_data={
            'cloud_name': ut_id(gvar, 'ctc2'),
            'metadata_name': 'metadata-name-that-is-too-long-for-the-database_____________________',
            'metadata': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu1')
    )

    # 27 Test that .yaml files are parsed as YAML.
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud metadata-add yaml value specified for "metadata (metadata_name)" is invalid - scanner error',
        '/cloud/metadata-add/', group=(ut_id(gvar, 'ctg1')),
        form_data={
            'cloud_name': 'invalid-unit-test',
            'metadata_name': 'invalid-unit-test.yaml',
            'metadata': 'invalid: unit: test'
        },
        server_user=ut_id(gvar, 'ctu1')
    )

    # 28
    execute_csv2_request(
        gvar, 1, 'CV', 'Field \'metadata\' doesn\'t have a default value',
        '/cloud/metadata-add/', group=(ut_id(gvar, 'ctg1')),
        form_data={
            'cloud_name': ut_id(gvar, 'ctc2'),
            'metadata_name': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'ctu1')
    )

    # 29 Add metadata properly.
    execute_csv2_request(
        gvar, 0, None, 'cloud metadata file "{}::{}::{}" successfully added.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc2'), ut_id(gvar, 'cty4')),
        '/cloud/metadata-add/', group=(ut_id(gvar, 'ctg1')),
        form_data={
            'cloud_name': ut_id(gvar, 'ctc2'),
            'metadata_name': ut_id(gvar, 'cty4'),
            'metadata': 'unit-test: unit-test'
        },
        server_user=ut_id(gvar, 'ctu1')
    )

    # 30 Attempt to add the metadata added in 2 again.
    execute_csv2_request(
        gvar, 1, 'CV', 'Duplicate entry \'{}-{}-{}\' for key \'PRIMARY\''.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc2'), ut_id(gvar, 'cty4')),
        '/cloud/metadata-add/', group=(ut_id(gvar, 'ctg1')),
        form_data={
            'cloud_name': ut_id(gvar, 'ctc2'),
            'metadata_name': ut_id(gvar, 'cty4'),
            'metadata': 'unit-test: unit-test'
        },
        server_user=ut_id(gvar, 'ctu1')
    )

    # 31 Add YAML metadata properly.
    execute_csv2_request(
        gvar, 0, None, 'cloud metadata file "{}::{}::{}" successfully added.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc2'), ut_id(gvar, 'cty4.yaml')),
        '/cloud/metadata-add/', group=(ut_id(gvar, 'ctg1')),
        form_data={
            'cloud_name': ut_id(gvar, 'ctc2'),
            'metadata_name': ut_id(gvar, 'cty4.yaml'),
            'metadata': '- example: yes'
        },
        server_user=ut_id(gvar, 'ctu1')
    )

if __name__ == "__main__":
    main(None)
