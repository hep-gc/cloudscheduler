from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, generate_secret, sanity_requests, parameters_requests
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
    sanity_requests(gvar, '/alias/update/', ut_id(gvar, 'atg1'), ut_id(gvar, 'atu1'), ut_id(gvar, 'atg2'), ut_id(gvar, 'atu2'))

    parameters = {
        # 06 Send a GET request.
        # 07 Give invalid parameter.
        # 08 Omit cloud_name.
        # 09 Give cloud_name and cloud_name.1.
        'cloud_name': {'valid': ut_id(gvar, 'atc2'), 'test_cases': {
            # 10
            '': 'cloud alias update, value specified for "cloud_name" must not be the empty string.',
            # 11
            'invalid-unit-Test': 'cloud alias update, value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 12
            '-invalid-unit-test': 'cloud alias update, value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 13
            'invalid-unit-test!': 'cloud alias update, value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 14
            'invalid-unit-test': 'cloud alias update, "{}" failed - specified value in list of values does not exist: cloud_name=invalid-unit-test'.format(ut_id(gvar, 'ata2'))
        }, 'mandatory': True, 'array_field': True},
        # 15 Omit alias_name.
        # 16 Give two alias_names.
        'alias_name': {'valid': ut_id(gvar, 'ata2'), 'test_cases': {
            # 17
            '': 'cloud alias update, value specified for "alias_name" must not be the empty string.',
            # 18
            'invalid-unit-test!': 'cloud alias update, value specified for "alias_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 19
            'invalid-unit-test': 'cloud alias group update "{}.invalid-unit-test" failed - specified alias does not exist.'.format(ut_id(gvar, 'atg1'))
        }, 'mandatory': True},
        # 20
        # 21 Give two cloud_options.
        'cloud_option': {'valid': 'add', 'test_cases': {'invalid-unit-test': 'cloud alias update, value specified for "cloud_option" must be one of the following options: [\'add\', \'delete\'].'}}
    }

    parameters_requests(gvar, '/alias/update/', ut_id(gvar, 'atg1'), ut_id(gvar, 'atu1'), parameters)

    # 22 Add atc2 to ata2.
    execute_csv2_request(
        gvar, 0, None, 'cloud alias "{}.{}" successfully updated.'.format(ut_id(gvar, 'atg1'), ut_id(gvar, 'ata2')),
        '/alias/update/', group=ut_id(gvar, 'atg1'), form_data={
            'alias_name': ut_id(gvar, 'ata2'),
            'cloud_name': ut_id(gvar, 'atc2')
        },
        server_user=ut_id(gvar, 'atu1')
    )

    # 23 Ensure that 19 actually added atc2.
    execute_csv2_request(
        gvar, 0, None, None,
        '/alias/list/', group=ut_id(gvar, 'atg1'),
        expected_list='cloud_alias_list', list_filter={'group_name': ut_id(gvar, 'atg1'), 'cloud_name': ut_id(gvar, 'atc2')},
        values={'alias_name': ut_id(gvar, 'ata2')},
        server_user=ut_id(gvar, 'atu1')
    )

    # Currently adding a cloud to an alias that it is already "in" causes the server to do nothing and give a successful response.

    # 24 Remove atc1 from ata2.
    execute_csv2_request(
        gvar, 0, None, 'cloud alias "{}.{}" successfully updated.'.format(ut_id(gvar, 'atg1'), ut_id(gvar, 'ata2')),
        '/alias/update/', group=ut_id(gvar, 'atg1'), form_data={
            'alias_name': ut_id(gvar, 'ata2'),
            'cloud_name': ut_id(gvar, 'atc1'),
            'cloud_option': 'delete'
        },
        server_user=ut_id(gvar, 'atu1')
    )

    # 25 Remove atc2 from ata2, causing ata2 to be deleted.
    execute_csv2_request(
        gvar, 0, None, 'cloud alias "{}.{}" successfully updated.'.format(ut_id(gvar, 'atg1'), ut_id(gvar, 'ata2')),
        '/alias/update/', group=ut_id(gvar, 'atg1'), form_data={
            'alias_name': ut_id(gvar, 'ata2'),
            'cloud_name': ut_id(gvar, 'atc2'),
            'cloud_option': 'delete'
        },
        server_user=ut_id(gvar, 'atu1')
    )

if __name__ == '__main__':
    main(None)
