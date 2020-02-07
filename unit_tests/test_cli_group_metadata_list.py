from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id
from sys import argv

# lno: GV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv2_request(gvar, argv[0])

    # 01
    execute_csv2_command(
        gvar, 0, None, 'Active Group/Metadata:',
        ['cloudscheduler', 'metadata', 'list', '-su', ut_id(gvar, 'clu4')]
    )

    # 02
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'metadata', 'list', '-xx', 'yy', '-su', ut_id(gvar, 'clu4')]
    )

    # 03
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: job-cores',
        ['cloudscheduler', 'metadata', 'list', '-jc', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 04
    execute_csv2_command(
        gvar, None, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'metadata', 'list', '-s', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')], timeout=8
    )

    # 05
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'metadata', 'list', '-su', ut_id(gvar, 'clu4')]
    )

    # 06
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler metadata list".',
        ['cloudscheduler', 'metadata', 'list', '-h', '-su', ut_id(gvar, 'clu4')]
    )

    # 07
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'metadata', 'list', '-H', '-su', ut_id(gvar, 'clu4')]
    )

    # 08
    execute_csv2_command(
        gvar, 0, None, 'Expose API requested',
        ['cloudscheduler', 'metadata', 'list', '-xA', '-su', ut_id(gvar, 'clu4')]
    )

    # 09
    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'metadata', 'list', '-g', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 10
    execute_csv2_command(
        gvar, 0, None, 'Active Group/Metadata:',
        ['cloudscheduler', 'metadata', 'list', '-g', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu4')]
    )

    # 11
    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'metadata', 'list', '-mn', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 12
    execute_csv2_command(
        gvar, 0, None, 'Active Group/Metadata:',
        ['cloudscheduler', 'metadata', 'list', '-mn', ut_id(gvar, 'clm2'), '-su', ut_id(gvar, 'clu4')]
    )

    # 13
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'metadata', 'list', '-ok', '-su', ut_id(gvar, 'clu4')],
        expected_list='Active Group/Metadata', columns=['Group', 'Metadata Filename']
    )

    # 14
    execute_csv2_command(
        gvar, 0, None, 'metadata list, 1. Active Group/Metadata: keys=group_name,metadata_name, columns=enabled,priority,mime_type',
        ['cloudscheduler', 'metadata', 'list', '-VC', '-su', ut_id(gvar, 'clu4')]
    )

    # 15
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'metadata', 'list', '-NV', '-su', ut_id(gvar, 'clu4')],
        expected_list='Active Group/Metadata', columns=['Group', 'Metadata Filename', 'Enabled', 'Priority', 'MIME Type']
    )

    # 16
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'metadata', 'list', '-V', 'enabled', '-su', ut_id(gvar, 'clu4')],
        expected_list='Active Group/Metadata', columns=['Group', 'Metadata Filename', 'Enabled']
    )

    # 17
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'metadata', 'list', '-su', ut_id(gvar, 'clu4')],
        expected_list='Active Group/Metadata', columns=['Group', 'Metadata Filename', 'Enabled']
    )

    # 18
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'metadata', 'list', '-r', '-su', ut_id(gvar, 'clu4')],
        expected_list='Active Group/Metadata', columns=['Key', 'Value']
    )

    # 19
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'metadata', 'list', '-V', '', '-su', ut_id(gvar, 'clu4')],
        expected_list='Active Group/Metadata', columns=['Group', 'Metadata Filename', 'Enabled', 'Priority', 'MIME Type']
    )

if __name__ == "__main__":
    main(None)
