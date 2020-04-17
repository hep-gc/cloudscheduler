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
    sanity_requests(gvar, '/cloud/metadata-query/', ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctu1'), ut_id(gvar, 'ctg2'), ut_id(gvar, 'ctu2'))

    # 06 Omit all parameters.
    execute_csv2_request(
        gvar, 1, None, 'cloud metadata_query, request did not contain mandatory parameter "cloud_name".',
        '/cloud/metadata-query/', group=ut_id(gvar, 'ctg1'),
        server_user=ut_id(gvar, 'ctu1')
    )

    # 07 Omit cloud_name.
    execute_csv2_request(
        gvar, 1, None, 'cloud metadata_query, request did not contain mandatory parameter "cloud_name".',
        '/cloud/metadata-query/', group=ut_id(gvar, 'ctg1'), query_data={'metadata_name': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu1')
    )

    # 08 Give empty cloud_name.
    execute_csv2_request(
        gvar, 1, None, 'cloud metadata_query, value specified for "cloud_name" must not be the empty string.',
        '/cloud/metadata-query/', group=ut_id(gvar, 'ctg1'), query_data={'cloud_name': '', 'metadata_name': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu1')
    )

    # 09 Omit metadata_name.
    execute_csv2_request(
        gvar, 1, None, 'cloud metadata_query, request did not contain mandatory parameter "metadata_name".',
        '/cloud/metadata-query/', group=ut_id(gvar, 'ctg1'), query_data={'cloud_name': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu1')
    )

    # 10 Give empty metadata_name.
    execute_csv2_request(
        gvar, 1, None, 'cloud metadata_query, value specified for "metadata_name" must not be the empty string.',
        '/cloud/metadata-query/', group=ut_id(gvar, 'ctg1'), query_data={'cloud_name': 'invalid-unit-test', 'metadata_name': ''},
        server_user=ut_id(gvar, 'ctu1')
    )

    # 11 Give a cloud_name / metadata_name combination that does not exist.
    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/metadata-query/', group=ut_id(gvar, 'ctg1'), query_data={'cloud_name': 'invalid-unit-test', 'metadata_name': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu1')
    )

    # 12
    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/metadata-query/', group=ut_id(gvar, 'ctg1'), query_data={'cloud_name': ut_id(gvar, 'ctc2'), 'metadata_name': ut_id(gvar, 'cty1')},
        server_user=ut_id(gvar, 'ctu1')
    )

if __name__ == "__main__":
    main(None)
