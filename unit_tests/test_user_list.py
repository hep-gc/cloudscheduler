from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, sanity_requests
from sys import argv

# lno: UV - error code identifier.

def main(gvar):
    
    # 01 - 05
    sanity_requests(gvar, '/user/list/', ut_id(gvar, 'utg1'), ut_id(gvar, 'utu4'), ut_id(gvar, 'utg2'), ut_id(gvar, 'utu2'))

    # 06 Attempt as an unprivileged user.
    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 403, forbidden.',
        '/user/list/', group=ut_id(gvar, 'utg1'),
        server_user=ut_id(gvar, 'utu3')
    )

    # 07 Give a bad parameter.
    execute_csv2_request(
        gvar, 1, 'UV', 'request contained a bad parameter "invalid-unit-test".',
        '/user/list/', group=ut_id(gvar, 'utg1'), form_data={'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'utu4')
    )

    # 08
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/', group=ut_id(gvar, 'utg1'),
        expected_list='user_list', list_filter={'username': ut_id(gvar, 'utu3')},
        values={'user_groups': ut_id(gvar, 'utg1')},
        server_user=ut_id(gvar, 'utu4')
    )

if __name__ == "__main__":
    main(initialize_csv2_request(selections=argv[1] if len(argv) > 1 else ''))
