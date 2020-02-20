from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id
from sys import argv

# lno: MV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)

    # 01
    execute_csv2_command(
        gvar, 1, None, 'No action specified for object "my"',
        ['cloudscheduler', 'my', '-su', ut_id(gvar, 'clu4')]
    )

    # 02
    execute_csv2_command(
        gvar, 1, None, 'Invalid action "invalid-unit-test" for object "my"',
        ['cloudscheduler', 'my', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 03
    execute_csv2_command(
        gvar, None, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'my', '-s', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')], timeout=8
    )

    # 04
    execute_csv2_command(
        gvar, 1, None, 'No action specified for object "my"; use -h or -H for help.',
        ['cloudscheduler', 'my', '-su', ut_id(gvar, 'clu4')]
    )

    # 05
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler my".',
        ['cloudscheduler', 'my', '-h', '-su', ut_id(gvar, 'clu4')]
    )

    # 06
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'my', '-H', '-su', ut_id(gvar, 'clu4')]
    )

    # SETTINGS
    # 07
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'clu4'), ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'my', 'settings', '-su', ut_id(gvar, 'clu4')],
        expected_list='Settings', columns=['Username', 'Cert Common Name', 'Default Group', 'Status', 'Foreign VMs', 'Global Switch', 'Jobs by Target Alias', 'Refresh Interval', 'Slot Detail', 'Slot Flavors']
    )

    # 08
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'my', 'settings', '-xx', 'yy', '-su', ut_id(gvar, 'clu4')]
    )

    # 09
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: metadata-mime-type',
        ['cloudscheduler', 'my', 'settings', '-mmt', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 10
    execute_csv2_command(
        gvar, None, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'my', 'settings', '-s', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')], timeout=8
    )

    # 11
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler my settings".',
        ['cloudscheduler', 'my', 'settings', '-h', '-su', ut_id(gvar, 'clu4')]
    )

    # 12
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'my', 'settings', '-H', '-su', ut_id(gvar, 'clu4')]
    )

    # 13
    execute_csv2_command(
        gvar, 0, None, 'Expose API requested',
        ['cloudscheduler', 'my', 'settings', '-xA', '-su', ut_id(gvar, 'clu4')]
    )

    # 14
    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'my', 'settings', '-g', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 15
    execute_csv2_command(
        gvar, 1, None, 'Error: The following command line arguments were invalid: group',
        ['cloudscheduler', 'my', 'settings', '-g', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu4')]
    )

    # 16
    execute_csv2_command(
        gvar, 1, 'UV', 'user update, value specified for a password is less than 6 characters.',
        ['cloudscheduler', 'my', 'settings', '-upw', 'abc', '-su', ut_id(gvar, 'clu4')]
    )

    # 17
    execute_csv2_command(
        gvar, 1, 'UV', 'user update, value specified for a password is less then 16 characters, and does not contain a mixture of upper, lower, and numerics.',
        ['cloudscheduler', 'my', 'settings', '-upw', 'abcdef', '-su', ut_id(gvar, 'clu4')]
    )

    # 18
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu4')),
        ['cloudscheduler', 'my', 'settings', '-upw', 'Abc123', '-su', ut_id(gvar, 'clu4')]
    )

    # 19
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu4')),
        ['cloudscheduler', 'my', 'settings', '-upw', gvar['user_secret'], '-su', ut_id(gvar, 'clu4'), '-spw', 'Abc123']
    )

if __name__ == '__main__':
    main(None)
