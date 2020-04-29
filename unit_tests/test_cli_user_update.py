from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id, sanity_commands, parameters_commands
from sys import argv

# lno: UV - error code identifier.

def main(gvar):

    # 01 - 14
    sanity_commands(gvar, 'user', 'update')

    # 15
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specified on the command line',
        ['user', 'update']
    )

    parameters = {
        # 16 Omit `--username`.
        # We cannot specify test cases for `--username` here because it would complain that we did not specify any fields to update.
        '--username': {'valid': ut_id(gvar, 'clu7'), 'test_cases': {}, 'mandatory': True},
        '--user-password': {'valid': gvar['user_secret'], 'test_cases': {
            # 17
            '': 'value specified for a password is less than 6 characters.',
            # 18
            'inv': 'value specified for a password is less than 6 characters.',
            # 19
            'invalid': 'value specified for a password is less then 16 characters, and does not contain a mixture of upper, lower, and numerics.'
        }},
        # 20
        '--super-user': {'valid': 0, 'test_cases': {'invalid-unit-test': 'boolean value specified for "is_superuser" must be one of the following: true, false, yes, no, 1, or 0.'}},
        # 21
        '--group-option': {'valid': 'add', 'test_cases': {'invalid-unit-test': 'value specified for "group_option" must be one of the following options: [\'add\', \'delete\'].'}}
    }

    parameters_commands(gvar, 'user', 'update', ut_id(gvar, 'clg1'), ut_id(gvar, 'clu4'), parameters)

    # 22 Specify a user that does not exist.
    execute_csv2_command(
        gvar, 1, 'UV', 'the request did not match any rows.',
        ['user', 'update', '-un', 'invalid-unit-test', '-upw', gvar['user_secret'], '-g', ut_id(gvar, 'clg1')]
    )

    # 23
    execute_csv2_command(
        gvar, 1, None, '"cloudscheduler user update" requires at least one option to update.',
        ['user', 'update', '-un', ut_id(gvar, 'clu7')]
    )

    # 24
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: only-keys',
        ['user', 'update', '-ok']
    )

    # 25
    execute_csv2_command(
        gvar, 1, 'UV', 'common name "{0}" conflicts with registered user "{0}".'.format(ut_id(gvar, 'clu3')),
        ['user', 'update', '-un', ut_id(gvar, 'clu7'), '-ucn', ut_id(gvar, 'clu3')]
    )

    # 26
    execute_csv2_command(
        gvar, 1, 'UV', 'common name "{}" conflicts with registered user "{}".'.format(ut_id(gvar, 'command-line-user-3'), ut_id(gvar, 'clu3')),
        ['user', 'update', '-un', ut_id(gvar, 'clu7'), '-ucn', ut_id(gvar, 'command-line-user-3')]
    )

    # 27 We have to specify server and server password explicitly because `--super-user` has to be the last parameter.
    execute_csv2_command(
        gvar, 1, None, 'Value omitted for option: -SU | --super-user',
        ['user', 'update', '-un', ut_id(gvar, 'clu7'), '-s', 'unit-test', '-spw', gvar['user_secret'], '--super-user']
    )

    # 28
    execute_csv2_command(
        gvar, 1, 'UV', 'user update must specify at least one field to update.',
        ['user', 'update', '-un', ut_id(gvar, 'clu7'), '-go', 'add']
    )

    # 29
    execute_csv2_command(
        gvar, 1, None, 'user update, parameter "group_name" contains an empty string which is specifically disallowed.',
        ['user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', '']
    )

    # 30
    execute_csv2_command(
        gvar, 1, 'UV', 'specified group "invalid-unit-test" does not exist.',
        ['user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', 'invalid-unit-test']
    )

    # 31
    execute_csv2_command(
        gvar, 1, 'UV', 'user update, "{}" failed - group "{}" was specified twice.'.format(ut_id(gvar, 'clu7'), ut_id(gvar, 'clg1')),
        ['user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', ut_id(gvar, 'clg1,clg1')]
    )

    # 32
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['user', 'update', '-un', ut_id(gvar, 'clu7'), '-ucn', '']
    )

    # 33
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['user', 'update', '-un', ut_id(gvar, 'clu7'), '-ucn', ut_id(gvar, 'command-line-user-update'), '-SU', 'yes']
    )

    # 34 Implicitly add clu7 to clg1.
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', ut_id(gvar, 'clg1')]
    )

    # 35 Explicitly delete clu7 from clg1.
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', ut_id(gvar, 'clg1'), '-go', 'delete']
    )

    # 36 Explicitly add clu7 to clg1.
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', ut_id(gvar, 'clg1'), '-go', 'add']
    )

    # 37 Explicitly delete clu7 from clg1 and clg3.
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', ut_id(gvar, 'clg1,clg3'), '-go', 'delete']
    )

    # 38 Implicitly add clu7 to clg1 and clg3.
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', ut_id(gvar, 'clg1,clg3')]
    )

if __name__ == "__main__":
    main(initialize_csv2_request(selections=argv[1] if len(argv) > 1 else ''))
