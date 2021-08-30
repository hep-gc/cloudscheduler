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
    sanity_requests(gvar, '/group/metadata-delete/', ut_id(gvar, 'gtg4'), ut_id(gvar, 'gtu5'), ut_id(gvar, 'gtg7'), ut_id(gvar, 'gtu2'))

    parameters = {
        # 06 Send a GET request.
        # 07 Give an invalid parameter.
        # 08 Give two metadata_names.
        # 09
        'metadata_name': {'valid': ut_id(gvar, 'gty6'), 'test_cases': {'invalid-unit-test': 'file "{}::invalid-unit-test" does not exist.'.format(ut_id(gvar, 'gtg5'))},'mandatory': True}
    }

    parameters_requests(gvar, '/group/metadata-delete/', ut_id(gvar, 'gtg5'), ut_id(gvar, 'gtu5'), parameters)

    # 10
    execute_csv2_request(
        gvar, 0, None, 'file "{}::{}" successfully deleted.'.format(ut_id(gvar, 'gtg5'), ut_id(gvar, 'gty6')),
        '/group/metadata-delete/', group=ut_id(gvar, 'gtg5'), form_data={'metadata_name': ut_id(gvar, 'gty6')},
        server_user=ut_id(gvar, 'gtu3')
    )

    # Deleting group metadata that is in a cloud's exceptions list should remove it from that list.
    # 11
    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/list/', group=ut_id(gvar, 'gtg5'), expected_list='cloud_list',
        list_filter={'group_name': ut_id(gvar, 'gtg5'), 'cloud_name': ut_id(gvar, 'gtc1')}, values={'group_exclusions': ut_id(gvar, 'gty4')},
        server_user=ut_id(gvar, 'gtu3')
    )

if __name__ == "__main__":
    main(None)
