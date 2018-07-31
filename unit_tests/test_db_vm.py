from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id
import sys

# lno: VV - error code identifier.

def main(gvar, user_secret):
    if not gvar:
        gvar = {}
        if len(sys.argv) > 1:
            initialize_csv2_request(gvar, sys.argv[0], selections=sys.argv[1])
        else:
            initialize_csv2_request(gvar, sys.argv[0])

    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', form_data={'group': 'vm-test-group'},
        list='vm_list', filter={'group_name': 'vm-test-group', 'cloud_name': 'vm-test-cloud', 'vmid': 'vmid1'},
        values={'power_status': 1, 'auth_url': 'vm-test-authurl', 'activity': None, 'manual_control': 0, 'idle_time': None, 'condor_slots': None, 'project': 'vm-test-project', 'cores': None, 'last_updated': '2018-07-30 14:18:02', 'machine': None, 'ram': None, 'status': 'ACTIVE', 'retire_request_time': None, 'my_current_time': None, 'condor_slots_used': None, 'terminate_time': None, 'retired_time': None, 'disk': None, 'group_name': 'vm-test-group', 'terminate': 0, 'state': None, 'task': None, 'status_changed_time': '2018-07-30 05:55:57', 'flavor_id': '5', 'flavor_name': None, 'poller_status': 'unregistered', 'foreign_vm': 0, 'entered_current_state': None, 'hostname': 'vm-test-group--vm-test-cloud--vmid1', 'swap': None, 'vmid': 'vmid1', 'keep_alive':0, 'cloud_name': 'vm-test-cloud'}
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', form_data={'group': 'vm-test-group'},
        list='vm_list', filter={'group_name': 'vm-test-group', 'cloud_name': 'vm-test-cloud', 'vmid': 'vmid2'},
        values={'power_status': 1, 'auth_url': 'vm-test-authurl', 'activity': None, 'manual_control': 0, 'idle_time': None, 'condor_slots': None, 'project': 'vm-test-project', 'cores': None, 'last_updated': '2018-07-30 14:18:02', 'machine': None, 'ram': None, 'status': 'ACTIVE', 'retire_request_time': None, 'my_current_time': None, 'condor_slots_used': None, 'terminate_time': None, 'retired_time': None, 'disk': None, 'group_name': 'vm-test-group', 'terminate': 0, 'state': None, 'task': None, 'status_changed_time': '2018-07-30 12:43:22', 'flavor_id': '4', 'flavor_name': None, 'poller_status': 'unregistered', 'foreign_vm': 0, 'entered_current_state': None, 'hostname': 'vm-test-group--vm-test-cloud--vmid2', 'swap': None, 'vmid': 'vmid2', 'keep_alive':0, 'cloud_name': 'vm-test-cloud'}
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', form_data={'group': 'vm-test-group'},
        list='vm_list', filter={'group_name': 'vm-test-group', 'cloud_name': 'vm-test-cloud', 'vmid': 'vmid3'},
        values={'power_status': 1, 'auth_url': 'vm-test-authurl', 'activity': None, 'manual_control': 0, 'idle_time': None, 'condor_slots': None, 'project': 'vm-test-project', 'cores': None, 'last_updated': '2018-07-30 14:18:02', 'machine': None, 'ram': None, 'status': 'ACTIVE', 'retire_request_time': None, 'my_current_time': None, 'condor_slots_used': None, 'terminate_time': None, 'retired_time': None, 'disk': None, 'group_name': 'vm-test-group', 'terminate': 0, 'state': None, 'task': None, 'status_changed_time': '2018-07-30 12:48:18', 'flavor_id': '4', 'flavor_name': None, 'poller_status': 'unregistered', 'foreign_vm': 0, 'entered_current_state': None, 'hostname': 'vm-test-group--vm-test-cloud--vmid3', 'swap': None, 'vmid': 'vmid3', 'keep_alive':0, 'cloud_name': 'vm-test-cloud'}
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', form_data={'group': 'vm-test-group'},
        list='vm_list', filter={'group_name': 'vm-test-group', 'cloud_name': 'vm-test-cloud', 'vmid': 'vmid4'},
        values={'power_status': 1, 'auth_url': 'vm-test-authurl', 'activity': None, 'manual_control': 0, 'idle_time': None, 'condor_slots': None, 'project': 'vm-test-project', 'cores': None, 'last_updated': '2018-07-30 14:18:02', 'machine': None, 'ram': None, 'status': 'ACTIVE', 'retire_request_time': None, 'my_current_time': None, 'condor_slots_used': None, 'terminate_time': None, 'retired_time': None, 'disk': None, 'group_name': 'vm-test-group', 'terminate': 0, 'state': None, 'task': None, 'status_changed_time': '2018-07-30 12:48:18', 'flavor_id': '4', 'flavor_name': None, 'poller_status': 'foreign', 'foreign_vm': 1, 'entered_current_state': None, 'hostname': 'foreign-cloud--vmid4', 'swap': None, 'vmid': 'vmid4', 'keep_alive': 0, 'cloud_name': 'vm-test-cloud'}
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', form_data={'group': 'vm-test-group'},
        list='vm_list', filter={'group_name': 'vm-test-group', 'cloud_name': 'vm-test-cloud', 'vmid': 'vmid5'},
        values={'power_status': 1, 'auth_url': 'vm-test-authurl', 'activity': None, 'manual_control': 0, 'idle_time': None, 'condor_slots': None, 'project': 'vm-test-project', 'cores': None, 'last_updated': '2018-07-30 14:18:02', 'machine': None, 'ram': None, 'status': 'ACTIVE', 'retire_request_time': None, 'my_current_time': None, 'condor_slots_used': None, 'terminate_time': None, 'retired_time': None, 'disk': None, 'group_name': 'vm-test-group', 'terminate': 0, 'state': None, 'task': None, 'status_changed_time': '2018-07-30 12:48:18', 'flavor_id': '4', 'flavor_name': None, 'poller_status': 'foreign', 'foreign_vm': 1, 'entered_current_state': None, 'hostname': 'foreign-cloud--vmid5', 'swap': None, 'vmid': 'vmid5', 'keep_alive': 0, 'cloud_name': 'vm-test-cloud'}
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', form_data={'group': 'vm-test-group'},
        list='vm_list', filter={'group_name': 'vm-test-group', 'cloud_name': 'vm-test-cloud', 'vmid': 'vmid6'},
        values={'power_status': 1, 'auth_url': 'vm-test-authurl', 'activity': None, 'manual_control': 0, 'idle_time': None, 'condor_slots': None, 'project': 'vm-test-project', 'cores': None, 'last_updated': '2018-07-30 14:18:02', 'machine': None, 'ram': None, 'status': 'ACTIVE', 'retire_request_time': None, 'my_current_time': None, 'condor_slots_used': None, 'terminate_time': None, 'retired_time': None, 'disk': None, 'group_name': 'vm-test-group', 'terminate': 0, 'state': None, 'task': None, 'status_changed_time': '2018-07-30 12:48:18', 'flavor_id': '4', 'flavor_name': None, 'poller_status': 'foreign', 'foreign_vm': 1, 'entered_current_state': None, 'hostname': 'foreign-cloud--vmid6', 'swap': None, 'vmid': 'vmid6', 'keep_alive': 0, 'cloud_name': 'vm-test-cloud'}
    )

    execute_csv2_request(
        gvar, 0, None, "vm update, VMs set to manual control=1.",
        '/vm/update/', form_data={'vm_option': 'manctl', 'hostname': 'vm-test-group--vm-test-cloud--vmid1'}
    )

    execute_csv2_request(
        gvar, 0, None, "vm update, VMs set to manual control=3.",
        '/vm/update/', form_data={'vm_option': 'manctl'}
    )

    execute_csv2_request(
        gvar, 0, None, "vm update, VMs set to system control=1.",
        '/vm/update/', form_data={'vm_option': 'sysctl', 'hostname': 'vm-test-group--vm-test-cloud--vmid2'}
    )

    execute_csv2_request(
        gvar, 0, None, "vm update, VMs set to system control=3.",
        '/vm/update/', form_data={'vm_option': 'sysctl'}
    )

    execute_csv2_request(
        gvar, 0, None, "vm update, VMs retired=1.",
        '/vm/update/', form_data={'vm_option': 'retire', 'hostname': 'vm-test-group--vm-test-cloud--vmid3'}
    )

    execute_csv2_request(
        gvar, 0, None, "vm update, VMs retired=3.",
        '/vm/update/', form_data={'vm_option': 'retire'}
    )

    execute_csv2_request(
        gvar, 0, None, "vm update, VMs killed=0.",
        '/vm/update/', form_data={'vm_option': 'kill', 'hostname': 'foreign-cloud--vmid4'}
    )

    execute_csv2_request(
        gvar, 0, None, "vm update, VMs killed=1.",
        '/vm/update/', form_data={'vm_option': 'kill', 'hostname': 'vm-test-group--vm-test-cloud--vmid1'}
    )

    execute_csv2_request(
        gvar, 0, None, "vm update, VMs killed=3.",
        '/vm/update/', form_data={'vm_option': 'kill'}
    )

if __name__ == "__main__":
    main(None)