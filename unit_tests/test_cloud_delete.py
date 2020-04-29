from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, sanity_requests, parameters_requests
from sys import argv

# lno: CV - error code identifier.

def main(gvar):

    # 01 - 05
    sanity_requests(gvar, '/cloud/delete/', ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctu1'), ut_id(gvar, 'ctg2'), ut_id(gvar, 'ctu2'))
    
    parameters = {
        # 06 Send a GET request.
        # 07 Give an invalid parameter.
        # 08 Omit cloud_name.
        # 09 Give two cloud_names.
        'cloud_name': {'valid': ut_id(gvar, 'ctc1'), 'test_cases': {
            # 10
            '': 'cloud delete value specified for "cloud_name" must not be the empty string.',
            # 11
            'Invalid-Unit-Test': 'cloud delete value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 12
            'invalid-unit-test-': 'cloud delete value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 13
            'invalid-unit-test!': 'cloud delete value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 14
            'invalid-unit-test': 'the request did not match any rows.',
        }, 'mandatory': True}
    }

    parameters_requests(gvar, '/cloud/delete/', ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctu1'), parameters)

    # 15
    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully deleted.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc1')),
        '/cloud/delete/', group=ut_id(gvar, 'ctg1'), form_data={'cloud_name': ut_id(gvar, 'ctc1')},
        server_user=ut_id(gvar, 'ctu1')
    )

if __name__ == "__main__":
    main(initialize_csv2_request(selections=argv[1] if len(argv) > 1 else ''))
