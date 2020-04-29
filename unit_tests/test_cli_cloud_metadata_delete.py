from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id, sanity_commands, parameters_commands
from sys import argv

# lno: CV - error code identifier.

def main(gvar):

    # 01 - 14
    sanity_commands(gvar, 'cloud', 'metadata-delete')

    parameters = {
        # 15 Attempt without confirmation.
        # 16 Omit `--metadata-name`.
        '--metadata-name': {'valid': ut_id(gvar, 'clm1'), 'test_cases': {
            # 17
            '': 'cloud metadata-delete value specified for "metadata_name" must not be the empty string.',
            # 18
            'invalid-unit-test!': 'cloud metadata-delete value specified for "metadata_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 19
            'invalid-unit-test': 'the request did not match any rows.'
        }, 'mandatory': True},
        # 20 Omit `--cloud-name`.
        '--cloud-name': {'valid': ut_id(gvar, 'clc2'), 'test_cases': {
            # 21
            '': 'cannot delete "{}::::{}", file doesn\'t exist.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clm1')),
            # 22
            'invalid-unit-test': 'cannot delete "{}::invalid-unit-test::{}", file doesn\'t exist.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clm1'))
        }, 'mandatory': True}
    }

    parameters_commands(gvar, 'cloud', 'metadata-delete', ut_id(gvar, 'clg1'), ut_id(gvar, 'clu3'), parameters, requires_confirmation=True)

    # 23
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: metadata-mime-type',
        ['cloud', 'metadata-delete', '-mmt', 'invalid-unit-test', '-su', ut_id(gvar, 'clu3')]
    )

    # 24
    execute_csv2_command(
        gvar, 0, None, 'cloud metadata file "{}::{}::{}" successfully deleted.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2'), ut_id(gvar, 'clm1')),
        ['cloud', 'metadata-delete', '--cloud-name', ut_id(gvar, 'clc2'), '--metadata-name', ut_id(gvar, 'clm1'), '-Y', '-su', ut_id(gvar, 'clu3')]
    )

if __name__ == "__main__":
    main(initialize_csv2_request(selections=argv[1] if len(argv) > 1 else ''))
