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

    # 01 - 14
    sanity_commands(gvar, 'cloud', 'metadata-delete')

    # 15
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specified on the command line:',
        ['cloud', 'metadata-delete', '-g', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu3')]
    )

    # 16
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: metadata-mime-type',
        ['cloud', 'metadata-delete', '-mmt', 'invalid-unit-test', '-su', ut_id(gvar, 'clu3')]
    )

    # 17 Attempt to delete metadata that does not exist.
    execute_csv2_command(
        gvar, 1, None, 'cannot delete "{}::invalid-unit-test::invalid-unit-test", file doesn\'t exist.'.format(ut_id(gvar, 'clg1')),
        ['cloud', 'metadata-delete', '--cloud-name', 'invalid-unit-test', '--metadata-name', 'invalid-unit-test', '-Y', '-su', ut_id(gvar, 'clu3')]
    )

    # 18 Attempt to delete metadata from a cloud that does not exist.
    execute_csv2_command(
        gvar, 1, None, 'the request did not match any rows.',
        ['cloud', 'metadata-delete', '--cloud-name', ut_id(gvar, 'clc2'), '--metadata-name', 'invalid-unit-test', '-Y', '-su', ut_id(gvar, 'clu3')]
    )

    # 19
    execute_csv2_command(
        gvar, 0, None, 'cloud metadata file "{}::{}::{}" successfully deleted.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2'), ut_id(gvar, 'clm1')),
        ['cloud', 'metadata-delete', '--cloud-name', ut_id(gvar, 'clc2'), '--metadata-name', ut_id(gvar, 'clm1'), '-Y', '-su', ut_id(gvar, 'clu3')]
    )

if __name__ == "__main__":
    main(None)
