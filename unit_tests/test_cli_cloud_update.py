from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id
import sys

# lno: CV - error code identifier.

def main(gvar, user_secret):
    if not gvar:
        gvar = {}
        if len(sys.argv) > 1:
            initialize_csv2_request(gvar, sys.argv[0], selections=sys.argv[1])
        else:
            initialize_csv2_request(gvar, sys.argv[0])

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'update']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'cloud', 'update', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: metadata-mime-type',
        ['cloudscheduler', 'cloud', 'update', '-mmt', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'user settings for server "invalid-unit-test" does not contain a URL value.',
        ['cloudscheduler', 'cloud', 'update', '-s', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'update', '-s', 'unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler cloud update".',
        ['cloudscheduler', 'cloud', 'update', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'cloud', 'update', '-H']
    )

    execute_csv2_command(
        gvar, 1, None, 'Expose API requested',
        ['cloudscheduler', 'cloud', 'update', '-xA']
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'cloud', 'update', '-g', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'update', '-g', ut_id(gvar, 'clg1')]
    )

    execute_csv2_command(
        gvar, 1, None, 'the request did not match any rows.',
        ['cloudscheduler', 'cloud', 'update', '-cn', 'invalid-unit-test', '-ca', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'requires at least one option to modify.',
        ['cloudscheduler', 'cloud', 'update', '-cn', ut_id(gvar, 'clc2')]
    )

    execute_csv2_command(
        gvar, 1, 'CV35', 'value specified for "ram_ctl" must be a integer value.',
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-vr', 'invalid-unit-test'
        ]
    )
    
    execute_csv2_command(
        gvar, 1, 'CV35', 'value specified for "cores_ctl" must be a integer value.',
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-vc', 'invalid-unit-test'
        ]
    )

    execute_csv2_command(
        gvar, 1, 'CV35', 'boolean value specified for "enabled" must be one of the following: true, false, yes, no, 1, or 0.',
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-ce', 'invalid-unit-test'
        ]
    )

    execute_csv2_command(
        gvar, 1, 'CV35', 'value specified for "vm_keep_alive" must be a integer value.',
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-vka', 'invalid-unit-test'
        ]
    )

    execute_csv2_command(
        gvar, 1, 'CV35', 'value specified for "spot_price" must be a integer value.',
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-csp', 'invalid-unit-test'
        ]
    )

    execute_csv2_command(
        gvar, 1, 'CV03', 'cloud update, "{}" failed - specified metadata_name "invalid-unit-test" does not exist.'.format(ut_id(gvar, 'clc2')),
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-gme', 'invalid-unit-test'
        ]
    )

    execute_csv2_command(
        gvar, 1, 'CV35', 'value specified for "metadata_option" must be one of the following options: [\\\'add\\\', \\\'delete\\\'].',
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-gmo', 'invalid-unit-test'
        ]
    )

    execute_csv2_command(
        gvar, 1, 'CV23', 'cloud update must specify at least one field to update.',
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-gmo', 'add'
        ]
    )

    execute_csv2_command(
        gvar, 1, 'CV23', 'cloud update must specify at least one field to update.',
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-gmo', 'delete'
        ]
    )

    execute_csv2_command(
        gvar, 1, 'CV03', 'cloud update, "{}" failed - specified metadata_name "invalid-unit-test" does not exist.'.format(ut_id(gvar, 'clc2')),
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-gme', 'invalid-unit-test',
            '-gmo', 'add'
        ]
    )

    execute_csv2_command(
        gvar, 1, 'CV03', 'cloud update, "{}" failed - specified metadata_name "invalid-unit-test" does not exist.'.format(ut_id(gvar, 'clc2')),
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-gme', 'invalid-unit-test',
            '-gmo', 'delete'
        ]
    )

    execute_csv2_command(
        gvar, 1, 'CV03', 'cloud update, "{}" failed - specified metadata_name "invalid-unit-test" does not exist.'.format(ut_id(gvar, 'clc2')),
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-gme', '{},invalid-unit-test'.format(ut_id(gvar, 'clm2'))
        ]
    )

    execute_csv2_command(
        gvar, 1, 'CV03', 'cloud update, "{}" failed - specified metadata_name "invalid-unit-test" does not exist.'.format(ut_id(gvar, 'clc2')),
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-gme', '{},invalid-unit-test'.format(ut_id(gvar, 'clm2')),
            '-gmo', 'add'
        ]
    )

    execute_csv2_command(
        gvar, 1, 'CV03', 'cloud update, "{}" failed - specified metadata_name "invalid-unit-test" does not exist.'.format(ut_id(gvar, 'clc2')),
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-gme', '{},invalid-unit-test'.format(ut_id(gvar, 'clm2')),
            '-gmo', 'delete'
        ]
    )

    execute_csv2_command(
        gvar, 0, None, 'cloud "{}::{}" successfully updated.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2')),
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-ca', 'command-line-cloud-update.ca',
            '-cpw', 'command-line-cloud-update',
            '-cp', 'command-line-cloud-update',
            '-cr', 'clc10-r',
            '-ct', 'local',
            '-cu', ut_id(gvar, 'clc10'),
            '-ce', 'no',
            '-vka', '10',
            '-vi', 'command-line-cloud-update',
            '-vf', 'command-line-cloud-update',
            '-csp', '10',
            '-gme', ut_id(gvar, 'clm2')
        ]
    )

    execute_csv2_command(
        gvar, 0, None, 'cloud "{}::{}" successfully updated.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2')),
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-ca', 'command-line-cloud-update.ca',
            '-cpw', 'command-line-cloud-update',
            '-cp', 'command-line-cloud-update',
            '-cr', 'clc10-r',
            '-ct', 'local',
            '-cu', ut_id(gvar, 'clc10'),
            '-gme', ut_id(gvar, 'clm2.yaml,clm3')
        ]
    )

    execute_csv2_command(
        gvar, 0, None, 'cloud "{}::{}" successfully updated.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2')),
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-ca', 'command-line-cloud-update.ca',
            '-cpw', 'command-line-cloud-update',
            '-cp', 'command-line-cloud-update',
            '-cr', 'clc10-r',
            '-ct', 'local',
            '-cu', ut_id(gvar, 'clc10'),
            '-gme', ut_id(gvar, 'clm2.yaml'),
            '-gmo', 'delete'
        ]
    )

    execute_csv2_command(
        gvar, 0, None, 'cloud "{}::{}" successfully updated.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2')),
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-ca', 'command-line-cloud-update.ca',
            '-cpw', 'command-line-cloud-update',
            '-cp', 'command-line-cloud-update',
            '-cr', 'clc10-r',
            '-ct', 'local',
            '-cu', ut_id(gvar, 'clc10'),
            '-gme', ut_id(gvar, 'clm2,clm3'),
            '-gmo', 'delete'
        ]
    )

    execute_csv2_command(
        gvar, 0, None, 'cloud "{}::{}" successfully updated.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2')),
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-ca', 'command-line-cloud-update.ca',
            '-cpw', 'command-line-cloud-update',
            '-cp', 'command-line-cloud-update',
            '-cr', 'clc10-r',
            '-ct', 'local',
            '-cu', ut_id(gvar, 'clc10'),
            '-gme', ut_id(gvar, 'clm2'),
            '-gmo', 'add'
        ]
    )

    execute_csv2_command(
        gvar, 0, None, 'cloud "{}::{}" successfully updated.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2')),
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-ca', 'command-line-cloud-update.ca',
            '-cpw', 'command-line-cloud-update',
            '-cp', 'command-line-cloud-update',
            '-cr', 'clc10-r',
            '-ct', 'local',
            '-cu', ut_id(gvar, 'clc10'),
            '-gme', ut_id(gvar, 'clm2.yaml,clm3'),
            '-gmo', 'add'
        ]
    )

if __name__ == "__main__":
    main(None)
