from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id
from os import environ
from sys import argv

# lno: CV - error code identifier.

EDIT_SCRIPT_DIR = 'metadata_edit_scripts'
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
        ['cloudscheduler', 'cloud', 'metadata-edit', '-su', ut_id(gvar, 'clu4')]
    )

    # 02
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'cloud', 'metadata-edit', '-xx', 'yy', '-su', ut_id(gvar, 'clu4')]
    )

    # 03
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: metadata-mime-type',
        ['cloudscheduler', 'cloud', 'metadata-edit', '-mmt', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 04
    execute_csv2_command(
        gvar, None, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'cloud', 'metadata-edit', '-s', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')], timeout=8
    )

    # 05
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'metadata-edit', '-su', ut_id(gvar, 'clu4')]
    )

    # 06
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler cloud metadata-edit".',
        ['cloudscheduler', 'cloud', 'metadata-edit', '-h', '-su', ut_id(gvar, 'clu4')]
    )

    # 07
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'cloud', 'metadata-edit', '-H', '-su', ut_id(gvar, 'clu4')]
    )

    # 08
    execute_csv2_command(
        gvar, 1, None, 'Expose API requested',
        ['cloudscheduler', 'cloud', 'metadata-edit', '-xA', '-su', ut_id(gvar, 'clu4')]
    )

    # 09
    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'cloud', 'metadata-edit', '-g', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 10
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'metadata-edit', '-g', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu4')]
    )

    # 11
    execute_csv2_command(
        gvar, 1, None, 'no value, neither default nor command line, for the following required parameters',
        ['cloudscheduler', 'cloud', 'metadata-edit', '-cn', 'invalid-unit-test', '-mn', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )
    
    # 12
    execute_csv2_command(
        gvar, 1, None, 'received an invalid metadata file id "{}::invalid-unit-test::invalid-unit-test".'.format(ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'cloud', 'metadata-edit', '-cn', 'invalid-unit-test', '-mn', 'invalid-unit-test', '-te', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 13
    execute_csv2_command(
        gvar, 1, None, 'received an invalid metadata file id "{}::{}::invalid-unit-test".'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2')),
        ['cloudscheduler', 'cloud', 'metadata-edit', '-cn', ut_id(gvar, 'clc2'), '-mn', 'invalid-unit-test', '-te', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 14
    execute_csv2_command(
        gvar, 1, None, 'received an invalid metadata file id "{}::invalid-unit-test::{}".'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clm2')),
        ['cloudscheduler', 'cloud', 'metadata-edit', '-cn', 'invalid-unit-test', '-mn', ut_id(gvar, 'clm2'), '-te', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 15
    execute_csv2_command(
        gvar, 1, None, None,
        ['cloudscheduler', 'cloud', 'metadata-edit', '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm2'), '-te', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    environ['EDITOR'] = '{}/editscript5'.format(EDIT_SCRIPT_DIR)

    # 16
    execute_csv2_command(
        gvar, 0, None, 'completed, no changes.',
        ['cloudscheduler', 'cloud', 'metadata-edit', '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm2'), '-su', ut_id(gvar, 'clu4')]
    )

    environ.pop('EDITOR')

    # 17
    execute_csv2_command(
        gvar, 1, None, 'Error: "cloudscheduler cloud metadata-edit" - no value, neither default nor command line, for the following required parameters:',
        ['cloudscheduler', 'cloud', 'metadata-edit', '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm2'), '-su', ut_id(gvar, 'clu4')]
    )

    # The edit scripts in the next 8 tests will break easily as they rely on some system variables
    # 18
    execute_csv2_command(
        gvar, 0, None, 'completed, no changes.',
        ['cloudscheduler', 'cloud', 'metadata-edit', '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm2'), '-te', '{}/editscript5'.format(EDIT_SCRIPT_DIR), '-su', ut_id(gvar, 'clu4')]
    )

    # 19
    execute_csv2_command(
        gvar, 0, None, 'successfully  updated.',
        ['cloudscheduler', 'cloud', 'metadata-edit', '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm2'), '-te', '{}/editscript6'.format(EDIT_SCRIPT_DIR), '-su', ut_id(gvar, 'clu4')]
    )

    # 20
    execute_csv2_command(
        gvar, 0, None, 'successfully  updated.',
        ['cloudscheduler', 'cloud', 'metadata-edit', '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm2.yaml'), '-te', '{}/editscript7'.format(EDIT_SCRIPT_DIR), '-su', ut_id(gvar, 'clu4')]
    )

    # 21
    execute_csv2_command(
        gvar, 1, None, 'Invalid yaml file "scanner error": mapping values are not allowed here',
        ['cloudscheduler', 'cloud', 'metadata-edit', '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm2.yaml'), '-te', '{}/editscript8'.format(EDIT_SCRIPT_DIR), '-su', ut_id(gvar, 'clu4')]
    )

if __name__ == "__main__":
    main(None)
