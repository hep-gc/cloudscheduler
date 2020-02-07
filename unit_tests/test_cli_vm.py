from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id
from sys import argv

# lno: VV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv2_request(gvar, argv[0])

    # 01
    execute_csv2_command(
        gvar, 1, None, 'No action specified for object "vm"',
        ['cloudscheduler', 'vm', '-su', ut_id(gvar, 'clu4')]
    )

    # 02
    execute_csv2_command(
        gvar, 1, None, 'Invalid action "invalid-unit-test" for object "vm"',
        ['cloudscheduler', 'vm', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 03
    execute_csv2_command(
        gvar, None, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'vm', '-s', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')], timeout=8
    )

    # 04
    execute_csv2_command(
        gvar, 1, None, 'No action specified for object "vm"; use -h or -H for help.',
        ['cloudscheduler', 'vm', '-su', ut_id(gvar, 'clu4')]
    )

    # 05
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler vm".',
        ['cloudscheduler', 'vm', '-h', '-su', ut_id(gvar, 'clu4')]
    )

    # 06
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'vm', '-H', '-su', ut_id(gvar, 'clu4')]
    )

    #### LIST ####
    # 07
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'vm', 'list', '-xx', 'yy', '-su', ut_id(gvar, 'clu4')]
    )
    
    # 08
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: vm-option',
        ['cloudscheduler', 'vm', 'list', '-vo', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 09
    execute_csv2_command(
        gvar, None, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'vm', 'list', '-s', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')], timeout=8
    )

    # 10
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}'.format(ut_id(gvar, 'clu4'), ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'vm', 'list', '-g', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu4')]
    )

    # 11
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'vm', 'list', '-su', ut_id(gvar, 'clu4')]
    )

    # 12
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler vm list".',
        ['cloudscheduler', 'vm', 'list', '-h', '-su', ut_id(gvar, 'clu4')]
    )

    # 13
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'vm', 'list', '-H', '-su', ut_id(gvar, 'clu4')]
    )

    # 14
    execute_csv2_command(
        gvar, 0, None, 'Expose API requested',
        ['cloudscheduler', 'vm', 'list', '-xA', '-su', ut_id(gvar, 'clu4')]
    )

    # 15
    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'vm', 'list', '-g', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 16
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'vm', 'list', '-ok', '-su', ut_id(gvar, 'clu4')],
        expected_list='VMs', columns=['Group', 'Cloud', 'Hostname']
    )

    # 17
    execute_csv2_command(
        gvar, 0, None, 'vm list, 1. VMs: keys=group_name,cloud_name,hostname, columns=vmid,vm_ips,vm_floating_ips,auth_url,project,status,flavor_id,task,power_status,start_time,htcondor_startd_errors,htcondor_startd_time,htcondor_partitionable_slots,htcondor_dynamic_slots,htcondor_slots_timestamp,retire,terminate,last_updated,flavor_name,condor_slots,foreign_vm,cores,disk,ram,swap,poller_status,age,manual_control',
        ['cloudscheduler', 'vm', 'list', '-VC', '-su', ut_id(gvar, 'clu4')]
    )

    # 18
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'vm', 'list', '-NV', '-su', ut_id(gvar, 'clu4')],
        expected_list='VMs', columns=['Group', 'Terminate', 'STARTD Errors', 'Last Updated', 'Manual_Control', 'Swap (GBs)', 'Condor Slots', 'Start Time', 'Hostname', 'Power Status', 'IPs', 'Authorization URL', 'Foreign', 'Cloud', 'cores', 'Floating IPs', 'Flavor ID', 'Project', 'Flavor', 'STARTD Time', 'Dynamic Slots', 'Slots Timestamp', 'Primary Slots', 'State Age', 'Ram (MBs)', 'Disk (GBs)', 'HTCondor', 'VMID', 'Poller Status', 'Retire', 'Status', 'Task']
    )

    # 19
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'vm', 'list', '-V', 'project,task', '-su', ut_id(gvar, 'clu4')],
        expected_list='VMs', columns=['Group', 'Cloud', 'Hostname', 'Project', 'Task']
    )

    # 20
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'vm', 'list', '-su', ut_id(gvar, 'clu4')],
        expected_list='VMs', columns=['Group', 'Cloud', 'Hostname', 'Project', 'Task']
    )

    # 21
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'vm', 'list', '-V', '', '-su', ut_id(gvar, 'clu4')],
        expected_list='VMs', columns=['Group', 'Terminate', 'STARTD Errors', 'Last Updated', 'Manual_Control', 'Swap (GBs)', 'Condor Slots', 'Start Time', 'Hostname', 'Power Status', 'IPs', 'Authorization URL', 'Foreign', 'Cloud', 'cores', 'Floating IPs', 'Flavor ID', 'Project', 'Flavor', 'STARTD Time', 'Dynamic Slots', 'Slots Timestamp', 'Primary Slots', 'State Age', 'Ram (MBs)', 'Disk (GBs)', 'HTCondor', 'VMID', 'Poller Status', 'Retire', 'Status', 'Task']
    )

    # 22
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'vm', 'list', '-r', '-su', ut_id(gvar, 'clu4')],
        expected_list='VMs', columns=['Key', 'Value']
    )

    # 23
    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'vm', 'list', '-cn', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 24
    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'vm', 'list', '-vc', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 25
    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'vm', 'list', '-vd', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 26
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-ved\', \'invalid-unit-test\']',
        ['cloudscheduler', 'vm', 'list', '-ved', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 27
    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'vm', 'list', '-vF', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 28
    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'vm', 'list', '-vf', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 29
    execute_csv2_command(
        gvar, 1, None, 'Error: The following command line arguments were invalid: vm-keyname',
        ['cloudscheduler', 'vm', 'list', '-vk', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 30
    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'vm', 'list', '-vr', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 31
    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'vm', 'list', '-vS', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 32
    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'vm', 'list', '-vs', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    #### UPDATE ####
    # TODO: Add update tests.

if __name__ == "__main__":
    main(None)
