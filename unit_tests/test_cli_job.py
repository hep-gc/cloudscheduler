from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id
from sys import argv

# lno: JV - error code identifier.

def main(gvar, user_secret):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv2_request(gvar, argv[0])

    execute_csv2_command(
        gvar, 1, None, 'No action specified for object "job"',
        ['cloudscheduler', 'job', '-s', 'unit-test-un']
    )

    execute_csv2_command(
        gvar, 1, None, 'Invalid action "invalid-unit-test" for object "job"',
        ['cloudscheduler', 'job', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'job', '-s', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'No action specified for object "job"; use -h or -H for help.',
        ['cloudscheduler', 'job', '-s', 'unit-test-un']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler job".',
        ['cloudscheduler', 'job', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'job', '-H']
    )

    #### LIST ####
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'job', 'list', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: job-cores',
        ['cloudscheduler', 'job', 'list', '-jc', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'job', 'list', '-s', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'job', 'list', '-s', 'unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'job', 'list', '-s', 'unit-test-un']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler job list".',
        ['cloudscheduler', 'job', 'list', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'job', 'list', '-H']
    )

    execute_csv2_command(
        gvar, 0, None, 'Expose API requested',
        ['cloudscheduler', 'job', 'list', '-xA']
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'job', 'list', '-g', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, '')[:-1], ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'job', 'list', '-g', ut_id(gvar, 'clg1'), '-s', 'unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test-un, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'test'), ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'job', 'list', '-g', ut_id(gvar, 'clg1'), '-s', 'unit-test-un']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'job', 'list', '-ok'],
        list='Jobs', columns=['Group', 'Job', 'ID']
    )

    execute_csv2_command(
        gvar, 0, None, 'job list, 1. Jobs: keys=group_name,global_job_id, columns=cluster_id,proc_id,user,user_data,requirements,target_alias,cloud_name,instance_type,request_cpus,request_ram,request_disk,request_swap,job_per_core,image,network,job_priority,job_status,js_idle,js_running,js_completed,js_held,js_other,keep_alive,max_price,entered_current_status,q_date,held_reason',
        ['cloudscheduler', 'job', 'list', '-VC']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'job', 'list', '-NV'],
        list='Jobs', columns=['Requested', 'Group', 'Job', 'ID', 'Cluster', 'ID', 'Process', 'ID', 'User', 'User', 'Data', 'Requirements', 'Target', 'Clouds', 'Cloud', 'Instance', 'Type', 'CPUs', 'RAM', '{MBs}', 'Disk', '{GBs}', 'Swap', '(GBs)', 'Jobs', 'per', 'Core', 'Image', 'Job', 'Job', 'Status', 'Flags', 'Group', 'Job', 'ID', 'Network', 'Priority', 'Status', 'Code', 'Idle', 'Running', 'Completed', 'Held', 'Other', 'Keep', 'Alive', '(seconds)', 'Max', 'Spot', 'Price', 'Group', 'Job', 'ID', 'State', 'Change', 'Date', 'Queued', 'Date', 'Held', 'Job', 'Reason']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'job', 'list', '-V', 'cluster_id,proc_id,user'],
        list='Jobs', columns=['Group', 'Job', 'ID', 'Cluster', 'ID', 'Process', 'ID', 'User']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'job', 'list'],
        list='Jobs', columns=['Group', 'Job', 'ID', 'Cluster', 'ID', 'Process', 'ID', 'User']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'job', 'list', '-V', ''],
        list='Jobs', columns=['Requested', 'Group', 'Job', 'ID', 'Cluster', 'ID', 'Process', 'ID', 'User', 'User', 'Data', 'Requirements', 'Target', 'Clouds', 'Cloud', 'Instance', 'Type', 'CPUs', 'RAM', '{MBs}', 'Disk', '{GBs}', 'Swap', '(GBs)', 'Jobs', 'per', 'Core', 'Image', 'Job', 'Job', 'Status', 'Flags', 'Group', 'Job', 'ID', 'Network', 'Priority', 'Status', 'Code', 'Idle', 'Running', 'Completed', 'Held', 'Other', 'Keep', 'Alive', '(seconds)', 'Max', 'Spot', 'Price', 'Group', 'Job', 'ID', 'State', 'Change', 'Date', 'Queued', 'Date', 'Held', 'Job', 'Reason']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'job', 'list', '-r'],
        list='Jobs', columns=['Key', 'Value']
    )
            
if __name__ == "__main__":
    main(None)

