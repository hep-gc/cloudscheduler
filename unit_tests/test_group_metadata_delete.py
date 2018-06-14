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
        '/group/metadata-delete/',
        server_user='invalid-unit-test', server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'GV34', 'invalid method "GET" specified.',
        '/group/metadata-delete/',
        server_user=ut_id(gvar, 'gtu1'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 403, forbidden.',
        '/group/metadata-delete/', form_data={'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'gtu1'), server_pw='Abc123'
    )

    # TODO: should a privileged user be able to add/delete metadata to a group they are not in?
    # execute_csv2_request(
    #     gvar, 1, '???', '???',
    #     '/group/metadata-delete/', form_data={'invalid-unit-test': 'invalid-unit-test'},
    #     server_user=ut_id(gvar, 'gtu2'), server_pw='Abc123'
    # )
    
    # TODO: should the error be "no metadata/meta name specified"?
    execute_csv2_request(
        gvar, 1, 'GV35', 'no group name specified.',
        '/group/metadata-delete/', form_data={'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'gtu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'GV32', 'request contained a bad parameter "invalid-unit-test".',
        '/group/metadata-delete/', form_data={
            'metadata_name': 'invalid-unit-test',
            'invalid-unit-test': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw='Abc123'
    )

    # TODO: 500
    execute_csv2_request(
        gvar, 1, 'GV18', '???',
        '/group/metadata-delete/', form_data={
            'metadata_name': 'invalid-unit-test',
            'group': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw='Abc123'
    )

    # TODO: 500
    execute_csv2_request(
        gvar, 1, 'GV18', '???',
        '/group/metadata-delete/', form_data={
            'metadata_name': 'invalid-unit-test',
            'group': 'testing'
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'GV33', '"{}::invalid-unit-test" failed - the request did not match any rows.'.format(ut_id(gvar, 'gtg5')),
        '/group/metadata-delete/', form_data={
            'metadata_name': 'invalid-unit-test',
            'group': ut_id(gvar, 'gtg5')
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 0, None, 'file "{}::{}" successfully deleted.'.format(ut_id(gvar, 'gtg5'), ut_id(gvar, 'gty5')),
        '/group/metadata-delete/', form_data={
            'metadata_name': ut_id(gvar, 'gty5'),
            'group': ut_id(gvar, 'gtg5')
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw='Abc123'
    )

if __name__ == "__main__":
    main(None)