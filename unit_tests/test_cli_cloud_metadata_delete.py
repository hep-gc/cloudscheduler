from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id
from sys import argv

# lno: CV - error code identifier.

def main(gvar, user_secret):
    if not gvar:
        gvar = {'mnomonic': 'CV'}
        if len(argv) > 1:
            initialize_csv2_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv2_request(gvar, argv[0])

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line:',
        ['cloudscheduler', 'cloud', 'metadata-delete']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'cloud', 'metadata-delete', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: metadata-mime-type',
        ['cloudscheduler', 'cloud', 'metadata-delete', '-mmt', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'cloud', 'metadata-delete', '-s', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'metadata-delete', '-s', 'unit-test-un']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler cloud metadata-delete".',
        ['cloudscheduler', 'cloud', 'metadata-delete', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'cloud', 'metadata-delete', '-H']
    )

    execute_csv2_command(
        gvar, 1, None, 'Expose API requested',
        ['cloudscheduler', 'cloud', 'metadata-delete', '-xA']
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'cloud', 'metadata-delete', '-g', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'metadata-delete', '-g', ut_id(gvar, 'clg1')]
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot delete "{}::invalid-unit-test::invalid-unit-test", file doesn\\\'t exist.'.format(ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'cloud', 'metadata-delete', '-cn', 'invalid-unit-test', '-mn', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'the request did not match any rows.',
        ['cloudscheduler', 'cloud', 'metadata-delete', '-cn', ut_id(gvar, 'clc2'), '-mn', 'invalid-unit-test', '-Y']
    )

    execute_csv2_command(
        gvar, 0, None, 'cloud metadata file "{}::{}::{}" successfully deleted.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2'), ut_id(gvar, 'clm1')),
        ['cloudscheduler', 'cloud', 'metadata-delete', '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm1'), '-Y']
    )

    execute_csv2_command(
        gvar, 0, None, 'cloud metadata file "{}::{}::{}" successfully deleted.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2'), ut_id(gvar, 'clm3')),
        ['cloudscheduler', 'cloud', 'metadata-delete', '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm3'), '-Y', '-s', 'unit-test']
    )

if __name__ == "__main__":
    main(None)
