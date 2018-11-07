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

    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 401, unauthorized.',
        '/server/config/',
        server_user=ut_id(gvar, 'invalid-unit-test'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 403, forbidden.',
        '/server/config/',
        server_user=ut_id(gvar, 'stu1'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'SV03', 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'stu2')),
        '/server/config/',
        server_user=ut_id(gvar, 'stu2'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 403, forbidden.',
        '/server/config/',
        server_user=ut_id(gvar, 'stu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/server/config/',
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/server/config/',
        list='config_list', filter={'category': 'web_frontend', 'config_key': 'log_file'},
        values={'type': 'str', 'value': '/var/log/cloudscheduler/csv2_web.log'},
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'SV03', 'cannot switch to invalid group "invalid-unit-test".',
        '/server/config/', form_data={'group': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'SV03', 'cannot switch to invalid group "{}".'.format(ut_id(gvar, 'stg1')),
        '/server/config/', form_data={'group': ut_id(gvar, 'stg1')},
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/server/config/', form_data={'group': ut_id(gvar, 'stg2')},
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'SV02', 'server config update request contained a bad parameter "invalid-unit-test".',
        '/server/config/', form_data={'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'SV02', 'server config update request contained a rejected/bad parameter "config_key".',
        '/server/config/', form_data={'config_key': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'SV02', 'server config update request contained a rejected/bad parameter "value".',
        '/server/config/', form_data={'value': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'SV02', 'server config update value specified for "category" must be one of the following options:',
        '/server/config/', form_data={'category': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'SV01', 'server config update failed - the request did not match any rows',
        '/server/config/', form_data={
            'category': 'web_frontend',
            'log_level': 10,
        },
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'SV02', 'server config update value specified for "log_level" must be an integer value.',
        '/server/config/', form_data={
            'category': 'csjobs.py',
            'log_level': 'invalid-unit-test',
        },
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'SV02', 'server config update value specified for "enable_glint" must be one of the following options: [\'False\', \'True\'].',
        '/server/config/', form_data={
            'category': 'web_frontend',
            'enable_glint': 'invalid-unit-test',
        },
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'SV02', 'server config update request did not contain mandatory parameter "category".',
        '/server/config/', form_data={
            'enable_glint': 'False',
        },
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'SV00', 'server config must specify at least one field to update.',
        '/server/config/', form_data={
            'category': 'web_frontend',
        },
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, 'server config successfully updated',
        '/server/config/', form_data={
            'category': 'web_frontend',
            'enable_glint': 'True',
            'log_file': '/var/log/cloudscheduler/csv2_web_update.log',
        },
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/server/config/',
        list='config_list', filter={'category': 'web_frontend', 'config_key': 'enable_glint'},
        values={'type': 'bool', 'value': 'True'},
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/server/config/',
        list='config_list', filter={'category': 'web_frontend', 'config_key': 'log_file'},
        values={'type': 'str', 'value': '/var/log/cloudscheduler/csv2_web_update.log'},
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, 'server config successfully updated',
        '/server/config/', form_data={
            'category': 'csjobs.py',
            'log_level': 10,
        },
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/server/config/',
        list='config_list', filter={'category': 'csjobs.py', 'config_key': 'log_level'},
        values={'type': 'int', 'value': '10'},
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    # Reset server back to correct values
    execute_csv2_request(
        gvar, 0, None, 'server config successfully updated',
        '/server/config/', form_data={
            'category': 'web_frontend',
            'enable_glint': 'False',
            'log_file': '/var/log/cloudscheduler/csv2_web.log',
        },
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/server/config/',
        list='config_list', filter={'category': 'web_frontend', 'config_key': 'enable_glint'},
        values={'type': 'bool', 'value': 'False'},
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/server/config/',
        list='config_list', filter={'category': 'web_frontend', 'config_key': 'log_file'},
        values={'type': 'str', 'value': '/var/log/cloudscheduler/csv2_web.log'},
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, 'server config successfully updated',
        '/server/config/', form_data={
            'category': 'csjobs.py',
            'log_level': 20,
        },
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/server/config/',
        list='config_list', filter={'category': 'csjobs.py', 'config_key': 'log_level'},
        values={'type': 'int', 'value': '20'},
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

if __name__ == "__main__":
    main(None)
