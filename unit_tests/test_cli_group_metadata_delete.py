from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id, sanity_commands, parameters_commands
from sys import argv

# lno: GV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)

    # 01 - 14
    sanity_commands(gvar, 'metadata', 'delete')

    parameters = {
        # 15 Attempt without confirmation.
        # 16 Omit `--metadata-name`.
        '--metadata-name': {'valid': ut_id(gvar, 'clm1'), 'test_cases': {
            # 17
            '': '"cloudscheduler group metadata-delete" cannot delete "{}::", file doesn\'t exist.'.format(ut_id(gvar, 'clg1')),
            # 18
            'invalid-unit-test': '"cloudscheduler group metadata-delete" cannot delete "{}::invalid-unit-test", file doesn\'t exist.'.format(ut_id(gvar, 'clg1'))
        }, 'mandatory': True}
    }

    parameters_commands(gvar, 'metadata', 'delete', ut_id(gvar, 'clg1'), ut_id(gvar, 'clu3'), parameters, requires_confirmation=True)

    # 19
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: job-cores',
        ['metadata', 'delete', '-jc', 'invalid-unit-test', '-Y', '-su', ut_id(gvar, 'clu3')]
    )

    # 20
    execute_csv2_command(
        gvar, 0, None, 'group metadata file "{}::{}" successfully deleted.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clm1')),
        ['metadata', 'delete', '-mn', ut_id(gvar, 'clm1'), '-Y', '-su', ut_id(gvar, 'clu3')]
    )

if __name__ == "__main__":
    main(None)
