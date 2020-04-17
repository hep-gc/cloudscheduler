from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, sanity_requests
from sys import argv

# lno: GV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)
    
    # 01 - 05
    sanity_requests(gvar, '/group/metadata-list/', ut_id(gvar, 'gtg4'), ut_id(gvar, 'gtu3'), ut_id(gvar, 'gtg7'), ut_id(gvar, 'gtu1'))

    # 06
    execute_csv2_request(
        gvar, 1, 'GV', 'request contained a bad parameter "invalid-unit-test".',
        '/group/metadata-list/', group=ut_id(gvar, 'gtg4'),
        form_data={'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'gtu3')
    )

    # 07
    execute_csv2_request(
        gvar, 0, None, None,
        '/group/metadata-list/', group=ut_id(gvar, 'gtg5'),
        expected_list='group_metadata_list', list_filter={'group_name': ut_id(gvar, 'gtg5')},
        values={'metadata_name': ut_id(gvar, 'gty4')},
        server_user=ut_id(gvar, 'gtu3')
    )

if __name__ == "__main__":
    main(None)
