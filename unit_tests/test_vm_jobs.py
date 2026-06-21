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
    sanity_requests(gvar, '/vm/jobs/', ut_id(gvar, 'vtg1'), ut_id(gvar, 'vtu1'), ut_id(gvar, 'vtu2'), ut_id(gvar, 'vtu2'))
    
    # 06
    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/jobs/', group=ut_id(gvar, 'vtg1'),
        server_user=ut_id(gvar, 'vtu1')
    )
    
    # 07 
    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/jobs/', group=ut_id(gvar, 'vtg1'),
        query_data={'job_status': '1'},
        server_user=ut_id(gvar, 'vtu1')
    )
    
    # 08
    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/jobs/', group=ut_id(gvar, 'vtg1'),
        query_data={'job_status': '2'},
        server_user=ut_id(gvar, 'vtu1')
    )
    
    # 09 
    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/jobs/', group=ut_id(gvar, 'vtg1'),
        query_data={'job_status': '4'},
        server_user=ut_id(gvar, 'vtu1')
    )
    
    # 10
    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/jobs/', group=ut_id(gvar, 'vtg1'),
        query_data={'job_status': '5'},
        server_user=ut_id(gvar, 'vtu1')
    )
    
    # 11 
    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/jobs/', group=ut_id(gvar, 'vtg1'),
        query_data={'group_name': ut_id(gvar, 'vtg1')},
        server_user=ut_id(gvar, 'vtu1')
    )
    
    # 12
    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/jobs/', group=ut_id(gvar, 'vtg1'),
        query_data={'group_name': ut_id(gvar, 'vtg1'), 'job_status': '1'},
        server_user=ut_id(gvar, 'vtu1')
    )
  
if __name__ == "__main__":
    main(None)
