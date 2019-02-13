from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id
from sys import argv

# lno: CV - error code identifier.

def main(gvar, user_secret):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv2_request(gvar, argv[0])
    
    # 01
    execute_csv2_request(
        gvar, 2, None, 'server "unit-test", HTTP response code 401, unauthorized.',
        '/cloud/status/',
        server_user='invalid-unit-test', server_pw=user_secret
    )

    # 02
    execute_csv2_request(
        gvar, 1, 'CV33', 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'ctu1')),
        '/cloud/status/',
        server_user=ut_id(gvar, 'ctu1'), server_pw=user_secret
    )

    # 03
    execute_csv2_request(
        gvar, 1, 'CV33', 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'ctu2')),
        '/cloud/status/',
        server_user=ut_id(gvar, 'ctu2'), server_pw=user_secret
    )

    # 04
    execute_csv2_request(
        gvar, 1, 'CV33', 'cannot switch to invalid group "invalid-unit-test".',
        '/cloud/status/', form_data={'group': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 05
    execute_csv2_request(
        gvar, 1, 'CV33', 'cannot switch to invalid group "{}".'.format(ut_id(gvar, 'ctg2')),
        '/cloud/status/', form_data={'group': ut_id(gvar, 'ctg2')},
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 06
    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/status/',
        list='cloud_status_list', filter={'cloud_name': ut_id(gvar, 'ctc2')},
        values={
            'group_name': ut_id(gvar, 'ctg1'),
            'cloud_name': ut_id(gvar, 'ctc2'),
            'ram_ctl': -1,
            'default_flavor': None,
            'keep_alive': 0,
            'default_image': None,
            'enabled': 1,
            'cores_ctl': -1,
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

if __name__ == "__main__":
    main(None)
