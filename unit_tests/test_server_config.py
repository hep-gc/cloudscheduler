from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id
import sys

# lno: SV - error code identifier.

def main(gvar, user_secret):
    if not gvar:
        gvar = {}
        if len(sys.argv) > 1:
            initialize_csv2_request(gvar, sys.argv[0], selections=sys.argv[1])
        else:
            initialize_csv2_request(gvar, sys.argv[0])

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
        gvar, 1, 'SV02', 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'stu2')),
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
        gvar, 1, 'SV02', 'cannot switch to invalid group "invalid-unit-test".',
        '/server/config/', form_data={'group': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'SV02', 'cannot switch to invalid group "{}".'.format(ut_id(gvar, 'stg1')),
        '/server/config/', form_data={'group': ut_id(gvar, 'stg1')},
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/server/config/', form_data={'group': ut_id(gvar, 'stg2')},
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'SV01', 'server config update request contained a bad parameter "invalid-unit-test".',
        '/server/config/', form_data={'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'SV01', 'server config update value specified for "category" must be one of the following options:',
        '/server/config/', form_data={'category': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'SV01', 'server config update value specified for "config_key" must be one of the following options:',
        '/server/config/', form_data={'config_key': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'SV01', 'server config update request did not contain mandatory parameter "category".',
        '/server/config/', form_data={'value': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/server/config/', form_data={'category': 'web_frontend', 'value': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/server/config/', form_data={'config_key': 'log_file', 'value': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'stu4'), server_pw=user_secret
    )

if __name__ == "__main__":
    main(None)
