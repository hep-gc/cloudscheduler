from unit_test_common import execute_csv2_request, execute_csv2_command, initialize_csv2_request, ut_id
from sys import argv

# lno: JV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv2_request(gvar, argv[0])

    execute_csv2_request(
        gvar, 0, None, None,
        '/job/list/', group=ut_id(gvar, 'dtg1'), expected_list='job_list', list_filter={'group_name': ut_id(gvar, 'dtg1')},
        values={'request_cpus': 1,
            'request_ram': 1,
            'request_disk': '0.0010',
            'job_priority': 10
        }
    )

if __name__ == "__main__":
    main(None)
