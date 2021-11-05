from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id, sanity_commands
from sys import argv

# lno: CV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)
    
    # 01 - 14
    sanity_commands(gvar, 'cloud', 'metadata-list')

    # 15
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: metadata-mime-type',
        ['cloud', 'metadata-list', '-mmt', 'invalid-unit-test', '-g', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu3')]
    )

    # 16
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloud', 'metadata-list', '-NV', '-su', ut_id(gvar, 'clu3')],
        expected_list='Clouds/Metadata', expected_columns={'Group', 'Cloud', 'Metadata Filename', 'Enabled', 'Priority', 'MIME Type', 'Checksum'}
    )

    # 17
    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloud', 'metadata-list', '--cloud-name', 'valid-unit-test', '-su', ut_id(gvar, 'clu3')],
        expected_list='Clouds/Metadata'
    )
    
    # 18
    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloud', 'metadata-list', '--metadata-name', 'valid-unit-test', '-su', ut_id(gvar, 'clu3')],
        expected_list='Clouds/Metadata'
    )

    # 19
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'clu3'), ut_id(gvar, 'clg1')),
        ['cloud', 'metadata-list', '--cloud-name', ut_id(gvar, 'clc2'), '--metadata-name', ut_id(gvar, 'clm2'), '-su', ut_id(gvar, 'clu3')],
        expected_list='Clouds/Metadata'
    )

    # 20
    execute_csv2_command(
        gvar, 0, None, 'Rows: 1',
        ['cloud', 'metadata-list', '--cloud-name', ut_id(gvar, 'clc2'), '--metadata-name', ut_id(gvar, 'clm2'), '-su', ut_id(gvar, 'clu3')],
        expected_list='Clouds/Metadata'
    )

    # 21
    execute_csv2_command(
        gvar, 0, None, 'cloud metadata-list, 1. Clouds/Metadata: keys=group_name,cloud_name,metadata_name, columns=enabled,priority,mime_type',
        ['cloud', 'metadata-list', '--view-columns', '-su', ut_id(gvar, 'clu3')]
    )

if __name__ == "__main__":
    main(None)
