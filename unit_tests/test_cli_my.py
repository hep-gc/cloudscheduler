from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id, sanity_commands, table_commands
from sys import argv

# lno: MV - error code identifier.

MY_SETTINGS_COLUMNS = ['Username', 'Cert Common Name', 'Default Group', 'Status', 'Foreign VMs', 'Global Switch', 'Jobs by Target Alias', 'Refresh Interval', 'Slot Detail', 'Slot Flavors']

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)

    # 01 - 13
    sanity_commands(gvar, 'my')

    #### SETTINGS ####
    # 14 - 27
    sanity_commands(gvar, 'my', 'settings')

    # 28 - 34
    # `my settings` rejects `--group`.
    table_commands(gvar, 'my', 'settings', '', ut_id(gvar, 'clu3'), {'Settings': MY_SETTINGS_COLUMNS})

    # 35
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'clu3'), ut_id(gvar, 'clg1')),
        ['my', 'settings', '-su', ut_id(gvar, 'clu3')],
        expected_list='Settings', expected_columns=set(MY_SETTINGS_COLUMNS)
    )

    # 36
    execute_csv2_command(
        gvar, 1, None, 'Error: The following command line arguments were invalid: group',
        ['my', 'settings', '-g', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu3')]
    )

    # We cannot use `parameters_commands()` here because it specifies a group in each request, and `my settings` rejects `--group`.
    # 37 Give a password that is too short.
    execute_csv2_command(
        gvar, 1, 'UV', 'user update, value specified for a password is less than 6 characters.',
        ['my', 'settings', '-upw', 'abc', '-su', ut_id(gvar, 'clu3')]
    )

    # 38 Give a password that is too weak.
    execute_csv2_command(
        gvar, 1, 'UV', 'user update, value specified for a password is less then 16 characters, and does not contain a mixture of upper, lower, and numerics.',
        ['my', 'settings', '-upw', 'abcdef', '-su', ut_id(gvar, 'clu3')]
    )

    # I tried to test `--user-password ???` here, but it somehow caused terminal input to be invisible after the tests had ran. I think this is because the CLI uses `getpass.getpass()` to get the password.

    # 39
    execute_csv2_command(
        gvar, 1, None, 'value specified for "default_group" must not be the empty string.',
        ['my', 'settings', '--group-name', '', '-su', ut_id(gvar, 'clu3')]
    )

    # 40
    execute_csv2_command(
        gvar, 1, None, 'unable to update default - user is not a member of the specified group (invalid-unit-test).',
        ['my', 'settings', '--group-name', 'invalid-unit-test', '-su', ut_id(gvar, 'clu3')]
    )

    # 41
    execute_csv2_command(
        gvar, 1, None, 'boolean value specified for "flag_show_foreign_global_vms" must be one of the following: true, false, yes, no, 1, or 0.',
        ['my', 'settings', '--show-foreign-vms', 'invalid-unit-test', '-su', ut_id(gvar, 'clu3')]
    )

    # 42
    execute_csv2_command(
        gvar, 1, None, 'boolean value specified for "flag_global_status" must be one of the following: true, false, yes, no, 1, or 0.',
        ['my', 'settings', '--show-global-status', 'invalid-unit-test', '-su', ut_id(gvar, 'clu3')]
    )

    # 43
    execute_csv2_command(
        gvar, 1, None, 'boolean value specified for "flag_jobs_by_target_alias" must be one of the following: true, false, yes, no, 1, or 0.',
        ['my', 'settings', '--show-jobs-by-target-alias', 'invalid-unit-test', '-su', ut_id(gvar, 'clu3')]
    )

    # 44
    execute_csv2_command(
        gvar, 1, None, 'value specified for "status_refresh_interval" must be an integer value.',
        ['my', 'settings', '--status-refresh-interval', 'invalid-unit-test', '-su', ut_id(gvar, 'clu3')]
    )

    # 45
    execute_csv2_command(
        gvar, 1, None, 'boolean value specified for "flag_show_slot_detail" must be one of the following: true, false, yes, no, 1, or 0.',
        ['my', 'settings', '--show-slot-detail', 'invalid-unit-test', '-su', ut_id(gvar, 'clu3')]
    )

    # 46
    execute_csv2_command(
        gvar, 1, None, 'boolean value specified for "flag_show_slot_flavors" must be one of the following: true, false, yes, no, 1, or 0.',
        ['my', 'settings', '--show-slot-flavors', 'invalid-unit-test', '-su', ut_id(gvar, 'clu3')]
    )

    # 47
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu3')),
        ['my', 'settings', '-upw', 'Abc123', '-su', ut_id(gvar, 'clu3')]
    )

    # 48 Revert the password change for future tests.
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu3')),
        ['my', 'settings', '-upw', gvar['user_secret'], '-su', ut_id(gvar, 'clu3'), '-spw', 'Abc123']
    )

if __name__ == '__main__':
    main(None)
