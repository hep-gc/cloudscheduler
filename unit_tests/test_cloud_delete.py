from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id
from sys import argv

# lno: CV - error code identifier.

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
        '/cloud/delete/', group=ut_id(gvar, 'ctg1'),
        server_user='invalid-unit-test'
    )

    # 2
    execute_csv2_request(
        gvar, 1, None, 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'ctu1')),
        '/cloud/delete/', group=ut_id(gvar, 'ctg1'),
        server_user=ut_id(gvar, 'ctu1')
    )

    # 3
    execute_csv2_request(
        gvar, 1, None, 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'ctu2')),
        '/cloud/delete/', group=ut_id(gvar, 'ctg1'),
        server_user=ut_id(gvar, 'ctu2')
    )

    # 4
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud delete request did not contain mandatory parameter "cloud_name".',
        '/cloud/delete/', group=ut_id(gvar, 'ctg1'),
        server_user=ut_id(gvar, 'ctu3')
    )

    # 5
    execute_csv2_request(
        gvar, 1, 'CV', 'cloud delete request contained a bad parameter "invalid-unit-test".',
        '/cloud/delete/', group=ut_id(gvar, 'ctg1'),
        form_data={'cloud_name': 'invalid-unit-test', 'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu3')
    )

    # 6
    execute_csv2_request(
        gvar, 1, 'CV', 'cannot switch to invalid group "{}".'.format(ut_id(gvar, 'ctg2')),
        '/cloud/delete/', group=ut_id(gvar, 'ctg2'), form_data={'cloud_name': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu3')
    )

    # 7
    execute_csv2_request(
        gvar, 1, 'CV', 'value specified for "cloud_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        '/cloud/delete/', group=ut_id(gvar, 'ctg1'), form_data={'cloud_name': 'Invalid-Unit-Test'},
        server_user=ut_id(gvar, 'ctu3')
    )

    # 8
    execute_csv2_request(
        gvar, 1, 'CV', 'value specified for "cloud_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        '/cloud/delete/', group=ut_id(gvar, 'ctg1'), form_data={'cloud_name': 'invalid-unit-test-'},
        server_user=ut_id(gvar, 'ctu3')
    )

    # 9
    execute_csv2_request(
        gvar, 1, 'CV', 'value specified for "cloud_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        '/cloud/delete/', group=ut_id(gvar, 'ctg1'), form_data={'cloud_name': 'invalid-unit-test!'},
        server_user=ut_id(gvar, 'ctu3')
    )

    # 10
    execute_csv2_request(
        gvar, 1, 'CV', 'the request did not match any rows.',
        '/cloud/delete/', group=ut_id(gvar, 'ctg1'), form_data={'cloud_name': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu3')
    )

    # 11
    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully deleted.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc1')),
        '/cloud/delete/', group=ut_id(gvar, 'ctg1'), form_data={'cloud_name': ut_id(gvar, 'ctc1')},
        server_user=ut_id(gvar, 'ctu3')
    )

if __name__ == "__main__":
    main(None)
