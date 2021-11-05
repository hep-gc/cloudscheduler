from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id, sanity_commands, table_commands
from sys import argv

# lno: GV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)

    # 01 - 14
    sanity_commands(gvar, 'metadata', 'list')

    # 15
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: job-cores',
        ['metadata', 'list', '-jc', 'invalid-unit-test', '-g', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu3')]
    )

    # 16
    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['metadata', 'list', '-mn', 'invalid-unit-test', '-su', ut_id(gvar, 'clu3')],
        expected_list='Active Group/Metadata'
    )

    # 17
    execute_csv2_command(
        gvar, 0, None, 'Rows: 1',
        ['metadata', 'list', '-mn', ut_id(gvar, 'clm2'), '-su', ut_id(gvar, 'clu3')],
        expected_list='Active Group/Metadata'
    )

    # 18
    execute_csv2_command(
        gvar, 0, None, 'metadata list, 1. Active Group/Metadata: keys=group_name,metadata_name, columns=enabled,priority,mime_type',
        ['metadata', 'list', '-VC', '-su', ut_id(gvar, 'clu3')]
    )

    table_headers = {
        # 19 - 25
        'Active Group/Metadata': ['Group', 'Metadata Filename', 'Enabled', 'Priority', 'MIME Type', 'Checksum']
    }

    table_commands(gvar, 'metadata', 'list', ut_id(gvar, 'clg1'), ut_id(gvar, 'clu3'), table_headers)

if __name__ == "__main__":
    main(None)
