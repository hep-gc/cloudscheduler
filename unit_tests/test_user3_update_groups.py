from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id
import sys

def main(gvar):
    if not gvar:
        gvar = {}
        if len(sys.argv) > 1:
            initialize_csv2_request(gvar, sys.argv[0], selections=sys.argv[1])
        else:
            initialize_csv2_request(gvar, sys.argv[0])
    
    # adding a group to a user that doesn't exit should fail
    execute_csv2_request(
        gvar, 1, 'UV21', '"%s" failed - the request did not match any rows.' % ut_id(gvar, 'utu8'),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu8'),
            'group_name.1': ut_id(gvar, 'utg1')
            }
        )

    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu8')},
        values=None
        )

    # adding a user with a group that doesn't exist should fail
    execute_csv2_request(
        gvar, 1, 'UV04', '"{}" failed - specified group "{}" does not exist.'.format(ut_id(gvar, 'utu1'), ut_id(gvar, 'utg4')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'utu1'),
            'password1': 'AaBbCc123',
            'password2': 'AaBbCc123',
            'group_name.1': ut_id(gvar, 'utg4'),
            'cert_cn': '%s test user one' % ut_id(gvar, 'unit')
            }
        )

    # adding a user with a list of groups, one which doesn't exist should fail
    execute_csv2_request(
        gvar, 1, 'UV04', '"{}" failed - specified group "{}" does not exist.'.format(ut_id(gvar, 'utu1'), ut_id(gvar, 'utg4')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'utu1'),
            'password1': 'AaBbCc123',
            'password2': 'AaBbCc123',
            'group_name.1': ut_id(gvar, 'utg2'),
            'group_name.2': ut_id(gvar, 'utg3'),
            'group_name.3': ut_id(gvar, 'utg4'),
            'cert_cn': '%s test user one' % ut_id(gvar, 'unit')
            }
        )
    
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu1')},
        values=None
        )
    
    # adding a user with a list of valid groups should succeed
    execute_csv2_request(
        gvar, 0, None, 'user "%s" successfully added.' % ut_id(gvar, 'utu1'),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'utu1'),
            'password1': 'AaBbCc123',
            'password2': 'AaBbCc123',
            'group_name.1': ut_id(gvar, 'utg2'),
            'group_name.2': ut_id(gvar, 'utg3'),
            'cert_cn': '%s test user one' % ut_id(gvar, 'unit')
            }
        )

    # user added with group list should be associated with those groups
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu1')},
        values={'user_groups': ut_id(gvar, 'utg2,utg3')}
        )

    execute_csv2_request(
        gvar, None, None, None,
        '/user/delete/', form_data={'username': ut_id(gvar, 'utu1')}
        )
    
    # adding a user with no groups should succeed
    execute_csv2_request(
        gvar, 0, None, 'user "%s" successfully added.' % ut_id(gvar, 'utu1'),
        '/user/add/', form_data={'username': ut_id(gvar, 'utu1'), 'password1': 'AaBbCc123', 'password2': 'AaBbCc123', 'cert_cn': '%s test user one' % ut_id(gvar, 'unit')}
        )

    # user added with no groups shouldn't have any groups
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu1')},
        values={'user_groups': None, 'is_superuser': 0}
        )

    # adding a group that doesn't exist should fail
    execute_csv2_request(
        gvar, 1, 'UV20', '"{}" failed - specified group "{}" does not exist.'.format(ut_id(gvar, 'utu1'), ut_id(gvar, 'utg4')),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu1'),
            'group_name.1': ut_id(gvar, 'utg4')
            } 
        )

    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu1')},
        values={'user_groups': None}
        )

    # adding a group that exists should succeed
    execute_csv2_request(
        gvar, 0, None, 'user "%s" successfully updated.' % ut_id(gvar, 'utu1'),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu1'),
            'group_name.1': ut_id(gvar, 'utg1')
            }
        )

    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu1')},
        values={'user_groups': ut_id(gvar, 'utg1')}
        )

    # adding a list of groups where one doesn't exist should fail
    execute_csv2_request(
        gvar, 1, 'UV20', '"{}" failed - specified group "{}" does not exist.'.format(ut_id(gvar, 'utu1'), ut_id(gvar, 'utg4')),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu1'),
            'group_name.1': ut_id(gvar, 'utg2'),
            'group_name.2': ut_id(gvar, 'utg4')
            }
        )

    # failed update shouldn't add any groups, valid or not
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu1')},
        values={'user_groups': ut_id(gvar, 'utg1')}
        )

    # adding a list of valid groups should succeed
    execute_csv2_request(
        gvar, 0, None, 'user "%s" successfully updated.' % ut_id(gvar, 'utu1'),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu1'),
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_name.2': ut_id(gvar, 'utg2'),
            'group_name.3': ut_id(gvar, 'utg3')
            }
        )

    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu1')},
        values={'user_groups': '{},{},{}'.format(ut_id(gvar, 'utg1'), ut_id(gvar, 'utg2'), ut_id(gvar, 'utg3'))}
        )
    
    # adding a group that the user is already in should be okay?
    execute_csv2_request(
        gvar, 0, None, 'user "%s" successfully updated.' % ut_id(gvar, 'utu1'),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu1'),
            'group_name.1': ut_id(gvar, 'utg1')
            }
        )

    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu1')},
        values={'user_groups': '{},{},{}'.format(ut_id(gvar, 'utg1'), ut_id(gvar, 'utg2'), ut_id(gvar, 'utg3'))}
        )
    
    # adding a list of valid groups that the user is already in should be okay?
    execute_csv2_request(
        gvar, 0, None, 'user "%s" successfully updated.' % ut_id(gvar, 'utu1'),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu1'),
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_name.2': ut_id(gvar, 'utg2')
            }
        )

    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu1')},
        values={'user_groups': '{},{},{}'.format(ut_id(gvar, 'utg1'), ut_id(gvar, 'utg2'), ut_id(gvar, 'utg3'))}
        )
    
    # removing a group that doesn't exist should fail
    execute_csv2_request(
        gvar, 1, 'UV20', '"{}" failed - specified group "{}" does not exist.'.format(ut_id(gvar, 'utu1'), ut_id(gvar, 'utg4')),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu1'),
            'group_name.1': ut_id(gvar, 'utg4'),
            'group_option': 'delete'
        }
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu1')},
        values={'user_groups': '{},{},{}'.format(ut_id(gvar, 'utg1'), ut_id(gvar, 'utg2'), ut_id(gvar, 'utg3'))}
        )

    # removing a group from a list should succeed
    execute_csv2_request(
        gvar, 0, None, 'user "%s" successfully updated.' % ut_id(gvar, 'utu1'),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu1'),
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_option': 'delete'
            }
        )
    
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu1')},
        values={'user_groups': '{},{}'.format(ut_id(gvar, 'utg2'), ut_id(gvar, 'utg3'))}
        )
    
    # removing a group that the user is not in should succeed
    execute_csv2_request(
        gvar, 0, None, 'user "%s" successfully updated.' % ut_id(gvar, 'utu1'),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu1'),
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_option': 'delete'
        }
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu1')},
        values={'user_groups': '{},{}'.format(ut_id(gvar, 'utg2'), ut_id(gvar, 'utg3'))}
    )

    # removing a list of groups from a user should succeed
    execute_csv2_request(
        gvar, 0, None, 'user "%s" successfully updated.' % ut_id(gvar, 'utu1'),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu1'),
            'group_name.1': ut_id(gvar, 'utg2'),
            'group_name.2': ut_id(gvar, 'utg3'),
            'group_option': 'delete'
            }
        )

    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu1')},
        values={'user_groups': None}
        )

    # adding an invalid group with the "add" group option should fail
    execute_csv2_request(
        gvar, 1, 'UV20', '"{}" failed - specified group "{}" does not exist.'.format(ut_id(gvar, 'utu1'), ut_id(gvar, 'utg4')),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu1'),
            'group_name.1': ut_id(gvar, 'utg4'),
            'group_option': 'add'
        }
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu1')},
        values={'user_groups': None}
        )

    # adding a list of groups with an invalid group with the "add" option should fail
    execute_csv2_request(
        gvar, 1, 'UV20', '"{}" failed - specified group "{}" does not exist.'.format(ut_id(gvar, 'utu1'), ut_id(gvar, 'utg4')),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu1'),
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_name.2': ut_id(gvar, 'utg4'),
            'group_name.3': ut_id(gvar, 'utg2'),
            'group_option': 'add'
        }
    )
    
    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu1')},
        values={'user_groups': None}
    )

    # adding a single group to a user with the "add" option should succeed
    execute_csv2_request(
        gvar, 0, None, 'user "%s" successfully updated.' % ut_id(gvar, 'utu1'),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu1'),
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_option': 'add'
        }
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu1')},
        values={'user_groups': ut_id(gvar, 'utg1')}
    )

    # adding multiple groups with the "add" option should succeed
    execute_csv2_request(
        gvar, 0, None, 'user "%s" successfully updated.' % ut_id(gvar, 'utu1'),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu1'),
            'group_name.1': ut_id(gvar, 'utg2'),
            'group_name.2': ut_id(gvar, 'utg3'),
            'group_option': 'add'
        }
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu1')},
        values={'user_groups': ut_id(gvar, 'utg1,utg2,utg3')}
    )

    # adding a group that the user is already in should be okay?
    execute_csv2_request(
        gvar, 0, None, 'user "%s" successfully updated.' % ut_id(gvar, 'utu1'),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu1'),
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_option': 'add'
        }
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu1')},
        values={'user_groups': ut_id(gvar, 'utg1,utg2,utg3')}
    )

    # adding a list of groups that the user is already in should be okay?
    execute_csv2_request(
        gvar, 0, None, 'user "%s" successfully updated.' % ut_id(gvar, 'utu1'),
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu1'),
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_name.2': ut_id(gvar, 'utg2'),
            'group_option': 'add'
        }
    )

    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu1')},
        values={'user_groups': ut_id(gvar, 'utg1,utg2,utg3')}
    )

    execute_csv2_request(
        gvar, 1, 'UV99', 'group-option "invalid-option" invalid, must be either "add" or "delete".',
        '/user/update/', form_data={
            'username': ut_id(gvar, 'utu2'),
            'group_name.1': ut_id(gvar, 'utg1'),
            'group_option': 'invalid-option'
            }
        )

    execute_csv2_request(
        gvar, 0, None, None,
        '/user/list/',
        list='user_list', filter={'username': ut_id(gvar, 'utu1')},
        values={'user_groups': ut_id(gvar, 'utg1,utg2,utg3')}
    )

if __name__ == "__main__":
    main(None)