from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id
from sys import argv

# lno: VV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)

    # 1
    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 401, unauthorized.',
        '/vm/list/', group=ut_id(gvar, 'vtg1'),
        server_user='invalid-unit-test', server_pw='invalid-unit-test'
    )

    # 2
    execute_csv2_request(
        gvar, 1, None, 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'vtu1')),
        '/vm/list/', group=ut_id(gvar, 'vtg1'),
        server_user=ut_id(gvar, 'vtu1')
    )

    # 3
    execute_csv2_request(
        gvar, 1, None, 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'vtu2')),
        '/vm/list/', group=ut_id(gvar, 'vtg1'),
        server_user=ut_id(gvar, 'vtu2')
    )

    # 4
    execute_csv2_request(
        gvar, 1, 'VV', 'request contained a bad parameter "invalid-unit-test".',
        '/vm/list/', group=(ut_id(gvar, 'vtg1')), form_data={'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'vtu3')
    )

    # 5
    execute_csv2_request(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        '/vm/list/', group='invalid-unit-test',
        server_user=ut_id(gvar, 'vtu3')
    )

    # 6
    execute_csv2_request(
        gvar, 1, None, 'cannot switch to invalid group "{}".'.format(ut_id(gvar, 'vtg2')),
        '/vm/list/', group=ut_id(gvar, 'vtg2'),
        server_user=ut_id(gvar, 'vtu3')
    )

    # 7
    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', group=ut_id(gvar, 'vtg1'),
        server_user=ut_id(gvar, 'vtu3')
    )

if __name__ == "__main__":
    main(None)
