from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, generate_secret
from sys import argv

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)
    if not gvar['user_secret']:
        gvar['user_secret'] = generate_secret()

    # 01
    execute_csv2_request(
        gvar, None, None, None,
        '/user/delete/', form_data={'username': ut_id(gvar, 'atu1')}
    )

    # 02
    execute_csv2_request(
        gvar, None, None, None,
        '/user/delete/', form_data={'username': ut_id(gvar, 'atu2')}
    )
    
    # 03
    execute_csv2_request(
        gvar, None, None, None,
        '/group/delete/', form_data={'group_name': ut_id(gvar, 'atg1')}
    )

    # 04
    execute_csv2_request(
        gvar, None, None, None,
        '/group/delete/', form_data={'group_name': ut_id(gvar, 'atg2')}
    )

if __name__ == '__main__':
    main(None)
