from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id, sanity_commands, parameters_commands
from sys import argv

# lno: GV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)

    # 01 - 13
    sanity_commands(gvar, 'group')

    # 14 - 27
    sanity_commands(gvar, 'group', 'add')

    # 28
    execute_csv2_command(
        gvar, 1, None, 'You are not authorized to access object "group";',
        ['group', '-su', ut_id(gvar, 'clu3')]
    )

    # 29
    execute_csv2_command(
        gvar, 1, None, 'You are not authorized to access object "group";',
        ['group', 'add', '-su', ut_id(gvar, 'clu3')]
    )
    
    parameters = {
        # 30 Omit --group-name.
        '--group-name': {'valid': ut_id(gvar, 'clg10'), 'test_cases': {
            # 31
            '': 'group add value specified for "group_name" must not be the empty string.',
            # 32
            'invalid-unit-Test': 'group add value specified for "group_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 33
            'invalid-unit-test-': 'group add value specified for "group_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 34
            'invalid-unit--test': 'group add value specified for "group_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 35
            'invalid-unit-test!': 'group add value specified for "group_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 36
            'group-name-that-is-too-long-for-the-database-test-group-name-too-long-error-case': 'Data too long for column \'group_name\' at row 1',
            # 37
            ut_id(gvar, 'clg2'): 'Duplicate entry \'{}\' for key \'PRIMARY\''.format(ut_id(gvar, 'clg2'))
        }, 'mandatory': True},
        # 38
        '--htcondor-fqdn': {'valid': gvar['cloud_credentials']['authurl'], 'test_cases': {'': 'group add parameter "htcondor_fqdn" contains an empty string which is specifically disallowed.'}},
        '--username': {'valid': ut_id(gvar, 'clu3'), 'test_cases': {
            # 39
            'invalid-unit-test': 'specified user "invalid-unit-test" does not exist.',
            # 40
            ut_id(gvar, 'clu3,clu3'): 'group add, "{}" failed - user "{}" was specified twice.'.format(ut_id(gvar, 'clg10'), ut_id(gvar, 'clu3'))
        }}
    }

    parameters_commands(gvar, 'group', 'add', ut_id(gvar, 'clg1'), ut_id(gvar, 'clu4'), parameters)

    # 41
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specified on the command line',
        # The `--server-user` is automatically inserted as clu4 by `execute_csv2_command()`.
        ['group', 'add', '--htcondor-fqdn', 'invalid-unit-test', '--username', 'invalid-unit-test']
    )

    # 42
    execute_csv2_command(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'clg10')),
        ['group', 'add',
            '--group-name', ut_id(gvar, 'clg10'),
            '--htcondor-fqdn', gvar['fqdn'],
            '--username', ut_id(gvar, 'clu3'),
            '--vm-flavor', '',
            '--vm-image', '',
            '--vm-keyname', '',
            '--vm-network', '']
    )

    # 43 Ensure that clg10 was created.
    execute_csv2_command(
        gvar, 0, None, 'Rows: 1',
        ['group', 'list', '-gn', ut_id(gvar, 'clg10')]
    )

if __name__ == "__main__":
    main(None)
