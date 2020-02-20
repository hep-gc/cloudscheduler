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
        '/group/metadata-add/',
        server_user='invalid-unit-test'
    )

    # 02
    execute_csv2_request(
        gvar, 1, 'GV', 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'gtu1')),
        '/group/metadata-add/',
        server_user=ut_id(gvar, 'gtu1')
    )

    # 03
    execute_csv2_request(
        gvar, 1, 'GV', 'user "%s" is not a member of any group.' % ut_id(gvar, 'gtu1'),
        '/group/metadata-add/', form_data={'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'gtu1')
    )

    # 04
    execute_csv2_request(
        gvar, 1, 'GV', 'user "%s" is not a member of any group.' % ut_id(gvar, 'gtu2'),
        '/group/metadata-add/', form_data={'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'gtu2')
    )
    
    # 05
    execute_csv2_request(
        gvar, 1, 'GV', 'group metadata-add request did not contain mandatory parameter "metadata_name".',
        '/group/metadata-add/', form_data={'enabled': 1},
        server_user=ut_id(gvar, 'gtu3')
    )

    # 06
    execute_csv2_request(
        gvar, 1, 'GV', 'group metadata-add request contained a bad parameter "invalid-unit-test".',
        '/group/metadata-add/', form_data={
            'metadata_name': ut_id(gvar, 'group-md-invalid-unit-test'),
            'invalid-unit-test': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'gtu3')
    )

    # 07
    execute_csv2_request(
        gvar, 1, 'GV', 'cannot switch to invalid group "invalid-unit-test".',
        '/group/metadata-add/', group='invalid-unit-test', form_data={
            'metadata_name': ut_id(gvar, 'group-md-invalid-unit-test')
            },
        server_user=ut_id(gvar, 'gtu3')
    )

    # 08
    execute_csv2_request(
        gvar, 1, 'GV', 'cannot switch to invalid group "{}".'.format(ut_id(gvar, 'gtg7')),
        '/group/metadata-add/', group=ut_id(gvar, 'gtg7'), form_data={
            'metadata_name': ut_id(gvar, 'group-md-invalid-unit-test')
            },
        server_user=ut_id(gvar, 'gtu3')
    )

    # 09
    execute_csv2_request(
        gvar, 1, 'GV', 'value specified for "metadata_name" must be all lower case.',
        '/group/metadata-add/', group=ut_id(gvar, 'gtg4'), form_data={
            'metadata_name': 'Invalid-Unit-Test'
            },
        server_user=ut_id(gvar, 'gtu3')
    )

    # 10
    execute_csv2_request(
        gvar, 1, 'GV', 'boolean value specified for "enabled" must be one of the following: true, false, yes, no, 1, or 0.',
        '/group/metadata-add/', group=ut_id(gvar, 'gtg4'), form_data={
            'metadata_name': ut_id(gvar, 'group-md-invalid-unit-test'),
            'enabled': 'invalid-unit-test'
            },
        server_user=ut_id(gvar, 'gtu3')
    )

    # 11
    execute_csv2_request(
        gvar, 1, 'GV', 'value specified for "mime_type" must be one of the following options: [\'cloud-config\', \'ucernvm-config\'].',
        '/group/metadata-add/', group=ut_id(gvar, 'gtg4'), form_data={
            'metadata_name': ut_id(gvar, 'group-md-invalid-unit-test'),
            'enabled': 0,
            'mime_type': 'invalid-unit-test'
            },
        server_user=ut_id(gvar, 'gtu3')
    )

    # 12
    execute_csv2_request(
        gvar, 1, 'GV', 'Field \'metadata\' doesn\'t have a default value',
        '/group/metadata-add/', group=ut_id(gvar, 'gtg4'), form_data={
            'metadata_name': ut_id(gvar, 'group-md-invalid-unit-test'),
            'enabled': 0,
            'mime_type': 'cloud-config'
            },
        server_user=ut_id(gvar, 'gtu3')
    )

    # 13
    execute_csv2_request(
        gvar, 1, 'GV', 'value specified for "priority" must be an integer value.',
        '/group/metadata-add/', group=ut_id(gvar, 'gtg4'), form_data={
            'metadata_name': ut_id(gvar, 'group-md-invalid-unit-test'),
            'enabled': 0,
            'mime_type': 'cloud-config',
            'metadata': 'invalid-unit-test',
            'priority': 'invalid-unit-test'
            },
        server_user=ut_id(gvar, 'gtu3')
    )

    # 14
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

    # 15
    execute_csv2_request(
        gvar, 1, 'GV', 'group metadata-add parameter "metadata_name" contains an empty string which is specifically disallowed.',
        '/group/metadata-add/', group=ut_id(gvar, 'gtg5'), form_data={
            'metadata_name': '',
            'metadata': 'invalid-unit-test',
            },
        server_user=ut_id(gvar, 'gtu3')
    )

    # 16
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

    # 17
    execute_csv2_request(
        gvar, 0, None, 'file "{}::{}" successfully added.'.format(ut_id(gvar, 'gtg4'), ut_id(gvar, 'gty1.yaml')),
        '/group/metadata-add/', group=ut_id(gvar, 'gtg4'), form_data={
            'metadata_name': ut_id(gvar, 'gty1.yaml'),
            'enabled': 0,
            'mime_type': 'cloud-config',
            'metadata': '- example: metadata',
            'priority': 1
            },
        server_user=ut_id(gvar, 'gtu3')
    )

    # 18 Verify that 17 actually added metadata
    execute_csv2_request(
        gvar, 0, None, None,
        '/group/metadata-list/', group=ut_id(gvar, 'gtg4'), expected_list='group_metadata_list', list_filter={'metadata_name': ut_id(gvar, 'gty1.yaml')},
        values={'metadata_name': ut_id(gvar, 'gty1.yaml'),
            'group_name': ut_id(gvar, 'gtg4'),
            'enabled': 0,
            'mime_type': 'cloud-config',
            'metadata': '- example: metadata',
            'priority': 1
            },
        server_user=ut_id(gvar, 'gtu5')
    )

    # 19 Verify that 17 actually added metadata
    execute_csv2_request(
        gvar, 0, None, None,
        '/group/list/', expected_list='group_list', list_filter={'group_name': ut_id(gvar, 'gtg4')},
        values={'group_name': ut_id(gvar, 'gtg4'),
            'htcondor_fqdn': 'unit-test-group-four.ca',
            'htcondor_container_hostname': None,
            'htcondor_other_submitters': None,
            'metadata_names': ','.join(sorted([ut_id(gvar, 'gty1.yaml'),'default.yaml.j2']))
        },
        server_user=ut_id(gvar, 'gtu5')
    )

    # 20
    execute_csv2_request(
        gvar, 1, 'GV', 'Duplicate entry \'{}-{}\' for key \'PRIMARY\''.format(ut_id(gvar, 'gtg4'), ut_id(gvar, 'gty1.yaml')),
        '/group/metadata-add/', group=ut_id(gvar, 'gtg4'), form_data={
            'metadata_name': ut_id(gvar, 'gty1.yaml'),
            'enabled': 1,
            'mime_type': 'ucernvm-config',
            'metadata': '{"example": "not yaml"}',
            'priority': 0
            },
        server_user=ut_id(gvar, 'gtu3')
    )

    # 21
    execute_csv2_request(
        gvar, 1, 'GV', 'group metadata_add, invalid method "GET" specified.',
        '/group/metadata-add/',
        server_user=ut_id(gvar, 'gtu3')
    )

if __name__ == "__main__":
    main(None)
