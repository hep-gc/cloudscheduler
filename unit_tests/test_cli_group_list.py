from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id
from sys import argv

# lno: GV - error code identifier.

def main(gvar, user_secret):
    if not gvar:
        gvar = {'mnomonic': 'GV'}
        if len(argv) > 1:
            initialize_csv2_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv2_request(gvar, argv[0])

    # 001
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized',
        ['cloudscheduler', 'group', 'list', '-xx', 'yy']
    )

    # 002
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: cloud-name',
        ['cloudscheduler', 'group', 'list', '-cn', 'invalid-unit-test']
    )

    # 003
    execute_csv2_command(
        gvar, 1, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'group', 'list', '-s', 'invalid-unit-test']
    )

    # 004
    execute_csv2_command(
        gvar, 1, None, 'You are not authorized to access object "group";',
        ['cloudscheduler', 'group', 'list', '-s', 'unit-test-un']
    )

    # 005
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'group', 'list', '-s', 'unit-test']
    )

    # 006
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler group list".',
        ['cloudscheduler', 'group', 'list', '-h']
    )

    # 007
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'group', 'list', '-H']
    )

    # 008
    execute_csv2_command(
        gvar, 0, None, 'Expose API requested',
        ['cloudscheduler', 'group', 'list', '-xA']
    )

    # 009
    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'group', 'list', '-g', 'invalid-unit-test']
    )

    # 010
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, '')[:-1], ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'group', 'list', '-g', ut_id(gvar, 'clg1')]
    )

    # 011
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, '')[:-1], ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'group', 'list']
    )

    # 012
    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'group', 'list', '-gn', 'invalid-unit-test']
    )

    # 013
    execute_csv2_command(
        gvar, 0, None, 'Rows: 1',
        ['cloudscheduler', 'group', 'list', '-gn', ut_id(gvar, 'clg1')]
    )

    # 014
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'group', 'list', '-ok'],
        list='Groups', columns=['Group']
    )

    # 015
    execute_csv2_command(
        gvar, 0, None, 'group list, table #1 columns: keys=group_name, columns=condor_central_manager,metadata_names',
        ['cloudscheduler', 'group', 'list', '-VC']
    )

    # 016
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'group', 'list', '-NV'],
        list='Groups', columns=['Group', 'Central', 'Manager', 'Metadata', 'Filenames']
    )

    # 017
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'group', 'list', '-V', 'metadata_names'],
        list='Groups', columns=['Group', 'Metadata', 'Filenames']
    )

    # 018
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'group', 'list'],
        list='Groups', columns=['Group', 'Metadata', 'Filenames']
    )

    # 019
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'group', 'list', '-r'],
        list='Groups', columns=['Key', 'Value']
    )

    # 020
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'group', 'list', '-V', ''],
        list='Groups', columns=['Group', 'Central', 'Manager', 'Metadata', 'Filenames']
    )

if __name__ == "__main__":
    main(None)
