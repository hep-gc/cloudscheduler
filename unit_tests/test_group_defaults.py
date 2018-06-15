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
        '/group/defaults/',
        server_user=ut_id(gvar, 'invalid-unit-test'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'GV07', 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'gtu1')),
        '/group/defaults/',
        server_user=ut_id(gvar, 'gtu1'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/group/defaults/',
        server_user=ut_id(gvar, 'gtu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'GV07', 'cannot switch to invalid group "invalid-unit-test".',
        '/group/defaults/', form_data={'group': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'gtu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'GV07', 'cannot switch to invalid group "testing".',
        '/group/defaults/', form_data={'group': 'testing'},
        server_user=ut_id(gvar, 'gtu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'GV05', 'group defaults update "{}" failed'.format(ut_id(gvar, 'gtg4')),
        '/group/defaults/', form_data={'group': ut_id(gvar, 'gtg4')},
        server_user=ut_id(gvar, 'gtu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'GV06', 'request contained a bad parameter "invalid-unit-test".',
        '/group/defaults/', form_data={'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'gtu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'GV05', 'Incorrect integer value: \'invalid-unit-test\' for column \'job_cpus\' at row 1',
        '/group/defaults/', form_data={
            'group': ut_id(gvar, 'gtg4'),
            'job_cpus': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'GV05', 'Incorrect integer value: \'invalid-unit-test\' for column \'job_ram\' at row 1',
        '/group/defaults/', form_data={
            'group': ut_id(gvar, 'gtg4'),
            'job_ram': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'GV05', 'Incorrect integer value: \'invalid-unit-test\' for column \'job_disk\' at row 1',
        '/group/defaults/', form_data={
            'group': ut_id(gvar, 'gtg4'),
            'job_disk': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'GV05', 'Incorrect integer value: \'invalid-unit-test\' for column \'job_scratch\' at row 1',
        '/group/defaults/', form_data={
            'group': ut_id(gvar, 'gtg4'),
            'job_scratch': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, 'GV05', 'Incorrect integer value: \'invalid-unit-test\' for column \'job_swap\' at row 1',
        '/group/defaults/', form_data={
            'group': ut_id(gvar, 'gtg4'),
            'job_swap': 'invalid-unit-test'
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 0, None, '"{}" successfully updated.'.format(ut_id(gvar, 'gtg4')),
        '/group/defaults/', form_data={
            'group': ut_id(gvar, 'gtg4'),
            'job_cpus': 1,
            'job_ram': 1,
            'job_disk': 1,
            'job_scratch': 1,
            'job_swap': 1
        },
        server_user=ut_id(gvar, 'gtu3'), server_pw='Abc123'
    )

if __name__ == "__main__":
    main(None)