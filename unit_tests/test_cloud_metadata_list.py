from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, sanity_requests
from sys import argv

# lno: CV - error code identifier.

def main(gvar):

    # 01 - 05
    sanity_requests(gvar, '/cloud/metadata-list/', ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctu1'), ut_id(gvar, 'ctg2'), ut_id(gvar, 'ctu2'))

    # 6
    execute_csv2_request(
        gvar, 1, 'CV', 'request contained a bad parameter "invalid-unit-test".',
        '/cloud/metadata-list/', group=(ut_id(gvar, 'ctg1')),
        form_data={'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu1')
    )

    # 7
    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/metadata-list/', group=ut_id(gvar, 'ctg1'),
        expected_list='cloud_metadata_list', 
        list_filter={'metadata_name': ut_id(gvar, 'cty1'), 'cloud_name': ut_id(gvar, 'ctc2'), 'group_name': ut_id(gvar, 'ctg1')},
        values={'metadata': '- example: yes', 'enabled': 1, 'mime_type': 'cloud-config', 'priority': 0},
        server_user=ut_id(gvar, 'ctu1')
    )

if __name__ == "__main__":
    main(initialize_csv2_request(selections=argv[1] if len(argv) > 1 else ''))
