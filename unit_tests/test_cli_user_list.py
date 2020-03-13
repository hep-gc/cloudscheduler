from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id
from sys import argv

# lno: UV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)
    #### LIST ####
    # 47
    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['user', 'list', '-g', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 48
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['user', 'list', '-xx', 'yy', '-su', ut_id(gvar, 'clu4')]
    )

    # 49
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: group-option',
        ['user', 'list', '-go', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 50
    execute_csv2_command(
        gvar, None, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['user', 'list', '-s', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')], timeout=8
    )

    # 51
    execute_csv2_command(
        gvar, 0, None, None,
        ['user', 'list', '-su', ut_id(gvar, 'clu4')],
        expected_list='Users', columns=['Username', 'Common Name', 'Active Group', 'User Groups', 'Username', 'Not In Groups', 'Super User', 'Joined']
    )

    # 52
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler user list".',
        ['user', 'list', '-h', '-su', ut_id(gvar, 'clu4')]
    )

    # 53
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['user', 'list', '-H', '-su', ut_id(gvar, 'clu4')]
    )

    # 54
    execute_csv2_command(
        gvar, 0, None, 'Expose API requested',
        ['user', 'list', '-xA', '-su', ut_id(gvar, 'clu4')]
    )

    # 55
    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['user', 'list', '-un', ut_id(gvar, 'cli-invalid-unit-test'), '-su', ut_id(gvar, 'clu4')]
    )

    # 56
    execute_csv2_command(
        gvar, 0, None, 'Rows: 1',
        ['user', 'list', '-un', ut_id(gvar, 'clu1'), '-su', ut_id(gvar, 'clu4')]
    )

    # 57
    execute_csv2_command(
        gvar, 0, None, None,
        ['user', 'list', '-ok', '-su', ut_id(gvar, 'clu4')],
        expected_list='Users', columns=['Username']
    )

    # 58
    execute_csv2_command(
        gvar, 0, None, 'user list, 1. Users: keys=username, columns=cert_cn,active_group,user_groups,available_groups,is_superuser,join_date',
        ['user', 'list', '-VC', '-su', ut_id(gvar, 'clu4')]
    )

    # 59
    execute_csv2_command(
        gvar, 0, None, None,
        ['user', 'list', '-NV', '-su', ut_id(gvar, 'clu4')],
        expected_list='Users', columns=['Username', 'Common Name', 'Active Group', 'User Groups', 'Username', 'Not In Groups', 'Super User', 'Joined']
    )

    # 60
    execute_csv2_command(
        gvar, 0, None, None,
        ['user', 'list', '-V', 'is_superuser', '-su', ut_id(gvar, 'clu4')],
        expected_list='Users', columns=['Username', 'Super User']
    )

    # 61
    execute_csv2_command(
        gvar, 0, None, None,
        ['user', 'list', '-r', '-su', ut_id(gvar, 'clu4')],
        expected_list='Users', columns=['Key', 'Value']
    )

    # 62
    execute_csv2_command(
        gvar, 0, None, None,
        ['user', 'list', '-V', '', '-su', ut_id(gvar, 'clu4')],
        expected_list='Users', columns=['Username', 'Common Name', 'Active Group', 'User Groups', 'Username', 'Not In Groups', 'Super User', 'Joined']
    )

if __name__ == "__main__":
    main(None)
