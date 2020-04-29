from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, sanity_requests
from sys import argv

# lno: SV - error code identifier.

def main(gvar):

    # This file should always be run with setup to avoid changing server config values without changing them back.
    # 01 - 05
    sanity_requests(gvar, '/server/config/', ut_id(gvar, 'stg1'), ut_id(gvar, 'stu1'), ut_id(gvar, 'stg2'), ut_id(gvar, 'stu2'))

    # 06 Attempt as an unprivileged user.
    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 403, forbidden.',
        '/server/config/', group=ut_id(gvar, 'stg1'),
        server_user=ut_id(gvar, 'stu3')
    )

    # We cannot use parameters_requests() here, because it asserts that a GET request will fail.

    # 07
    execute_csv2_request(
        gvar, 1, 'SV', 'server config update failed - no category specified.',
        '/server/config/', group=ut_id(gvar, 'stg1'), form_data={'enable_glint': 'False'},
        server_user=ut_id(gvar, 'stu1')
    )

    # 08
    execute_csv2_request(
        gvar, 1, 'SV', 'server config update failed - invalid category "invalid-unit-test" specified.',
        '/server/config/', group=ut_id(gvar, 'stg1'), form_data={'category': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'stu1')
    )

    # 09
    execute_csv2_request(
        gvar, 1, 'SV', 'invalid key "invalid_unit_test" specified.',
        '/server/config/', group=ut_id(gvar, 'stg1'), form_data={'category': 'web_frontend', 'invalid_unit_test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'stu1')
    )
    
    # 10
    execute_csv2_request(
        gvar, 1, 'SV', 'invalid key "config-key" specified.',
        '/server/config/', group=ut_id(gvar, 'stg1'), form_data={'category': 'web_frontend', 'config-key': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'stu1')
    )

    # 11
    execute_csv2_request(
        gvar, 1, 'SV', 'invalid key "config-value" specified.',
        '/server/config/', group=ut_id(gvar, 'stg1'), form_data={'category': 'web_frontend', 'config-value': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'stu1')
    )

    # 12
    execute_csv2_request(
        gvar, 1, 'SV', 'config_key="enable_glint" must be a boolean value.',
        '/server/config/', group=ut_id(gvar, 'stg1'), form_data={
            'category': 'web_frontend',
            'enable_glint': 'invalid-unit-test',
        },
        server_user=ut_id(gvar, 'stu1')
    )

    # 13
    execute_csv2_request(
        gvar, 1, 'SV', 'config_key="log_level" must be an integer.',
        '/server/config/', group=ut_id(gvar, 'stg1'), form_data={
            'category': 'condor_poller.py',
            'log_level': 'invalid-unit-test',
        },
        server_user=ut_id(gvar, 'stu1')
    )

    # 14 Update bool and str fields.
    execute_csv2_request(
        gvar, 0, None, 'server config update successfully updated the following keys',
        '/server/config/', group=ut_id(gvar, 'stg1'), form_data={
            'category': 'web_frontend',
            'enable_glint': 'True',
            'log_file': '/var/log/cloudscheduler/csv2_web_update.log',
        },
        server_user=ut_id(gvar, 'stu1')
    )

    # 15 Ensure values were updated.
    execute_csv2_request(
        gvar, 0, None, None,
        '/server/config/', group=ut_id(gvar, 'stg1'),
        expected_list='config_list', list_filter={'category': 'web_frontend', 'config_key': 'enable_glint'},
        values={'config_type': 'bool', 'config_value': 'True'},
        server_user=ut_id(gvar, 'stu1')
    )

    # 16 Ensure values were updated.
    execute_csv2_request(
        gvar, 0, None, None,
        '/server/config/', group=ut_id(gvar, 'stg1'),
        expected_list='config_list', list_filter={'category': 'web_frontend', 'config_key': 'log_file'},
        values={'config_type': 'str', 'config_value': '/var/log/cloudscheduler/csv2_web_update.log'},
        server_user=ut_id(gvar, 'stu1')
    )

    # 17 Update an int field.
    execute_csv2_request(
        gvar, 0, None, 'server config update successfully updated the following keys',
        '/server/config/', group=ut_id(gvar, 'stg1'), form_data={
            'category': 'condor_poller.py',
            'log_level': 10,
        },
        server_user=ut_id(gvar, 'stu1')
    )

    # 18 Ensure log_level was updated properly.
    execute_csv2_request(
        gvar, 0, None, None,
        '/server/config/', group=ut_id(gvar, 'stg1'),
        expected_list='config_list', list_filter={'category': 'condor_poller.py', 'config_key': 'log_level'},
        values={'config_type': 'int', 'config_value': '10'},
        server_user=ut_id(gvar, 'stu1')
    )

    # 19 Reset server back to original values. (Setup verifies that these are the values when it runs.)
    execute_csv2_request(
        gvar, 0, None, 'server config update successfully updated the following keys',
        '/server/config/', group=ut_id(gvar, 'stg1'), form_data={
            'category': 'web_frontend',
            'enable_glint': 'True',
            'log_file': '/var/log/cloudscheduler/csv2_web.log',
        },
        server_user=ut_id(gvar, 'stu1')
    )

    # 20
    execute_csv2_request(
        gvar, 0, None, 'server config update successfully updated the following keys',
        '/server/config/', group=ut_id(gvar, 'stg1'), form_data={
            'category': 'condor_poller.py',
            'log_level': 20,
        },
        server_user=ut_id(gvar, 'stu1')
    )

if __name__ == "__main__":
    main(initialize_csv2_request(selections=argv[1] if len(argv) > 1 else ''))
