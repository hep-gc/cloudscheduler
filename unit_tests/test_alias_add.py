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
    # 01
    execute_csv2_request(
        gvar, 2, None, 'server "unit-test", HTTP response code 401, unauthorized.',
        '/alias/add/', group=ut_id(gvar, 'atg1'),
        server_user='invalid-unit-test'
    )

    # 02
    execute_csv2_request(
        gvar, 1, None, 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'atu2')),
        '/alias/add/', group=ut_id(gvar, 'atg1'),
        server_user=ut_id(gvar, 'atu2')
    )

    # 03
    execute_csv2_request(
        gvar, 2, None, 'server "unit-test", HTTP response code 401, unauthorized.',
        '/alias/add/', group=ut_id(gvar, 'atg1'),
        server_user=ut_id(gvar, 'atu1'), server_pw='invalid-unit-test'
    )

    # 04 Attempt to switch to a group that the user is not in.
    execute_csv2_request(
        gvar, 1, None, 'cannot switch to invalid group "{}".'.format(ut_id(gvar, 'atg2')),
        '/alias/add/', group=ut_id(gvar, 'atg2'),
        server_user=ut_id(gvar, 'atu1')
    )

    # 05
    execute_csv2_request(
        gvar, 1, None, 'cloud alias add, invalid method "GET" specified.',
        '/alias/add/', group=ut_id(gvar, 'atg1'),
        server_user=ut_id(gvar, 'atu1')
    )

    PARAMETERS = [
        # 06 Omit cloud_name.
        ('cloud_name', [
            # 07
            ('', 'cloud alias add, value specified for "cloud_name" must not be the empty string.'),
            # 08
            ('3E1', 'cloud alias add, value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain a more than one consecutive dash or start or end with a dash.'),
            # 09
            ('-invalid-unit-test', 'cloud alias add, value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain a more than one consecutive dash or start or end with a dash.'),
            # 10 Name of a non-existent cloud.
            ('invalid-unit-test', 'cloud alias add, "invalid-unit-test" failed - specified value in list of values does not exist: cloud_name=invalid-unit-test, group_name={}.'.format(ut_id(gvar, 'atg1')))
        ], ut_id(gvar, 'atc1')),
        # 11 Omit alias_name.
        ('alias_name', [
            # 12
            ('', 'cloud alias add, value specified for "alias_name" must not be the empty string.'),
            # 13
            ('\\invalid-unit-test', 'value specified for "alias_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain a more than one consecutive dash or start or end with a dash.'),
            # 14
            ('alias-name-that-is-too-long-for-the-database', 'Data too long for column \'alias_name\'')
        ], 'invalid-unit-test'),
        # 15
        ('invalid-unit-test', [('invalid-unit-test', 'cloud alias add, request contained a bad parameter "invalid-unit-test".')])
    ]

    parameters_requests(gvar, '/alias/add/', ut_id(gvar, 'atg1'), ut_id(gvar, 'atu1'), PARAMETERS)
    
    # 16 Create an alias properly.
    execute_csv2_request(
        gvar, 0, None, 'cloud alias "{}.{}" successfully added.'.format(ut_id(gvar, 'atg1'), ut_id(gvar, 'atc1a2')),
        '/alias/add/', group=ut_id(gvar, 'atg1'), form_data={
            'cloud_name': ut_id(gvar, 'atc1'),
            'alias_name': ut_id(gvar, 'atc1a2')
        },
        server_user=ut_id(gvar, 'atu1')
    )

    # 17 Attempt to create an alias with a name that is taken.
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
