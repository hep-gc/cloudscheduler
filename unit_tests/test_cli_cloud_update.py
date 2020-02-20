from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id
from sys import argv

# lno: CV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)

    # 01
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'update', '-su', ut_id(gvar, 'clu4')]
    )

    # 02
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'cloud', 'update', '-xx', 'yy', '-su', ut_id(gvar, 'clu4')]
    )

    # 03
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: metadata-mime-type',
        ['cloudscheduler', 'cloud', 'update', '-mmt', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 04
    execute_csv2_command(
        gvar, None, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'cloud', 'update', '-s', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')], timeout=8
    )

    # 05
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'update', '-su', ut_id(gvar, 'clu4')]
    )

    # 06
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler cloud update".',
        ['cloudscheduler', 'cloud', 'update', '-h', '-su', ut_id(gvar, 'clu4')]
    )

    # 07
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'cloud', 'update', '-H', '-su', ut_id(gvar, 'clu4')]
    )

    # 08
    execute_csv2_command(
        gvar, 1, None, 'Expose API requested',
        ['cloudscheduler', 'cloud', 'update', '-xA', '-su', ut_id(gvar, 'clu4')]
    )

    # 09
    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'cloud', 'update', '-g', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 10
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'update', '-g', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu4')]
    )

    # 11
    execute_csv2_command(
        gvar, 1, None, 'cloud update "{}::invalid-unit-test" failed - cloud "{}::invalid-unit-test" does not exist.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'cloud', 'update', '-cn', 'invalid-unit-test', '-ca', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 12
    execute_csv2_command(
        gvar, 1, None, '"cloudscheduler cloud update" requires at least one option to modify.',
        ['cloudscheduler', 'cloud', 'update', '-cn', ut_id(gvar, 'clc2'), '-su', ut_id(gvar, 'clu4')]
    )

    # 13
    execute_csv2_command(
        gvar, 1, 'CV', 'value specified for "ram_ctl" must be an integer value.',
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-vr', 'invalid-unit-test',
            '-su', ut_id(gvar, 'clu4')
        ]
    )
    
    # 14
    execute_csv2_command(
        gvar, 1, 'CV', 'value specified for "cores_ctl" must be an integer value.',
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-vc', 'invalid-unit-test',
            '-su', ut_id(gvar, 'clu4')
        ]
    )

    # 15
    execute_csv2_command(
        gvar, 1, 'CV', 'boolean value specified for "enabled" must be one of the following: true, false, yes, no, 1, or 0.',
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-ce', 'invalid-unit-test',
            '-su', ut_id(gvar, 'clu4')
        ]
    )

    # 16
    execute_csv2_command(
        gvar, 1, 'CV', 'value specified for "vm_keep_alive" must be an integer value.',
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-vka', 'invalid-unit-test',
            '-su', ut_id(gvar, 'clu4')
        ]
    )

    # 17
    execute_csv2_command(
        gvar, 1, 'CV', 'cloud update value specified for "spot_price" must be a floating point value.',
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-csp', 'invalid-unit-test',
            '-su', ut_id(gvar, 'clu4')
        ]
    )

    # 18
    execute_csv2_command(
        gvar, 1, 'CV', 'cloud update, "{}" failed - specified metadata_name "invalid-unit-test" does not exist.'.format(ut_id(gvar, 'clc2')),
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-gme', 'invalid-unit-test',
            '-su', ut_id(gvar, 'clu4')
        ]
    )

    # 19
    execute_csv2_command(
        gvar, 1, 'CV', 'value specified for "metadata_option" must be one of the following options: [\'add\', \'delete\'].',
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-gmo', 'invalid-unit-test',
            '-su', ut_id(gvar, 'clu4')
        ]
    )

    # 20
    execute_csv2_command(
        gvar, 1, 'CV', 'cloud update must specify at least one field to update.',
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-gmo', 'add',
            '-su', ut_id(gvar, 'clu4')
        ]
    )

    # 21
    execute_csv2_command(
        gvar, 1, 'CV', 'cloud update must specify at least one field to update.',
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-gmo', 'delete',
            '-su', ut_id(gvar, 'clu4')
        ]
    )

    # 22
    execute_csv2_command(
        gvar, 1, 'CV', 'cloud update, "{}" failed - specified metadata_name "invalid-unit-test" does not exist.'.format(ut_id(gvar, 'clc2')),
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-gme', 'invalid-unit-test',
            '-gmo', 'add',
            '-su', ut_id(gvar, 'clu4')
        ]
    )

    # 23
    execute_csv2_command(
        gvar, 1, 'CV', 'cloud update, "{}" failed - specified metadata_name "invalid-unit-test" does not exist.'.format(ut_id(gvar, 'clc2')),
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-gme', 'invalid-unit-test',
            '-gmo', 'delete',
            '-su', ut_id(gvar, 'clu4')
        ]
    )

    # 24
    execute_csv2_command(
        gvar, 1, 'CV', 'cloud update, "{}" failed - specified metadata_name "invalid-unit-test" does not exist.'.format(ut_id(gvar, 'clc2')),
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-gme', '{},invalid-unit-test'.format(ut_id(gvar, 'clm2')),
            '-su', ut_id(gvar, 'clu4')
        ]
    )

    # 25
    execute_csv2_command(
        gvar, 1, 'CV', 'cloud update, "{}" failed - specified metadata_name "invalid-unit-test" does not exist.'.format(ut_id(gvar, 'clc2')),
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-gme', '{},invalid-unit-test'.format(ut_id(gvar, 'clm2')),
            '-gmo', 'add',
            '-su', ut_id(gvar, 'clu4')
        ]
    )

    # 26
    execute_csv2_command(
        gvar, 1, 'CV', 'cloud update, "{}" failed - specified metadata_name "invalid-unit-test" does not exist.'.format(ut_id(gvar, 'clc2')),
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-gme', '{},invalid-unit-test'.format(ut_id(gvar, 'clm2')),
            '-gmo', 'delete',
            '-su', ut_id(gvar, 'clu4')
        ]
    )

    # 27
    execute_csv2_command(
        gvar, 0, None, 'cloud "{}::{}" successfully updated.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2')),
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-ce', 'no',
            '-vi', '',
            '-vf', '',
            '-vk', '',
            '-vka', '10',
            '-vn', '',
            '-csp', '10',
            '-gme', ut_id(gvar, 'clm2'),
            '-su', ut_id(gvar, 'clu4')
        ]
    )

    # 28
    execute_csv2_command(
        gvar, 0, None, 'cloud "{}::{}" successfully updated.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2')),
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-gme', ut_id(gvar, 'clm2.yaml,clm3'),
            '-su', ut_id(gvar, 'clu4')
        ]
    )

    # 29
    execute_csv2_command(
        gvar, 0, None, 'cloud "{}::{}" successfully updated.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2')),
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-gme', ut_id(gvar, 'clm2.yaml'),
            '-gmo', 'delete',
            '-su', ut_id(gvar, 'clu4')
        ]
    )

    # 30
    execute_csv2_command(
        gvar, 0, None, 'cloud "{}::{}" successfully updated.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2')),
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-gme', ut_id(gvar, 'clm2,clm3'),
            '-gmo', 'delete',
            '-su', ut_id(gvar, 'clu4')
        ]
    )

    # 31
    execute_csv2_command(
        gvar, 0, None, 'cloud "{}::{}" successfully updated.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2')),
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-gme', ut_id(gvar, 'clm2'),
            '-gmo', 'add',
            '-su', ut_id(gvar, 'clu4')
        ]
    )

    # 32
    execute_csv2_command(
        gvar, 0, None, 'cloud "{}::{}" successfully updated.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2')),
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-gme', ut_id(gvar, 'clm2.yaml,clm3'),
            '-gmo', 'add',
            '-su', ut_id(gvar, 'clu4')
        ]
    )

    # 33
    execute_csv2_command(
        gvar, 0, None, 'cloud "{}::{}" successfully updated.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2')),
        ['cloudscheduler', 'cloud', 'update',
            '-cn', ut_id(gvar, 'clc2'),
            '-gmo', 'add',
            '-g', ut_id(gvar, 'clg1'),
            '-su', ut_id(gvar, 'clu4')
        ]
    )

if __name__ == "__main__":
    main(None)
