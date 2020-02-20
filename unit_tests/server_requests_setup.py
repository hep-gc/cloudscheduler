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

    # unprivileged user in no groups
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'stu1')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'stu1'),
            'password1': gvar['user_secret'],
            'password2': gvar['user_secret'],
            'cert_cn': '{} test user one'.format(ut_id(gvar, 'server'))
        }
    )
    
    # privileged user in no groups
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'stu2')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'stu2'),
            'password1': gvar['user_secret'],
            'password2': gvar['user_secret'],
            'cert_cn': '{} test user two'.format(ut_id(gvar, 'server')),
            'is_superuser': 1
        }
    )

    # group without users
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'stg1')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'stg1'),
            'htcondor_fqdn': gvar['user_settings']['server-address']
        }
    )

    # group with users
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'stg2')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'stg2'),
            'htcondor_fqdn': gvar['user_settings']['server-address']
        }
    )

    # unprivileged user in group
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'stu3')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'stu3'),
            'password1': gvar['user_secret'],
            'password2': gvar['user_secret'],
            'cert_cn': '{} test user three'.format(ut_id(gvar, 'server')),
            'group_name': ut_id(gvar, 'stg2'),
        }
    )

    # privileged user in group
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'stu4')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'stu4'),
            'password1': gvar['user_secret'],
            'password2': gvar['user_secret'],
            'is_superuser': 1,
            'cert_cn': '{} test user four'.format(ut_id(gvar, 'server')),
            'group_name': ut_id(gvar, 'stg2'),
        }
    )


if __name__ == "__main__":
    main(None)
