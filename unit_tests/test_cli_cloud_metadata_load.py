from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id, sanity_commands
from sys import argv

# lno: CV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)

    METADATA_FILEPATH = 'ut.yaml'

    # 01 - 14
    sanity_commands(gvar, 'cloud', 'metadata-load')

    parameters = {
        '--cloud_name': {'valid': ut_id(gvar, 'clc2'), 'test_cases': {
            '': 'TODO',
            'invalid-unit-test': 'cloud name  "invalid-unit-test" does not exist.'
        }, 'mandatory': True},
        '--metadata-name': {'valid': ut_id(gvar, 'clm2'), 'test_cases': {
            '': 'TODO',
            'invalid-unit-Test': 'TODO',
            'invalid-unit-test-': 'TODO',
            'invalid-unit-test!': 'TODO',
            'metadata-name-that-is-too-long-for-the-database': 'TODO'
        }, 'mandatory': True},
        '--file-path': {'valid': METADATA_FILEPATH, 'test_cases': {
            '': 'TODO',
            'invalid-unit-test': 'The specified metadata file "invalid-unit-test" does not exist.'
        }, 'mandatory': True},
        '--metadata-enabled': {'valid': 0, 'test_cases': {'invalid-unit-test': 'boolean value specified for "enabled" must be one of the following: true, false, yes, no, 1, or 0.'}}
        '--metadata-mime-type': {'valid': 'cloud-config': {'invalid-unit-test': 'value specified for "mime_type" must be one of the following options: [\'cloud-config\', \'ucernvm-config\'].'}}
        '--priority': {'valid': 0, 'test_cases': {'invalid-unit-test': 'value specified for "priority" must be an integer value.'}}

    # 01
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloud', 'metadata-load', '-g', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu4')]
    )

    # 03
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: only-keys',
        ['cloud', 'metadata-load', '-ok', '-su', ut_id(gvar, 'clu4')]
    )

    # 16
    execute_csv2_command(
        gvar, 1, 'CV', 'value specified for "metadata (metadata_name)" is invalid - scanner error',
        ['cloud', 'metadata-load', '-cn', ut_id(gvar, 'clc2'), '-f', 'notyamlfile.txt', '-mn', 'invalid-unit-test.yaml', '-su', ut_id(gvar, 'clu4')]
    )

    # 17
    execute_csv2_command(
        gvar, 0, None, 'file "{}::{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2'), ut_id(gvar, 'clm10')),
        ['cloud', 'metadata-load', '-cn', ut_id(gvar, 'clc2'), '-f', 'notyamlfile.txt', '-mn', ut_id(gvar, 'clm10'), '-su', ut_id(gvar, 'clu4')]
    )

    # 18
    execute_csv2_command(
        gvar, 0, None, 'file "{}::{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2'), ut_id(gvar, 'clm10.yaml')),
        ['cloud', 'metadata-load', '-cn', ut_id(gvar, 'clc2'), '-f', 'ut.yaml', '-mn', ut_id(gvar, 'clm10.yaml'), '-su', ut_id(gvar, 'clu4')]
    )

    # 19
    execute_csv2_command(
        gvar, 0, None, 'file "{}::{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2'), ut_id(gvar, 'clm11')),
        ['cloud', 'metadata-load', '-cn', ut_id(gvar, 'clc2'), '-f', 'notyamlfile.txt', '-mn', ut_id(gvar, 'clm11'), '-g', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu4')]
    )

if __name__ == "__main__":
    main(None)
