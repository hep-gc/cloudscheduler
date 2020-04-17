from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id, sanity_commands, table_commands
from sys import argv

# lno: AV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)

    # 01 - 14
    sanity_commands(gvar, 'alias', 'list')

    # 15
    execute_csv2_command(
        gvar, 0, None, None,
        ['alias', 'list', '-NV', '-g', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu3')],
        expected_list='Aliases', expected_columns={'Group', 'Alias', 'Clouds'}
    )

    # 16
    execute_csv2_command(
        gvar, 0, None, 'alias list, 1. Aliases: keys=group_name,alias_name, columns=clouds\nalias list, 2. Clouds (optional): keys=group_name,cloud_name, columns=',
        ['alias', 'list', '--view-columns', '-g', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu3')]
    )

    table_headers = {
        'Aliases': ['Group', 'Alias', 'Clouds'],
        'Clouds': ['Group', 'Cloud']
    }

    # 17 - 33
    table_commands(gvar, 'alias', 'list', ut_id(gvar, 'clg1'), ut_id(gvar, 'clu3'), table_headers)

if __name__ == '__main__':
    main(None)
