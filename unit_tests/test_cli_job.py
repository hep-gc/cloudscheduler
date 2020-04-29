from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id, sanity_commands, table_commands
from sys import argv

# lno: JV - error code identifier.

JOB_LIST_COLUMNS = ['Group', 'Job ID', 'Cluster ID', 'Process ID', 'User', 'User Data', 'Requirements', 'Target Alias', 'Cloud', 'Instance Type', 'Requested', 'CPUs', 'RAM {MBs}', 'Disk {GBs}', 'Swap (GBs)', 'Jobs per Core', 'Image', 'Network', 'Job', 'Priority', 'Status Code', 'Job Status Flags', 'Idle', 'Running', 'Completed', 'Held', 'Other', 'Keep Alive (seconds)', 'Max Spot Price', 'State Change Date', 'Queued Date', 'Held Job Reason']

def main(gvar):

    # 01 - 13
    sanity_commands(gvar, 'job')

    #### LIST ####
    # 14 - 27
    sanity_commands(gvar, 'job', 'list')

    # 28
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: job-cores',
        ['job', 'list', '-jc', 'invalid-unit-test', '-g', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu3')]
    )

    # 29
    execute_csv2_command(
        gvar, 0, None, 'job list, 1. Jobs: keys=group_name,global_job_id, columns=cluster_id,proc_id,user,user_data,requirements,target_alias,cloud_name,instance_type,request_cpus,request_ram,request_disk,request_swap,job_per_core,image,network,job_priority,job_status,js_idle,js_running,js_completed,js_held,js_other,keep_alive,max_price,entered_current_status,q_date,held_reason',
        ['job', 'list', '-VC']
    )

    # 30 - 36
    table_commands(gvar, 'job', 'list', ut_id(gvar, 'clg1'), ut_id(gvar, 'clu3'), {'Jobs': JOB_LIST_COLUMNS})

    # 37
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'clu3'), ut_id(gvar, 'clg1')),
        ['job', 'list', '-su', ut_id(gvar, 'clu3')],
        expected_list='Jobs', expected_columns=set(JOB_LIST_COLUMNS)
    )

if __name__ == "__main__":
    main(initialize_csv2_request(selections=argv[1] if len(argv) > 1 else ''))
