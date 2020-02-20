from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id
from sys import argv

# lno: GV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)

    # 01 The server user for this and a few other group add tests is clu3 (not clu4), because clu3 lacks privileges.
    execute_csv2_command(
        gvar, 1, None, 'You are not authorized to access object "group";',
        ['cloudscheduler', 'group', '-su', ut_id(gvar, 'clu3')]
    )

    # 02
    execute_csv2_command(
        gvar, 1, None, 'No action specified for object "group"',
        ['cloudscheduler', 'group', '-su', ut_id(gvar, 'clu4')]
    )

    # 03
    execute_csv2_command(
        gvar, 1, None, 'Invalid action "invalid-unit-test" for object "group"',
        ['cloudscheduler', 'group', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 04
    execute_csv2_command(
        gvar, None, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'group', '-s', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')], timeout=8
    )

    # 05
    execute_csv2_command(
        gvar, 1, None, 'No action specified for object "group"; use -h or -H for help.',
        ['cloudscheduler', 'group', '-su', ut_id(gvar, 'clu4')]
    )

    # 06
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler group".',
        ['cloudscheduler', 'group', '-h', '-su', ut_id(gvar, 'clu4')]
    )

    # 07
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'group', '-H', '-su', ut_id(gvar, 'clu4')]
    )

    #### ADD ####
    # 08
    execute_csv2_command(
        gvar, 1, None, 'You are not authorized to access object "group";',
        ['cloudscheduler', 'group', 'add', '-su', ut_id(gvar, 'clu3')]
    )
    
    # 09
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'group', 'add', '-su', ut_id(gvar, 'clu4')]
    )

    # 10
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'group', 'add', '-xx', 'yy', '-su', ut_id(gvar, 'clu4')]
    )

    # 11
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
#       gvar, 1, None, 'The following command line arguments were invalid: job-cores',
        ['cloudscheduler', 'group', 'add', '-jc', '3', '-su', ut_id(gvar, 'clu4')]
    )

    # 12
    execute_csv2_command(
        gvar, None, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'group', 'add', '-s', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')], timeout=8
    )

    # 13
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'group', 'add', '-su', ut_id(gvar, 'clu4')]
    )

    # 14
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler group add".',
        ['cloudscheduler', 'group', 'add', '-h', '-su', ut_id(gvar, 'clu4')]
    )

    # 15
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'group', 'add', '-H', '-su', ut_id(gvar, 'clu4')]
    )

    # 16
    execute_csv2_command(
        gvar, 1, None, 'Expose API requested',
        ['cloudscheduler', 'group', 'add', '-xA', '-su', ut_id(gvar, 'clu4')]
    )

    # 17
    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'group', 'add', '-g', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 18
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'group', 'add', '-htcf', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 19
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'group', 'add', '-un', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 20
    execute_csv2_command(
        gvar, 1, 'GV', 'value specified for "group_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        ['cloudscheduler', 'group', 'add', '-gn', '', '-htcf', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 21
    execute_csv2_command(
        gvar, 1, 'GV', 'group add parameter "htcondor_fqdn" contains an empty string which is specifically disallowed.',
        ['cloudscheduler', 'group', 'add', '-gn', ut_id(gvar, 'cli-invalid-unit-test'), '-htcf', '', '-su', ut_id(gvar, 'clu4')]
    )

    # 22
    execute_csv2_command(
        gvar, 1, 'GV', 'value specified for "group_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        ['cloudscheduler', 'group', 'add', '-gn', 'Invalid-Unit-Test', '-htcf', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 23
    execute_csv2_command(
        gvar, 1, 'GV', 'value specified for "group_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        ['cloudscheduler', 'group', 'add', '-gn', 'invalid-unit-test-', '-htcf', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 24
    execute_csv2_command(
        gvar, 1, 'GV', 'value specified for "group_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        ['cloudscheduler', 'group', 'add', '-gn', 'invalid!unit?test', '-htcf', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 25
    execute_csv2_command(
        gvar, 1, 'GV', 'Data too long for column \'group_name\' at row 1',
        ['cloudscheduler', 'group', 'add', '-gn', 'thisisagroupnametoolongtobeinsertedintothedatabasethisisagroupnametoolongtobeinsertedintothedatabasethisisagroupnametoolongtobein', '-htcf', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 26
    execute_csv2_command(
        gvar, 1, None, 'You are not authorized to access object "group";',
        ['cloudscheduler', 'group', 'add', '-gn', ut_id(gvar, 'clg10'), '-htcf', 'command-line-group-10', '-su', ut_id(gvar, 'clu3')]
    )

    # 27
    execute_csv2_command(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'clg10')),
        ['cloudscheduler', 'group', 'add', '-gn', ut_id(gvar, 'clg10'), '-htcf', 'command-line-group-10', '-su', ut_id(gvar, 'clu4')]
    )

    # 28
    execute_csv2_command(
        gvar, 1, 'GV', 'specified user "invalid-unit-test" does not exist.',
        ['cloudscheduler', 'group', 'add', '-gn', ut_id(gvar, 'cli-invalid-unit-test'), '-htcf', 'invalid-unit-test', '-un', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 29
    execute_csv2_command(
        gvar, 1, 'GV', 'group add, "{}" failed - user "{}" was specified twice.'.format(ut_id(gvar, 'cli-invalid-unit-test'), ut_id(gvar, 'clu3')),
        ['cloudscheduler', 'group', 'add', '-gn', ut_id(gvar, 'cli-invalid-unit-test'), '-htcf', 'invalid-unit-test', '-un', ut_id(gvar, 'clu3,clu3'), '-su', ut_id(gvar, 'clu4')]
    )

    # 30
    execute_csv2_command(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'clg11')),
        ['cloudscheduler', 'group', 'add', '-gn', ut_id(gvar, 'clg11'), '-htcf', 'command-line-group-11', '-un', ut_id(gvar, 'clu3'), '-vf', '', '-vi', '', '-vk', '', '-vn', '', '-su', ut_id(gvar, 'clu4')]
    )

if __name__ == "__main__":
    main(None)
