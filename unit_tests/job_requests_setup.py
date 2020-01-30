from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, generate_secret
from sys import argv
import job_requests_cleanup

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv2_request(gvar, argv[0])
    if not gvar['user_secret']:
        gvar['user_secret'] = generate_secret()
    
    job_requests_cleanup.main(gvar)

    # unprivileged user in no groups
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'jtu1')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'jtu1'),
            'password1': gvar['user_secret'],
            'password2': gvar['user_secret'],
            'cert_cn': ut_id(gvar, 'job test user one')
        }
    )
    
    # privileged user in no groups
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'jtu2')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'jtu2'),
            'password1': gvar['user_secret'],
            'password2': gvar['user_secret'],
            'cert_cn': ut_id(gvar, 'job test user two'),
            'is_superuser': 1
        }
    )

    # group with users
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'jtg1')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'jtg1'),
            'htcondor_fqdn': 'unit-test-group-one.ca'
        }
    )

    # group without users
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'jtg2')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'jtg2'),
            'htcondor_fqdn': 'unit-test-group-two.ca'
        }
    )

    # unprivileged user in jtg1
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'jtu3')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'jtu3'),
            'password1': gvar['user_secret'],
            'password2': gvar['user_secret'],
            'cert_cn': ut_id(gvar, 'job test user three'),
            'group_name.1': ut_id(gvar, 'jtg1')
        }
    )
    
    # privileged user in jtg1
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'jtu4')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'jtu4'),
            'password1': gvar['user_secret'],
            'password2': gvar['user_secret'],
            'cert_cn': ut_id(gvar, 'job test user four'),
            'is_superuser': 1,
            'group_name.1': ut_id(gvar, 'jtg1')
        }
    )

if __name__ == "__main__":
    main(None)
