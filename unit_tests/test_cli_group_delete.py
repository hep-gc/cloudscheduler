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

    # 01
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'group', 'delete', '-su', ut_id(gvar, 'clu4')]
    )

    # 02
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized',
        ['cloudscheduler', 'group', 'delete', '-xx', 'yy', '-su', ut_id(gvar, 'clu4')]
    )

    # 03
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: job-cores',
        ['cloudscheduler', 'group', 'delete', '-jc', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 04
    execute_csv2_command(
        gvar, None, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'group', 'delete', '-s', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')], timeout=8
    )

    # 05
    execute_csv2_command(
        gvar, 1, None, 'You are not authorized to access object "group";',
        ['cloudscheduler', 'group', 'delete', '-su', ut_id(gvar, 'clu3')]
    )

    # 06
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'group', 'delete', '-su', ut_id(gvar, 'clu4')]
    )

    # 07
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler group delete".',
        ['cloudscheduler', 'group', 'delete', '-h', '-su', ut_id(gvar, 'clu4')]
    )

    # 08
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'group', 'delete', '-H', '-su', ut_id(gvar, 'clu4')]
    )

    # 09
    execute_csv2_command(
        gvar, 1, None, 'Expose API requested',
        ['cloudscheduler', 'group', 'delete', '-xA', '-su', ut_id(gvar, 'clu4')]
    )

    # 10
    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'group', 'delete', '-g', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 11
    execute_csv2_command(
        gvar, 1, None, 'cannot delete "", group doesn\'t exist.',
        ['cloudscheduler', 'group', 'delete', '-gn', '', '-su', ut_id(gvar, 'clu4')]
    )

    # 12
    execute_csv2_command(
        gvar, 1, None, 'cannot delete "invalid-unit-test", group doesn\'t exist.',
        ['cloudscheduler', 'group', 'delete', '-gn', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 13
    execute_csv2_command(
        gvar, 1, None, 'You are not authorized to access object "group";',
        ['cloudscheduler', 'group', 'delete', '-gn', ut_id(gvar, 'clg3'), '-Y', '-su', ut_id(gvar, 'clu3')]
    )

    # 14
    execute_csv2_command(
        gvar, 0, None, 'group "{}" successfully deleted.'.format(ut_id(gvar, 'clg3')),
        ['cloudscheduler', 'group', 'delete', '-gn', ut_id(gvar, 'clg3'), '-Y', '-su', ut_id(gvar, 'clu4')]
    )

    # 15
    execute_csv2_command(
        gvar, 0, None, 'group "{}" successfully deleted.'.format(ut_id(gvar, 'clg4')),
        ['cloudscheduler', 'group', 'delete', '-gn', ut_id(gvar, 'clg4'), '-Y', '-su', ut_id(gvar, 'clu4')]
    )

if __name__ == "__main__":
    main(None)
