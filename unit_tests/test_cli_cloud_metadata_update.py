from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id
from sys import argv

# lno: CV - error code identifier.

def main(gvar, user_secret):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv2_request(gvar, argv[0])

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'metadata-update', '-s', 'unit-test-un']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'cloud', 'metadata-update', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: cloud-project',
        ['cloudscheduler', 'cloud', 'metadata-update', '-cp', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'cloud', 'metadata-update', '-s', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'metadata-update', '-s', 'unit-test-un']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler cloud metadata-update".',
        ['cloudscheduler', 'cloud', 'metadata-update', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'cloud', 'metadata-update', '-H']
    )

    execute_csv2_command(
        gvar, 1, None, 'Expose API requested',
        ['cloudscheduler', 'cloud', 'metadata-update', '-xA']
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'cloud', 'metadata-update', '-g', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'metadata-update', '-g', ut_id(gvar, 'clg1')]
    )

    execute_csv2_command(
        gvar, 1, None, 'requires at least one option to modify.',
        ['cloudscheduler', 'cloud', 'metadata-update', '-cn', 'invalid-unit-test', '-mn', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'CV30', 'the request did not match any rows.',
        ['cloudscheduler', 'cloud', 'metadata-update', '-cn', 'invalid-unit-test', '-mn', 'invalid-unit-test', '-me', '0']
    )

    execute_csv2_command(
        gvar, 1, 'CV30', 'the request did not match any rows.',
        ['cloudscheduler', 'cloud', 'metadata-update', '-cn', ut_id(gvar, 'clc2'), '-mn', 'invalid-unit-test', '-me', '0']
    )

    execute_csv2_command(
        gvar, 1, 'CV29', 'boolean value specified for "enabled" must be one of the following: true, false, yes, no, 1, or 0.',
        ['cloudscheduler', 'cloud', 'metadata-update', '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm2'), '-me', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'CV29', r'value specified for "mime_type" must be one of the following options: [\'cloud-config\', \'ucernvm-config\'].',
        ['cloudscheduler', 'cloud', 'metadata-update', '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm2'), '-mmt', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'CV29', 'value specified for "priority" must be an integer value.',
        ['cloudscheduler', 'cloud', 'metadata-update', '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm2'), '-mp', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'file "{}::{}::{}" successfully  updated.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2'), ut_id(gvar, 'clm2')),
        ['cloudscheduler', 'cloud', 'metadata-update', '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm2'), '-me', 'false']
    )

    execute_csv2_command(
        gvar, 0, None, 'file "{}::{}::{}" successfully  updated.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2'), ut_id(gvar, 'clm2')),
        ['cloudscheduler', 'cloud', 'metadata-update', '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm2'), '-mmt', 'ucernvm-config']
    )

    execute_csv2_command(
        gvar, 0, None, 'file "{}::{}::{}" successfully  updated.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2'), ut_id(gvar, 'clm2')),
        ['cloudscheduler', 'cloud', 'metadata-update', '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm2'), '-mp', '1']
    )

    execute_csv2_command(
        gvar, 0, None, 'file "{}::{}::{}" successfully  updated.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2'), ut_id(gvar, 'clm2')),
        ['cloudscheduler', 'cloud', 'metadata-update', '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm2'), '-mp', '1', '-g', ut_id(gvar, 'clg1'), '-s', 'unit-test']
    )

if __name__ == "__main__":
    main(None)
