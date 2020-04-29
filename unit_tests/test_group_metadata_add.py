from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, sanity_requests, parameters_requests
from sys import argv

# lno: GV - error code identifier.

def main(gvar):

    # 01 - 05
    sanity_requests(gvar, '/group/metadata-add/', ut_id(gvar, 'gtg4'), ut_id(gvar, 'gtu3'), ut_id(gvar, 'gtg7'), ut_id(gvar, 'gtu1'))

    parameters = {
        # 06 Send a GET request.
        # 07 Give an invalid parameter.
        # 08 Omit metadata_name.
        # 09 Give two metadata_names.
        'metadata_name': {'valid': 'invalid-unit-test', 'test_cases': {
            # 10
            '': 'group metadata-add value specified for "metadata_name" must not be the empty string.',
            # 11
            'Invalid-Unit-Test': 'group metadata-add value specified for "metadata_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 12
            'invalid-unit-test-': 'group metadata-add value specified for "metadata_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 13
            'invalid-unit--test': 'group metadata-add value specified for "metadata_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 14
            'invalid-unit-test!': 'group metadata-add value specified for "metadata_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 15
            'metadata-name-that-is-too-long-for-the-database_________________________': 'Data too long for column \'metadata_name\''
        }, 'mandatory': True},
        # 16 Omit metadata.
        # 17 Give two metadata.
        'metadata': {'valid': 'invalid-unit-test', 'test_cases': {}, 'mandatory': True},
        # 18 Give two enableds.
        # 19
        'enabled': {'valid': 0, 'test_cases': {'invalid-unit-test': 'boolean value specified for "enabled" must be one of the following: true, false, yes, no, 1, or 0.'}},
        # 20 Give two mime_types.
        # 21
        'mime_type': {'valid': 'cloud-config', 'test_cases': {'invalid-unit-test': 'value specified for "mime_type" must be one of the following options: [\'cloud-config\', \'ucernvm-config\'].'}},
        # 22 Give two priorities.
        # 23
        'priority': {'valid': 0, 'test_cases': {'invalid-unit-test': 'value specified for "priority" must be an integer value.'}}
    }

    parameters_requests(gvar, '/group/metadata-add/', ut_id(gvar, 'gtg5'), ut_id(gvar, 'gtu3'), parameters)
    
    # 24
    execute_csv2_request(
        gvar, 1, 'GV', 'yaml value specified for "metadata (metadata_name)" is invalid - scanner error',
        '/group/metadata-add/', group=ut_id(gvar, 'gtg4'), form_data={
            'metadata_name': 'invalid-unit-test.yaml',
            'enabled': 0,
            'mime_type': 'cloud-config',
            'metadata': 'foo: somebody said I should put a colon here: so I did',
            'priority': 1
            },
        server_user=ut_id(gvar, 'gtu3')
    )

    # 25
    execute_csv2_request(
        gvar, 0, None, 'file "{}::{}" successfully added.'.format(ut_id(gvar, 'gtg5'), ut_id(gvar, 'gty1')),
        '/group/metadata-add/', group=ut_id(gvar, 'gtg5'), form_data={
            'metadata_name': ut_id(gvar, 'gty1'),
            'enabled': 0,
            'mime_type': 'cloud-config',
            'metadata': '{"not-yaml":"yes"}',
            'priority': 1
            },
        server_user=ut_id(gvar, 'gtu3')
    )

    # 26
    execute_csv2_request(
        gvar, 0, None, 'file "{}::{}" successfully added.'.format(ut_id(gvar, 'gtg5'), ut_id(gvar, 'gty1.yaml')),
        '/group/metadata-add/', group=ut_id(gvar, 'gtg5'), form_data={
            'metadata_name': ut_id(gvar, 'gty1.yaml'),
            'enabled': 0,
            'mime_type': 'cloud-config',
            'metadata': '- example: metadata',
            'priority': 1
            },
        server_user=ut_id(gvar, 'gtu3')
    )

    # 27 Verify that the above actually added metadata
    execute_csv2_request(
        gvar, 0, None, None,
        '/group/metadata-list/', group=ut_id(gvar, 'gtg5'), expected_list='group_metadata_list', list_filter={'metadata_name': ut_id(gvar, 'gty1.yaml')},
        values={'metadata_name': ut_id(gvar, 'gty1.yaml'),
            'group_name': ut_id(gvar, 'gtg5'),
            'enabled': 0,
            'mime_type': 'cloud-config',
            'metadata': '- example: metadata',
            'priority': 1
            },
        server_user=ut_id(gvar, 'gtu3')
    )

    # 28 Verify that the above actually added metadata
    execute_csv2_request(
        gvar, 0, None, None,
        '/group/list/', group=ut_id(gvar, 'gtg4'), expected_list='group_list', list_filter={'group_name': ut_id(gvar, 'gtg5')},
        values={'group_name': ut_id(gvar, 'gtg5'),
            'metadata_names': ','.join(sorted([ut_id(gvar, 'gty1'), ut_id(gvar, 'gty1.yaml'), ut_id(gvar, 'gty4'), ut_id(gvar, 'gty5'), ut_id(gvar, 'gty5.yaml'), ut_id(gvar, 'gty6'), 'default.yaml.j2']))
        },
        server_user=ut_id(gvar, 'gtu5')
    )

    # 29 Attempt to add metadata that a group already has.
    execute_csv2_request(
        gvar, 1, 'GV', 'Duplicate entry \'{}-{}\' for key \'PRIMARY\''.format(ut_id(gvar, 'gtg5'), ut_id(gvar, 'gty1.yaml')),
        '/group/metadata-add/', group=ut_id(gvar, 'gtg5'), form_data={
            'metadata_name': ut_id(gvar, 'gty1.yaml'),
            'enabled': 1,
            'mime_type': 'ucernvm-config',
            'metadata': '{"example": "not yaml"}',
            'priority': 0
            },
        server_user=ut_id(gvar, 'gtu3')
    )

if __name__ == "__main__":
    main(initialize_csv2_request(selections=argv[1] if len(argv) > 1 else ''))
