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
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'cloud', 'metadata-collation', '-xx', 'yy', '-s', 'unit-test-un']
    )

    # 2
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: metadata-mime-type',
        ['cloudscheduler', 'cloud', 'metadata-collation', '-mmt', 'invalid-unit-test']
    )

    # 3
    execute_csv2_command(
        gvar, None, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'cloud', 'metadata-collation', '-s', 'invalid-unit-test'], timeout=8
    )

    # 4
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'metadata-collation', '-s', 'unit-test-un']
    )

    # 5
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler cloud metadata-collation".',
        ['cloudscheduler', 'cloud', 'metadata-collation', '-h']
    )

    # 6
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'cloud', 'metadata-collation', '-H']
    )

    # 7
    execute_csv2_command(
        gvar, 0, None, 'Expose API requested',
        ['cloudscheduler', 'cloud', 'metadata-collation', '-xA']
    )

    # 8
    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'cloud', 'metadata-collation', '-g', 'invalid-unit-test']
    )

    # 9
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test-un, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'test'), ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'cloud', 'metadata-collation', '-g', ut_id(gvar, 'clg1')]
    )

    # 10
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, '')[:-1], ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'cloud', 'metadata-collation', '-s', 'unit-test', '-g', ut_id(gvar, 'clg1')]
    )

    # 11
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test-un, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'test'), ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'cloud', 'metadata-collation', '-s', 'unit-test-un']
    )

    # 12
    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'cloud', 'metadata-collation', '-cn', 'invalid-unit-test']
    )

    # 13
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'metadata-collation', '-ok'],
        expected_list='Clouds/Metadata Collation', columns=['Group', 'Cloud', 'Metadata', 'Filename']
    )

    # 14
    execute_csv2_command(
        gvar, 0, None, 'cloud metadata-collation, 1. Clouds/Metadata Collation: keys=group_name,cloud_name,metadata_name, columns=priority,type',
        ['cloudscheduler', 'cloud', 'metadata-collation', '-VC']
    )

    # 15
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'metadata-collation', '-NV'],
        expected_list='Clouds/Metadata Collation', columns=['Group', 'Cloud', 'Metadata', 'Filename', 'Priority', 'Type']
    )
    
    # 16
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'metadata-collation', '-V', 'type'],
        expected_list='Clouds/Metadata Collation', columns=['Group', 'Cloud', 'Metadata', 'Filename', 'Type']
    )

    # 17
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'metadata-collation'],
        expected_list='Clouds/Metadata Collation', columns=['Group', 'Cloud', 'Metadata', 'Filename', 'Type']
    )

    # 18
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'metadata-collation', '-V', ''],
        expected_list='Clouds/Metadata Collation', columns=['Group', 'Cloud', 'Metadata', 'Filename', 'Priority', 'Type']
    )

    # 19
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'metadata-collation', '-r'],
        expected_list='Clouds/Metadata Collation', columns=['Key', 'Value']
    )

if __name__ == "__main__":
    main(None)
