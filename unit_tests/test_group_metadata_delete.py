from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id
from sys import argv

# lno: GV - error code identifier.

def main(gvar):
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
        server_user='invalid-unit-test'
    )

    # 02
    execute_csv2_request(
        gvar, 1, 'GV', 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'gtu1')),
        '/group/metadata-delete/',
        server_user=ut_id(gvar, 'gtu1')
    )

    # 03
    execute_csv2_request(
        gvar, 1, 'GV', 'user "%s" is not a member of any group.' % ut_id(gvar, 'gtu1'),
        '/group/metadata-delete/'
, form_data={'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'gtu1')
    )

    # 04
    execute_csv2_request(
        gvar, 1, 'GV', 'group metadata-delete request did not contain mandatory parameter "metadata_name".',
        '/group/metadata-delete/', group=ut_id(gvar, 'gtg5'),
        server_user=ut_id(gvar, 'gtu3')
    )

    # 05
    execute_csv2_request(
        gvar, 1, 'GV', 'request contained a bad parameter "invalid-unit-test".',
        '/group/metadata-delete/', group=ut_id(gvar, 'gtg5')
, form_data={
            'metadata_name': 'invalid-unit-test',
            'invalid-unit-test': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'gtu3')
    )

    # 06
    execute_csv2_request(
        gvar, 1, 'GV', 'cannot switch to invalid group "invalid-unit-test".',
        '/group/metadata-delete/', group='invalid-unit-test', form_data={
            'metadata_name': 'invalid-unit-test'
            },
        server_user=ut_id(gvar, 'gtu3')
    )

    # 07
    execute_csv2_request(
        gvar, 1, 'GV', 'cannot switch to invalid group "{}".'.format(ut_id(gvar, 'gtg7')),
        '/group/metadata-delete/', group=ut_id(gvar, 'gtg7'), form_data={
            'metadata_name': 'invalid-unit-test'
            },
        server_user=ut_id(gvar, 'gtu3')
    )

    # 08
    execute_csv2_request(
        gvar, 1, 'GV', '"{}::invalid-unit-test" failed - the request did not match any rows.'.format(ut_id(gvar, 'gtg5')),
        '/group/metadata-delete/', group=ut_id(gvar, 'gtg5'), form_data={
            'metadata_name': 'invalid-unit-test'
            },
        server_user=ut_id(gvar, 'gtu3')
    )

    # 09
    execute_csv2_request(
        gvar, 0, None, 'file "{}::{}" successfully deleted.'.format(ut_id(gvar, 'gtg5'), ut_id(gvar, 'gty4')),
        '/group/metadata-delete/', group=ut_id(gvar, 'gtg5'), form_data={
            'metadata_name': ut_id(gvar, 'gty4')
            },
        server_user=ut_id(gvar, 'gtu3')
    )

    # Deleting group metadata that is in a clouds exceptions list should remove it from that list
    # 10
    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/list/', group=ut_id(gvar, 'gtg5'),expected_list='cloud_list', list_filter={'cloud_name': ut_id(gvar, 'gtc1')},
        values={'cloud_name': ut_id(gvar, 'gtc1'), 'group_name': ut_id(gvar, 'gtg5'), 'group_exclusions': ut_id(gvar, 'gty6')},
        server_user=ut_id(gvar, 'gtu3')
    )

    # 11
    execute_csv2_request(
        gvar, 0, None, 'file "{}::{}" successfully deleted.'.format(ut_id(gvar, 'gtg5'), ut_id(gvar, 'gty6')),
        '/group/metadata-delete/', group=ut_id(gvar, 'gtg5'), form_data={
            'metadata_name': ut_id(gvar, 'gty6')
            },
        server_user=ut_id(gvar, 'gtu3')
    )

    # 12
    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/list/', group=ut_id(gvar, 'gtg5'),
        expected_list='cloud_list', list_filter={'cloud_name': ut_id(gvar, 'gtc1')},
        values={'cloud_name': ut_id(gvar, 'gtc1'), 'group_name': ut_id(gvar, 'gtg5'), 'group_exclusions': None},
        server_user=ut_id(gvar, 'gtu3')
    )

    # 13
    execute_csv2_request(
        gvar, 1, 'GV', 'group metadata-delete request did not contain mandatory parameter "metadata_name".',
        '/group/metadata-delete/',
        server_user=ut_id(gvar, 'gtu3')
    )

if __name__ == "__main__":
    main(None)
