from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id # pylint: disable=E0401
from sys import argv

# lno: SV - error code identifier.

def main(gvar, user_secret):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv2_request(gvar, argv[0])

    # set profile
    execute_csv2_command(
        gvar, 1, None, 'You are not authorized to access object "server";',
        ['cloudscheduler', 'server', 'config', '-s', 'unit-test-un']
    )

    # set profile
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'server', 'config', '-s', 'unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}'.format(ut_id(gvar, '')[:-1]),
        ['cloudscheduler', 'server', 'config']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'server', 'config', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: group-name',
        ['cloudscheduler', 'server', 'config', '-gn', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'server', 'config', '-s', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'server', 'config', '-s', 'unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler server config".',
        ['cloudscheduler', 'server', 'config', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'server', 'config', '-H']
    )

    execute_csv2_command(
        gvar, 0, None, 'Expose API requested',
        ['cloudscheduler', 'server', 'config', '-xA']
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'server', 'config', '-g', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, '')[:-1], ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'server', 'config', '-g', ut_id(gvar, 'clg1')]
    )

    execute_csv2_command(
        gvar, 1, 'SV', 'server config update value specified for "category" must be one of the following options:',
        ['cloudscheduler', 'server', 'config', '-cc', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'SV', 'server config must specify at least one field to update.',
        ['cloudscheduler', 'server', 'config', '-cc', 'web_frontend']
    )

    execute_csv2_command(
        gvar, 1, 'SV', 'server config update failed - the request did not match any rows',
        ['cloudscheduler', 'server', 'config', '-cc', 'web_frontend', '-c', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'SV', 'server config update value specified for "log_level" must be an integer value.',
        ['cloudscheduler', 'server', 'config', '-cc', 'csjobs.py', '-ll', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'SV', r'server config update value specified for "enable_glint" must be one of the following options: [\'False\', \'True\'].',
        ['cloudscheduler', 'server', 'config', '-cc', 'web_frontend', '-eg', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'server config successfully updated',
        ['cloudscheduler', 'server', 'config', '-cc', 'web_frontend', '-lf', '/var/log/cloudscheduler/csv2_web_update.log', '-eg', 'True']
    )

    execute_csv2_command(
        gvar, 0, None, 'server config successfully updated',
        ['cloudscheduler', 'server', 'config', '-cc', 'csjobs.py', '-ll', '10']
    )

    execute_csv2_command(
        gvar, 0, None, 'server config successfully updated',
        ['cloudscheduler', 'server', 'config', '-cc', 'web_frontend', '-lf', '/var/log/cloudscheduler/csv2_web.log', '-eg', 'False']
    )

    execute_csv2_command(
        gvar, 0, None, 'server config successfully updated',
        ['cloudscheduler', 'server', 'config', '-cc', 'csjobs.py', '-ll', '20']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'server', 'config', '-ok'],
        list='Server Configuration', columns=['Category', 'Config', 'Key']
    )

    execute_csv2_command(
        gvar, 0, None, 'server config, 1. Server Configuration: keys=category,config_key, columns=config_type,config_value',
        ['cloudscheduler', 'server', 'config', '-VC']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'server', 'config', '-NV'],
        list='Server Configuration', columns=['Category', 'Config', 'Key', 'Config', 'Type', 'Config', 'Value']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'server', 'config', '-V', 'config_value'],
        list='Server Configuration', columns=['Category', 'Config', 'Key', 'Config', 'Value']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'server', 'config'],
        list='Server Configuration', columns=['Category', 'Config', 'Key', 'Config', 'Value']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'server', 'config', '-r'],
        list='Server Configuration', columns=['Key', 'Value']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'server', 'config', '-V', ''],
        list='Server Configuration', columns=['Category', 'Config', 'Key', 'Config', 'Type', 'Config', 'Value']
    )

if __name__ == "__main__":
    main(None, None)
