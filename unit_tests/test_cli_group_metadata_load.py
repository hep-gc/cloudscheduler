from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id, sanity_commands, parameters_commands
from sys import argv

# lno: GV - error code identifier.
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
    sanity_commands(gvar, 'metadata', 'load')

    parameters = {
        # 15 Omit `--metadata-name`.
        '--metadata-name': {'valid': 'invalid-unit-test.yaml', 'test_cases': {
            # 16
            '': 'value specified for "metadata_name" must not be the empty string.',
            # 17
            'invalid-unit-Test': 'value specified for "metadata_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 18
            'invalid-unit-test-': 'value specified for "metadata_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 19
            'invalid-unit--test': 'value specified for "metadata_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 20
            'invalid-unit-test!': 'value specified for "metadata_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 21
            'metadata-name-that-is-too-long-for-the-database-test-metadata-name-too-long-error-case': 'Data too long for column \'metadata_name\' at row 1'
        }, 'mandatory': True},
        # 22 Omit `--file-path`.
        '--file-path': {'valid': METADATA_FILEPATH, 'test_cases': {
            # 23
            '': 'The specified metadata file "" does not exist.',
            # 24
            'invalid-unit-test': 'The specified metadata file "invalid-unit-test" does not exist.',
            INVALID_YAML_FILEPATH: 'value specified for "metadata (metadata_name)" is invalid - scanner error'
        }, 'mandatory': True},
        # 25
        '--metadata-enabled': {'valid': 0, 'test_cases': {'invalid-unit-test': 'boolean value specified for "enabled" must be one of the following: true, false, yes, no, 1, or 0.'}},
        # 26
        '--metadata-mime-type': {'valid': 'cloud-config', 'test_cases': {'invalid-unit-test': 'value specified for "mime_type" must be one of the following options: [\'cloud-config\', \'ucernvm-config\'].'}},
        # 27
        '--metadata-priority': {'valid': 0, 'test_cases': {'invalid-unit-test': 'value specified for "priority" must be an integer value.'}}
    }

    parameters_commands(gvar, 'metadata', 'load', ut_id(gvar, 'clg1'), ut_id(gvar, 'clu3'), parameters)

    # 28
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: job-cores',
        ['metadata', 'load', '-jc', 'invalid-unit-test', '-g', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu3')]
    )

    # 29
    execute_csv2_command(
        gvar, 0, None, 'file "{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clm10')),
        ['metadata', 'load', '-f', INVALID_YAML_FILEPATH, '-mn', ut_id(gvar, 'clm10'), '-su', ut_id(gvar, 'clu3')]
    )

    # 30
    execute_csv2_command(
        gvar, 0, None, 'file "{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clm10.yaml')),
        ['metadata', 'load', '-f', METADATA_FILEPATH, '-mn', ut_id(gvar, 'clm10.yaml'), '-su', ut_id(gvar, 'clu3')]
    )

if __name__ == "__main__":
    main(None)
