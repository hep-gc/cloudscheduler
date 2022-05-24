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

    # 01 - 14
    sanity_commands(gvar, 'group', 'update')

    # 15
    execute_csv2_command(
        gvar, 1, None, 'You are not authorized to access object "group";',
        ['group', 'update', '-gn', ut_id(gvar, 'clg3'), '-un', ut_id(gvar, 'clu3,clu7'), '-su', ut_id(gvar, 'clu3')]
    )

    parameters = {
        # 16 Omit `--group-name`.
        # We cannot specify `--group-name` test cases here because will complain that we don't specify a field to update.
        '--group-name': {'valid': ut_id(gvar, 'clg3'), 'test_cases': {}, 'mandatory': True},
        # 17
        '--user-option': {'valid': 'add', 'test_cases': {'invalid-unit-test': 'value specified for "user_option" must be one of the following options: [\'add\', \'delete\'].'}},
        # 18
        '--username': {'valid': ut_id(gvar, 'clu7'), 'test_cases': {'invalid-unit-test': 'specified user "invalid-unit-test" does not exist.'}},
        # 19
        '--public-visibility': {'valid': 0, 'test_cases': {'invalid-unit-test': 'boolean value specified for "public_visibility" must be one of the following: true, false, yes, no, 1, or 0.'}}
    }
    
    parameters_commands(gvar, 'group', 'update', ut_id(gvar, 'clg1'), ut_id(gvar, 'clu4'), parameters)

    # 20
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: cloud-name',
        ['group', 'update', '-cn', 'invalid-unit-test', '-g', ut_id(gvar, 'clg1')]
    )

    # 21 Give `--group-name` as the empty string.
    execute_csv2_command(
        gvar, 1, None, 'value specified for "group_name" must not be the empty string.',
        ['group', 'update', '-gn', '', '--htcondor-fqdn', 'invalid-unit-test']
    )

    # 22 Give a `--group-name` with the wrong format.
    execute_csv2_command(
        gvar, 1, None, 'value specified for "group_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
        ['group', 'update', '-gn', 'invalid-unit-test!', '--htcondor-fqdn', 'invalid-unit-test']
    )

    # 23 Fail to specify any fields to update.
    execute_csv2_command(
        gvar, 1, None, 'requires at least one option to update.',
        ['group', 'update', '-gn', ut_id(gvar, 'clg3')]
    )

    # 24 Ensure that `--user-option` by itself does not count as a field to update.
    execute_csv2_command(
        gvar, 1, None, 'must specify at least one field to update.',
        ['group', 'update', '-gn', ut_id(gvar, 'clg3'), '--user-option', 'add']
    )

    # 25 Attempt to update a group that does not exist.
    execute_csv2_command(
        gvar, 1, 'GV', 'the request did not match any rows.',
        ['group', 'update', '-gn', 'invalid-unit-test', '--htcondor-fqdn', '']
    )

    # 26 Specify the same `--username` twice.
    execute_csv2_command(
        gvar, 1, 'GV', 'group update, "{}" failed - user "{}" was specified twice.'.format(ut_id(gvar, 'clg3'), ut_id(gvar, 'clu3')),
        ['group', 'update', '-gn', ut_id(gvar, 'clg3'), '--username', ut_id(gvar, 'clu3,clu3')]
    )

    # 27 Update clg3's `--htcondor-fqdn`.
    execute_csv2_command(
        gvar, 0, None, 'group "{}" successfully updated.'.format(ut_id(gvar, 'clg3')),
        ['group', 'update', '-gn', ut_id(gvar, 'clg3'), '-htcf', 'localhost']
    )

    # 28 Ensure that clg3's `--htcondor-fqdn` was updated.
    execute_csv2_command(
        gvar, 0, None, 'localhost',
        ['group', 'list', '-gn', ut_id(gvar, 'clg3')],
        expected_list='Groups'
    )

    # 29 Implicitly add clu3 and clu7 to clg3.
    execute_csv2_command(
        gvar, 0, None, 'group "{}" successfully updated.'.format(ut_id(gvar, 'clg3')),
        ['group', 'update', '-gn', ut_id(gvar, 'clg3'), '-un', ut_id(gvar, 'clu3,clu7')]
    )

    # 30 Ensure that clu3 was added to clg3.
    execute_csv2_command(
        gvar, 0, None, ut_id(gvar, 'clg3'),
        ['user', 'list', '-un', ut_id(gvar, 'clu3')],
        expected_list='Users'
    )

    # 31 Update public visibility
    execute_csv2_command(
        gvar, 0, None, 'group "{}" successfully updated.'.format(ut_id(gvar, 'clg3')),
        ['group', 'update', '-gn', ut_id(gvar, 'clg3'), '-pub', 1]
    )

    # 32 Explicitly delete clu3 and clu7 from clg3.
    execute_csv2_command(
        gvar, 0, None, 'group "{}" successfully updated.'.format(ut_id(gvar, 'clg3')),
        ['group', 'update', '-gn', ut_id(gvar, 'clg3'), '-un', ut_id(gvar, 'clu3,clu7'), '-uo', 'delete']
    )

    # 33 Ensure that clu7 was removed from clg3.
    execute_csv2_command(
        gvar, 0, None, 'None',
        ['user', 'list', '-un', ut_id(gvar, 'clu7')],
        expected_list='Users'
    )

    # 34 Explicitly add clu3 to clg3.
    execute_csv2_command(
        gvar, 0, None, 'group "{}" successfully updated.'.format(ut_id(gvar, 'clg3')),
        ['group', 'update', '-gn', ut_id(gvar, 'clg3'), '-un', ut_id(gvar, 'clu3'), '-uo', 'add']
    )

    # 35 Ensure that clu3 was added to clg3.
    execute_csv2_command(
        gvar, 0, None, ut_id(gvar, 'clg3'),
        ['user', 'list', '-un', ut_id(gvar, 'clu3')],
        expected_list='Users'
    )

    # 36 Explicitly delete clu3 from clg3.
    execute_csv2_command(
        gvar, 0, None, 'group "{}" successfully updated.'.format(ut_id(gvar, 'clg3')),
        ['group', 'update', '-gn', ut_id(gvar, 'clg3'), '-un', ut_id(gvar, 'clu3'), '-uo', 'delete']
    )

    # 37 Ensure that clu3 was removed from clg3.
    execute_csv2_command(
        gvar, 0, None, 'None',
        ['user', 'list', '-un', ut_id(gvar, 'clu7')],
        expected_list='Users'
    )

if __name__ == "__main__":
    main(None)
