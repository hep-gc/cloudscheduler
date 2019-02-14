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
        '/user/update/',
        server_user='invalid-unit-test', server_pw=user_secret
    )

    # 02
    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 403, forbidden.',
        '/user/update/',
        server_user=ut_id(gvar, 'utu1'), server_pw=user_secret
    )

    # 03
    execute_csv2_request(
        gvar, 1, 'UV18', 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'utu2')),
        '/user/update/',
        server_user=ut_id(gvar, 'utu2'), server_pw=user_secret
    )

    # 04
    execute_csv2_request(
        gvar, 1, 'UV25', 'invalid method "GET" specified.',
        '/user/update/'
    )

    # 05
    execute_csv2_request(
        gvar, 1, 'UV18', 'cannot switch to invalid group "invalid-unit-test".',
        '/user/update/', form_data={'group': 'invalid-unit-test'}
    )

    # 06
    execute_csv2_request(
        gvar, 1, 'UV18', 'cannot switch to invalid group "{}".'.format(ut_id(gvar, 'utg2')),
        '/user/update/', form_data={'group': ut_id(gvar, 'utg2')}
    )

    # 07
    execute_csv2_request(
        gvar, 1, 'UV19', 'request contained a bad parameter "invalid-unit-test".',
        '/user/update/', form_data={'invalid-unit-test': 'invalid-unit-test'}
    )

    # 08
    execute_csv2_request(
        gvar, 1, 'UV19', 'value specified for "username" must be all lower case.',
        '/user/update/', form_data={'username': 'Invalid-unit-test'}
    )

    # 09
    execute_csv2_request(
        gvar, 1, 'UV23', 'must specify at least one field to update.',
        '/user/update/', form_data={'username': 'invalid-unit-test'}
    )

    # 10
    execute_csv2_request(
        gvar, 1, 'UV22', 'the request did not match any rows.',
        '/user/update/', form_data={
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test'
        }
    )

    # 11
    execute_csv2_request(
        gvar, 1, 'UV23', 'must specify at least one field to update.',
        '/user/update/', form_data={'username': ut_id(gvar, 'utu6')}
    )

    # 12
    execute_csv2_request(
        gvar, 1, 'UV19', 'boolean value specified for "is_superuser" must be one of the following: true, false, yes, no, 1, or 0.',
        '/user/update/', form_data={'is_superuser': 'invalid-unit-test'}
    )

    # 13
    execute_csv2_request(
        gvar, 1, 'UV19', 'value specified for a password is less than 6 characters.',
        '/user/update/', form_data={'password': 'test'}
    )

    # 14
    execute_csv2_request(
        gvar, 1, 'UV19', 'value specified for a password is less then 16 characters, and does not contain a mixture of upper, lower, and numerics.',
        '/user/update/', form_data={'password': 'invalid'}
    )

    # 15
    execute_csv2_request(
        gvar, 1, 'UV19', 'password update received a password but no verify password; both are required.',
        '/user/update/', form_data={'password1': 'test'}
    )

    # 16
    execute_csv2_request(
        gvar, 1, 'UV19', 'password update received a verify password but no password; both are required.',
        '/user/update/', form_data={'password2': 'test'}
    )

    # 17
    execute_csv2_request(
        gvar, 1, 'UV19', 'value specified for a password is less than 6 characters.',
        '/user/update/', form_data={
            'password1': 'test',
            'password2': 'test'
        }
    )

    # 18
    execute_csv2_request(
        gvar, 1, 'UV19', 'value specified for a password is less then 16 characters, and does not contain a mixture of upper, lower, and numerics.',
        '/user/update/', form_data={
            'password1': 'invalid',
            'password2': 'invalid'
        }
    )

    # 19
    execute_csv2_request(
        gvar, 1, 'UV19', 'values specified for passwords do not match.',
        '/user/update/', form_data={
            'password1': 'Abc123',
            'password2': '321cbA'
        }
    )

    # 20
    execute_csv2_request(
        gvar, 1, 'UV19', 'request contained a rejected/bad parameter "join_date".',
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu6'),
            'join_date': 'invalid-unit-test'
        }
    )

    # 21
    execute_csv2_request(
        gvar, 1, 'UV19', 'request contained a rejected/bad parameter "active_group".',
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu6'),
            'active_group': 'invalid-unit-test'
        }
    )

    # 22
    execute_csv2_request(
        gvar, 1, 'UV21', 'specified group "invalid-unit-test" does not exist.',
        '/user/update/', form_data={
            'username': 'invalid-unit-test',
            'group_name': 'invalid-unit-test'
        }
    )

    # 23
    execute_csv2_request(
        gvar, 1, 'UV19', 'request contained a bad parameter "htcondor_fqdn".',
        '/user/update/', form_data={
            'username': 'invalid-unit-test',
            'htcondor_fqdn': 'invalid-unit-test'
        }
    )

    # 24
    execute_csv2_request(
        gvar, 1, 'UV21', 'user update, "{}" failed - group "{}" was specified twice.'.format(ut_id(gvar, 'utu6'), ut_id(gvar, 'utg1')),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_name.2': ut_id(gvar, 'utg1')
        }
    )

    # 25
    execute_csv2_request(
        gvar, 1, 'UV20', 'common name "{0}" conflicts with registered user "{0}".'.format(ut_id(gvar, 'utu3')),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu6'),
            'cert_cn': ut_id(gvar, 'utu3')
        }
    )

    # 26
    execute_csv2_request(
        gvar, 1, 'UV20', 'common name "{}" conflicts with registered user "{}".'.format(ut_id(gvar, 'user test user three'), ut_id(gvar, 'utu3')),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu6'),
            'cert_cn': ut_id(gvar, 'user test user three')
        }
    )

    # 27
    execute_csv2_request(
        gvar, 1, 'UV19', 'value specified for "group_option" must be one of the following options: [\'add\', \'delete\'].',
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_option': 'invalid-unit-test'
        }
    )

    # 28
    execute_csv2_request(
        gvar, 1, 'UV23', 'must specify at least one field to update.',
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_option': 'add'
        }
    )

    # 29
    execute_csv2_request(
        gvar, 1, 'UV23', 'must specify at least one field to update.',
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_option': 'delete'
        }
    )

    # 30
    execute_csv2_request(
        gvar, 1, 'UV21', 'specified group "invalid-unit-test" does not exist.',
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_option': 'add',
            'group_name': 'invalid-unit-test'
        }
    )

    # 31
    execute_csv2_request(
        gvar, 1, 'UV21', 'specified group "invalid-unit-test" does not exist.',
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_option': 'delete',
            'group_name': 'invalid-unit-test'
        }
    )

    # 32
    execute_csv2_request(
        gvar, 1, 'UV21', 'specified group "invalid-unit-test" does not exist.',
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_name.2': 'invalid-unit-test'
        }
    )

    # 33
    execute_csv2_request(
        gvar, 1, 'UV21', 'specified group "invalid-unit-test" does not exist.',
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_name.2': 'invalid-unit-test',
            'group_option': 'add'
        }
    )

    # 34
    execute_csv2_request(
        gvar, 1, 'UV21', 'specified group "invalid-unit-test" does not exist.',
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_name.2': 'invalid-unit-test',
            'group_option': 'delete'
        }
    )

    # 35
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'utu6')),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu6'),
            'cert_cn': ut_id(gvar, 'user-test-user-six')
        }
    )

    # 36
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'utu6')),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu6'),
            'cert_cn': ut_id(gvar, 'user-test-user-six')
        }
    )

    # 37
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu6')},
        values={'username': ut_id(gvar, 'utu6'), 'user_groups': None, 'cert_cn': ut_id(gvar, 'user-test-user-six')}
    )

    # 38
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'utu6')),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_name': ut_id(gvar, 'utg1')
        }
    )

    # 39
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu6')},
        values={'username': ut_id(gvar, 'utu6'), 'user_groups': ut_id(gvar, 'utg1')}
    )

    # 40
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'utu6')),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_name.2': ut_id(gvar, 'utg2')
        }
    )

    # 41
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu6')},
        values={'username': ut_id(gvar, 'utu6'), 'user_groups': ut_id(gvar, 'utg1,utg2')}
    )

    # 42
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'utu6')),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_option': 'delete'
        }
    )

    # 43
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu6')},
        values={'username': ut_id(gvar, 'utu6'), 'user_groups': ut_id(gvar, 'utg2')}
    )

    # 44
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'utu6')),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_option': 'add'
        }
    )

    # 45
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu6')},
        values={'username': ut_id(gvar, 'utu6'), 'user_groups': ut_id(gvar, 'utg1,utg2')}
    )

    # 46
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'utu6')),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_name.2': ut_id(gvar, 'utg2'),
            'group_option': 'delete'
        }
    )

    # 47
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu6')},
        values={'username': ut_id(gvar, 'utu6'), 'user_groups': None}
    )

    # 48
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'utu6')),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_name.2': ut_id(gvar, 'utg2'),
            'group_option': 'add'
        }
    )

    # 49
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu6')},
        values={'username': ut_id(gvar, 'utu6'), 'user_groups': ut_id(gvar, 'utg1,utg2')}
    )

    # 50
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'utu6')),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_name.1': ut_id(gvar, 'utg1')
        }, html=True
    )

    # 51
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu6')},
        values={'username': ut_id(gvar, 'utu6'), 'user_groups': ut_id(gvar, 'utg1')}
    )

    # 52
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'utu6')),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_name.2': ut_id(gvar, 'utg2')
        }, html=True
    )

    # 53
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu6')},
        values={'username': ut_id(gvar, 'utu6'), 'user_groups': ut_id(gvar, 'utg1,utg2')}
    )

    # 54
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'utu6')),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_name': ''
        }, html=True
    )

    # 55
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu6')},
        values={'username': ut_id(gvar, 'utu6'), 'user_groups': None}
    )

if __name__ == "__main__":
    main(None)
