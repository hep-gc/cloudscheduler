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

    # 01 - 13
    sanity_commands(gvar, 'cloud')

    # 14 - 27
    sanity_commands(gvar, 'cloud', 'add')

    parameters = {
        # 28 Give an invalid parameter.
        # 29 Omit name.
        '--cloud-name': {'valid': 'invalid-unit-test', 'test_cases': {
            # 30
            '': 'cloud add value specified for "cloud_name" must not be the empty string.',
            # 31
            'Invalid-Unit-Test': 'cloud add value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 32
            'invalid-unit--test': 'cloud add value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 33
            'invalid-unit-test-': 'cloud add value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 34
            'invalid-unit-test!': 'cloud add value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 35
            'invalid,unit,test': 'cloud add value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 36
            'cloud-name-that-is-too-long-for-the-database': 'Data too long for column \'cloud_name\' at row 1',
            # 37 Attempt to create a cloud that already exists.
            ut_id(gvar, 'clc2'): 'Duplicate entry \'{}-{}\' for key \'PRIMARY\''.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2'))
        }, 'mandatory': True},
        # 38 Omit type.
        # 39
        '--cloud-type': {'valid': 'openstack', 'test_cases': {'invalid-unit-test': 'cloud add value specified for "cloud_type" must be one of the following options: [\'amazon\', \'local\', \'openstack\'].'}, 'mandatory': True},
        # 40 Omit address.
        # 41
        '--cloud-address': {'valid': gvar['cloud_credentials']['authurl'], 'test_cases': {'': 'cloud add parameter "authurl" contains an empty string which is specifically disallowed.'}, 'mandatory': True},
        # 42 Omit user.
        # 43
        '--cloud-user': {'valid': gvar['cloud_credentials']['username'], 'test_cases': {'': 'cloud add parameter "username" contains an empty string which is specifically disallowed.'}, 'mandatory': True},
        # 44 Omit password.
        # 45
        '--cloud-password': {'valid': gvar['cloud_credentials']['password'], 'test_cases': {'': 'cloud add parameter "password" contains an empty string which is specifically disallowed.'}, 'mandatory': True},
        # 46 Omit project.
        # 47
        '--cloud-project': {'valid': gvar['cloud_credentials']['project'], 'test_cases': {'': 'cloud add parameter "project" contains an empty string which is specifically disallowed.'}, 'mandatory': True},
        # 48 Omit region.
        # 49
        '--cloud-region': {'valid': gvar['cloud_credentials']['region'], 'test_cases': {'': 'cloud add parameter "region" contains an empty string which is specifically disallowed.'}, 'mandatory': True},
        # 50
        '--cloud-enabled': {'valid': 0, 'test_cases': {'invalid-unit-test': 'cloud add boolean value specified for "enabled" must be one of the following: true, false, yes, no, 1, or 0.'}},
        # 51
        '--cloud-priority': {'valid': 0, 'test_cases': {'invalid-unit-test': 'cloud add value specified for "priority" must be an integer value.'}},
        # 52
        '--cloud-spot-price': {'valid': 0.0, 'test_cases': {'invalid-unit-test': 'cloud add value specified for "spot_price" must be a floating point value.'}},
        # 53
        '--group-metadata-exclusion': {'valid': '', 'test_cases': {'invalid-unit-test': 'cloud add, "invalid-unit-test" failed - specified metadata_name "invalid-unit-test" does not exist.'}},
        '--vm-boot-volume': {'valid': '{"GBs_per_core": 10}', 'test_cases': {
            # 54
            'invalid-unit-test': 'cloud add value specified for "vm_boot_volume" must be a valid JSON string.',
            # 55
            '{"invalid-unit-test": 0}': 'cloud add dictionary specified for "vm_boot_volume" contains the following undefined keys: [\'invalid-unit-test\']'}
        },
        # 56
        '--vm-cores': {'valid': 0, 'test_cases': {'invalid-unit-test': 'cloud add value specified for "cores_ctl" must be an integer value.'}},
        # 57
        '--vm-flavor': {'valid': '', 'test_cases': {'invalid-unit-test': 'cloud add, "invalid-unit-test" failed - specified item does not exist: vm_flavor=invalid-unit-test, group_name={}, cloud_name=invalid-unit-test.'.format(ut_id(gvar, 'clg1'))}},
        # 58
        '--vm-image': {'valid': '', 'test_cases': {'invalid-unit-test': 'cloud add, "invalid-unit-test" failed - specified item does not exist: vm_image=invalid-unit-test, group_name={}, cloud_name=invalid-unit-test.'.format(ut_id(gvar, 'clg1'))}},
        # 59
        '--vm-keep-alive': {'valid': 0, 'test_cases': {'invalid-unit-test': 'cloud add value specified for "vm_keep_alive" must be an integer value.'}},
        # 60
        '--vm-keyname': {'valid': '', 'test_cases': {'invalid-unit-test': 'cloud add, "invalid-unit-test" failed - specified item does not exist: vm_keyname=invalid-unit-test, group_name={}, cloud_name=invalid-unit-test.'.format(ut_id(gvar, 'clg1'))}},
        # 61
        '--vm-ram': {'valid': 0, 'test_cases': {'invalid-unit-test': 'cloud add value specified for "ram_ctl" must be an integer value.'}},
    }

    parameters_commands(gvar, 'cloud', 'add', ut_id(gvar, 'clg1'), ut_id(gvar, 'clu3'), parameters)

    # 62
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: metadata-mime-type',
        ['cloud', 'add', '-mmt', 'invalid-unit-test', '-g', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu3')]
    )

    # 63
    execute_csv2_command(
        gvar, 0, None, 'cloud "{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc10')),
        ['cloud', 'add',
            '-cn', ut_id(gvar, 'clc10'),
            '-ca', gvar['cloud_credentials']['authurl'],
            '-cU', gvar['cloud_credentials']['username'],
            '-cpw', gvar['cloud_credentials']['password'],
            '-cr', gvar['cloud_credentials']['region'],
            '-cP', gvar['cloud_credentials']['project'],
            '-ct', 'openstack',
            '-ce', 'yes',
            '-vi', '',
            '-vf', '',
            '-vk', '',
            '-vka', '10',
            '-vn', '',
            '-csp', '10',
            '-gme', ut_id(gvar, 'clm2'),
            '-su', ut_id(gvar, 'clu3')
        ]
    )

    # 64
    execute_csv2_command(
        gvar, 0, None, 'cloud "{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc11')),
        ['cloud', 'add',
            '-cn', ut_id(gvar, 'clc11'),
            '-ca', gvar['cloud_credentials']['authurl'],
            '-cU', gvar['cloud_credentials']['username'],
            '-cpw', gvar['cloud_credentials']['password'],
            '-cr', gvar['cloud_credentials']['region'],
            '-cP', gvar['cloud_credentials']['project'],
            '-ct', 'openstack',
            '-gme', ut_id(gvar, 'clm2,clm2.yaml'),
            '-su', ut_id(gvar, 'clu3')
        ]
    )

if __name__ == "__main__":
    main(None)
