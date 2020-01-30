from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id
from sys import argv

# lno: UV - error code identifier.

def main(gvar):
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
        server_user='invalid-unit-test'
    )

    # 02
    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 403, forbidden.',
        '/user/delete/',
        server_user=ut_id(gvar, 'utu1')
    )

    # 03
    execute_csv2_request(
        gvar, 1, 'UV', 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'utu2')),
        '/user/delete/',
        server_user=ut_id(gvar, 'utu2')
    )

    # 04
    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 403, forbidden.',
        '/user/delete/',
        server_user=ut_id(gvar, 'utu3')
    )

    # 05
    execute_csv2_request(
        gvar, 1, 'UV', 'user delete did not contain mandatory parameter "username".',
        '/user/delete/',
        server_user=ut_id(gvar, 'utu4')
    )

    # 06
    execute_csv2_request(
        gvar, 1, 'UV', 'cannot switch to invalid group "invalid-unit-test".',
        '/user/delete/', group='invalid-unit-test',
        server_user=ut_id(gvar, 'utu4')
    )

    # 07
    execute_csv2_request(
        gvar, 1, 'UV', 'cannot switch to invalid group "{}".'.format(ut_id(gvar, 'utg2')),
        '/user/delete/', group=ut_id(gvar, 'utg2'),
        server_user=ut_id(gvar, 'utu4')
    )

    # 08
    execute_csv2_request(
        gvar, 1, 'UV', 'request contained superfluous parameter "invalid-unit-test".',
        '/user/delete/'
, form_data={'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'utu4')
    )

    # 09
    execute_csv2_request(
        gvar, 1, 'UV', 'value specified for "username" must be all lower case.',
        '/user/delete/'
, form_data={'username': 'Invalid-unit-test'},
        server_user=ut_id(gvar, 'utu4')
    )

    # 10
    execute_csv2_request(
        gvar, 1, 'UV', 'request contained superfluous parameter "password".',
        '/user/delete/'
, form_data={'password': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'utu4')
    )

    # 11
    execute_csv2_request(
        gvar, 1, 'UV', 'user delete did not contain mandatory parameter "username".',
        '/user/delete/', group=ut_id(gvar, 'utg1'),
        server_user=ut_id(gvar, 'utu4')
    )

    # 12
    execute_csv2_request(
        gvar, 1, 'UV', 'the request did not match any rows.',
        '/user/delete/', form_data={'username': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'utu4')
    )

    # 13
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully deleted.'.format(ut_id(gvar, 'utu5')),
        '/user/delete/', form_data={'username': ut_id(gvar, 'utu5')},
        server_user=ut_id(gvar, 'utu4')
    )

if __name__ == "__main__":
    main(None)
