from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id
import sys

def main(gvar, user_secret):
    if not gvar:
        gvar = {}
        if len(sys.argv) > 1:
            initialize_csv2_request(gvar, sys.argv[0], selections=sys.argv[1])
        else:
            initialize_csv2_request(gvar, sys.argv[0])

    execute_csv2_command(
        gvar, 1, None, 'No action specified for object "vm"',
        ['cloudscheduler', 'vm']
    )

    execute_csv2_command(
        gvar, 1, None, 'Invalid action "invalid-unit-test" for object "vm"',
        ['cloudscheduler', 'vm', 'invalid-unit-test']
    )

    #### LIST ####
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'vm', 'list', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'vm', 'list', '-g', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, '')[:-1], ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'vm', 'list', '-g', ut_id(gvar, 'clg1')]
    )

    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, '')[:-1], ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'vm', 'list']
    )

    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, '')[:-1], ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'vm', 'list', '-ok']
    )

    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'vm', 'list', '-cn', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'vm', 'list', '-vc', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'vm', 'list', '-vd', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-ved\', \'invalid-unit-test\']',
        ['cloudscheduler', 'vm', 'list', '-ved', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'vm', 'list', '-vF', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'vm', 'list', '-vf', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'vm', 'list', '-vk', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'vm', 'list', '-vr', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'vm', 'list', '-vS', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'vm', 'list', '-vs', 'invalid-unit-test']
    )

    #### UPDATE ####

if __name__ == "__main__":
    main(None)

