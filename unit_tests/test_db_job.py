from unit_test_common import execute_csv2_request, execute_csv2_command, initialize_csv2_request, ut_id
from sys import argv

# lno: JV - error code identifier.

def main(gvar, user_secret):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv2_request(gvar, argv[0])

    execute_csv2_request(
        gvar, 0, None, None,
        '/job/list/?vm-test-group', list='job_list', filter={'group_name': 'vm-test-group', 'global_job_id': 'csv2-dev2.heprc.uvic.ca#1.0#1'},
        values={'hold_job_reason': None, 'request_ram': 2000, 'js_idle': 0, 'held_reason': 'vm-testing', 'instance_type': 'vm-test-instance', 'request_disk': '14.3051', 'js_held': 1, 'request_cpus': 1, 'keep_alive': '0', 'js_completed': 0, 'js_running': 0, 'js_other': 0, 'job_status': 5, 'user': 'jodiew@csv2-dev2.heprc.uvic.ca', 'requirements': 'group_name is "vm-test-group"', 'cloud_name': None, 'proc_id': 0, 'target_alias': None, 'job_priority': 10, 'cluster_id': 1}
    )

    execute_csv2_command(
        gvar, 0, None, 'Rows: 1',
        ['cloudscheduler', 'job', 'list', '-g', 'vm-test-group', '-s', 'unit-test']
    )

if __name__ == "__main__":
    main(None)
