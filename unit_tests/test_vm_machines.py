from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, sanity_requests
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
    sanity_requests(gvar, '/vm/machines/', ut_id(gvar, 'vtg1'), ut_id(gvar, 'vtu1'), ut_id(gvar, 'vtu2'), ut_id(gvar, 'vtu2'))

    # 06 
    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/machines/', group=ut_id(gvar, 'vtg1'),
        server_user=ut_id(gvar, 'vtu1')
    )

    # 07 
    execute_csv2_request(
        gvar, 0, None, 'Machines updated, machines: 0.',
        '/vm/machines/update/', group=ut_id(gvar, 'vtg1'),
        form_data={'machine_option': 'retire', 'machine_hosts': 'invalid-machine'},
        server_user=ut_id(gvar, 'vtu1')
    )

    # 08 
    execute_csv2_request(
        gvar, 0, None, 'Machines updated, machines: 0.',
        '/vm/machines/update/', group=ut_id(gvar, 'vtg1'),
        form_data={'machine_option': 'kill', 'machine_hosts': 'invalid-machine'},
        server_user=ut_id(gvar, 'vtu1')
    )

    # 09 
    execute_csv2_request(
        gvar, 1, None, 'VV-00646 machine update value specified for "machine_option" must be one of the following options: [\'kill\', \'native\', \'retire\'].',
        '/vm/machines/update/', group=ut_id(gvar, 'vtg1'),
        form_data={'machine_option': 'dance', 'machine_hosts': 'invalid-machine'},
        server_user=ut_id(gvar, 'vtu1')
    )

if __name__ == "__main__":
    main(None)
