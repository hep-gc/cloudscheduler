from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id
from sys import argv

# lno: SV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)

    # 1
    execute_csv2_command(
        gvar, 1, None, 'You are not authorized to access object "server";',
        ['cloudscheduler', 'server', 'config', '-su', ut_id(gvar, 'clu3')]
    )

    # 2
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'server', 'config', '-xx', 'yy', '-su', ut_id(gvar, 'clu4')]
    )

    # 3
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: group-name',
        ['cloudscheduler', 'server', 'config', '-gn', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 4
    execute_csv2_command(
        gvar, None, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'server', 'config', '-s', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')], timeout=8
    )

    # 5
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler server config".',
        ['cloudscheduler', 'server', 'config', '-h', '-su', ut_id(gvar, 'clu4')]
    )

    # 6
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'server', 'config', '-H', '-su', ut_id(gvar, 'clu4')]
    )

    # 7
    execute_csv2_command(
        gvar, 0, None, 'Expose API requested',
        ['cloudscheduler', 'server', 'config', '-xA', '-su', ut_id(gvar, 'clu4')]
    )

    # 8
    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'server', 'config', '-g', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 9
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'clu4'), ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'server', 'config', '-g', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu4')]
    )

    # 10
    execute_csv2_command(
        gvar, 1, 'SV', 'server config update failed - invalid category "invalid-unit-test" specified.',
        ['cloudscheduler', 'server', 'config', '-cc', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 11
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'clu4'), ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'server', 'config', '-cc', 'web_frontend', '-su', ut_id(gvar, 'clu4')],
        expected_list='Server Configuration', columns=['Category', 'Config Key', 'Type', 'Value']
    )

    # 12
    execute_csv2_command(
        gvar, 1, 'SV', 'server config update failed - category="web_frontend", invalid key "invalid-unit-test" specified.',
        ['cloudscheduler', 'server', 'config', '-cc', 'web_frontend', '-ckv', 'invalid-unit-test=invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 13
    execute_csv2_command(
        gvar, 1, 'SV', 'server config update failed - value specified ("invalid-unit-test") for category="csjobs.py", config_key="log_level" must be an integer.',
        ['cloudscheduler', 'server', 'config', '-cc', 'csjobs.py', '-ckv', 'log_level=invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 14
    execute_csv2_command(
        gvar, 1, 'SV', 'server config update failed - value specified ("invalid-unit-test") for category="web_frontend", config_key="enable_glint" must be a boolean value.',
        ['cloudscheduler', 'server', 'config', '-cc', 'web_frontend', '-ckv', 'enable_glint=invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # Attempt to change real server settings.
    # 15
    execute_csv2_command(
        gvar, 0, None, 'server config update successfully updated the following keys: log_file, enable_glint',
        ['cloudscheduler', 'server', 'config', '-cc', 'web_frontend', '-ckv', 'log_file=/var/log/cloudscheduler/csv2_web_update.log,enable_glint=True', '-su', ut_id(gvar, 'clu4')]
    )

    # 16
    execute_csv2_command(
        gvar, 0, None, 'server config update successfully updated the following keys: log_level',
        ['cloudscheduler', 'server', 'config', '-cc', 'csjobs.py', '-ckv', 'log_level=10', '-su', ut_id(gvar, 'clu4')]
    )

    # Change settings back to what we presume they were.
    # 17
    execute_csv2_command(
        gvar, 0, None, 'server config update successfully updated the following keys: log_file, enable_glint',
        ['cloudscheduler', 'server', 'config', '-cc', 'web_frontend', '-ckv', 'log_file=/var/log/cloudscheduler/csv2_web.log,enable_glint=False', '-su', ut_id(gvar, 'clu4')]
    )

    # 18
    execute_csv2_command(
        gvar, 0, None, 'server config update successfully updated the following keys: log_level',
        ['cloudscheduler', 'server', 'config', '-cc', 'csjobs.py', '-ckv', 'log_level=20', '-su', ut_id(gvar, 'clu4')]
    )

    # View-based.
    # 19
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'server', 'config', '-ok', '-su', ut_id(gvar, 'clu4')],
        expected_list='Server Configuration', columns=['Category', 'Config Key']
    )

    # 20
    execute_csv2_command(
        gvar, 0, None, 'server config, 1. Server Configuration: keys=category,config_key, columns=config_type,config_value',
        ['cloudscheduler', 'server', 'config', '-VC', '-su', ut_id(gvar, 'clu4')]
    )

    # 21
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'server', 'config', '-NV', '-su', ut_id(gvar, 'clu4')],
        expected_list='Server Configuration', columns=['Category', 'Config Key', 'Type', 'Value']
    )

    # 22
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'server', 'config', '-V', 'config_value', '-su', ut_id(gvar, 'clu4')],
        expected_list='Server Configuration', columns=['Category', 'Config Key', 'Value']
    )

    # 23
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'server', 'config', '-su', ut_id(gvar, 'clu4')],
        expected_list='Server Configuration', columns=['Category', 'Config Key', 'Value']
    )

    # 24
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'server', 'config', '-r', '-su', ut_id(gvar, 'clu4')],
        expected_list='Server Configuration', columns=['Key', 'Value']
    )

    # 25
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'server', 'config', '-V', '', '-su', ut_id(gvar, 'clu4')],
        expected_list='Server Configuration', columns=['Category', 'Config Key', 'Type', 'Value']
    )

if __name__ == "__main__":
    main(None, None)
