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
        gvar, 1, 'GV04', 'invalid method "GET" specified.',
        '/group/add/'
    )

    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 403, forbidden.',
        '/group/add/',
        server_user=ut_id(gvar, 'gtu1'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, None, 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'gtu2')),
        '/group/add/',
        server_user=ut_id(gvar, 'gtu2'), server_pw='Abc123'
    )

    execute_csv2_request(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        '/group/add/', form_data={'group': 'invalid-unit-test'}
    )

    execute_csv2_request(
        gvar, 1, 'GV01', 'request did not contain mandatory parameter "group_name".',
        '/group/add/', form_data={'condor_central_manager': 'invalid-unit-test'}
    )

    execute_csv2_request(
        gvar, 1, 'GV01', 'request contained a bad parameter "invalid-unit-test".',
        '/group/add/', form_data={'invalid-unit-test': 'invalid-unit-test'}
    )

    execute_csv2_request(
        gvar, 1, 'GV01', 'value specified for "group_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        '/group/add/', form_data={'group_name': ut_id(gvar, 'Gtg1')}
    )

    execute_csv2_request(
        gvar, 1, 'GV01', 'value specified for "group_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        '/group/add/', form_data={'group_name': ut_id(gvar, 'gtg1-')}
    )

    execute_csv2_request(
        gvar, 1, 'GV01', 'value specified for "group_name" must be all lower case, numeric digits, and dashes but cannot start or end with dashes.',
        '/group/add/', form_data={'group_name': ut_id(gvar, 'gtg!1')}
    )

    execute_csv2_request(
        gvar, 1, 'GV02', 'Data too long for column \'group_name\' at row 1',
        '/group/add/', form_data={'group_name': ut_id(gvar, 'thisisagroupnametoolongtoinsertintothedatabasethisisagroupnametoolongtoinsertintothedatabasethisisagroupnametoolongtoinsertintothedatabase')}
    )

    execute_csv2_request(
        gvar, 1, 'GV97', '"{}" failed - specified user "invalid-unit-test" does not exist.'.format(ut_id(gvar, 'gtg1')),
        '/group/add/', form_data={
            'username.1': 'invalid-unit-test',
            'group_name': ut_id(gvar, 'gtg1')
        }
    )

    execute_csv2_request(
        gvar, 1, 'GV01', 'value specified for "user_option" must be one of the following options: [\'add\', \'delete\'].',
        '/group/add/', form_data={
            'user_option': 'invalid-unit-test',
            'group_name': ut_id(gvar, 'gtg1')
        }
    )

    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'gtg1')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'gtg1'),
            'username.1': ut_id(gvar, 'gtu3')
        }
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/group/list/',
        list='group_list', filter={'group_name': ut_id(gvar, 'gtg1')},
        values={'group_name': ut_id(gvar, 'gtg1'), 'metadata_names': None, 'condor_central_manager': None}
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'gtu3')},
        values={'username': ut_id(gvar, 'gtu3'), 'user_groups': ut_id(gvar, 'gtg1,gtg4,gtg5')}
    )

    execute_csv2_request(
        gvar, 1, 'GV02', '"{0}" failed - (1062, "Duplicate entry \'{0}\' for key \'PRIMARY\'").'.format(ut_id(gvar, 'gtg1')),
        '/group/add/', form_data={'group_name': ut_id(gvar, 'gtg1')}
    )

    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'gtg2')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'gtg2'),
            'condor_central_manager': 'unit-test-group-two.ca'
        }
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/group/list/',
        list='group_list', filter={'group_name': ut_id(gvar, 'gtg2')},
        values={'group_name': ut_id(gvar, 'gtg2'), 'metadata_names': None, 'condor_central_manager': 'unit-test-group-two.ca'}
    )

    execute_csv2_request(
        gvar, 1, 'GV03', 'Incorrect integer value: \'invalid-unit-test\' for column \'job_cpus\' at row 1',
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'gtg3'),
            'condor_central_manager': 'unit-test-group-three.ca',
            'job_cpus': 'invalid-unit-test'
        }
    )

    execute_csv2_request(
        gvar, 1, 'GV03', 'Incorrect integer value: \'invalid-unit-test\' for column \'job_ram\' at row 1',
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'gtg3'),
            'condor_central_manager': 'unit-test-group-three.ca',
            'job_ram': 'invalid-unit-test'
        }
    )

    execute_csv2_request(
        gvar, 1, 'GV03', 'Incorrect integer value: \'invalid-unit-test\' for column \'job_disk\' at row 1',
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'gtg3'),
            'condor_central_manager': 'unit-test-group-three.ca',
            'job_disk': 'invalid-unit-test'
        }
    )

    execute_csv2_request(
        gvar, 1, 'GV03', 'Incorrect integer value: \'invalid-unit-test\' for column \'job_scratch\' at row 1',
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'gtg3'),
            'condor_central_manager': 'unit-test-group-three.ca',
            'job_scratch': 'invalid-unit-test'
        }
    )

    execute_csv2_request(
        gvar, 1, 'GV03', 'Incorrect integer value: \'invalid-unit-test\' for column \'job_swap\' at row 1',
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'gtg3'),
            'condor_central_manager': 'unit-test-group-three.ca',
            'job_swap': 'invalid-unit-test'
        }
    )

    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'gtg3')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'gtg3'),
            'condor_central_manager': 'unit-test-group-three.ca',
            'job_cpus': 1,
            'job_ram': 1,
            'job_disk': 1,
            'job_scratch': 1,
            'job_swap': 1
        }
    )


    

if __name__ == "__main__":
    main(None)