from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id
from sys import argv

# lno: UV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)

    #### DELETE ####
    # 35
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['user', 'delete', '-su', ut_id(gvar, 'clu4')]
    )

    # 36
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['user', 'delete', '-xx', 'yy', '-su', ut_id(gvar, 'clu4')]
    )

    # 37
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: group-option',
        ['user', 'delete', '-go', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 38
    execute_csv2_command(
        gvar, None, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['user', 'delete', '-s', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')], timeout=8
    )

    # 39
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler user delete".',
        ['user', 'delete', '-h', '-su', ut_id(gvar, 'clu4')]
    )

    # 40
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['user', 'delete', '-H', '-su', ut_id(gvar, 'clu4')]
    )

    # 41
    execute_csv2_command(
        gvar, 1, None, 'Expose API requested',
        ['user', 'delete', '-xA', '-su', ut_id(gvar, 'clu4')]
    )
    
    # 42
    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['user', 'delete', '-g', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 43 We have to specify the server and server password explicitly because -un has to be the last parameter.
    execute_csv2_command(
        gvar, 1, None, 'Value omitted for option: -un | --username',
        ['user', 'delete', '-s', 'unit-test', '-su', ut_id(gvar, 'clu4'), '-spw', gvar['user_secret'], '-un']
    )

    # 44
    execute_csv2_command(
        gvar, 1, None, 'cannot delete "invalid-unit-test", user doesn\'t exist.',
        ['user', 'delete', '-un', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 45
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully deleted.'.format(ut_id(gvar, 'clu5')),
        ['user', 'delete', '-un', ut_id(gvar, 'clu5'), '-Y', '-su', ut_id(gvar, 'clu4')]
    )

    # 46
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully deleted.'.format(ut_id(gvar, 'clu6')),
        ['user', 'delete', '-un', ut_id(gvar, 'clu6'), '-Y', '-su', ut_id(gvar, 'clu4')]
    )

if __name__ == "__main__":
    main(None)
