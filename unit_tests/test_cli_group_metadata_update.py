from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id, sanity_commands, parameters_commands
from sys import argv

# lno: GV - error code identifier.

def main(gvar):

    # 01 - 14
    sanity_commands(gvar, 'metadata', 'update')

    parameters = {
        # 15 Omit `--metadata-name`.
        # We cannot specify test cases for `--metadata-name` here because it complains that we are not specifying any options to modify.
        '--metadata-name': {'valid': ut_id(gvar, 'clm2'), 'test_cases': {}, 'mandatory': True},
        # 16
        '--metadata-enabled': {'valid': 0, 'test_cases': {'invalid-unit-test': 'value specified for "enabled" must be one of the following: true, false, yes, no, 1, or 0.'}},
        # 17
        '--metadata-mime-type': {'valid': 'cloud-config', 'test_cases': {'invalid-unit-test': 'value specified for "mime_type" must be one of the following options: [\'cloud-config\', \'ucernvm-config\'].'}},
        # 18
        '--metadata-priority': {'valid': 0, 'test_cases': {'invalid-unit-test': 'value specified for "priority" must be an integer value.'}}
    }

    parameters_commands(gvar, 'metadata', 'update', ut_id(gvar, 'clg1'), ut_id(gvar, 'clu3'), parameters)

    # 19
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: job-cores',
        ['metadata', 'update', '-jc', 'invalid-unit-test', '-g', ut_id(gvar, 'clg1'),  '-su', ut_id(gvar, 'clu3')]
    )

    # 20
    execute_csv2_command(
        gvar, 1, None, 'group metadata-update value specified for "metadata_name" must not be the empty string.',
        ['metadata', 'update', '-mn', '', '-me', '0', '-su', ut_id(gvar, 'clu3')]
    )

    # 21 Attempt to update metadata that does not exist.
    execute_csv2_command(
        gvar, 1, None, 'the request did not match any rows.',
        ['metadata', 'update', '-mn', 'invalid-unit-test', '-me', '0', '-su', ut_id(gvar, 'clu3')]
    )

    # 22 Fail to specify any fields to update.
    execute_csv2_command(
        gvar, 1, None, 'requires at least one option to modify.',
        ['metadata', 'update', '-mn', ut_id(gvar, 'clm2'), '-su', ut_id(gvar, 'clu3')]
    )

    # 23
    execute_csv2_command(
        gvar, 0, None, 'file "{}::{}" successfully  updated.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clm2')),
        ['metadata', 'update', '-mn', ut_id(gvar, 'clm2'), '--metadata-enabled', 'true', '--metadata-mime-type', 'ucernvm-config', '--metadata-priority', '1', '-su', ut_id(gvar, 'clu3')]
    )

if __name__ == "__main__":
    main(initialize_csv2_request(selections=argv[1] if len(argv) > 1 else ''))
