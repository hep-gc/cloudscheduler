from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id
from sys import argv

# lno: GV - error code identifier.

def main(gvar, user_secret):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv2_request(gvar, argv[0])
    
    # 01
    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 401, unauthorized.',
        '/group/metadata-delete/',
        server_user='invalid-unit-test', server_pw=user_secret
    )

    # 02
    execute_csv2_request(
        gvar, 1, 'GV29', 'invalid method "GET" specified.',
        '/group/metadata-delete/',
        server_user=ut_id(gvar, 'gtu1'), server_pw=user_secret
    )

    # 03
    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 403, forbidden.',
        '/group/metadata-delete/', form_data={'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'gtu1'), server_pw=user_secret
    )

    # 04
    execute_csv2_request(
        gvar, 1, 'GV30', 'group metadata-delete request did not contain mandatory parameter "metadata_name".',
        '/group/metadata-delete/', form_data={'group': ut_id(gvar, 'gtg5')},
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    # 05
    execute_csv2_request(
        gvar, 1, 'GV30', 'request contained a bad parameter "invalid-unit-test".',
        '/group/metadata-delete/', form_data={
            'metadata_name': 'invalid-unit-test',
            'invalid-unit-test': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    # 06
    execute_csv2_request(
        gvar, 1, 'GV29', 'cannot switch to invalid group "invalid-unit-test".',
        '/group/metadata-delete/', form_data={
            'metadata_name': 'invalid-unit-test',
            'group': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    # 07
    execute_csv2_request(
        gvar, 1, 'GV29', 'cannot switch to invalid group "{}".'.format(ut_id(gvar, 'gtg7')),
        '/group/metadata-delete/', form_data={
            'metadata_name': 'invalid-unit-test',
            'group': ut_id(gvar, 'gtg7')
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    # 08
    execute_csv2_request(
        gvar, 1, 'GV31', '"{}::invalid-unit-test" failed - the request did not match any rows.'.format(ut_id(gvar, 'gtg5')),
        '/group/metadata-delete/', form_data={
            'metadata_name': 'invalid-unit-test',
            'group': ut_id(gvar, 'gtg5')
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    # 09
    execute_csv2_request(
        gvar, 0, None, 'file "{}::{}" successfully deleted.'.format(ut_id(gvar, 'gtg5'), ut_id(gvar, 'gty4')),
        '/group/metadata-delete/', form_data={
            'metadata_name': ut_id(gvar, 'gty4'),
            'group': ut_id(gvar, 'gtg5')
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    # Deleting group metadata that is in a clouds exceptions list should remove it from that list
    # 10
    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/list/',
        list='cloud_list', filter={'cloud_name': ut_id(gvar, 'gtc1')},
        values={'cloud_name': ut_id(gvar, 'gtc1'), 'group_name': ut_id(gvar, 'gtg5'), 'group_exclusions': ut_id(gvar, 'gty6')},
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    # 11
    execute_csv2_request(
        gvar, 0, None, 'file "{}::{}" successfully deleted.'.format(ut_id(gvar, 'gtg5'), ut_id(gvar, 'gty6')),
        '/group/metadata-delete/', form_data={
            'metadata_name': ut_id(gvar, 'gty6'),
            'group': ut_id(gvar, 'gtg5')
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    # 12
    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/list/',
        list='cloud_list', filter={'cloud_name': ut_id(gvar, 'gtc1')},
        values={'cloud_name': ut_id(gvar, 'gtc1'), 'group_name': ut_id(gvar, 'gtg5'), 'group_exclusions': None},
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

if __name__ == "__main__":
    main(None)
