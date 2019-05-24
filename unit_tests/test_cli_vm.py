from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id
from sys import argv

# lno: VV - error code identifier.

def main(gvar, user_secret):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv2_request(gvar, argv[0])

    # 1
    execute_csv2_command(
        gvar, 1, None, 'No action specified for object "vm"',
        ['cloudscheduler', 'vm', '-s', 'unit-test-un']
    )

    # 2
    execute_csv2_command(
        gvar, 1, None, 'Invalid action "invalid-unit-test" for object "vm"',
        ['cloudscheduler', 'vm', 'invalid-unit-test']
    )

    # 3
    execute_csv2_command(
        gvar, 1, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'vm', '-s', 'invalid-unit-test']
    )

    # 4
    execute_csv2_command(
        gvar, 1, None, 'No action specified for object "vm"; use -h or -H for help.',
        ['cloudscheduler', 'vm', '-s', 'unit-test-un']
    )

    # 5
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler vm".',
        ['cloudscheduler', 'vm', '-h']
    )

    # 6
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'vm', '-H']
    )

    #### LIST ####
    # 7
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'vm', 'list', '-xx', 'yy']
    )
    
    # 8
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: vm-option',
        ['cloudscheduler', 'vm', 'list', '-vo', 'invalid-unit-test']
    )

    # 9
    execute_csv2_command(
        gvar, 1, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'vm', 'list', '-s', 'invalid-unit-test']
    )

    # 10
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'vm', 'list', '-s', 'unit-test']
    )

    # 11
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'vm', 'list', '-s', 'unit-test-un']
    )

    # 12
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler vm list".',
        ['cloudscheduler', 'vm', 'list', '-h']
    )

    # 13
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'vm', 'list', '-H']
    )

    # 14
    execute_csv2_command(
        gvar, 0, None, 'Expose API requested',
        ['cloudscheduler', 'vm', 'list', '-xA']
    )

    # 15
    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'vm', 'list', '-g', 'invalid-unit-test']
    )

    # 16
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test-un, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'test'), ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'vm', 'list', '-g', ut_id(gvar, 'clg1')]
    )

    # 17
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'vm', 'list', '-ok'],
        list='VMs', columns=['Group', 'Cloud', 'Hostname']
    )

    # 18
    execute_csv2_command(
        gvar, 0, None, 'vm list, 1. VMs: keys=group_name,cloud_name,hostname, columns=vmid,vm_ips,vm_floating_ips,auth_url,project,status,flavor_id,task,power_status,start_time,htcondor_partitionable_slots,htcondor_dynamic_slots,htcondor_slots_timestamp,retire,terminate,last_updated,flavor_name,condor_slots,foreign_vm,cores,disk,ram,swap,poller_status,age,manual_control',
        ['cloudscheduler', 'vm', 'list', '-VC']
    )

    # 19
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'vm', 'list', '-NV'],
        list='VMs', columns=[
            'HTCondor',
            'Group',
            'Cloud',
            'Hostname',
            'VMID',
            'IPs',
            'Floating',
            'IPs',
            'Authorization',
            'URL',
            'Project',
            'Status',
            'Flavor',
            'ID',
            'Task',
            'Power',
            'Status',
            'Start',
            'Time',
            'Primary',
            'Slots',
            'Dynamic',
            'Slots',
            'Slots',
            'Timestamp',
            'Retire',
            'Terminate',
            'Last',
            'Updated',
            'Flavor',
            'Condor',
            'Slots',
            'Foreign',
            'cores',
            'Group',
            'Cloud',
            'Hostname',
            'Disk',
            '(GBs)',
            'Ram',
            '(MBs)',
            'Swap',
            '(GBs)',
            'Poller',
            'Status',
            'State',
            'Age',
            'Manual_Control'
            ]
    )

    # 20
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'vm', 'list', '-V', 'project,task'],
        list='VMs', columns=['Group', 'Cloud', 'Hostname', 'Project', 'Task']
    )

    # 21
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'vm', 'list'],
        list='VMs', columns=['Group', 'Cloud', 'Hostname', 'Project', 'Task']
    )

    # 22
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'vm', 'list', '-V', ''],
        list='VMs', columns=[
            'HTCondor',
            'Group',
            'Cloud',
            'Hostname',
            'VMID',
            'IPs',
            'Floating',
            'IPs',
            'Authorization',
            'URL',
            'Project',
            'Status',
            'Flavor',
            'ID',
            'Task',
            'Power',
            'Status',
            'Start',
            'Time',
            'Primary',
            'Slots',
            'Dynamic',
            'Slots',
            'Slots',
            'Timestamp',
            'Retire',
            'Terminate',
            'Last',
            'Updated',
            'Flavor',
            'Condor',
            'Slots',
            'Foreign',
            'cores',
            'Group',
            'Cloud',
            'Hostname',
            'Disk',
            '(GBs)',
            'Ram',
            '(MBs)',
            'Swap',
            '(GBs)',
            'Poller',
            'Status',
            'State',
            'Age',
            'Manual_Control'
            ]
    )

    # 23
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'vm', 'list', '-r'],
        list='VMs', columns=['Key', 'Value']
    )

    # 24
    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'vm', 'list', '-cn', 'invalid-unit-test']
    )

    # 25
    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'vm', 'list', '-vc', 'invalid-unit-test']
    )

    # 26
    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'vm', 'list', '-vd', 'invalid-unit-test']
    )

    # 27
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-ved\', \'invalid-unit-test\']',
        ['cloudscheduler', 'vm', 'list', '-ved', 'invalid-unit-test']
    )

    # 28
    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'vm', 'list', '-vF', 'invalid-unit-test']
    )

    # 29
    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'vm', 'list', '-vf', 'invalid-unit-test']
    )

    # 30
    execute_csv2_command(
        gvar, 1, None, 'Error: The following command line arguments were invalid: vm-keyname',
        ['cloudscheduler', 'vm', 'list', '-vk', 'invalid-unit-test']
    )

    # 31
    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'vm', 'list', '-vr', 'invalid-unit-test']
    )

    # 32
    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'vm', 'list', '-vS', 'invalid-unit-test']
    )

    # 33
    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'vm', 'list', '-vs', 'invalid-unit-test']
    )

    # 34
    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'vm', 'list', '-vS', 'invalid-unit-test']
    )

    # 35
    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'vm', 'list', '-vs', 'invalid-unit-test']
    )

    #### UPDATE ####

if __name__ == "__main__":
    main(None)

