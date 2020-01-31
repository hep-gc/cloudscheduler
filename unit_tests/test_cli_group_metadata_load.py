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
        ['cloudscheduler', 'metadata', 'load', '-su', ut_id(gvar, 'clu4')]
    )

    # 02
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'metadata', 'load', '-xx', 'yy', '-su', ut_id(gvar, 'clu4')]
    )

    # 03
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: job-cores',
        ['cloudscheduler', 'metadata', 'load', '-jc', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 04
    execute_csv2_command(
        gvar, 1, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'metadata', 'load', '-mn', 'invalid-unit-test', '-f', 'ut.yaml', '-s', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 05
    execute_csv2_command(
        gvar, 1, None, None,
        ['cloudscheduler', 'metadata', 'load', '-su', ut_id(gvar, 'clu4')]
    )

    # 06
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler metadata load".',
        ['cloudscheduler', 'metadata', 'load', '-h', '-su', ut_id(gvar, 'clu4')]
    )

    # 07
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'metadata', 'load', '-H', '-su', ut_id(gvar, 'clu4')]
    )

    # 08
    execute_csv2_command(
        gvar, 0, None, 'Expose API requested',
        ['cloudscheduler', 'metadata', 'load', '-xA', '-mn', ut_id(gvar, 'clm11'), '-f', 'ut.yaml', '-su', ut_id(gvar, 'clu4')]
    )

    # 09
    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'metadata', 'load', '-g', 'invalid-unit-test', '-mn', 'invalid-unit-test', '-f', 'ut.yaml', '-su', ut_id(gvar, 'clu4')]
    )

    # 10
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'metadata', 'load', '-g', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu4')]
    )

    # 11
    execute_csv2_command(
        gvar, 1, None, 'The specified metadata file "invalid-unit-test" does not exist.',
        ['cloudscheduler', 'metadata', 'load', '-f', 'invalid-unit-test', '-mn', ut_id(gvar, 'cli-invalid-unit-test'), '-su', ut_id(gvar, 'clu4')]
    )

    # 12
    execute_csv2_command(
        gvar, 1, 'GV', 'boolean value specified for "enabled" must be one of the following: true, false, yes, no, 1, or 0.',
        ['cloudscheduler', 'metadata', 'load', '-f', 'ut.yaml', '-mn', ut_id(gvar, 'cli-invalid-unit-test'), '-me', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 13
    execute_csv2_command(
        gvar, 1, 'GV', r'value specified for "mime_type" must be one of the following options: [\'cloud-config\', \'ucernvm-config\'].',
        ['cloudscheduler', 'metadata', 'load', '-f', 'ut.yaml', '-mn', ut_id(gvar, 'cli-invalid-unit-test'), '-mmt', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 14
    execute_csv2_command(
        gvar, 1, 'GV', 'value specified for "priority" must be an integer value.',
        ['cloudscheduler', 'metadata', 'load', '-f', 'ut.yaml', '-mn', ut_id(gvar, 'cli-invalid-unit-test'), '-mp', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 15
    execute_csv2_command(
        gvar, 1, 'GV', 'value specified for "metadata (metadata_name)" is invalid - scanner error',
        ['cloudscheduler', 'metadata', 'load', '-f', 'notyamlfile.txt', '-mn', 'invalid-unit-test.yaml', '-su', ut_id(gvar, 'clu4')]
    )

    # 16
    execute_csv2_command(
        gvar, 0, None, 'file "{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clm10')),
        ['cloudscheduler', 'metadata', 'load', '-f', 'notyamlfile.txt', '-mn', ut_id(gvar, 'clm10'), '-su', ut_id(gvar, 'clu4')]
    )

    # 17
    execute_csv2_command(
        gvar, 0, None, 'file "{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clm10.yaml')),
        ['cloudscheduler', 'metadata', 'load', '-f', 'ut.yaml', '-mn', ut_id(gvar, 'clm10.yaml'), '-su', ut_id(gvar, 'clu4')]
    )

if __name__ == "__main__":
    main(None)
