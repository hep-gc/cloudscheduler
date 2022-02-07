from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, generate_secret
from sys import argv
import server_requests_cleanup

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)
    if not gvar['user_secret']:
        gvar['user_secret'] = generate_secret()
    
    server_requests_cleanup.main(gvar)

    # 06 group with users
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'stg1')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'stg1'),
            'htcondor_fqdn': gvar['fqdn']
        }
    )

    # 07 group without users
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'stg2')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'stg2'),
            'htcondor_fqdn': gvar['fqdn']
        }
    )

    # 08 privileged user in group
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'stu1')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'stu1'),
            'password1': gvar['user_secret'],
            'password2': gvar['user_secret'],
            'is_superuser': 1,
            'cert_cn': '{} test user 1'.format(ut_id(gvar, 'server')),
            'group_name': ut_id(gvar, 'stg1'),
        }
    )

    # 09 privileged user in no groups
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'stu2')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'stu2'),
            'password1': gvar['user_secret'],
            'password2': gvar['user_secret'],
            'cert_cn': '{} test user 2'.format(ut_id(gvar, 'server')),
            'is_superuser': 1
        }
    )

    # 10 unprivileged user in group
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'stu3')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'stu3'),
            'password1': gvar['user_secret'],
            'password2': gvar['user_secret'],
            'cert_cn': '{} test user 3'.format(ut_id(gvar, 'server')),
            'group_name': ut_id(gvar, 'stg1'),
        }
    )

    # We check that values are as expected here so that the setup will fail and we won't change anything if there are settings that we won't be able to revert to their original values.
    # If you change the values below, you should also change them at the end of server_config.
    # 11 Confirm log_file.
    execute_csv2_request(
        gvar, 0, None, None,
        '/server/config/', group=ut_id(gvar, 'stg1'),
        expected_list='config_list', list_filter={'category': 'web_frontend', 'config_key': 'log_file'},
        values={'config_type': 'str', 'config_value': '/var/log/cloudscheduler/csv2_web.log'},
        server_user=ut_id(gvar, 'stu1')
    )

    # 12 Confirm enable_glint.
    execute_csv2_request(
        gvar, 0, None, None,
        '/server/config/', group=ut_id(gvar, 'stg1'),
        expected_list='config_list', list_filter={'category': 'web_frontend', 'config_key': 'enable_glint'},
        values={'config_type': 'bool', 'config_value': 'True'},
        server_user=ut_id(gvar, 'stu1')
    )

    # 13 Confirm log_level.
    execute_csv2_request(
        gvar, 0, None, None,
        '/server/config/', group=ut_id(gvar, 'stg1'),
        expected_list='config_list', list_filter={'category': 'condor_poller.py', 'config_key': 'log_level'},
        values={'config_type': 'int', 'config_value': '30'},
        server_user=ut_id(gvar, 'stu1')
    )

if __name__ == "__main__":
    main(None)
