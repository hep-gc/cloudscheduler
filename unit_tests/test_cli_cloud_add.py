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

    # 1
    execute_csv2_command(
        gvar, 1, None, 'No action specified for object "cloud"',
        ['cloudscheduler', 'cloud']
    )

    # 2
    execute_csv2_command(
        gvar, 1, None, 'Invalid action "invalid-unit-test" for object "cloud"',
        ['cloudscheduler', 'cloud', 'invalid-unit-test']
    )
    
    # 3 No longer works because cloudscheduler prompts you for a web address if you specify an unknown server
    execute_csv2_command(
        gvar, 1, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'cloud', '-s', 'invalid-unit-test']
    )
    
    # 4
    execute_csv2_command(
        gvar, 1, None, 'No action specified for object "cloud"; use -h or -H for help.',
        ['cloudscheduler', 'cloud', '-s', 'unit-test-un']
    )

    # 5
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler cloud".',
        ['cloudscheduler', 'cloud', '-h']
    )

    # 6
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'cloud', '-H']
    )

    #### ADD ####
    # 7
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'add']
    )

    # 8
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'cloud', 'add', '-xx', 'yy']
    )

    # 9
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: metadata-mime-type',
        ['cloudscheduler', 'cloud', 'add', '-mmt', 'invalid-unit-test']
    )

    # 10
    execute_csv2_command(
        gvar, 1, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'cloud', 'add', '-s', 'invalid-unit-test']
    )

    # 11
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'add', '-s', 'unit-test-un']
    )

    # 12
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler cloud add".',
        ['cloudscheduler', 'cloud', 'add', '-h']
    )

    # 13
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'cloud', 'add', '-H']
    )

    # 14
    execute_csv2_command(
        gvar, 1, None, 'Expose API requested',
        ['cloudscheduler', 'cloud', 'add', '-xA']
    )

    # 15
    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'cloud', 'add', '-g', 'invalid-unit-test']
    )

    # 16
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'add', '-g', ut_id(gvar, 'clg1')]
    )

    # 17
    execute_csv2_command(
        gvar, 1, 'CV', r'value specified for "cloud_type" must be one of the following options: [\'amazon\', \'azure\', \'google\', \'local\', \'opennebula\', \'openstack\'].',
        ['cloudscheduler', 'cloud', 'add',
            '-cn', ut_id(gvar, 'cli-invalid-unit-test'),
            '-ca', 'invalid-unit-test',
            '-cpw', 'invalid-unit-test',
            '-cP', 'invalid-unit-test',
            '-cr', 'invalid-unit-test',
            '-ct', 'invalid-unit-test',
            '-cU', 'invalid-unit-test'
        ]
    )

    # 18
    execute_csv2_command(
        gvar, 1, 'CV', r'Data too long for column \'cloud_name\' at row 1',
        ['cloudscheduler', 'cloud', 'add',
            '-cn', 'thiscloudnameistoolongtobeinserted',
            '-ca', 'invalid-unit-test',
            '-cpw', 'invalid-unit-test',
            '-cP', 'invalid-unit-test',
            '-cr', 'invalid-unit-test',
            '-ct', 'local',
            '-cU', 'invalid-unit-test'
        ]
    )

    # 19
    execute_csv2_command(
        gvar, 1, 'CV', 'value specified for "cloud_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        ['cloudscheduler', 'cloud', 'add',
            '-cn', 'Invalid-unit-test',
            '-ca', 'invalid-unit-test',
            '-cpw', 'invalid-unit-test',
            '-cP', 'invalid-unit-test',
            '-cr', 'invalid-unit-test',
            '-ct', 'local',
            '-cU', 'invalid-unit-test'
        ]
    )

    # 20
    execute_csv2_command(
        gvar, 1, 'CV', 'value specified for "cloud_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        ['cloudscheduler', 'cloud', 'add',
            '-cn', 'invalid-unit-test-',
            '-ca', 'invalid-unit-test',
            '-cpw', 'invalid-unit-test',
            '-cP', 'invalid-unit-test',
            '-cr', 'invalid-unit-test',
            '-ct', 'local',
            '-cU', 'invalid-unit-test'
        ]
    )

    # 21
    execute_csv2_command(
        gvar, 1, 'CV', 'value specified for "cloud_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        ['cloudscheduler', 'cloud', 'add',
            '-cn', 'invalid!unit?test',
            '-ca', 'invalid-unit-test',
            '-cpw', 'invalid-unit-test',
            '-cP', 'invalid-unit-test',
            '-cr', 'invalid-unit-test',
            '-ct', 'local',
            '-cU', 'invalid-unit-test'
        ]
    )

    # 22
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
            '-vc', 'invalid-unit-test'
        ]
    )

    # 23
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
            '-vr', 'invalid-unit-test'
        ]
    )

    # 24
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
            '-ce', 'invalid-unit-test'
        ]
    )

    # 25
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
            '-vka', 'invalid-unit-test'
        ]
    )

    # 26
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
            '-csp', 'invalid-unit-test'
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
            '-gme', 'invalid-unit-test'
        ]
    )

    # 28
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
            '-gme', '{},invalid-unit-test'.format(ut_id(gvar, 'clm2'))
        ]
    )

    # 29
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
            '-gme', ut_id(gvar, 'clm2')
        ]
    )

    # 30
    execute_csv2_command(
        gvar, 1, 'CV', 'Duplicate entry \\\'{}-{}\\\' for key \\\'PRIMARY\\\''.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc10')),
        ['cloudscheduler', 'cloud', 'add',
            '-cn', ut_id(gvar, 'clc10'),
            '-ca', 'command-line-cloud-ten.ca',
            '-cpw', 'command-line-cloud-ten',
            '-cP', 'command-line-cloud-ten',
            '-cr', 'clc10-r',
            '-ct', 'local',
            '-cU', ut_id(gvar, 'clc10')
        ]
    )

    # 31
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
            '-gme', ut_id(gvar, 'clm2,clm2.yaml')
        ]
    )

    # 32
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
            '-s', 'unit-test',
            '-g', ut_id(gvar, 'clg1'),
        ]
    )

if __name__ == "__main__":
    main(None)
