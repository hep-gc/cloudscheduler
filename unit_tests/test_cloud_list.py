from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, sanity_requests
from sys import argv

# lno: CV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv2_request(gvar, argv[0])

    # 01 - 05
    sanity_requests(gvar, '/cloud/list', ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctu3'), ut_id(gvar, 'ctg2'), ut_id(gvar, 'ctu1'))

    # 06
    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/list/', group=ut_id(gvar, 'ctg1'),
        expected_list='cloud_list', list_filter={'group_name': ut_id(gvar, 'ctg1'), 'cloud_name': ut_id(gvar, 'ctc2')},
        values={
            'authurl': 'unit-test-cloud-two.ca',
            'project': 'unit-test-cloud-two',
            'username': ut_id(gvar, 'ctu3'),
            'region': ut_id(gvar, 'ctc2-r'),
            'cloud_type': 'local',
            'cloud_priority': 0,
            'cacertificate': None,
            'user_domain_name': 'Default',
            'project_domain_name': '\'Default\'',
        },
        server_user=ut_id(gvar, 'ctu3')
    )

    # 07
    execute_csv2_request(
        gvar, 1, 'CV', 'request contained a bad parameter "invalid-unit-test".',
        '/cloud/list/', group=(ut_id(gvar, 'ctg1')),
        form_data={'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu3')
    )

    # 08
    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/list/', group=ut_id(gvar, 'ctg1'),
        expected_list='cloud_list',
        server_user=ut_id(gvar, 'ctu3'), html=True
    )

if __name__ == "__main__":
    main(None)
