from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, generate_secret
from sys import argv
import nogroup_requests_cleanup

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)
    if not gvar['user_secret']:
        gvar['user_secret'] = generate_secret()

    nogroup_requests_cleanup.main(gvar)

    # 07 group for priviledged user
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'ngg1')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'ngg1')
        }
    )

    # 08 group for unpriviledged user
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'ngg2')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'ngg2')
        }
    )

    # 09 privileged user in no groups
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'ngu1')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'ngu1'),
            'password1': gvar['user_secret'],
            'password2': gvar['user_secret'],
            'cert_cn': '{} test user 1'.format(ut_id(gvar, 'server')),
            'is_superuser': 1
        }
    )

    # 10 unprivileged user in no groups
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'ngu2')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'ngu2'),
            'password1': gvar['user_secret'],
            'password2': gvar['user_secret'],
            'cert_cn': '{} test user 2'.format(ut_id(gvar, 'server')),
        }
    )

    # 11 privileged user in a group that we will attempt to remove
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'ngu3')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'ngu3'),
            'password1': gvar['user_secret'],
            'password2': gvar['user_secret'],
            'cert_cn': '{} test user 3'.format(ut_id(gvar, 'server')),
            'group_name': ut_id(gvar, 'ngg1'),
            'is_superuser': 1
        }
    )

    # 12 unprivileged user in a group that we will attempt to remove
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'ngu4')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'ngu4'),
            'password1': gvar['user_secret'],
            'password2': gvar['user_secret'],
            'group_name': ut_id(gvar, 'ngg2'),
            'cert_cn': '{} test user 4'.format(ut_id(gvar, 'server')),
        }
    )

if __name__ == "__main__":
    main(None)
