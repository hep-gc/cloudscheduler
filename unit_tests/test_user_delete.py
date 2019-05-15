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
    
    # 01
    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 401, unauthorized.',
        '/user/delete/',
        server_user='invalid-unit-test', server_pw=user_secret
    )

    # 02
    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 403, forbidden.',
        '/user/delete/',
        server_user=ut_id(gvar, 'utu1'), server_pw=user_secret
    )

    # 03
    execute_csv2_request(
        gvar, 1, 'UV', 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'utu2')),
        '/user/delete/',
        server_user=ut_id(gvar, 'utu2'), server_pw=user_secret
    )

    # 04
    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 403, forbidden.',
        '/user/delete/',
        server_user=ut_id(gvar, 'utu3'), server_pw=user_secret
    )

    # 05
    execute_csv2_request(
        gvar, 1, 'UV', 'invalid method "GET" specified.',
        '/user/delete/'
    )

    # 06
    execute_csv2_request(
        gvar, 1, 'UV', 'cannot switch to invalid group "invalid-unit-test".',
        '/user/delete/', group='invalid-unit-test'
    )

    # 07
    execute_csv2_request(
        gvar, 1, 'UV', 'cannot switch to invalid group "{}".'.format(ut_id(gvar, 'utg2')),
        '/user/delete/', group=ut_id(gvar, 'utg2')
    )

    # 08
    execute_csv2_request(
        gvar, 1, 'UV', 'request contained superfluous parameter "invalid-unit-test".',
        '/user/delete/'
, form_data={'invalid-unit-test': 'invalid-unit-test'}
    )

    # 09
    execute_csv2_request(
        gvar, 1, 'UV', 'value specified for "username" must be all lower case.',
        '/user/delete/'
, form_data={'username': 'Invalid-unit-test'}
    )

    # 10
    execute_csv2_request(
        gvar, 1, 'UV', 'request contained superfluous parameter "password".',
        '/user/delete/'
, form_data={'password': 'invalid-unit-test'}
    )

    # 11
    execute_csv2_request(
        gvar, 1, 'UV', 'request did not contain mandatory parameter "username".',
        '/user/delete/', group=ut_id(gvar, 'utg1'),
        server_user=ut_id(gvar, 'utu4'), server_pw=user_secret
    )

    # 12
    execute_csv2_request(
        gvar, 1, 'UV', 'the request did not match any rows.',
        '/user/delete/', form_data={'username': 'invalid-unit-test'}
    )

    # 13
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully deleted.'.format(ut_id(gvar, 'utu5')),
        '/user/delete/', form_data={'username': ut_id(gvar, 'utu5')}
    )

if __name__ == "__main__":
    main(None)
