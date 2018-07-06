from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id
import sys

# lno: UV - error code identifier.

def main(gvar, user_secret):
    if not gvar:
        gvar = {}
        if len(sys.argv) > 1:
            initialize_csv2_request(gvar, sys.argv[0], selections=sys.argv[1])
        else:
            initialize_csv2_request(gvar, sys.argv[0])
    
    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 401, unauthorized.',
        '/user/list/',
        server_user='invalid-unit-test', server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 403, forbidden.',
        '/user/list/',
        server_user=ut_id(gvar, 'utu1'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'UV12', 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'utu2')),
        '/user/list/',
        server_user=ut_id(gvar, 'utu2'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 403, forbidden.',
        '/user/list/',
        server_user=ut_id(gvar, 'utu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'UV12', 'cannot switch to invalid group "invalid-unit-test".',
        '/user/list/', form_data={'group': 'invalid-unit-test'}
    )

    execute_csv2_request(
        gvar, 1, 'UV12', 'cannot switch to invalid group "{}".'.format(ut_id(gvar, 'utg2')),
        '/user/list/', form_data={'group': ut_id(gvar, 'utg2')}
    )

    execute_csv2_request(
        gvar, 1, 'UV13', 'request contained a bad parameter "invalid-unit-test".',
        '/user/list/', form_data={'invalid-unit-test': 'invalid-unit-test'}
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/'
    )

if __name__ == "__main__":
    main(None)