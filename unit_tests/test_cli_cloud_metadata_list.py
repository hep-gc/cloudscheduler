from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id
from sys import argv

# lno: CV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)
    # 01
    execute_csv2_command(
        gvar, 0, None, 'Clouds/Metadata:',
        ['cloudscheduler', 'cloud', 'metadata-list', '-su', ut_id(gvar, 'clu4')]
    )

    # 02
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'cloud', 'metadata-list', '-xx', 'yy', '-su', ut_id(gvar, 'clu4')]
    )

    # 03
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: metadata-mime-type',
        ['cloudscheduler', 'cloud', 'metadata-list', '-mmt', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 04
    execute_csv2_command(
        gvar, None, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'cloud', 'metadata-list', '-s', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')], timeout=8
    )

    # 05
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'metadata-list', '-su', ut_id(gvar, 'clu4')]
    )

    # 06
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler cloud metadata-list".',
        ['cloudscheduler', 'cloud', 'metadata-list', '-h', '-su', ut_id(gvar, 'clu4')]
    )

    # 07
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'cloud', 'metadata-list', '-H', '-su', ut_id(gvar, 'clu4')]
    )

    # 08
    execute_csv2_command(
        gvar, 0, None, 'Expose API requested',
        ['cloudscheduler', 'cloud', 'metadata-list', '-xA', '-su', ut_id(gvar, 'clu4')]
    )

    # 09
    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'cloud', 'metadata-list', '-g', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 10
    execute_csv2_command(
        gvar, 0, None, 'Clouds/Metadata:',
        ['cloudscheduler', 'cloud', 'metadata-list', '-g', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu4')]
    )

    # 11
    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'cloud', 'metadata-list', '-cn', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 12
    execute_csv2_command(
        gvar, 0, None, 'Clouds/Metadata:',
        ['cloudscheduler', 'cloud', 'metadata-list', '-cn', ut_id(gvar, 'clc2'), '-su', ut_id(gvar, 'clu4')]
    )

    # 13
    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'cloud', 'metadata-list', '-mn', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 14
    execute_csv2_command(
        gvar, 0, None, 'Clouds/Metadata:',
        ['cloudscheduler', 'cloud', 'metadata-list', '-mn', ut_id(gvar, 'clm2'), '-su', ut_id(gvar, 'clu4')]
    )

    # 15
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-mlo\', \'invalid-unit-test\']',
        ['cloudscheduler', 'cloud', 'metadata-list', '-mlo', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 16
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'clu4'), ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'cloud', 'metadata-list', '-su', ut_id(gvar, 'clu4')]
    )

    # 17
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'clu4'), ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'cloud', 'metadata-list', '-su', ut_id(gvar, 'clu4')]
    )

    # 18
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'clu4'), ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'cloud', 'metadata-list', '-su', ut_id(gvar, 'clu4')]
    )

    # 19
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'metadata-list', '-ok', '-su', ut_id(gvar, 'clu4')],
        expected_list='Clouds/Metadata', columns=['Group', 'Cloud', 'Metadata Filename']
    )

    # 20
    execute_csv2_command(
        gvar, 0, None, 'cloud metadata-list, 1. Clouds/Metadata: keys=group_name,cloud_name,metadata_name, columns=enabled,priority,mime_type',
        ['cloudscheduler', 'cloud', 'metadata-list', '-VC', '-su', ut_id(gvar, 'clu4')]
    )

    # 21
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'metadata-list', '-NV', '-su', ut_id(gvar, 'clu4')],
        expected_list='Clouds/Metadata', columns=['Group', 'Cloud', 'Metadata Filename', 'Enabled', 'Priority', 'MIME Type']
    )

    # 22
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'metadata-list', '-V', 'endabled', '-su', ut_id(gvar, 'clu4')],
        expected_list='Clouds/Metadata', columns=['Group', 'Cloud', 'Metadata Filename']
    )

    # 23
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'metadata-list', '-su', ut_id(gvar, 'clu4')],
        expected_list='Clouds/Metadata', columns=['Group', 'Cloud', 'Metadata Filename']
    )

    # 24
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'metadata-list', '-r', '-su', ut_id(gvar, 'clu4')],
        expected_list='Clouds/Metadata', columns=['Key', 'Value']
    )

    # 25
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'metadata-list', '-V', '', '-su', ut_id(gvar, 'clu4')],
        expected_list='Clouds/Metadata', columns=['Group', 'Cloud', 'Metadata Filename', 'Enabled', 'Priority', 'MIME Type']
    )

if __name__ == "__main__":
    main(None)
