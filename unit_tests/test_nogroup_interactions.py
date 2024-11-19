from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, generate_secret, execute_csv2_command
from sys import argv

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)
    if not gvar['user_secret']:
        gvar['user_secret'] = generate_secret()

    NO_GROUP_ERROR_MSG = "The current user is not in any group, contact your system administrator"
    ATTEMPT_TO_DELETE_OWN_LAST_GROUP_MSG = "You cannot delete your own last group"
    # 01 interaction for superuser with no groups
    execute_csv2_request(
        gvar, 
        1, 
        None, 
        NO_GROUP_ERROR_MSG,
        '/user/list/',
        server_user=ut_id(gvar, 'ngu1')
    )

    # 02 interaction for regular user with no groups
    execute_csv2_request(
        gvar, 
        1, 
        None, 
        NO_GROUP_ERROR_MSG,
        '/user/list/',
        server_user=ut_id(gvar, 'ngu2')
    )

    # 03 superuser in ngg1 attempts to delete other users last group ngg2
    execute_csv2_command(
        gvar, 
        0, 
        None, 
        'group "{}" successfully deleted.'.format(ut_id(gvar, 'ngg2')),
        ['group', 'delete', '-gn', ut_id(gvar, 'ngg2'), '-Y', '-su', ut_id(gvar, 'ngu3')]
    )
    # 04 superuser in ngg1 attempts to delete own last group ngg1
    execute_csv2_command(
        gvar, 
        1, 
        None, 
        ATTEMPT_TO_DELETE_OWN_LAST_GROUP_MSG,
        ['group', 'delete', '-gn', ut_id(gvar, 'ngg1'), '-Y', '-su', ut_id(gvar, 'ngu3')]
    )
    return 0

if __name__ == '__main__':
    main(None)
