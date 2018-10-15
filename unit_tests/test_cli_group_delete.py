from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id
import sys

# lno: GV - error code identifier.

def main(gvar, user_secret):
    if not gvar:
        gvar = {}
        if len(sys.argv) > 1:
            initialize_csv2_request(gvar, sys.argv[0], selections=sys.argv[1])
        else:
            initialize_csv2_request(gvar, sys.argv[0])

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'group', 'delete', '-s', 'unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized',
        ['cloudscheduler', 'group', 'delete', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: job-cores',
        ['cloudscheduler', 'group', 'delete', '-jc', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'user settings for server "invalid-unit-test" does not contain a URL value.',
        ['cloudscheduler', 'group', 'delete', '-s', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'group', 'delete', '-s', 'unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler group delete".',
        ['cloudscheduler', 'group', 'delete', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'group', 'delete', '-H']
    )

    execute_csv2_command(
        gvar, 1, None, 'Expose API requested',
        ['cloudscheduler', 'group', 'delete', '-xA']
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'group', 'delete', '-g', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, r'cannot delete "", group doesn\'t exist.',
        ['cloudscheduler', 'group', 'delete', '-gn', '']
    )

    execute_csv2_command(
        gvar, 1, None, r'cannot delete "invalid-unit-test", group doesn\'t exist.',
        ['cloudscheduler', 'group', 'delete', '-gn', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'You are not authorized to access object "group";',
        ['cloudscheduler', 'group', 'delete', '-gn', ut_id(gvar, 'clg3'), '-Y', '-s', 'unit-test-un']
    )

    execute_csv2_command(
        gvar, 0, None, 'group "{}" successfully deleted.'.format(ut_id(gvar, 'clg3')),
        ['cloudscheduler', 'group', 'delete', '-gn', ut_id(gvar, 'clg3'), '-Y', '-s', 'unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'group "{}" successfully deleted.'.format(ut_id(gvar, 'clg4')),
        ['cloudscheduler', 'group', 'delete', '-gn', ut_id(gvar, 'clg4'), '-Y']
    )

if __name__ == "__main__":
    main(None)