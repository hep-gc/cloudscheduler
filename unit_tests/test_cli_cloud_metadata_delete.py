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

    # 01
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line:',
        ['cloudscheduler', 'cloud', 'metadata-delete']
    )

    # 02
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'cloud', 'metadata-delete', '-xx', 'yy']
    )

    # 03
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: metadata-mime-type',
        ['cloudscheduler', 'cloud', 'metadata-delete', '-mmt', 'invalid-unit-test']
    )

    # 04
    execute_csv2_command(
        gvar, None, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'cloud', 'metadata-delete', '-s', 'invalid-unit-test'], timeout=8
    )

    # 05
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'metadata-delete']
    )

    # 06
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler cloud metadata-delete".',
        ['cloudscheduler', 'cloud', 'metadata-delete', '-h']
    )

    # 07
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'cloud', 'metadata-delete', '-H']
    )

    # 08
    execute_csv2_command(
        gvar, 1, None, 'Expose API requested',
        ['cloudscheduler', 'cloud', 'metadata-delete', '-xA']
    )

    # 09
    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'cloud', 'metadata-delete', '-g', 'invalid-unit-test']
    )

    # 10
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'metadata-delete', '-g', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu4'), '-spw', user_secret]
    )

    # 11
    execute_csv2_command(
        gvar, 1, None, 'cannot delete "{}::invalid-unit-test::invalid-unit-test", file doesn\'t exist.'.format(ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'cloud', 'metadata-delete', '-cn', 'invalid-unit-test', '-mn', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4'), '-spw', user_secret]
    )

    # 12
    execute_csv2_command(
        gvar, 1, None, 'the request did not match any rows.',
        ['cloudscheduler', 'cloud', 'metadata-delete', '-cn', ut_id(gvar, 'clc2'), '-mn', 'invalid-unit-test', '-Y', '-su', ut_id(gvar, 'clu4'), '-spw', user_secret]
    )

    # 13
    execute_csv2_command(
        gvar, 0, None, 'cloud metadata file "{}::{}::{}" successfully deleted.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2'), ut_id(gvar, 'clm1')),
        ['cloudscheduler', 'cloud', 'metadata-delete', '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm1'), '-Y', '-su', ut_id(gvar, 'clu4'), '-spw', user_secret]
    )

    # 14
    execute_csv2_command(
        gvar, 0, None, 'cloud metadata file "{}::{}::{}" successfully deleted.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2'), ut_id(gvar, 'clm3')),
        ['cloudscheduler', 'cloud', 'metadata-delete', '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm3'), '-Y', '-su', ut_id(gvar, 'clu4'), '-spw', user_secret, '-s', 'unit-test']
    )

if __name__ == "__main__":
    main(None, None)
