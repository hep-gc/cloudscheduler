from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id
from os import environ
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
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'metadata-edit']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'cloud', 'metadata-edit', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: metadata-mime-type',
        ['cloudscheduler', 'cloud', 'metadata-edit', '-mmt', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'cloud', 'metadata-edit', '-s', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'metadata-edit', '-s', 'unit-test-un']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler cloud metadata-edit".',
        ['cloudscheduler', 'cloud', 'metadata-edit', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'cloud', 'metadata-edit', '-H']
    )

    execute_csv2_command(
        gvar, 1, None, 'Expose API requested',
        ['cloudscheduler', 'cloud', 'metadata-edit', '-xA']
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'cloud', 'metadata-edit', '-g', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'cloud', 'metadata-edit', '-g', ut_id(gvar, 'clg1')]
    )

    execute_csv2_command(
        gvar, 1, None, 'no value, neither default nor command line, for the following required parameters',
        ['cloudscheduler', 'cloud', 'metadata-edit', '-cn', 'invalid-unit-test', '-mn', 'invalid-unit-test']
    )
    
    execute_csv2_command(
        gvar, 1, None, 'received an invalid metadata file id "{}::invalid-unit-test::invalid-unit-test".'.format(ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'cloud', 'metadata-edit', '-cn', 'invalid-unit-test', '-mn', 'invalid-unit-test', '-te', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'received an invalid metadata file id "{}::{}::invalid-unit-test".'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2')),
        ['cloudscheduler', 'cloud', 'metadata-edit', '-cn', ut_id(gvar, 'clc2'), '-mn', 'invalid-unit-test', '-te', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'received an invalid metadata file id "{}::invalid-unit-test::{}".'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clm2')),
        ['cloudscheduler', 'cloud', 'metadata-edit', '-cn', 'invalid-unit-test', '-mn', ut_id(gvar, 'clm2'), '-te', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, None,
        ['cloudscheduler', 'cloud', 'metadata-edit', '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm2'), '-te', 'invalid-unit-test']
    )

    environ['EDITOR'] = './editscript5'

    execute_csv2_command(
        gvar, 0, None, 'completed, no changes.',
        ['cloudscheduler', 'cloud', 'metadata-edit', '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm2')]
    )

    environ.pop('EDITOR')

    execute_csv2_command(
        gvar, 1, None, 'Error: "cloudscheduler cloud metadata-edit" - no value, neither default nor command line, for the following required parameters:',
        ['cloudscheduler', 'cloud', 'metadata-edit', '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm2')]
    )

    # The edit scripts in the next 8 tests will break easily as they rely on some system variables
    execute_csv2_command(
        gvar, 0, None, 'completed, no changes.',
        ['cloudscheduler', 'cloud', 'metadata-edit', '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm2'), '-te', './editscript5']
    )

    execute_csv2_command(
        gvar, 0, None, 'successfully  updated.',
        ['cloudscheduler', 'cloud', 'metadata-edit', '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm2'), '-te', './editscript6-un']
    )

    execute_csv2_command(
        gvar, 0, None, 'successfully  updated.',
        ['cloudscheduler', 'cloud', 'metadata-edit', '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm2.yaml'), '-te', './editscript7-un']
    )

    execute_csv2_command(
        gvar, 1, None, 'Invalid yaml file "scanner error": mapping values are not allowed here',
        ['cloudscheduler', 'cloud', 'metadata-edit', '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm2.yaml'), '-te', './editscript8-un']
    )

    execute_csv2_command(
        gvar, 0, None, 'completed, no changes.',
        ['cloudscheduler', 'cloud', 'metadata-edit', '-g', ut_id(gvar, 'clg1'), '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm2'), '-te', './editscript5', '-s', 'unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'successfully  updated.',
        ['cloudscheduler', 'cloud', 'metadata-edit', '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm2'), '-te', './editscript6']
    )

    execute_csv2_command(
        gvar, 0, None, 'successfully  updated.',
        ['cloudscheduler', 'cloud', 'metadata-edit', '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm2.yaml'), '-te', './editscript7']
    )

    execute_csv2_command(
        gvar, 1, None, 'Invalid yaml file "scanner error": mapping values are not allowed here',
        ['cloudscheduler', 'cloud', 'metadata-edit', '-cn', ut_id(gvar, 'clc2'), '-mn', ut_id(gvar, 'clm2.yaml'), '-te', './editscript8']
    )

if __name__ == "__main__":
    main(None)
