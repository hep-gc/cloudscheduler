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

    execute_csv2_request(
        gvar, 0, None, 'group "vm-test-group" successfully added.',
        '/group/add/'
, form_data={
            'group_name': 'vm-test-group',
            'htcondor_fqdn': 'vm-test-group-one.ca',
            'username': ut_id(gvar, '')[:-1]
        }
    )

    execute_csv2_request(
        gvar, 0, None, 'cloud "vm-test-group::vm-test-cloud" successfully added.',
        '/cloud/add/', group='vm-test-group', form_data={
            'cloud_name': 'vm-test-cloud',
            'authurl': 'vm-test-cloud.ca',
            'project': 'vm-test-cloud',
            'username': 'vm-test-cloud',
            'password': 'Abc123',
            'region': 'vm-test-cloud',
            'cloud_type': 'local'
        }
    )

if __name__ == "__main__":
    main(None)
