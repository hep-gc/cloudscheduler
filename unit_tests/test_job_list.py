from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id
from sys import argv

# lno: JV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)

    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 401, unauthorized.',
        '/job/list/', group=ut_id(gvar,'jtg1'),
        server_user='invalid-unit-test', server_pw='invalid-unit-test'
    )

    execute_csv2_request(
        gvar, 1, None, 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'jtu1')),
        '/job/list/', group=ut_id(gvar,'jtg1'),
        server_user=ut_id(gvar, 'jtu1')
    )

    execute_csv2_request(
        gvar, 1, None, 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'jtu2')),
        '/job/list/', group=ut_id(gvar,'jtg1'),
        server_user=ut_id(gvar, 'jtu2')
    )

    execute_csv2_request(
        gvar, 1, 'JV', 'request contained a bad parameter "invalid-unit-test".',
        '/job/list/', group=ut_id(gvar,'jtg1'),
        form_data={'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'jtu3')
    )

    execute_csv2_request(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        '/job/list/', group='invalid-unit-test',
        server_user=ut_id(gvar, 'jtu3')
    )

    execute_csv2_request(
        gvar, 1, None, 'cannot switch to invalid group "{}".'.format(ut_id(gvar, 'jtg2')),
        '/job/list/', group=ut_id(gvar,'jtg2'),
        server_user=ut_id(gvar, 'jtu3')
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/job/list/', group=ut_id(gvar,'jtg1'),
        server_user=ut_id(gvar, 'jtu3')
    )

if __name__ == "__main__":
    main(None)
