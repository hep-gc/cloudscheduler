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
    sanity_requests(gvar, '/cloud/metadata-fetch/', ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctu3'), ut_id(gvar, 'ctg2'), ut_id(gvar, 'ctu1'))

    # 06
    execute_csv2_request(
        gvar, 1, None, 'TODO',
        '/cloud/metadata-fetch/', group=ut_id(gvar, 'ctg1'),
        server_user=ut_id(gvar, 'ctu3')
    )

    # 07 Give an invalid parameter.
    execute_csv2_request(
        gvar, 1, None, 'TODO',
        '/cloud/metadata-fetch/', group=ut_id(gvar, 'ctg1'), form_data={'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu3')
    )

    # Omit cloud_name.
    execute_csv2_request(
        gvar, 1, None, 'TODO'.format(ut_id(gvar, 'ctg1')),
        '/cloud/metadata-fetch/', group=ut_id(gvar, 'ctg1'), query_data={'metadata_name': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu3')
    )

    # Give empty cloud_name.
    execute_csv2_request(
        gvar, 1, None, 'TODO'.format(ut_id(gvar, 'ctg1')),
        '/cloud/metadata-fetch/', group=ut_id(gvar, 'ctg1'), query_data={'cloud_name': '', 'metadata_name': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu3')
    )

    # Give a cloud_name with the wrong format.
    execute_csv2_request(
        gvar, 1, None, 'TODO'.format(ut_id(gvar, 'ctg1')),
        '/cloud/metadata-fetch/', group=ut_id(gvar, 'ctg1'), query_data={'cloud_name': 'invalid-unit-test!', 'metadata_name': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu3')
    )

    # Omit metadata_name.
    execute_csv2_request(
        gvar, 1, None, 'TODO'.format(ut_id(gvar, 'ctg1')),
        '/cloud/metadata-fetch/', group=ut_id(gvar, 'ctg1'), query_data={'cloud_name': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu3')
    )

    # Give empty metadata_name.
    execute_csv2_request(
        gvar, 1, None, 'TODO'.format(ut_id(gvar, 'ctg1')),
        '/cloud/metadata-fetch/', group=ut_id(gvar, 'ctg1'), query_data={'cloud_name': 'invalid-unit-test', 'metadata_name': ''},
        server_user=ut_id(gvar, 'ctu3')
    )

    # Give a metadata_name with the wrong format.
    execute_csv2_request(
        gvar, 1, None, 'TODO'.format(ut_id(gvar, 'ctg1')),
        '/cloud/metadata-fetch/', group=ut_id(gvar, 'ctg1'), query_data={'cloud_name': 'invalid-unit-test', 'metadata_name': 'invalid-unit-test!'},
        server_user=ut_id(gvar, 'ctu3')
    )

    # Give a cloud_name / metadata_name combination that does not exist.
    execute_csv2_request(
        gvar, 1, None, 'TODO'.format(ut_id(gvar, 'ctg1')),
        '/cloud/metadata-fetch/', group=ut_id(gvar, 'ctg1'), query_data={'cloud_name': 'invalid-unit-test', 'metadata_name': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu3')
    )

    # Fetch metadata properly.
    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/metadata-fetch/', group=ut_id(gvar, 'ctg1'), query_data={'cloud_name': ut_id(gvar, 'ctc2'), 'metadata_name': ut_id(gvar, 'cty1')},
        server_user=ut_id(gvar, 'ctu3')
    )

if __name__ == "__main__":
    main(None)
