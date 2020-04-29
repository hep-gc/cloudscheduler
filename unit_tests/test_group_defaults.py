from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, sanity_requests
from sys import argv

# lno: GV - error code identifier.

def main(gvar):

    # 01 - 05
    sanity_requests(gvar, '/group/defaults/', ut_id(gvar, 'gtg4'), ut_id(gvar, 'gtu3'), ut_id(gvar, 'gtg7'), ut_id(gvar, 'gtu1'))

    # We cannot use parameters_requests here because /group/defaults/ accepts GET requests (in addition to POSTs).
    # 06
    execute_csv2_request(
        gvar, 1, 'GV', 'request contained a bad parameter "invalid-unit-test".',
        '/group/defaults/', group=(ut_id(gvar, 'gtg4')), form_data={'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'gtu3')
    )

    # 07 - 16
    int_parameters = ['job_cpus', 'job_ram', 'job_disk', 'job_swap', 'vm_keep_alive']
    for param in int_parameters:
        execute_csv2_request(
            gvar, 1, 'GV', 'default update/list request contained a bad parameter "{}.1".'.format(param),
            '/group/defaults/', group=ut_id(gvar, 'gtg4'), form_data={param: 0, '{}.1'.format(param): 0},
            server_user=ut_id(gvar, 'gtu3')
        )
        execute_csv2_request(
            gvar, 1, 'GV', 'default update/list value specified for "{}" must be an integer value.'.format(param),
            '/group/defaults/', group=ut_id(gvar, 'gtg4'), form_data={param: 'invalid-unit-test'},
            server_user=ut_id(gvar, 'gtu3')
        )

    # 17
    execute_csv2_request(
        gvar, 1, 'GV', 'request contained a rejected/bad parameter "job_scratch".',
        '/group/defaults/', group=ut_id(gvar, 'gtg4'), form_data={'job_scratch': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'gtu3')
    )

    # 18 - 21
    vm_parameters = ['vm_image', 'vm_flavor', 'vm_network', 'vm_keyname']
    for param in vm_parameters:
        execute_csv2_request(
            gvar, 1, 'GV', 'group defaults update specified item does not exist: {}=invalid-unit-test, group_name={}.'.format(param, ut_id(gvar, 'gtg4')),
            '/group/defaults/', group=ut_id(gvar, 'gtg4'), form_data={param: 'invalid-unit-test'},
            server_user=ut_id(gvar, 'gtu3')
        )

    # 22 Proper POST request.
    execute_csv2_request(
        gvar, 0, None, '"{}" successfully updated.'.format(ut_id(gvar, 'gtg4')),
        '/group/defaults/', group=ut_id(gvar, 'gtg4'), form_data={
            'job_cpus': 1,
            'job_ram': 1,
            'job_disk': 1,
            'job_swap': 1,
            'vm_keep_alive': 1,
            'vm_flavor': '',
            'vm_image': '',
            'vm_keyname': '',
            'vm_network': '',
        },
        server_user=ut_id(gvar, 'gtu3')
    )

    # 23 Proper GET request checking that the POST worked.
    execute_csv2_request(
        gvar, 0, None, None,
        '/group/defaults/', group=ut_id(gvar, 'gtg4'),
        expected_list='defaults_list', list_filter={'group_name': ut_id(gvar, 'gtg4')}, values={
            'htcondor_fqdn': gvar['fqdn'],
            'job_cpus': 1,
            'job_ram': 1,
            'job_disk': 1,
            'vm_keep_alive': 1,
            'vm_flavor': '',
            'vm_image': '',
            'vm_keyname': '',
            'vm_network': '',
        },
        server_user=ut_id(gvar, 'gtu3')
    )

if __name__ == "__main__":
    main(initialize_csv2_request(selections=argv[1] if len(argv) > 1 else ''))
