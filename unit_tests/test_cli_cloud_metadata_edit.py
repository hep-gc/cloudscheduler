from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id, sanity_commands, parameters_commands
from os import environ
from sys import argv

# lno: CV - error code identifier.

EDIT_SCRIPT_DIR = 'metadata_edit_scripts'

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)

    # 01 - 14
    sanity_commands(gvar, 'cloud', 'metadata-edit')

    parameters = {
        # 15 Omit --cloud-name.
        '--cloud-name': {'valid': ut_id(gvar, 'clc2'), 'test_cases': {
            # 16
            '': 'cloud metadata_fetch, value specified for "cloud_name" must not be the empty string.',
            # 17
            'invalid-unit-test': 'file "{}::invalid-unit-test::{}" does not exist.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clm2'))
        }, 'mandatory': True},
        # 18 Omit --metadata-name.
        '--metadata-name': {'valid': ut_id(gvar, 'clm2'), 'test_cases': {
            # 19
            '': 'cloud metadata_fetch, value specified for "metadata_name" must not be the empty string.',
            # 20
            'invalid-unit-test': 'file "{}::{}::invalid-unit-test" does not exist.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2'))
        }, 'mandatory': True},
        # 21 Omit --text-editor.
        '--text-editor': {'valid': '{}/editscript5'.format(EDIT_SCRIPT_DIR), 'test_cases': {
            # 22
            '': 'Error: no editor specified. Use either the "-te" option or set the EDITOR or VISUAL environment variables.',
            # 23
            'invalid-unit-test': 'Error: specified editor "invalid-unit-test" does not exist.'
        }, 'mandatory': True}
    }

    parameters_commands(gvar, 'cloud', 'metadata-edit', ut_id(gvar, 'clg1'), ut_id(gvar, 'clu3'), parameters)

    # 24
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: metadata-mime-type',
        ['cloud', 'metadata-edit', '-mmt', 'invalid-unit-test', '-g', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu3')]
    )

    # 25
    execute_csv2_command(
        gvar, 1, None, 'no value, neither default nor command line, for the following required parameters',
        ['cloud', 'metadata-edit', '--cloud-name', 'invalid-unit-test', '--metadata-name', 'invalid-unit-test', '-su', ut_id(gvar, 'clu3')]
    )
    
    # 26
    execute_csv2_command(
        gvar, 1, None, 'file "{}::invalid-unit-test::invalid-unit-test" does not exist.'.format(ut_id(gvar, 'clg1')),
        ['cloud', 'metadata-edit', '--cloud-name', 'invalid-unit-test', '--metadata-name', 'invalid-unit-test', '--text-editor', 'invalid-unit-test', '-su', ut_id(gvar, 'clu3')]
    )

    environ['EDITOR'] = '{}/editscript5'.format(EDIT_SCRIPT_DIR)

    # 27
    execute_csv2_command(
        gvar, 0, None, 'completed, no changes.',
        ['cloud', 'metadata-edit', '--cloud-name', ut_id(gvar, 'clc2'), '--metadata-name', ut_id(gvar, 'clm2'), '-su', ut_id(gvar, 'clu3')]
    )

    del environ['EDITOR']

    # 28
    execute_csv2_command(
        gvar, 1, None, 'Error: "cloudscheduler cloud metadata-edit" - no value, neither default nor command line, for the following required parameters:',
        ['cloud', 'metadata-edit', '--cloud-name', ut_id(gvar, 'clc2'), '--metadata-name', ut_id(gvar, 'clm2'), '-su', ut_id(gvar, 'clu3')]
    )

    # 29
    execute_csv2_command(
        gvar, 1, None, 'Invalid yaml file "scanner error": mapping values are not allowed here',
        ['cloud', 'metadata-edit', '--cloud-name', ut_id(gvar, 'clc2'), '--metadata-name', ut_id(gvar, 'clm2.yaml'), '--text-editor', '{}/editscript8'.format(EDIT_SCRIPT_DIR), '-su', ut_id(gvar, 'clu3')]
    )

    # The edit scripts in the following tests will break easily as they rely on some system variables.
    # 30
    execute_csv2_command(
        gvar, 0, None, 'completed, no changes.',
        ['cloud', 'metadata-edit', '--cloud-name', ut_id(gvar, 'clc2'), '--metadata-name', ut_id(gvar, 'clm2'), '--text-editor', '{}/editscript5'.format(EDIT_SCRIPT_DIR), '-su', ut_id(gvar, 'clu3')]
    )

    # 31 Known to fail if run twice without setup / cleanup in between.
    execute_csv2_command(
        gvar, 0, None, 'successfully updated.',
        ['cloud', 'metadata-edit', '--cloud-name', ut_id(gvar, 'clc2'), '--metadata-name', ut_id(gvar, 'clm2'), '--text-editor', '{}/editscript6'.format(EDIT_SCRIPT_DIR), '-su', ut_id(gvar, 'clu3')]
    )

    # 32 Known to fail if run twice without setup / cleanup in between.
    execute_csv2_command(
        gvar, 0, None, 'successfully updated.',
        ['cloud', 'metadata-edit', '--cloud-name', ut_id(gvar, 'clc2'), '--metadata-name', ut_id(gvar, 'clm2.yaml'), '--text-editor', '{}/editscript7'.format(EDIT_SCRIPT_DIR), '-su', ut_id(gvar, 'clu3')]
    )

if __name__ == "__main__":
    main(None)
