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
        ['cloudscheduler', 'group', 'metadata-edit']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'group', 'metadata-edit', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: job-cores',
        ['cloudscheduler', 'group', 'metadata-edit', '-jc', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'user settings for server "invalid-unit-test" does not contain a URL value.',
        ['cloudscheduler', 'group', 'metadata-edit', '-s', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, None,
        ['cloudscheduler', 'group', 'metadata-edit', '-s', 'unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler group metadata-edit".',
        ['cloudscheduler', 'group', 'metadata-edit', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'group', 'metadata-edit', '-H']
    )

    execute_csv2_command(
        gvar, 1, None, 'Expose API requested',
        ['cloudscheduler', 'group', 'metadata-edit', '-xA']
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'group', 'metadata-edit', '-g', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'group', 'metadata-edit', '-g', ut_id(gvar, 'clg1')]
    )

    execute_csv2_command(
        gvar, 1, None, 'no value, neither default nor command line, for the following required parameters',
        ['cloudscheduler', 'group', 'metadata-edit', '-mn', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'file "{}::invalid-unit-test" does not exist.'.format(ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'group', 'metadata-edit', '-mn', 'invalid-unit-test', '-te', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, None,
        ['cloudscheduler', 'group', 'metadata-edit', '-mn', ut_id(gvar, 'clm2'), '-te', 'invalid-unit-test']
    )

    # The edit scripts in the next 4 tests will break easily as they rely on some system variables
    # execute_csv2_command(
    #     gvar, 0, None, '"{}::{}" completed, no changes.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clm2')),
    #     ['cloudscheduler', 'group', 'metadata-edit', '-mn', ut_id(gvar, 'clm2'), '-te', './editscript1']
    # )

    # execute_csv2_command(
    #     gvar, 0, None, '"{}::{}" successfully  updated.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clm2')),
    #     ['cloudscheduler', 'group', 'metadata-edit', '-mn', ut_id(gvar, 'clm2'), '-te', './editscript2']
    # )

    # execute_csv2_command(
    #     gvar, 0, None, '"{}::{}" successfully  updated.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clm2.yaml')),
    #     ['cloudscheduler', 'group', 'metadata-edit', '-mn', ut_id(gvar, 'clm2.yaml'), '-te', './editscript3']
    # )

    # execute_csv2_command(
    #     gvar, 1, None, 'Invalid yaml file "scanner error": mapping values are not allowed here',
    #     ['cloudscheduler', 'group', 'metadata-edit', '-mn', ut_id(gvar, 'clm2.yaml'), '-te', './editscript4']
    # )

if __name__ == "__main__":
    main(None)
