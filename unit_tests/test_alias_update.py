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

    # 06
    execute_csv2_request(
        gvar, 1, None, 'cloud alias update, invalid method "GET" specified.',
        '/alias/update/', group=ut_id(gvar, 'atg1'),
        server_user=ut_id(gvar, 'atu1')
    )

    PARAMETERS = [
        # 07 Give invalid parameter.
        # 08 Omit cloud_name.
        ('cloud_name', {
            # 09
            '': 'cloud alias update, value specified for "cloud_name" must not be the empty string.',
            # 10
            'invalid-unit-Test': 'cloud alias update, value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 11
            '-invalid-unit-test': 'cloud alias update, value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 12
            'invalid-unit-test!': 'cloud alias update, value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 13
            'invalid-unit-test': 'cloud alias update, "{}" failed - specified value in list of values does not exist: cloud_name=invalid-unit-test'.format(ut_id(gvar, 'ata1'))
        }, ut_id(gvar, 'atc1')),
        # 14 Omit alias_name.
        ('alias_name', {
            # 15
            '': 'cloud alias update, value specified for "alias_name" must not be the empty string.',
            # 16
            'invalid-unit-test!': 'cloud alias update, value specified for "alias_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 17
            'invalid-unit-test': 'cloud alias group update "{}.invalid-unit-test" failed - specified alias does not exist.'.format(ut_id(gvar, 'atg1'))
        }, ut_id(gvar, 'ata1')),
        # 18
        ('cloud_option', {'invalid-unit-test': 'cloud alias update, value specified for "cloud_option" must be one of the following options: [\'add\', \'delete\'].'})
    ]

    parameters_requests(gvar, '/alias/update/', ut_id(gvar, 'atg1'), ut_id(gvar, 'atu1'), PARAMETERS)

    # 19 Add atc2 to ata2.
    execute_csv2_request(
        gvar, 0, None, 'cloud alias "{}.{}" successfully updated.'.format(ut_id(gvar, 'atg1'), ut_id(gvar, 'ata2')),
        '/alias/update/', group=ut_id(gvar, 'atg1'), form_data={
            'alias_name': ut_id(gvar, 'ata2'),
            'cloud_name': ut_id(gvar, 'atc2')
        },
        server_user=ut_id(gvar, 'atu1')
    )

    # 20 Remove atc1 from ata2.
    execute_csv2_request(
        gvar, 0, None, 'cloud alias "{}.{}" successfully updated.'.format(ut_id(gvar, 'atg1'), ut_id(gvar, 'ata2')),
        '/alias/update/', group=ut_id(gvar, 'atg1'), form_data={
            'alias_name': ut_id(gvar, 'ata2'),
            'cloud_name': ut_id(gvar, 'atc1'),
            'cloud_option': 'delete'
        },
        server_user=ut_id(gvar, 'atu1')
    )

    # 21 Remove atc2 from ata2, causing ata2 to be deleted.
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
