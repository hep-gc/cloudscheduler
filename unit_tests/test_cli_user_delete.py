from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id, sanity_commands
from sys import argv

# lno: UV - error code identifier.

def main(gvar):

    # 01 - 14
    sanity_commands(gvar, 'user', 'delete')

    # 15
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specified on the command line',
        ['user', 'delete', '-g', ut_id(gvar, 'clg1')]
    )

    # 16
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: group-option',
        ['user', 'delete', '-go', 'invalid-unit-test']
    )

    # 17 We have to specify the server and server password explicitly because -un has to be the last parameter.
    execute_csv2_command(
        gvar, 1, None, 'Value omitted for option: -un | --username',
        ['user', 'delete', '-s', 'unit-test', '-spw', gvar['user_secret'], '-un']
    )

    # 18
    execute_csv2_command(
        gvar, 1, None, 'cannot delete "", user doesn\'t exist.',
        ['user', 'delete', '-un', '']
    )

    # 19
    execute_csv2_command(
        gvar, 1, None, 'cannot delete "invalid-unit-test", user doesn\'t exist.',
        ['user', 'delete', '-un', 'invalid-unit-test']
    )

    # 20 Delete a user who is not in any groups.
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully deleted.'.format(ut_id(gvar, 'clu5')),
        ['user', 'delete', '-un', ut_id(gvar, 'clu5'), '-Y']
    )

    # 21 Delete a user who is in clg1.
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully deleted.'.format(ut_id(gvar, 'clu6')),
        ['user', 'delete', '-un', ut_id(gvar, 'clu6'), '-Y']
    )

if __name__ == "__main__":
    main(initialize_csv2_request(selections=argv[1] if len(argv) > 1 else ''))
