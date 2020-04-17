from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id, sanity_commands
from sys import argv

# lno: CV - error code identifier.

# We have to include all the columns expected for both the Cloud status list and the Job status list when we are looking for either list, because both are included in the output.
CLOUD_JOB_COLUMNS = {'Group', 'Jobs', 'Idle', 'Running', 'Completed', 'Other', 'Foreign', 'Status', 'HTCondor', 'Agent', 'HTCondor FQDN', 'Days Left on Certificates', 'Condor', 'Worker', 'Group', 'Cloud', 'Defaults', 'Enabled', 'Flavor', 'Image', 'Keep Alive', 'Communications', 'Up', 'Request Time', 'VMs', 'Quota', 'Total', 'Starting', 'Unregistered', 'idle', 'Running', 'Retiring', 'Manual', 'Error', 'Other', 'Cores', 'Quota', 'Limit', 'Setting', 'Idle', 'Used', 'RAM', 'Quota', 'Limit', 'Setting', 'Idle', 'Used', 'Condor Slots', 'Busy', 'Busy Cores', 'Idle Cores', 'Foreign', 'VMs', 'Cores', 'RAM'}

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)

    # 01 - 14
    sanity_commands(gvar, 'cloud', 'status')

    # 15
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: metadata-mime-type',
        ['cloud', 'status', '-mmt', 'invalid-unit-test', '-g', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu3')]
    )

    # 16
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'clu3'), ut_id(gvar, 'clg1')),
        ['cloud', 'status', '-NV', '-su', ut_id(gvar, 'clu3')],
        expected_list='Cloud status', expected_columns=CLOUD_JOB_COLUMNS
    )

    # 17
    execute_csv2_command(
        gvar, 0, None, ut_id(gvar, 'clc2'),
        ['cloud', 'status', '-cn', ut_id(gvar, 'clc2'), '-NV', '-su', ut_id(gvar, 'clu3')],
        expected_list='Cloud status', expected_columns=CLOUD_JOB_COLUMNS
    )

    # 18
    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloud', 'status', '-cn', 'invalid-unit-test', '-NV', '-su', ut_id(gvar, 'clu3')]
    )

    # 19
    execute_csv2_command(
        gvar, 0, None, 'cloud status, 1. Job status: keys=group_name, columns=Jobs,Idle,Running,Completed,Other,foreign,htcondor_status,agent_status,htcondor_fqdn,condor_days_left,worker_days_left\ncloud status, 2. Cloud status: keys=group_name,cloud_name, columns=enabled,default_flavor,default_image,keep_alive,communication_up,communication_rt,VMs_quota,VMs,VMs_starting,VMs_unregistered,VMs_idle,VMs_running,VMs_retiring,VMs_manual,VMs_in_error,VMs_other,cores_quota,cores_limit,cores_ctl,cores_idle,cores_native,ram_quota,ram_limit,ram_ctl,ram_idle,ram_native,slot_count,slot_core_count,slot_idle_core_count,Foreign_VMs,cores_foreign,ram_foreign',
        ['cloud', 'status', '-VC', '-su', ut_id(gvar, 'clu3')]
    )

    # 20
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloud', 'status', '-NV', '-su', ut_id(gvar, 'clu3')],
        expected_list='Job status', expected_columns=CLOUD_JOB_COLUMNS
    )

if __name__ == "__main__":
    main(None)
