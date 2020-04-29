from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id, sanity_commands
from sys import argv

# lno: GV - error code identifier.

def main(gvar):

    # 01 - 14
    sanity_commands(gvar, 'group', 'list')

    # 15
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'--invalid-unit-test\', \'invalid-unit-test\']',
        ['group', 'list', '--invalid-unit-test', 'invalid-unit-test', '-g', ut_id(gvar, 'clg1')]
    )

    # 16
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: cloud-name',
        ['group', 'list', '-cn', 'invalid-unit-test', '-g', ut_id(gvar, 'clg1')]
    )

    # 17
    execute_csv2_command(
        gvar, 1, None, 'You are not authorized to access object "group";',
        ['group', 'list', '-su', ut_id(gvar, 'clu3')]
    )

    # 18
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'clu4'), ut_id(gvar, 'clg1')),
        ['group', 'list', '-NV'],
        expected_list='Groups', expected_columns={'Group', 'HTCondor', 'FQDN', 'Container Hostname', 'Other Submitters', 'Metadata Filenames'}
    )

    # 19
    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['group', 'list', '-gn', 'invalid-unit-test']
    )

    # 20
    execute_csv2_command(
        gvar, 0, None, 'Rows: 1',
        ['group', 'list', '-gn', ut_id(gvar, 'clg1')]
    )

    # 21
    execute_csv2_command(
        gvar, 0, None, 'group list, 1. Groups: keys=group_name, columns=htcondor_fqdn,htcondor_container_hostname,htcondor_other_submitters,metadata_names',
        ['group', 'list', '-VC']
    )

if __name__ == "__main__":
    main(initialize_csv2_request(selections=argv[1] if len(argv) > 1 else ''))
