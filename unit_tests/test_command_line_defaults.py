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
        gvar, 1, None, 'No action specified for object "defaults"',
        ['cloudscheduler', 'defaults']
    )

    execute_csv2_command(
        gvar, 1, None, 'Invalid action "invalid-unit-test" for object "defaults"',
        ['cloudscheduler', 'defaults', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler defaults".',
        ['cloudscheduler', 'defaults', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'defaults', '-H']
    )

    #### SET ####

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'defaults', 'set']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'defaults', 'set', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler defaults set".',
        ['cloudscheduler', 'defaults', 'set', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'defaults', 'set', '-H']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'defaults', 'set', '-s', ut_id(gvar, 'cld1')]
    )

    #### LIST ####

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'defaults', 'list']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'defaults', 'list', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler defaults list".',
        ['cloudscheduler', 'defaults', 'list', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'defaults', 'list', '-H']
    )

    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'defaults', 'list', '-s', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Rows: 1',
        ['cloudscheduler', 'defaults', 'list', '-s', ut_id(gvar, 'cld1')]
    )

    #### DELETE ####

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'defaults', 'delete']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'defaults', 'delete', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler defaults delete".',
        ['cloudscheduler', 'defaults', 'delete', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'defaults', 'delete', '-H']
    )

    execute_csv2_command(
        gvar, 1, None, 'Settings for server "invalid-unit-test" do not exist.',
        ['cloudscheduler', 'defaults', 'delete', '-s', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'defaults', 'delete', '-s', ut_id(gvar, 'cld1'), '-Y']
    )

if __name__ == "__main__":
    main(None)