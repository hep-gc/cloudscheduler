from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id
from sys import argv

# lno: JV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)

    # 01
    execute_csv2_command(
        gvar, 1, None, 'No action specified for object "job"',
        ['cloudscheduler', 'job', '-su', ut_id(gvar, 'clu4')]
    )

    # 02
    execute_csv2_command(
        gvar, 1, None, 'Invalid action "invalid-unit-test" for object "job"',
        ['cloudscheduler', 'job', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 03
    execute_csv2_command(
        gvar, None, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'job', '-s', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')], timeout=8
    )

    # 04
    execute_csv2_command(
        gvar, 1, None, 'No action specified for object "job"; use -h or -H for help.',
        ['cloudscheduler', 'job', '-su', ut_id(gvar, 'clu4')]
    )

    # 05
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler job".',
        ['cloudscheduler', 'job', '-h', '-su', ut_id(gvar, 'clu4')]
    )

    # 06
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'job', '-H', '-su', ut_id(gvar, 'clu4')]
    )

    #### LIST ####
    # 07
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'job', 'list', '-xx', 'yy', '-su', ut_id(gvar, 'clu4')]
    )

    # 08
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: job-cores',
        ['cloudscheduler', 'job', 'list', '-jc', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 09
    execute_csv2_command(
        gvar, None, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'job', 'list', '-s', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')], timeout=8
    )

    # 10
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'job', 'list', '-su', ut_id(gvar, 'clu4')]
    )

    # 11
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'job', 'list', '-su', ut_id(gvar, 'clu4')]
    )

    # 12
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler job list".',
        ['cloudscheduler', 'job', 'list', '-h', '-su', ut_id(gvar, 'clu4')]
    )

    # 13
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'job', 'list', '-H', '-su', ut_id(gvar, 'clu4')]
    )

    # 14
    execute_csv2_command(
        gvar, 0, None, 'Expose API requested',
        ['cloudscheduler', 'job', 'list', '-xA', '-su', ut_id(gvar, 'clu4')]
    )

    # 15
    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'job', 'list', '-g', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 16
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'clu4'), ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'job', 'list', '-g', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu4')]
    )

    # 17
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'clu4'), ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'job', 'list', '-g', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu4')]
    )

    # 18
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'job', 'list', '-ok', '-su', ut_id(gvar, 'clu4')],
        expected_list='Jobs', columns=['Group', 'Job ID']
    )

    # 19
    execute_csv2_command(
        gvar, 0, None, 'job list, 1. Jobs: keys=group_name,global_job_id, columns=cluster_id,proc_id,user,user_data,requirements,target_clouds,cloud_name,instance_type,request_cpus,request_ram,request_disk,request_swap,job_per_core,image,network,job_priority,job_status,js_idle,js_running,js_completed,js_held,js_other,keep_alive,max_price,entered_current_status,q_date,held_reason',
        ['cloudscheduler', 'job', 'list', '-VC', '-su', ut_id(gvar, 'clu4')]
    )

    # 20
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'job', 'list', '-NV', '-su', ut_id(gvar, 'clu4')],
        expected_list='Jobs', columns=['Group', 'Job ID', 'Cluster ID', 'Process ID', 'User', 'User Data', 'Requirements', 'Target Clouds', 'Cloud', 'Instance Type', 'Requested', 'CPUs', 'RAM {MBs}', 'Disk {GBs}', 'Swap (GBs)', 'Jobs per Core', 'Image', 'Network', 'Job', 'Priority', 'Status Code', 'Job Status Flags', 'Idle', 'Running', 'Completed', 'Held', 'Other', 'Keep Alive (seconds)', 'Max Spot Price', 'State Change Date', 'Queued Date', 'Held Job Reason']
    )

    # 21
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'job', 'list', '-V', 'cluster_id,proc_id,user', '-su', ut_id(gvar, 'clu4')],
        expected_list='Jobs', columns=['Group', 'Job ID', 'Cluster ID', 'Process ID', 'User']
    )

    # 22
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'job', 'list', '-su', ut_id(gvar, 'clu4')],
        expected_list='Jobs', columns=['Group', 'Job ID', 'Cluster ID', 'Process ID', 'User']
    )

    # 23
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'job', 'list', '-V', '', '-su', ut_id(gvar, 'clu4')],
        expected_list='Jobs', columns=['Group', 'Job ID', 'Cluster ID', 'Process ID', 'User', 'User Data', 'Requirements', 'Target Clouds', 'Cloud', 'Instance Type', 'Requested', 'CPUs', 'RAM {MBs}', 'Disk {GBs}', 'Swap (GBs)', 'Jobs per Core', 'Image', 'Network', 'Job', 'Priority', 'Status Code', 'Job Status Flags', 'Idle', 'Running', 'Completed', 'Held', 'Other', 'Keep Alive (seconds)', 'Max Spot Price', 'State Change Date', 'Queued Date', 'Held Job Reason']
    )

    # 24
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'job', 'list', '-r', '-su', ut_id(gvar, 'clu4')],
        expected_list='Jobs', columns=['Key', 'Value']
    )
            
if __name__ == "__main__":
    main(None)
