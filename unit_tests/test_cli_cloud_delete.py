from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id, sanity_commands
from sys import argv

# lno: CV - error code identifier.

def main(gvar):

    # 01 - 14
    sanity_commands(gvar, 'cloud', 'delete')

    # 15
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: metadata-mime-type',
        ['cloud', 'delete', '-mmt', 'invalid-unit-test', '-g', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu3')]
    )

    # 16
    execute_csv2_command(
        gvar, 1, None, 'cannot delete "invalid-unit-test", cloud doesn\'t exist in group "{}".'.format(ut_id(gvar, 'clg1')),
        ['cloud', 'delete', '-cn', 'invalid-unit-test', '-su', ut_id(gvar, 'clu3')]
    )

    # 17
    execute_csv2_command(
        gvar, -1, None, 'Are you sure you want to delete cloud "{}::{}"?'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc1')),
        ['cloud', 'delete', '-cn', ut_id(gvar, 'clc1'), '-su', ut_id(gvar, 'clu3')], timeout=8
    )

    # 18
    execute_csv2_command(
        gvar, 0, None, 'cloud "{}::{}" successfully deleted.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc1')),
        ['cloud', 'delete', '-cn', ut_id(gvar, 'clc1'), '-Y', '-su', ut_id(gvar, 'clu3')]
    )

if __name__ == "__main__":
    main(initialize_csv2_request(selections=argv[1] if len(argv) > 1 else ''))
