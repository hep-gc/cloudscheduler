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
        gvar, 1, 'CV', 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'ctu1')),
        '/cloud/status/',
        server_user=ut_id(gvar, 'ctu1'), server_pw=user_secret
    )

    # 03
    execute_csv2_request(
        gvar, 1, 'CV', 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'ctu2')),
        '/cloud/status/',
        server_user=ut_id(gvar, 'ctu2'), server_pw=user_secret
    )

    # 04
    execute_csv2_request(
        gvar, 1, 'CV', 'cannot switch to invalid group "invalid-unit-test".',
        '/cloud/status/', group='invalid-unit-test',
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

    # 05
    execute_csv2_request(
        gvar, 1, 'CV', 'cannot switch to invalid group "{}".'.format(ut_id(gvar, 'ctg2')),
        '/cloud/status/', group=ut_id(gvar, 'ctg2'),
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
            'VMs': '0',
            'VMs_manual': '0',
            'VMs_in_error': '0',
            'VMs_starting': '0',
            'VMs_retiring': '0',
            'VMs_unregistered': '0',
            'VMs_idle': '0',
            'VMs_running': '0',
            'cores_native': '0',
            'ram_native': '0',
            'slot_count': '0',
            'slot_core_count': '0',
            'slot_idle_core_count': '0',
            'Foreign_VMs': '0',
            'enabled': 1,
            'cores_ctl': -1,
            'cores_limit': 0,
            'VMs_quota': 0,
            'VMs_native_foreign': '0',
            'cores_quota': 0,
            'cores_foreign': '0',
            'cores_native_foreign': '0',
            'ram_ctl': -1,
            'ram_limit': 0,
            'ram_quota': 0,
            'ram_foreign': '0',
            'ram_native_foreign': '0',
        },
        server_user=ut_id(gvar, 'ctu3'), server_pw=user_secret
    )

if __name__ == "__main__":
    main(None)
