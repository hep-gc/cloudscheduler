from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, generate_secret
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
        '/alias/add', group=ut_id(gvar, 'atg1'),
        server_user='invalid-unit-test'
    )

    # 03
    execute_csv2_request(
        gvar, 1, None, 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'atu2')),
        '/alias/add', group=ut_id(gvar, 'atg1'),
        server_user=ut_id(gvar, 'atu2')
    )

    # 05
    execute_csv2_request(
        gvar, 2, None, 'server "unit-test", HTTP response code 401, unauthorized.',
        '/alias/add', group=ut_id(gvar, 'atg1'),
        server_user=ut_id(gvar, 'atu1'), server_pw='invalid-unit-test'
    )

    # 08
    execute_csv2_request(
        gvar, 1, None, 'cannot switch to invalid group "{}".'.format(ut_id(gvar, 'atg2')),
        '/alias/add', group=ut_id(gvar, 'atg2'),
        server_user=ut_id(gvar, 'atu1')
    )

    # 09
    execute_csv2_request(
        gvar, 1, None, 'cloud alias add, invalid method "GET" specified.',
        '/alias/add', group=ut_id(gvar, 'atg1'),
        server_user=ut_id(gvar, 'atu1')
    )

    #
    execute_csv2_request(
        gvar, 1, None, 'TODO',
        '/alias/add', group=ut_id(gvar, 'atg1'), form_data={
            'cloud_name': ut_id(gvar, 'atc1'),
            'alias_name': 'invalid-unit-test',
            'invalid-unit-test': None
        },
        server_user=ut_id(gvar, 'atu1')
    )

    #
    execute_csv2_request(
        gvar, 1, None, 'TODO',
        '/alias/add', group=ut_id(gvar, 'atg1'), form_data={
            'cloud_name': ut_id(gvar, 'atc1'),
            'alias_name': 'invalid-unit-test',
            'invalid-unit-test': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'atu1')
    )

    # Bad cloud names.
    #
    execute_csv2_request(
        gvar, 1, None, 'TODO',
        '/alias/add', group=ut_id(gvar, 'atu1'), form_data={
            'cloud_name': None,
            'alias_name': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'atu1')
    )

    #
    execute_csv2_request(
        gvar, 1, None, 'TODO',
        '/alias/add', group=ut_id(gvar, 'atu1'), form_data={
            'cloud_name': 0,
            'alias-name': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'atu1')
    )

    #
    execute_csv2_request(
        gvar, 1, None, 'TODO',
        '/alias/add', group=ut_id(gvar, 'atu1'), form_data={
            'cloud_name': '-invalid-unit-test',
            'alias-name': ut_id(gvar, 'invalid-unit-test')
        },
        server_user=ut_id(gvar, 'atu1')
    )

    #
    execute_csv2_request(
        gvar, 1, None, 'TODO',
        '/alias/add', group=ut_id(gvar, 'atu1'), form_data={
            'cloud_name': 'invalid-unit-test',
            'alias-name': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'atu1')
    )

    # Bad alias names.
    #
    execute_csv2_request(
        gvar, 1, None, 'TODO',
        '/alias/add', group=ut_id(gvar, 'atu1'), form_data={
            'cloud_name': 'invalid-unit-test',
            'alias-name': None
        },
        server_user=ut_id(gvar, 'atu1')
    )

    #
    execute_csv2_request(
        gvar, 1, None, 'TODO',
        '/alias/add', group=ut_id(gvar, 'atu1'), form_data={
            'cloud_name': 'invalid-unit-test',
            'alias-name': '-invalid-unit-test'
        },
        server_user=ut_id(gvar, 'atu1')
    )

    # Create an alias properly.
    #
    execute_csv2_request(
        gvar, 1, None, 'TODO',
        '/alias/add', group=ut_id(gvar, 'atu1'), form_data={
            'cloud_name': ut_id(gvar, 'atc1'),
            'alias-name': ut_id(gvar, 'atc1a1')
        },
        server_user=ut_id(gvar, 'atu1')
    )

    # Attempt to create an alias with a name that is taken.
    #
    execute_csv2_request(
        gvar, 1, None, 'TODO',
        '/alias/add', group=ut_id(gvar, 'atu1'), form_data={
            'cloud_name': ut_id(gvar, 'atc1'),
            'alias-name': ut_id(gvar, 'atc1a1')
        },
        server_user=ut_id(gvar, 'atu1')
    )

if __name__ == '__main__':
    main(None)
