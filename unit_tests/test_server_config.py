from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id
from sys import argv

# lno: SV - error code identifier.

def main(gvar, user_secret):
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
        server_user=ut_id(gvar, 'invalid-unit-test'), server_pw=user_secret
    )

    # 02
    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 403, forbidden.',
        '/server/config/',
        server_user=ut_id(gvar, 'stu1'), server_pw=user_secret
    )

    # 03
    execute_csv2_request(
        gvar, 1, 'SV', 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'stu2')),
        '/server/config/',
        server_user=ut_id(gvar, 'stu2'), server_pw=user_secret
    )

    # 04
    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 403, forbidden.',
        '/server/config/',
        server_user=ut_id(gvar, 'stu3'), server_pw=user_secret
    )

    # 05
    execute_csv2_request(
        gvar, 0, None, None,
        '/server/config/', group=ut_id(gvar,'stg1'),
        expected_list='config_list', list_filter={'category': 'web_frontend', 'config_key': 'log_file'},
        values={'config_type': 'str', 'config_value': '/var/log/cloudscheduler/csv2_web.log'},
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    # 06
    execute_csv2_request(
        gvar, 1, 'SV', 'cannot switch to invalid group "invalid-unit-test".',
        '/server/config/', group='invalid-unit-test',
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    # 07
    execute_csv2_request(
        gvar, 1, 'SV', 'cannot switch to invalid group "{}".'.format(ut_id(gvar, 'stg1')),
        '/server/config/', group=ut_id(gvar,'stg1'),
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    # 08
    execute_csv2_request(
        gvar, 0, None, None,
        '/server/config/', group=ut_id(gvar,'stg2'),
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    # 09
    execute_csv2_request(
        gvar, 1, 'SV', 'server config update request contained a bad parameter "invalid-unit-test".',
        '/server/config/', group=ut_id(gvar, 'stg1')
, form_data={'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    # 10
    execute_csv2_request(
        gvar, 1, 'SV', 'server config update request contained a bad parameter "config-key".',
        '/server/config/', group=ut_id(gvar, 'stg1')
, form_data={'config-key': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    # 11
    execute_csv2_request(
        gvar, 1, 'SV', 'server config update request contained a bad parameter "config-value".',
        '/server/config/', group=ut_id(gvar, 'stg1')
, form_data={'config-value': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    # 12
    execute_csv2_request(
        gvar, 1, 'SV', 'server config update value specified for "category" must be one of the following options:',
        '/server/config/', group=ut_id(gvar, 'stg1')
, form_data={'category': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    # 13
    execute_csv2_request(
        gvar, 1, 'SV', 'server config update failed - the request did not match any rows',
        '/server/config/', group=ut_id(gvar, 'stg1')
, form_data={
            'category': 'web_frontend',
            'log_level': 10,
        },
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    # 14
    execute_csv2_request(
        gvar, 1, 'SV', 'server config update value specified for "log_level" must be an integer value.',
        '/server/config/', group=ut_id(gvar, 'stg1')
, form_data={
            'category': 'csjobs.py',
            'log_level': 'invalid-unit-test',
        },
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    # 15
    execute_csv2_request(
        gvar, 1, 'SV', 'server config update value specified for "enable_glint" must be one of the following options: [\'False\', \'True\'].',
        '/server/config/', group=ut_id(gvar, 'stg1')
, form_data={
            'category': 'web_frontend',
            'enable_glint': 'invalid-unit-test',
        },
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    # 16
    execute_csv2_request(
        gvar, 1, 'SV', 'server config update request did not contain mandatory parameter "category".',
        '/server/config/', group=ut_id(gvar, 'stg1')
, form_data={
            'enable_glint': 'False',
        },
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    # 17
    execute_csv2_request(
        gvar, 1, 'SV', 'server config must specify at least one field to update.',
        '/server/config/', group=ut_id(gvar, 'stg1')
, form_data={
            'category': 'web_frontend',
        },
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    # 18
    execute_csv2_request(
        gvar, 0, None, 'server config successfully updated',
        '/server/config/', group=ut_id(gvar, 'stg1')
, form_data={
            'category': 'web_frontend',
            'enable_glint': 'True',
            'log_file': '/var/log/cloudscheduler/csv2_web_update.log',
        },
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    # 19
    execute_csv2_request(
        gvar, 0, None, None,
        '/server/config/', group=ut_id(gvar, 'stg1'),
        expected_list='config_list', list_filter={'category': 'web_frontend', 'config_key': 'enable_glint'},
        values={'config_type': 'bool', 'config_value': 'True'},
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    # 20
    execute_csv2_request(
        gvar, 0, None, None,
        '/server/config/', group=ut_id(gvar, 'stg1'),
        expected_list='config_list', list_filter={'category': 'web_frontend', 'config_key': 'log_file'},
        values={'config_type': 'str', 'config_value': '/var/log/cloudscheduler/csv2_web_update.log'},
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    # 21
    execute_csv2_request(
        gvar, 0, None, 'server config successfully updated',
        '/server/config/', group=ut_id(gvar, 'stg1')
, form_data={
            'category': 'csjobs.py',
            'log_level': 10,
        },
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    # 22
    execute_csv2_request(
        gvar, 0, None, None,
        '/server/config/', group=ut_id(gvar, 'stg1'),
        expected_list='config_list', list_filter={'category': 'csjobs.py', 'config_key': 'log_level'},
        values={'config_type': 'int', 'config_value': '10'},
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    # 23 Reset server back to correct values
    execute_csv2_request(
        gvar, 0, None, 'server config successfully updated',
        '/server/config/', group=ut_id(gvar, 'stg1')
, form_data={
            'category': 'web_frontend',
            'enable_glint': 'False',
            'log_file': '/var/log/cloudscheduler/csv2_web.log',
        },
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    # 24
    execute_csv2_request(
        gvar, 0, None, None,
        '/server/config/', group=ut_id(gvar, 'stg1'),
        expected_list='config_list', list_filter={'category': 'web_frontend', 'config_key': 'enable_glint'},
        values={'config_type': 'bool', 'config_value': 'False'},
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    # 25
    execute_csv2_request(
        gvar, 0, None, None,
        '/server/config/', group=ut_id(gvar, 'stg1'),
        expected_list='config_list', list_filter={'category': 'web_frontend', 'config_key': 'log_file'},
        values={'config_type': 'str', 'config_value': '/var/log/cloudscheduler/csv2_web.log'},
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    # 26
    execute_csv2_request(
        gvar, 0, None, 'server config successfully updated',
        '/server/config/', group=ut_id(gvar, 'stg1')
, form_data={
            'category': 'csjobs.py',
            'log_level': 20,
        },
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    # 27
    execute_csv2_request(
        gvar, 0, None, None,
        '/server/config/',
        expected_list='config_list', list_filter={'category': 'csjobs.py', 'config_key': 'log_level'},
        values={'config_type': 'int', 'config_value': '20'},
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

if __name__ == "__main__":
    main(None)
