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
        '/user/update/', #I assume that this request does not reqire a group specification (same for all requests below)
        server_user='invalid-unit-test'
    )

    # 02
    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 403, forbidden.',
        '/user/update/',
        server_user=ut_id(gvar, 'utu1')
    )

    # 03
    execute_csv2_request(
        gvar, 1, 'UV', 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'utu2')),
        '/user/update/',
        server_user=ut_id(gvar, 'utu2')
    )

    # 04
    execute_csv2_request(
        gvar, 1, 'UV', 'invalid method "GET" specified.',
        '/user/update/',
        server_user=ut_id(gvar, 'utu4')
    )

    # 05
    execute_csv2_request(
        gvar, 1, 'UV', 'cannot switch to invalid group "invalid-unit-test".',
        '/user/update/', group='invalid-unit-test',
        server_user=ut_id(gvar, 'utu4')
    )

    # 06
    execute_csv2_request(
        gvar, 1, 'UV', 'cannot switch to invalid group "{}".'.format(ut_id(gvar, 'utg2')),
        '/user/update/', group=ut_id(gvar, 'utg2'),
        server_user=ut_id(gvar, 'utu4')
    )

    # 07
    execute_csv2_request(
        gvar, 1, 'UV', 'request contained a bad parameter "invalid-unit-test".',
        '/user/update/'
, form_data={'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'utu4')
    )

    # 08
    execute_csv2_request(
        gvar, 1, 'UV', 'value specified for "username" must be all lower case.',
        '/user/update/'
, form_data={'username': 'Invalid-unit-test'},
        server_user=ut_id(gvar, 'utu4')
    )

    # 09
    execute_csv2_request(
        gvar, 1, 'UV', 'must specify at least one field to update.',
        '/user/update/'
, form_data={'username': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'utu4')
    )

    # 10
    execute_csv2_request(
        gvar, 1, 'UV', 'the request did not match any rows.',
        '/user/update/'
, form_data={
            'username': 'invalid-unit-test',
            'password': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 11
    execute_csv2_request(
        gvar, 1, 'UV', 'must specify at least one field to update.',
        '/user/update/'
, form_data={'username': ut_id(gvar, 'utu6')},
        server_user=ut_id(gvar, 'utu4')
    )

    # 12
    execute_csv2_request(
        gvar, 1, 'UV', 'boolean value specified for "is_superuser" must be one of the following: true, false, yes, no, 1, or 0.',
        '/user/update/'
, form_data={'is_superuser': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'utu4')
    )

    # 13
    execute_csv2_request(
        gvar, 1, 'UV', 'value specified for a password is less than 6 characters.',
        '/user/update/'
, form_data={'password': 'test'},
        server_user=ut_id(gvar, 'utu4')
    )

    # 14
    execute_csv2_request(
        gvar, 1, 'UV', 'value specified for a password is less then 16 characters, and does not contain a mixture of upper, lower, and numerics.',
        '/user/update/'
, form_data={'password': 'invalid'},
        server_user=ut_id(gvar, 'utu4')
    )

    # 15
    execute_csv2_request(
        gvar, 1, 'UV', 'password update received a password but no verify password; both are required.',
        '/user/update/'
, form_data={'password1': 'test'},
        server_user=ut_id(gvar, 'utu4')
    )

    # 16
    execute_csv2_request(
        gvar, 1, 'UV', 'password update received a verify password but no password; both are required.',
        '/user/update/'
, form_data={'password2': 'test'},
        server_user=ut_id(gvar, 'utu4')
    )

    # 17
    execute_csv2_request(
        gvar, 1, 'UV', 'value specified for a password is less than 6 characters.',
        '/user/update/'
, form_data={
            'password1': 'test',
            'password2': 'test'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 18
    execute_csv2_request(
        gvar, 1, 'UV', 'value specified for a password is less then 16 characters, and does not contain a mixture of upper, lower, and numerics.',
        '/user/update/'
, form_data={
            'password1': 'invalid',
            'password2': 'invalid'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 19
    execute_csv2_request(
        gvar, 1, 'UV', 'values specified for passwords do not match.',
        '/user/update/'
, form_data={
            'password1': 'Abc123',
            'password2': '321cbA'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 20
    execute_csv2_request(
        gvar, 1, 'UV', 'request contained a rejected/bad parameter "join_date".',
        '/user/update/'
, form_data={
            'username': ut_id(gvar, 'utu6'),
            'join_date': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 21
    execute_csv2_request(
        gvar, 1, 'UV', 'request contained a rejected/bad parameter "active_group".',
        '/user/update/'
, form_data={
            'username': ut_id(gvar, 'utu6'),
            'active_group': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 22
    execute_csv2_request(
        gvar, 1, 'UV', 'specified group "invalid-unit-test" does not exist.',
        '/user/update/'
, form_data={
            'username': 'invalid-unit-test',
            'group_name': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 23
    execute_csv2_request(
        gvar, 1, 'UV', 'request contained a bad parameter "htcondor_fqdn".',
        '/user/update/'
, form_data={
            'username': 'invalid-unit-test',
            'htcondor_fqdn': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 24
    execute_csv2_request(
        gvar, 1, 'UV', 'user update, "{}" failed - group "{}" was specified twice.'.format(ut_id(gvar, 'utu6'), ut_id(gvar, 'utg1')),
        '/user/update/'
, form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_name.2': ut_id(gvar, 'utg1')
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 25
    execute_csv2_request(
        gvar, 1, 'UV', 'common name "{0}" conflicts with registered user "{0}".'.format(ut_id(gvar, 'utu3')),
        '/user/update/'
, form_data={
            'username': ut_id(gvar, 'utu6'),
            'cert_cn': ut_id(gvar, 'utu3')
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 26
    execute_csv2_request(
        gvar, 1, 'UV', 'common name "{}" conflicts with registered user "{}".'.format(ut_id(gvar, 'user test user three'), ut_id(gvar, 'utu3')),
        '/user/update/'
, form_data={
            'username': ut_id(gvar, 'utu6'),
            'cert_cn': ut_id(gvar, 'user test user three')
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 27
    execute_csv2_request(
        gvar, 1, 'UV', 'value specified for "group_option" must be one of the following options: [\'add\', \'delete\'].',
        '/user/update/'
, form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_option': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 28
    execute_csv2_request(
        gvar, 1, 'UV', 'must specify at least one field to update.',
        '/user/update/'
, form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_option': 'add'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 29
    execute_csv2_request(
        gvar, 1, 'UV', 'must specify at least one field to update.',
        '/user/update/'
, form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_option': 'delete'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 30
    execute_csv2_request(
        gvar, 1, 'UV', 'specified group "invalid-unit-test" does not exist.',
        '/user/update/'
, form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_option': 'add',
            'group_name': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 31
    execute_csv2_request(
        gvar, 1, 'UV', 'specified group "invalid-unit-test" does not exist.',
        '/user/update/'
, form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_option': 'delete',
            'group_name': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 32
    execute_csv2_request(
        gvar, 1, 'UV', 'specified group "invalid-unit-test" does not exist.',
        '/user/update/'
, form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_name.2': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 33
    execute_csv2_request(
        gvar, 1, 'UV', 'specified group "invalid-unit-test" does not exist.',
        '/user/update/'
, form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_name.2': 'invalid-unit-test',
            'group_option': 'add'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 34
    execute_csv2_request(
        gvar, 1, 'UV', 'specified group "invalid-unit-test" does not exist.',
        '/user/update/'
, form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_name.2': 'invalid-unit-test',
            'group_option': 'delete'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 35
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'utu6')),
        '/user/update/'
, form_data={
            'username': ut_id(gvar, 'utu6'),
            'cert_cn': ut_id(gvar, 'user-test-user-six')
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 36
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'utu6')),
        '/user/update/'
, form_data={
            'username': ut_id(gvar, 'utu6'),
            'cert_cn': ut_id(gvar, 'user-test-user-six')
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 37
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        expected_list='user_list', list_filter={'username': ut_id(gvar, 'utu6')},
        values={'username': ut_id(gvar, 'utu6'), 'user_groups': None, 'cert_cn': ut_id(gvar, 'user-test-user-six')},
        server_user=ut_id(gvar, 'utu4')
    )

    # 38
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'utu6')),
        '/user/update/'
, form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_name': ut_id(gvar, 'utg1')
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 39
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        expected_list='user_list', list_filter={'username': ut_id(gvar, 'utu6')},
        values={'username': ut_id(gvar, 'utu6'), 'user_groups': ut_id(gvar, 'utg1')},
        server_user=ut_id(gvar, 'utu4')
    )

    # 40
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'utu6')),
        '/user/update/'
, form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_name.2': ut_id(gvar, 'utg2')
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 41
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        expected_list='user_list', list_filter={'username': ut_id(gvar, 'utu6')},
        values={'username': ut_id(gvar, 'utu6'), 'user_groups': ut_id(gvar, 'utg1,utg2')},
        server_user=ut_id(gvar, 'utu4')
    )

    # 42
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'utu6')),
        '/user/update/'
, form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_option': 'delete'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 43
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        expected_list='user_list', list_filter={'username': ut_id(gvar, 'utu6')},
        values={'username': ut_id(gvar, 'utu6'), 'user_groups': ut_id(gvar, 'utg2')},
        server_user=ut_id(gvar, 'utu4')
    )

    # 44
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'utu6')),
        '/user/update/'
, form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_option': 'add'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 45
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        expected_list='user_list', list_filter={'username': ut_id(gvar, 'utu6')},
        values={'username': ut_id(gvar, 'utu6'), 'user_groups': ut_id(gvar, 'utg1,utg2')},
        server_user=ut_id(gvar, 'utu4')
    )

    # 46
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'utu6')),
        '/user/update/'
, form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_name.2': ut_id(gvar, 'utg2'),
            'group_option': 'delete'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 47
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        expected_list='user_list', list_filter={'username': ut_id(gvar, 'utu6')},
        values={'username': ut_id(gvar, 'utu6'), 'user_groups': None},
        server_user=ut_id(gvar, 'utu4')
    )

    # 48
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'utu6')),
        '/user/update/'
, form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_name.2': ut_id(gvar, 'utg2'),
            'group_option': 'add'
        },
        server_user=ut_id(gvar, 'utu4')
    )

    # 49
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        expected_list='user_list', list_filter={'username': ut_id(gvar, 'utu6')},
        values={'username': ut_id(gvar, 'utu6'), 'user_groups': ut_id(gvar, 'utg1,utg2')},
        server_user=ut_id(gvar, 'utu4')
    )

    # 50
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'utu6')),
        '/user/update/'
, form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_name.1': ut_id(gvar, 'utg1')
        },
        server_user=ut_id(gvar, 'utu4'), html=True
    )

    # 51
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        expected_list='user_list', list_filter={'username': ut_id(gvar, 'utu6')},
        values={'username': ut_id(gvar, 'utu6'), 'user_groups': ut_id(gvar, 'utg1')},
        server_user=ut_id(gvar, 'utu4')
    )

    # 52
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'utu6')),
        '/user/update/'
, form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_name.2': ut_id(gvar, 'utg2')
        },
        server_user=ut_id(gvar, 'utu4'), html=True
    )

    # 53
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        expected_list='user_list', list_filter={'username': ut_id(gvar, 'utu6')},
        values={'username': ut_id(gvar, 'utu6'), 'user_groups': ut_id(gvar, 'utg1,utg2')},
        server_user=ut_id(gvar, 'utu4')
    )

    # 54
    execute_csv2_request(
        gvar, 0, None, 'user update, parameter "group_name" contains an empty string which is specifically disallowed.'.format(ut_id(gvar, 'utu6')),
        '/user/update/'
, form_data={
            'username': ut_id(gvar, 'utu6'),
            'group_name': ''
        },
        server_user=ut_id(gvar, 'utu4'), html=True
    )

if __name__ == "__main__":
    main(None)
