from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id
from sys import argv

# lno: UV - error code identifier.

def main(gvar, user_secret):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv2_request(gvar, argv[0])
    
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
        gvar, 1, 'UV', 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'utu2')),
        '/user/list/',
        server_user=ut_id(gvar, 'utu2'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 403, forbidden.',
        '/user/list/',
        server_user=ut_id(gvar, 'utu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'UV', 'cannot switch to invalid group "invalid-unit-test".',
        '/user/list/?invalid-unit-test'
    )

    execute_csv2_request(
        gvar, 1, 'UV', 'cannot switch to invalid group "{}".'.format(ut_id(gvar, 'utg2')),
        '/user/list/?"{}"'.format(ut_id(gvar, 'utg2'))
    )

    execute_csv2_request(
        gvar, 1, 'UV', 'request contained a bad parameter "invalid-unit-test".',
        '/user/list/' #I am assuing a group does not need to be specified for this request
, form_data={'invalid-unit-test': 'invalid-unit-test'}
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/' #I am assuing a group does not need to be specified for this request
    )

if __name__ == "__main__":
    main(None)
