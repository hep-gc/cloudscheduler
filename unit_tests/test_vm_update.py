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
        gvar, 1, 'VV02', 'vm update request contained a bad parameter "invalid-unit-test".',
        '/vm/update/', form_data={'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'vtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        '/vm/update/', form_data={'group': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'vtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'VV02', 'vm update request did not contain mandatory parameter "vm_option".',
        '/vm/update/', form_data={'group': ut_id(gvar, 'vtg1')},
        server_user=ut_id(gvar, 'vtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, None, 'cannot switch to invalid group "{}".'.format(ut_id(gvar, 'vtg2')),
        '/vm/update/', form_data={'group': ut_id(gvar, 'vtg2')},
        server_user=ut_id(gvar, 'vtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'VV02', "vm update value specified for \"vm_option\" must be one of the following options: ['kill', 'manctl', 'retire', 'sysctl'].",
        '/vm/update/', form_data={'group': ut_id(gvar, 'vtg1'), 'vm_option': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'vtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, "vm update, VMs set to system control: 0.",
        '/vm/update/', form_data={'vm_option': 'sysctl'},
        server_user=ut_id(gvar, 'vtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, "vm update, VMs killed: 0.",
        '/vm/update/', form_data={'vm_option': 'kill'},
        server_user=ut_id(gvar, 'vtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, "vm update, VMs set to manual control: 0.",
        '/vm/update/', form_data={'vm_option': 'manctl'},
        server_user=ut_id(gvar, 'vtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, "vm update, VMs retired: 0.",
        '/vm/update/', form_data={'vm_option': 'retire'},
        server_user=ut_id(gvar, 'vtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'VV02', "vm update value specified for \"poller_status\" must be one of the following options: ['error', 'manual', 'native', 'other', 'retiring', 'running', 'unregistered'].",
        '/vm/update/', form_data={'vm_option': 'sysctl', 'poller_status': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'vtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, "vm update, VMs set to system control: 0.",
        '/vm/update/', form_data={'vm_option': 'sysctl', 'poller_status': 'error'},
        server_user=ut_id(gvar, 'vtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, "vm update, VMs set to system control: 0.",
        '/vm/update/', form_data={'vm_option': 'sysctl', 'cloud_name': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'vtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, "vm update, VMs set to system control: 0.",
        '/vm/update/', form_data={'vm_option': 'sysctl', 'hostname': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'vtu3'), server_pw=user_secret
    )

if __name__ == "__main__":
    main(None)
