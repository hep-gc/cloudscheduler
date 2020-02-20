from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id
from sys import argv

# lno: CV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)
    # 01
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'metadata-update', '-su', ut_id(gvar, 'clu4')]
    )

    # 02
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'cloud', 'metadata-update', '-xx', 'yy', '-su', ut_id(gvar, 'clu4')]
    )

    # 03
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: cloud-project',
        ['cloudscheduler', 'cloud', 'metadata-update', '-cP', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 04
    execute_csv2_command(
        gvar, None, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'cloud', 'metadata-update', '-s', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')], timeout=8
    )

    # 05
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'metadata-update', '-su', ut_id(gvar, 'clu4')]
    )

    # 06
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler cloud metadata-update".',
        ['cloudscheduler', 'cloud', 'metadata-update', '-h', '-su', ut_id(gvar, 'clu4')]
    )

    # 07
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'cloud', 'metadata-update', '-H', '-su', ut_id(gvar, 'clu4')]
    )

    # 08
    execute_csv2_command(
        gvar, 1, None, 'Expose API requested',
        ['cloudscheduler', 'cloud', 'metadata-update', '-xA', '-su', ut_id(gvar, 'clu4')]
    )

    # 09
    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'cloud', 'metadata-update', '-g', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 10
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'metadata-update', '-g', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu4')]
    )

    # 11
    execute_csv2_command(
        gvar, 1, None, 'requires at least one option to modify.',
        ['cloudscheduler', 'cloud', 'metadata-update', '-cn', 'invalid-unit-test', '-mn', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 12
    execute_csv2_command(
        gvar, 1, 'CV', 'the request did not match any rows.',
        ['cloudscheduler', 'cloud', 'metadata-update', '-cn', 'invalid-unit-test', '-mn', 'invalid-unit-test', '-me', '0', '-su', ut_id(gvar, 'clu4')]
    )

    # 13
    execute_csv2_command(
        gvar, 1, 'CV', 'the request did not match any rows.',
        ['cloudscheduler', 'cloud', 'metadata-update', '-cn', ut_id(gvar, 'clc2'), '-mn', 'invalid-unit-test', '-me', '0', '-su', ut_id(gvar, 'clu4')]
    )

    # 14
    execute_csv2_command(
        gvar, 1, 'CV', 'boolean value specified for "enabled" must be one of the following: true, false, yes, no, 1, or 0.',
        ['cloudscheduler', 'cloud', 'metadata-update', '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm2'), '-me', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 15
    execute_csv2_command(
        gvar, 1, 'CV', 'value specified for "mime_type" must be one of the following options: [\'cloud-config\', \'ucernvm-config\'].',
        ['cloudscheduler', 'cloud', 'metadata-update', '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm2'), '-mmt', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 16
    execute_csv2_command(
        gvar, 1, 'CV', 'value specified for "priority" must be an integer value.',
        ['cloudscheduler', 'cloud', 'metadata-update', '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm2'), '-mp', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 17
    execute_csv2_command(
        gvar, 0, None, 'file "{}::{}::{}" successfully  updated.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2'), ut_id(gvar, 'clm2')),
        ['cloudscheduler', 'cloud', 'metadata-update', '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm2'), '-me', 'false', '-su', ut_id(gvar, 'clu4')]
    )

    # 18
    execute_csv2_command(
        gvar, 0, None, 'file "{}::{}::{}" successfully  updated.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2'), ut_id(gvar, 'clm2')),
        ['cloudscheduler', 'cloud', 'metadata-update', '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm2'), '-mmt', 'ucernvm-config', '-su', ut_id(gvar, 'clu4')]
    )

    # 19
    execute_csv2_command(
        gvar, 0, None, 'file "{}::{}::{}" successfully  updated.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2'), ut_id(gvar, 'clm2')),
        ['cloudscheduler', 'cloud', 'metadata-update', '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm2'), '-mp', '1', '-su', ut_id(gvar, 'clu4')]
    )

    # 20
    execute_csv2_command(
        gvar, 0, None, 'file "{}::{}::{}" successfully  updated.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2'), ut_id(gvar, 'clm2')),
        ['cloudscheduler', 'cloud', 'metadata-update', '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm2'), '-mp', '1', '-g', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu4')]
    )

if __name__ == "__main__":
    main(None)
