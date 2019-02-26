from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id
from sys import argv

# lno: JV - error code identifier.

def main(gvar, user_secret):
    if not gvar:
        gvar = {'mnomonic': 'JV'}
        if len(argv) > 1:
            initialize_csv2_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv2_request(gvar, argv[0])

    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 401, unauthorized.',
        '/job/list/',
        server_user='invalid-unit-test', server_pw='invalid-unit-test'
    )

    execute_csv2_request(
        gvar, 1, None, 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'jtu1')),
        '/job/list/',
        server_user=ut_id(gvar, 'jtu1'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, None, 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'jtu2')),
        '/job/list/',
        server_user=ut_id(gvar, 'jtu2'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'JV00', 'request contained a bad parameter "invalid-unit-test".',
        '/job/list/', form_data={'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'jtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        '/job/list/', form_data={'group': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'jtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, None, 'cannot switch to invalid group "{}".'.format(ut_id(gvar, 'jtg2')),
        '/job/list/', form_data={'group': ut_id(gvar, 'jtg2')},
        server_user=ut_id(gvar, 'jtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/job/list/', form_data={'group': ut_id(gvar, 'jtg1')},
        server_user=ut_id(gvar, 'jtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/job/list/',
        server_user=ut_id(gvar, 'jtu3'), server_pw=user_secret
    )

if __name__ == "__main__":
    main(None)