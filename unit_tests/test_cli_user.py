from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id
from sys import argv

# lno: UV - error code identifier.

def main(gvar, user_secret):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv2_request(gvar, argv[0])

    # set profile
    # 01
    execute_csv2_command(
        gvar, 1, None, 'You are not authorized to access object "user";',
        ['cloudscheduler', 'user', 'list', '-s', 'unit-test-un']
    )

    # set profile
    # 02
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'user', 'list', '-s', 'unit-test']
    )

    # 03
    execute_csv2_command(
        gvar, 1, None, 'No action specified for object "user"',
        ['cloudscheduler', 'user']
    )

    # 04
    execute_csv2_command(
        gvar, 1, None, 'Invalid action "invalid-unit-test" for object "user"',
        ['cloudscheduler', 'user', 'invalid-unit-test']
    )

    # 05
    execute_csv2_command(
        gvar, 1, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'user', '-s', 'invalid-unit-test']
    )

    # 06
    execute_csv2_command(
        gvar, 1, None, 'No action specified for object "user"; use -h or -H for help.',
        ['cloudscheduler', 'user', '-s', 'unit-test']
    )

    # 07
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler user".',
        ['cloudscheduler', 'user', '-h']
    )

    # 08
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'user', '-H']
    )

    #### ADD ####
    # 09
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'user', 'add']
    )

    # 10
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized',
        ['cloudscheduler', 'user', 'add', '-xx', 'yy']
    )

    # 11
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: group-option',
        ['cloudscheduler', 'user', 'add', '-go', 'invalid-unit-test']
    )

    # 12
    execute_csv2_command(
        gvar, 1, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'user', 'add', '-s', 'invalid-unit-test']
    )

    # 13
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'user', 'add', '-s', 'unit-test']
    )

    # 14
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler user add".',
        ['cloudscheduler', 'user', 'add', '-h']
    )

    # 15
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'user', 'add', '-H']
    )

    # 16
    execute_csv2_command(
        gvar, 1, None, 'Expose API requested',
        ['cloudscheduler', 'user', 'add', '-xA']
    )

    # 17
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'user', 'add', '-un', ut_id(gvar, 'cli-invalid-unit-test')]
    )

    # 18
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'user', 'add', '-ucn', 'invalid-unit-test']
    )

    # 19
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'user', 'add', '-upw', 'invalid-unit-test']
    )

    # 20
    execute_csv2_command(
        gvar, 1, 'UV', 'value specified for a password is less than 6 characters.',
        ['cloudscheduler', 'user', 'add', '-un', ut_id(gvar, 'cli-invalid-unit-test'), '-upw', 'test', '-ucn', 'invalid-unit-test']
    )

    # 21
    execute_csv2_command(
        gvar, 1, 'UV', 'value specified for a password is less then 16 characters, and does not contain a mixture of upper, lower, and numerics.',
        ['cloudscheduler', 'user', 'add', '-un', ut_id(gvar, 'cli-invalid-unit-test'), '-upw', 'invalid', '-ucn', 'invalid-unit-test']
    )

    # 22
    execute_csv2_command(
        gvar, 1, 'UV', 'value specified for "username" must be all lower case.',
        ['cloudscheduler', 'user', 'add', '-un', 'Invalid-Unit-Test', '-upw', 'invalid-unit-test', '-ucn', 'invalid-unit-test']
    )

    # 23
    execute_csv2_command(
        gvar, 1, 'UV', 'specified group "invalid-unit-test" does not exist.',
        ['cloudscheduler', 'user', 'add', '-un', ut_id(gvar, 'cli-invalid-unit-test'), '-upw', 'invalid-unit-test', '-ucn', 'invalid-unit-test', '-gn', 'invalid-unit-test']
    )

    # 24
    execute_csv2_command(
        gvar, 1, 'UV', r'Data too long for column \'username\' at row 1',
        ['cloudscheduler', 'user', 'add', '-un', 'thisisausernametoolongtoinsertint', '-upw', 'invalid-unit-test', '-ucn', 'invalid-unit-test']
    )

    # 25
    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'user', 'add', '-un', ut_id(gvar, 'cli-invalid-unit-test'), '-upw', 'invalid-unit-test', '-ucn', 'invalid-unit-test', '-g', 'invalid-unit-test']
    )

    # 26
    execute_csv2_command(
        gvar, 1, 'UV', 'username "{}" unavailable.'.format(ut_id(gvar, 'clu1')),
        ['cloudscheduler', 'user', 'add', '-un', ut_id(gvar, 'clu1'), '-upw', 'invalid-unit-test', '-ucn', 'invalid-unit-test']
    )

    # 27
    execute_csv2_command(
        gvar, 1, 'UV', 'username "{}" unavailable.'.format(ut_id(gvar, 'command line user one')),
        ['cloudscheduler', 'user', 'add', '-un', ut_id(gvar, 'command line user one'), '-upw', 'invalid-unit-test', '-ucn', 'invalid-unit-test']
    )

    # 28
    execute_csv2_command(
        gvar, 1, 'UV', 'common name "{0}" conflicts with registered user "{0}".'.format(ut_id(gvar, 'clu1')),
        ['cloudscheduler', 'user', 'add', '-un', ut_id(gvar, 'cli-invalid-unit-test'), '-upw', 'invalid-unit-test', '-ucn', ut_id(gvar, 'clu1')]
    )

    # 29
    execute_csv2_command(
        gvar, 1, 'UV', 'common name "{}" conflicts with registered user "{}".'.format(ut_id(gvar, 'command line user one'), ut_id(gvar, 'clu1')),
        ['cloudscheduler', 'user', 'add', '-un', ut_id(gvar, 'cli-invalid-unit-test'), '-upw', 'invalid-unit-test', '-ucn', ut_id(gvar, 'command line user one')]
    )

    # 30
    execute_csv2_command(
        gvar, 1, 'UV', 'user add, "{}" failed - group "{}" was specified twice.'.format(ut_id(gvar, 'cli-invalid-unit-test'), ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'user', 'add', '-un', ut_id(gvar, 'cli-invalid-unit-test'), '-upw', 'invalid-unit-test', '-ucn', 'invalid-unit-test', '-gn', ut_id(gvar, 'clg1,clg1')]
    )

    # 31
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'clu10')),
        ['cloudscheduler', 'user', 'add', '-un', ut_id(gvar, 'clu10'), '-upw', user_secret, '-ucn', ut_id(gvar, 'command line user 10')]
    )

    # 32
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-SU\']',
        ['cloudscheduler', 'user', 'add', '-un', ut_id(gvar, 'clu11'), '-upw', user_secret, '-ucn', ut_id(gvar, 'command line user 11'), '-SU']
    )

    # 33
    execute_csv2_command(
        gvar, 1, 'UV', 'boolean value specified for "is_superuser" must be one of the following: true, false, yes, no, 1, or 0.',
        ['cloudscheduler', 'user', 'add', '-un', ut_id(gvar, 'clu11'), '-upw', user_secret, '-ucn', ut_id(gvar, 'command line user 11'), '-SU', 'invalid-unit-test']
    )

    # 34
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'clu11')),
        ['cloudscheduler', 'user', 'add', '-un', ut_id(gvar, 'clu11'), '-upw', user_secret, '-ucn', ut_id(gvar, 'command line user 11'), '-SU', 'true']
    )

    # 35
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'clu12')),
        ['cloudscheduler', 'user', 'add', '-un', ut_id(gvar, 'clu12'), '-upw', user_secret, '-ucn', ut_id(gvar, 'command line user 12'), '-gn', ut_id(gvar, 'clg1')]
    )

    # 36
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'clu13')),
        ['cloudscheduler', 'user', 'add', '-un', ut_id(gvar, 'clu13'), '-upw', user_secret, '-ucn', ut_id(gvar, 'command line user 13'), '-gn', ut_id(gvar, 'clg1,clg2')]
    )

    #### DELETE ####
    # 37
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'user', 'delete']
    )

    # 38
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'user', 'delete', '-xx', 'yy']
    )

    # 39
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: group-option',
        ['cloudscheduler', 'user', 'delete', '-go', 'invalid-unit-test']
    )

    # 49
    execute_csv2_command(
        gvar, 1, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'user', 'delete', '-s', 'invalid-unit-test']
    )

    # 41
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'user', 'delete', '-s', 'unit-test']
    )

    # 42
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler user delete".',
        ['cloudscheduler', 'user', 'delete', '-h']
    )

    # 43
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'user', 'delete', '-H']
    )

    # 44
    execute_csv2_command(
        gvar, 1, None, 'Expose API requested',
        ['cloudscheduler', 'user', 'delete', '-xA']
    )
    
    # 45
    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'user', 'delete', '-g', 'invalid-unit-test']
    )

    # 46
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-un\']',
        ['cloudscheduler', 'user', 'delete', '-un']
    )

    # 47
    execute_csv2_command(
        gvar, 1, None, r'cannot delete "invalid-unit-test", user doesn\'t exist.',
        ['cloudscheduler', 'user', 'delete', '-un', 'invalid-unit-test']
    )

    # 48
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully deleted.'.format(ut_id(gvar, 'clu5')),
        ['cloudscheduler', 'user', 'delete', '-un', ut_id(gvar, 'clu5'), '-Y']
    )

    # 49
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully deleted.'.format(ut_id(gvar, 'clu6')),
        ['cloudscheduler', 'user', 'delete', '-un', ut_id(gvar, 'clu6'), '-Y']
    )

    #### LIST ####
    # 50
    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'user', 'list', '-g', 'invalid-unit-test']
    )

    # 51
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'user', 'list', '-xx', 'yy']
    )

    # 52
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: group-option',
        ['cloudscheduler', 'user', 'list', '-go', 'invalid-unit-test']
    )

    # 53
    execute_csv2_command(
        gvar, 1, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'user', 'list', '-s', 'invalid-unit-test']
    )

    # 54
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'user', 'list', '-s', 'unit-test']
    )

    # 55
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler user list".',
        ['cloudscheduler', 'user', 'list', '-h']
    )

    # 56
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'user', 'list', '-H']
    )

    # 57
    execute_csv2_command(
        gvar, 0, None, 'Expose API requested',
        ['cloudscheduler', 'user', 'list', '-xA']
    )

    # 58
    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'cli-invalid-unit-test')]
    )

    # 59
    execute_csv2_command(
        gvar, 0, None, 'Rows: 1',
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'clu1')]
    )

    # 60
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'user', 'list', '-ok'],
        list='Users', columns=['Username']
    )

    # 61
    execute_csv2_command(
        gvar, 0, None, 'user list, 1. Users: keys=username, columns=cert_cn,active_group,user_groups,available_groups,is_superuser,join_date',
        ['cloudscheduler', 'user', 'list', '-VC']
    )

    # 62
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'user', 'list', '-NV'],
        list='Users', columns=['Username', 'Common', 'Name', 'Active', 'Group', 'User', 'Groups', 'Username', 'Not', 'In', 'Groups', 'Super', 'User', 'Joined']
    )

    # 63
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'user', 'list', '-V', 'is_superuser'],
        list='Users', columns=['Username', 'Super', 'User']
    )

    # 64
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'user', 'list'],
        list='Users', columns=['Username', 'Super', 'User']
    )

    # 65
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'user', 'list', '-r'],
        list='Users', columns=['Key', 'Value']
    )

    # 66
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'user', 'list', '-V', ''],
        list='Users', columns=['Username', 'Common', 'Name', 'Active', 'Group', 'User', 'Groups', 'Username', 'Not', 'In', 'Groups', 'Super', 'User', 'Joined']
    )

    #### UPDATE ####
    # 67
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'user', 'update']
    )

    # 68
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'user', 'update', '-xx', 'yy']
    )

    # 69
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: only-keys',
        ['cloudscheduler', 'user', 'update', '-ok']
    )

    # 70
    execute_csv2_command(
        gvar, 1, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'user', 'update', '-s', 'invalid-unit-test']
    )

    # 71
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'user', 'update', '-s', 'unit-test']
    )

    # 72
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler user update".',
        ['cloudscheduler', 'user', 'update', '-h']
    )

    # 73
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'user', 'update', '-H']
    )

    # 74
    execute_csv2_command(
        gvar, 1, None, 'Expose API requested',
        ['cloudscheduler', 'user', 'update', '-xA']
    )

    # 75
    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'user', 'update', '-g', 'invalid-unit-test']
    )

    # 76
    execute_csv2_command(
        gvar, 1, None, '"cloudscheduler user update" requires at least one option to update.',
        ['cloudscheduler', 'user', 'update', '-un', 'invalid-unit-test']
    )

    # 77
    execute_csv2_command(
        gvar, 1, 'UV', 'the request did not match any rows.',
        ['cloudscheduler', 'user', 'update', '-un', 'invalid-unit-test', '-SU', 'yes']
    )

    # 78
    execute_csv2_command(
        gvar, 1, None, '"cloudscheduler user update" requires at least one option to update.',
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7')]
    )

    # 79
    execute_csv2_command(
        gvar, 1, 'UV', 'value specified for a password is less than 6 characters.',
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-upw', 'test']
    )

    # 80
    execute_csv2_command(
        gvar, 1, 'UV', 'value specified for a password is less then 16 characters, and does not contain a mixture of upper, lower, and numerics.',
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-upw', 'invalid']
    )

    # 81
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-ucn', '']
    )

    # 82
    execute_csv2_command(
        gvar, 1, 'UV', 'common name "{0}" conflicts with registered user "{0}".'.format(ut_id(gvar, 'clu1')),
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-ucn', ut_id(gvar, 'clu1')]
    )

    # 83
    execute_csv2_command(
        gvar, 1, 'UV', 'common name "{}" conflicts with registered user "{}".'.format(ut_id(gvar, 'command line user one'), ut_id(gvar, 'clu1')),
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-ucn', ut_id(gvar, 'command line user one')]
    )

    # 84
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-ucn', ut_id(gvar, 'command line user update')]
    )

    # 85
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-SU\']',
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-SU']
    )

    # 86
    execute_csv2_command(
        gvar, 1, 'UV', 'boolean value specified for "is_superuser" must be one of the following: true, false, yes, no, 1, or 0.',
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-SU', 'invalid-unit-test']
    )

    # 87
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-SU', 'yes']
    )

    # 88
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-SU', 'false']
    )

    # 89
    execute_csv2_command(
        gvar, 1, 'UV', r'value specified for "group_option" must be one of the following options: [\'add\', \'delete\'].',
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-go', 'invalid-unit-test']
    )

    # 90
    execute_csv2_command(
        gvar, 1, 'UV', 'user update must specify at least one field to update.',
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-go', 'add']
    )

    # 91
    execute_csv2_command(
        gvar, 1, 'UV', 'user update must specify at least one field to update.',
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-go', 'delete']
    )

    # TODO: is this expected?
    # 92
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', '']
    )

    # 93
    execute_csv2_command(
        gvar, 1, 'UV', 'specified group "invalid-unit-test" does not exist.',
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', 'invalid-unit-test']
    )

    # 94
    execute_csv2_command(
        gvar, 1, 'UV', 'user update, "{}" failed - group "{}" was specified twice.'.format(ut_id(gvar, 'clu7'), ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', ut_id(gvar, 'clg1,clg1')]
    )

    # 95
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', ut_id(gvar, 'clg1')]
    )


    # 96
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', ut_id(gvar, 'clg1'), '-go', 'delete']
    )

    # 97
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', ut_id(gvar, 'clg1'), '-go', 'add']
    )

    # 98
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', ut_id(gvar, 'clg2'), '-go', 'add']
    )

    # 99
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', ut_id(gvar, 'clg1,clg2'), '-go', 'delete']
    )

    # 100
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', ut_id(gvar, 'clg1,clg2')]
    )

    # 101
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', ut_id(gvar, 'clg1')]
    )

    # 102
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', ut_id(gvar, 'clg1'), '-go', 'add']
    )

if __name__ == "__main__":
    main(None)

