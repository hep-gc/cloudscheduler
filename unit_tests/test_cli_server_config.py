from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id, sanity_commands, table_commands
from sys import argv

# lno: SV - error code identifier.

SERVER_CONFIG_COLUMNS = ['Category', 'Config Key', 'Type', 'Value']

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)

    # These tests change certain configuration keys, then blindly assume what the keys' original values were and attempt to change them back.
    # These assumed original values should be checked before running if you want the values on the server to be preserved.

    # 01 - 13
    sanity_commands(gvar, 'server')

    # 14 - 27
    sanity_commands(gvar, 'server', 'config')

    # 28
    execute_csv2_command(
        gvar, 1, None, 'You are not authorized to access object "server";',
        ['server', 'config', '-su', ut_id(gvar, 'clu3')]
    )

    # 29
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'clu4'), ut_id(gvar, 'clg1')),
        ['server', 'config', '-g', ut_id(gvar, 'clg1')],
        expected_list='Server Configuration', expected_columns=set(SERVER_CONFIG_COLUMNS)
    )

    # 30 Filter by category.
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'clu4'), ut_id(gvar, 'clg1')),
        ['server', 'config', '-cc', 'web_frontend'],
        expected_list='Server Configuration', expected_columns=set(SERVER_CONFIG_COLUMNS)
    )

    # 31
    execute_csv2_command(
        gvar, 0, None, 'server config, 1. Server Configuration: keys=category,config_key, columns=config_type,config_value',
        ['server', 'config', '-VC']
    )

    # 32 - 38
    table_headers = {'Server Configuration': ['Category', 'Config Key', 'Type', 'Value']}

    table_commands(gvar, 'server', 'config', ut_id(gvar, 'clg1'), ut_id(gvar, 'clu4'), table_headers)

    # 39
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: group-name',
        ['server', 'config', '-gn', 'invalid-unit-test']
    )

    # 40
    execute_csv2_command(
        gvar, 1, 'SV', 'server config update failed - invalid category "invalid-unit-test" specified.',
        ['server', 'config', '-cc', 'invalid-unit-test']
    )

    # 41
    execute_csv2_command(
        gvar, 1, 'SV', 'server config update failed - category="web_frontend", invalid key "invalid-unit-test" specified.',
        ['server', 'config', '-cc', 'web_frontend', '-ckv', 'invalid-unit-test=invalid-unit-test']
    )

    # 42
    execute_csv2_command(
        gvar, 1, 'SV', 'server config update failed - value specified ("invalid-unit-test") for category="condor_poller.py", config_key="log_level" must be an integer.',
        ['server', 'config', '-cc', 'condor_poller.py', '-ckv', 'log_level=invalid-unit-test']
    )

    # 43
    execute_csv2_command(
        gvar, 1, 'SV', 'server config update failed - value specified ("invalid-unit-test") for category="web_frontend", config_key="enable_glint" must be a boolean value.',
        ['server', 'config', '-cc', 'web_frontend', '-ckv', 'enable_glint=invalid-unit-test']
    )

    # Attempt to change real server settings.
    # 44
    execute_csv2_command(
        gvar, 0, None, 'server config update successfully updated the following keys: log_file, enable_glint',
        ['server', 'config', '-cc', 'web_frontend', '-ckv', 'log_file=/var/log/cloudscheduler/csv2_web_update.log,enable_glint=False']
    )

    # 45
    execute_csv2_command(
        gvar, 0, None, 'server config update successfully updated the following keys: log_level',
        ['server', 'config', '-cc', 'condor_poller.py', '-ckv', 'log_level=10']
    )

    # Change settings back to what we presume they were.
    # 46
    execute_csv2_command(
        gvar, 0, None, 'server config update successfully updated the following keys: log_file, enable_glint',
        ['server', 'config', '-cc', 'web_frontend', '-ckv', 'log_file=/var/log/cloudscheduler/csv2_web.log,enable_glint=True']
    )

    # 47
    execute_csv2_command(
        gvar, 0, None, 'server config update successfully updated the following keys: log_level',
        ['server', 'config', '-cc', 'condor_poller.py', '-ckv', 'log_level=20']
    )

if __name__ == "__main__":
    main(None)
