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

    execute_csv2_command(
        gvar, 0, None, 'Clouds/Metadata:',
        ['cloudscheduler', 'cloud', 'metadata-list']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'cloud', 'metadata-list', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: metadata-mime-type',
        ['cloudscheduler', 'cloud', 'metadata-list', '-mmt', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'user settings for server "invalid-unit-test" does not contain a URL value.',
        ['cloudscheduler', 'cloud', 'metadata-list', '-s', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'metadata-list', '-s', 'unit-test-un']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler cloud metadata-list".',
        ['cloudscheduler', 'cloud', 'metadata-list', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'cloud', 'metadata-list', '-H']
    )

    execute_csv2_command(
        gvar, 0, None, 'Expose API requested',
        ['cloudscheduler', 'cloud', 'metadata-list', '-xA']
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'cloud', 'metadata-list', '-g', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Clouds/Metadata:',
        ['cloudscheduler', 'cloud', 'metadata-list', '-g', ut_id(gvar, 'clg1')]
    )

    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'cloud', 'metadata-list', '-cn', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Clouds/Metadata:',
        ['cloudscheduler', 'cloud', 'metadata-list', '-cn', ut_id(gvar, 'clc2')]
    )

    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'cloud', 'metadata-list', '-mn', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Clouds/Metadata:',
        ['cloudscheduler', 'cloud', 'metadata-list', '-mn', ut_id(gvar, 'clm2')]
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-mlo\', \'invalid-unit-test\']',
        ['cloudscheduler', 'cloud', 'metadata-list', '-mlo', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test-un, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'test'), ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'cloud', 'metadata-list']
    )

    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, '')[:-1], ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'cloud', 'metadata-list', '-s', 'unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test-un, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'test'), ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'cloud', 'metadata-list', '-s', 'unit-test-un']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'metadata-list', '-ok'],
        list='Clouds/Metadata', columns=['Group', 'Cloud', 'Metadata Filename']
    )

    execute_csv2_command(
        gvar, 0, None, 'cloud metadata-list, table #1 columns: keys=group_name,cloud_name,metadata_name, columns=enabled,priority,mime_type',
        ['cloudscheduler', 'cloud', 'metadata-list', '-VC']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'metadata-list', '-NV'],
        list='Clouds/Metadata', columns=['Group', 'Cloud', 'Metadata Filename', 'Enabled', 'Priority', 'MIME Type']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'metadata-list', '-V', 'endabled'],
        list='Clouds/Metadata', columns=['Group', 'Cloud', 'Metadata Filename']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'metadata-list'],
        list='Clouds/Metadata', columns=['Group', 'Cloud', 'Metadata Filename']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'metadata-list', '-r'],
        list='Clouds/Metadata', columns=['Key', 'Value']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'metadata-list', '-V', ''],
        list='Clouds/Metadata', columns=['Group', 'Cloud', 'Metadata Filename', 'Enabled', 'Priority', 'MIME Type']
    )

if __name__ == "__main__":
    main(None)
