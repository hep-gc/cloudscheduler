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
    sanity_commands(gvar, 'cloud', 'update')

    parameters = {
        # 15 Omit --cloud-name.
        '--cloud-name': {'valid': ut_id(gvar, 'clc2'), 'test_cases': {
            # 16
            '': 'cloud update value specified for "cloud_name" must not be the empty string.',
            # 17
            'invalid-unit-Test': 'cloud update value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 18
            'invalid-unit-test-': 'cloud update value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 19
            'invalid-unit-test!': 'cloud update value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 20 Specify a cloud that does not exist.
            'invalid-unit-test': 'cloud update "{}::invalid-unit-test" failed - cloud {}::invalid-unit-test does not exist'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clg1'))
        }, 'mandatory': True},
        # 21
        '--cloud-enabled': {'valid': 0, 'test_cases': {'invalid-unit-test': 'boolean value specified for "enabled" must be one of the following: true, false, yes, no, 1, or 0.'}},
        # 22
        '--cloud-spot-price': {'valid': 0, 'test_cases': {'invalid-unit-test': 'cloud update value specified for "spot_price" must be a floating point value.'}},
        # 23
        '--group-metadata-exclusion': {'valid': ut_id(gvar, 'clm2'), 'test_cases': {'invalid-unit-test': 'cloud update, "{}" failed - specified metadata_name "invalid-unit-test" does not exist.'.format(ut_id(gvar, 'clc2'))}},
        # 24
        '--group-metadata-option': {'valid': 'add', 'test_cases': {'invalid-unit-test': 'value specified for "metadata_option" must be one of the following options: [\'add\', \'delete\'].'}},
        # 25
        '--vm-ram': {'valid': 0, 'test_cases': {'invalid-unit-test': 'value specified for "ram_ctl" must be an integer value.'}},
        # 26
        '--vm-cores': {'valid': 0, 'test_cases': {'invalid-unit-test':'value specified for "cores_ctl" must be an integer value.'}},
        # 27
        '--vm-keep-alive': {'valid': 0, 'test_cases': {'invalid-unit-test': 'value specified for "vm_keep_alive" must be an integer value.'}}
    }

    parameters_commands(gvar, 'cloud', 'update', ut_id(gvar, 'clg1'), ut_id(gvar, 'clu3'), parameters)

    # 28
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: metadata-mime-type',
        ['cloud', 'update', '-mmt', 'invalid-unit-test', '-g', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu3')]
    )

    # 29 Ensure that --group-metadata-option by itself does not qualify as a field to update.
    execute_csv2_command(
        gvar, 1, None, 'cloud update must specify at least one field to update.',
        ['cloud', 'update', '-cn', ut_id(gvar, 'clc2'), '-gmo', 'add', '-su', ut_id(gvar, 'clu3')]
    )

    # 30 Ensure that non-existent metadata in a list are still caught.
    execute_csv2_command(
        gvar, 1, 'CV', 'cloud update, "{}" failed - specified metadata_name "invalid-unit-test" does not exist.'.format(ut_id(gvar, 'clc2')),
        ['cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-gme', '{},invalid-unit-test'.format(ut_id(gvar, 'clm2')),
            '-gmo', 'add',
            '-su', ut_id(gvar, 'clu3')
        ]
    )

    # 31
    execute_csv2_command(
        gvar, 0, None, 'cloud "{}::{}" successfully updated.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2')),
        ['cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-ce', 'no',
            '-vi', '',
            '-vf', '',
            '-vk', '',
            '-vka', '10',
            '-vn', '',
            '-csp', '10',
            '-gme', ut_id(gvar, 'clm2'),
            '-su', ut_id(gvar, 'clu3')
        ]
    )

    # 32 Implicitly add metadata.
    execute_csv2_command(
        gvar, 0, None, 'cloud "{}::{}" successfully updated.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2')),
        ['cloud', 'update', '-cn', ut_id(gvar, 'clc2'), '-gme', ut_id(gvar, 'clm2.yaml'), '-su', ut_id(gvar, 'clu3')]
    )

    # 33 Explicitly delete metadata.
    execute_csv2_command(
        gvar, 0, None, 'cloud "{}::{}" successfully updated.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2')),
        ['cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-gme', ut_id(gvar, 'clm2,clm2.yaml'),
            '-gmo', 'delete',
            '-su', ut_id(gvar, 'clu3')
        ]
    )

    # 34 Explicitly add metadata.
    execute_csv2_command(
        gvar, 0, None, 'cloud "{}::{}" successfully updated.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2')),
        ['cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-gme', ut_id(gvar, 'clm2,clm2.yaml'),
            '-gmo', 'add',
            '-su', ut_id(gvar, 'clu3')
        ]
    )

    # 35 Update app credentials
    execute_csv2_command(
        gvar, 0, None, 'cloud "{}::{}" successfully updated.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2')),
        ['cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-cac', gvar['cloud_credentials']['app_credentials']
        ]
    )

    # 35 Update app credentials
    execute_csv2_command(
        gvar, 0, None, 'cloud "{}::{}" successfully updated.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2')),
        ['cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-cas', gvar['cloud_credentials']['app_credentials_secret']
        ]
    )

    # 36 Update userid
    execute_csv2_command(
        gvar, 0, None, 'cloud "{}::{}" successfully updated.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2')),
        ['cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            #'-cac', gvar['cloud_credentials']['app_credentials'],
            #'-cas', gvar['cloud_credentials']['app_credentials_secret'],
            '-ui', gvar['cloud_credentials']['userid']
        ]
    )

if __name__ == "__main__":
    main(None)
