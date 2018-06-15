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
        '/group/update/',
        server_user='invalid-unit-test', server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 403, forbidden.',
        '/group/update/',
        server_user=ut_id(gvar, 'gtu1') , server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 403, forbidden.',
        '/group/update/',
        server_user=ut_id(gvar, 'gtu3') , server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, None, 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'gtu2')),
        '/group/update/',
        server_user=ut_id(gvar, 'gtu2') , server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'GV25', 'invalid method "GET" specified.',
        '/group/update/'
    )

    execute_csv2_request(
        gvar, 1, 'GV22', 'cannot switch to invalid group "invalid-unit-test".',
        '/group/update/', form_data={'group': 'invalid-unit-test'}
    )

    execute_csv2_request(
        gvar, 1, 'GV23', 'request contained a bad parameter "invalid-unit-test".',
        '/group/update/', form_data={'invalid-unit-test': 'invalid-unit-test'}
    )

    execute_csv2_request(
        gvar, 1, 'GV23', 'value specified for "group_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        '/group/update/', form_data={'group_name': ut_id(gvar, 'Gtg1')}
    )

    execute_csv2_request(
        gvar, 1, 'GV23', 'value specified for "group_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        '/group/update/', form_data={'group_name': ut_id(gvar, 'gtg!1')}
    )

    execute_csv2_request(
        gvar, 1, 'GV23', 'value specified for "group_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        '/group/update/', form_data={'group_name': ut_id(gvar, 'gtg1-')}
    )

    execute_csv2_request(
        gvar, 1, 'GV24', 'group update "invalid-unit-test" failed',
        '/group/update/', form_data={'group_name': 'invalid-unit-test'}
    )

    execute_csv2_request(
        gvar, 1, 'GV23', 'value specified for "user_option" must be one of the following options: [\'add\', \'delete\'].',
        '/group/update/', form_data={'user_option': 'invalid-unit-test'}
    )

    execute_csv2_request(
        gvar, 1, 'GV23', 'group update request did not contain mandatory parameter "group_name".',
        '/group/update/', form_data={'username': 'invalid-unit-test'}
    )

    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully updated.'.format(ut_id(gvar, 'gtg4')),
        '/group/update/', form_data={
            'group_name': ut_id(gvar, 'gtg4'),
            'condor_central_manager': 'unit-test-group-four-update.ca'
        }
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/group/list/',
        list='group_list', filter={'group_name': ut_id(gvar, 'gtg4')},
        values={'group_name': ut_id(gvar, 'gtg4'), 'condor_central_manager': 'unit-test-group-four-update.ca'}
    )

    execute_csv2_request(
        gvar, 1, 'GV96', 'specified user "invalid-unit-test" does not exist.',
        '/group/update/', form_data={
            'group_name': ut_id(gvar, 'gtg4'),
            'username.1': 'invalid-unit-test'
        }
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/group/list/',
        list='group_list', filter={'group_name': ut_id(gvar, 'gtg4')},
        values={'group_name': ut_id(gvar, 'gtg4'), 'condor_central_manager': 'unit-test-group-four-update.ca'}
    )

    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully updated.'.format(ut_id(gvar, 'gtg4')),
        '/group/update/', form_data={
            'group_name': ut_id(gvar, 'gtg4'),
            'username.1': ut_id(gvar, 'gtu4')
        }
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/group/list/',
        list='group_list', filter={'group_name': ut_id(gvar, 'gtg4')},
        values={'group_name': ut_id(gvar, 'gtg4'), 'condor_central_manager': 'unit-test-group-four-update.ca'}
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'gtu4')},
        values={'user_groups': ut_id(gvar, 'gtg4')}
    )

if __name__ == "__main__":
    main(None)