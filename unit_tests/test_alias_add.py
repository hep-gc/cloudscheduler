from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, generate_secret, sanity_requests, parameters_requests
from sys import argv

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv2_request(gvar, argv[0])
    if not gvar['user_secret']:
        gvar['user_secret'] = generate_secret()

    # Bad requests.
    # 01 - 04
    sanity_requests(gvar, '/alias/add/', ut_id(gvar, 'atg1'), ut_id(gvar, 'atu1'), ut_id(gvar, 'atg2'), ut_id(gvar, 'atu2'))

    # 05
    execute_csv2_request(
        gvar, 1, None, 'cloud alias add, invalid method "GET" specified.',
        '/alias/add/', group=ut_id(gvar, 'atg1'),
        server_user=ut_id(gvar, 'atu1')
    )

    PARAMETERS = [
        # 06 Give invalid parameter.
        # 07 Omit cloud_name.
        ('cloud_name', [
            # 08
            ('', 'cloud alias add, value specified for "cloud_name" must not be the empty string.'),
            # 09
            ('3E1', 'cloud alias add, value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain a more than one consecutive dash or start or end with a dash.'),
            # 10
            ('-invalid-unit-test', 'cloud alias add, value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain a more than one consecutive dash or start or end with a dash.'),
            # 11 Name of a non-existent cloud.
            ('invalid-unit-test', 'cloud alias add, "invalid-unit-test" failed - specified value in list of values does not exist: cloud_name=invalid-unit-test, group_name={}.'.format(ut_id(gvar, 'atg1')))
        ], ut_id(gvar, 'atc1')),
        # 12 Omit alias_name.
        ('alias_name', [
            # 13
            ('', 'cloud alias add, value specified for "alias_name" must not be the empty string.'),
            # 14
            ('\\invalid-unit-test', 'value specified for "alias_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain a more than one consecutive dash or start or end with a dash.'),
            # 15
            ('alias-name-that-is-too-long-for-the-database', 'Data too long for column \'alias_name\'')
        ], 'invalid-unit-test'),
    ]

    parameters_requests(gvar, '/alias/add/', ut_id(gvar, 'atg1'), ut_id(gvar, 'atu1'), PARAMETERS)
    
    # 16 Create an alias properly.
    execute_csv2_request(
        gvar, 0, None, 'cloud alias "{}.{}" successfully added.'.format(ut_id(gvar, 'atg1'), ut_id(gvar, 'ata2')),
        '/alias/add/', group=ut_id(gvar, 'atg1'), form_data={
            'alias_name': ut_id(gvar, 'ata2'),
            'cloud_name': ut_id(gvar, 'atc1')
        },
        server_user=ut_id(gvar, 'atu1')
    )

    # 17 Attempt to create an alias with a name that is taken.
    execute_csv2_request(
        gvar, 1, None, 'cloud alias add "{}.{}" failed - specified alias already exists.'.format(ut_id(gvar, 'atg1'), ut_id(gvar, 'ata2')),
        '/alias/add/', group=ut_id(gvar, 'atg1'), form_data={
            'alias_name': ut_id(gvar, 'ata2'),
            'cloud_name': ut_id(gvar, 'atc1')
        },
        server_user=ut_id(gvar, 'atu1')
    )

if __name__ == '__main__':
    main(None)
