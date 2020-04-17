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
    sanity_requests(gvar, '/group/metadata-query/', ut_id(gvar, 'gtg4'), ut_id(gvar, 'gtu3'), ut_id(gvar, 'gtg7'), ut_id(gvar, 'gtu2'))

    # 06 Omit metdata_name.
    execute_csv2_request(
        gvar, 1, None, 'group metadata_query, request did not contain mandatory parameter "metadata_name".',
        '/group/metadata-query/', group=ut_id(gvar, 'gtg4'),
        server_user=ut_id(gvar, 'gtu3')
    )

    # 10 Give empty metadata_name.
    execute_csv2_request(
        gvar, 1, None, 'group metadata_query, value specified for "metadata_name" must not be the empty string.',
        '/group/metadata-query/', group=ut_id(gvar, 'gtg4'), query_data={'metadata_name': ''},
        server_user=ut_id(gvar, 'gtu3')
    )

    # 11 Give a metadata_name that does not exist.
    execute_csv2_request(
        gvar, 0, None, None,
        '/group/metadata-query/', group=ut_id(gvar, 'gtg4'), query_data={'metadata_name': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'gtu3')
    )

    # 12
    execute_csv2_request(
        gvar, 0, None, None,
        '/group/metadata-query/', group=ut_id(gvar, 'gtg5'), query_data={'metadata_name': ut_id(gvar, 'gty4')},
        server_user=ut_id(gvar, 'gtu3')
    )

if __name__ == "__main__":
    main(None)
