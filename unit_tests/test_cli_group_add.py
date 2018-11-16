from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id
from sys import argv

# lno: GV - error code identifier.

def main(gvar, user_secret):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv2_request(gvar, argv[0])

    execute_csv2_command(
        gvar, 1, None, 'You are not authorized to access object "group";',
        ['cloudscheduler', 'group', '-s', 'unit-test-un']
    )

    execute_csv2_command(
        gvar, 1, None, 'No action specified for object "group"',
        ['cloudscheduler', 'group', '-s', 'unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'Invalid action "invalid-unit-test" for object "group"',
        ['cloudscheduler', 'group', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'user settings for server "invalid-unit-test" does not contain a URL value.',
        ['cloudscheduler', 'group', '-s', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'No action specified for object "group"; use -h or -H for help.',
        ['cloudscheduler', 'group', '-s', 'unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler group".',
        ['cloudscheduler', 'group', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'group', '-H']
    )

    #### ADD ####
    execute_csv2_command(
        gvar, 1, None, 'You are not authorized to access object "group";',
        ['cloudscheduler', 'group', 'add', '-s', 'unit-test-un']
    )
    
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'group', 'add', '-s', 'unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'group', 'add', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: job-cores',
        ['cloudscheduler', 'group', 'add', '-jc', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'user settings for server "invalid-unit-test" does not contain a URL value.',
        ['cloudscheduler', 'group', 'add', '-s', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'group', 'add', '-s', 'unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler group add".',
        ['cloudscheduler', 'group', 'add', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'group', 'add', '-H']
    )

    execute_csv2_command(
        gvar, 1, None, 'Expose API requested',
        ['cloudscheduler', 'group', 'add', '-xA']
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'group', 'add', '-g', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'group', 'add', '-gm', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'group', 'add', '-gn', ut_id(gvar, 'cli-invalid-unit-test')]
    )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'group', 'add', '-un', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'GV01', 'value specified for "group_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        ['cloudscheduler', 'group', 'add', '-gn', '', '-gm', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'GV01', 'group add parameter "condor_central_manager" contains an empty string which is specifically disallowed.',
        ['cloudscheduler', 'group', 'add', '-gn', ut_id(gvar, 'cli-invalid-unit-test'), '-gm', '']
    )

    execute_csv2_command(
        gvar, 1, 'GV01', 'value specified for "group_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        ['cloudscheduler', 'group', 'add', '-gn', 'Invalid-Unit-Test', '-gm', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'GV01', 'value specified for "group_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        ['cloudscheduler', 'group', 'add', '-gn', 'invalid-unit-test-', '-gm', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'GV01', 'value specified for "group_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        ['cloudscheduler', 'group', 'add', '-gn', 'invalid!unit?test', '-gm', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'GV03', r'Data too long for column \'group_name\' at row 1',
        ['cloudscheduler', 'group', 'add', '-gn', 'thisisagroupnametoolongtobeinsertedintothedatabasethisisagroupnametoolongtobeinsertedintothedatabasethisisagroupnametoolongtobein', '-gm', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'You are not authorized to access object "group";',
        ['cloudscheduler', 'group', 'add', '-gn', ut_id(gvar, 'clg10'), '-gm', 'command-line-group-10', '-s', 'unit-test-un']
    )

    execute_csv2_command(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'clg10')),
        ['cloudscheduler', 'group', 'add', '-gn', ut_id(gvar, 'clg10'), '-gm', 'command-line-group-10', '-s', 'unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'GV02', 'specified user "invalid-unit-test" does not exist.',
        ['cloudscheduler', 'group', 'add', '-gn', ut_id(gvar, 'cli-invalid-unit-test'), '-gm', 'invalid-unit-test', '-un', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'GV02', 'group add, "{}" failed - user "{}" was specified twice.'.format(ut_id(gvar, 'cli-invalid-unit-test'), ut_id(gvar, 'clu3')),
        ['cloudscheduler', 'group', 'add', '-gn', ut_id(gvar, 'cli-invalid-unit-test'), '-gm', 'invalid-unit-test', '-un', ut_id(gvar, 'clu3,clu3')]
    )

    execute_csv2_command(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'clg11')),
        ['cloudscheduler', 'group', 'add', '-gn', ut_id(gvar, 'clg11'), '-gm', 'command-line-group-11', '-un', ut_id(gvar, 'clu3'), '-vf', '', '-vi', '', '-vk', '', '-vn', '']
    )

if __name__ == "__main__":
    main(None)