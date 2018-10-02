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
        '/group/defaults/',
        server_user=ut_id(gvar, 'invalid-unit-test'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'GV08', 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'gtu1')),
        '/group/defaults/',
        server_user=ut_id(gvar, 'gtu1'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/group/defaults/',
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'GV08', 'cannot switch to invalid group "invalid-unit-test".',
        '/group/defaults/', form_data={'group': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'GV08', 'cannot switch to invalid group "{}".'.format(ut_id(gvar, 'gtg7')),
        '/group/defaults/', form_data={'group': ut_id(gvar, 'gtg7')},
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'GV06', 'group defaults update "{}" failed'.format(ut_id(gvar, 'gtg4')),
        '/group/defaults/', form_data={'group': ut_id(gvar, 'gtg4')},
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'GV07', 'request contained a bad parameter "invalid-unit-test".',
        '/group/defaults/', form_data={'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'GV07', 'group defaults update value specified for "job_cpus" must be an integer value.',
        '/group/defaults/', form_data={
            'group': ut_id(gvar, 'gtg4'),
            'job_cpus': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'GV07', 'group defaults update value specified for "job_ram" must be an integer value.',
        '/group/defaults/', form_data={
            'group': ut_id(gvar, 'gtg4'),
            'job_ram': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'GV07', 'group defaults update value specified for "job_disk" must be an integer value.',
        '/group/defaults/', form_data={
            'group': ut_id(gvar, 'gtg4'),
            'job_disk': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'GV07', 'request contained a rejected/bad parameter "job_scratch".',
        '/group/defaults/', form_data={
            'group': ut_id(gvar, 'gtg4'),
            'job_scratch': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'GV07', 'group defaults update value specified for "job_swap" must be an integer value.',
        '/group/defaults/', form_data={
            'group': ut_id(gvar, 'gtg4'),
            'job_swap': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'GV07', 'group defaults update value specified for "vm_keep_alive" must be an integer value.',
        '/group/defaults/', form_data={
            'group': ut_id(gvar, 'gtg4'),
            'vm_keep_alive': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 0, None, '"{}" successfully updated.'.format(ut_id(gvar, 'gtg4')),
        '/group/defaults/', form_data={
            'group': ut_id(gvar, 'gtg4'),
            'job_cpus': 1,
            'job_ram': 1,
            'job_disk': 1,
            'job_swap': 1,
            'vm_keep_alive': 1,
            'vm_flavor': '',
            'vm_image': '',
            'vm_network': '',
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'GV##', 'group defaults, "{0}" failed - specified item does not exist: vm_image=invalid-unit-test, group_name={0}.'.format(ut_id(gvar, 'gtg4')),
        '/group/defaults/', form_data={
            'group': ut_id(gvar, 'gtg4'),
            'vm_image': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'GV##', 'group defaults, "{0}" failed - specified item does not exist: vm_flavor=invalid-unit-test, group_name={0}.'.format(ut_id(gvar, 'gtg4')),
        '/group/defaults/', form_data={
            'group': ut_id(gvar, 'gtg4'),
            'vm_flavor': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

    execute_csv2_request(
        gvar, 1, 'GV##', 'group defaults, "{0}" failed - specified item does not exist: vm_network=invalid-unit-test, group_name={0}.'.format(ut_id(gvar, 'gtg4')),
        '/group/defaults/', form_data={
            'group': ut_id(gvar, 'gtg4'),
            'vm_network': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw=user_secret
    )

if __name__ == "__main__":
    main(None)