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
        gvar, 1, None, 'The following command line arguments were unrecognized',
        ['cloudscheduler', 'group', 'list', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: job-cores',
        ['cloudscheduler', 'group', 'list', '-jc', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'user settings for server "invalid-unit-test" does not contain a URL value.',
        ['cloudscheduler', 'group', 'list', '-s', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'You are not authorized to access object "group";',
        ['cloudscheduler', 'group', 'list', '-s', 'unit-test-un']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'group', 'list', '-s', 'unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler group list".',
        ['cloudscheduler', 'group', 'list', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'group', 'list', '-H']
    )

    execute_csv2_command(
        gvar, 0, None, 'Expose API requested',
        ['cloudscheduler', 'group', 'list', '-xA']
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'group', 'list', '-g', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, '')[:-1], ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'group', 'list', '-g', ut_id(gvar, 'clg1')]
    )

    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, '')[:-1], ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'group', 'list']
    )

    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'group', 'list', '-gn', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Rows: 1',
        ['cloudscheduler', 'group', 'list', '-gn', ut_id(gvar, 'clg1')]
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'group', 'list', '-ok'],
        list='Groups', columns=['Group']
    )

    execute_csv2_command(
        gvar, 0, None, 'group list, table #1 columns: keys=group_name, columns=condor_central_manager,metadata_names',
        ['cloudscheduler', 'group', 'list', '-VC']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'group', 'list', '-NV'],
        list='Groups', columns=['Group', 'Central Manager', 'Metadata Filenames']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'group', 'list', '-V', 'metadata_names'],
        list='Groups', columns=['Group', 'Metadata Filenames']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'group', 'list'],
        list='Groups', columns=['Group', 'Metadata Filenames']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'group', 'list', '-r'],
        list='Groups', columns=['Key', 'Value']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'group', 'list', '-V', ''],
        list='Groups', columns=['Group', 'Central Manager', 'Metadata Filenames']
    )

if __name__ == "__main__":
    main(None)