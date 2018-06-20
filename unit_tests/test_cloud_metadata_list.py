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
        '/cloud/metadata-list/',
        server_user='invalid-unit-test', server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, None, 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'ctu1')),
        '/cloud/metadata-list/',
        server_user=ut_id(gvar, 'ctu1'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, None, 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'ctu2')),
        '/cloud/metadata-list/',
        server_user=ut_id(gvar, 'ctu2'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        '/cloud/metadata-list/', form_data={'group': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, None, 'cannot switch to invalid group "{}".'.format(ut_id(gvar, 'ctg2')),
        '/cloud/metadata-list/', form_data={'group': ut_id(gvar, 'ctg2')},
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, None, 'metadata-list-option "invalid-unit-test" is invalid; only "merge" is valid.',
        '/cloud/metadata-list/', form_data={'metadata_list_option': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, '???', '???',
        '/cloud/metadata-list/', form_data={'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/metadata-list/', form_data={'metadata_list_option': 'merge'},
        list='cloud_metadata_list', filter={'cloud_name': ut_id(gvar, 'ctc2')},
        values={'metadata_name': ut_id(gvar, 'cty1'), 'cloud_name': ut_id(gvar, 'ctc2'), 'group_name': ut_id(gvar, 'ctg1')},
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/metadata-list/',
        list='cloud_metadata_list', filter={'metadata_name': ut_id(gvar, 'cty1')},
        values={'metadata_name': ut_id(gvar, 'cty1'), 'cloud_name': ut_id(gvar, 'ctc2'), 'group_name': ut_id(gvar, 'ctg1')},
        server_user=ut_id(gvar, 'ctu3'), server_pw='Abc123'
    )

if __name__ == "__main__":
    main(None)