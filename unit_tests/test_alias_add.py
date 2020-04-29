from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, generate_secret, sanity_requests, parameters_requests
from sys import argv

def main(gvar):

    # Bad requests.
    # 01 - 05
    sanity_requests(gvar, '/alias/add/', ut_id(gvar, 'atg1'), ut_id(gvar, 'atu1'), ut_id(gvar, 'atg2'), ut_id(gvar, 'atu2'))

    parameters = {
        # 06 Send a GET request.
        # 07 Give an invalid parameter.
        # 08 Omit cloud_name.
        # 09 Give cloud_name and cloud_name.1.
        'cloud_name': {'valid': ut_id(gvar, 'atc1'), 'test_cases': {
            # 10
            '': 'cloud alias add, value specified for "cloud_name" must not be the empty string.',
            # 11
            'invalid-unit-test!': 'cloud alias add, value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 12
            'invalid-unit--test': 'cloud alias add, value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 13
            'invalid-unit-test-': 'cloud alias add, value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 14 Name of a non-existent cloud.
            'invalid-unit-test': 'cloud alias add, "invalid-unit-test" failed - specified value in list of values does not exist: cloud_name=invalid-unit-test, group_name={}.'.format(ut_id(gvar, 'atg1'))
        }, 'mandatory': True, 'array_field': True},
        # 15 Omit alias_name.
        # 16 Give two alias_names.
        'alias_name': {'valid': 'invalid-unit-test', 'test_cases': {
            # 17
            '': 'cloud alias add, value specified for "alias_name" must not be the empty string.',
            # 18
            'invalid-unit-test!': 'value specified for "alias_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 19
            'alias-name-that-is-too-long-for-the-database': 'Data too long for column \'alias_name\'',
            # 20 Attempt to create an alias that already exists.
            ut_id(gvar, 'ata1'): 'cloud alias add "{}.{}" failed - specified alias already exists.'.format(ut_id(gvar, 'atg1'), ut_id(gvar, 'ata1'))
        }, 'mandatory': True}
    }

    parameters_requests(gvar, '/alias/add/', ut_id(gvar, 'atg1'), ut_id(gvar, 'atu1'), parameters)
    
    # 21 Create an alias properly.
    execute_csv2_request(
        gvar, 0, None, 'cloud alias "{}.{}" successfully added.'.format(ut_id(gvar, 'atg1'), ut_id(gvar, 'ata3')),
        '/alias/add/', group=ut_id(gvar, 'atg1'), form_data={
            'alias_name': ut_id(gvar, 'ata3'),
            'cloud_name': ut_id(gvar, 'atc1')
        },
        server_user=ut_id(gvar, 'atu1')
    )

    # 22 Ensure that 19 actually created ata3.
    execute_csv2_request(
        gvar, 0, None, None,
        '/alias/list/', group=ut_id(gvar, 'atg1'),
        expected_list='cloud_alias_list', list_filter={'group_name': ut_id(gvar, 'atg1'), 'cloud_name': ut_id(gvar, 'atc1')},
        values={'alias_name': ut_id(gvar, 'ata3')},
        server_user=ut_id(gvar, 'atu1')
    )

if __name__ == '__main__':
    main(initialize_csv2_request(selections=argv[1] if len(argv) > 1 else ''))
