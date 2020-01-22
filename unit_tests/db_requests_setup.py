from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, generate_secret
from sys import argv
import db_requests_cleanup

def main(gvar, user_secret):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv2_request(gvar, argv[0])
    if not user_secret:
        user_secret = generate_secret()

    db_requests_cleanup.main(gvar)

    # 3
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'dtg1')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'dtg1'),
            'htcondor_fqdn': 'db-test-group-one.ca',
        }
    )

    # 4
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'dtu1')),
        '/user/add/'
, form_data={
            'username': ut_id(gvar, 'dtu1'),
            'password1': user_secret,
            'password2': user_secret,
            'cert_cn': '{} test user one'.format(ut_id(gvar, 'database')),
            'group_name.1': ut_id(gvar, 'dtg1')
        }
    )

    # 5
    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully added.'.format(ut_id(gvar, 'dtg1'), ut_id(gvar, 'dtc1')),
        '/cloud/add/', group=ut_id(gvar, 'dtg1'), form_data={
            'cloud_name': ut_id(gvar, 'dtc1'),
            'authurl': 'db-test-cloud-one.ca',
            'project': 'db-test-cloud-one',
            'username': ut_id(gvar, 'dtu1'),
            'password': user_secret,
            'region': ut_id(gvar, 'dtr1'),
            'cloud_type': 'local'
        },
        server_user=ut_id(gvar, 'dtu1'), server_pw=user_secret
    )

if __name__ == "__main__":
    main(None, None)
