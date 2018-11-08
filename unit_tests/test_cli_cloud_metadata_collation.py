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
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'cloud', 'metadata-collation', '-xx', 'yy', '-s', 'unit-test-un']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: metadata-mime-type',
        ['cloudscheduler', 'cloud', 'metadata-collation', '-mmt', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'user settings for server "invalid-unit-test" does not contain a URL value.',
        ['cloudscheduler', 'cloud', 'metadata-collation', '-s', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'metadata-collation', '-s', 'unit-test-un']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler cloud metadata-collation".',
        ['cloudscheduler', 'cloud', 'metadata-collation', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'cloud', 'metadata-collation', '-H']
    )

    execute_csv2_command(
        gvar, 0, None, 'Expose API requested',
        ['cloudscheduler', 'cloud', 'metadata-collation', '-xA']
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'cloud', 'metadata-collation', '-g', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test-un, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'test'), ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'cloud', 'metadata-collation', '-g', ut_id(gvar, 'clg1')]
    )

    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, '')[:-1], ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'cloud', 'metadata-collation', '-s', 'unit-test', '-g', ut_id(gvar, 'clg1')]
    )

    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test-un, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'test'), ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'cloud', 'metadata-collation', '-s', 'unit-test-un']
    )

    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'cloud', 'metadata-collation', '-cn', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'metadata-collation', '-ok'],
        list='Clouds/Metadata Collation', columns=['Group', 'Cloud', 'Metadata Filename']
    )

    execute_csv2_command(
        gvar, 0, None, 'cloud metadata-collation, table #1 columns: keys=group_name,cloud_name,metadata_name, columns=priority,type',
        ['cloudscheduler', 'cloud', 'metadata-collation', '-VC']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'metadata-collation', '-NV'],
        list='Clouds/Metadata Collation', columns=['Group', 'Cloud', 'Metadata Filename', 'Priority', 'Type']
    )
    
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'metadata-collation', '-V', 'type'],
        list='Clouds/Metadata Collation', columns=['Group', 'Cloud', 'Metadata Filename', 'Type']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'metadata-collation'],
        list='Clouds/Metadata Collation', columns=['Group', 'Cloud', 'Metadata Filename', 'Type']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'metadata-collation', '-V', ''],
        list='Clouds/Metadata Collation', columns=['Group', 'Cloud', 'Metadata Filename', 'Priority', 'Type']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'metadata-collation', '-r'],
        list='Clouds/Metadata Collation', columns=['Key', 'Value']
    )

if __name__ == "__main__":
    main(None)
