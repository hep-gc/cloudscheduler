from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id, generate_secret
from sys import argv
import group_requests_cleanup

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv2_request(gvar, argv[0])
    if not gvar['user_secret']:
        gvar['user_secret'] = generate_secret()
    
    # 01
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'atu2'), ut_id(gvar, 'atg1')),
        ['cloudscheduler', 'accounting', 'apel', '-su', ut_id(gvar, 'clu3')],
        expected_list='APEL Accounting', columns=['Group', 'Cloud', 'Hostname', 'Cloud', 'Type', 'Region', 'Flavor', 'ID', 'Name', 'Image', 'ID', 'Name', 'Benchmark', 'Type', 'Score', 'VM', 'ID', 'Cores', 'Disk', 'RAM', 'Started', 'Ended', 'CPU Time', 'Network', 'Type', 'Received (MBs)', 'Sent (MBs)', 'Last Update']
    )

if __name__ == '__main__':
    main(None)
