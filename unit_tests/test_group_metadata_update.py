from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, sanity_requests, parameters_requests
from sys import argv

# lno: GV - error code identifier.

def main(gvar):
    
    # 01 - 05
    sanity_requests(gvar, '/group/metadata-update/', ut_id(gvar, 'gtg4'), ut_id(gvar, 'gtu3'), ut_id(gvar, 'gtg7'), ut_id(gvar, 'gtu1'))

    parameters = {
        # 06 Send a GET request.
        # 07 Give a bad parameter.
        # 08 Omit metadata_name.
        # 09 Give two metadata_names.
        'metadata_name': {'valid': ut_id(gvar, 'gty5'), 'test_cases': {
            # 10
            '': 'group metadata-update value specified for "metadata_name" must not be the empty string.',
            # 11
            'invalid-unit-Test': 'group metadata-update value specified for "metadata_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 12
            'invalid-unit-test-': 'group metadata-update value specified for "metadata_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 13
            'invalid-unit-test!': 'group metadata-update value specified for "metadata_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
        }, 'mandatory': True},
        # 14 Give two enableds.
        # 15
        'enabled': {'valid': 0, 'test_cases': {'invalid-unit-test': 'boolean value specified for "enabled" must be one of the following: true, false, yes, no, 1, or 0.'}},
        # 16 Give two mime_types.
        # 17
        'mime_type': {'valid': 'cloud-config', 'test_cases': {'invalid-unit-test': 'value specified for "mime_type" must be one of the following options: [\'cloud-config\', \'ucernvm-config\'].'}}
    }

    parameters_requests(gvar, '/group/metadata-update/', ut_id(gvar, 'gtg5'), ut_id(gvar, 'gtu3'), parameters)

    # 18 Attempt to update metadata that does not exist.
    execute_csv2_request(
        gvar, 1, 'GV', '"{}::invalid-unit-test" failed - the request did not match any rows.'.format(ut_id(gvar, 'gtg5')),
        '/group/metadata-update/', group=ut_id(gvar, 'gtg5'), form_data={
            'metadata_name': 'invalid-unit-test',
            # We must specify at least one field to update.
            'enabled': 0
        },
        server_user=ut_id(gvar, 'gtu3')
    )

    # 19
    execute_csv2_request(
        gvar, 1, 'GV', 'group metadata-update "{}::{}" specified no fields to update and was ignored.'.format(ut_id(gvar, 'gtg5'), ut_id(gvar, 'gty5')),
        '/group/metadata-update/', group=ut_id(gvar, 'gtg5'), form_data={'metadata_name': ut_id(gvar, 'gty5')},
        server_user=ut_id(gvar, 'gtu3')
    )

    # 20 Ensure that values are as expected before updating.
    execute_csv2_request(
        gvar, 0, None, None,
        '/group/metadata-list/', group=ut_id(gvar, 'gtg5'), expected_list='group_metadata_list', list_filter={'group_name': ut_id(gvar, 'gtg5'), 'metadata_name': ut_id(gvar, 'gty5')},
        values={'enabled': 1, 'metadata': '- example: yaml', 'priority': 0, 'mime_type': 'cloud-config'},
        server_user=ut_id(gvar, 'gtu3')
    )

    # 21
    execute_csv2_request(
        gvar, 0, None, 'group metadata file "{}::{}" successfully  updated.'.format(ut_id(gvar, 'gtg5'), ut_id(gvar, 'gty5')),
        '/group/metadata-update/', group=ut_id(gvar, 'gtg5'), form_data={
            'metadata_name': ut_id(gvar, 'gty5'),
            'enabled': 0,
            'mime_type': 'ucernvm-config',
            'metadata': '- example: metadata',
            'priority': 10,
            },
        server_user=ut_id(gvar, 'gtu3')
    )

    # 22 Ensure that gty5 was updated properly.
    execute_csv2_request(
        gvar, 0, None, None,
        '/group/metadata-list/', group=ut_id(gvar, 'gtg5'), expected_list='group_metadata_list', list_filter={'group_name': ut_id(gvar, 'gtg5'), 'metadata_name': ut_id(gvar, 'gty5')},
        values={'enabled': 0, 'metadata': '- example: metadata', 'priority': 10, 'mime_type': 'ucernvm-config'},
        server_user=ut_id(gvar, 'gtu3')
    )

    # 23
    execute_csv2_request(
        gvar, 1, 'GV', 'yaml value specified for "metadata (metadata_name)" is invalid - scanner error',
        '/group/metadata-update/', group=ut_id(gvar, 'gtg5'), form_data={
            'metadata_name': ut_id(gvar, 'gty5.yaml'),
            'enabled': 0,
            'mime_type': 'ucernvm-config',
            'metadata': 'invalid: unit: test',
            'priority': 10,
            },
        server_user=ut_id(gvar, 'gtu3')
    )

    # 24
    execute_csv2_request(
        gvar, 0, None, 'group metadata file "{}::{}" successfully  updated.'.format(ut_id(gvar, 'gtg5'), ut_id(gvar, 'gty5.yaml')),
        '/group/metadata-update/', group=ut_id(gvar, 'gtg5'), form_data={
            'metadata_name': ut_id(gvar, 'gty5.yaml'),
            'enabled': 0,
            'mime_type': 'ucernvm-config',
            'metadata': '- example: valid-yaml',
            'priority': 10,
            },
        server_user=ut_id(gvar, 'gtu3')
    )

    # 25 Ensure that gty5.yaml was updated properly.
    execute_csv2_request(
        gvar, 0, None, None,
        '/group/metadata-list/', group=ut_id(gvar, 'gtg5'), expected_list='group_metadata_list', list_filter={'group_name': ut_id(gvar, 'gtg5'), 'metadata_name': ut_id(gvar, 'gty5.yaml')},
        values={'enabled': 0, 'mime_type': 'ucernvm-config', 'metadata': '- example: valid-yaml', 'priority': 10},
        server_user=ut_id(gvar, 'gtu3')
    )

if __name__ == "__main__":
    main(initialize_csv2_request(selections=argv[1] if len(argv) > 1 else ''))
