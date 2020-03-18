from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id, sanity_commands, table_commands
from sys import argv

# lno: VV - error code identifier.

VM_LIST_COLUMNS = ['Group', 'Cloud', 'Hostname', 'VMID', 'IPs', 'Floating IPs', 'Authorization URL', 'Project', 'Status', 'Flavor ID', 'Task', 'Power Status', 'Start Time', 'HTCondor', 'STARTD Errors', 'STARTD Time', 'Primary Slots', 'Dynamic Slots', 'Slots Timestamp', 'Retire', 'Terminate', 'Last Updated', 'Flavor', 'Condor Slots', 'Foreign', 'cores', 'Disk (GBs)', 'Ram (MBs)', 'Swap (GBs)', 'Poller Status', 'State Age', 'Manual_Control']

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)

    # 01 - 13
    sanity_commands(gvar, 'vm')

    #### LIST ####
    # 14 - 27
    sanity_commands(gvar, 'vm', 'list')

    # 28
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: vm-option',
        ['vm', 'list', '--vm-option', 'invalid-unit-test', '-g', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu3')]
    )

    # 29
    execute_csv2_command(
        gvar, 0, None, 'vm list, 1. VMs: keys=group_name,cloud_name,hostname, columns=vmid,vm_ips,vm_floating_ips,auth_url,project,status,flavor_id,task,power_status,start_time,htcondor_startd_errors,htcondor_startd_time,htcondor_partitionable_slots,htcondor_dynamic_slots,htcondor_slots_timestamp,retire,terminate,last_updated,flavor_name,condor_slots,foreign_vm,cores,disk,ram,swap,poller_status,age,manual_control',
        ['vm', 'list', '-VC', '-su', ut_id(gvar, 'clu3')]
    )

    # 30 - 36
    table_commands(gvar, 'vm', 'list', ut_id(gvar, 'clg1'), ut_id(gvar, 'clu3'), {'VMs': VM_LIST_COLUMNS})

    # 37
    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['vm', 'list', '--cloud-name', 'invalid-unit-test', '-su', ut_id(gvar, 'clu3')]
    )

    # 38
    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['vm', 'list', '--vm-cores', 'invalid-unit-test', '-su', ut_id(gvar, 'clu3')]
    )

    # 39
    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['vm', 'list', '--vm-disk', 'invalid-unit-test', '-su', ut_id(gvar, 'clu3')]
    )

    # 40
    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['vm', 'list', '--vm-foreign', 'invalid-unit-test', '-su', ut_id(gvar, 'clu3')]
    )

    # 41
    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['vm', 'list', '--vm-flavor', 'invalid-unit-test', '--vm-ram', 'invalid-unit-test', '--vm-status', 'invalid-unit-test', '--vm-swap', 'invalid-unit-test', '-su', ut_id(gvar, 'clu3')]
    )

    # 42
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}'.format(ut_id(gvar, 'clu3')),
        ['vm', 'list', '-su', ut_id(gvar, 'clu3')]
    )

    #### UPDATE ####
    # 43 - 56
    sanity_commands(gvar, 'vm', 'update')

    # In order to test `vm update` properly we would need to know that at least one VM exists, and its identity.
    # Because of the way that Cloudscheduler works, VMs are not manually added, so this would be difficult to implement and has been left unimplemented for now.

if __name__ == "__main__":
    main(None)
