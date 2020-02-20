from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id
from sys import argv

# lno: CV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)

    # 01
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'cloud', 'status', '-xx', 'yy', '-su', ut_id(gvar, 'clu4')]
    )

    # 02
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: metadata-mime-type',
        ['cloudscheduler', 'cloud', 'status', '-mmt', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 03
    execute_csv2_command(
        gvar, None, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'cloud', 'status', '-s', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')], timeout=8
    )

    # 04
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'status', '-su', ut_id(gvar, 'clu4')]
    )

    # 05
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler cloud status".',
        ['cloudscheduler', 'cloud', 'status', '-h', '-su', ut_id(gvar, 'clu4')]
    )

    # 06
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'cloud', 'status', '-H', '-su', ut_id(gvar, 'clu4')]
    )

    # 07
    execute_csv2_command(
        gvar, 0, None, 'Expose API requested',
        ['cloudscheduler', 'cloud', 'status', '-xA', '-su', ut_id(gvar, 'clu4')]
    )

    # 08
    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'cloud', 'status', '-g', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 09
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'clu4'), ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'cloud', 'status', '-g', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu4')]
    )

    # 10
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'clu4'), ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'cloud', 'status', '-su', ut_id(gvar, 'clu4')]
    )

    # 11
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'clu4'), ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'cloud', 'status', '-su', ut_id(gvar, 'clu4')]
    )

    # 12
    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'cloud', 'status', '-cn', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 13
    execute_csv2_command(
        gvar, 0, None, ut_id(gvar, 'clc2'),
        ['cloudscheduler', 'cloud', 'status', '-su', ut_id(gvar, 'clu4')]
    )

    # 14
    execute_csv2_command(
        gvar, 0, None, 'Rows: 1',
        ['cloudscheduler', 'cloud', 'status', '-cn', ut_id(gvar, 'clc2')]
    )

    # 15
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'status', '-ok', '-su', ut_id(gvar, 'clu4')],
        expected_list='Cloud status', columns=['Group', 'Cloud']
    )

    # 16
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'status', '-ok', '-su', ut_id(gvar, 'clu4')],
        expected_list='Job status', columns=['Group', 'Group', 'Cloud']
    )

    # 17
    execute_csv2_command(
        gvar, 0, None, 'cloud status, 1. Job status: keys=group_name, columns=Jobs,Idle,Running,Completed,Other,foreign,htcondor_status,agent_status,htcondor_fqdn,condor_days_left,worker_days_left\ncloud status, 2. Cloud status: keys=group_name,cloud_name, columns=enabled,default_flavor,default_image,keep_alive,communication_up,communication_rt,VMs_quota,VMs,VMs_starting,VMs_unregistered,VMs_idle,VMs_running,VMs_retiring,VMs_manual,VMs_in_error,VMs_other,cores_quota,cores_limit,cores_ctl,cores_idle,cores_native,ram_quota,ram_limit,ram_ctl,ram_idle,ram_native,slot_count,slot_core_count,slot_idle_core_count,Foreign_VMs,cores_foreign,ram_foreign',
        ['cloudscheduler', 'cloud', 'status', '-NV', '-VC', '-su', ut_id(gvar, 'clu4')]
    )

    # 18 We have to include all the columns expected for both the Cloud status list and the Job status list here and in the next test because of the way that the common code checks them.
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'status', '-NV', '-su', ut_id(gvar, 'clu4')],
        expected_list='Cloud status', columns=['Group', 'Jobs', 'Idle', 'Running', 'Completed', 'Other', 'Foreign', 'Status', 'HTCondor', 'Agent', 'HTCondor FQDN', 'Days Left on Certificates', 'Condor', 'Worker', 'Group', 'Cloud', 'Defaults', 'Enabled', 'Flavor', 'Image', 'Keep Alive', 'Communications', 'Up', 'Request Time', 'VMs', 'Quota', 'Total', 'Starting', 'Unregistered', 'idle', 'Running', 'Retiring', 'Manual', 'Error', 'Other', 'Cores', 'Quota', 'Limit', 'Setting', 'Idle', 'Used', 'RAM', 'Quota', 'Limit', 'Setting', 'Idle', 'Used', 'Condor Slots', 'Busy', 'Busy Cores', 'Idle Cores', 'Foreign', 'VMs', 'Cores', 'RAM']
    )

    # 19
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'status', '-NV', '-su', ut_id(gvar, 'clu4')],
        expected_list='Job status', columns=['Group', 'Jobs', 'Idle', 'Running', 'Completed', 'Other', 'Foreign', 'Status', 'HTCondor', 'Agent', 'HTCondor FQDN', 'Days Left on Certificates', 'Condor', 'Worker', 'Group', 'Cloud', 'Defaults', 'Enabled', 'Flavor', 'Image', 'Keep Alive', 'Communications', 'Up', 'Request Time', 'VMs', 'Quota', 'Total', 'Starting', 'Unregistered', 'idle', 'Running', 'Retiring', 'Manual', 'Error', 'Other', 'Cores', 'Quota', 'Limit', 'Setting', 'Idle', 'Used', 'RAM', 'Quota', 'Limit', 'Setting', 'Idle', 'Used', 'Condor Slots', 'Busy', 'Busy Cores', 'Idle Cores', 'Foreign', 'VMs', 'Cores', 'RAM']
    )

    # 20
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'status', '-V', 'Jobs/enabled', '-su', ut_id(gvar, 'clu4')]
    )

    # 21
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'status', '-su', ut_id(gvar, 'clu4')],
        expected_list='Cloud status', columns=['Group', 'Jobs', 'Defaults', 'Group', 'Cloud', 'Enabled']
    )

    # 22
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'status', '-su', ut_id(gvar, 'clu4')],
        expected_list='Job status', columns=['Group', 'Jobs', 'Defaults', 'Group', 'Cloud', 'Enabled']
    )

    # 23
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'status', '-r', '-su', ut_id(gvar, 'clu4')],
        expected_list='Cloud status', columns=['Key', 'Value']
    )

    # 24
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'status', '-r', '-su', ut_id(gvar, 'clu4')],
        expected_list='Job status', columns=['Key', 'Value']
    )

    # 25
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'status', '-V', '', '-su', ut_id(gvar, 'clu4')]
    )

if __name__ == "__main__":
    main(None)
