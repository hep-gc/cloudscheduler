from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id
import sys

# lno: VV - error code identifier.

def main(gvar, user_secret):
    if not gvar:
        gvar = {}
        if len(sys.argv) > 1:
            initialize_csv2_request(gvar, sys.argv[0], selections=sys.argv[1])
        else:
            initialize_csv2_request(gvar, sys.argv[0])

    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 401, unauthorized.',
        '/vm/update/',
        server_user='invalid-unit-test', server_pw='invalid-unit-test'
    )

    execute_csv2_request(
        gvar, 1, None, 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'vtu1')),
        '/vm/update/',
        server_user=ut_id(gvar, 'vtu1'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, None, 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'vtu2')),
        '/vm/update/',
        server_user=ut_id(gvar, 'vtu2'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'VV05', 'invalid method "GET" specified.',
        '/vm/update/',
        server_user=ut_id(gvar, 'vtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'VV06', 'the vm-option is required and must be one of the following: [\'kill\', \'retire\', \'manctl\', \'sysctl\'].',
        '/vm/update/', form_data={'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'vtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        '/vm/update/', form_data={'group': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'vtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, None, 'cannot switch to invalid group "{}".'.format(ut_id(gvar, 'vtg2')),
        '/vm/update/', form_data={'group': ut_id(gvar, 'vtg2')},
        server_user=ut_id(gvar, 'vtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'VV06', "the vm-option is required and must be one of the following: ['kill', 'retire', 'manctl', 'sysctl'].",
        '/vm/update/', form_data={'group': ut_id(gvar, 'vtg1'), 'vm-option': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'vtu3'), server_pw=user_secret
    )

    # TODO: come back to this later, I don't think the functionality is there yet
    execute_csv2_request(
        gvar, 1, 'VV06', "the vm-option is required and must be one of the following: ['kill', 'retire', 'manctl', 'sysctl'].",
        '/vm/update/', form_data={'vm-option': 'sysctl', 'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'vtu3'), server_pw=user_secret
    )

if __name__ == "__main__":
    main(None)