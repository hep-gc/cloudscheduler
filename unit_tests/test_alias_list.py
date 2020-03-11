from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, generate_secret, sanity_requests
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

    # Bad requests.
    # 01 - 05
    sanity_requests(gvar, '/alias/list/', ut_id(gvar, 'atg1'), ut_id(gvar, 'atu1'), ut_id(gvar, 'atg2'), ut_id(gvar, 'atu2'))

    # 06
    execute_csv2_request(
        gvar, 1, None, 'cloud alias list, request contained a bad parameter "invalid-unit-test".',
        '/alias/list/', group=ut_id(gvar, 'atg1'), form_data={'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'atu1')
    )

    # 07 Find ata1 in the list.
    execute_csv2_request(
        gvar, 0, None, None,
        '/alias/list/', group=ut_id(gvar, 'atg1'),
        expected_list='cloud_alias_list', list_filter={'group_name': ut_id(gvar, 'atg1'), 'cloud_name': ut_id(gvar, 'atc1')},
        values={'alias_name': ut_id(gvar, 'ata1')},
        server_user=ut_id(gvar, 'atu1')
    )

if __name__ == '__main__':
    main(None)
