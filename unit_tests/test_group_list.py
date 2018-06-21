from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id
import sys

def main(gvar):
    if not gvar:
        gvar = {}
        if len(sys.argv) > 1:
            initialize_csv2_request(gvar, sys.argv[0], selections=sys.argv[1])
        else:
            initialize_csv2_request(gvar, sys.argv[0])
    
    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 401, unauthorized.',
        '/group/list/',
        server_user='invalid-unit-test', server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 403, forbidden.',
        '/group/list/',
        server_user=ut_id(gvar, 'gtu1'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, None, 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'gtu2')),
        '/group/list/',
        server_user=ut_id(gvar, 'gtu2'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        '/group/list/', form_data={'group': 'invalid-unit-test'}
    )

    execute_csv2_request(
        gvar, 1, 'GV##', 'request contained a bad parameter "invalid-unit-test".',
        '/group/list/', form_data={'invalid-unit-test': 'invalid-unit-test'}
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/group/list/'
    )

if __name__ == "__main__":
    main(None)