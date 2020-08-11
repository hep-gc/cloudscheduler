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
    sanity_commands(gvar, 'group', 'delete')

    # 15
    execute_csv2_command(
        gvar, 1, None, 'You are not authorized to access object "group";',
        ['group', 'delete', '-gn', ut_id(gvar, 'clg4'), '-Y', '-su', ut_id(gvar, 'clu3')]
    )

    parameters = {
        # 16 Omit `--group-name`.
        '--group-name': {'valid': ut_id(gvar, 'clg4'), 'test_cases': {
            # 17
            '': 'cannot delete "", group doesn\'t exist.',
            # 18
            'invalid-unit-test': 'cannot delete "invalid-unit-test", group doesn\'t exist.'
        }, 'mandatory': True}
    }

    # `group delete` rejects the `--group` option (not to be confused with `--group-name`), even though it is global.
    parameters_commands(gvar, 'group', 'delete', '', ut_id(gvar, 'clu4'), parameters, requires_confirmation=True)

    # 19
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: job-cores',
        ['group', 'delete', '-jc', 'invalid-unit-test', '-Y', '-su', ut_id(gvar, 'clu4')]
    )

    # 20
    execute_csv2_command(
        gvar, 0, None, 'group "{}" successfully deleted.'.format(ut_id(gvar, 'clg4')),
        ['group', 'delete', '-gn', ut_id(gvar, 'clg4'), '-Y', '-su', ut_id(gvar, 'clu4')]
    )

if __name__ == "__main__":
    main(None)
