from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id
from sys import argv

# lno: GV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv2_request(gvar, argv[0])

    # 01
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'group', 'update', '-su', ut_id(gvar, 'clu4')]
    )

    # 02
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'group', 'update', '-xx', 'yy', '-su', ut_id(gvar, 'clu4')]
    )

    # 03
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: cloud-name',
        ['cloudscheduler', 'group', 'update', '-cn', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 04
    execute_csv2_command(
        gvar, None, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'group', 'update', '-s', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')], timeout=8
    )

    # 05
    execute_csv2_command(
        gvar, 1, None, None,
        ['cloudscheduler', 'group', 'update', '-su', ut_id(gvar, 'clu4')]
    )

    # 06
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler group update".',
        ['cloudscheduler', 'group', 'update', '-h', '-su', ut_id(gvar, 'clu4')]
    )

    # 07
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'group', 'update', '-H', '-su', ut_id(gvar, 'clu4')]
    )

    # 08
    execute_csv2_command(
        gvar, 1, None, 'Expose API requested',
        ['cloudscheduler', 'group', 'metadataupdate', '-xA', '-su', ut_id(gvar, 'clu4')]
    )

    # 09
    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'group', 'update', '-g', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 10
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'group', 'update', '-g', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu4')]
    )

    # 11
    execute_csv2_command(
        gvar, 1, None, 'requires at least one option to update.',
        ['cloudscheduler', 'group', 'update', '-gn', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 12
    execute_csv2_command(
        gvar, 1, 'GV', 'the request did not match any rows.',
        ['cloudscheduler', 'group', 'update', '-gn', 'invalid-unit-test', '-htcf', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 13
    execute_csv2_command(
        gvar, 1, None, 'specified user "invalid-unit-test" does not exist.',
        ['cloudscheduler', 'group', 'update', '-gn', ut_id(gvar, 'clg1'), '-un', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 14
    execute_csv2_command(
        gvar, 1, None, 'value specified for "user_option" must be one of the following options: [\'add\', \'delete\'].',
        ['cloudscheduler', 'group', 'update', '-gn', ut_id(gvar, 'clg1'), '-uo', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 15
    execute_csv2_command(
        gvar, 1, None, 'must specify at least one field to update.',
        ['cloudscheduler', 'group', 'update', '-gn', ut_id(gvar, 'clg1'), '-uo', 'add', '-su', ut_id(gvar, 'clu4')]
    )

    # 16
    execute_csv2_command(
        gvar, 1, None, 'must specify at least one field to update.',
        ['cloudscheduler', 'group', 'update', '-gn', ut_id(gvar, 'clg1'), '-uo', 'delete', '-su', ut_id(gvar, 'clu4')]
    )

    ''' htcondor_fqdn is currently allowed to be the empty string when updating.
    # 17
    execute_csv2_command(
        gvar, 1, 'GV', 'group update parameter "htcondor_fqdn" contains an empty string which is specifically disallowed.',
        ['cloudscheduler', 'group', 'update', '-gn', ut_id(gvar, 'clg1'), '-htcf', '', '-su', ut_id(gvar, 'clu4')]
    )
    '''

    # 18
    execute_csv2_command(
        gvar, 1, 'GV', 'group update, "{}" failed - user "{}" was specified twice.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clu3')),
        ['cloudscheduler', 'group', 'update', '-gn', ut_id(gvar, 'clg1'), '-un', ut_id(gvar, 'clu3,clu3'), '-su', ut_id(gvar, 'clu4')]
    )

    # 19
    execute_csv2_command(
        gvar, 0, None, 'group "{}" successfully updated.'.format(ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'group', 'update', '-gn', ut_id(gvar, 'clg1'), '-htcf', 'unit-test-group-update.ca', '-su', ut_id(gvar, 'clu4')]
    )

    # 20
    execute_csv2_command(
#       gvar, 0, None, 'unit-test-group-update.ca',
        gvar, 0, None, None,
        ['cloudscheduler', 'group', 'list', '-gn', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu4')]
    )

    # 21
    execute_csv2_command(
        gvar, 1, None, 'You are not authorized to access object "group";',
        ['cloudscheduler', 'group', 'update', '-gn', ut_id(gvar, 'clg1'), '-un', ut_id(gvar, 'clu3,clu7'), '-su', ut_id(gvar, 'clu3')]
    )

    # 22
    execute_csv2_command(
        gvar, 0, None, 'group "{}" successfully updated.'.format(ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'group', 'update', '-gn', ut_id(gvar, 'clg1'), '-un', ut_id(gvar, 'clu3,clu7'), '-su', ut_id(gvar, 'clu4')]
    )

    # 23
    execute_csv2_command(
        gvar, 0, None, ut_id(gvar, 'clg1'),
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'clu3'), '-su', ut_id(gvar, 'clu4')]
    )

    # 24
    execute_csv2_command(
        gvar, 0, None, ut_id(gvar, 'clg1'),
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'clu7'), '-su', ut_id(gvar, 'clu4')]
    )

    # 25
    execute_csv2_command(
        gvar, 0, None, 'group "{}" successfully updated.'.format(ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'group', 'update', '-gn', ut_id(gvar, 'clg1'), '-un', ut_id(gvar, 'clu3,clu7'), '-uo', 'delete', '-su', ut_id(gvar, 'clu4')]
    )

    # 26
    execute_csv2_command(
        gvar, 0, None, 'None',
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'clu7'), '-su', ut_id(gvar, 'clu4')]
    )

    # 27
    execute_csv2_command(
        gvar, 0, None, 'group "{}" successfully updated.'.format(ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'group', 'update', '-gn', ut_id(gvar, 'clg1'), '-un', ut_id(gvar, 'clu3'), '-uo', 'add', '-su', ut_id(gvar, 'clu4')]
    )

    # 28
    execute_csv2_command(
        gvar, 0, None, ut_id(gvar, 'clg1'),
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'clu3'), '-su', ut_id(gvar, 'clu4')]
    )

    # 29
    execute_csv2_command(
        gvar, 0, None, 'None',
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'clu7'), '-su', ut_id(gvar, 'clu4')]
    )

    # 30
    execute_csv2_command(
        gvar, 0, None, 'group "{}" successfully updated.'.format(ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'group', 'update', '-gn', ut_id(gvar, 'clg1'), '-un', ut_id(gvar, 'clu3'), '-uo', 'delete', '-su', ut_id(gvar, 'clu4')]
    )

    # 31
    execute_csv2_command(
        gvar, 0, None, 'None',
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'clu7'), '-su', ut_id(gvar, 'clu4')]
    )

    # 32
    execute_csv2_command(
        gvar, 0, None, 'group "{}" successfully updated.'.format(ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'group', 'update', '-gn', ut_id(gvar, 'clg1'), '-un', ut_id(gvar, 'clu3,clu7'), '-uo', 'add', '-su', ut_id(gvar, 'clu4')]
    )

    # 33
    execute_csv2_command(
        gvar, 0, None, ut_id(gvar, 'clg1'),
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'clu3'), '-su', ut_id(gvar, 'clu4')]
    )

    # 34
    execute_csv2_command(
        gvar, 0, None, ut_id(gvar, 'clg1'),
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'clu7'), '-su', ut_id(gvar, 'clu4')]
    )

if __name__ == "__main__":
    main(None)
