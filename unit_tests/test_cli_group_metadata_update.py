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

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'metadata', 'update']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'metadata', 'update', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: job-cores',
        ['cloudscheduler', 'metadata', 'update', '-jc', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'user settings for server "invalid-unit-test" does not contain a URL value.',
        ['cloudscheduler', 'metadata', 'update', '-mn', 'invalid-unit-test', '-me', '0', '-s', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, None,
        ['cloudscheduler', 'metadata', 'update', '-s', 'unit-test-un']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler metadata update".',
        ['cloudscheduler', 'metadata', 'update', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'metadata', 'update', '-H']
    )

    execute_csv2_command(
        gvar, 1, None, 'Expose API requested',
        ['cloudscheduler', 'metadata', 'update', '-mn', 'invalid-unit-test', '-me', '0', '-xA']
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'metadata', 'update', '-mn', 'invalid-unit-test', '-me', '0', '-g', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'metadata', 'update', '-g', ut_id(gvar, 'clg1')]
    )

    execute_csv2_command(
        gvar, 1, None, 'the request did not match any rows.',
        ['cloudscheduler', 'metadata', 'update', '-mn', 'invalid-unit-test', '-me', '0']
    )

    execute_csv2_command(
        gvar, 1, None, 'value specified for "enabled" must be one of the following: true, false, yes, no, 1, or 0.',
        ['cloudscheduler', 'metadata', 'update', '-mn', 'invalid-unit-test', '-me', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, r'value specified for "mime_type" must be one of the following options: [\'cloud-config\', \'ucernvm-config\'].',
        ['cloudscheduler', 'metadata', 'update', '-mn', 'invalid-unit-test', '-mmt', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'value specified for "priority" must be an integer value.',
        ['cloudscheduler', 'metadata', 'update', '-mn', 'invalid-unit-test', '-mp', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'requires at least one option to modify.',
        ['cloudscheduler', 'metadata', 'update', '-mn', ut_id(gvar, 'clm2')]
    )

    execute_csv2_command(
        gvar, 0, None, 'file "{}::{}" successfully  updated.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clm2')),
        ['cloudscheduler', 'metadata', 'update', '-mn', ut_id(gvar, 'clm2'), '-me', 'false']
    )

    execute_csv2_command(
        gvar, 0, None, 'file "{}::{}" successfully  updated.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clm2')),
        ['cloudscheduler', 'metadata', 'update', '-mn', ut_id(gvar, 'clm2'), '-mmt', 'ucernvm-config']
    )

    execute_csv2_command(
        gvar, 0, None, 'file "{}::{}" successfully  updated.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clm2')),
        ['cloudscheduler', 'metadata', 'update', '-mn', ut_id(gvar, 'clm2'), '-mp', '1']
    )

if __name__ == "__main__":
    main(None)
