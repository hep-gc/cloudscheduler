from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id
import sys

def main(gvar):
    if not gvar:
        gvar = {}
        if len(sys.argv) > 1:
            initialize_csv2_request(gvar, sys.argv[0], selections=sys.argv[1])
        else:
            initialize_csv2_request(gvar, sys.argv[0])

    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 401, unauthorized.',
        '/group/metadata-add/',
        server_user='invalid-unit-test', server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'GV29', 'invalid method "GET" specified.',
        '/group/metadata-add/',
        server_user=ut_id(gvar, 'gtu1'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 403, forbidden.',
        '/group/metadata-add/', form_data={'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'gtu1'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 403, forbidden.',
        '/group/metadata-add/', form_data={'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'gtu2'), server_pw='Abc123'
    )
    
    execute_csv2_request(
        gvar, 1, 'GV30', 'no group name specified.',
        '/group/metadata-add/', form_data={'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'gtu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'GV26', 'cannot switch to invalid group "invalid-unit-test".',
        '/group/metadata-add/', form_data={
            'metadata_name': 'invalid-unit-test',
            'group': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'GV26', 'cannot switch to invalid group "testing".',
        '/group/metadata-add/', form_data={
            'metadata_name': 'invalid-unit-test',
            'group': 'testing'
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'GV27', 'value specified for "metadata_name" must be all lower case.',
        '/group/metadata-add/', form_data={
            'group': ut_id(gvar, 'gtg4'),
            'metadata_name': 'Invalid-Unit-Test'
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'GV27', 'boolean value specified for "enabled" must be one of the following: true, false, yes, no, 1, or 0.',
        '/group/metadata-add/', form_data={
            'group': ut_id(gvar, 'gtg4'),
            'metadata_name': 'invalid-unit-test',
            'enabled': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'GV27', 'value specified for "mime_type" must be one of the following options: [\'cloud-config\', \'ucernvm-config\'].',
        '/group/metadata-add/', form_data={
            'group': ut_id(gvar, 'gtg4'),
            'metadata_name': 'invalid-unit-test',
            'enabled': 0,
            'mime_type': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'GV28', 'Field \'metadata\' doesn\'t have a default value',
        '/group/metadata-add/', form_data={
            'group': ut_id(gvar, 'gtg4'),
            'metadata_name': 'invalid-unit-test',
            'enabled': 0,
            'mime_type': 'cloud-config'
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw='Abc123'
    )

    # TODO: maybe this should be checked before insertion into db?
    execute_csv2_request(
        gvar, 1, 'GV28', 'Incorrect integer value: \'invalid-unit-test\' for column \'priority\' at row 1',
        '/group/metadata-add/', form_data={
            'group': ut_id(gvar, 'gtg4'),
            'metadata_name': 'invalid-unit-test',
            'enabled': 0,
            'mime_type': 'cloud-config',
            'metadata': 'invalid-unit-test',
            'priority': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw='Abc123'
    )

    # TODO: I thought files with .metadata endings were being validated as metadata
    # execute_csv2_request(
    #     gvar, 1, '???', '???',
    #     '/group/metadata-add/', form_data={
    #         'group': ut_id(gvar, 'gtg4'),
    #         'metadata_name': 'invalid-unit-test.metadata',
    #         'enabled': 0,
    #         'mime_type': 'cloud-config',
    #         'metadata': '{"invalid-unit-test":"yes"}',
    #         'priority': 1
    #     },
    #     server_user=ut_id(gvar, 'gtu3'), server_pw='Abc123'
    # )

    execute_csv2_request(
        gvar, 0, None, 'file "{}::{}" successfully added.'.format(ut_id(gvar, 'gtg4'), ut_id(gvar, 'gty1')),
        '/group/metadata-add/', form_data={
            'group': ut_id(gvar, 'gtg4'),
            'metadata_name': ut_id(gvar, 'gty1'),
            'enabled': 0,
            'mime_type': 'cloud-config',
            'metadata': '- example: metadata',
            'priority': 1
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/group/list/',
        list='group_list', filter={'group_name': ut_id(gvar, 'gtg4')},
        values={'group_name': ut_id(gvar, 'gtg4'), 'metadata_names': ut_id(gvar, 'gty1')}
    )

    execute_csv2_request(
        gvar, 1, 'GV28', 'Duplicate entry \'{}-{}\' for key \'PRIMARY\''.format(ut_id(gvar, 'gtg4'), ut_id(gvar, 'gty1')),
        '/group/metadata-add/', form_data={
            'group': ut_id(gvar, 'gtg4'),
            'metadata_name': ut_id(gvar, 'gty1'),
            'enabled': 1,
            'mime_type': 'ucernvm-config',
            'metadata': '{"example": "not yaml"}',
            'priority': 0
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 0, None, 'file "{}::{}" successfully added.'.format(ut_id(gvar, 'gtg5'), ut_id(gvar, 'gty1')),
        '/group/metadata-add/', form_data={
            'group': ut_id(gvar, 'gtg5'),
            'metadata_name': ut_id(gvar, 'gty1'),
            'enabled': 0,
            'mime_type': 'cloud-config',
            'metadata': '- example: yaml',
            'priority': 1
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw='Abc123'
    )

if __name__ == "__main__":
    main(None)