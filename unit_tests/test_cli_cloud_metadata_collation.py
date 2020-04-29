from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id, sanity_commands
from sys import argv

# lno: CV - error code identifier.

def main(gvar):

    # 01 - 14
    sanity_commands(gvar, 'cloud', 'metadata-collation')

    # 15
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: metadata-mime-type',
        ['cloud', 'metadata-collation', '-mmt', 'invalid-unit-test', '-g', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu3')]
    )

    # 16
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'clu3'), ut_id(gvar, 'clg1')),
        ['cloud', 'metadata-collation', '-NV', '-su', ut_id(gvar, 'clu3')],
        expected_list='Clouds/Metadata Collation', expected_columns={'Group', 'Cloud', 'Metadata Filename', 'Priority', 'Type'}
    )

    # 17 Specify a cloud that does not exist.
    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloud', 'metadata-collation', '--cloud-name', 'invalid-unit-test', '-su', ut_id(gvar, 'clu3')],
        expected_list='Clouds/Metadata Collation'
    )

    # 18
    execute_csv2_command(
        gvar, 0, None, ut_id(gvar, 'clm2'),
        ['cloud', 'metadata-collation', '--cloud-name', ut_id(gvar, 'clc2'), '-su', ut_id(gvar, 'clu3')],
        expected_list='Clouds/Metadata Collation'
    )

    # 19
    execute_csv2_command(
        gvar, 0, None, 'cloud metadata-collation, 1. Clouds/Metadata Collation: keys=group_name,cloud_name,metadata_name, columns=priority,type',
        ['cloud', 'metadata-collation', '--view-columns', '-su', ut_id(gvar, 'clu3')]
    )

    # Other common table options are tested in cli_alias_list.

if __name__ == "__main__":
    main(initialize_csv2_request(selections=argv[1] if len(argv) > 1 else ''))
