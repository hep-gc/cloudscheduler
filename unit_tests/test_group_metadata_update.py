from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id
import sys

def main(gvar, user_secret):
    if not gvar:
        gvar = {}
        if len(sys.argv) > 1:
            initialize_csv2_request(gvar, sys.argv[0], selections=sys.argv[1])
        else:
            initialize_csv2_request(gvar, sys.argv[0])
    
    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 401, unauthorized.',
        '/group/metadata-update/',
        server_user='invalid-unit-test', server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'GV40', 'invalid method "GET" specified.',
        '/group/metadata-update/',
        server_user=ut_id(gvar, 'gtu1'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 403, forbidden.',
        '/group/metadata-update/', form_data={'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'gtu1'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'GV41', 'no metadata name specified.',
        '/group/metadata-update/', form_data={'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'GV39', 'group metadata-update "{}::invalid-unit-test" failed'.format(ut_id(gvar, 'gtg5')),
        '/group/metadata-update/', form_data={'metadata_name': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'GV38', 'request contained a bad parameter "invalid-unit-test".',
        '/group/metadata-update/', form_data={'metadata_name': 'invalid-unit-test', 'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'GV37', 'cannot switch to invalid group "invalid-unit-test".',
        '/group/metadata-update/', form_data={'metadata_name': 'invalid-unit-test', 'group': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'GV37', 'cannot switch to invalid group "testing".',
        '/group/metadata-update/', form_data={'metadata_name': 'invalid-unit-test', 'group': ut_id(gvar, 'gtg7')},
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'GV38', 'value specified for "metadata_name" must be all lower case.',
        '/group/metadata-update/', form_data={'metadata_name': 'Invalid-Unit-Test'},
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'GV38', 'boolean value specified for "enabled" must be one of the following: true, false, yes, no, 1, or 0.',
        '/group/metadata-update/', form_data={
            'metadata_name': 'invalid-unit-test',
            'enabled': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'GV38', 'value specified for "mime_type" must be one of the following options: [\'cloud-config\', \'ucernvm-config\'].',
        '/group/metadata-update/', form_data={
            'metadata_name': 'invalid-unit-test',
            'enabled': 0,
            'mime_type': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'GV39', '"{}::invalid-unit-test" failed - the request did not match any rows.'.format(ut_id(gvar, 'gtg5')),
        '/group/metadata-update/', form_data={
            'metadata_name': 'invalid-unit-test',
            'enabled': 0,
            'mime_type': 'cloud-config',
            'group': ut_id(gvar, 'gtg5')
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/group/metadata-list/', form_data={'group': ut_id(gvar, 'gtg5')},
        list='group_metadata_list', filter={'metadata_name': ut_id(gvar, 'gty5')},
        values={'metadata_name': ut_id(gvar, 'gty5'), 'enabled': 1, 'metadata': '- example: yaml', 'group_name': ut_id(gvar, 'gtg5'), 'priority': 0, 'mime_type': 'cloud-config'},
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, 'group metadata file "{}::{}" successfully  updated.'.format(ut_id(gvar, 'gtg5'), ut_id(gvar, 'gty5')),
        '/group/metadata-update/', form_data={
            'metadata_name': ut_id(gvar, 'gty5'),
            'enabled': 0,
            'mime_type': 'ucernvm-config',
            'metadata': '- example: metadata',
            'priority': 10,
            'group': ut_id(gvar, 'gtg5')
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/group/metadata-list/', form_data={'group': ut_id(gvar, 'gtg5')},
        list='group_metadata_list', filter={'metadata_name': ut_id(gvar, 'gty5')},
        values={'metadata_name': ut_id(gvar, 'gty5'), 'enabled': 0, 'metadata': '- example: metadata', 'group_name': ut_id(gvar, 'gtg5'), 'priority': 10, 'mime_type': 'ucernvm-config'},
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'GV38', 'yaml value specified for "metadata (metadata_name)" is invalid - scanner error',
        '/group/metadata-update/', form_data={
            'metadata_name': ut_id(gvar, 'gty5.yaml'),
            'enabled': 0,
            'mime_type': 'ucernvm-config',
            'metadata': 'foo: somebody said I should put a colon here: so I did',
            'priority': 10,
            'group': ut_id(gvar, 'gtg5')
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, 'group metadata file "{}::{}" successfully  updated.'.format(ut_id(gvar, 'gtg5'), ut_id(gvar, 'gty5.yaml')),
        '/group/metadata-update/', form_data={
            'metadata_name': ut_id(gvar, 'gty5.yaml'),
            'enabled': 0,
            'mime_type': 'ucernvm-config',
            'metadata': '- example: valid-yaml',
            'priority': 10,
            'group': ut_id(gvar, 'gtg5')
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

if __name__ == "__main__":
    main(None)