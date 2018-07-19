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
        ['cloudscheduler', 'group', 'metadata-load']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'group', 'metadata-load', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: job-cores',
        ['cloudscheduler', 'group', 'metadata-load', '-jc', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'user settings for server "invalid-unit-test" does not contain a URL value.',
        ['cloudscheduler', 'group', 'metadata-load', '-s', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, None,
        ['cloudscheduler', 'group', 'metadata-load', '-s', 'unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler group metadata-load".',
        ['cloudscheduler', 'group', 'metadata-load', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'group', 'metadata-load', '-H']
    )

    execute_csv2_command(
        gvar, 1, None, 'Expose API requested',
        ['cloudscheduler', 'group', 'metadata-load', '-xA']
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'group', 'metadata-load', '-g', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'group', 'metadata-load', '-g', ut_id(gvar, 'clg1')]
    )

    execute_csv2_command(
        gvar, 1, None, 'The specified metadata file "invalid-unit-test" does not exist.',
        ['cloudscheduler', 'group', 'metadata-load', '-f', 'invalid-unit-test', '-mn', ut_id(gvar, 'cli-invalid-unit-test')]
    )

    execute_csv2_command(
        gvar, 1, 'GV25', 'boolean value specified for "enabled" must be one of the following: true, false, yes, no, 1, or 0.',
        ['cloudscheduler', 'group', 'metadata-load', '-f', 'ut.yaml', '-mn', ut_id(gvar, 'cli-invalid-unit-test'), '-me', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'GV25', r'value specified for "mime_type" must be one of the following options: [\'cloud-config\', \'ucernvm-config\'].',
        ['cloudscheduler', 'group', 'metadata-load', '-f', 'ut.yaml', '-mn', ut_id(gvar, 'cli-invalid-unit-test'), '-mmt', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'GV25', 'value specified for "priority" must be a integer value.',
        ['cloudscheduler', 'group', 'metadata-load', '-f', 'ut.yaml', '-mn', ut_id(gvar, 'cli-invalid-unit-test'), '-mp', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'GV25', 'value specified for "metadata (metadata_name)" is invalid - scanner error',
        ['cloudscheduler', 'group', 'metadata-load', '-f', 'notyamlfile.txt', '-mn', 'invalid-unit-test.yaml']
    )

    execute_csv2_command(
        gvar, 0, None, 'file "{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clm10')),
        ['cloudscheduler', 'group', 'metadata-load', '-f', 'notyamlfile.txt', '-mn', ut_id(gvar, 'clm10')]
    )

    execute_csv2_command(
        gvar, 0, None, 'file "{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clm10.yaml')),
        ['cloudscheduler', 'group', 'metadata-load', '-f', 'ut.yaml', '-mn', ut_id(gvar, 'clm10.yaml')]
    )

if __name__ == "__main__":
    main(None)