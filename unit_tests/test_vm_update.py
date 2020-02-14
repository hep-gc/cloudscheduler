from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id
from sys import argv

# lno: VV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv2_request(gvar, argv[0])

    # 1
    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 401, unauthorized.',
        '/vm/update/',
        server_user='invalid-unit-test', server_pw='invalid-unit-test'
    )

    # 2
    execute_csv2_request(
        gvar, 1, None, 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'vtu1')),
        '/vm/update/',
        server_user=ut_id(gvar, 'vtu1')
    )

    # 3
    execute_csv2_request(
        gvar, 1, None, 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'vtu2')),
        '/vm/update/',
        server_user=ut_id(gvar, 'vtu2')
    )

    # 4
    execute_csv2_request(
        gvar, 1, 'VV', 'invalid method "GET" specified.',
        '/vm/update/',
        server_user=ut_id(gvar, 'vtu3')
    )

    # 5
    execute_csv2_request(
        gvar, 1, 'VV', 'vm update request contained a bad parameter "invalid-unit-test".',
        '/vm/update/', form_data={'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'vtu3')
    )

    # 6
    execute_csv2_request(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        '/vm/update/', group='invalid-unit-test',
        server_user=ut_id(gvar, 'vtu3')
    )

    # 7
    execute_csv2_request(
        gvar, 1, 'VV', 'vm update request did not contain mandatory parameter "vm_option".',
        '/vm/update/', group=ut_id(gvar, 'vtg1'), form_data={'vm_hosts': ''},
        server_user=ut_id(gvar, 'vtu3')
    )

    # 8
    execute_csv2_request(
        gvar, 1, None, 'cannot switch to invalid group "{}".'.format(ut_id(gvar, 'vtg2')),
        '/vm/update/', group=ut_id(gvar, 'vtg2'),
        server_user=ut_id(gvar, 'vtu3')
    )

    # 9
    execute_csv2_request(
        gvar, 1, 'VV', "vm update value specified for \"vm_option\" must be one of the following options: ['kill', 'manctl', 'retain', 'retire', 'sysctl'].",
        '/vm/update/', group=ut_id(gvar, 'vtg1'), form_data={'vm_option': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'vtu3')
    )

    # 10
    execute_csv2_request(
        gvar, 0, None, "vm update, VMs set to system control: 0.",
        '/vm/update/', group=ut_id(gvar, 'vtg1'), form_data={'vm_option': 'sysctl', 'vm_hosts': ''},
        server_user=ut_id(gvar, 'vtu3')
    )

    # 11
    execute_csv2_request(
        gvar, 0, None, "vm update, VMs killed: 0.",
        '/vm/update/', group=ut_id(gvar, 'vtg1'), form_data={'vm_option': 'kill', 'vm_hosts': ''},
        server_user=ut_id(gvar, 'vtu3')
    )

    # 12
    execute_csv2_request(
        gvar, 0, None, "vm update, VMs set to manual control: 0.",
        '/vm/update/', group=ut_id(gvar, 'vtg1'), form_data={'vm_option': 'manctl', 'vm_hosts': ''},
        server_user=ut_id(gvar, 'vtu3')
    )

    # 13
    execute_csv2_request(
        gvar, 0, None, "vm update, VMs retired: 0.",
        '/vm/update/', group=ut_id(gvar, 'vtg1'), form_data={'vm_option': 'retire', 'vm_hosts': ''},
        server_user=ut_id(gvar, 'vtu3')
    )

    # 14
    execute_csv2_request(
        gvar, 1, 'VV', "vm update value specified for \"poller_status\" must be one of the following options: ['error', 'idle', 'manual', 'native', 'other', 'retiring', 'running', 'starting', 'unregistered'].",
        '/vm/update/', group=ut_id(gvar, 'vtg1'), form_data={'vm_option': 'sysctl', 'poller_status': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'vtu3')
    )

    # 15
    execute_csv2_request(
        gvar, 0, None, "vm update, VMs set to system control: 0.",
        '/vm/update/', group=ut_id(gvar, 'vtg1'), form_data={'vm_option': 'sysctl', 'poller_status': 'error', 'vm_hosts': ''},
        server_user=ut_id(gvar, 'vtu3')
    )

    # 16
    execute_csv2_request(
        gvar, 0, None, "vm update, VMs set to system control: 0.",
        '/vm/update/', group=ut_id(gvar, 'vtg1'), form_data={'vm_option': 'sysctl', 'cloud_name': 'invalid-unit-test', 'vm_hosts': ''},
        server_user=ut_id(gvar, 'vtu3')
    )

    # 17
    execute_csv2_request(
        gvar, 0, None, "vm update, VMs set to system control: 0.",
        '/vm/update/', group=ut_id(gvar, 'vtg1'), form_data={'vm_option': 'sysctl', 'vm_hosts': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'vtu3')
    )

if __name__ == "__main__":
    main(None)
