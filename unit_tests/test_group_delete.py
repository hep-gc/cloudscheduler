from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, sanity_requests, parameters_requests
from sys import argv

# lno: GV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)

    # 01 - 05
    sanity_requests(gvar, '/group/delete/', ut_id(gvar, 'gtg4'), ut_id(gvar, 'gtu5'), ut_id(gvar, 'gtg7'), ut_id(gvar, 'gtu2'))

    # 06 Attempt as an unprivileged user.
    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 403, forbidden.',
        '/group/delete/', group=ut_id(gvar, 'gtg4'),
        server_user=ut_id(gvar, 'gtu3')
    )

    parameters = {
        # 07 Send a GET request.
        # 08 Omit group_name.
        # 09 Give two group_names.
        'group_name': {'valid': ut_id(gvar, 'gtg6'), 'test_cases': {
            # 10
            '': 'group delete value specified for "group_name" must not be the empty string.',
            # 11
            'Invalid-Unit-Test': 'group delete value specified for "group_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 12
            'invalid-unit-test-': 'group delete value specified for "group_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 13
            'invalid-unit-test!': 'group delete value specified for "group_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
        }, 'mandatory': True},
        # 14 Give two user_options.
        # 15
        'user_option': {'valid': 'add', 'test_cases': {'invalid-unit-test': 'group delete value specified for "user_option" must be one of the following options: [\'add\', \'delete\'].'}}
    }

    parameters_requests(gvar, '/group/delete/', ut_id(gvar, 'gtg4'), ut_id(gvar, 'gtu5'), parameters)

    # 16 Attempt to delete a group that does not exist.
    execute_csv2_request(
        gvar, 1, None, 'group resources delete "invalid-unit-test" failed - the request did not match any rows.',
        '/group/delete/', group=ut_id(gvar, 'gtg4'), form_data={'group_name': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'gtu5')
    )

    # 17
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully deleted.'.format(ut_id(gvar, 'gtg6')),
        '/group/delete/', group=ut_id(gvar, 'gtg4'), form_data={'group_name': ut_id(gvar, 'gtg6')},
        server_user=ut_id(gvar, 'gtu5')
    )

if __name__ == "__main__":
    main(None)
