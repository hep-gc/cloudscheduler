from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id
from sys import argv

# lno: CV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv2_request(gvar, argv[0])

    # 1
    execute_csv2_command(
        gvar, 1, None, 'No action specified for object "cloud"',
        ['cloudscheduler', 'cloud', '-su', ut_id(gvar, 'clu4')]
    )

    # 2
    execute_csv2_command(
        gvar, 1, None, 'Invalid action "invalid-unit-test" for object "cloud"',
        ['cloudscheduler', 'cloud', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )
    
    # 3
    execute_csv2_command(
        gvar, None, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'cloud', '-s', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')], timeout=8
    )
    
    # 4
    execute_csv2_command(
        gvar, 1, None, 'No action specified for object "cloud"; use -h or -H for help.',
        ['cloudscheduler', 'cloud', '-su', ut_id(gvar, 'clu4')]
    )

    # 5
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler cloud".',
        ['cloudscheduler', 'cloud', '-h', '-su', ut_id(gvar, 'clu4')]
    )

    # 6
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'cloud', '-H', '-su', ut_id(gvar, 'clu4')]
    )

    #### ADD ####
    # 7
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'add', '-su', ut_id(gvar, 'clu4')]
    )

    # 8
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'cloud', 'add', '-xx', 'yy', '-su', ut_id(gvar, 'clu4')]
    )

    # 9
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: metadata-mime-type',
        ['cloudscheduler', 'cloud', 'add', '-mmt', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 10
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'add', '-su', ut_id(gvar, 'clu4')]
    )

    # 11
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler cloud add".',
        ['cloudscheduler', 'cloud', 'add', '-h', '-su', ut_id(gvar, 'clu4')]
    )

    # 12
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'cloud', 'add', '-H', '-su', ut_id(gvar, 'clu4')]
    )

    # 13
    execute_csv2_command(
        gvar, 1, None, 'Expose API requested',
        ['cloudscheduler', 'cloud', 'add', '-xA', '-su', ut_id(gvar, 'clu4')]
    )

    # 14
    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'cloud', 'add', '-g', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 15
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'add', '-g', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu4')]
    )

    # 16
    execute_csv2_command(
        gvar, 1, 'CV', 'value specified for "cloud_type" must be one of the following options: [\'amazon\', \'azure\', \'google\', \'local\', \'opennebula\', \'openstack\'].',
        ['cloudscheduler', 'cloud', 'add',
            '-cn', ut_id(gvar, 'cli-invalid-unit-test'),
            '-ca', 'invalid-unit-test',
            '-cpw', 'invalid-unit-test',
            '-cP', 'invalid-unit-test',
            '-cr', 'invalid-unit-test',
            '-ct', 'invalid-unit-test',
            '-cU', 'invalid-unit-test',
            '-su', ut_id(gvar, 'clu4')
        ]
    )

    # 17
    execute_csv2_command(
        gvar, 1, 'CV', 'Data too long for column \'cloud_name\' at row 1',
        ['cloudscheduler', 'cloud', 'add',
            '-cn', 'thiscloudnameistoolongtobeinserted',
            '-ca', 'invalid-unit-test',
            '-cpw', 'invalid-unit-test',
            '-cP', 'invalid-unit-test',
            '-cr', 'invalid-unit-test',
            '-ct', 'local',
            '-cU', 'invalid-unit-test',
            '-su', ut_id(gvar, 'clu4')
        ]
    )

    # 18
    execute_csv2_command(
        gvar, 1, 'CV', 'value specified for "cloud_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        ['cloudscheduler', 'cloud', 'add',
            '-cn', 'Invalid-unit-test',
            '-ca', 'invalid-unit-test',
            '-cpw', 'invalid-unit-test',
            '-cP', 'invalid-unit-test',
            '-cr', 'invalid-unit-test',
            '-ct', 'local',
            '-cU', 'invalid-unit-test',
            '-su', ut_id(gvar, 'clu4')
        ]
    )

    # 19
    execute_csv2_command(
        gvar, 1, 'CV', 'value specified for "cloud_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        ['cloudscheduler', 'cloud', 'add',
            '-cn', 'invalid-unit-test-',
            '-ca', 'invalid-unit-test',
            '-cpw', 'invalid-unit-test',
            '-cP', 'invalid-unit-test',
            '-cr', 'invalid-unit-test',
            '-ct', 'local',
            '-cU', 'invalid-unit-test',
            '-su', ut_id(gvar, 'clu4')
        ]
    )

    # 20
    execute_csv2_command(
        gvar, 1, 'CV', 'value specified for "cloud_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        ['cloudscheduler', 'cloud', 'add',
            '-cn', 'invalid!unit?test',
            '-ca', 'invalid-unit-test',
            '-cpw', 'invalid-unit-test',
            '-cP', 'invalid-unit-test',
            '-cr', 'invalid-unit-test',
            '-ct', 'local',
            '-cU', 'invalid-unit-test',
            '-su', ut_id(gvar, 'clu4')
        ]
    )

    # 21
    execute_csv2_command(
        gvar, 1, 'CV', 'value specified for "cores_ctl" must be an integer value.',
        ['cloudscheduler', 'cloud', 'add',
            '-cn', ut_id(gvar, 'cli-invalid-unit-test'),
            '-ca', 'invalid-unit-test',
            '-cpw', 'invalid-unit-test',
            '-cP', 'invalid-unit-test',
            '-cr', 'invalid-unit-test',
            '-ct', 'local',
            '-cU', 'invalid-unit-test',
            '-vc', 'invalid-unit-test',
            '-su', ut_id(gvar, 'clu4')
        ]
    )

    # 22
    execute_csv2_command(
        gvar, 1, 'CV', 'value specified for "ram_ctl" must be an integer value.',
        ['cloudscheduler', 'cloud', 'add',
            '-cn', ut_id(gvar, 'cli-invalid-unit-test'),
            '-ca', 'invalid-unit-test',
            '-cpw', 'invalid-unit-test',
            '-cP', 'invalid-unit-test',
            '-cr', 'invalid-unit-test',
            '-ct', 'local',
            '-cU', 'invalid-unit-test',
            '-vr', 'invalid-unit-test',
            '-su', ut_id(gvar, 'clu4')
        ]
    )

    # 23
    execute_csv2_command(
        gvar, 1, 'CV', 'value specified for "enabled" must be one of the following: true, false, yes, no, 1, or 0.',
        ['cloudscheduler', 'cloud', 'add',
            '-cn', ut_id(gvar, 'cli-invalid-unit-test'),
            '-ca', 'invalid-unit-test',
            '-cpw', 'invalid-unit-test',
            '-cP', 'invalid-unit-test',
            '-cr', 'invalid-unit-test',
            '-ct', 'local',
            '-cU', 'invalid-unit-test',
            '-ce', 'invalid-unit-test',
            '-su', ut_id(gvar, 'clu4')
        ]
    )

    # 24
    execute_csv2_command(
        gvar, 1, 'CV', 'value specified for "vm_keep_alive" must be an integer value.',
        ['cloudscheduler', 'cloud', 'add',
            '-cn', ut_id(gvar, 'cli-invalid-unit-test'),
            '-ca', 'invalid-unit-test',
            '-cpw', 'invalid-unit-test',
            '-cP', 'invalid-unit-test',
            '-cr', 'invalid-unit-test',
            '-ct', 'local',
            '-cU', 'invalid-unit-test',
            '-vka', 'invalid-unit-test',
            '-su', ut_id(gvar, 'clu4')
        ]
    )

    # 25
    execute_csv2_command(
        gvar, 1, 'CV', 'cloud add value specified for "spot_price" must be a floating point value.',
        ['cloudscheduler', 'cloud', 'add',
            '-cn', ut_id(gvar, 'cli-invalid-unit-test'),
            '-ca', 'invalid-unit-test',
            '-cpw', 'invalid-unit-test',
            '-cP', 'invalid-unit-test',
            '-cr', 'invalid-unit-test',
            '-ct', 'local',
            '-cU', 'invalid-unit-test',
            '-csp', 'invalid-unit-test',
            '-su', ut_id(gvar, 'clu4')
        ]
    )

    # 26
    execute_csv2_command(
        gvar, 1, 'CV', 'cloud add, "{}" failed - specified metadata_name "invalid-unit-test" does not exist.'.format(ut_id(gvar, 'cli-invalid-unit-test')),
        ['cloudscheduler', 'cloud', 'add',
            '-cn', ut_id(gvar, 'cli-invalid-unit-test'),
            '-ca', 'invalid-unit-test',
            '-cpw', 'invalid-unit-test',
            '-cP', 'invalid-unit-test',
            '-cr', 'invalid-unit-test',
            '-ct', 'local',
            '-cU', 'invalid-unit-test',
            '-gme', 'invalid-unit-test',
            '-su', ut_id(gvar, 'clu4')
        ]
    )

    # 27
    execute_csv2_command(
        gvar, 1, 'CV', 'cloud add, "{}" failed - specified metadata_name "invalid-unit-test" does not exist.'.format(ut_id(gvar, 'cli-invalid-unit-test')),
        ['cloudscheduler', 'cloud', 'add',
            '-cn', ut_id(gvar, 'cli-invalid-unit-test'),
            '-ca', 'invalid-unit-test',
            '-cpw', 'invalid-unit-test',
            '-cP', 'invalid-unit-test',
            '-cr', 'invalid-unit-test',
            '-ct', 'local',
            '-cU', 'invalid-unit-test',
            '-gme', '{},invalid-unit-test'.format(ut_id(gvar, 'clm2')),
            '-su', ut_id(gvar, 'clu4')
        ]
    )

    # 28
    execute_csv2_command(
        gvar, 0, None, 'cloud "{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc10')),
        ['cloudscheduler', 'cloud', 'add',
            '-cn', ut_id(gvar, 'clc10'),
            '-ca', 'command-line-cloud-ten.ca',
            '-cpw', 'command-line-cloud-ten',
            '-cP', 'command-line-cloud-ten',
            '-cr', 'clc10-r',
            '-ct', 'local',
            '-cU', ut_id(gvar, 'clc10'),
            '-ce', 'yes',
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

    # 29
    execute_csv2_command(
        gvar, 1, 'CV', 'Duplicate entry \'{}-{}\' for key \'PRIMARY\''.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc10')),
        ['cloudscheduler', 'cloud', 'add',
            '-cn', ut_id(gvar, 'clc10'),
            '-ca', 'command-line-cloud-ten.ca',
            '-cpw', 'command-line-cloud-ten',
            '-cP', 'command-line-cloud-ten',
            '-cr', 'clc10-r',
            '-ct', 'local',
            '-cU', ut_id(gvar, 'clc10'),
            '-su', ut_id(gvar, 'clu4')
        ]
    )

    # 30
    execute_csv2_command(
        gvar, 0, None, 'cloud "{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc11')),
        ['cloudscheduler', 'cloud', 'add',
            '-cn', ut_id(gvar, 'clc11'),
            '-ca', 'command-line-cloud-11.ca',
            '-cpw', 'command-line-cloud-11',
            '-cP', 'command-line-cloud-11',
            '-cr', 'clc11-r',
            '-ct', 'local',
            '-cU', ut_id(gvar, 'clc11'),
            '-gme', ut_id(gvar, 'clm2,clm2.yaml'),
            '-su', ut_id(gvar, 'clu4')
        ]
    )

    # 31
    execute_csv2_command(
        gvar, 0, None, 'cloud "{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc12')),
        ['cloudscheduler', 'cloud', 'add',
            '-cn', ut_id(gvar, 'clc12'),
            '-ca', 'command-line-cloud-12.ca',
            '-cpw', 'command-line-cloud-12',
            '-cP', 'command-line-cloud-12',
            '-cr', 'clc12-r',
            '-ct', 'local',
            '-cU', ut_id(gvar, 'clc12'),
            '-su', ut_id(gvar, 'clu4')
        ]
    )

if __name__ == "__main__":
    main(None)
