from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, sanity_requests, parameters_requests
from sys import argv

# lno: CV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)
    
    # 01 - 05
    sanity_requests(gvar, '/cloud/metadata-delete/', ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctu3'), ut_id(gvar, 'ctg2'), ut_id(gvar, 'ctu1'))

    PARAMETERS = {
        # 06 Send a GET request.
        # 07 Give an invalid parameter.
        # 08 Omit cloud_name.
        'cloud_name': {'valid': ut_id(gvar, 'ctc3'), 'test_cases': {
            # 09
            '': 'cloud metadata-delete value specified for "cloud_name" must not be the empty string.',
            # 10
            'Invalid-unit-test': 'cloud metadata-delete value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 11
            'invalid-unit-test-': 'cloud metadata-delete value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 12
            'invalid-unit-test!': 'cloud metadata-delete value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 13 Tests both a cloud that does not exist and metadata that does not exist.
            'invalid-unit-test': 'the request did not match any rows.'
        }, 'mandatory': True},
        # 14 Omit metadata_name.
        'metadata_name': {'valid': ut_id(gvar, 'cty2'), 'test_cases': {
            # 15
            '': 'cloud metadata-delete value specified for "metadata_name" must not be the empty string.',
            # 16
            'invalid-unit-test!': 'cloud metadata-delete value specified for "metadata_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.'
        }, 'mandatory': True}
    }

    parameters_requests(gvar, '/cloud/metadata-delete/', ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctu3'), PARAMETERS)

    # 17
    execute_csv2_request(
        gvar, 0, None, 'cloud metadata file "{}::{}::{}" successfully deleted.'.format(ut_id(gvar, 'ctg1'), ut_id(gvar, 'ctc3'), ut_id(gvar, 'cty2')),
        '/cloud/metadata-delete/', group=(ut_id(gvar, 'ctg1')),
        form_data={
            'cloud_name': ut_id(gvar, 'ctc3'),
            'metadata_name': ut_id(gvar, 'cty2')
        },
        server_user=ut_id(gvar, 'ctu3')
    )

if __name__ == "__main__":
    main(None)
