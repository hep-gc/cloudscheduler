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
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'delete', '-s', 'unit-test-un']
    )

    # 2
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'cloud', 'delete', '-xx', 'yy']
    )

    # 3
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: metadata-mime-type',
        ['cloudscheduler', 'cloud', 'delete', '-mmt', 'invalid-unit-test']
    )

    # 4
    execute_csv2_command(
        gvar, None, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'cloud', 'delete', '-s', 'invalid-unit-test'], timeout=8
    )

    # 5
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'delete', '-s', 'unit-test-un']
    )

    # 6
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler cloud delete".',
        ['cloudscheduler', 'cloud', 'delete', '-h']
    )

    # 7
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'cloud', 'delete', '-H']
    )

    # 8
    execute_csv2_command(
        gvar, 1, None, 'Expose API requested',
        ['cloudscheduler', 'cloud', 'delete', '-xA']
    )

    # 9
    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'cloud', 'delete', '-g', 'invalid-unit-test']
    )

    # 10
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'delete', '-g', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu4'), '-spw', user_secret]
    )

    # 11
    execute_csv2_command(
        gvar, 1, None, 'cannot delete "invalid-unit-test", cloud doesn\'t exist in group "{}".'.format(ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'cloud', 'delete', '-cn', 'invalid-unit-test', '-g', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu4'), '-spw', user_secret]
    )

    # 12
    execute_csv2_command(
        gvar, 0, None, 'cloud "{}::{}" successfully deleted.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc1')),
        ['cloudscheduler', 'cloud', 'delete', '-cn', ut_id(gvar, 'clc1'), '-Y', '-g', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu4'), '-spw', user_secret]
    )

    # 13
    execute_csv2_command(
        gvar, 0, None, 'cloud "{}::{}" successfully deleted.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc3')),
        ['cloudscheduler', 'cloud', 'delete', '-cn', ut_id(gvar, 'clc3'), '-Y', '-g', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu4'), '-spw', user_secret]
    )

if __name__ == "__main__":
    main(None)
