from unit_test_common import execute_csv2_request, execute_csv2_command, initialize_csv2_request, ut_id
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
        values={'power_status': 1, 'auth_url': 'vm-test-authurl', 'manual_control': 0, 'project': 'vm-test-project', 'status': 'ACTIVE', 'retire_request_time': 0, 'group_name': 'vm-test-group', 'terminate': 0, 'flavor_id': '5', 'poller_status': 'unregistered', 'foreign_vm': 0, 'hostname': 'vm-test-group--vm-test-cloud--vmid1', 'vmid': 'vmid1', 'keep_alive':0, 'cloud_name': 'vm-test-cloud'}
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', form_data={'group': 'vm-test-group'},
        list='vm_list', filter={'group_name': 'vm-test-group', 'cloud_name': 'vm-test-cloud', 'vmid': 'vmid2'},
        values={'power_status': 1, 'auth_url': 'vm-test-authurl', 'manual_control': 0, 'project': 'vm-test-project', 'status': 'ACTIVE', 'retire_request_time': 0, 'group_name': 'vm-test-group', 'terminate': 0, 'flavor_id': '4', 'poller_status': 'unregistered', 'foreign_vm': 0, 'hostname': 'vm-test-group--vm-test-cloud--vmid2', 'vmid': 'vmid2', 'keep_alive':0, 'cloud_name': 'vm-test-cloud'}
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', form_data={'group': 'vm-test-group'},
        list='vm_list', filter={'group_name': 'vm-test-group', 'cloud_name': 'vm-test-cloud', 'vmid': 'vmid3'},
        values={'power_status': 1, 'auth_url': 'vm-test-authurl', 'manual_control': 0, 'project': 'vm-test-project', 'status': 'ACTIVE', 'retire_request_time': 0, 'group_name': 'vm-test-group', 'terminate': 0, 'flavor_id': '4', 'poller_status': 'unregistered', 'foreign_vm': 0, 'hostname': 'vm-test-group--vm-test-cloud--vmid3', 'vmid': 'vmid3', 'keep_alive':0, 'cloud_name': 'vm-test-cloud'}
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', form_data={'group': 'vm-test-group'},
        list='vm_list', filter={'group_name': 'vm-test-group', 'cloud_name': 'vm-test-cloud', 'vmid': 'vmid4'},
        values={'power_status': 1, 'auth_url': 'vm-test-authurl', 'manual_control': 0, 'project': 'vm-test-project', 'status': 'ACTIVE', 'retire_request_time': None, 'group_name': 'vm-test-group', 'terminate': 0, 'flavor_id': '4', 'poller_status': 'foreign', 'foreign_vm': 1, 'hostname': 'foreign-cloud--vmid4', 'vmid': 'vmid4', 'keep_alive':0, 'cloud_name': 'vm-test-cloud'}
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', form_data={'group': 'vm-test-group'},
        list='vm_list', filter={'group_name': 'vm-test-group', 'cloud_name': 'vm-test-cloud', 'vmid': 'vmid5'},
        values={'power_status': 1, 'auth_url': 'vm-test-authurl', 'manual_control': 0, 'project': 'vm-test-project', 'status': 'ACTIVE', 'retire_request_time': None, 'group_name': 'vm-test-group', 'terminate': 0, 'flavor_id': '4', 'poller_status': 'foreign', 'foreign_vm': 1, 'hostname': 'foreign-cloud--vmid5', 'vmid': 'vmid5', 'keep_alive':0, 'cloud_name': 'vm-test-cloud'}
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', form_data={'group': 'vm-test-group'},
        list='vm_list', filter={'group_name': 'vm-test-group', 'cloud_name': 'vm-test-cloud', 'vmid': 'vmid6'},
        values={'power_status': 1, 'auth_url': 'vm-test-authurl', 'manual_control': 0, 'project': 'vm-test-project', 'status': 'ACTIVE', 'retire_request_time': None, 'group_name': 'vm-test-group', 'terminate': 0, 'flavor_id': '4', 'poller_status': 'foreign', 'foreign_vm': 1, 'hostname': 'foreign-cloud--vmid6', 'vmid': 'vmid6', 'keep_alive':0, 'cloud_name': 'vm-test-cloud'}
    )

    # Setting Manual Control
    execute_csv2_request(
        gvar, 0, None, "vm update, VMs set to manual control: 0.",
        '/vm/update/', form_data={'vm_option': 'manctl', 'hostname': 'foreign-cloud--vmid4'}
    )

    execute_csv2_command(
        gvar, 0, None, 'vm update, VMs set to manual control: 0.',
        ['cloudscheduler', 'vm', 'update', '-vo', 'manctl', '-vh', 'foreign-cloud--vmid4']
    )

    execute_csv2_request(
        gvar, 0, None, "vm update, VMs set to manual control: 1.",
        '/vm/update/', form_data={'vm_option': 'manctl', 'hostname': 'vm-test-group--vm-test-cloud--vmid1'}
    )

    execute_csv2_command(
        gvar, 0, None, 'vm update, VMs set to manual control: 1.',
        ['cloudscheduler', 'vm', 'update', '-vo', 'manctl', '-vh', 'vm-test-group--vm-test-cloud--vmid2']
    )

    execute_csv2_request(
        gvar, 0, None, "vm update, VMs set to manual control: 3.",
        '/vm/update/', form_data={'vm_option': 'manctl'}
    )

    execute_csv2_command(
        gvar, 0, None, 'vm update, VMs set to manual control: 3.',
        ['cloudscheduler', 'vm', 'update', '-vo', 'manctl']
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', form_data={'group': 'vm-test-group'},
        list='vm_list', filter={'group_name': 'vm-test-group', 'cloud_name': 'vm-test-cloud', 'vmid': 'vmid1'},
        values={'power_status': 1, 'auth_url': 'vm-test-authurl', 'manual_control': 1, 'project': 'vm-test-project', 'status': 'ACTIVE', 'retire_request_time': 0, 'group_name': 'vm-test-group', 'terminate': 0, 'flavor_id': '5', 'poller_status': 'manual', 'foreign_vm': 0, 'hostname': 'vm-test-group--vm-test-cloud--vmid1', 'vmid': 'vmid1', 'keep_alive':0, 'cloud_name': 'vm-test-cloud'}
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', form_data={'group': 'vm-test-group'},
        list='vm_list', filter={'group_name': 'vm-test-group', 'cloud_name': 'vm-test-cloud', 'vmid': 'vmid2'},
        values={'power_status': 1, 'auth_url': 'vm-test-authurl', 'manual_control': 1, 'project': 'vm-test-project', 'status': 'ACTIVE', 'retire_request_time': 0, 'group_name': 'vm-test-group', 'terminate': 0, 'flavor_id': '4', 'poller_status': 'manual', 'foreign_vm': 0, 'hostname': 'vm-test-group--vm-test-cloud--vmid2', 'vmid': 'vmid2', 'keep_alive':0, 'cloud_name': 'vm-test-cloud'}
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', form_data={'group': 'vm-test-group'},
        list='vm_list', filter={'group_name': 'vm-test-group', 'cloud_name': 'vm-test-cloud', 'vmid': 'vmid3'},
        values={'power_status': 1, 'auth_url': 'vm-test-authurl', 'manual_control': 1, 'project': 'vm-test-project', 'status': 'ACTIVE', 'retire_request_time': 0, 'group_name': 'vm-test-group', 'terminate': 0, 'flavor_id': '4', 'poller_status': 'manual', 'foreign_vm': 0, 'hostname': 'vm-test-group--vm-test-cloud--vmid3', 'vmid': 'vmid3', 'keep_alive':0, 'cloud_name': 'vm-test-cloud'}
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', form_data={'group': 'vm-test-group'},
        list='vm_list', filter={'group_name': 'vm-test-group', 'cloud_name': 'vm-test-cloud', 'vmid': 'vmid4'},
        values={'power_status': 1, 'auth_url': 'vm-test-authurl', 'manual_control': 0, 'project': 'vm-test-project', 'status': 'ACTIVE', 'retire_request_time': None, 'group_name': 'vm-test-group', 'terminate': 0, 'flavor_id': '4', 'poller_status': 'foreign', 'foreign_vm': 1, 'hostname': 'foreign-cloud--vmid4', 'vmid': 'vmid4', 'keep_alive':0, 'cloud_name': 'vm-test-cloud'}
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', form_data={'group': 'vm-test-group'},
        list='vm_list', filter={'group_name': 'vm-test-group', 'cloud_name': 'vm-test-cloud', 'vmid': 'vmid5'},
        values={'power_status': 1, 'auth_url': 'vm-test-authurl', 'manual_control': 0, 'project': 'vm-test-project', 'status': 'ACTIVE', 'retire_request_time': None, 'group_name': 'vm-test-group', 'terminate': 0, 'flavor_id': '4', 'poller_status': 'foreign', 'foreign_vm': 1, 'hostname': 'foreign-cloud--vmid5', 'vmid': 'vmid5', 'keep_alive':0, 'cloud_name': 'vm-test-cloud'}
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', form_data={'group': 'vm-test-group'},
        list='vm_list', filter={'group_name': 'vm-test-group', 'cloud_name': 'vm-test-cloud', 'vmid': 'vmid6'},
        values={'power_status': 1, 'auth_url': 'vm-test-authurl', 'manual_control': 0, 'project': 'vm-test-project', 'status': 'ACTIVE', 'retire_request_time': None, 'group_name': 'vm-test-group', 'terminate': 0, 'flavor_id': '4', 'poller_status': 'foreign', 'foreign_vm': 1, 'hostname': 'foreign-cloud--vmid6', 'vmid': 'vmid6', 'keep_alive':0, 'cloud_name': 'vm-test-cloud'}
    )

    # Setting System Control
    execute_csv2_request(
        gvar, 0, None, "vm update, VMs set to system control: 0.",
        '/vm/update/', form_data={'vm_option': 'sysctl', 'hostname': 'foreign-cloud--vmid4'}
    )

    execute_csv2_command(
        gvar, 0, None, 'vm update, VMs set to system control: 0.',
        ['cloudscheduler', 'vm', 'update', '-vo', 'sysctl', '-vh', 'foreign-cloud--vmid4']
    )

    execute_csv2_request(
        gvar, 0, None, "vm update, VMs set to system control: 1.",
        '/vm/update/', form_data={'vm_option': 'sysctl', 'hostname': 'vm-test-group--vm-test-cloud--vmid2'}
    )

    execute_csv2_command(
        gvar, 0, None, 'vm update, VMs set to system control: 1.',
        ['cloudscheduler', 'vm', 'update', '-vo', 'sysctl', '-vh', 'vm-test-group--vm-test-cloud--vmid3']
    )

    execute_csv2_request(
        gvar, 0, None, "vm update, VMs set to system control: 3.",
        '/vm/update/', form_data={'vm_option': 'sysctl'}
    )

    execute_csv2_command(
        gvar, 0, None, 'vm update, VMs set to system control: 3.',
        ['cloudscheduler', 'vm', 'update', '-vo', 'sysctl']
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', form_data={'group': 'vm-test-group'},
        list='vm_list', filter={'group_name': 'vm-test-group', 'cloud_name': 'vm-test-cloud', 'vmid': 'vmid1'},
        values={'power_status': 1, 'auth_url': 'vm-test-authurl', 'manual_control': 0, 'project': 'vm-test-project', 'status': 'ACTIVE', 'retire_request_time': 0, 'group_name': 'vm-test-group', 'terminate': 0, 'flavor_id': '5', 'poller_status': 'unregistered', 'foreign_vm': 0, 'hostname': 'vm-test-group--vm-test-cloud--vmid1', 'vmid': 'vmid1', 'keep_alive':0, 'cloud_name': 'vm-test-cloud'}
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', form_data={'group': 'vm-test-group'},
        list='vm_list', filter={'group_name': 'vm-test-group', 'cloud_name': 'vm-test-cloud', 'vmid': 'vmid2'},
        values={'power_status': 1, 'auth_url': 'vm-test-authurl', 'manual_control': 0, 'project': 'vm-test-project', 'status': 'ACTIVE', 'retire_request_time': 0, 'group_name': 'vm-test-group', 'terminate': 0, 'flavor_id': '4', 'poller_status': 'unregistered', 'foreign_vm': 0, 'hostname': 'vm-test-group--vm-test-cloud--vmid2', 'vmid': 'vmid2', 'keep_alive':0, 'cloud_name': 'vm-test-cloud'}
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', form_data={'group': 'vm-test-group'},
        list='vm_list', filter={'group_name': 'vm-test-group', 'cloud_name': 'vm-test-cloud', 'vmid': 'vmid3'},
        values={'power_status': 1, 'auth_url': 'vm-test-authurl', 'manual_control': 0, 'project': 'vm-test-project', 'status': 'ACTIVE', 'retire_request_time': 0, 'group_name': 'vm-test-group', 'terminate': 0, 'flavor_id': '4', 'poller_status': 'unregistered', 'foreign_vm': 0, 'hostname': 'vm-test-group--vm-test-cloud--vmid3', 'vmid': 'vmid3', 'keep_alive':0, 'cloud_name': 'vm-test-cloud'}
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', form_data={'group': 'vm-test-group'},
        list='vm_list', filter={'group_name': 'vm-test-group', 'cloud_name': 'vm-test-cloud', 'vmid': 'vmid4'},
        values={'power_status': 1, 'auth_url': 'vm-test-authurl', 'manual_control': 0, 'project': 'vm-test-project', 'status': 'ACTIVE', 'retire_request_time': None, 'group_name': 'vm-test-group', 'terminate': 0, 'flavor_id': '4', 'poller_status': 'foreign', 'foreign_vm': 1, 'hostname': 'foreign-cloud--vmid4', 'vmid': 'vmid4', 'keep_alive':0, 'cloud_name': 'vm-test-cloud'}
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', form_data={'group': 'vm-test-group'},
        list='vm_list', filter={'group_name': 'vm-test-group', 'cloud_name': 'vm-test-cloud', 'vmid': 'vmid5'},
        values={'power_status': 1, 'auth_url': 'vm-test-authurl', 'manual_control': 0, 'project': 'vm-test-project', 'status': 'ACTIVE', 'retire_request_time': None, 'group_name': 'vm-test-group', 'terminate': 0, 'flavor_id': '4', 'poller_status': 'foreign', 'foreign_vm': 1, 'hostname': 'foreign-cloud--vmid5', 'vmid': 'vmid5', 'keep_alive':0, 'cloud_name': 'vm-test-cloud'}
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', form_data={'group': 'vm-test-group'},
        list='vm_list', filter={'group_name': 'vm-test-group', 'cloud_name': 'vm-test-cloud', 'vmid': 'vmid6'},
        values={'power_status': 1, 'auth_url': 'vm-test-authurl', 'manual_control': 0, 'project': 'vm-test-project', 'status': 'ACTIVE', 'retire_request_time': None, 'group_name': 'vm-test-group', 'terminate': 0, 'flavor_id': '4', 'poller_status': 'foreign', 'foreign_vm': 1, 'hostname': 'foreign-cloud--vmid6', 'vmid': 'vmid6', 'keep_alive':0, 'cloud_name': 'vm-test-cloud'}
    )

    # Setting Retire
    execute_csv2_request(
        gvar, 0, None, "vm update, VMs retired: 0.",
        '/vm/update/', form_data={'vm_option': 'retire', 'hostname': 'foreign-cloud--vmid4'}
    )

    execute_csv2_command(
        gvar, 0, None, 'vm update, VMs retired: 0.',
        ['cloudscheduler', 'vm', 'update', '-vo', 'retire', '-vh', 'foreign-cloud--vmid4']
    )

    execute_csv2_request(
        gvar, 0, None, "vm update, VMs retired: 1.",
        '/vm/update/', form_data={'vm_option': 'retire', 'hostname': 'vm-test-group--vm-test-cloud--vmid3'}
    )

    execute_csv2_command(
        gvar, 0, None, 'vm update, VMs retired: 1.',
        ['cloudscheduler', 'vm', 'update', '-vo', 'retire', '-vh', 'vm-test-group--vm-test-cloud--vmid1']
    )

    execute_csv2_request(
        gvar, 0, None, "vm update, VMs retired: 3.",
        '/vm/update/', form_data={'vm_option': 'retire'}
    )

    execute_csv2_command(
        gvar, 0, None, 'vm update, VMs retired: 3.',
        ['cloudscheduler', 'vm', 'update', '-vo', 'retire']
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', form_data={'group': 'vm-test-group'},
        list='vm_list', filter={'group_name': 'vm-test-group', 'cloud_name': 'vm-test-cloud', 'vmid': 'vmid4'},
        values={'power_status': 1, 'auth_url': 'vm-test-authurl', 'manual_control': 0, 'project': 'vm-test-project', 'status': 'ACTIVE', 'retire_request_time': None, 'group_name': 'vm-test-group', 'terminate': 0, 'flavor_id': '4', 'poller_status': 'foreign', 'foreign_vm': 1, 'hostname': 'foreign-cloud--vmid4', 'vmid': 'vmid4', 'keep_alive':0, 'cloud_name': 'vm-test-cloud'}
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', form_data={'group': 'vm-test-group'},
        list='vm_list', filter={'group_name': 'vm-test-group', 'cloud_name': 'vm-test-cloud', 'vmid': 'vmid5'},
        values={'power_status': 1, 'auth_url': 'vm-test-authurl', 'manual_control': 0, 'project': 'vm-test-project', 'status': 'ACTIVE', 'retire_request_time': None, 'group_name': 'vm-test-group', 'terminate': 0, 'flavor_id': '4', 'poller_status': 'foreign', 'foreign_vm': 1, 'hostname': 'foreign-cloud--vmid5', 'vmid': 'vmid5', 'keep_alive':0, 'cloud_name': 'vm-test-cloud'}
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', form_data={'group': 'vm-test-group'},
        list='vm_list', filter={'group_name': 'vm-test-group', 'cloud_name': 'vm-test-cloud', 'vmid': 'vmid6'},
        values={'power_status': 1, 'auth_url': 'vm-test-authurl', 'manual_control': 0, 'project': 'vm-test-project', 'status': 'ACTIVE', 'retire_request_time': None, 'group_name': 'vm-test-group', 'terminate': 0, 'flavor_id': '4', 'poller_status': 'foreign', 'foreign_vm': 1, 'hostname': 'foreign-cloud--vmid6', 'vmid': 'vmid6', 'keep_alive':0, 'cloud_name': 'vm-test-cloud'}
    )


    # Setting Kill
    execute_csv2_request(
        gvar, 0, None, "vm update, VMs killed: 0.",
        '/vm/update/', form_data={'vm_option': 'kill', 'hostname': 'foreign-cloud--vmid4'}
    )

    execute_csv2_command(
        gvar, 0, None, 'vm update, VMs killed: 0.',
        ['cloudscheduler', 'vm', 'update', '-vo', 'kill', '-vh', 'foreign-cloud--vmid4']
    )

    execute_csv2_request(
        gvar, 0, None, "vm update, VMs killed: 1.",
        '/vm/update/', form_data={'vm_option': 'kill', 'hostname': 'vm-test-group--vm-test-cloud--vmid1'}
    )

    execute_csv2_command(
        gvar, 0, None, 'vm update, VMs killed: 1.',
        ['cloudscheduler', 'vm', 'update', '-vo', 'kill', '-vh', 'vm-test-group--vm-test-cloud--vmid2']
    )

    execute_csv2_request(
        gvar, 0, None, "vm update, VMs killed: 3.",
        '/vm/update/', form_data={'vm_option': 'kill'}
    )

    execute_csv2_command(
        gvar, 0, None, 'vm update, VMs killed: 3.',
        ['cloudscheduler', 'vm', 'update', '-vo', 'kill']
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', form_data={'group': 'vm-test-group'},
        list='vm_list', filter={'group_name': 'vm-test-group', 'cloud_name': 'vm-test-cloud', 'vmid': 'vmid1'},
        values={'power_status': 1, 'auth_url': 'vm-test-authurl', 'manual_control': 0, 'project': 'vm-test-project', 'status': 'ACTIVE', 'group_name': 'vm-test-group', 'terminate': 1, 'flavor_id': '5', 'poller_status': 'unregistered', 'foreign_vm': 0, 'hostname': 'vm-test-group--vm-test-cloud--vmid1', 'vmid': 'vmid1', 'keep_alive':0, 'cloud_name': 'vm-test-cloud'}
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', form_data={'group': 'vm-test-group'},
        list='vm_list', filter={'group_name': 'vm-test-group', 'cloud_name': 'vm-test-cloud', 'vmid': 'vmid2'},
        values={'power_status': 1, 'auth_url': 'vm-test-authurl', 'manual_control': 0, 'project': 'vm-test-project', 'status': 'ACTIVE', 'group_name': 'vm-test-group', 'terminate': 1, 'flavor_id': '4', 'poller_status': 'unregistered', 'foreign_vm': 0, 'hostname': 'vm-test-group--vm-test-cloud--vmid2', 'vmid': 'vmid2', 'keep_alive':0, 'cloud_name': 'vm-test-cloud'}
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', form_data={'group': 'vm-test-group'},
        list='vm_list', filter={'group_name': 'vm-test-group', 'cloud_name': 'vm-test-cloud', 'vmid': 'vmid3'},
        values={'power_status': 1, 'auth_url': 'vm-test-authurl', 'manual_control': 0, 'project': 'vm-test-project', 'status': 'ACTIVE', 'group_name': 'vm-test-group', 'terminate': 1, 'flavor_id': '4', 'poller_status': 'unregistered', 'foreign_vm': 0, 'hostname': 'vm-test-group--vm-test-cloud--vmid3', 'vmid': 'vmid3', 'keep_alive':0, 'cloud_name': 'vm-test-cloud'}
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', form_data={'group': 'vm-test-group'},
        list='vm_list', filter={'group_name': 'vm-test-group', 'cloud_name': 'vm-test-cloud', 'vmid': 'vmid4'},
        values={'power_status': 1, 'auth_url': 'vm-test-authurl', 'manual_control': 0, 'project': 'vm-test-project', 'status': 'ACTIVE', 'retire_request_time': None, 'group_name': 'vm-test-group', 'terminate': 0, 'flavor_id': '4', 'poller_status': 'foreign', 'foreign_vm': 1, 'hostname': 'foreign-cloud--vmid4', 'vmid': 'vmid4', 'keep_alive':0, 'cloud_name': 'vm-test-cloud'}
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', form_data={'group': 'vm-test-group'},
        list='vm_list', filter={'group_name': 'vm-test-group', 'cloud_name': 'vm-test-cloud', 'vmid': 'vmid5'},
        values={'power_status': 1, 'auth_url': 'vm-test-authurl', 'manual_control': 0, 'project': 'vm-test-project', 'status': 'ACTIVE', 'retire_request_time': None, 'group_name': 'vm-test-group', 'terminate': 0, 'flavor_id': '4', 'poller_status': 'foreign', 'foreign_vm': 1, 'hostname': 'foreign-cloud--vmid5', 'vmid': 'vmid5', 'keep_alive':0, 'cloud_name': 'vm-test-cloud'}
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', form_data={'group': 'vm-test-group'},
        list='vm_list', filter={'group_name': 'vm-test-group', 'cloud_name': 'vm-test-cloud', 'vmid': 'vmid6'},
        values={'power_status': 1, 'auth_url': 'vm-test-authurl', 'manual_control': 0, 'project': 'vm-test-project', 'status': 'ACTIVE', 'retire_request_time': None, 'group_name': 'vm-test-group', 'terminate': 0, 'flavor_id': '4', 'poller_status': 'foreign', 'foreign_vm': 1, 'hostname': 'foreign-cloud--vmid6', 'vmid': 'vmid6', 'keep_alive':0, 'cloud_name': 'vm-test-cloud'}
    )

if __name__ == "__main__":
    main(None)
