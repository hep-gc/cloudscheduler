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
    
    # 1
    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 401, unauthorized.',
        '/group/metadata-list/', group=ut_id(gvar, 'gtg5'),
        server_user='invalid-unit-test'
    )

    # 2
    execute_csv2_request(
        gvar, 1, None, 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'gtu1')),
        '/group/metadata-list/', group=ut_id(gvar, 'gtg5'),
        server_user=ut_id(gvar, 'gtu1')
    )

    # 3
    execute_csv2_request(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        '/group/metadata-list/', group='invalid-unit-test',
        server_user=ut_id(gvar, 'gtu3')
    )

    # 4
    execute_csv2_request(
        gvar, 1, None, 'cannot switch to invalid group "{}".'.format(ut_id(gvar, 'gtg7')),
        '/group/metadata-list/', group=ut_id(gvar, 'gtg7'),
        server_user=ut_id(gvar, 'gtu3')
    )

     # 5
    execute_csv2_request(
        gvar, 1, 'GV', 'request contained a bad parameter "invalid-unit-test".',
        '/group/metadata-list/', group=ut_id(gvar, 'gtg5'),
        form_data={'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'gtu3')
    )

    # 6
    execute_csv2_request(
        gvar, 0, None, None,
        '/group/metadata-list/', group=ut_id(gvar, 'gtg5'),
        expected_list='group_metadata_list', list_filter={'metadata_name': ut_id(gvar, 'gty4')},
        values={'metadata_name': ut_id(gvar, 'gty4'), 'group_name': ut_id(gvar, 'gtg5')},
        server_user=ut_id(gvar, 'gtu5')
    )

if __name__ == "__main__":
    main(None)
