from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, sanity_requests
from sys import argv

# lno: JV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)

    # 01 - 05
    sanity_requests(gvar, '/job/list/', ut_id(gvar, 'jtg1'), ut_id(gvar, 'jtu1'), ut_id(gvar, 'jtg2'), ut_id(gvar, 'jtu2'))

    # 06
    execute_csv2_request(
        gvar, 1, None, 'job list, request contained a bad parameter "invalid_unit_test".',
        '/job/list/', group=ut_id(gvar, 'jtg1'), form_data={'invalid_unit_test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'jtu1')
    )

    # 07
    execute_csv2_request(
        gvar, 0, None, None,
        '/job/list/', group=ut_id(gvar, 'jtg1'),
        server_user=ut_id(gvar, 'jtu1')
    )

if __name__ == "__main__":
    main(None)
