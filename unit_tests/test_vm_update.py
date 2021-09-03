from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, sanity_requests, parameters_requests
from sys import argv

# lno: VV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)

    # 01 - 05
    sanity_requests(gvar, '/vm/update/', ut_id(gvar, 'vtg1'), ut_id(gvar, 'vtu1'), ut_id(gvar, 'vtg2'), ut_id(gvar, 'vtu2'))

    parameters = {
        # 06 Send a GET request.
        # 07 Send an invalid parameter.
        # 08 Omit vm_option.
        # 09 Give two vm_options.
        # 10
        'vm_option': {'valid': 'retain', 'test_cases': {'invalid-unit-test': 'vm update value specified for "vm_option" must be one of the following options: [\'kill\', \'manctl\', \'retain\', \'retire\', \'sysctl\'].'}, 'mandatory': True},
        # 11 Give two vm_hosts.
        # 12
        'vm_hosts': {'valid': 'invalid-unit-test', 'test_cases': {'': 'vm update value specified for "vm_hosts" must not be the empty string'}},
        # 13 Give two poller_statuses.
        # 14
        'poller_status': {'valid': 'idle', 'test_cases': {'invalid-unit-test': 'vm update value specified for "poller_status" must be one of the following options: [\'error\', \'idle\', \'manual\', \'native\', \'other\', \'retiring\', \'running\', \'starting\', \'unregistered\'].'}}
    }

    parameters_requests(gvar, '/vm/update/', ut_id(gvar, 'vtg1'), ut_id(gvar, 'vtu1'), parameters)

    # 'vm_hosts' specifies which VMs to update, so setting it to 'valid-unit-test' selects 0 VMs.
    # This means the tests below aren't actually testing much.
    # 15
    execute_csv2_request(
        gvar, 0, None, "vm update, VMs set to system control: 0.",
        '/vm/update/', group=ut_id(gvar, 'vtg1'), form_data={'vm_option': 'sysctl', 'vm_hosts': 'valid-unit-test'},
        server_user=ut_id(gvar, 'vtu1')
    )

    # 16
    execute_csv2_request(
        gvar, 0, None, "vm update, VMs killed: 0.",
        '/vm/update/', group=ut_id(gvar, 'vtg1'), form_data={'vm_option': 'kill', 'vm_hosts': ['valid-unit-test-0', 'valid-unit-test-1']},
        server_user=ut_id(gvar, 'vtu1')
    )

    # 17
    execute_csv2_request(
        gvar, 0, None, "vm update, VMs set to manual control: 0.",
        '/vm/update/', group=ut_id(gvar, 'vtg1'), form_data={'vm_option': 'manctl', 'vm_hosts': 'valid-unit-test'},
        server_user=ut_id(gvar, 'vtu1')
    )

    # 18
    execute_csv2_request(
        gvar, 0, None, "vm update, VMs retired: 0.",
        '/vm/update/', group=ut_id(gvar, 'vtg1'), form_data={'vm_option': 'retire', 'vm_hosts': 'valid-unit-test'},
        server_user=ut_id(gvar, 'vtu1')
    )

    # 19
    execute_csv2_request(
        gvar, 0, None, "vm update, VMs set to system control: 0.",
        '/vm/update/', group=ut_id(gvar, 'vtg1'), form_data={'vm_option': 'sysctl', 'poller_status': 'error', 'vm_hosts': 'valid-unit-test'},
        server_user=ut_id(gvar, 'vtu1')
    )

    # 20
    execute_csv2_request(
        gvar, 0, None, "vm update, VMs set to system control: 0.",
        '/vm/update/', group=ut_id(gvar, 'vtg1'), form_data={'vm_option': 'sysctl', 'cloud_name': 'valid-unit-test', 'vm_hosts': 'valid-unit-test'},
        server_user=ut_id(gvar, 'vtu1')
    )

    # 21
    execute_csv2_request(
        gvar, 0, None, "vm update, VMs set to system control: 0.",
        '/vm/update/', group=ut_id(gvar, 'vtg1'), form_data={'vm_option': 'sysctl', 'vm_hosts': 'valid-unit-test'},
        server_user=ut_id(gvar, 'vtu1')
    )

if __name__ == "__main__":
    main(None)
