from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id
from sys import argv

# lno: CV - error code identifier.

def main(gvar, user_secret):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv2_request(gvar, argv[0])

    # 01
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'update', '-s', 'unit-test-un']
    )

    # 02
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'cloud', 'update', '-xx', 'yy']
    )

    # 03
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: metadata-mime-type',
        ['cloudscheduler', 'cloud', 'update', '-mmt', 'invalid-unit-test']
    )

    # 04
    execute_csv2_command(
        gvar, 1, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'cloud', 'update', '-s', 'invalid-unit-test']
    )

    # 05
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'update', '-s', 'unit-test-un']
    )

    # 06
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler cloud update".',
        ['cloudscheduler', 'cloud', 'update', '-h']
    )

    # 07
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'cloud', 'update', '-H']
    )

    # 08
    execute_csv2_command(
        gvar, 1, None, 'Expose API requested',
        ['cloudscheduler', 'cloud', 'update', '-xA']
    )

    # 09
    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'cloud', 'update', '-g', 'invalid-unit-test']
    )

    # 10
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'update', '-g', ut_id(gvar, 'clg1')]
    )

    # 11
    execute_csv2_command(
        gvar, 1, None, 'the request did not match any rows.',
        ['cloudscheduler', 'cloud', 'update', '-cn', 'invalid-unit-test', '-ca', 'invalid-unit-test']
    )

    # 12
    execute_csv2_command(
        gvar, 1, None, 'cloud update must specify at least one field to update.',
        ['cloudscheduler', 'cloud', 'update', '-cn', ut_id(gvar, 'clc2')]
    )

    # 13
    execute_csv2_command(
        gvar, 1, 'CV35', 'value specified for "ram_ctl" must be an integer value.',
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-vr', 'invalid-unit-test'
        ]
    )
    
    # 14
    execute_csv2_command(
        gvar, 1, 'CV35', 'value specified for "cores_ctl" must be an integer value.',
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-vc', 'invalid-unit-test'
        ]
    )

    # 15
    execute_csv2_command(
        gvar, 1, 'CV35', 'boolean value specified for "enabled" must be one of the following: true, false, yes, no, 1, or 0.',
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-ce', 'invalid-unit-test'
        ]
    )

    # 16
    execute_csv2_command(
        gvar, 1, 'CV35', 'value specified for "vm_keep_alive" must be an integer value.',
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-vka', 'invalid-unit-test'
        ]
    )

    # 17
    execute_csv2_command(
        gvar, 1, 'CV35', 'value specified for "spot_price" must be an integer value.',
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-csp', 'invalid-unit-test'
        ]
    )

    # 18
    execute_csv2_command(
        gvar, 1, 'CV03', 'cloud update, "{}" failed - specified metadata_name "invalid-unit-test" does not exist.'.format(ut_id(gvar, 'clc2')),
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-gme', 'invalid-unit-test'
        ]
    )

    # 19
    execute_csv2_command(
        gvar, 1, 'CV35', 'value specified for "metadata_option" must be one of the following options: [\\\'add\\\', \\\'delete\\\'].',
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-gmo', 'invalid-unit-test'
        ]
    )

    # 20
    execute_csv2_command(
        gvar, 1, 'CV23', 'cloud update must specify at least one field to update.',
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-gmo', 'add'
        ]
    )

    # 21
    execute_csv2_command(
        gvar, 1, 'CV23', 'cloud update must specify at least one field to update.',
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-gmo', 'delete'
        ]
    )

    # 22
    execute_csv2_command(
        gvar, 1, 'CV03', 'cloud update, "{}" failed - specified metadata_name "invalid-unit-test" does not exist.'.format(ut_id(gvar, 'clc2')),
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-gme', 'invalid-unit-test',
            '-gmo', 'add'
        ]
    )

    # 23
    execute_csv2_command(
        gvar, 1, 'CV03', 'cloud update, "{}" failed - specified metadata_name "invalid-unit-test" does not exist.'.format(ut_id(gvar, 'clc2')),
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-gme', 'invalid-unit-test',
            '-gmo', 'delete'
        ]
    )

    # 24
    execute_csv2_command(
        gvar, 1, 'CV03', 'cloud update, "{}" failed - specified metadata_name "invalid-unit-test" does not exist.'.format(ut_id(gvar, 'clc2')),
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-gme', '{},invalid-unit-test'.format(ut_id(gvar, 'clm2'))
        ]
    )

    # 25
    execute_csv2_command(
        gvar, 1, 'CV03', 'cloud update, "{}" failed - specified metadata_name "invalid-unit-test" does not exist.'.format(ut_id(gvar, 'clc2')),
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-gme', '{},invalid-unit-test'.format(ut_id(gvar, 'clm2')),
            '-gmo', 'add'
        ]
    )

    # 26
    execute_csv2_command(
        gvar, 1, 'CV03', 'cloud update, "{}" failed - specified metadata_name "invalid-unit-test" does not exist.'.format(ut_id(gvar, 'clc2')),
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-gme', '{},invalid-unit-test'.format(ut_id(gvar, 'clm2')),
            '-gmo', 'delete'
        ]
    )

    # 27
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
            '-vi', '',
            '-vf', '',
            '-vk', '',
            '-vka', '10',
            '-vn', '',
            '-csp', '10',
            '-gme', ut_id(gvar, 'clm2')
        ]
    )

    # 28
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

    # 29
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

    # 30
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

    # 31
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

    # 32
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

    # 33
    execute_csv2_command(
        gvar, 0, None, 'cloud "{}::{}" successfully updated.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2')),
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-ca', 'command-line-cloud-update2.ca',
            '-cpw', 'command-line-cloud-update2',
            '-cp', 'command-line-cloud-update2',
            '-cr', 'clc10-r',
            '-ct', 'local',
            '-cu', ut_id(gvar, 'clc10'),
            '-gmo', 'add',
            '-g', ut_id(gvar, 'clg1'),
            '-s', 'unit-test',
        ]
    )

if __name__ == "__main__":
    main(None)
