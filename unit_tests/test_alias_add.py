from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, generate_secret, parameters_requests
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
    # 0
    execute_csv2_request(
        gvar, 2, None, 'server "unit-test", HTTP response code 401, unauthorized.',
        '/alias/add/', group=ut_id(gvar, 'atg1'),
        server_user='invalid-unit-test'
    )

    # 0
    execute_csv2_request(
        gvar, 1, None, 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'atu2')),
        '/alias/add/', group=ut_id(gvar, 'atg1'),
        server_user=ut_id(gvar, 'atu2')
    )

    # 0
    execute_csv2_request(
        gvar, 2, None, 'server "unit-test", HTTP response code 401, unauthorized.',
        '/alias/add/', group=ut_id(gvar, 'atg1'),
        server_user=ut_id(gvar, 'atu1'), server_pw='invalid-unit-test'
    )

    # 0
    execute_csv2_request(
        gvar, 1, None, 'cannot switch to invalid group "{}".'.format(ut_id(gvar, 'atg2')),
        '/alias/add/', group=ut_id(gvar, 'atg2'),
        server_user=ut_id(gvar, 'atu1')
    )

    # 0
    execute_csv2_request(
        gvar, 1, None, 'cloud alias add, invalid method "GET" specified.',
        '/alias/add/', group=ut_id(gvar, 'atg1'),
        server_user=ut_id(gvar, 'atu1')
    )

    PARAMETERS = [
        ('cloud_name', [
            #
            ('', 'TODO'),
            # 
            (3.1, 'cloud alias add, value specified for "cloud_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.'),
            # 
            ('-invalid-unit-test', 'cloud alias add, value specified for "cloud_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.'),
            ('cloud-name-that-is-too-long-for-the-database', 'TODO'),
            # Name of a non-existent cloud.
            ('invalid-unit-test', 'cloud alias add, "invalid-unit-test" failed - specified value in list of values does not exist: cloud_name=invalid-unit-test, group_name={}.'.format(ut_id(gvar, 'atg1')))
        ], ut_id(gvar, 'atc1')),
        # 
        ('alias_name', [
            ('', 'TODO'),
            ('\033[92m', 'cloud alias add, value specified for "alias_name" must be all lower case.')
        ], 'invalid-unit-test'),
        # 
        ('invalid_unit_test', [('invalid-unit-test', 'cloud alias add, request contained a bad parameter "invalid_unit_test".')])
    ]

    parameters_requests(gvar, '/alias/add/', ut_id(gvar, 'atg1'), ut_id(gvar, 'atu1'), PARAMETERS)
    
    # Create an alias properly.
    #
    execute_csv2_request(
        gvar, 0, None, 'cloud alias "{}.{}" successfully added.'.format(ut_id(gvar, 'atg1'), ut_id(gvar, 'atc1a2')),
        '/alias/add/', group=ut_id(gvar, 'atg1'), form_data={
            'cloud_name': ut_id(gvar, 'atc1'),
            'alias_name': ut_id(gvar, 'atc1a2')
        },
        server_user=ut_id(gvar, 'atu1')
    )

    # Attempt to create an alias with a name that is taken.
    #
    execute_csv2_request(
        gvar, 1, None, 'cloud alias add "{}.{}" failed - specified alias already exists.'.format(ut_id(gvar, 'atg1'), ut_id(gvar, 'atc1a2')),
        '/alias/add/', group=ut_id(gvar, 'atg1'), form_data={
            'cloud_name': ut_id(gvar, 'atc1'),
            'alias_name': ut_id(gvar, 'atc1a2')
        },
        server_user=ut_id(gvar, 'atu1')
    )

if __name__ == '__main__':
    main(None)
