from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, generate_secret, sanity_requests
from sys import argv

# lno: UV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)
    
    new_secret = generate_secret()
    
    # 01 - 05
    sanity_requests(gvar, '/user/settings/', ut_id(gvar, 'utg1'), ut_id(gvar, 'utu3'), ut_id(gvar, 'utg2'), ut_id(gvar, 'utu1'))

    # We cannot use parameters_requests() because /user/settings/ accepts both GET and POST requests.

    # 06
    execute_csv2_request(
        gvar, 1, 'UV', 'user update, request contained a unnamed/bad parameter "password.1".',
        '/user/settings/', group=ut_id(gvar, 'utg1'), form_data={
            'password.1': gvar['user_secret'],
            'password.2': gvar['user_secret']
        },
        server_user=ut_id(gvar, 'utu3')
    )

    # 07
    execute_csv2_request(
        gvar, 1, 'UV', 'value specified for a password is less than 6 characters.',
        '/user/settings/', group=ut_id(gvar, 'utg1'), form_data={'password': 'inv'},
        server_user=ut_id(gvar, 'utu3')
    )

    # 08
    execute_csv2_request(
        gvar, 1, 'UV', 'value specified for a password is less then 16 characters, and does not contain a mixture of upper, lower, and numerics.',
        '/user/settings/', group=ut_id(gvar, 'utg1'), form_data={'password': 'invalid'},
        server_user=ut_id(gvar, 'utu3')
    )

    # 09
    execute_csv2_request(
        gvar, 1, 'UV', 'user update, request contained a unnamed/bad parameter "password1.1".',
        '/user/settings/', group=ut_id(gvar, 'utg1'), form_data={
            'password1.1': gvar['user_secret'],
            'password1.2': gvar['user_secret']
        },
        server_user=ut_id(gvar, 'utu3')
    )

    # 10
    execute_csv2_request(
        gvar, 1, 'UV', 'password update received a password but no verify password; both are required.',
        '/user/settings/', group=ut_id(gvar, 'utg1'), form_data={'password1': gvar['user_secret']},
        server_user=ut_id(gvar, 'utu3')
    )

    # 11
    execute_csv2_request(
        gvar, 1, 'UV', 'user update, request contained a unnamed/bad parameter "password2.1".',
        '/user/settings/', group=ut_id(gvar, 'utg1'), form_data={
            'password2.1': gvar['user_secret'],
            'password2.2': gvar['user_secret']
        },
        server_user=ut_id(gvar, 'utu3')
    )

    # 12
    execute_csv2_request(
        gvar, 1, 'UV', 'password update received a verify password but no password; both are required.',
        '/user/settings/', group=ut_id(gvar, 'utg1'), form_data={'password2': gvar['user_secret']},
        server_user=ut_id(gvar, 'utu3')
    )

    # 13
    execute_csv2_request(
        gvar, 1, 'UV', 'value specified for a password is less than 6 characters.',
        '/user/settings/', group=ut_id(gvar, 'utg1'), form_data={
            'password1': 'inv',
            'password2': 'inv'
        },
        server_user=ut_id(gvar, 'utu3')
    )

    # 14
    execute_csv2_request(
        gvar, 1, 'UV', 'value specified for a password is less then 16 characters, and does not contain a mixture of upper, lower, and numerics.',
        '/user/settings/', group=ut_id(gvar, 'utg1'), form_data={
            'password1': 'invalid',
            'password2': 'invalid'
        },
        server_user=ut_id(gvar, 'utu3')
    )

    # 15
    execute_csv2_request(
        gvar, 1, 'UV', 'values specified for passwords do not match.',
        '/user/settings/', group=ut_id(gvar, 'utg1'), form_data={
            'password1': 'Abc123',
            'password2': '321cbA'
        },
        server_user=ut_id(gvar, 'utu3')
    )

    # 16
    execute_csv2_request(
        gvar, 1, 'UV', 'user update, request contained a unnamed/bad parameter "default_group.1".',
        '/user/settings/', group=ut_id(gvar, 'utg1'), form_data={
            'default_group.1': 'invalid-unit-test',
            'default_group.2': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'utu3')
    )

    # 17 Attempt to set the default_group to one that does not exist.
    execute_csv2_request(
        gvar, 1, 'UV', 'my settings unable to update default - user is not a member of the specified group (invalid-unit-test).',
        '/user/settings/', group=ut_id(gvar, 'utg1'), form_data={'default_group': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'utu3')
    )

    # 18
    execute_csv2_request(
        gvar, 1, 'UV', 'user update, request contained a unnamed/bad parameter "flag_show_foreign_global_vms.1".',
        '/user/settings/', group=ut_id(gvar, 'utg1'), form_data={
            'flag_show_foreign_global_vms.1': 0,
            'flag_show_foreign_global_vms.2': 0
        },
        server_user=ut_id(gvar, 'utu3')
    )

    # 19
    execute_csv2_request(
        gvar, 1, 'UV', 'user update, boolean value specified for "flag_global_status" must be one of the following: true, false, yes, no, 1, or 0.',
        '/user/settings/', group=ut_id(gvar, 'utg1'), form_data={'flag_global_status': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'utu3')
    )

    # 20
    execute_csv2_request(
        gvar, 1, 'UV', 'user update, boolean value specified for "flag_jobs_by_target_alias" must be one of the following: true, false, yes, no, 1, or 0.',
        '/user/settings/', group=ut_id(gvar, 'utg1'), form_data={'flag_jobs_by_target_alias': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'utu3')
    )

    # 21
    execute_csv2_request(
        gvar, 1, 'UV', 'user update, boolean value specified for "flag_show_foreign_global_vms" must be one of the following: true, false, yes, no, 1, or 0.',
        '/user/settings/', group=ut_id(gvar, 'utg1'), form_data={'flag_show_foreign_global_vms': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'utu3')
    )

    # 22
    execute_csv2_request(
        gvar, 1, 'UV', 'user update, boolean value specified for "flag_show_slot_detail" must be one of the following: true, false, yes, no, 1, or 0.',
        '/user/settings/', group=ut_id(gvar, 'utg1'), form_data={'flag_show_slot_detail': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'utu3')
    )

    # 23
    execute_csv2_request(
        gvar, 1, 'UV', 'user update, boolean value specified for "flag_show_slot_flavors" must be one of the following: true, false, yes, no, 1, or 0.',
        '/user/settings/', group=ut_id(gvar, 'utg1'), form_data={'flag_show_slot_flavors': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'utu3')
    )

    # 24
    execute_csv2_request(
        gvar, 1, 'UV', 'user update, request contained a unnamed/bad parameter "status_refresh_interval.1".',
        '/user/settings/', group=ut_id(gvar, 'utg1'), form_data={
            'status_refresh_interval.1': 'invalid-unit-test',
            'status_refresh_interval.2': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'utu3')
    )

    # 25
    execute_csv2_request(
        gvar, 1, 'UV', 'user update, value specified for "status_refresh_interval" must be an integer value.',
        '/user/settings/', group=ut_id(gvar, 'utg1'), form_data={'status_refresh_interval': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'utu3')
    )

    # 26
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'utu3')),
        '/user/settings/', group=ut_id(gvar, 'utg1'), form_data={
            'password': new_secret,
            'default_group': ut_id(gvar, 'utg1'),
            'flag_show_foreign_global_vms': 0,
            'flag_global_status': 1
        },
        server_user=ut_id(gvar, 'utu3')
    )

    # 27
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'utu3')),
        '/user/settings/', group=ut_id(gvar, 'utg1'), form_data={
            'password1': gvar['user_secret'],
            'password2': gvar['user_secret']
        },
        server_user=ut_id(gvar, 'utu3'), server_pw=new_secret
    )

    # 28 Ensure a GET request returns the current settings, and ensure that these settings are what we set them to.
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/settings/', group=ut_id(gvar, 'utg1'),
        expected_list='user_list', list_filter={'username': ut_id(gvar, 'utu3')}, values={
            'default_group': ut_id(gvar, 'utg1'),
            'flag_show_foreign_global_vms': 0,
            'flag_global_status': 1
        },
        server_user=ut_id(gvar, 'utu3')
    )

if __name__ == "__main__":
    main(None)
