from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id
from sys import argv

# lno: MV - error code identifier.

def main(gvar, user_secret):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv2_request(gvar, argv[0])

    execute_csv2_command(
        gvar, 1, None, 'No action specified for object "my"',
        ['cloudscheduler', 'my']
    )

    execute_csv2_command(
        gvar, 1, None, 'Invalid action "invalid-unit-test" for object "my"',
        ['cloudscheduler', 'my', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'my', '-s', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'No action specified for object "my"; use -h or -H for help.',
        ['cloudscheduler', 'my', '-s', 'unit-test-un']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler my".',
        ['cloudscheduler', 'my', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'my', '-H']
    )

    # SETTINGS
    execute_csv2_command(
        gvar, 1, None, 'Error: "cloudscheduler my settings" requires at least one option to update.',
        ['cloudscheduler', 'my', 'settings']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'my', 'settings', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: metadata-mime-type',
        ['cloudscheduler', 'my', 'settings', '-mmt', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'my', 'settings', '-s', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'Error: "cloudscheduler my settings" requires at least one option to update.',
        ['cloudscheduler', 'my', 'settings', '-s', 'unit-test-un']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler my settings".',
        ['cloudscheduler', 'my', 'settings', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'my', 'settings', '-H']
    )

    execute_csv2_command(
        gvar, 1, None, 'Expose API requested',
        ['cloudscheduler', 'my', 'settings', '-xA']
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'my', 'settings', '-g', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'Error: The following command line arguments were invalid: group',
        ['cloudscheduler', 'my', 'settings', '-g', ut_id(gvar, 'clg1')]
    )

    execute_csv2_command(
        gvar, 1, 'UV15', 'user update, value specified for a password is less than 6 characters.',
        ['cloudscheduler', 'my', 'settings', '-upw', 'abc']
    )

    execute_csv2_command(
        gvar, 1, 'UV15', 'user update, value specified for a password is less then 16 characters, and does not contain a mixture of upper, lower, and numerics.',
        ['cloudscheduler', 'my', 'settings', '-upw', 'abcdef']
    )

    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'test')),
        ['cloudscheduler', 'my', 'settings', '-upw', 'Abc123']
    )

    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'test')),
        ['cloudscheduler', 'my', 'settings', '-upw', user_secret]
    )

