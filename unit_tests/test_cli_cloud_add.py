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
        gvar, 1, None, 'No action specified for object "cloud"',
        ['cloudscheduler', 'cloud']
    )

    execute_csv2_command(
        gvar, 1, None, 'Invalid action "invalid-unit-test" for object "cloud"',
        ['cloudscheduler', 'cloud', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'user settings for server "invalid-unit-test" does not contain a URL value.',
        ['cloudscheduler', 'cloud', '-s', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'No action specified for object "cloud"; use -h or -H for help.',
        ['cloudscheduler', 'cloud', '-s', 'unit-test-un']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler cloud".',
        ['cloudscheduler', 'cloud', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'cloud', '-H']
    )

    #### ADD ####
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'add']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'cloud', 'add', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: metadata-mime-type',
        ['cloudscheduler', 'cloud', 'add', '-mmt', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'user settings for server "invalid-unit-test" does not contain a URL value.',
        ['cloudscheduler', 'cloud', 'add', '-s', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'add', '-s', 'unit-test-un']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler cloud add".',
        ['cloudscheduler', 'cloud', 'add', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'cloud', 'add', '-H']
    )

    execute_csv2_command(
        gvar, 1, None, 'Expose API requested',
        ['cloudscheduler', 'cloud', 'add', '-xA']
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'cloud', 'add', '-g', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'add', '-g', ut_id(gvar, 'clg1')]
    )

    execute_csv2_command(
        gvar, 1, 'CV01', r'value specified for "cloud_type" must be one of the following options: [\'amazon\', \'azure\', \'google\', \'local\', \'opennebula\', \'openstack\'].',
        ['cloudscheduler', 'cloud', 'add',
            '-cn', ut_id(gvar, 'cli-invalid-unit-test'),
            '-ca', 'invalid-unit-test',
            '-cpw', 'invalid-unit-test',
            '-cp', 'invalid-unit-test',
            '-cr', 'invalid-unit-test',
            '-ct', 'invalid-unit-test',
            '-cu', 'invalid-unit-test'
        ]
    )

    execute_csv2_command(
        gvar, 1, 'CV02', r'Data too long for column \'cloud_name\' at row 1',
        ['cloudscheduler', 'cloud', 'add',
            '-cn', 'thiscloudnameistoolongtobeinserted',
            '-ca', 'invalid-unit-test',
            '-cpw', 'invalid-unit-test',
            '-cp', 'invalid-unit-test',
            '-cr', 'invalid-unit-test',
            '-ct', 'local',
            '-cu', 'invalid-unit-test'
        ]
    )

    execute_csv2_command(
        gvar, 1, 'CV01', 'value specified for "cloud_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        ['cloudscheduler', 'cloud', 'add',
            '-cn', 'Invalid-unit-test',
            '-ca', 'invalid-unit-test',
            '-cpw', 'invalid-unit-test',
            '-cp', 'invalid-unit-test',
            '-cr', 'invalid-unit-test',
            '-ct', 'local',
            '-cu', 'invalid-unit-test'
        ]
    )

    execute_csv2_command(
        gvar, 1, 'CV01', 'value specified for "cloud_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        ['cloudscheduler', 'cloud', 'add',
            '-cn', 'invalid-unit-test-',
            '-ca', 'invalid-unit-test',
            '-cpw', 'invalid-unit-test',
            '-cp', 'invalid-unit-test',
            '-cr', 'invalid-unit-test',
            '-ct', 'local',
            '-cu', 'invalid-unit-test'
        ]
    )

    execute_csv2_command(
        gvar, 1, 'CV01', 'value specified for "cloud_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        ['cloudscheduler', 'cloud', 'add',
            '-cn', 'invalid!unit?test',
            '-ca', 'invalid-unit-test',
            '-cpw', 'invalid-unit-test',
            '-cp', 'invalid-unit-test',
            '-cr', 'invalid-unit-test',
            '-ct', 'local',
            '-cu', 'invalid-unit-test'
        ]
    )

    execute_csv2_command(
        gvar, 1, 'CV01', 'value specified for "cores_ctl" must be an integer value.',
        ['cloudscheduler', 'cloud', 'add',
            '-cn', ut_id(gvar, 'cli-invalid-unit-test'),
            '-ca', 'invalid-unit-test',
            '-cpw', 'invalid-unit-test',
            '-cp', 'invalid-unit-test',
            '-cr', 'invalid-unit-test',
            '-ct', 'local',
            '-cu', 'invalid-unit-test',
            '-vc', 'invalid-unit-test'
        ]
    )

    execute_csv2_command(
        gvar, 1, 'CV01', 'value specified for "ram_ctl" must be an integer value.',
        ['cloudscheduler', 'cloud', 'add',
            '-cn', ut_id(gvar, 'cli-invalid-unit-test'),
            '-ca', 'invalid-unit-test',
            '-cpw', 'invalid-unit-test',
            '-cp', 'invalid-unit-test',
            '-cr', 'invalid-unit-test',
            '-ct', 'local',
            '-cu', 'invalid-unit-test',
            '-vr', 'invalid-unit-test'
        ]
    )

    execute_csv2_command(
        gvar, 1, 'CV01', 'value specified for "enabled" must be one of the following: true, false, yes, no, 1, or 0.',
        ['cloudscheduler', 'cloud', 'add',
            '-cn', ut_id(gvar, 'cli-invalid-unit-test'),
            '-ca', 'invalid-unit-test',
            '-cpw', 'invalid-unit-test',
            '-cp', 'invalid-unit-test',
            '-cr', 'invalid-unit-test',
            '-ct', 'local',
            '-cu', 'invalid-unit-test',
            '-ce', 'invalid-unit-test'
        ]
    )

    execute_csv2_command(
        gvar, 1, 'CV01', 'value specified for "vm_keep_alive" must be an integer value.',
        ['cloudscheduler', 'cloud', 'add',
            '-cn', ut_id(gvar, 'cli-invalid-unit-test'),
            '-ca', 'invalid-unit-test',
            '-cpw', 'invalid-unit-test',
            '-cp', 'invalid-unit-test',
            '-cr', 'invalid-unit-test',
            '-ct', 'local',
            '-cu', 'invalid-unit-test',
            '-vka', 'invalid-unit-test'
        ]
    )

    execute_csv2_command(
        gvar, 1, 'CV01', 'value specified for "spot_price" must be an integer value.',
        ['cloudscheduler', 'cloud', 'add',
            '-cn', ut_id(gvar, 'cli-invalid-unit-test'),
            '-ca', 'invalid-unit-test',
            '-cpw', 'invalid-unit-test',
            '-cp', 'invalid-unit-test',
            '-cr', 'invalid-unit-test',
            '-ct', 'local',
            '-cu', 'invalid-unit-test',
            '-csp', 'invalid-unit-test'
        ]
    )

    execute_csv2_command(
        gvar, 1, 'CV03', 'cloud add, "{}" failed - specified metadata_name "invalid-unit-test" does not exist.'.format(ut_id(gvar, 'cli-invalid-unit-test')),
        ['cloudscheduler', 'cloud', 'add',
            '-cn', ut_id(gvar, 'cli-invalid-unit-test'),
            '-ca', 'invalid-unit-test',
            '-cpw', 'invalid-unit-test',
            '-cp', 'invalid-unit-test',
            '-cr', 'invalid-unit-test',
            '-ct', 'local',
            '-cu', 'invalid-unit-test',
            '-gme', 'invalid-unit-test'
        ]
    )

    execute_csv2_command(
        gvar, 1, 'CV03', 'cloud add, "{}" failed - specified metadata_name "invalid-unit-test" does not exist.'.format(ut_id(gvar, 'cli-invalid-unit-test')),
        ['cloudscheduler', 'cloud', 'add',
            '-cn', ut_id(gvar, 'cli-invalid-unit-test'),
            '-ca', 'invalid-unit-test',
            '-cpw', 'invalid-unit-test',
            '-cp', 'invalid-unit-test',
            '-cr', 'invalid-unit-test',
            '-ct', 'local',
            '-cu', 'invalid-unit-test',
            '-gme', '{},invalid-unit-test'.format(ut_id(gvar, 'clm2'))
        ]
    )

    execute_csv2_command(
        gvar, 0, None, 'cloud "{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc10')),
        ['cloudscheduler', 'cloud', 'add',
            '-cn', ut_id(gvar, 'clc10'),
            '-ca', 'command-line-cloud-ten.ca',
            '-cpw', 'command-line-cloud-ten',
            '-cp', 'command-line-cloud-ten',
            '-cr', 'clc10-r',
            '-ct', 'local',
            '-cu', ut_id(gvar, 'clc10'),
            '-ce', 'yes',
            '-vka', '10',
            '-vi', '',
            '-vf', '',
            '-vn', '',
            '-csp', '10',
            '-gme', ut_id(gvar, 'clm2')
        ]
    )

    execute_csv2_command(
        gvar, 1, 'CV02', 'Duplicate entry \\\'{}-{}\\\' for key \\\'PRIMARY\\\''.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc10')),
        ['cloudscheduler', 'cloud', 'add',
            '-cn', ut_id(gvar, 'clc10'),
            '-ca', 'command-line-cloud-ten.ca',
            '-cpw', 'command-line-cloud-ten',
            '-cp', 'command-line-cloud-ten',
            '-cr', 'clc10-r',
            '-ct', 'local',
            '-cu', ut_id(gvar, 'clc10')
        ]
    )

    execute_csv2_command(
        gvar, 0, None, 'cloud "{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc11')),
        ['cloudscheduler', 'cloud', 'add',
            '-cn', ut_id(gvar, 'clc11'),
            '-ca', 'command-line-cloud-11.ca',
            '-cpw', 'command-line-cloud-11',
            '-cp', 'command-line-cloud-11',
            '-cr', 'clc11-r',
            '-ct', 'local',
            '-cu', ut_id(gvar, 'clc11'),
            '-gme', ut_id(gvar, 'clm2,clm2.yaml')
        ]
    )

    execute_csv2_command(
        gvar, 0, None, 'cloud "{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc12')),
        ['cloudscheduler', 'cloud', 'add',
            '-cn', ut_id(gvar, 'clc12'),
            '-ca', 'command-line-cloud-12.ca',
            '-cpw', 'command-line-cloud-12',
            '-cp', 'command-line-cloud-12',
            '-cr', 'clc12-r',
            '-ct', 'local',
            '-cu', ut_id(gvar, 'clc12'),
            '-s', 'unit-test',
            '-g', ut_id(gvar, 'clg1'),
        ]
    )

if __name__ == "__main__":
    main(None)
