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
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'cloud', 'list', '-xx', 'yy', '-s', 'unit-test-un']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: metadata-mime-type',
        ['cloudscheduler', 'cloud', 'list', '-mmt', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'user settings for server "invalid-unit-test" does not contain a URL value.',
        ['cloudscheduler', 'cloud', 'list', '-s', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'list', '-s', 'unit-test-un']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler cloud list".',
        ['cloudscheduler', 'cloud', 'list', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'cloud', 'list', '-H']
    )

    execute_csv2_command(
        gvar, 0, None, 'Expose API requested',
        ['cloudscheduler', 'cloud', 'list', '-xA']
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'cloud', 'list', '-g', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test-un, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'test'), ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'cloud', 'list', '-g', ut_id(gvar, 'clg1')]
    )

    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, '')[:-1], ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'cloud', 'list', '-s', 'unit-test', '-g', ut_id(gvar, 'clg1')]
    )

    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test-un, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'test'), ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'cloud', 'list', '-s', 'unit-test-un']
    )

    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'cloud', 'list', '-cn', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Rows: 1',
        ['cloudscheduler', 'cloud', 'list', '-cn', ut_id(gvar, 'clc2')]
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'list', '-ok'],
        list='Clouds', columns=['Group', 'Cloud']
    )

    execute_csv2_command(
        gvar, 0, None, 'cloud list, table #1 columns: keys=group_name,cloud_name, columns=',
        ['cloudscheduler', 'cloud', 'list', '-VC']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'list', '-NV'],
        list='Clouds', columns=['Cores', 'RAM', 'Group', 'Cloud', 'Enabled', 'URL', 'Project Domain', 'Project', 'User Domain', 'User', 'Region', 'Spot Price', 'Cloud Type', 'Keyname', 'Control', 'Max', 'VM', 'Metadata', 'Flavor', 'Image', 'Keep Alive', 'Group Exclusions', 'Filenames', 'CA Certificate']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'list', '-V', 'enabled,authurl'],
        list='Clouds', columns=['Group', 'Cloud', 'Enabled', 'URL']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'list'],
        list='Clouds', columns=['Group', 'Cloud', 'Enabled', 'URL']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'list', '-r'],
        list='Clouds', columns=['Key', 'Value']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'list', '-V', ''],
        list='Clouds', columns=['Cores', 'RAM', 'Group', 'Cloud', 'Enabled', 'URL', 'Project Domain', 'Project', 'User Domain', 'User', 'Region', 'Spot Price', 'Cloud Type', 'Keyname', 'Control', 'Max', 'VM', 'Metadata', 'Flavor', 'Image', 'Keep Alive', 'Group Exclusions', 'Filenames', 'CA Certificate']
    )

if __name__ == "__main__":
    main(None)
