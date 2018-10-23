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
        gvar, 0, None, 'Active Group/Metadata:',
        ['cloudscheduler', 'metadata', 'list']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'metadata', 'list', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: job-cores',
        ['cloudscheduler', 'metadata', 'list', '-jc', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'user settings for server "invalid-unit-test" does not contain a URL value.',
        ['cloudscheduler', 'metadata', 'list', '-s', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'metadata', 'list', '-s', 'unit-test-un']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler metadata list".',
        ['cloudscheduler', 'metadata', 'list', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'metadata', 'list', '-H']
    )

    execute_csv2_command(
        gvar, 0, None, 'Expose API requested',
        ['cloudscheduler', 'metadata', 'list', '-xA']
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'metadata', 'list', '-g', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Active Group/Metadata:',
        ['cloudscheduler', 'metadata', 'list', '-g', ut_id(gvar, 'clg1')]
    )

    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'metadata', 'list', '-mn', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Active Group/Metadata:',
        ['cloudscheduler', 'metadata', 'list', '-mn', ut_id(gvar, 'clm2')]
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'metadata', 'list', '-ok'],
        list='Active Group/Metadata', columns=['Group', 'Metadata Filename']
    )

    execute_csv2_command(
        gvar, 0, None, 'metadata list, table #1 columns: keys=group_name,metadata_name, columns=enabled,priority,mime_type',
        ['cloudscheduler', 'metadata', 'list', '-VC']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'metadata', 'list', '-NV'],
        list='Active Group/Metadata', columns=['Group', 'Metadata Filename', 'Enabled', 'Priority', 'MIME Type']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'metadata', 'list', '-V', 'enabled'],
        list='Active Group/Metadata', columns=['Group', 'Metadata Filename', 'Enabled']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'metadata', 'list'],
        list='Active Group/Metadata', columns=['Group', 'Metadata Filename', 'Enabled']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'metadata', 'list', '-r'],
        list='Active Group/Metadata', columns=['Key', 'Value']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'metadata', 'list', '-V', ''],
        list='Active Group/Metadata', columns=['Group', 'Metadata Filename', 'Enabled', 'Priority', 'MIME Type']
    )

if __name__ == "__main__":
    main(None)
