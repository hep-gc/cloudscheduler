from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, sanity_requests
from sys import argv

# lno: CV - error code identifier.

def main(gvar):
    # 01 - 05
    sanity_requests(gvar, '/cloud/status/', ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctu1'), ut_id(gvar, 'ctu2'), ut_id(gvar, 'ctu2'))

    # 06
    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/status/', group=ut_id(gvar, 'ctg1'),
        expected_list='cloud_status_list', list_filter={'group_name': ut_id(gvar, 'ctg1'), 'cloud_name': ut_id(gvar, 'ctc2')},
        values={'VMs': '0'}, server_user=ut_id(gvar, 'ctu1')
    )

    # 07
    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/status/', group=ut_id(gvar, 'ctg1'), form_data={'cloud_name': ut_id(gvar, 'ctc2')},
        expected_list='cloud_status_list', list_filter={'group_name': ut_id(gvar, 'ctg1'), 'cloud_name': ut_id(gvar, 'ctc2')},
        values={
            'VMs': '0',
            'VMs_manual': '0',
            'VMs_in_error': '0',
            'VMs_starting': '0',
            'VMs_retiring': '0',
            'VMs_unregistered': '0',
            'VMs_idle': '0',
            'VMs_running': '0',
            'cores_native': '0',
            'ram_native': 0,
            'slot_count': '0',
            'slot_core_count': '0',
            'slot_idle_core_count': '0',
            'cores_ctl': -1,
            'ram_ctl': -1
        },
        server_user=ut_id(gvar, 'ctu1')
    )

if __name__ == "__main__":
    main(initialize_csv2_request(selections=argv[1] if len(argv) > 1 else ''))
