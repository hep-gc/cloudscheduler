from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, sanity_requests
from sys import argv

# lno: VV - error code identifier.

def main(gvar):

    # 01 - 05
    sanity_requests(gvar, '/vm/list/', ut_id(gvar, 'vtg1'), ut_id(gvar, 'vtu1'), ut_id(gvar, 'vtg2'), ut_id(gvar, 'vtu2'))

    # 06
    execute_csv2_request(
        gvar, 1, 'VV', 'request contained a bad parameter "invalid_unit_test".',
        '/vm/list/', group=ut_id(gvar, 'vtg1'), form_data={'invalid_unit_test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'vtu1')
    )

    # 07
    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', group=ut_id(gvar, 'vtg1'),
        server_user=ut_id(gvar, 'vtu1')
    )

if __name__ == "__main__":
    main(initialize_csv2_request(selections=argv[1] if len(argv) > 1 else ''))
