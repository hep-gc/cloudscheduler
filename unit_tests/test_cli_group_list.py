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
        gvar, 1, None, 'The following command line arguments were unrecognized',
        ['cloudscheduler', 'group', 'list', '-xx', 'yy', '-su', ut_id(gvar, 'clu4')]
    )

    # 02
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: cloud-name',
        ['cloudscheduler', 'group', 'list', '-cn', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 03
    execute_csv2_command(
        gvar, None, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'group', 'list', '-s', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')], timeout=8
    )

    # 04
    execute_csv2_command(
        gvar, 1, None, 'You are not authorized to access object "group";',
        ['cloudscheduler', 'group', 'list', '-su', ut_id(gvar, 'clu3')]
    )

    # 05
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'group', 'list', '-su', ut_id(gvar, 'clu4')]
    )

    # 06
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler group list".',
        ['cloudscheduler', 'group', 'list', '-h', '-su', ut_id(gvar, 'clu4')]
    )

    # 07
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'group', 'list', '-H', '-su', ut_id(gvar, 'clu4')]
    )

    # 08
    execute_csv2_command(
        gvar, 0, None, 'Expose API requested',
        ['cloudscheduler', 'group', 'list', '-xA', '-su', ut_id(gvar, 'clu4')]
    )

    # 09
    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'group', 'list', '-g', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 10
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'clu4'), ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'group', 'list', '-g', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu4')]
    )

    # 11
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'clu4'), ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'group', 'list', '-su', ut_id(gvar, 'clu4')]
    )

    # 12
    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'group', 'list', '-gn', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 13
    execute_csv2_command(
        gvar, 0, None, 'Rows: 1',
        ['cloudscheduler', 'group', 'list', '-gn', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu4')]
    )

    # 14
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'group', 'list', '-ok', '-su', ut_id(gvar, 'clu4')],
        expected_list='Groups', columns=['Group']
    )

    # 15
    execute_csv2_command(
        gvar, 0, None, 'group list, 1. Groups: keys=group_name, columns=htcondor_fqdn,htcondor_container_hostname,htcondor_other_submitters,metadata_names',
        ['cloudscheduler', 'group', 'list', '-VC', '-su', ut_id(gvar, 'clu4')]
    )

    # 16
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'group', 'list', '-NV', '-su', ut_id(gvar, 'clu4')],
        expected_list='Groups', columns=['Group', 'HTCondor', 'FQDN', 'Container Hostname', 'Other Submitters', 'Metadata Filenames']
    )

    # 17
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'group', 'list', '-V', 'metadata_names', '-su', ut_id(gvar, 'clu4')],
        expected_list='Groups', columns=['Group', 'Metadata Filenames']
    )

    # 18
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'group', 'list', '-su', ut_id(gvar, 'clu4')],
        expected_list='Groups', columns=['Group', 'Metadata Filenames']
    )

    # 19
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'group', 'list', '-r', '-su', ut_id(gvar, 'clu4')],
        expected_list='Groups', columns=['Key', 'Value']
    )

    # 20
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'group', 'list', '-V', '', '-su', ut_id(gvar, 'clu4')],
        expected_list='Groups', columns=['Group', 'HTCondor', 'FQDN', 'Container Hostname', 'Other Submitters', 'Metadata Filenames']
    )

if __name__ == "__main__":
    main(None)
