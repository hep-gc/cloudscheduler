from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id
from sys import argv

# lno: UV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)

    #### UPDATE ####
    # 63
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['user', 'update', '-su', ut_id(gvar, 'clu4')]
    )

    # 64
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['user', 'update', '-xx', 'yy', '-su', ut_id(gvar, 'clu4')]
    )

    # 65
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: only-keys',
        ['user', 'update', '-ok', '-su', ut_id(gvar, 'clu4')]
    )

    # 66
    execute_csv2_command(
        gvar, None, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['user', 'update', '-s', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')], timeout=8
    )

    # 67
    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['user', 'update', '-su', ut_id(gvar, 'clu4')]
    )

    # 68
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler user update".',
        ['user', 'update', '-h', '-su', ut_id(gvar, 'clu4')]
    )

    # 69
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['user', 'update', '-H', '-su', ut_id(gvar, 'clu4')]
    )

    # 70
    execute_csv2_command(
        gvar, 1, None, 'Expose API requested',
        ['user', 'update', '-xA', '-su', ut_id(gvar, 'clu4')]
    )

    # 71
    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['user', 'update', '-g', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 72
    execute_csv2_command(
        gvar, 1, None, '"cloudscheduler user update" requires at least one option to update.',
        ['user', 'update', '-un', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 73
    execute_csv2_command(
        gvar, 1, 'UV', 'the request did not match any rows.',
        ['user', 'update', '-un', 'invalid-unit-test', '-SU', 'yes', '-su', ut_id(gvar, 'clu4')]
    )

    # 74
    execute_csv2_command(
        gvar, 1, None, '"cloudscheduler user update" requires at least one option to update.',
        ['user', 'update', '-un', ut_id(gvar, 'clu7'), '-su', ut_id(gvar, 'clu4')]
    )

    # 75
    execute_csv2_command(
        gvar, 1, 'UV', 'value specified for a password is less than 6 characters.',
        ['user', 'update', '-un', ut_id(gvar, 'clu7'), '-upw', 'test', '-su', ut_id(gvar, 'clu4')]
    )

    # 76
    execute_csv2_command(
        gvar, 1, 'UV', 'value specified for a password is less then 16 characters, and does not contain a mixture of upper, lower, and numerics.',
        ['user', 'update', '-un', ut_id(gvar, 'clu7'), '-upw', 'invalid', '-su', ut_id(gvar, 'clu4')]
    )

    # 77
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['user', 'update', '-un', ut_id(gvar, 'clu7'), '-ucn', '', '-su', ut_id(gvar, 'clu4')]
    )

    # 78
    execute_csv2_command(
        gvar, 1, 'UV', 'common name "{0}" conflicts with registered user "{0}".'.format(ut_id(gvar, 'clu1')),
        ['user', 'update', '-un', ut_id(gvar, 'clu7'), '-ucn', ut_id(gvar, 'clu1'), '-su', ut_id(gvar, 'clu4')]
    )

    # 79
    execute_csv2_command(
        gvar, 1, 'UV', 'common name "{}" conflicts with registered user "{}".'.format(ut_id(gvar, 'command line user one'), ut_id(gvar, 'clu1')),
        ['user', 'update', '-un', ut_id(gvar, 'clu7'), '-ucn', ut_id(gvar, 'command line user one'), '-su', ut_id(gvar, 'clu4')]
    )

    # 80
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['user', 'update', '-un', ut_id(gvar, 'clu7'), '-ucn', ut_id(gvar, 'command line user update'), '-su', ut_id(gvar, 'clu4')]
    )

    # 81 We have to specify server and server password explicitly because -SU has to be the last parameter.
    execute_csv2_command(
        gvar, 1, None, 'Value omitted for option: -SU | --super-user',
        ['user', 'update', '-un', ut_id(gvar, 'clu7'), '-s', 'unit-test', '-su', ut_id(gvar, 'clu4'), '-spw', gvar['user_secret'], '-SU']
    )

    # 82
    execute_csv2_command(
        gvar, 1, 'UV', 'boolean value specified for "is_superuser" must be one of the following: true, false, yes, no, 1, or 0.',
        ['user', 'update', '-un', ut_id(gvar, 'clu7'), '-SU', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 83
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['user', 'update', '-un', ut_id(gvar, 'clu7'), '-SU', 'yes', '-su', ut_id(gvar, 'clu4')]
    )

    # 84
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['user', 'update', '-un', ut_id(gvar, 'clu7'), '-SU', 'false', '-su', ut_id(gvar, 'clu4')]
    )

    # 85
    execute_csv2_command(
        gvar, 1, 'UV', 'value specified for "group_option" must be one of the following options: [\'add\', \'delete\'].',
        ['user', 'update', '-un', ut_id(gvar, 'clu7'), '-go', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 86
    execute_csv2_command(
        gvar, 1, 'UV', 'user update must specify at least one field to update.',
        ['user', 'update', '-un', ut_id(gvar, 'clu7'), '-go', 'add', '-su', ut_id(gvar, 'clu4')]
    )

    # 87
    execute_csv2_command(
        gvar, 1, 'UV', 'user update must specify at least one field to update.',
        ['user', 'update', '-un', ut_id(gvar, 'clu7'), '-go', 'delete', '-su', ut_id(gvar, 'clu4')]
    )

    # 88
    execute_csv2_command(
        gvar, 0, None, 'user update, parameter "group_name" contains an empty string which is specifically disallowed.'.format(ut_id(gvar, 'clu7')),
        ['user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', '', '-su', ut_id(gvar, 'clu4')]
    )

    # 89
    execute_csv2_command(
        gvar, 1, 'UV', 'specified group "invalid-unit-test" does not exist.',
        ['user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 90
    execute_csv2_command(
        gvar, 1, 'UV', 'user update, "{}" failed - group "{}" was specified twice.'.format(ut_id(gvar, 'clu7'), ut_id(gvar, 'clg1')),
        ['user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', ut_id(gvar, 'clg1,clg1'), '-su', ut_id(gvar, 'clu4')]
    )

    # 91
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu4')]
    )

    # 92
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', ut_id(gvar, 'clg1'), '-go', 'delete', '-su', ut_id(gvar, 'clu4')]
    )

    # 93
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', ut_id(gvar, 'clg1'), '-go', 'add', '-su', ut_id(gvar, 'clu4')]
    )

    # 94
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', ut_id(gvar, 'clg3'), '-go', 'add', '-su', ut_id(gvar, 'clu4')]
    )

    # 95
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', ut_id(gvar, 'clg1,clg5'), '-go', 'delete', '-su', ut_id(gvar, 'clu4')]
    )

    # 96
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', ut_id(gvar, 'clg1,clg5'), '-su', ut_id(gvar, 'clu4')]
    )

    # 97
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu4')]
    )

    # 98
    execute_csv2_command(
        gvar, 0, None, 'user "{}" successfully updated.'.format(ut_id(gvar, 'clu7')),
        ['user', 'update', '-un', ut_id(gvar, 'clu7'), '-gn', ut_id(gvar, 'clg1'), '-go', 'add', '-su', ut_id(gvar, 'clu4')]
    )

if __name__ == "__main__":
    main(None)
