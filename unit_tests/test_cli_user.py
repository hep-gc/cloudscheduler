from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id
from sys import argv

# lno: UV - error code identifier.

def main(gvar):
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
        ['cloudscheduler', 'user', 'list', '-su', ut_id(gvar, 'clu3')]
    )

    # set profile
    # 02
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'user', 'list', '-su', ut_id(gvar, 'clu4')]
    )

    # 03
    execute_csv2_command(
        gvar, 1, None, 'No action specified for object "user"; use -h or -H for help.',
        ['cloudscheduler', 'user', '-su', ut_id(gvar, 'clu4')]
    )

    # 04
    execute_csv2_command(
        gvar, 1, None, 'Invalid action "invalid-unit-test" for object "user"',
        ['cloudscheduler', 'user', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 05
    execute_csv2_command(
        gvar, None, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'user', '-s', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')], timeout=8
    )

    # 06
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler user".',
        ['cloudscheduler', 'user', '-h', '-su', ut_id(gvar, 'clu4')]
    )

    # 07
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'user', '-H', '-su', ut_id(gvar, 'clu4')]
    )

    #### ADD ####
    # 08
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'user', 'add', '-su', ut_id(gvar, 'clu4')]
    )

    # 09
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized',
        ['cloudscheduler', 'user', 'add', '-xx', 'yy', '-su', ut_id(gvar, 'clu4')]
    )

    # 10
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: group-option',
        ['cloudscheduler', 'user', 'add', '-go', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 11
    execute_csv2_command(
        gvar, None, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'user', 'add', '-s', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')], timeout=8
    )

    # 12
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler user add".',
        ['cloudscheduler', 'user', 'add', '-h', '-su', ut_id(gvar, 'clu4')]
    )

    # 13
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'user', 'add', '-H', '-su', ut_id(gvar, 'clu4')]
    )

    # 14
    execute_csv2_command(
        gvar, 1, None, 'Expose API requested',
        ['cloudscheduler', 'user', 'add', '-xA', '-su', ut_id(gvar, 'clu4')]
    )

    # 15
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'user', 'add', '-un', ut_id(gvar, 'cli-invalid-unit-test'), '-su', ut_id(gvar, 'clu4')]
    )

    # 16
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'user', 'add', '-ucn', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 17
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'user', 'add', '-upw', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 18
    execute_csv2_command(
        gvar, 1, 'UV', 'value specified for a password is less than 6 characters.',
        ['cloudscheduler', 'user', 'add', '-un', ut_id(gvar, 'cli-invalid-unit-test'), '-upw', 'test', '-ucn', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 19
    execute_csv2_command(
        gvar, 1, 'UV', 'value specified for a password is less then 16 characters, and does not contain a mixture of upper, lower, and numerics.',
        ['cloudscheduler', 'user', 'add', '-un', ut_id(gvar, 'cli-invalid-unit-test'), '-upw', 'invalid', '-ucn', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 20
    execute_csv2_command(
        gvar, 1, 'UV', 'value specified for "username" must be all lower case.',
        ['cloudscheduler', 'user', 'add', '-un', 'Invalid-Unit-Test', '-upw', 'invalid-unit-test', '-ucn', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 21
    execute_csv2_command(
        gvar, 1, 'UV', 'specified group "invalid-unit-test" does not exist.',
        ['cloudscheduler', 'user', 'add', '-un', ut_id(gvar, 'cli-invalid-unit-test'), '-upw', 'invalid-unit-test', '-ucn', 'invalid-unit-test', '-gn', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 22
    execute_csv2_command(
        gvar, 1, 'UV', 'Data too long for column \'username\' at row 1',
        ['cloudscheduler', 'user', 'add', '-un', 'thisisausernametoolongtoinsertint', '-upw', 'invalid-unit-test', '-ucn', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 23
    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'user', 'add', '-un', ut_id(gvar, 'cli-invalid-unit-test'), '-upw', 'invalid-unit-test', '-ucn', 'invalid-unit-test', '-g', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 24
    execute_csv2_command(
        gvar, 1, 'UV', 'username "{}" unavailable.'.format(ut_id(gvar, 'clu1')),
        ['cloudscheduler', 'user', 'add', '-un', ut_id(gvar, 'clu1'), '-upw', 'invalid-unit-test', '-ucn', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 25
    execute_csv2_command(
        gvar, 1, 'UV', 'username "{}" unavailable.'.format(ut_id(gvar, 'command line user one')),
        ['cloudscheduler', 'user', 'add', '-un', ut_id(gvar, 'command line user one'), '-upw', 'invalid-unit-test', '-ucn', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 26
    execute_csv2_command(
        gvar, 1, 'UV', 'common name "{0}" conflicts with registered user "{0}".'.format(ut_id(gvar, 'clu1')),
        ['cloudscheduler', 'user', 'add', '-un', ut_id(gvar, 'cli-invalid-unit-test'), '-upw', 'invalid-unit-test', '-ucn', ut_id(gvar, 'clu1'), '-su', ut_id(gvar, 'clu4')]
    )

    # 27
    execute_csv2_command(
        gvar, 1, 'UV', 'common name "{}" conflicts with registered user "{}".'.format(ut_id(gvar, 'command line user one'), ut_id(gvar, 'clu1')),
        ['cloudscheduler', 'user', 'add', '-un', ut_id(gvar, 'cli-invalid-unit-test'), '-upw', 'invalid-unit-test', '-ucn', ut_id(gvar, 'command line user one'), '-su', ut_id(gvar, 'clu4')]
    )

    # 28
    execute_csv2_command(
        gvar, 1, 'UV', 'user add, "{}" failed - group "{}" was specified twice.'.format(ut_id(gvar, 'cli-invalid-unit-test'), ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'user', 'add', '-un', ut_id(gvar, 'cli-invalid-unit-test'), '-upw', 'invalid-unit-test', '-ucn', 'invalid-unit-test', '-gn', ut_id(gvar, 'clg1,clg1'), '-su', ut_id(gvar, 'clu4')]
    )

    # 29
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'clu10')),
        ['cloudscheduler', 'user', 'add', '-un', ut_id(gvar, 'clu10'), '-upw', gvar['user_secret'], '-ucn', ut_id(gvar, 'command line user 10'), '-su', ut_id(gvar, 'clu4')]
    )

    # 30 We have to specify server and server password explicitly because -SU has to be the last parameter.
    execute_csv2_command(
        gvar, 1, None, 'Value omitted for option: -SU | --super-user',
        ['cloudscheduler', 'user', 'add', '-un', ut_id(gvar, 'clu11'), '-upw', gvar['user_secret'], '-ucn', ut_id(gvar, 'command line user 11'), '-s', 'unit-test', '-su', ut_id(gvar, 'clu4'), '-spw', gvar['user_secret'], '-SU']
    )

    # 31
    execute_csv2_command(
        gvar, 1, 'UV', 'boolean value specified for "is_superuser" must be one of the following: true, false, yes, no, 1, or 0.',
        ['cloudscheduler', 'user', 'add', '-un', ut_id(gvar, 'clu11'), '-upw', gvar['user_secret'], '-ucn', ut_id(gvar, 'command line user 11'), '-SU', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 32
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'clu11')),
        ['cloudscheduler', 'user', 'add', '-un', ut_id(gvar, 'clu11'), '-upw', gvar['user_secret'], '-ucn', ut_id(gvar, 'command line user 11'), '-SU', 'true', '-su', ut_id(gvar, 'clu4')]
    )

    # 33
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'clu12')),
        ['cloudscheduler', 'user', 'add', '-un', ut_id(gvar, 'clu12'), '-upw', gvar['user_secret'], '-ucn', ut_id(gvar, 'command line user 12'), '-gn', ut_id(gvar, 'clg5'), '-su', ut_id(gvar, 'clu4')]
    )

    # 34
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'clu13')),
        ['cloudscheduler', 'user', 'add', '-un', ut_id(gvar, 'clu13'), '-upw', gvar['user_secret'], '-ucn', ut_id(gvar, 'command line user 13'), '-gn', ut_id(gvar, 'clg1,clg5'), '-su', ut_id(gvar, 'clu4')]
    )

    #### DELETE ####
    # 35
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'user', 'delete', '-su', ut_id(gvar, 'clu4')]
    )

    # 36
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'user', 'delete', '-xx', 'yy', '-su', ut_id(gvar, 'clu4')]
    )

    # 37
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: group-option',
        ['cloudscheduler', 'user', 'delete', '-go', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 38
    execute_csv2_command(
        gvar, None, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'user', 'delete', '-s', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')], timeout=8
    )

    # 39
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler user delete".',
        ['cloudscheduler', 'user', 'delete', '-h', '-su', ut_id(gvar, 'clu4')]
    )

    # 40
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'user', 'delete', '-H', '-su', ut_id(gvar, 'clu4')]
    )

    # 41
    execute_csv2_command(
        gvar, 1, None, 'Expose API requested',
        ['cloudscheduler', 'user', 'delete', '-xA', '-su', ut_id(gvar, 'clu4')]
    )
    
    # 42
    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'user', 'delete', '-g', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 43 We have to specify the server and server password explicitly because -un has to be the last parameter.
    execute_csv2_command(
        gvar, 1, None, 'Value omitted for option: -un | --username',
        ['cloudscheduler', 'user', 'delete', '-s', 'unit-test', '-su', ut_id(gvar, 'clu4'), '-spw', gvar['user_secret'], '-un']
    )

    # 44
    execute_csv2_command(
        gvar, 1, None, 'cannot delete "invalid-unit-test", user doesn\'t exist.',
        ['cloudscheduler', 'user', 'delete', '-un', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 45
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully deleted.'.format(ut_id(gvar, 'clu5')),
        ['cloudscheduler', 'user', 'delete', '-un', ut_id(gvar, 'clu5'), '-Y', '-su', ut_id(gvar, 'clu4')]
    )

    # 46
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully deleted.'.format(ut_id(gvar, 'clu6')),
        ['cloudscheduler', 'user', 'delete', '-un', ut_id(gvar, 'clu6'), '-Y', '-su', ut_id(gvar, 'clu4')]
    )

    #### LIST ####
    # 47
    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'user', 'list', '-g', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 48
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'user', 'list', '-xx', 'yy', '-su', ut_id(gvar, 'clu4')]
    )

    # 49
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: group-option',
        ['cloudscheduler', 'user', 'list', '-go', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 50
    execute_csv2_command(
        gvar, None, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'user', 'list', '-s', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')], timeout=8
    )

    # 51
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'user', 'list', '-su', ut_id(gvar, 'clu4')],
        expected_list='Users', columns=['Username', 'Super User']
    )

    # 52
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler user list".',
        ['cloudscheduler', 'user', 'list', '-h', '-su', ut_id(gvar, 'clu4')]
    )

    # 53
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'user', 'list', '-H', '-su', ut_id(gvar, 'clu4')]
    )

    # 54
    execute_csv2_command(
        gvar, 0, None, 'Expose API requested',
        ['cloudscheduler', 'user', 'list', '-xA', '-su', ut_id(gvar, 'clu4')]
    )

    # 55
    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'cli-invalid-unit-test'), '-su', ut_id(gvar, 'clu4')]
    )

    # 56
    execute_csv2_command(
        gvar, 0, None, 'Rows: 1',
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'clu1'), '-su', ut_id(gvar, 'clu4')]
    )

    # 57
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'user', 'list', '-ok', '-su', ut_id(gvar, 'clu4')],
        expected_list='Users', columns=['Username']
    )

    # 58
    execute_csv2_command(
        gvar, 0, None, 'user list, 1. Users: keys=username, columns=cert_cn,active_group,user_groups,available_groups,is_superuser,join_date',
        ['cloudscheduler', 'user', 'list', '-VC', '-su', ut_id(gvar, 'clu4')]
    )

    # 59
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'user', 'list', '-NV', '-su', ut_id(gvar, 'clu4')],
        expected_list='Users', columns=['Username', 'Common Name', 'Active Group', 'User Groups', 'Username', 'Not In Groups', 'Super User', 'Joined']
    )

    # 60
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'user', 'list', '-V', 'is_superuser', '-su', ut_id(gvar, 'clu4')],
        expected_list='Users', columns=['Username', 'Super User']
    )

    # 61
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'user', 'list', '-r', '-su', ut_id(gvar, 'clu4')],
        expected_list='Users', columns=['Key', 'Value']
    )

    # 62
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'user', 'list', '-V', '', '-su', ut_id(gvar, 'clu4')],
        expected_list='Users', columns=['Username', 'Common Name', 'Active Group', 'User Groups', 'Username', 'Not In Groups', 'Super User', 'Joined']
    )

    #### UPDATE ####
    # 63
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'user', 'update', '-su', ut_id(gvar, 'clu4')]
    )

    # 64
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'user', 'update', '-xx', 'yy', '-su', ut_id(gvar, 'clu4')]
    )

    # 65
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: only-keys',
        ['cloudscheduler', 'user', 'update', '-ok', '-su', ut_id(gvar, 'clu4')]
    )

    # 66
    execute_csv2_command(
        gvar, None, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'user', 'update', '-s', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')], timeout=8
    )

    # 67
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'user', 'update', '-su', ut_id(gvar, 'clu4')]
    )

    # 68
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler user update".',
        ['cloudscheduler', 'user', 'update', '-h', '-su', ut_id(gvar, 'clu4')]
    )

    # 69
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'user', 'update', '-H', '-su', ut_id(gvar, 'clu4')]
    )

    # 70
    execute_csv2_command(
        gvar, 1, None, 'Expose API requested',
        ['cloudscheduler', 'user', 'update', '-xA', '-su', ut_id(gvar, 'clu4')]
    )

    # 71
    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'user', 'update', '-g', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 72
    execute_csv2_command(
        gvar, 1, None, '"cloudscheduler user update" requires at least one option to update.',
        ['cloudscheduler', 'user', 'update', '-un', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 73
    execute_csv2_command(
        gvar, 1, 'UV', 'the request did not match any rows.',
        ['cloudscheduler', 'user', 'update', '-un', 'invalid-unit-test', '-SU', 'yes', '-su', ut_id(gvar, 'clu4')]
    )

    # 74
    execute_csv2_command(
        gvar, 1, None, '"cloudscheduler user update" requires at least one option to update.',
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-su', ut_id(gvar, 'clu4')]
    )

    # 75
    execute_csv2_command(
        gvar, 1, 'UV', 'value specified for a password is less than 6 characters.',
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-upw', 'test', '-su', ut_id(gvar, 'clu4')]
    )

    # 76
    execute_csv2_command(
        gvar, 1, 'UV', 'value specified for a password is less then 16 characters, and does not contain a mixture of upper, lower, and numerics.',
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-upw', 'invalid', '-su', ut_id(gvar, 'clu4')]
    )

    # 77
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-ucn', '', '-su', ut_id(gvar, 'clu4')]
    )

    # 78
    execute_csv2_command(
        gvar, 1, 'UV', 'common name "{0}" conflicts with registered user "{0}".'.format(ut_id(gvar, 'clu1')),
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-ucn', ut_id(gvar, 'clu1'), '-su', ut_id(gvar, 'clu4')]
    )

    # 79
    execute_csv2_command(
        gvar, 1, 'UV', 'common name "{}" conflicts with registered user "{}".'.format(ut_id(gvar, 'command line user one'), ut_id(gvar, 'clu1')),
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-ucn', ut_id(gvar, 'command line user one'), '-su', ut_id(gvar, 'clu4')]
    )

    # 80
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-ucn', ut_id(gvar, 'command line user update'), '-su', ut_id(gvar, 'clu4')]
    )

    # 81 We have to specify server and server password explicitly because -SU has to be the last parameter.
    execute_csv2_command(
        gvar, 1, None, 'Value omitted for option: -SU | --super-user',
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-s', 'unit-test', '-su', ut_id(gvar, 'clu4'), '-spw', gvar['user_secret'], '-SU']
    )

    # 82
    execute_csv2_command(
        gvar, 1, 'UV', 'boolean value specified for "is_superuser" must be one of the following: true, false, yes, no, 1, or 0.',
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-SU', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 83
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-SU', 'yes', '-su', ut_id(gvar, 'clu4')]
    )

    # 84
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-SU', 'false', '-su', ut_id(gvar, 'clu4')]
    )

    # 85
    execute_csv2_command(
        gvar, 1, 'UV', 'value specified for "group_option" must be one of the following options: [\'add\', \'delete\'].',
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-go', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 86
    execute_csv2_command(
        gvar, 1, 'UV', 'user update must specify at least one field to update.',
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-go', 'add', '-su', ut_id(gvar, 'clu4')]
    )

    # 87
    execute_csv2_command(
        gvar, 1, 'UV', 'user update must specify at least one field to update.',
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-go', 'delete', '-su', ut_id(gvar, 'clu4')]
    )

    # 88
    execute_csv2_command(
        gvar, 0, None, 'user update, parameter "group_name" contains an empty string which is specifically disallowed.'.format(ut_id(gvar, 'clu7')),
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', '', '-su', ut_id(gvar, 'clu4')]
    )

    # 89
    execute_csv2_command(
        gvar, 1, 'UV', 'specified group "invalid-unit-test" does not exist.',
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 90
    execute_csv2_command(
        gvar, 1, 'UV', 'user update, "{}" failed - group "{}" was specified twice.'.format(ut_id(gvar, 'clu7'), ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', ut_id(gvar, 'clg1,clg1'), '-su', ut_id(gvar, 'clu4')]
    )

    # 91
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu4')]
    )

    # 92
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', ut_id(gvar, 'clg1'), '-go', 'delete', '-su', ut_id(gvar, 'clu4')]
    )

    # 93
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', ut_id(gvar, 'clg1'), '-go', 'add', '-su', ut_id(gvar, 'clu4')]
    )

    # 94
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', ut_id(gvar, 'clg5'), '-go', 'add', '-su', ut_id(gvar, 'clu4')]
    )

    # 95
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', ut_id(gvar, 'clg1,clg5'), '-go', 'delete', '-su', ut_id(gvar, 'clu4')]
    )

    # 96
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', ut_id(gvar, 'clg1,clg5'), '-su', ut_id(gvar, 'clu4')]
    )

    # 97
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu4')]
    )

    # 98
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', ut_id(gvar, 'clg1'), '-go', 'add', '-su', ut_id(gvar, 'clu4')]
    )

if __name__ == "__main__":
    main(None)

