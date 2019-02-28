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

    # 01
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'metadata', 'delete']
    )

    # 02
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized',
        ['cloudscheduler', 'metadata', 'delete', '-xx', 'yy']
    )

    # 03
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: job-cores',
        ['cloudscheduler', 'metadata', 'delete', '-jc', 'invalid-unit-test']
    )

    # 04
    execute_csv2_command(
        gvar, 1, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'metadata', 'delete', '-mn', 'invalid-unit-test', '-s', 'invalid-unit-test']
    )

    # 05
    execute_csv2_command(
        gvar, 1, None, None,
        ['cloudscheduler', 'metadata', 'delete', '-s', 'unit-test-un']
    )

    # 06
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler metadata delete".',
        ['cloudscheduler', 'metadata', 'delete', '-h']
    )

    # 07
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'metadata', 'delete', '-H']
    )

    # 08
    execute_csv2_command(
        gvar, 1, None, 'Expose API requested',
        ['cloudscheduler', 'metadata', 'delete', '-mn', 'invalid-unit-test', '-xA']
    )

    # 09
    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'metadata', 'delete', '-mn', 'invalid-unit-test', '-g', 'invalid-unit-test']
    )

    # 10
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'metadata', 'delete', '-g', ut_id(gvar, 'clg1')]
    )

    # 11
    execute_csv2_command(
        gvar, 1, 'GV31', 'the request did not match any rows.',
        ['cloudscheduler', 'metadata', 'delete', '-mn', 'invalid-unit-test', '-Y']
    )

    # 12
    execute_csv2_command(
        gvar, 0, None, 'group metadata file "{}::{}" successfully deleted.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clm1')),
        ['cloudscheduler', 'metadata', 'delete', '-mn', ut_id(gvar, 'clm1'), '-Y']
    )

if __name__ == "__main__":
    main(None)
