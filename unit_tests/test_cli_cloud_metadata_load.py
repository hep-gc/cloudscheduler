from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id, sanity_commands, parameters_commands
from sys import argv

# lno: CV - error code identifier.

# Filepath of a file containing valid YAML metadata.
METADATA_FILEPATH = 'ut.yaml'
# Filepath of a file containing text that cannot be parsed as YAML.
INVALID_YAML_FILEPATH = 'notyamlfile.txt'

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)

    # 01 - 14
    sanity_commands(gvar, 'cloud', 'metadata-load')

    parameters = {
        # 15 Omit --cloud-name.
        '--cloud-name': {'valid': ut_id(gvar, 'clc2'), 'test_cases': {
            # 16
            '': 'cloud metadata-add value specified for "cloud_name" must not be the empty string.',
            # 17
            'invalid-unit-test': 'cloud name "invalid-unit-test" does not exist.'
        }, 'mandatory': True},
        # 18 Omit --metadata-name.
        '--metadata-name': {'valid': ut_id(gvar, 'clm2'), 'test_cases': {
            # 19
            '': 'cloud metadata-add value specified for "metadata_name" must not be the empty string.',
            # 20
            'invalid-unit-Test': 'cloud metadata-add value specified for "metadata_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 21
            'invalid-unit-test-': 'cloud metadata-add value specified for "metadata_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 22
            'invalid-unit--test': 'cloud metadata-add value specified for "metadata_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 23
            'invalid-unit-test!': 'cloud metadata-add value specified for "metadata_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 24
            'metadata-name-that-is-too-long-for-the-database-test-metadata-name-too-long-error-case': 'Data too long for column \'metadata_name\''
        }, 'mandatory': True},
        # 25 Omit --file-path.
        '--file-path': {'valid': METADATA_FILEPATH, 'test_cases': {
            # 26
            '': 'The specified metadata file "" does not exist.',
            # 27
            'invalid-unit-test': 'The specified metadata file "invalid-unit-test" does not exist.'
        }, 'mandatory': True},
        # 28
        '--metadata-enabled': {'valid': 0, 'test_cases': {'invalid-unit-test': 'boolean value specified for "enabled" must be one of the following: true, false, yes, no, 1, or 0.'}},
        # 29
        '--metadata-mime-type': {'valid': 'cloud-config', 'test_cases': {'invalid-unit-test': 'value specified for "mime_type" must be one of the following options: [\'cloud-config\', \'ucernvm-config\'].'}},
        # 30
        '--metadata-priority': {'valid': 0, 'test_cases': {'invalid-unit-test': 'value specified for "priority" must be an integer value.'}}
    }

    parameters_commands(gvar, 'cloud', 'metadata-load', ut_id(gvar, 'clg1'), ut_id(gvar, 'clu3'), parameters)

    # 31
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: only-keys',
        ['cloud', 'metadata-load', '-ok', '-g', ut_id(gvar, 'clg1'),'-su', ut_id(gvar, 'clu3')]
    )

    # 32 Attempt to give text not parsable as YAML as YAML metadata.
    execute_csv2_command(
        gvar, 1, 'CV', 'value specified for "metadata (metadata_name)" is invalid - scanner error',
        ['cloud', 'metadata-load', '-cn', ut_id(gvar, 'clc2'), '-f', INVALID_YAML_FILEPATH, '-mn', 'invalid-unit-test.yaml', '-su', ut_id(gvar, 'clu3')]
    )

    # 33 Properly add non-YAML metadata.
    execute_csv2_command(
        gvar, 0, None, 'file "{}::{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2'), ut_id(gvar, 'clm10')),
        ['cloud', 'metadata-load', '-cn', ut_id(gvar, 'clc2'), '-f', INVALID_YAML_FILEPATH, '-mn', ut_id(gvar, 'clm10'), '-su', ut_id(gvar, 'clu3')]
    )

    # 34 Properly add YAML metadata.
    execute_csv2_command(
        gvar, 0, None, 'file "{}::{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2'), ut_id(gvar, 'clm10.yaml')),
        ['cloud', 'metadata-load', '-cn', ut_id(gvar, 'clc2'), '-f', 'ut.yaml', '-mn', ut_id(gvar, 'clm10.yaml'), '-su', ut_id(gvar, 'clu3')]
    )

if __name__ == "__main__":
    main(None)
