from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id, sanity_commands, parameters_commands
from sys import argv

# lno: UV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)

    # 01 - 13
    sanity_commands(gvar, 'user')

    # 14 - 27
    sanity_commands(gvar, 'user', 'add')

    # 28
    execute_csv2_command(
        gvar, 1, None, 'You are not authorized to access object "user";',
        ['user', 'list', '-su', ut_id(gvar, 'clu3')]
    )

    parameters = {
        # 29 Omit `--username`.
        '--username': {'valid': ut_id(gvar, 'clu10'), 'test_cases': {
            # 30
            '': 'value specified for "username" must not be the empty string.',
            # 31
            'invalid-unit-Test': 'value specified for "username" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 32
            'invalid-unit-test-': 'value specified for "username" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 33
            'invalid-unit--test': 'value specified for "username" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 34
            'invalid-unit-test!': 'value specified for "username" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 35
            'username-that-is-too-long-for-the-database': 'Data too long for column \'username\' at row 1',
            # 36
            ut_id(gvar, 'clu3'): 'username "{}" unavailable.'.format(ut_id(gvar, 'clu3')),
            # 37
            ut_id(gvar, 'command-line-user-3'): 'username "{}" unavailable.'.format(ut_id(gvar, 'command-line-user-3'))
        }, 'mandatory': True},
        # 38 Omit `--user-password`.
        '--user-password': {'valid': gvar['user_secret'], 'test_cases': {
            # 39
            '': 'value specified for a password is less than 6 characters.',
            # 40
            'inv': 'value specified for a password is less than 6 characters.',
            # 41
            'invalid': 'value specified for a password is less then 16 characters, and does not contain a mixture of upper, lower, and numerics.',
        }, 'mandatory': True},
        '--group-name': {'valid': ut_id(gvar, 'clg3'), 'test_cases': {
            # 42
            '': 'parameter "group_name" contains an empty string which is specifically disallowed.',
            # 43
            'invalid-unit-test': 'specified group "invalid-unit-test" does not exist.',
            # 44
            ut_id(gvar, 'clg3,clg3'): 'user add, "{}" failed - group "{}" was specified twice.'.format(ut_id(gvar, 'clu10'), ut_id(gvar, 'clg3'))
        }},
        # 45
        '--super-user': {'valid': 0, 'test_cases': {'invalid-unit-test': 'boolean value specified for "is_superuser" must be one of the following: true, false, yes, no, 1, or 0.'}},
        '--user-common-name': {'valid': 'invalid-unit-test', 'test_cases': {
            # 46
            ut_id(gvar, 'clu3'): 'common name "{0}" conflicts with registered user "{0}".'.format(ut_id(gvar, 'clu3')),
            # 47
            ut_id(gvar, 'command-line-user-3'): 'common name "{}" conflicts with registered user "{}".'.format(ut_id(gvar, 'command-line-user-3'), ut_id(gvar, 'clu3'))
        }}
    }
    
    parameters_commands(gvar, 'user', 'add', ut_id(gvar, 'clg1'), ut_id(gvar, 'clu4'), parameters)

    # 48
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: group-option',
        ['user', 'add', '-go', 'invalid-unit-test', '-g', ut_id(gvar, 'clg1')]
    )

    # 49
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'clu10')),
        ['user', 'add', '-un', ut_id(gvar, 'clu10'), '-upw', gvar['user_secret'], '-ucn', ut_id(gvar, 'command-line-user-10'), '-gn', ut_id(gvar, 'clg1,clg3')]
    )

    # 50 We have to specify server and server password explicitly because `--super-user` has to be the last parameter.
    execute_csv2_command(
        gvar, 1, None, 'Value omitted for option: -SU | --super-user',
        ['user', 'add', '-s', 'unit-test', '-spw', gvar['user_secret'], '-un', ut_id(gvar, 'clu11'), '-upw', gvar['user_secret'], '-ucn', ut_id(gvar, 'command-line-user-11'), '--super-user']
    )

    # 51
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'clu11')),
        ['user', 'add', '-un', ut_id(gvar, 'clu11'), '-upw', gvar['user_secret'], '-ucn', ut_id(gvar, 'command-line-user-11'), '-SU', 'true', '-gn', ut_id(gvar, 'clg3')]
    )

if __name__ == "__main__":
    main(None)
