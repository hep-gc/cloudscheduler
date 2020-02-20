from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id
from sys import argv

# lno: GV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)
    
    # 01
    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 401, unauthorized.',
        '/group/metadata-update/',
        server_user='invalid-unit-test'
    )

    # 02
    execute_csv2_request(
        gvar, 1, 'GV', 'user "%s" is not a member of any group.' % ut_id(gvar, 'gtu1'),
        '/group/metadata-update/',
        server_user=ut_id(gvar, 'gtu1')
    )

    # 03
    execute_csv2_request(
        gvar, 1, 'GV', 'user "%s" is not a member of any group.' % ut_id(gvar, 'gtu2'),
        '/group/metadata-update/', form_data={'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'gtu2')
    )

    # 04
    execute_csv2_request(
        gvar, 1, 'GV', 'group metadata-update request did not contain mandatory parameter "metadata_name".',
        '/group/metadata-update/', group=(ut_id(gvar, 'gtg5')), form_data={'enabled': 0},
        server_user=ut_id(gvar, 'gtu3')
    )

    # 05
    execute_csv2_request(
        gvar, 1, 'GV', 'group metadata-update "%s::invalid-unit-test" specified no fields to update and was ignored.' % ut_id(gvar, 'gtg4'),
        '/group/metadata-update/', group=(ut_id(gvar, 'gtg4')), form_data={'metadata_name': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'gtu3')
    )

    # 06
    execute_csv2_request(
        gvar, 1, 'GV', 'request contained a bad parameter "invalid-unit-test".',
        '/group/metadata-update/', group=(ut_id(gvar, 'gtg5')), form_data={'metadata_name': 'invalid-unit-test', 'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'gtu3')
    )

    # 07
    execute_csv2_request(
        gvar, 1, 'GV', 'cannot switch to invalid group "invalid-unit-test".',
        '/group/metadata-update/', group='invalid-unit-test', form_data={'metadata_name': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'gtu3')
    )

    # 08
    execute_csv2_request(
        gvar, 1, 'GV', 'cannot switch to invalid group "{}".'.format(ut_id(gvar, 'gtg7')),
        '/group/metadata-update/', group=ut_id(gvar, 'gtg7'), form_data={'metadata_name': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'gtu3')
    )

    # 09
    execute_csv2_request(
        gvar, 1, 'GV', 'value specified for "metadata_name" must be all lower case.',
        '/group/metadata-update/', group=(ut_id(gvar, 'gtg5')), form_data={'metadata_name': 'Invalid-Unit-Test'},
        server_user=ut_id(gvar, 'gtu3')
    )

    # 10
    execute_csv2_request(
        gvar, 1, 'GV', 'boolean value specified for "enabled" must be one of the following: true, false, yes, no, 1, or 0.',
        '/group/metadata-update/', group=(ut_id(gvar, 'gtg5')), form_data={
            'metadata_name': 'invalid-unit-test',
            'enabled': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'gtu3')
    )

    # 11
    execute_csv2_request(
        gvar, 1, 'GV', 'value specified for "mime_type" must be one of the following options: [\'cloud-config\', \'ucernvm-config\'].',
        '/group/metadata-update/', group=(ut_id(gvar, 'gtg5')), form_data={
            'metadata_name': 'invalid-unit-test',
            'enabled': 0,
            'mime_type': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'gtu3')
    )

    # 12
    execute_csv2_request(
        gvar, 1, 'GV', '"{}::invalid-unit-test" failed - the request did not match any rows.'.format(ut_id(gvar, 'gtg5')),
        '/group/metadata-update/', group=ut_id(gvar, 'gtg5'), form_data={
            'metadata_name': 'invalid-unit-test',
            'enabled': 0,
            'mime_type': 'cloud-config',
            },
        server_user=ut_id(gvar, 'gtu3')
    )

    # 13
    execute_csv2_request(
        gvar, 0, None, None,
        '/group/metadata-list/', group=ut_id(gvar, 'gtg5'), expected_list='group_metadata_list', list_filter={'metadata_name': ut_id(gvar, 'gty5')},
        values={'metadata_name': ut_id(gvar, 'gty5'), 'enabled': 1, 'metadata': '- example: yaml', 'group_name': ut_id(gvar, 'gtg5'), 'priority': 0, 'mime_type': 'cloud-config'},
        server_user=ut_id(gvar, 'gtu3')
    )

    # 14
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

    # 15
    execute_csv2_request(
        gvar, 0, None, None,
        '/group/metadata-list/', group=ut_id(gvar, 'gtg5'), expected_list='group_metadata_list', list_filter={'metadata_name': ut_id(gvar, 'gty5')},
        values={'metadata_name': ut_id(gvar, 'gty5'), 'enabled': 0, 'metadata': '- example: metadata', 'group_name': ut_id(gvar, 'gtg5'), 'priority': 10, 'mime_type': 'ucernvm-config'},
        server_user=ut_id(gvar, 'gtu3')
    )

    # 16
    execute_csv2_request(
        gvar, 1, 'GV', 'yaml value specified for "metadata (metadata_name)" is invalid - scanner error',
        '/group/metadata-update/', group=ut_id(gvar, 'gtg5'), form_data={
            'metadata_name': ut_id(gvar, 'gty5.yaml'),
            'enabled': 0,
            'mime_type': 'ucernvm-config',
            'metadata': 'foo: somebody said I should put a colon here: so I did',
            'priority': 10,
            },
        server_user=ut_id(gvar, 'gtu3')
    )

    # 17
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

if __name__ == "__main__":
    main(None)
