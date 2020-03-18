from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, sanity_requests
from sys import argv

# lno: CV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)

    # 01 - 05
    sanity_requests(gvar, '/cloud/list', ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctu1'), ut_id(gvar, 'ctg2'), ut_id(gvar, 'ctu2'))

    # 06
    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/list/', group=ut_id(gvar, 'ctg1'),
        expected_list='cloud_list', list_filter={'group_name': ut_id(gvar, 'ctg1'), 'cloud_name': ut_id(gvar, 'ctc2')},
        values={
            'authurl': gvar['cloud_credentials']['authurl'],
            'username': gvar['cloud_credentials']['username'],
            'project': gvar['cloud_credentials']['project'],
            'region': gvar['cloud_credentials']['region'],
            'cloud_type': 'openstack',
            'cloud_priority': 0,
            'cacertificate': None,
            'user_domain_name': 'Default',
            'project_domain_name': 'Default',
        },
        server_user=ut_id(gvar, 'ctu1')
    )

    # 07
    execute_csv2_request(
        gvar, 1, 'CV', 'request contained a bad parameter "invalid-unit-test".',
        '/cloud/list/', group=(ut_id(gvar, 'ctg1')),
        form_data={'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu1')
    )

    # 08
    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/list/', group=ut_id(gvar, 'ctg1'),
        expected_list='cloud_list',
        server_user=ut_id(gvar, 'ctu1')
    )

if __name__ == "__main__":
    main(None)
