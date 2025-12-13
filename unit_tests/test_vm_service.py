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

    # 01
    execute_csv2_request(
        gvar, 0, None, None,
        '/vm/settings/', group=ut_id(gvar, 'vtg1'),
        expected_list='service_list',
        server_user=ut_id(gvar, 'vtu1')
    )

    # 02
    execute_csv2_request(
        gvar, 0, None, 'Update Success',
        '/vm/settings/update/', group=ut_id(gvar, 'vtg1'),
        form_data={'service_alias': 'csv2-main', 'service_option': 'show'},
        server_user=ut_id(gvar, 'vtu1')
    )

    # 03
    execute_csv2_request(
        gvar, 0, None, 'Update Success',
        '/vm/settings/update/', group=ut_id(gvar, 'vtg1'),
        form_data={'service_alias': 'csv2-main', 'service_option': 'hide'},
        server_user=ut_id(gvar, 'vtu1')
    )

    # 04
    execute_csv2_request(
        gvar, 0, None, "VV-00747 value specified for \"service_option\" must be one of the following options: ['hide', 'show'].",
        '/vm/settings/update/', group=ut_id(gvar, 'vtg1'),
        form_data={'service_alias': 'csv2-main', 'service_option': 'invalid'},
        server_user=ut_id(gvar, 'vtu1')
    )

    # 05
    execute_csv2_request(
        gvar, 1, None, 'No services selected.',
        '/vm/settings/update/', group=ut_id(gvar, 'vtg1'),
        form_data={'service_option': 'show'},
        server_user=ut_id(gvar, 'vtu1')
    )

if __name__ == "__main__":
    main(None)
