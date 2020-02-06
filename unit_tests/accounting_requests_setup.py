from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, generate_secret
from sys import argv
import accounting_requests_cleanup

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv2_request(gvar, argv[0])
    if not gvar['user_secret']:
        gvar['user_secret'] = generate_secret()

    accounting_requests_cleanup.main(gvar)

    # unprivileged user in no groups
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'atu1')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'atu1'),
            'password1': gvar['user_secret'],
            'password2': gvar['user_secret'],
            'cert_cn': '{} test user 1'.format(ut_id(gvar, 'accounting'))
        }
    )

    # unprivileged user in atg1
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'atu2')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'atu2'),
            'password1': gvar['user_secret'],
            'password2': gvar['user_secret'],
            'cert_cn': '{} test user 2'.format(ut_id(gvar, 'accounting'))
        }
    )

    # group containing atu2
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'atg1')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'atg1'),
            'htcondor_fqdn': 'accounting-test-group-1.ca',
            'username.1': ut_id(gvar, 'atu2')
        }
    )

if __name__ == '__main__':
    main(None)
