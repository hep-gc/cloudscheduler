from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id
from sys import argv

# lno: GV - error code identifier.

def main(gvar, user_secret):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv2_request(gvar, argv[0])

    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 401, unauthorized.',
        '/group/delete/',
        server_user=ut_id(gvar, 'invalid-unit-test'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, None, 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'gtu2')),
        '/group/delete/',
        server_user=ut_id(gvar, 'gtu2'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 403, forbidden.',
        '/group/delete/',
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'GV', 'invalid method "GET" specified.',
        '/group/delete/'
    )

    execute_csv2_request(
        gvar, 1, 'GV', 'request contained a bad parameter "invalid-unit-test".',
        '/group/delete/', form_data={'invalid-unit-test': 'invalid-unit-test'}
    )

    execute_csv2_request(
        gvar, 1, 'GV', 'cannot switch to invalid group "invalid-unit-test".',
        '/group/delete/', group='invalid-unit-test'
    )

    execute_csv2_request(
        gvar, 1, 'GV', 'group delete request did not contain mandatory parameter "group_name".',
        '/group/delete/', group=ut_id(gvar, 'gtg5'),
        server_user=ut_id(gvar, 'gtu5'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'GV', 'group delete "invalid-unit-test" failed - the request did not match any rows.',
        '/group/delete/'
, form_data={'group_name': 'invalid-unit-test'}
    )

    execute_csv2_request(
        gvar, 1, 'GV', 'group delete value specified for "group_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        '/group/delete/'
, form_data={'group_name': 'Invalid-Unit-Test'}
    )

    execute_csv2_request(
        gvar, 1, 'GV', 'group delete value specified for "user_option" must be one of the following options: [\'add\', \'delete\'].',
        '/group/delete/'
, form_data={'user_option': 'invalid-unit-test'}
    )

    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully deleted.'.format(ut_id(gvar, 'gtg6')),
        '/group/delete/'
, form_data={'group_name': ut_id(gvar, 'gtg6')},
        server_user=ut_id(gvar, 'gtu5'), server_pw=user_secret
    )

if __name__ == "__main__":
    main(None)
