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

    execute_csv2_command(
        gvar, 1, None, 'No action specified for object "vm"',
        ['cloudscheduler', 'vm', '-s', 'unit-test-un']
    )

    execute_csv2_command(
        gvar, 1, None, 'Invalid action "invalid-unit-test" for object "vm"',
        ['cloudscheduler', 'vm', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'user settings for server "invalid-unit-test" does not contain a URL value.',
        ['cloudscheduler', 'vm', '-s', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'No action specified for object "vm"; use -h or -H for help.',
        ['cloudscheduler', 'vm', '-s', 'unit-test-un']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler vm".',
        ['cloudscheduler', 'vm', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'vm', '-H']
    )

    #### LIST ####
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'vm', 'list', '-xx', 'yy']
    )
    
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: vm-option',
        ['cloudscheduler', 'vm', 'list', '-vo', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'user settings for server "invalid-unit-test" does not contain a URL value.',
        ['cloudscheduler', 'vm', 'list', '-s', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'vm', 'list', '-s', 'unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'vm', 'list', '-s', 'unit-test-un']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler vm list".',
        ['cloudscheduler', 'vm', 'list', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'vm', 'list', '-H']
    )

    execute_csv2_command(
        gvar, 0, None, 'Expose API requested',
        ['cloudscheduler', 'vm', 'list', '-xA']
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'vm', 'list', '-g', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test-un, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'test'), ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'vm', 'list', '-g', ut_id(gvar, 'clg1')]
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'vm', 'list', '-ok'],
        list='VMs', columns=['Group', 'Cloud', 'Hostname']
    )

    execute_csv2_command(
        gvar, 0, None, 'vm list, table #1 columns: keys=group_name,cloud_name,hostname, columns=',
        ['cloudscheduler', 'vm', 'list', '-VC']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'vm', 'list', '-NV'],
        list='VMs', columns=['Group', 'Cloud', 'Hostname', 'VMID', 'Authorization URL', 'Project', 'Status', 'Flavor ID', 'Task', 'Power Status', 'Terminate', 'Terminate Time', 'Status Change Time', 'Last Updated', 'Flavor', 'Condor Slots', 'Condor Off', 'Foreign', 'cores', 'Disk (GBs)', 'Ram (MBs)', 'Swap (GBs)', 'Poller Status']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'vm', 'list', '-V', 'project,task'],
        list='VMs', columns=['Group', 'Cloud', 'Hostname', 'Project', 'Task']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'vm', 'list'],
        list='VMs', columns=['Group', 'Cloud', 'Hostname', 'Project', 'Task']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'vm', 'list', '-V', ''],
        list='VMs', columns=['Group', 'Cloud', 'Hostname', 'VMID', 'Authorization URL', 'Project', 'Status', 'Flavor ID', 'Task', 'Power Status', 'Terminate', 'Terminate Time', 'Status Change Time', 'Last Updated', 'Flavor', 'Condor Slots', 'Condor Off', 'Foreign', 'cores', 'Disk (GBs)', 'Ram (MBs)', 'Swap (GBs)', 'Poller Status']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'vm', 'list', '-r'],
        list='VMs', columns=['Key', 'Value']
    )

    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'vm', 'list', '-cn', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'vm', 'list', '-vc', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'vm', 'list', '-vd', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-ved\', \'invalid-unit-test\']',
        ['cloudscheduler', 'vm', 'list', '-ved', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'vm', 'list', '-vF', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'vm', 'list', '-vf', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'Error: The following command line arguments were invalid: vm-keypair',
        ['cloudscheduler', 'vm', 'list', '-vk', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'vm', 'list', '-vr', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'vm', 'list', '-vS', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'vm', 'list', '-vs', 'invalid-unit-test']
    )

    #### UPDATE ####

if __name__ == "__main__":
    main(None)

