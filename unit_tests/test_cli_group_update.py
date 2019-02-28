from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id
from sys import argv

# lno: GV - error code identifier.

def main(gvar, user_secret):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv2_request(gvar, argv[0])

    # 001
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'group', 'update', '-s', 'unit-test']
    )

    # 002
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'group', 'update', '-xx', 'yy']
    )

    # 003
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: cloud-name',
        ['cloudscheduler', 'group', 'update', '-cn', 'invalid-unit-test']
    )

    # 004
    execute_csv2_command(
        gvar, 1, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'group', 'update', '-s', 'invalid-unit-test']
    )

    # 005
    execute_csv2_command(
        gvar, 1, None, None,
        ['cloudscheduler', 'group', 'update', '-s', 'unit-test']
    )

    # 006
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler group update".',
        ['cloudscheduler', 'group', 'update', '-h']
    )

    # 007
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'group', 'update', '-H']
    )

    # 008
    execute_csv2_command(
        gvar, 1, None, 'Expose API requested',
        ['cloudscheduler', 'group', 'metadataupdate', '-xA']
    )

    # 009
    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'group', 'update', '-g', 'invalid-unit-test']
    )

    # 010
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'group', 'update', '-g', ut_id(gvar, 'clg1')]
    )

    # 011
    execute_csv2_command(
        gvar, 1, None, 'requires at least one option to update.',
        ['cloudscheduler', 'group', 'update', '-gn', 'invalid-unit-test']
    )

    # 012
    execute_csv2_command(
        gvar, 1, 'GV44', 'the request did not match any rows.',
        ['cloudscheduler', 'group', 'update', '-gn', 'invalid-unit-test', '-htcf', 'invalid-unit-test']
    )

    # 013
    execute_csv2_command(
        gvar, 1, None, 'specified user "invalid-unit-test" does not exist.',
        ['cloudscheduler', 'group', 'update', '-gn', ut_id(gvar, 'clg1'), '-un', 'invalid-unit-test']
    )

    # 014
    execute_csv2_command(
        gvar, 1, None, r'value specified for "user_option" must be one of the following options: [\'add\', \'delete\'].',
        ['cloudscheduler', 'group', 'update', '-gn', ut_id(gvar, 'clg1'), '-uo', 'invalid-unit-test']
    )

    # 015
    execute_csv2_command(
        gvar, 1, None, 'must specify at least one field to update.',
        ['cloudscheduler', 'group', 'update', '-gn', ut_id(gvar, 'clg1'), '-uo', 'add']
    )

    # 016
    execute_csv2_command(
        gvar, 1, None, 'must specify at least one field to update.',
        ['cloudscheduler', 'group', 'update', '-gn', ut_id(gvar, 'clg1'), '-uo', 'delete']
    )

    # 017
    execute_csv2_command(
        gvar, 1, 'GV42', 'group update parameter "htcondor_fqdn" contains an empty string which is specifically disallowed.',
        ['cloudscheduler', 'group', 'update', '-gn', ut_id(gvar, 'clg1'), '-htcf', '']
    )

    # 018
    execute_csv2_command(
        gvar, 1, 'GV43', 'group add, "{}" failed - user "{}" was specified twice.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clu3')),
        ['cloudscheduler', 'group', 'update', '-gn', ut_id(gvar, 'clg1'), '-un', ut_id(gvar, 'clu3,clu3')]
    )

    # 019
    execute_csv2_command(
        gvar, 0, None, 'group "{}" successfully updated.'.format(ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'group', 'update', '-gn', ut_id(gvar, 'clg1'), '-htcf', 'unit-test-group-update.ca']
    )

    # 020
    execute_csv2_command(
#       gvar, 0, None, 'unit-test-group-update.ca',
        gvar, 0, None, None,
        ['cloudscheduler', 'group', 'list', '-gn', ut_id(gvar, 'clg1')]
    )

    # 021
    execute_csv2_command(
        gvar, 1, None, 'You are not authorized to access object "group";',
        ['cloudscheduler', 'group', 'update', '-gn', ut_id(gvar, 'clg1'), '-un', ut_id(gvar, 'clu3,clu7'), '-s', 'unit-test-un']
    )

    # 022
    execute_csv2_command(
        gvar, 0, None, 'group "{}" successfully updated.'.format(ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'group', 'update', '-gn', ut_id(gvar, 'clg1'), '-un', ut_id(gvar, 'clu3,clu7'), '-s', 'unit-test']
    )

    # 023
    execute_csv2_command(
        gvar, 0, None, ut_id(gvar, 'clg1'),
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'clu3')]
    )

    # 024
    execute_csv2_command(
        gvar, 0, None, ut_id(gvar, 'clg1'),
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'clu7')]
    )

    # 025
    execute_csv2_command(
        gvar, 0, None, 'group "{}" successfully updated.'.format(ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'group', 'update', '-gn', ut_id(gvar, 'clg1'), '-un', ut_id(gvar, 'clu3,clu7'), '-uo', 'delete']
    )

    # 026
    execute_csv2_command(
        gvar, 0, None, 'None',
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'clu7')]
    )

    # 027
    execute_csv2_command(
        gvar, 0, None, 'group "{}" successfully updated.'.format(ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'group', 'update', '-gn', ut_id(gvar, 'clg1'), '-un', ut_id(gvar, 'clu3'), '-uo', 'add']
    )

    # 028
    execute_csv2_command(
        gvar, 0, None, ut_id(gvar, 'clg1'),
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'clu3')]
    )

    # 029
    execute_csv2_command(
        gvar, 0, None, 'None',
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'clu7')]
    )

    # 030
    execute_csv2_command(
        gvar, 0, None, 'group "{}" successfully updated.'.format(ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'group', 'update', '-gn', ut_id(gvar, 'clg1'), '-un', ut_id(gvar, 'clu3'), '-uo', 'delete']
    )

    # 031
    execute_csv2_command(
        gvar, 0, None, 'None',
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'clu7')]
    )

    # 032
    execute_csv2_command(
        gvar, 0, None, 'group "{}" successfully updated.'.format(ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'group', 'update', '-gn', ut_id(gvar, 'clg1'), '-un', ut_id(gvar, 'clu3,clu7'), '-uo', 'add']
    )

    # 033
    execute_csv2_command(
        gvar, 0, None, ut_id(gvar, 'clg1'),
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'clu3')]
    )

    # 034
    execute_csv2_command(
        gvar, 0, None, ut_id(gvar, 'clg1'),
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'clu7')]
    )

if __name__ == "__main__":
    main(None)
