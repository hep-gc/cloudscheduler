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
        '/user/update/',
        server_user='invalid-unit-test', server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 403, forbidden.',
        '/user/update/',
        server_user=ut_id(gvar, 'utu1'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'UV12', 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'utu2')),
        '/user/update/',
        server_user=ut_id(gvar, 'utu2'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'UV25', 'invalid method "GET" specified.',
        '/user/update/'
    )

    execute_csv2_request(
        gvar, 1, 'UV18', 'cannot switch to invalid group "invalid-unit-test".',
        '/user/update/', form_data={'group': 'invalid-unit-test'}
    )

    execute_csv2_request(
        gvar, 1, 'UV18', 'cannot switch to invalid group "{}".'.format(ut_id(gvar, 'utg2')),
        '/user/update/', form_data={'group': ut_id(gvar, 'utg2')}
    )

    execute_csv2_request(
        gvar, 1, 'UV19', 'request contained a bad parameter "invalid-unit-test".',
        '/user/update/', form_data={'invalid-unit-test': 'invalid-unit-test'}
    )

    execute_csv2_request(
        gvar, 1, 'UV19', 'value specified for "username" must be all lower case.',
        '/user/update/', form_data={'username': 'Invalid-unit-test'}
    )

    execute_csv2_request(
        gvar, 1, 'UV23', 'must specify at least one field to update.',
        '/user/update/', form_data={'username': 'invalid-unit-test'}
    )

    execute_csv2_request(
        gvar, 1, 'UV22', 'the request did not match any rows.',
        '/user/update/', form_data={
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test'
        }
    )

    execute_csv2_request(
        gvar, 1, 'UV23', 'must specify at least one field to update.',
        '/user/update/', form_data={'username': ut_id(gvar, 'utu6')}
    )

    execute_csv2_request(
        gvar, 1, 'UV19', 'boolean value specified for "is_superuser" must be one of the following: true, false, yes, no, 1, or 0.',
        '/user/update/', form_data={'is_superuser': 'invalid-unit-test'}
    )

    execute_csv2_request(
        gvar, 1, 'UV19', 'value specified for a password is less than 6 characters.',
        '/user/update/', form_data={'password': 'test'}
    )

    execute_csv2_request(
        gvar, 1, 'UV19', 'value specified for a password is less then 16 characters, and does not contain a mixture of upper, lower, and numerics.',
        '/user/update/', form_data={'password': 'invalid'}
    )

    execute_csv2_request(
        gvar, 1, 'UV19', 'password update received a password but no verify password; both are required.',
        '/user/update/', form_data={'password1': 'test'}
    )

    execute_csv2_request(
        gvar, 1, 'UV19', 'password update received a verify password but no password; both are required.',
        '/user/update/', form_data={'password2': 'test'}
    )

    execute_csv2_request(
        gvar, 1, 'UV19', 'value specified for a password is less than 6 characters.',
        '/user/update/', form_data={
            'password1': 'test',
            'password2': 'test'
        }
    )

    execute_csv2_request(
        gvar, 1, 'UV19', 'value specified for a password is less then 16 characters, and does not contain a mixture of upper, lower, and numerics.',
        '/user/update/', form_data={
            'password1': 'invalid',
            'password2': 'invalid'
        }
    )

    execute_csv2_request(
        gvar, 1, 'UV19', 'values specified for passwords do not match.',
        '/user/update/', form_data={
            'password1': 'Abc123',
            'password2': '321cbA'
        }
    )

    execute_csv2_request(
        gvar, 1, 'UV19', 'request contained a rejected/bad parameter "join_date".',
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu6'),
            'join_date': 'invalid-unit-test'
        }
    )

    execute_csv2_request(
        gvar, 1, 'UV19', 'request contained a rejected/bad parameter "active_group".',
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu6'),
            'active_group': 'invalid-unit-test'
        }
    )

    execute_csv2_request(
        gvar, 1, 'UV21', 'specified group "invalid-unit-test" does not exist.',
        '/user/update/', form_data={
            'username': 'invalid-unit-test',
            'group_name': 'invalid-unit-test'
        }
    )

    execute_csv2_request(
        gvar, 1, 'UV19', 'request contained a bad parameter "condor_central_manager".',
        '/user/update/', form_data={
            'username': 'invalid-unit-test',
            'condor_central_manager': 'invalid-unit-test'
        }
    )

    execute_csv2_request(
        gvar, 1, 'UV21', 'user update, "{}" failed - group "{}" was specified twice.'.format(ut_id(gvar, 'utu6'), ut_id(gvar, 'utg1')),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_name.2': ut_id(gvar, 'utg1')
        }
    )

    execute_csv2_request(
        gvar, 1, 'UV20', 'common name "{0}" conflicts with registered user "{0}".'.format(ut_id(gvar, 'utu3')),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu6'),
            'cert_cn': ut_id(gvar, 'utu3')
        }
    )

    execute_csv2_request(
        gvar, 1, 'UV20', 'common name "{}" conflicts with registered user "{}".'.format(ut_id(gvar, 'user test user three'), ut_id(gvar, 'utu3')),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu6'),
            'cert_cn': ut_id(gvar, 'user test user three')
        }
    )

    execute_csv2_request(
        gvar, 1, 'UV19', 'value specified for "group_option" must be one of the following options: [\'add\', \'delete\'].',
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_option': 'invalid-unit-test'
        }
    )

    execute_csv2_request(
        gvar, 1, 'UV23', 'must specify at least one field to update.',
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_option': 'add'
        }
    )

    execute_csv2_request(
        gvar, 1, 'UV23', 'must specify at least one field to update.',
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_option': 'delete'
        }
    )

    execute_csv2_request(
        gvar, 1, 'UV21', 'specified group "invalid-unit-test" does not exist.',
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_option': 'add',
            'group_name': 'invalid-unit-test'
        }
    )

    execute_csv2_request(
        gvar, 1, 'UV21', 'specified group "invalid-unit-test" does not exist.',
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_option': 'delete',
            'group_name': 'invalid-unit-test'
        }
    )

    execute_csv2_request(
        gvar, 1, 'UV21', 'specified group "invalid-unit-test" does not exist.',
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_name.2': 'invalid-unit-test'
        }
    )

    execute_csv2_request(
        gvar, 1, 'UV21', 'specified group "invalid-unit-test" does not exist.',
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_name.2': 'invalid-unit-test',
            'group_option': 'add'
        }
    )

    execute_csv2_request(
        gvar, 1, 'UV21', 'specified group "invalid-unit-test" does not exist.',
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_name.2': 'invalid-unit-test',
            'group_option': 'delete'
        }
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu6')},
        values={'username': ut_id(gvar, 'utu6'), 'user_groups': None}
    )

    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'utu6')),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_name': ut_id(gvar, 'utg1')
        }
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu6')},
        values={'username': ut_id(gvar, 'utu6'), 'user_groups': ut_id(gvar, 'utg1')}
    )

    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'utu6')),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_name.2': ut_id(gvar, 'utg2')
        }
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu6')},
        values={'username': ut_id(gvar, 'utu6'), 'user_groups': ut_id(gvar, 'utg1,utg2')}
    )

    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'utu6')),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_option': 'delete'
        }
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu6')},
        values={'username': ut_id(gvar, 'utu6'), 'user_groups': ut_id(gvar, 'utg2')}
    )

    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'utu6')),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_option': 'add'
        }
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu6')},
        values={'username': ut_id(gvar, 'utu6'), 'user_groups': ut_id(gvar, 'utg1,utg2')}
    )

    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'utu6')),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_name.2': ut_id(gvar, 'utg2'),
            'group_option': 'delete'
        }
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu6')},
        values={'username': ut_id(gvar, 'utu6'), 'user_groups': None}
    )

    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'utu6')),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_name.2': ut_id(gvar, 'utg2'),
            'group_option': 'add'
        }
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu6')},
        values={'username': ut_id(gvar, 'utu6'), 'user_groups': ut_id(gvar, 'utg1,utg2')}
    )

    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'utu6')),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_name.1': ut_id(gvar, 'utg1')
        }, html=True
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu6')},
        values={'username': ut_id(gvar, 'utu6'), 'user_groups': ut_id(gvar, 'utg1')}
    )

    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'utu6')),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_name.2': ut_id(gvar, 'utg2')
        }, html=True
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu6')},
        values={'username': ut_id(gvar, 'utu6'), 'user_groups': ut_id(gvar, 'utg1,utg2')}
    )

    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'utu6')),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_name': ''
        }, html=True
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu6')},
        values={'username': ut_id(gvar, 'utu6'), 'user_groups': None}
    )

if __name__ == "__main__":
    main(None)