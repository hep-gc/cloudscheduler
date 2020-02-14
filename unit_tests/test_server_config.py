from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id
from sys import argv

# lno: SV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv2_request(gvar, argv[0])

    # 01
    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 401, unauthorized.',
        '/server/config/',
        server_user=ut_id(gvar, 'invalid-unit-test')
    )

    # 02
    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 403, forbidden.',
        '/server/config/',
        server_user=ut_id(gvar, 'stu1')
    )

    # 03
    execute_csv2_request(
        gvar, 1, 'SV', 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'stu2')),
        '/server/config/',
        server_user=ut_id(gvar, 'stu2')
    )

    # 04
    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 403, forbidden.',
        '/server/config/',
        server_user=ut_id(gvar, 'stu3')
    )

    # 05
    execute_csv2_request(
        gvar, 0, None, None,
        '/server/config/', group=ut_id(gvar, 'stg2'),
        expected_list='config_list', list_filter={'category': 'web_frontend', 'config_key': 'log_file'},
        values={'config_type': 'str', 'config_value': '/var/log/cloudscheduler/csv2_web.log'},
        server_user=ut_id(gvar, 'stu4')
    )

    # 06
    execute_csv2_request(
        gvar, 1, 'SV', 'cannot switch to invalid group "invalid-unit-test".',
        '/server/config/', group='invalid-unit-test',
        server_user=ut_id(gvar, 'stu4')
    )

    # 07
    execute_csv2_request(
        gvar, 1, 'SV', 'cannot switch to invalid group "{}".'.format(ut_id(gvar, 'stg1')),
        '/server/config/', group=ut_id(gvar, 'stg1'),
        server_user=ut_id(gvar, 'stu4')
    )

    # 08
    execute_csv2_request(
        gvar, 0, None, None,
        '/server/config/', group=ut_id(gvar, 'stg2'),
        server_user=ut_id(gvar, 'stu4')
    )

    # 09
    execute_csv2_request(
        gvar, 1, 'SV', 'invalid key "invalid-unit-test" specified.',
        '/server/config/', group=ut_id(gvar, 'stg2'), form_data={'category': 'web_frontend', 'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'stu4')
    )
    
    # 10
    execute_csv2_request(
        gvar, 1, 'SV', 'invalid key "config-key" specified.',
        '/server/config/', group=ut_id(gvar, 'stg2'), form_data={'category': 'web_frontend', 'config-key': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'stu4')
    )

    # 11
    execute_csv2_request(
        gvar, 1, 'SV', 'invalid key "config-value" specified.',
        '/server/config/', group=ut_id(gvar, 'stg2'), form_data={'category': 'web_frontend', 'config-value': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'stu4')
    )

    # 12
    execute_csv2_request(
        gvar, 1, 'SV', 'server config update failed - invalid category "invalid-unit-test" specified.',
        '/server/config/', group=ut_id(gvar, 'stg2'), form_data={'category': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'stu4')
    )

    # 13 Set a value that 14 can attempt to set to the same value
    execute_csv2_request(
        gvar, None, None, None,
        '/server/config/', group=ut_id(gvar, 'stg2'), form_data={
            'category': 'web_frontend',
            'enable_glint': 'True'
        },
        server_user=ut_id(gvar, 'stu4')
    )

    # 14
    execute_csv2_request(
        gvar, 0, None, None,
        '/server/config/', group=ut_id(gvar, 'stg2'), form_data={
            'category': 'web_frontend',
            'enable_glint': 'True'
        },
        server_user=ut_id(gvar, 'stu4')
    )

    # 15
    execute_csv2_request(
        gvar, 1, 'SV', 'config_key="log_level" must be an integer.',
        '/server/config/', group=ut_id(gvar, 'stg2'), form_data={
            'category': 'csjobs.py',
            'log_level': 'invalid-unit-test',
        },
        server_user=ut_id(gvar, 'stu4')
    )

    # 16
    execute_csv2_request(
        gvar, 1, 'SV', 'config_key="enable_glint" must be a boolean value.',
        '/server/config/', group=ut_id(gvar, 'stg2'), form_data={
            'category': 'web_frontend',
            'enable_glint': 'invalid-unit-test',
        },
        server_user=ut_id(gvar, 'stu4')
    )

    # 17
    execute_csv2_request(
        gvar, 1, 'SV', 'server config update failed - no category specified.',
        '/server/config/', group=ut_id(gvar, 'stg2'), form_data={
            'enable_glint': 'False',
        },
        server_user=ut_id(gvar, 'stu4')
    )

    # 18
    execute_csv2_request(
        gvar, 0, 'SV', None,
        '/server/config/', group=ut_id(gvar, 'stg2'), form_data={
            'category': 'web_frontend',
        },
        server_user=ut_id(gvar, 'stu4')
    )

    # 19
    execute_csv2_request(
        gvar, 0, None, 'server config update successfully updated the following keys',
        '/server/config/', group=ut_id(gvar, 'stg2'), form_data={
            'category': 'web_frontend',
            'enable_glint': 'True',
            'log_file': '/var/log/cloudscheduler/csv2_web_update.log',
        },
        server_user=ut_id(gvar, 'stu4')
    )

    # 20
    execute_csv2_request(
        gvar, 0, None, None,
        '/server/config/', group=ut_id(gvar, 'stg2'),
        expected_list='config_list', list_filter={'category': 'web_frontend', 'config_key': 'enable_glint'},
        values={'config_type': 'bool', 'config_value': 'True'},
        server_user=ut_id(gvar, 'stu4')
    )

    # 21
    execute_csv2_request(
        gvar, 0, None, None,
        '/server/config/', group=ut_id(gvar, 'stg2'),
        expected_list='config_list', list_filter={'category': 'web_frontend', 'config_key': 'log_file'},
        values={'config_type': 'str', 'config_value': '/var/log/cloudscheduler/csv2_web_update.log'},
        server_user=ut_id(gvar, 'stu4')
    )

    # 22
    execute_csv2_request(
        gvar, 0, None, 'server config update successfully updated the following keys',
        '/server/config/', group=ut_id(gvar, 'stg2'), form_data={
            'category': 'csjobs.py',
            'log_level': 10,
        },
        server_user=ut_id(gvar, 'stu4')
    )

    # 23
    execute_csv2_request(
        gvar, 0, None, None,
        '/server/config/', group=ut_id(gvar, 'stg2'),
        expected_list='config_list', list_filter={'category': 'csjobs.py', 'config_key': 'log_level'},
        values={'config_type': 'int', 'config_value': '10'},
        server_user=ut_id(gvar, 'stu4')
    )

    # 24 Reset server back to correct values
    execute_csv2_request(
        gvar, 0, None, 'server config update successfully updated the following keys',
        '/server/config/', group=ut_id(gvar, 'stg2'), form_data={
            'category': 'web_frontend',
            'enable_glint': 'False',
            'log_file': '/var/log/cloudscheduler/csv2_web.log',
        },
        server_user=ut_id(gvar, 'stu4')
    )

    # 25
    execute_csv2_request(
        gvar, 0, None, None,
        '/server/config/', group=ut_id(gvar, 'stg2'),
        expected_list='config_list', list_filter={'category': 'web_frontend', 'config_key': 'enable_glint'},
        values={'config_type': 'bool', 'config_value': 'False'},
        server_user=ut_id(gvar, 'stu4')
    )

    # 26
    execute_csv2_request(
        gvar, 0, None, None,
        '/server/config/', group=ut_id(gvar, 'stg2'),
        expected_list='config_list', list_filter={'category': 'web_frontend', 'config_key': 'log_file'},
        values={'config_type': 'str', 'config_value': '/var/log/cloudscheduler/csv2_web.log'},
        server_user=ut_id(gvar, 'stu4')
    )

    # 27
    execute_csv2_request(
        gvar, 0, None, 'server config update successfully updated the following keys',
        '/server/config/', group=ut_id(gvar, 'stg2'), form_data={
            'category': 'csjobs.py',
            'log_level': 20,
        },
        server_user=ut_id(gvar, 'stu4')
    )

    # 28
    execute_csv2_request(
        gvar, 0, None, None,
        '/server/config/',
        expected_list='config_list', list_filter={'category': 'csjobs.py', 'config_key': 'log_level'},
        values={'config_type': 'int', 'config_value': '20'},
        server_user=ut_id(gvar, 'stu4')
    )

if __name__ == "__main__":
    main(None, None)
