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

    # 01
    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 401, unauthorized.',
        '/group/update/',
        server_user='invalid-unit-test', server_pw=user_secret
    )

    # 02
    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 403, forbidden.',
        '/group/update/',
        server_user=ut_id(gvar, 'gtu1') , server_pw=user_secret
    )

    # 03
    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 403, forbidden.',
        '/group/update/',
        server_user=ut_id(gvar, 'gtu3') , server_pw=user_secret
    )

    # 04
    execute_csv2_request(
        gvar, 1, None, 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'gtu2')),
        '/group/update/',
        server_user=ut_id(gvar, 'gtu2') , server_pw=user_secret
    )

    # 05
    execute_csv2_request(
        gvar, 1, 'GV', 'invalid method "GET" specified.',
        '/group/update/'
    )

    # 06
    execute_csv2_request(
        gvar, 1, 'GV', 'cannot switch to invalid group "invalid-unit-test".',
        '/group/update/', group='invalid-unit-test'
    )

    # 07
    execute_csv2_request(
        gvar, 1, 'GV', 'request contained a bad parameter "invalid-unit-test".',
        '/group/update/', form_data={'invalid-unit-test': 'invalid-unit-test'}
    )

    # 08
    execute_csv2_request(
        gvar, 1, 'GV', 'value specified for "group_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        '/group/update/', form_data={'group_name': ut_id(gvar, 'Gtg1')}
    )

    # 09
    execute_csv2_request(
        gvar, 1, 'GV', 'value specified for "group_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        '/group/update/', form_data={'group_name': ut_id(gvar, 'gtg!1')}
    )

    # 10
    execute_csv2_request(
        gvar, 1, 'GV', 'value specified for "group_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        '/group/update/', form_data={'group_name': ut_id(gvar, 'gtg1-')}
    )

    # 11
    execute_csv2_request(
        gvar, 1, 'GV', 'group update must specify at least one field to update.',
        '/group/update/', form_data={'group_name': 'invalid-unit-test'}
    )

    # 12
    execute_csv2_request(
        gvar, 1, 'GV', 'value specified for "user_option" must be one of the following options: [\'add\', \'delete\'].',
        '/group/update/', form_data={'user_option': 'invalid-unit-test'}
    )

    # 13
    execute_csv2_request(
        gvar, 1, 'GV', 'group update request did not contain mandatory parameter "group_name".',
        '/group/update/', form_data={'username': 'invalid-unit-test'}
    )

    # 14
    execute_csv2_request(
        gvar, 1, 'GV', 'the request did not match any rows.',
        '/group/update/', form_data={
            'group_name': 'invalid-unit-test',
            'htcondor_fqdn': 'invalid-unit-test'
        }
    )

    # 15
    execute_csv2_request(
        gvar, 1, 'GV', 'group update parameter "htcondor_fqdn" contains an empty string which is specifically disallowed.',
        '/group/update/', form_data={
            'group_name': ut_id(gvar, 'gtg4'),
            'htcondor_fqdn': ''
        }
    )

    # 16
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully updated.'.format(ut_id(gvar, 'gtg4')),
        '/group/update/', form_data={
            'group_name': ut_id(gvar, 'gtg4'),
            'htcondor_fqdn': 'unit-test-group-four-update.ca'
        }
    )

    # 17
    execute_csv2_request(
        gvar, 0, None, None,
        '/group/list/',
        list='group_list', filter={'group_name': ut_id(gvar, 'gtg4')},
        values={'group_name': ut_id(gvar, 'gtg4'), 'htcondor_fqdn': 'unit-test-group-four-update.ca'}
    )

    # 18
    execute_csv2_request(
        gvar, 1, 'GV', 'specified user "invalid-unit-test" does not exist.',
        '/group/update/', form_data={
            'group_name': ut_id(gvar, 'gtg4'),
            'username.1': 'invalid-unit-test'
        }
    )

    # 19
    execute_csv2_request(
        gvar, 1, 'GV', 'group update, "{}" failed - user "{}" was specified twice.'.format(ut_id(gvar, 'gtg4'), ut_id(gvar, 'gtu4')),
        '/group/update/', form_data={
            'group_name': ut_id(gvar, 'gtg4'),
            'username.1': ut_id(gvar, 'gtu4'),
            'username.2': ut_id(gvar, 'gtu4')
        }
    )

    # 20
    execute_csv2_request(
        gvar, 0, None, None,
        '/group/list/',
        list='group_list', filter={'group_name': ut_id(gvar, 'gtg4')},
        values={'group_name': ut_id(gvar, 'gtg4'), 'htcondor_fqdn': 'unit-test-group-four-update.ca'}
    )

    # 21
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully updated.'.format(ut_id(gvar, 'gtg4')),
        '/group/update/', form_data={
            'group_name': ut_id(gvar, 'gtg4'),
            'username.1': ut_id(gvar, 'gtu4')
        }
    )

    # 22
    execute_csv2_request(
        gvar, 0, None, None,
        '/group/list/',
        list='group_list', filter={'group_name': ut_id(gvar, 'gtg4')},
        values={'group_name': ut_id(gvar, 'gtg4'), 'htcondor_fqdn': 'unit-test-group-four-update.ca'}
    )

    # 23
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'gtu4')},
        values={'user_groups': ut_id(gvar, 'gtg4')}
    )

    # 24
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully updated.'.format(ut_id(gvar, 'gtg4')),
        '/group/update/', form_data={
            'group_name': ut_id(gvar, 'gtg4'),
            'username': ''
        }, html=True
    )

    # 25
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'gtu4')},
        values={'user_groups': None}
    )

    # 26
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully updated.'.format(ut_id(gvar, 'gtg4')),
        '/group/update/', form_data={
            'group_name': ut_id(gvar, 'gtg4'),
            'username.1': ut_id(gvar, 'gtu4')
        }, html=True
    )

    # 27
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'gtu4')},
        values={'user_groups': ut_id(gvar, 'gtg4')}
    )

    # 28
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully updated.'.format(ut_id(gvar, 'gtg4')),
        '/group/update/', form_data={
            'group_name': ut_id(gvar, 'gtg4'),
            'username.1': ut_id(gvar, 'gtu5')
        }, html=True
    )

    # 29
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'gtu4')},
        values={'user_groups': None}
    )

    # 30
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'gtu5')},
        values={'user_groups': ut_id(gvar, 'gtg4,gtg5')}
    )

    # 31
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully updated.'.format(ut_id(gvar, 'gtg4')),
        '/group/update/', form_data={
            'group_name': ut_id(gvar, 'gtg4'),
            'username.1': ut_id(gvar, 'gtu4'),
            'username.2': ut_id(gvar, 'gtu5')
        }, html=True
    )

    # 32
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'gtu4')},
        values={'user_groups': ut_id(gvar, 'gtg4')}
    )

    # 33
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'gtu5')},
        values={'user_groups': ut_id(gvar, 'gtg4,gtg5')}
    )

if __name__ == "__main__":
    main(None)
