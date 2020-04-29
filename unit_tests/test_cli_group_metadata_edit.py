from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id, sanity_commands, parameters_commands
from os import environ
from sys import argv

# lno: GV - error code identifier.

EDIT_SCRIPT_DIR = 'metadata_edit_scripts'

def main(gvar):
    
    # 01 - 14
    sanity_commands(gvar, 'metadata', 'edit')

    # Necessary to ensure that failing to specify `--text-editor` produces an error.
    environ.pop('EDITOR', None)
    parameters = {
        # 15 Omit `--metadata_name`.
        '--metadata-name': {'valid': ut_id(gvar, 'clm2'), 'test_cases': {
            # 16
            '': 'value specified for "metadata_name" must not be the empty string.',
            # 17
            'invalid-unit-test': 'file "{}::invalid-unit-test" does not exist.'.format(ut_id(gvar, 'clg1')),
        }, 'mandatory': True},
        # 18 Omit `--text-editor`.
        '--text-editor': {'valid': '{}/editscript1'.format(EDIT_SCRIPT_DIR), 'test_cases': {
            # 19
            '': 'no editor specified. Use either the "-te" option or set the EDITOR or VISUAL environment variables.',
            # 20
            'invalid-unit-test': 'specified editor "invalid-unit-test" does not exist.',
        }, 'mandatory': True}
    }

    parameters_commands(gvar, 'metadata', 'edit', ut_id(gvar, 'clg1'), ut_id(gvar, 'clu3'), parameters)

    # 21
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: job-cores',
        ['metadata', 'edit', '-mn', ut_id(gvar, 'clm2'), '-te', '{}/editscript1'.format(EDIT_SCRIPT_DIR), '-jc', 'invalid-unit-test', '-g', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu3')]
    )

    # 22
    execute_csv2_command(
        gvar, 1, None, 'Invalid yaml file "scanner error": mapping values are not allowed here',
        ['metadata', 'edit', '-mn', ut_id(gvar, 'clm2.yaml'), '-te', '{}/editscript4'.format(EDIT_SCRIPT_DIR), '-su', ut_id(gvar, 'clu3')]
    )

    # If we do not specify `--text-editor`, the CLI should use `environ['EDITOR']` if it is set.
    environ['EDITOR'] = '{}/editscript1'.format(EDIT_SCRIPT_DIR)
    # 23
    execute_csv2_command(
        gvar, 0, None, 'completed, no changes.',
        ['metadata', 'edit', '-mn', ut_id(gvar, 'clm2'), '-su', ut_id(gvar, 'clu3')]
    )
    environ.pop('EDITOR', None)

    # The edit scripts in the following tests will break easily as they rely on some system variables.
    # 24
    execute_csv2_command(
        gvar, 0, None, '"{}::{}" completed, no changes.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clm2')),
        ['metadata', 'edit', '-mn', ut_id(gvar, 'clm2'), '-te', '{}/editscript1'.format(EDIT_SCRIPT_DIR), '-su', ut_id(gvar, 'clu3')]
    )

    # 25 Known to fail if run twice without setup / cleanup in between.
    execute_csv2_command(
        gvar, 0, None, '"{}::{}" successfully  updated.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clm2')),
        ['metadata', 'edit', '-mn', ut_id(gvar, 'clm2'), '-te', '{}/editscript2'.format(EDIT_SCRIPT_DIR), '-su', ut_id(gvar, 'clu3')]
    )

    # 26 Known to fail if run twice without setup / cleanup in between.
    execute_csv2_command(
        gvar, 0, None, '"{}::{}" successfully  updated.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clm2.yaml')),
        ['metadata', 'edit', '-mn', ut_id(gvar, 'clm2.yaml'), '-te', '{}/editscript3'.format(EDIT_SCRIPT_DIR), '-su', ut_id(gvar, 'clu3')]
    )

if __name__ == "__main__":
    main(initialize_csv2_request(selections=argv[1] if len(argv) > 1 else ''))
