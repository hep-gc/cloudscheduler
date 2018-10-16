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
        ['cloudscheduler', 'metadata', 'delete']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized',
        ['cloudscheduler', 'metadata', 'delete', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: job-cores',
        ['cloudscheduler', 'metadata', 'delete', '-jc', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'user settings for server "invalid-unit-test" does not contain a URL value.',
        ['cloudscheduler', 'metadata', 'delete', '-mn', 'invalid-unit-test', '-s', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, None,
        ['cloudscheduler', 'metadata', 'delete', '-s', 'unit-test-un']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler metadata delete".',
        ['cloudscheduler', 'metadata', 'delete', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'metadata', 'delete', '-H']
    )

    execute_csv2_command(
        gvar, 1, None, 'Expose API requested',
        ['cloudscheduler', 'metadata', 'delete', '-mn', 'invalid-unit-test', '-xA']
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'metadata', 'delete', '-mn', 'invalid-unit-test', '-g', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'metadata', 'delete', '-g', ut_id(gvar, 'clg1')]
    )

    execute_csv2_command(
        gvar, 1, 'GV31', 'the request did not match any rows.',
        ['cloudscheduler', 'metadata', 'delete', '-mn', 'invalid-unit-test', '-Y']
    )

    execute_csv2_command(
        gvar, 0, None, 'group metadata file "{}::{}" successfully deleted.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clm1')),
        ['cloudscheduler', 'metadata', 'delete', '-mn', ut_id(gvar, 'clm1'), '-Y']
    )

if __name__ == "__main__":
    main(None)
