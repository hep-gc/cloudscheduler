from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, generate_secret
from sys import argv

# lno: UV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv2_request(gvar, argv[0])
    
    new_secret = generate_secret()
    
    # 1
    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 401, unauthorized.',
        '/user/settings/',
        server_user='invalid-unit-test'
    )

    # 2
    execute_csv2_request(
        gvar, 1, 'UV', 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'utu1')),
        '/user/settings/',
        server_user=ut_id(gvar, 'utu1')
    )

    # 3
    execute_csv2_request(
        gvar, 1, 'UV', 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'utu2')),
        '/user/settings/',
        server_user=ut_id(gvar, 'utu2')
    )

    # 4
    execute_csv2_request(
        gvar, 1, 'UV', 'cannot switch to invalid group "invalid-unit-test".',
        '/user/settings/', group='invalid-unit-test',
        server_user=ut_id(gvar, 'utu3')
    )

    # 5
    execute_csv2_request(
        gvar, 1, 'UV', 'cannot switch to invalid group "{}".'.format(ut_id(gvar, 'utg2')),
        '/user/settings/', group=ut_id(gvar, 'utg2'),
        server_user=ut_id(gvar, 'utu3')
    )

    # 6
    execute_csv2_request(
        gvar, 1, 'UV', 'request contained a unnamed/bad parameter "invalid-unit-test".',
        '/user/settings/' , form_data={'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'utu3')
    )

    # 7
    execute_csv2_request(
        gvar, 1, 'UV', 'value specified for a password is less than 6 characters.',
        '/user/settings/' , form_data={'password': 'test'},
        server_user=ut_id(gvar, 'utu3')
    )

    # 8
    execute_csv2_request(
        gvar, 1, 'UV', 'value specified for a password is less then 16 characters, and does not contain a mixture of upper, lower, and numerics.',
        '/user/settings/', form_data={'password': 'invalid'},
        server_user=ut_id(gvar, 'utu3')
    )

    # 9
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'utu3')),
        '/user/settings/', form_data={'password': new_secret},
        server_user=ut_id(gvar, 'utu3')
    )

    # 10
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'utu3')),
        '/user/settings/', form_data={'password': gvar['user_secret']},
        server_user=ut_id(gvar, 'utu3'), server_pw=new_secret
    )

    # 11
    execute_csv2_request(
        gvar, 1, 'UV', 'password update received a password but no verify password; both are required.',
        '/user/settings/', form_data={'password1': 'test'},
        server_user=ut_id(gvar, 'utu3')
    )

    # 12
    execute_csv2_request(
        gvar, 1, 'UV', 'password update received a verify password but no password; both are required.',
        '/user/settings/', form_data={'password2': 'test'},
        server_user=ut_id(gvar, 'utu3')
    )

    # 13
    execute_csv2_request(
        gvar, 1, 'UV', 'value specified for a password is less than 6 characters.',
        '/user/settings/', form_data={
            'password1': 'test',
            'password2': 'test'
        },
        server_user=ut_id(gvar, 'utu3')
    )

    # 14
    execute_csv2_request(
        gvar, 1, 'UV', 'value specified for a password is less then 16 characters, and does not contain a mixture of upper, lower, and numerics.',
        '/user/settings/', form_data={
            'password1': 'invalid',
            'password2': 'invalid'
        },
        server_user=ut_id(gvar, 'utu3')
    )

    # 15
    execute_csv2_request(
        gvar, 1, 'UV', 'values specified for passwords do not match.',
        '/user/settings/', form_data={
            'password1': 'Abc123',
            'password2': '321cbA'
        },
        server_user=ut_id(gvar, 'utu3')
    )

    # 16
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'utu3')),
        '/user/settings/', form_data={
            'password1': new_secret,
            'password2': new_secret
        },
        server_user=ut_id(gvar, 'utu3')
    )

    # 17
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'utu3')),
        '/user/settings/', form_data={
            'password1': gvar['user_secret'],
            'password2': gvar['user_secret']
        },
        server_user=ut_id(gvar, 'utu3'), server_pw=new_secret
    )

if __name__ == "__main__":
    main(None)
