from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id, sanity_commands, parameters_commands
from sys import argv

# lno: CV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)

    # 01 - 12
    sanity_commands(gvar, 'alias')

    # 13 - 24
    sanity_commands(gvar, 'alias', 'add')

    PARAMETERS = {
        # 25 Give an invalid parameter.
        # 26 Omit name.
        '--cloud-name': {'valid': 'invalid-unit-test', 'test_cases': {
            # 27
            '': 'alias add value specified for "cloud_name" must not be the empty string.',
            # 28
            'Invalid-Unit-Test': 'alias add value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 29
            'invalid-unit--test': 'alias add value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 30
            'invalid-unit-test-': 'alias add value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 31
            'invalid-unit-test!': 'alias add value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 32
            'invalid,unit,test': 'alias add value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 0 Specify a cloud that does not exist.
            'invalid-unit-test': 'cloud alias add, "invalid-unit-test" failed - specified value in list of values does not exist: cloud_name=invalid-unit-test, group_name={}.'.format(ut_id(gvar, 'atg1'))
        }, 'mandatory': True},
        # 0 Omit alias.
        '--alias-name': {'valid': 'invalid-unit-test', 'test_cases': {
            # 27
            '': 'alias add value specified for "alias_name" must not be the empty string.',
            # 28
            'Invalid-Unit-Test': 'alias add value specified for "alias_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 29
            'invalid-unit--test': 'alias add value specified for "alias_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 30
            'invalid-unit-test-': 'alias add value specified for "alias_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 31
            'invalid-unit-test!': 'alias add value specified for "alias_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 32
            'invalid,unit,test': 'alias add value specified for "alias_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 33
            'alias-name-that-is-too-long-for-the-database': 'Data too long for column \'alias_name\' at row 1',
            # 34 Attempt to create a cloud that already exists.
            ut_id(gvar, 'cla1'): 'Duplicate entry \'{}-{}\' for key \'PRIMARY\''.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'cla1'))
        }, 'mandatory': True},
    }

    parameters_commands(gvar, 'cloud', 'add', ut_id(gvar, 'clg1'), ut_id(gvar, 'clu3'), PARAMETERS)

    # 21 Create an alias properly.
    execute_csv2_command(
        gvar, 0, None, 'cloud alias "{}.{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'cla3')),
        ['alias', 'add', '-g', ut_id(gvar, 'clg1'), '--alias-name', ut_id(gvar, 'cla3'), '--cloud-name', ut_id(gvar, 'clc2'), '-su', ut_id(gvar, 'clu3')],
    )

    # 22 Ensure that 19 actually created cla3.
    execute_csv2_command(
        gvar, 0, None, 'Rows: 1',
        ['alias', 'list', '-g', ut_id(gvar, 'clg1'), '-an', ut_id(gvar, 'cla3'), '-su', ut_id(gvar, 'clu3')],
    )

if __name__ == "__main__":
    main(None)
