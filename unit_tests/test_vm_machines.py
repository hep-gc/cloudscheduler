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
        gvar, 0, None, None,
        '/vm/machines/', group=ut_id(gvar, 'vtg1'),
        expected_list='machines_list', list_filter={'activity': 'Busy'},
        query_data={'activity': 'Busy'},
        server_user=ut_id(gvar, 'vtu1')
    )

    #08
    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/machines/', group=ut_id(gvar, 'vtg1'),
        expected_list='machines_list', list_filter={'activity': 'Idle'},
        query_data={'activity': 'Idle'},
        server_user=ut_id(gvar, 'vtu1')
    )

    # 09
    execute_csv2_request(
        gvar, 0, None, 'Machines updated, machines: 0.',
        '/vm/machines/update/', group=ut_id(gvar, 'vtg1'),
        form_data={'machine_option': 'kill', 'machine_hosts': 'invalid-machine'},
        server_user=ut_id(gvar, 'vtu1')
    )

    # 10 
    execute_csv2_request(
        gvar, 1, 'VV', 'machine update value specified for "machine_option" must be one of the following options:',
        '/vm/machines/update/', group=ut_id(gvar, 'vtg1'),
        form_data={'machine_option': 'dance', 'machine_hosts': 'invalid-machine'},
        server_user=ut_id(gvar, 'vtu1')
    )

    # 11 
    execute_csv2_request(
        gvar, 1, 'VV', 'machines update, invalid method "GET" specified.',
        '/vm/machines/update/', group=ut_id(gvar, 'vtg1'),
        server_user=ut_id(gvar, 'vtu1')
    )

    # 12 
    execute_csv2_request(
        gvar, 1, 'VV', 'machine update request contained a bad parameter "invalid_key".',
        '/vm/machines/update/', group=ut_id(gvar, 'vtg1'),
        form_data={'machine_option': 'retire', 'machine_hosts': 'invalid-machine', 'invalid_key': 'bad_value'},
        server_user=ut_id(gvar, 'vtu1')
    )
    
    # 13
    execute_csv2_request(
        gvar, 1, 'VV', 'machine update request did not contain mandatory parameter "machine_option".',
        '/vm/machines/update/', group=ut_id(gvar, 'vtg1'),
        form_data={'machine_hosts': 'invalid-machine'}, # Missing machine_option
        server_user=ut_id(gvar, 'vtu1')
    )

if __name__ == "__main__":
    main(None)
