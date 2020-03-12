from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id, sanity_commands
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

    # 15
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specified on the command line',
        ['metadata', 'delete', '-su', ut_id(gvar, 'clu3')]
    )

    # 16
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'--invalid-unit-test\', \'invalid-unit-test\']',
        ['metadata', 'delete', '--invalid-unit-test', 'invalid-unit-test', '-g', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu4')]
    )

    # 17
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: job-cores',
        ['metadata', 'delete', '-jc', 'invalid-unit-test', '-su', ut_id(gvar, 'clu3')]
    )

    # 18
    execute_csv2_command(
        gvar, 1, 'GV', 'the request did not match any rows.',
        ['metadata', 'delete', '-mn', 'invalid-unit-test', '-Y', '-su', ut_id(gvar, 'clu3')]
    )

    # 19
    execute_csv2_command(
        gvar, 0, None, 'group metadata file "{}::{}" successfully deleted.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clm1')),
        ['metadata', 'delete', '-mn', ut_id(gvar, 'clm1'), '-Y', '-su', ut_id(gvar, 'clu3')]
    )

if __name__ == "__main__":
    main(None)
