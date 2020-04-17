from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id, sanity_commands, parameters_commands
from sys import argv

# lno: AV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)

    # 01 - 14
    sanity_commands(gvar, 'alias', 'update')

    parameters = {
        # 15 Omit name.
        '--cloud-name': {'valid': ut_id(gvar, 'clc2'), 'test_cases': {
            # 16
            '': 'cloud alias update, value specified for "cloud_name" must not be the empty string.',
            # 17
            'Invalid-Unit-Test': 'cloud alias update, value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 18
            'invalid-unit--test': 'cloud alias update, value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 19
            'invalid-unit-test-': 'cloud alias update, value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 20
            'invalid-unit-test!': 'cloud alias update, value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 21
            'invalid,unit,test': 'cloud alias update, value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 22 Attempt to add a cloud that does not exist.
            'invalid-unit-test': 'cloud alias update, "{}" failed - specified value in list of values does not exist: cloud_name=invalid-unit-test, group_name={}.'.format(ut_id(gvar, 'cla2'), ut_id(gvar, 'clg1'))
        }, 'mandatory': True},
        # 23 Omit alias.
        '--alias-name': {'valid': ut_id(gvar, 'cla2'), 'test_cases': {
            # 24
            '': 'cloud alias update, value specified for "alias_name" must not be the empty string.',
            # 25
            'invalid-unit-test!': 'cloud alias update, value specified for "alias_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 26 Specify an alias that does not exist.
            'invalid-unit-test': 'cloud alias group update "{}.invalid-unit-test" failed - specified alias does not exist.'.format(ut_id(gvar, 'clg1'))
        }, 'mandatory': True},
        '--cloud-option': {'valid': 'invalid-unit-test', 'test_cases': {
            # 27
            '': 'cloud alias update, value specified for "cloud_option" must be one of the following options: [\'add\', \'delete\'].',
            # 28
            'invalid-unit-test': 'cloud alias update, value specified for "cloud_option" must be one of the following options: [\'add\', \'delete\'].'
        }}
    }

    parameters_commands(gvar, 'alias', 'update', ut_id(gvar, 'clg1'), ut_id(gvar, 'clu3'), parameters)

    # 29 Attempt to remove a cloud that an alias does not have.
    execute_csv2_command(
        gvar, 1, 'AV', 'cloud alias update, "{}" failed - specified value in list of values does not exist: cloud_name=invalid-unit-test, group_name={}.'.format(ut_id(gvar, 'cla2'), ut_id(gvar, 'clg1')),
        ['alias', 'update', '-g', ut_id(gvar, 'clg1'), '--alias-name', ut_id(gvar, 'cla2'), '--cloud-name', 'invalid-unit-test', '--cloud-option', 'delete', '-su', ut_id(gvar, 'clu3')],
    )

    # 30 Explicitly add clc3 to cla2.
    execute_csv2_command(
        gvar, 0, None, 'cloud alias "{}.{}" successfully updated.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'cla2')),
        ['alias', 'update', '--alias-name', ut_id(gvar, 'cla2'), '--cloud-name', ut_id(gvar, 'clc3'), '--cloud-option', 'add', '-su', ut_id(gvar, 'clu3')],
    )

    # 32 Explicitly remove clc2 and clc3 from cla2, causing cla2 to be deleted.
    execute_csv2_command(
        gvar, 0, None, 'cloud alias "{}.{}" successfully updated.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'cla2')),
        ['alias', 'update', '--alias-name', ut_id(gvar, 'cla2'), '--cloud-name', ut_id(gvar, 'clc2'), '--cloud-option', 'delete', '-su', ut_id(gvar, 'clu3')],
    )

if __name__ == "__main__":
    main(None)
