from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id
import sys

# lno: GV - error code identifier.

def main(gvar, user_secret):
    if not gvar:
        gvar = {}
        if len(sys.argv) > 1:
            initialize_csv2_request(gvar, sys.argv[0], selections=sys.argv[1])
        else:
            initialize_csv2_request(gvar, sys.argv[0])

    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 401, unauthorized.',
        '/group/metadata-add/',
        server_user='invalid-unit-test', server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'GV27', 'invalid method "GET" specified.',
        '/group/metadata-add/',
        server_user=ut_id(gvar, 'gtu1'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 403, forbidden.',
        '/group/metadata-add/', form_data={'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'gtu1'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 403, forbidden.',
        '/group/metadata-add/', form_data={'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'gtu2'), server_pw=user_secret
    )
    
    execute_csv2_request(
        gvar, 1, 'GV28', 'no metadata name specified.',
        '/group/metadata-add/', form_data={'enabled': 1},
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'GV25', 'group metadata-add request contained a bad parameter "invalid-unit-test".',
        '/group/metadata-add/', form_data={
            'metadata_name': ut_id(gvar, 'group-md-invalid-unit-test'),
            'invalid-unit-test': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'GV24', 'cannot switch to invalid group "invalid-unit-test".',
        '/group/metadata-add/', form_data={
            'metadata_name': ut_id(gvar, 'group-md-invalid-unit-test'),
            'group': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'GV24', 'cannot switch to invalid group "{}".'.format(ut_id(gvar, 'gtg7')),
        '/group/metadata-add/', form_data={
            'metadata_name': ut_id(gvar, 'group-md-invalid-unit-test'),
            'group': ut_id(gvar, 'gtg7')
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'GV25', 'value specified for "metadata_name" must be all lower case.',
        '/group/metadata-add/', form_data={
            'group': ut_id(gvar, 'gtg4'),
            'metadata_name': 'Invalid-Unit-Test'
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'GV25', 'boolean value specified for "enabled" must be one of the following: true, false, yes, no, 1, or 0.',
        '/group/metadata-add/', form_data={
            'group': ut_id(gvar, 'gtg4'),
            'metadata_name': ut_id(gvar, 'group-md-invalid-unit-test'),
            'enabled': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'GV25', 'value specified for "mime_type" must be one of the following options: [\'cloud-config\', \'ucernvm-config\'].',
        '/group/metadata-add/', form_data={
            'group': ut_id(gvar, 'gtg4'),
            'metadata_name': ut_id(gvar, 'group-md-invalid-unit-test'),
            'enabled': 0,
            'mime_type': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'GV26', 'Field \'metadata\' doesn\'t have a default value',
        '/group/metadata-add/', form_data={
            'group': ut_id(gvar, 'gtg4'),
            'metadata_name': ut_id(gvar, 'group-md-invalid-unit-test'),
            'enabled': 0,
            'mime_type': 'cloud-config'
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'GV25', 'value specified for "priority" must be a integer value.',
        '/group/metadata-add/', form_data={
            'group': ut_id(gvar, 'gtg4'),
            'metadata_name': ut_id(gvar, 'group-md-invalid-unit-test'),
            'enabled': 0,
            'mime_type': 'cloud-config',
            'metadata': 'invalid-unit-test',
            'priority': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'GV25', 'yaml value specified for "metadata (metadata_name)" is invalid - scanner error',
        '/group/metadata-add/', form_data={
            'group': ut_id(gvar, 'gtg4'),
            'metadata_name': 'invalid-unit-test.yaml',
            'enabled': 0,
            'mime_type': 'cloud-config',
            'metadata': 'foo: somebody said I should put a colon here: so I did',
            'priority': 1
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, 'file "{}::{}" successfully added.'.format(ut_id(gvar, 'gtg5'), ut_id(gvar, 'gty1')),
        '/group/metadata-add/', form_data={
            'group': ut_id(gvar, 'gtg5'),
            'metadata_name': ut_id(gvar, 'gty1'),
            'enabled': 0,
            'mime_type': 'cloud-config',
            'metadata': '{"not-yaml":"yes"}',
            'priority': 1
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, 'file "{}::{}" successfully added.'.format(ut_id(gvar, 'gtg4'), ut_id(gvar, 'gty1.yaml')),
        '/group/metadata-add/', form_data={
            'group': ut_id(gvar, 'gtg4'),
            'metadata_name': ut_id(gvar, 'gty1.yaml'),
            'enabled': 0,
            'mime_type': 'cloud-config',
            'metadata': '- example: metadata',
            'priority': 1
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/group/list/',
        list='group_list', filter={'group_name': ut_id(gvar, 'gtg4')},
        values={'group_name': ut_id(gvar, 'gtg4'), 'metadata_names': ut_id(gvar, 'gty1.yaml')}
    )

    execute_csv2_request(
        gvar, 1, 'GV26', 'Duplicate entry \'{}-{}\' for key \'PRIMARY\''.format(ut_id(gvar, 'gtg4'), ut_id(gvar, 'gty1.yaml')),
        '/group/metadata-add/', form_data={
            'group': ut_id(gvar, 'gtg4'),
            'metadata_name': ut_id(gvar, 'gty1.yaml'),
            'enabled': 1,
            'mime_type': 'ucernvm-config',
            'metadata': '{"example": "not yaml"}',
            'priority': 0
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, 'file "{}::{}" successfully added.'.format(ut_id(gvar, 'gtg5'), ut_id(gvar, 'gty1.yaml')),
        '/group/metadata-add/', form_data={
            'group': ut_id(gvar, 'gtg5'),
            'metadata_name': ut_id(gvar, 'gty1.yaml'),
            'enabled': 0,
            'mime_type': 'cloud-config',
            'metadata': '- example: yaml',
            'priority': 1
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/group/metadata-list/', form_data={'group': ut_id(gvar, 'gtg5')},
        list='group_metadata_list', filter={'metadata_name': ut_id(gvar, 'gty1.yaml')},
        values={'metadata_name': ut_id(gvar, 'gty1.yaml'), 'enabled': 0, 'metadata': '- example: yaml', 'group_name': ut_id(gvar, 'gtg5'), 'priority': 1, 'mime_type': 'cloud-config'},
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

if __name__ == "__main__":
    main(None)