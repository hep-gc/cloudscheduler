from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id
import sys

def main(gvar, user_secret):
    if not gvar:
        gvar = {}
        if len(sys.argv) > 1:
            initialize_csv2_request(gvar, sys.argv[0], selections=sys.argv[1])
        else:
            initialize_csv2_request(gvar, sys.argv[0])

    execute_csv2_command(
        gvar, 1, None, 'No action specified for object "user"',
        ['cloudscheduler', 'user']
    )

    execute_csv2_command(
        gvar, 1, None, 'Invalid action "invalid-unit-test" for object "user"',
        ['cloudscheduler', 'user', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'user settings for server "invalid-unit-test" does not contain a URL value.',
        ['cloudscheduler', 'user', '-s', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'No action specified for object "user"; use -h or -H for help.',
        ['cloudscheduler', 'user', '-s', 'unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler user".',
        ['cloudscheduler', 'user', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'user', '-H']
    )

    #### ADD ####
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'user', 'add']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized',
        ['cloudscheduler', 'user', 'add', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: group-option',
        ['cloudscheduler', 'user', 'add', '-go', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'user settings for server "invalid-unit-test" does not contain a URL value.',
        ['cloudscheduler', 'user', 'add', '-s', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'user', 'add', '-s', 'unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler user add".',
        ['cloudscheduler', 'user', 'add', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'user', 'add', '-H']
    )

    execute_csv2_command(
        gvar, 1, None, 'Expose API requested',
        ['cloudscheduler', 'user', 'add', '-xA']
    )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'user', 'add', '-un', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'user', 'add', '-ucn', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'user', 'add', '-upw', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'UV01', 'value specified for a password is less than 6 characters.',
        ['cloudscheduler', 'user', 'add', '-un', 'invalid-unit-test', '-upw', 'test', '-ucn', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'UV01', 'value specified for a password is less then 16 characters, and does not contain a mixture of upper, lower, and numerics.',
        ['cloudscheduler', 'user', 'add', '-un', 'invalid-unit-test', '-upw', 'invalid', '-ucn', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'UV01', 'value specified for "username" must be all lower case.',
        ['cloudscheduler', 'user', 'add', '-un', 'Invalid-Unit-Test', '-upw', 'invalid-unit-test', '-ucn', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'UV03', 'specified group "invalid-unit-test" does not exist.',
        ['cloudscheduler', 'user', 'add', '-un', 'invalid-unit-test', '-upw', 'invalid-unit-test', '-ucn', 'invalid-unit-test', '-gn', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'UV04', r'Data too long for column \'username\' at row 1',
        ['cloudscheduler', 'user', 'add', '-un', 'thisisausernametoolongtoinsertint', '-upw', 'invalid-unit-test', '-ucn', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'user', 'add', '-un', 'invalid-unit-test', '-upw', 'invalid-unit-test', '-ucn', 'invalid-unit-test', '-g', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'UV02', 'username "{}" unavailable.'.format(ut_id(gvar, 'clu1')),
        ['cloudscheduler', 'user', 'add', '-un', ut_id(gvar, 'clu1'), '-upw', 'invalid-unit-test', '-ucn', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'UV02', 'username "{}" unavailable.'.format(ut_id(gvar, 'command line user one')),
        ['cloudscheduler', 'user', 'add', '-un', ut_id(gvar, 'command line user one'), '-upw', 'invalid-unit-test', '-ucn', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'UV02', 'common name "{0}" conflicts with registered user "{0}".'.format(ut_id(gvar, 'clu1')),
        ['cloudscheduler', 'user', 'add', '-un', 'invalid-unit-test', '-upw', 'invalid-unit-test', '-ucn', ut_id(gvar, 'clu1')]
    )

    execute_csv2_command(
        gvar, 1, 'UV02', 'common name "{}" conflicts with registered user "{}".'.format(ut_id(gvar, 'command line user one'), ut_id(gvar, 'clu1')),
        ['cloudscheduler', 'user', 'add', '-un', 'invalid-unit-test', '-upw', 'invalid-unit-test', '-ucn', ut_id(gvar, 'command line user one')]
    )

    execute_csv2_command(
        gvar, 1, 'UV05', r'Duplicate entry \'invalid-unit-test-jodiew-clg1\' for key \'PRIMARY\'',
        ['cloudscheduler', 'user', 'add', '-un', 'invalid-unit-test', '-upw', 'invalid-unit-test', '-ucn', 'invalid-unit-test', '-gn', ut_id(gvar, 'clg1,clg1')]
    )

    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'clu10')),
        ['cloudscheduler', 'user', 'add', '-un', ut_id(gvar, 'clu10'), '-upw', user_secret, '-ucn', ut_id(gvar, 'command line user 10')]
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-SU\']',
        ['cloudscheduler', 'user', 'add', '-un', ut_id(gvar, 'clu11'), '-upw', user_secret, '-ucn', ut_id(gvar, 'command line user 11'), '-SU']
    )

    execute_csv2_command(
        gvar, 1, 'UV01', 'boolean value specified for "is_superuser" must be one of the following: true, false, yes, no, 1, or 0.',
        ['cloudscheduler', 'user', 'add', '-un', ut_id(gvar, 'clu11'), '-upw', user_secret, '-ucn', ut_id(gvar, 'command line user 11'), '-SU', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'clu11')),
        ['cloudscheduler', 'user', 'add', '-un', ut_id(gvar, 'clu11'), '-upw', user_secret, '-ucn', ut_id(gvar, 'command line user 11'), '-SU', 'true']
    )

    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'clu12')),
        ['cloudscheduler', 'user', 'add', '-un', ut_id(gvar, 'clu12'), '-upw', user_secret, '-ucn', ut_id(gvar, 'command line user 12'), '-gn', ut_id(gvar, 'clg1')]
    )

    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'clu13')),
        ['cloudscheduler', 'user', 'add', '-un', ut_id(gvar, 'clu13'), '-upw', user_secret, '-ucn', ut_id(gvar, 'command line user 13'), '-gn', ut_id(gvar, 'clg1,clg2')]
    )

    #### DELETE ####
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'user', 'delete']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'user', 'delete', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: group-option',
        ['cloudscheduler', 'user', 'delete', '-go', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'user settings for server "invalid-unit-test" does not contain a URL value.',
        ['cloudscheduler', 'user', 'delete', '-s', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'user', 'delete', '-s', 'unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler user delete".',
        ['cloudscheduler', 'user', 'delete', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'user', 'delete', '-H']
    )

    execute_csv2_command(
        gvar, 1, None, 'Expose API requested',
        ['cloudscheduler', 'user', 'delete', '-xA']
    )
    
    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'user', 'delete', '-g', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-un\']',
        ['cloudscheduler', 'user', 'delete', '-un']
    )

    execute_csv2_command(
        gvar, 1, None, r'cannot delete "invalid-unit-test", user doesn\'t exist.',
        ['cloudscheduler', 'user', 'delete', '-un', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully deleted.'.format(ut_id(gvar, 'clu5')),
        ['cloudscheduler', 'user', 'delete', '-un', ut_id(gvar, 'clu5')]
    )

    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully deleted.'.format(ut_id(gvar, 'clu6')),
        ['cloudscheduler', 'user', 'delete', '-un', ut_id(gvar, 'clu6')]
    )

    #### LIST ####
    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'user', 'list', '-g', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'user', 'list', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: group-option',
        ['cloudscheduler', 'user', 'list', '-go', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'user settings for server "invalid-unit-test" does not contain a URL value.',
        ['cloudscheduler', 'user', 'list', '-s', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'user', 'list', '-s', 'unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler user list".',
        ['cloudscheduler', 'user', 'list', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'user', 'list', '-H']
    )

    execute_csv2_command(
        gvar, 0, None, 'Expose API requested',
        ['cloudscheduler', 'user', 'list', '-xA']
    )

    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'user', 'list', '-un', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Rows: 1',
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'clu1')]
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'user', 'list', '-ok']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'user', 'list']
    )

    #### UPDATE ####
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'user', 'update']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'user', 'update', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: only-keys',
        ['cloudscheduler', 'user', 'update', '-ok']
    )

    execute_csv2_command(
        gvar, 1, None, 'user settings for server "invalid-unit-test" does not contain a URL value.',
        ['cloudscheduler', 'user', 'update', '-s', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'user', 'update', '-s', 'unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler user update".',
        ['cloudscheduler', 'user', 'update', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'user', 'update', '-H']
    )

    execute_csv2_command(
        gvar, 1, None, 'Expose API requested',
        ['cloudscheduler', 'user', 'update', '-xA']
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'user', 'update', '-g', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'UV22', 'the request did not match any rows.',
        ['cloudscheduler', 'user', 'update', '-un', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'UV##', 'nothing to update',
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7')]
    )

    execute_csv2_command(
        gvar, 1, 'UV19', 'value specified for a password is less than 6 characters.',
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-upw', 'test']
    )

    execute_csv2_command(
        gvar, 1, 'UV19', 'value specified for a password is less then 16 characters, and does not contain a mixture of upper, lower, and numerics.',
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-upw', 'invalid']
    )

    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-ucn', '']
    )

    execute_csv2_command(
        gvar, 0, None, '| Common Name   |  ',
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'clu7')]
    )

    execute_csv2_command(
        gvar, 1, 'UV20', 'common name "{0}" conflicts with registered user "{0}".'.format(ut_id(gvar, 'clu1')),
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-ucn', ut_id(gvar, 'clu1')]
    )

    execute_csv2_command(
        gvar, 1, 'UV20', 'common name "{}" conflicts with registered user "{}".'.format(ut_id(gvar, 'command line user one'), ut_id(gvar, 'clu1')),
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-ucn', ut_id(gvar, 'command line user one')]
    )

    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-ucn', ut_id(gvar, 'command line user update')]
    )

    execute_csv2_command(
        gvar, 0, None, '| Common Name   | {} '.format(ut_id(gvar, 'command line user update')),
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'clu7')]
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-SU\']',
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-SU']
    )

    execute_csv2_command(
        gvar, 1, 'UV19', 'boolean value specified for "is_superuser" must be one of the following: true, false, yes, no, 1, or 0.',
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-SU', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-SU', 'yes']
    )

    execute_csv2_command(
        gvar, 0, None, '| Super User    | 1',
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'clu7')]
    )

    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-SU', 'false']
    )

    execute_csv2_command(
        gvar, 0, None, '| Super User    | 0',
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'clu7')]
    )

    execute_csv2_command(
        gvar, 1, 'UV19', r'value specified for "group_option" must be one of the following options: [\'add\', \'delete\'].',
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-go', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'nothing to update',
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-go', 'add']
    )

    execute_csv2_command(
        gvar, 1, None, 'nothing to update',
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-go', 'delete']
    )

    execute_csv2_command(
        gvar, 1, None, 'nothing to update',
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', '']
    )

    execute_csv2_command(
        gvar, 1, 'UV21', 'specified group "invalid-unit-test" does not exist.',
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'UV22', r'Duplicate entry \'jodiew-clu7-jodiew-clg1\' for key \'PRIMARY\'',
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', ut_id(gvar, 'clg1,clg1')]
    )

    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', ut_id(gvar, 'clg1')]
    )

    execute_csv2_command(
        gvar, 0, None, '| User Groups   | {} '.format(ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'clu7')]
    )

    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', ut_id(gvar, 'clg1'), '-go', 'delete']
    )

    execute_csv2_command(
        gvar, 0, None, '| User Groups   | None ',
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'clu7')]
    )

    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', ut_id(gvar, 'clg1'), '-go', 'add']
    )

    execute_csv2_command(
        gvar, 0, None, '| User Groups   | {} '.format(ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'clu7')]
    )

    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', ut_id(gvar, 'clg2'), '-go', 'add']
    )

    execute_csv2_command(
        gvar, 0, None, '| User Groups   | {} '.format(ut_id(gvar, 'clg1,clg2')),
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'clu7')]
    )

    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', ut_id(gvar, 'clg1,clg2'), '-go', 'delete']
    )

    execute_csv2_command(
        gvar, 0, None, '| User Groups   | None ',
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'clu7')]
    )

    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', ut_id(gvar, 'clg1,clg2')]
    )

    execute_csv2_command(
        gvar, 0, None, '| User Groups   | {} '.format(ut_id(gvar, 'clg1,clg2')),
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'clu7')]
    )

    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', ut_id(gvar, 'clg1')]
    )

    execute_csv2_command(
        gvar, 0, None, '| User Groups   | {} '.format(ut_id(gvar, 'clg1,clg2')),
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'clu7')]
    )

    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['cloudscheduler', 'user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', ut_id(gvar, 'clg1'), '-go', 'add']
    )

    execute_csv2_command(
        gvar, 0, None, '| User Groups   | {} '.format(ut_id(gvar, 'clg1,clg2')),
        ['cloudscheduler', 'user', 'list', '-un', ut_id(gvar, 'clu7')]
    )

if __name__ == "__main__":
    main(None)

