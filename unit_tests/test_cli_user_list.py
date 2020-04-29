from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id, sanity_commands, table_commands
from sys import argv

# lno: UV - error code identifier.

USER_LIST_COLUMNS = ['Username', 'Common Name', 'Active Group', 'User Groups', 'Username', 'Not In Groups', 'Super User', 'Joined']

def main(gvar):
    # 01 - 14
    sanity_commands(gvar, 'user', 'list')

    # 15
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: group-option',
        ['user', 'list', '-go', 'invalid-unit-test', '-g', ut_id(gvar, 'clg1')]
    )

    # 16
    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['user', 'list', '-un', 'invalid-unit-test']
    )

    # 17
    execute_csv2_command(
        gvar, 0, None, 'Rows: 1',
        ['user', 'list', '-un', ut_id(gvar, 'clu3')]
    )

    # 18
    execute_csv2_command(
        gvar, 0, None, 'user list, 1. Users: keys=username, columns=cert_cn,active_group,user_groups,available_groups,is_superuser,join_date',
        ['user', 'list', '-VC']
    )

    # 19 - 25
    table_commands(gvar, 'user', 'list', ut_id(gvar, 'clg1'), ut_id(gvar, 'clu4'), {'Users': USER_LIST_COLUMNS})

    # 26
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'clu4'), ut_id(gvar, 'clg1')),
        ['user', 'list'],
        expected_list='Users', expected_columns=set(USER_LIST_COLUMNS)
    )

if __name__ == "__main__":
    main(initialize_csv2_request(selections=argv[1] if len(argv) > 1 else ''))
