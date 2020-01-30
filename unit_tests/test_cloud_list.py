from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id
from sys import argv

# lno: CV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv2_request(gvar, argv[0])

    #1 
    execute_csv2_request(
        gvar, 2, None, 'HTTP response code 401, unauthorized.',
        '/cloud/list/', group=ut_id(gvar, 'ctg1'),
        server_user='invalid-unit-test'
    )

    #2
    execute_csv2_request(
        gvar, 1, None, 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'ctu1')),
        '/cloud/list/', group=ut_id(gvar, 'ctg1'),
        server_user=ut_id(gvar, 'ctu1')
    )

    #3
    execute_csv2_request(
        gvar, 1, None, 'user "{}" is not a member of any group.'.format(ut_id(gvar, 'ctu2')),
        '/cloud/list/', group=ut_id(gvar, 'ctg1'),
        server_user=ut_id(gvar, 'ctu2')
    )

    #4
    execute_csv2_request(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        '/cloud/list/', group='invalid-unit-test',
        server_user=ut_id(gvar, 'ctu3')
    )

    #5
    execute_csv2_request(
        gvar, 1, None, 'cannot switch to invalid group "{}".'.format(ut_id(gvar, 'ctg2')),
        '/cloud/list/', group=ut_id(gvar, 'ctg2'),
        server_user=ut_id(gvar, 'ctu3')
    )

    #6
    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/list/', group=ut_id(gvar, 'ctg1'),
        expected_list='cloud_list', list_filter={'cloud_name': ut_id(gvar, 'ctc2')},
        values={
            'cloud_name': ut_id(gvar, 'ctc2'),
            'group_name': ut_id(gvar, 'ctg1'),
            'authurl': 'unit-test-cloud-two.ca',
            'project': 'unit-test-cloud-two',
            'username': ut_id(gvar, 'ctu3'),
            'region': ut_id(gvar, 'ctc2-r'),
            'cloud_type': 'local',
            'cloud_priority': 0,
            'cacertificate': None,
            'user_domain_name': 'Default',
            'project_domain_name': '\'Default\'',
        },
        server_user=ut_id(gvar, 'ctu3')
    )

    #7
    execute_csv2_request(
        gvar, 1, 'CV', 'request contained a bad parameter "invalid-unit-test".',
        '/cloud/list/', group=(ut_id(gvar, 'ctg1')),
        form_data={'invalid-unit-test': 'invalid-unit-test'},
        server_user=ut_id(gvar, 'ctu3')
    )

    #8
    execute_csv2_request(
        gvar, 0, None, None,
        '/cloud/list/', group=ut_id(gvar, 'ctg1'),
        expected_list='cloud_list',
        server_user=ut_id(gvar, 'ctu3'), html=True
    )

if __name__ == "__main__":
    main(None)
