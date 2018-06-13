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
        '/group/metadata-update/',
        server_user='invalid-unit-test', server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'GV40', 'invalid method "GET" specified.',
        '/group/metadata-update/',
        server_user=ut_id(gvar, 'gtu1'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 403, forbidden.',
        '/group/metadata-update/', form_data={'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'gtu1'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'GV41', 'no group name specified.',
        '/group/metadata-update/', form_data={'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'gtu3'), server_pw='Abc123'
    )

    # TODO: this currently returns an SQL syntax error, should be something more user friendly
    execute_csv2_request(
        gvar, 1, 'GV39', '???',
        '/group/metadata-update/', form_data={'metadata_name': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'gtu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'GV38', 'request contained a bad parameter "invalid-unit-test".',
        '/group/metadata-update/', form_data={'metadata_name': 'invalid-unit-test', 'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'gtu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'GV37', 'cannot switch to invalid group "invalid-unit-test".',
        '/group/metadata-update/', form_data={'metadata_name': 'invalid-unit-test', 'group': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'gtu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'GV37', 'cannot switch to invalid group "testing".',
        '/group/metadata-update/', form_data={'metadata_name': 'invalid-unit-test', 'group': 'testing'},
        server_user=ut_id(gvar, 'gtu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'GV38', 'value specified for "metadata_name" must be all lower case.',
        '/group/metadata-update/', form_data={'metadata_name': 'Invalid-Unit-Test'},
        server_user=ut_id(gvar, 'gtu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'GV38', 'boolean value specified for "enabled" must be one of the following: true, false, yes, no, 1, or 0.',
        '/group/metadata-update/', form_data={
            'metadata_name': 'invalid-unit-test',
            'enabled': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'GV38', 'value specified for "mime_type" must be one of the following options: [\'cloud-config\', \'ucernvm-config\'].',
        '/group/metadata-update/', form_data={
            'metadata_name': 'invalid-unit-test',
            'enabled': 0,
            'mime_type': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'GV39', '"{}::invalid-unit-test" failed - the request did not match any rows.'.format(ut_id(gvar, 'gtg5')),
        '/group/metadata-update/', form_data={
            'metadata_name': 'invalid-unit-test',
            'enabled': 0,
            'mime_type': 'cloud-config',
            'group': ut_id(gvar, 'gtg5')
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw='Abc123'
    )

if __name__ == "__main__":
    main(None)