from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id
import sys

# lno: GV - error code identifier.

def main(gvar, user_secret):
    if not gvar:
        gvar = {}
        if len(sys.argv) > 1:
            initialize_csv2_request(gvar, sys.argv[0], selections=sys.argv[1])
        else:
            initialize_csv2_request(gvar, sys.argv[0])

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'group', 'update']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'group', 'update', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: job-cores',
        ['cloudscheduler', 'group', 'update', '-jc', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'user settings for server "invalid-unit-test" does not contain a URL value.',
        ['cloudscheduler', 'group', 'update', '-s', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, None,
        ['cloudscheduler', 'group', 'update', '-s', 'unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler group update".',
        ['cloudscheduler', 'group', 'update', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'group', 'update', '-H']
    )

    execute_csv2_command(
        gvar, 1, None, 'Expose API requested',
        ['cloudscheduler', 'group', 'metadataupdate', '-xA']
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'group', 'update', '-g', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'group', 'update', '-g', ut_id(gvar, 'clg1')]
    )

    execute_csv2_command(
        gvar, 1, None, 'requires at least one option to update.',
        ['cloudscheduler', 'group', 'update', '-gn', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'GV44', 'the request did not match any rows.',
        ['cloudscheduler', 'group', 'update', '-gn', 'invalid-unit-test', '-gm', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'specified user "invalid-unit-test" does not exist.',
        ['cloudscheduler', 'group', 'update', '-gn', ut_id(gvar, 'clg1'), '-un', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, r'value specified for "user_option" must be one of the following options: [\'add\', \'delete\'].',
        ['cloudscheduler', 'group', 'update', '-gn', ut_id(gvar, 'clg1'), '-uo', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'must specify at least one field to update.',
        ['cloudscheduler', 'group', 'update', '-gn', ut_id(gvar, 'clg1'), '-uo', 'add']
    )

    execute_csv2_command(
        gvar, 1, None, 'must specify at least one field to update.',
        ['cloudscheduler', 'group', 'update', '-gn', ut_id(gvar, 'clg1'), '-uo', 'delete']
    )

    execute_csv2_command(
        gvar, 1, None, 'must specify at least one field to update.',
        ['cloudscheduler', 'group', 'update', '-gn', ut_id(gvar, 'clg1'), '-gm', '']
    )

    execute_csv2_command(
        gvar, 1, 'GV43', 'group add, "jodiew-clg1" failed - user "jodiew-clu3" was specified twice.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clu3')),
        ['cloudscheduler', 'group', 'update', '-gn', ut_id(gvar, 'clg1'), '-un', ut_id(gvar, 'clu3,clu3')]
    )

    execute_csv2_command(
        gvar, 0, None, 'group "{}" successfully updated.'.format(ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'group', 'update', '-gn', ut_id(gvar, 'clg1'), '-gm', 'unit-test-group-update.ca']
    )

    execute_csv2_command(
        gvar, 0, None, 'unit-test-group-update.ca',
        ['cloudscheduler', 'group', 'list', '-gn', ut_id(gvar, 'clg1')]
    )

    execute_csv2_command(
        gvar, 0, None, 'group "{}" successfully updated.'.format(ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'group', 'update', '-gn', ut_id(gvar, 'clg1'), '-un', ut_id(gvar, 'clu3,clu7')]
    )

    execute_csv2_command(
        gvar, 0, None, ut_id(gvar, 'clg1'),
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'clu3')]
    )

    execute_csv2_command(
        gvar, 0, None, ut_id(gvar, 'clg1'),
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'clu7')]
    )

    execute_csv2_command(
        gvar, 0, None, 'group "{}" successfully updated.'.format(ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'group', 'update', '-gn', ut_id(gvar, 'clg1'), '-un', ut_id(gvar, 'clu3,clu7'), '-uo', 'delete']
    )

    execute_csv2_command(
        gvar, 0, None, 'None',
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'clu7')]
    )

    execute_csv2_command(
        gvar, 0, None, 'group "{}" successfully updated.'.format(ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'group', 'update', '-gn', ut_id(gvar, 'clg1'), '-un', ut_id(gvar, 'clu3'), '-uo', 'add']
    )

    execute_csv2_command(
        gvar, 0, None, ut_id(gvar, 'clg1'),
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'clu3')]
    )

    execute_csv2_command(
        gvar, 0, None, 'None',
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'clu7')]
    )

    execute_csv2_command(
        gvar, 0, None, 'group "{}" successfully updated.'.format(ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'group', 'update', '-gn', ut_id(gvar, 'clg1'), '-un', ut_id(gvar, 'clu3'), '-uo', 'delete']
    )

    execute_csv2_command(
        gvar, 0, None, 'None',
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'clu7')]
    )

    execute_csv2_command(
        gvar, 0, None, 'group "{}" successfully updated.'.format(ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'group', 'update', '-gn', ut_id(gvar, 'clg1'), '-un', ut_id(gvar, 'clu3,clu7'), '-uo', 'add']
    )

    execute_csv2_command(
        gvar, 0, None, ut_id(gvar, 'clg1'),
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'clu3')]
    )

    execute_csv2_command(
        gvar, 0, None, ut_id(gvar, 'clg1'),
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'clu7')]
    )

if __name__ == "__main__":
    main(None)