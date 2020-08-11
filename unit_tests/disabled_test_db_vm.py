# The name of this file has been changed to prevent ./run_tests from running it.

from unit_test_common import execute_csv2_request, execute_csv2_command, initialize_csv2_request, ut_id
from sys import argv

# lno: VV - error code identifier.

def main(gvar, user_secret):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)
    # 1
    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', group=ut_id(gvar, 'dtg1'), expected_list='vm_list', list_filter={'group_name': ut_id(gvar, 'dtg1'), 'cloud_name': ut_id(gvar, 'dtc1'), 'vmid': 'vmid1'},
        values={'power_status': 1,
            'authurl': 'vm-test-authurl',
            'manual_control': 0,
            'project': 'vm-test-project',
            'status': 'ACTIVE',
            'retire_request_time': 0,
            'group_name': ut_id(gvar, 'dtg1'),
            'terminate': 0,
            'flavor_id': '5',
            'poller_status': 'unregistered',
            'foreign_vm': 0,
            'hostname': 'vm-test-group--vm-test-cloud--vmid1',
            'vmid': 'vmid1',
            'keep_alive': 0,
            'cloud_name': ut_id(gvar, 'dtc1')
        },
        server_user=ut_id(gvar, 'dtu1'), server_pw=user_secret
    )

    # 2
    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', group=ut_id(gvar, 'dtg1'), expected_list='vm_list', list_filter={'group_name': ut_id(gvar, 'dtg1'), 'cloud_name': ut_id(gvar, 'dtc1'), 'vmid': 'vmid2'},
        values={'power_status': 1,
            'authurl': 'vm-test-authurl',
            'manual_control': 0,
            'project': 'vm-test-project',
            'status': 'ACTIVE',
            'retire_request_time': 0,
            'group_name': ut_id(gvar, 'dtg1'),
            'terminate': 0,
            'flavor_id': '4',
            'poller_status': 'unregistered',
            'foreign_vm': 0,
            'hostname': 'vm-test-group--vm-test-cloud--vmid2',
            'vmid': 'vmid2',
            'keep_alive':0,
            'cloud_name': ut_id(gvar, 'dtc1')
        },
        server_user=ut_id(gvar, 'dtu1'), server_pw=user_secret
    )

    # 3
    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', group=ut_id(gvar, 'dtg1'), expected_list='vm_list', list_filter={'group_name': ut_id(gvar, 'dtg1'), 'cloud_name': ut_id(gvar, 'dtc1'), 'vmid': 'vmid3'},
        values={'power_status': 1,
            'authurl': 'vm-test-authurl',
            'manual_control': 0,
            'project': 'vm-test-project',
            'status': 'ACTIVE',
            'retire_request_time': 0,
            'group_name': ut_id(gvar, 'dtg1'),
            'terminate': 0,
            'flavor_id': '4',
            'poller_status': 'unregistered',
            'foreign_vm': 0,
            'hostname': 'vm-test-group--vm-test-cloud--vmid3',
            'vmid': 'vmid3',
            'keep_alive':0,
            'cloud_name': ut_id(gvar, 'dtc1')
        },
        server_user=ut_id(gvar, 'dtu1'), server_pw=user_secret
    )

    # 4
    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', group=ut_id(gvar, 'dtg1'), expected_list='vm_list', list_filter={'group_name': ut_id(gvar, 'dtg1'), 'cloud_name': ut_id(gvar, 'dtc1'), 'vmid': 'vmid4'},
        values={'power_status': 1,
            'authurl': 'vm-test-authurl',
            'manual_control': 0,
            'project': 'vm-test-project',
            'status': 'ACTIVE',
            'retire_request_time': None,
            'group_name': ut_id(gvar, 'dtg1'),
            'terminate': 0,
            'flavor_id': '4',
            'poller_status': 'foreign',
            'foreign_vm': 1,
            'hostname': 'foreign-cloud--vmid4',
            'vmid': 'vmid4',
            'keep_alive':0,
            'cloud_name': ut_id(gvar, 'dtc1')
        },
        server_user=ut_id(gvar, 'dtu1'), server_pw=user_secret
    )

    # 5
    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', group=ut_id(gvar, 'dtg1'), expected_list='vm_list', list_filter={'group_name': ut_id(gvar, 'dtg1'), 'cloud_name': ut_id(gvar, 'dtc1'), 'vmid': 'vmid5'},
        values={'power_status': 1,
            'authurl': 'vm-test-authurl',
            'manual_control': 0,
            'project': 'vm-test-project',
            'status': 'ACTIVE',
            'retire_request_time': None,
            'group_name': ut_id(gvar, 'dtg1'),
            'terminate': 0,
            'flavor_id': '4',
            'poller_status': 'foreign',
            'foreign_vm': 1,
            'hostname': 'foreign-cloud--vmid5',
            'vmid': 'vmid5',
            'keep_alive':0,
            'cloud_name': ut_id(gvar, 'dtc1')
        },
        server_user=ut_id(gvar, 'dtu1'), server_pw=user_secret
    )

    # 6
    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', group=ut_id(gvar, 'dtg1'), expected_list='vm_list', list_filter={'group_name': ut_id(gvar, 'dtg1'), 'cloud_name': ut_id(gvar, 'dtc1'), 'vmid': 'vmid6'},
        values={'power_status': 1,
            'authurl': 'vm-test-authurl',
            'manual_control': 0,
            'project': 'vm-test-project',
            'status': 'ACTIVE',
            'retire_request_time': None,
            'group_name': ut_id(gvar, 'dtg1'),
            'terminate': 0,
            'flavor_id': '4',
            'poller_status': 'foreign',
            'foreign_vm': 1,
            'hostname': 'foreign-cloud--vmid6',
            'vmid': 'vmid6',
            'keep_alive':0,
            'cloud_name': ut_id(gvar, 'dtc1')
        },
        server_user=ut_id(gvar, 'dtu1'), server_pw=user_secret
    )

    # 7
    # Setting Manual Control
    execute_csv2_request(
        gvar, 0, None, "vm update, VMs set to manual control: 0.",
        '/vm/update/', group=ut_id(gvar, 'dtg1'),
        form_data={'vm_option': 'manctl', 'hostname': 'foreign-cloud--vmid4'}
    )

    # 8
    execute_csv2_command(
        gvar, 0, None, 'vm update, VMs set to manual control: 0.',
        ['cloudscheduler', 'vm', 'update', '-vo', 'manctl', '-vh', 'foreign-cloud--vmid4']
    )

    # 9
    execute_csv2_request(
        gvar, 0, None, "vm update, VMs set to manual control: 1.",
        '/vm/update/', group=ut_id(gvar, 'dtg1'), form_data={'vm_option': 'manctl', 'hostname': 'vm-test-group--vm-test-cloud--vmid1'}
    )

    # 10
    execute_csv2_command(
        gvar, 0, None, 'vm update, VMs set to manual control: 1.',
        ['cloudscheduler', 'vm', 'update', '-vo', 'manctl', '-vh', 'vm-test-group--vm-test-cloud--vmid2']
    )

    # 11
    execute_csv2_request(
        gvar, 0, None, "vm update, VMs set to manual control: 3.",
        '/vm/update/', group=ut_id(gvar, 'dtg1'), form_data={'vm_option': 'manctl'}
    )

    # 12
    execute_csv2_command(
        gvar, 0, None, 'vm update, VMs set to manual control: 3.',
        ['cloudscheduler', 'vm', 'update', '-vo', 'manctl']
    )

    # 13
    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', group=ut_id(gvar, 'dtg1'), expected_list='vm_list', list_filter={'group_name': ut_id(gvar, 'dtg1'), 'cloud_name': ut_id(gvar, 'dtc1'), 'vmid': 'vmid1'},
        values={'power_status': 1,
            'authurl': 'vm-test-authurl',
            'manual_control': 1,
            'project': 'vm-test-project',
            'status': 'ACTIVE',
            'retire_request_time': 0,
            'group_name': ut_id(gvar, 'dtg1'),
            'terminate': 0,
            'flavor_id': '5',
            'poller_status': 'manual',
            'foreign_vm': 0,
            'hostname': 'vm-test-group--vm-test-cloud--vmid1',
            'vmid': 'vmid1',
            'keep_alive':0,
            'cloud_name': ut_id(gvar, 'dtc1')
        },
        server_user=ut_id(gvar, 'dtu1'), server_pw=user_secret
    )

    # 14
    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', group=ut_id(gvar, 'dtg1'), expected_list='vm_list', list_filter={'group_name': ut_id(gvar, 'dtg1'), 'cloud_name': ut_id(gvar, 'dtc1'), 'vmid': 'vmid2'},
        values={'power_status': 1,
            'authurl': 'vm-test-authurl',
            'manual_control': 1,
            'project': 'vm-test-project',
            'status': 'ACTIVE',
            'retire_request_time': 0,
            'group_name': ut_id(gvar, 'dtg1'),
            'terminate': 0,
            'flavor_id': '4',
            'poller_status': 'manual',
            'foreign_vm': 0,
            'hostname': 'vm-test-group--vm-test-cloud--vmid2',
            'vmid': 'vmid2',
            'keep_alive':0,
            'cloud_name': ut_id(gvar, 'dtc1')
        },
        server_user=ut_id(gvar, 'dtu1'), server_pw=user_secret
    )

    # 15
    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', group=ut_id(gvar, 'dtg1'), expected_list='vm_list', list_filter={'group_name': ut_id(gvar, 'dtg1'), 'cloud_name': ut_id(gvar, 'dtc1'), 'vmid': 'vmid3'},
        values={'power_status': 1,
            'authurl': 'vm-test-authurl',
            'manual_control': 1,
            'project': 'vm-test-project',
            'status': 'ACTIVE',
            'retire_request_time': 0,
            'group_name': ut_id(gvar, 'dtg1'),
            'terminate': 0,
            'flavor_id': '4',
            'poller_status': 'manual',
            'foreign_vm': 0,
            'hostname': 'vm-test-group--vm-test-cloud--vmid3',
            'vmid': 'vmid3',
            'keep_alive':0,
            'cloud_name': ut_id(gvar, 'dtc1')
        },
        server_user=ut_id(gvar, 'dtu1'), server_pw=user_secret
    )

    # 16
    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', group=ut_id(gvar, 'dtg1'), expected_list='vm_list', list_filter={'group_name': ut_id(gvar, 'dtg1'), 'cloud_name': ut_id(gvar, 'dtc1'), 'vmid': 'vmid4'},
        values={'power_status': 1,
            'authurl': 'vm-test-authurl',
            'manual_control': 0,
            'project': 'vm-test-project',
            'status': 'ACTIVE',
            'retire_request_time': None,
            'group_name': ut_id(gvar, 'dtg1'),
            'terminate': 0,
            'flavor_id': '4',
            'poller_status': 'foreign',
            'foreign_vm': 1,
            'hostname': 'foreign-cloud--vmid4',
            'vmid': 'vmid4',
            'keep_alive':0,
            'cloud_name': ut_id(gvar, 'dtc1')
        },
        server_user=ut_id(gvar, 'dtu1'), server_pw=user_secret
    )

    # 17
    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', group=ut_id(gvar, 'dtg1'), expected_list='vm_list', list_filter={'group_name': ut_id(gvar, 'dtg1'), 'cloud_name': ut_id(gvar, 'dtc1'), 'vmid': 'vmid5'},
        values={'power_status': 1,
            'authurl': 'vm-test-authurl',
            'manual_control': 0,
            'project': 'vm-test-project',
            'status': 'ACTIVE',
            'retire_request_time': None,
            'group_name': ut_id(gvar, 'dtg1'),
            'terminate': 0,
            'flavor_id': '4',
            'poller_status': 'foreign',
            'foreign_vm': 1,
            'hostname': 'foreign-cloud--vmid5',
            'vmid': 'vmid5',
            'keep_alive':0,
            'cloud_name': ut_id(gvar, 'dtc1')
        },
        server_user=ut_id(gvar, 'dtu1'), server_pw=user_secret
    )

    # 18
    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', group=ut_id(gvar, 'dtg1'), expected_list='vm_list', list_filter={'group_name': ut_id(gvar, 'dtg1'), 'cloud_name': ut_id(gvar, 'dtc1'), 'vmid': 'vmid6'},
        values={'power_status': 1,
            'authurl': 'vm-test-authurl',
            'manual_control': 0,
            'project': 'vm-test-project',
            'status': 'ACTIVE',
            'retire_request_time': None,
            'group_name': ut_id(gvar, 'dtg1'),
            'terminate': 0,
            'flavor_id': '4',
            'poller_status': 'foreign',
            'foreign_vm': 1,
            'hostname': 'foreign-cloud--vmid6',
            'vmid': 'vmid6',
            'keep_alive':0,
            'cloud_name': ut_id(gvar, 'dtc1')
        },
        server_user=ut_id(gvar, 'dtu1'), server_pw=user_secret
    )

    # 19
    # Setting System Control
    execute_csv2_request(
        gvar, 0, None, "vm update, VMs set to system control: 0.",
        '/vm/update/', group=(ut_id(gvar, 'dtg1')), form_data={'vm_option': 'sysctl', 'hostname': 'foreign-cloud--vmid4'}
    )

    # 20
    execute_csv2_command(
        gvar, 0, None, 'vm update, VMs set to system control: 0.',
        ['cloudscheduler', 'vm', 'update', '-vo', 'sysctl', '-vh', 'foreign-cloud--vmid4']
    )

    # 21
    execute_csv2_request(
        gvar, 0, None, "vm update, VMs set to system control: 1.",
        '/vm/update/', group=(ut_id(gvar, 'dtg1')), form_data={'vm_option': 'sysctl', 'hostname': 'vm-test-group--vm-test-cloud--vmid2'}
    )

    # 22
    execute_csv2_command(
        gvar, 0, None, 'vm update, VMs set to system control: 1.',
        ['cloudscheduler', 'vm', 'update', '-vo', 'sysctl', '-vh', 'vm-test-group--vm-test-cloud--vmid3']
    )

    # 23
    execute_csv2_request(
        gvar, 0, None, "vm update, VMs set to system control: 3.",
        '/vm/update/', group=(ut_id(gvar, 'dtg1')), form_data={'vm_option': 'sysctl'}
    )

    # 24
    execute_csv2_command(
        gvar, 0, None, 'vm update, VMs set to system control: 3.',
        ['cloudscheduler', 'vm', 'update', '-vo', 'sysctl']
    )

    # 25
    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', group=ut_id(gvar, 'dtg1'), expected_list='vm_list', list_filter={'group_name': ut_id(gvar, 'dtg1'), 'cloud_name': ut_id(gvar, 'dtc1'), 'vmid': 'vmid1'},
        values={'power_status': 1,
            'authurl': 'vm-test-authurl',
            'manual_control': 0,
            'project': 'vm-test-project',
            'status': 'ACTIVE',
            'retire_request_time': 0,
            'group_name': ut_id(gvar, 'dtg1'),
            'terminate': 0,
            'flavor_id': '5',
            'poller_status': 'unregistered',
            'foreign_vm': 0,
            'hostname': 'vm-test-group--vm-test-cloud--vmid1',
            'vmid': 'vmid1',
            'keep_alive':0,
            'cloud_name': ut_id(gvar, 'dtc1')
        },
        server_user=ut_id(gvar, 'dtu1'), server_pw=user_secret
    )

    # 26
    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', group=ut_id(gvar, 'dtg1'), expected_list='vm_list', list_filter={'group_name': ut_id(gvar, 'dtg1'), 'cloud_name': ut_id(gvar, 'dtc1'), 'vmid': 'vmid2'},
        values={'power_status': 1,
            'authurl': 'vm-test-authurl',
            'manual_control': 0,
            'project': 'vm-test-project',
            'status': 'ACTIVE',
            'retire_request_time': 0,
            'group_name': ut_id(gvar, 'dtg1'),
            'terminate': 0,
            'flavor_id': '4',
            'poller_status': 'unregistered',
            'foreign_vm': 0,
            'hostname': 'vm-test-group--vm-test-cloud--vmid2',
            'vmid': 'vmid2',
            'keep_alive':0,
            'cloud_name': ut_id(gvar, 'dtc1')
        },
        server_user=ut_id(gvar, 'dtu1'), server_pw=user_secret
    )

    # 27
    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', group=ut_id(gvar, 'dtg1'), expected_list='vm_list', list_filter={'group_name': ut_id(gvar, 'dtg1'), 'cloud_name': ut_id(gvar, 'dtc1'), 'vmid': 'vmid3'},
        values={'power_status': 1,
            'authurl': 'vm-test-authurl',
            'manual_control': 0,
            'project': 'vm-test-project',
            'status': 'ACTIVE',
            'retire_request_time': 0,
            'group_name': ut_id(gvar, 'dtg1'),
            'terminate': 0,
            'flavor_id': '4',
            'poller_status': 'unregistered',
            'foreign_vm': 0,
            'hostname': 'vm-test-group--vm-test-cloud--vmid3',
            'vmid': 'vmid3',
            'keep_alive':0,
            'cloud_name': ut_id(gvar, 'dtc1')
        },
        server_user=ut_id(gvar, 'dtu1'), server_pw=user_secret
    )

    # 28
    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', group=ut_id(gvar, 'dtg1'), expected_list='vm_list', list_filter={'group_name': ut_id(gvar, 'dtg1'), 'cloud_name': ut_id(gvar, 'dtc1'), 'vmid': 'vmid4'},
        values={'power_status': 1,
            'authurl': 'vm-test-authurl',
            'manual_control': 0,
            'project': 'vm-test-project',
            'status': 'ACTIVE',
            'retire_request_time': None,
            'group_name': ut_id(gvar, 'dtg1'),
            'terminate': 0,
            'flavor_id': '4',
            'poller_status': 'foreign',
            'foreign_vm': 1,
            'hostname': 'foreign-cloud--vmid4',
            'vmid': 'vmid4',
            'keep_alive':0,
            'cloud_name': ut_id(gvar, 'dtc1')
        },
        server_user=ut_id(gvar, 'dtu1'), server_pw=user_secret
    )

    # 29
    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', group=ut_id(gvar, 'dtg1'), expected_list='vm_list', list_filter={'group_name': ut_id(gvar, 'dtg1'), 'cloud_name': ut_id(gvar, 'dtc1'), 'vmid': 'vmid5'},
        values={'power_status': 1,
            'authurl': 'vm-test-authurl',
            'manual_control': 0,
            'project': 'vm-test-project',
            'status': 'ACTIVE',
            'retire_request_time': None,
            'group_name': ut_id(gvar, 'dtg1'),
            'terminate': 0,
            'flavor_id': '4',
            'poller_status': 'foreign',
            'foreign_vm': 1,
            'hostname': 'foreign-cloud--vmid5',
            'vmid': 'vmid5',
            'keep_alive':0,
            'cloud_name': ut_id(gvar, 'dtc1')
        },
        server_user=ut_id(gvar, 'dtu1'), server_pw=user_secret
    )

    # 30
    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', group=ut_id(gvar, 'dtg1'), expected_list='vm_list', list_filter={'group_name': ut_id(gvar, 'dtg1'), 'cloud_name': ut_id(gvar, 'dtc1'), 'vmid': 'vmid6'},
        values={'power_status': 1,
            'authurl': 'vm-test-authurl',
            'manual_control': 0,
            'project': 'vm-test-project',
            'status': 'ACTIVE',
            'retire_request_time': None,
            'group_name': ut_id(gvar, 'dtg1'),
            'terminate': 0,
            'flavor_id': '4',
            'poller_status': 'foreign',
            'foreign_vm': 1,
            'hostname': 'foreign-cloud--vmid6',
            'vmid': 'vmid6',
            'keep_alive':0,
            'cloud_name': ut_id(gvar, 'dtc1')
        },
        server_user=ut_id(gvar, 'dtu1'), server_pw=user_secret
    )

    # 31
    # Setting Retire
    execute_csv2_request(
        gvar, 0, None, "vm update, VMs retired: 0.",
        '/vm/update/', group=(ut_id(gvar, 'dtg1')), form_data={'vm_option': 'retire', 'hostname': 'foreign-cloud--vmid4'}
    )

    # 32
    execute_csv2_command(
        gvar, 0, None, 'vm update, VMs retired: 0.',
        ['cloudscheduler', 'vm', 'update', '-vo', 'retire', '-vh', 'foreign-cloud--vmid4']
    )

    # 33
    execute_csv2_request(
        gvar, 0, None, "vm update, VMs retired: 1.",
        '/vm/update/', group=(ut_id(gvar, 'dtg1')), form_data={'vm_option': 'retire', 'hostname': 'vm-test-group--vm-test-cloud--vmid3'}
    )

    # 34
    execute_csv2_command(
        gvar, 0, None, 'vm update, VMs retired: 1.',
        ['cloudscheduler', 'vm', 'update', '-vo', 'retire', '-vh', 'vm-test-group--vm-test-cloud--vmid1']
    )

    # 35
    execute_csv2_request(
        gvar, 0, None, "vm update, VMs retired: 3.",
        '/vm/update/', group=(ut_id(gvar, 'dtg1')), form_data={'vm_option': 'retire'}
    )

    # 36
    execute_csv2_command(
        gvar, 0, None, 'vm update, VMs retired: 3.',
        ['cloudscheduler', 'vm', 'update', '-vo', 'retire']
    )

    # 37
    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', group=ut_id(gvar, 'dtg1'), expected_list='vm_list', list_filter={'group_name': ut_id(gvar, 'dtg1'), 'cloud_name': ut_id(gvar, 'dtc1'), 'vmid': 'vmid4'},
        values={'power_status': 1,
            'authurl': 'vm-test-authurl',
            'manual_control': 0,
            'project': 'vm-test-project',
            'status': 'ACTIVE',
            'retire_request_time': None,
            'group_name': ut_id(gvar, 'dtg1'),
            'terminate': 0,
            'flavor_id': '4',
            'poller_status': 'foreign',
            'foreign_vm': 1,
            'hostname': 'foreign-cloud--vmid4',
            'vmid': 'vmid4',
            'keep_alive':0,
            'cloud_name': ut_id(gvar, 'dtc1')
        },
        server_user=ut_id(gvar, 'dtu1'), server_pw=user_secret
    )

    # 38
    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', group=ut_id(gvar, 'dtg1'), expected_list='vm_list', list_filter={'group_name': ut_id(gvar, 'dtg1'), 'cloud_name': ut_id(gvar, 'dtc1'), 'vmid': 'vmid5'},
        values={'power_status': 1,
            'authurl': 'vm-test-authurl',
            'manual_control': 0,
            'project': 'vm-test-project',
            'status': 'ACTIVE',
            'retire_request_time': None,
            'group_name': ut_id(gvar, 'dtg1'),
            'terminate': 0,
            'flavor_id': '4',
            'poller_status': 'foreign',
            'foreign_vm': 1,
            'hostname': 'foreign-cloud--vmid5',
            'vmid': 'vmid5',
            'keep_alive':0,
            'cloud_name': ut_id(gvar, 'dtc1')
        },
        server_user=ut_id(gvar, 'dtu1'), server_pw=user_secret
    )

    # 39
    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', group=ut_id(gvar, 'dtg1'), expected_list='vm_list', list_filter={'group_name': ut_id(gvar, 'dtg1'), 'cloud_name': ut_id(gvar, 'dtc1'), 'vmid': 'vmid6'},
        values={'power_status': 1,
            'authurl': 'vm-test-authurl',
            'manual_control': 0,
            'project': 'vm-test-project',
            'status': 'ACTIVE',
            'retire_request_time': None,
            'group_name': ut_id(gvar, 'dtg1'),
            'terminate': 0,
            'flavor_id': '4',
            'poller_status': 'foreign',
            'foreign_vm': 1,
            'hostname': 'foreign-cloud--vmid6',
            'vmid': 'vmid6',
            'keep_alive':0,
            'cloud_name': ut_id(gvar, 'dtc1')
        },
        server_user=ut_id(gvar, 'dtu1'), server_pw=user_secret
    )

    # 40
    # Setting Kill
    execute_csv2_request(
        gvar, 0, None, "vm update, VMs killed: 0.",
        '/vm/update/', group=(ut_id(gvar, 'dtg1')), form_data={'vm_option': 'kill', 'hostname': 'foreign-cloud--vmid4'}
    )

    # 41
    execute_csv2_command(
        gvar, 0, None, 'vm update, VMs killed: 0.',
        ['cloudscheduler', 'vm', 'update', '-vo', 'kill', '-vh', 'foreign-cloud--vmid4']
    )

    # 42
    execute_csv2_request(
        gvar, 0, None, "vm update, VMs killed: 1.",
        '/vm/update/', group=(ut_id(gvar, 'dtg1')), form_data={'vm_option': 'kill', 'hostname': 'vm-test-group--vm-test-cloud--vmid1'}
    )

    # 43
    execute_csv2_command(
        gvar, 0, None, 'vm update, VMs killed: 1.',
        ['cloudscheduler', 'vm', 'update', '-vo', 'kill', '-vh', 'vm-test-group--vm-test-cloud--vmid2']
    )

    # 44
    execute_csv2_request(
        gvar, 0, None, "vm update, VMs killed: 3.",
        '/vm/update/', group=(ut_id(gvar, 'dtg1')), form_data={'vm_option': 'kill'}
    )

    # 45
    execute_csv2_command(
        gvar, 0, None, 'vm update, VMs killed: 3.',
        ['cloudscheduler', 'vm', 'update', '-vo', 'kill']
    )

    # 46
    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', group=ut_id(gvar, 'dtg1'), expected_list='vm_list', list_filter={'group_name': ut_id(gvar, 'dtg1'), 'cloud_name': ut_id(gvar, 'dtc1'), 'vmid': 'vmid1'},
        values={'power_status': 1,
            'authurl': 'vm-test-authurl',
            'manual_control': 0,
            'project': 'vm-test-project',
            'status': 'ACTIVE',
            'group_name': ut_id(gvar, 'dtg1'),
            'terminate': 1,
            'flavor_id': '5',
            'poller_status': 'unregistered',
            'foreign_vm': 0,
            'hostname': 'vm-test-group--vm-test-cloud--vmid1',
            'vmid': 'vmid1',
            'keep_alive':0,
            'cloud_name': ut_id(gvar, 'dtc1')
        },
        server_user=ut_id(gvar, 'dtu1'), server_pw=user_secret
    )

    # 47
    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', group=ut_id(gvar, 'dtg1'), expected_list='vm_list', list_filter={'group_name': ut_id(gvar, 'dtg1'), 'cloud_name': ut_id(gvar, 'dtc1'), 'vmid': 'vmid2'},
        values={'power_status': 1,
            'authurl': 'vm-test-authurl',
            'manual_control': 0,
            'project': 'vm-test-project',
            'status': 'ACTIVE',
            'group_name': ut_id(gvar, 'dtg1'),
            'terminate': 1,
            'flavor_id': '4',
            'poller_status': 'unregistered',
            'foreign_vm': 0,
            'hostname': 'vm-test-group--vm-test-cloud--vmid2',
            'vmid': 'vmid2',
            'keep_alive':0,
            'cloud_name': ut_id(gvar, 'dtc1')
        },
        server_user=ut_id(gvar, 'dtu1'), server_pw=user_secret
    )

    # 48
    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', group=ut_id(gvar, 'dtg1'), expected_list='vm_list', list_filter={'group_name': ut_id(gvar, 'dtg1'), 'cloud_name': ut_id(gvar, 'dtc1'), 'vmid': 'vmid3'},
        values={'power_status': 1,
            'authurl': 'vm-test-authurl',
            'manual_control': 0,
            'project': 'vm-test-project',
            'status': 'ACTIVE',
            'group_name': ut_id(gvar, 'dtg1'),
            'terminate': 1,
            'flavor_id': '4',
            'poller_status': 'unregistered',
            'foreign_vm': 0,
            'hostname': 'vm-test-group--vm-test-cloud--vmid3',
            'vmid': 'vmid3',
            'keep_alive':0,
            'cloud_name': ut_id(gvar, 'dtc1')
        },
        server_user=ut_id(gvar, 'dtu1'), server_pw=user_secret
    )

    # 49
    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', group=ut_id(gvar, 'dtg1'), expected_list='vm_list', list_filter={'group_name': ut_id(gvar, 'dtg1'), 'cloud_name': ut_id(gvar, 'dtc1'), 'vmid': 'vmid4'},
        values={'power_status': 1,
            'authurl': 'vm-test-authurl',
            'manual_control': 0,
            'project': 'vm-test-project',
            'status': 'ACTIVE',
            'retire_request_time': None,
            'group_name': ut_id(gvar, 'dtg1'),
            'terminate': 0,
            'flavor_id': '4',
            'poller_status': 'foreign',
            'foreign_vm': 1,
            'hostname': 'foreign-cloud--vmid4',
            'vmid': 'vmid4',
            'keep_alive':0,
            'cloud_name': ut_id(gvar, 'dtc1')
        },
        server_user=ut_id(gvar, 'dtu1'), server_pw=user_secret
    )

    # 50
    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', group=ut_id(gvar, 'dtg1'), expected_list='vm_list', list_filter={'group_name': ut_id(gvar, 'dtg1'), 'cloud_name': ut_id(gvar, 'dtc1'), 'vmid': 'vmid5'},
        values={'power_status': 1,
            'authurl': 'vm-test-authurl',
            'manual_control': 0,
            'project': 'vm-test-project',
            'status': 'ACTIVE',
            'retire_request_time': None,
            'group_name': ut_id(gvar, 'dtg1'),
            'terminate': 0,
            'flavor_id': '4',
            'poller_status': 'foreign',
            'foreign_vm': 1,
            'hostname': 'foreign-cloud--vmid5',
            'vmid': 'vmid5',
            'keep_alive':0,
            'cloud_name': ut_id(gvar, 'dtc1')
        },
        server_user=ut_id(gvar, 'dtu1'), server_pw=user_secret
    )

    # 51
    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/list/', group=ut_id(gvar, 'dtg1'), expected_list='vm_list', list_filter={'group_name': ut_id(gvar, 'dtg1'), 'cloud_name': ut_id(gvar, 'dtc1'), 'vmid': 'vmid6'},
        values={'power_status': 1,
            'authurl': 'vm-test-authurl',
            'manual_control': 0,
            'project': 'vm-test-project',
            'status': 'ACTIVE',
            'retire_request_time': None,
            'group_name': ut_id(gvar, 'dtg1'),
            'terminate': 0,
            'flavor_id': '4',
            'poller_status': 'foreign',
            'foreign_vm': 1,
            'hostname': 'foreign-cloud--vmid6',
            'vmid': 'vmid6',
            'keep_alive':0,
            'cloud_name': ut_id(gvar, 'dtc1')
        },
        server_user=ut_id(gvar, 'dtu1'), server_pw=user_secret
    )

if __name__ == "__main__":
    main(None)
