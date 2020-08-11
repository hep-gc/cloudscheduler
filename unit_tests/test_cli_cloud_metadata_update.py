from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id, sanity_commands, parameters_commands
from sys import argv

# lno: CV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)
    # 01 - 14
    sanity_commands(gvar, 'cloud', 'metadata-update')

    parameters = {
        # 15 Omit --cloud-name.
        '--cloud-name': {'valid': ut_id(gvar, 'clc2'), 'test_cases': {
            # 16
            '': 'cloud metadata-update value specified for "cloud_name" must not be the empty string.',
            # 17
            'invalid-unit-Test': 'cloud metadata-update value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 18
            'invalid-unit-test-': 'cloud metadata-update value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 19
            'invalid-unit-test!': 'cloud metadata-update value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.'
        }, 'mandatory': True},
        # 20 Omit --metadata-name.
        # 21
        '--metadata-name': {'valid': ut_id(gvar, 'clm2'), 'test_cases': {'': 'cloud metadata-update value specified for "metadata_name" must not be the empty string.'}, 'mandatory': True},
        # 22
        '--metadata-enabled': {'valid': 0, 'test_cases': {'invalid-unit-test': 'boolean value specified for "enabled" must be one of the following: true, false, yes, no, 1, or 0.'}},
        # 23
        '--metadata-mime-type': {'valid': 'cloud-config', 'test_cases': {'invalid-unit-test': 'value specified for "mime_type" must be one of the following options: [\'cloud-config\', \'ucernvm-config\'].'}},
        # 24
        '--metadata-priority': {'valid': 0, 'test_cases': {'invalid-unit-test': 'value specified for "priority" must be an integer value.'}}

    }
    
    parameters_commands(gvar, 'cloud', 'metadata-update', ut_id(gvar, 'clg1'), ut_id(gvar, 'clu3'), parameters)

    # 25
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: cloud-project',
        ['cloud', 'metadata-update', '-cP', 'invalid-unit-test', '-su', ut_id(gvar, 'clu3')]
    )

    # 26
    execute_csv2_command(
        gvar, 1, None, 'requires at least one option to modify.',
        ['cloud', 'metadata-update', '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm2'), '-su', ut_id(gvar, 'clu3')]
    )

    # 27
    execute_csv2_command(
        gvar, 1, 'CV', 'the request did not match any rows.',
        ['cloud', 'metadata-update', '-cn', 'invalid-unit-test', '-mn', ut_id(gvar, 'clm2'), '-me', '0', '-su', ut_id(gvar, 'clu3')]
    )

    # 28
    execute_csv2_command(
        gvar, 1, 'CV', 'the request did not match any rows.',
        ['cloud', 'metadata-update', '-cn', ut_id(gvar, 'clc2'), '-mn', 'invalid-unit-test', '-me', '0', '-su', ut_id(gvar, 'clu3')]
    )

    # 29
    execute_csv2_command(
        gvar, 0, None, 'file "{}::{}::{}" successfully  updated.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2'), ut_id(gvar, 'clm2')),
        ['cloud', 'metadata-update', '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm2'), '-me', 1, '-mmt', 'ucernvm-config', '-mp', 10, '-su', ut_id(gvar, 'clu3')]
    )

if __name__ == "__main__":
    main(None)
