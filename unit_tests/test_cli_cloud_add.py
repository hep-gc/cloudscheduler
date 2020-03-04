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
    sanity_commands(gvar, 'cloud')

    # 13 - 24
    sanity_commands(gvar, 'cloud', 'add')

    PARAMETERS = {
        # 25 Give an invalid parameter.
        # 26 Omit name.
        '--cloud-name': {'valid': 'invalid-unit-test', 'test_cases': {
            # 27
            '': 'cloud add value specified for "cloud_name" must not be the empty string.',
            # 28
            'Invalid-Unit-Test': 'cloud add value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 29
            'invalid-unit--test': 'cloud add value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 30
            'invalid-unit-test-': 'cloud add value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 31
            'invalid-unit-test!': 'cloud add value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 32
            'invalid,unit,test': 'cloud add value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 33
            'cloud-name-that-is-too-long-for-the-database': 'Data too long for column \'cloud_name\' at row 1',
            # 34 Attempt to create a cloud that already exists.
            ut_id(gvar, 'clc2'): 'Duplicate entry \'{}-{}\' for key \'PRIMARY\''.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2'))
        }, 'mandatory': True},
        # 35 Omit type.
        # 36
        '--cloud-type': {'valid': 'local', 'test_cases': {'invalid-unit-test': 'cloud add value specified for "cloud_type" must be one of the following options: [\'amazon\', \'azure\', \'google\', \'local\', \'opennebula\', \'openstack\'].'}, 'mandatory': True},
        # 37 Omit address.
        # 38
        '--cloud-address': {'valid': gvar['cloud_credentials']['authurl'], 'test_cases': {'': 'cloud add parameter "authurl" contains an empty string which is specifically disallowed.'}, 'mandatory': True},
        # 39 Omit user.
        # 40
        '--cloud-user': {'valid': gvar['cloud_credentials']['username'], 'test_cases': {'': 'cloud add parameter "username" contains an empty string which is specifically disallowed.'}, 'mandatory': True},
        # 41 Omit password.
        # 42
        '--cloud-password': {'valid': gvar['cloud_credentials']['password'], 'test_cases': {'': 'cloud add parameter "password" contains an empty string which is specifically disallowed.'}, 'mandatory': True},
        # 43 Omit project.
        # 44
        '--cloud-project': {'valid': gvar['cloud_credentials']['project'], 'test_cases': {'': 'cloud add parameter "project" contains an empty string which is specifically disallowed.'}, 'mandatory': True},
        # 45 Omit region.
        # 46
        '--cloud-region': {'valid': gvar['cloud_credentials']['region'], 'test_cases': {'': 'cloud add parameter "region" contains an empty string which is specifically disallowed.'}, 'mandatory': True},
        # 47
        '--cloud-enabled': {'valid': 0, 'test_cases': {'invalid-unit-test': 'cloud add boolean value specified for "enabled" must be one of the following: true, false, yes, no, 1, or 0.'}},
        # 48
        '--cloud-priority': {'valid': 0, 'test_cases': {'invalid-unit-test': 'cloud add value specified for "priority" must be an integer value.'}},
        # 49
        '--cloud-spot-price': {'valid': 0.0, 'test_cases': {'invalid-unit-test': 'cloud add value specified for "spot_price" must be a floating point value.'}},
        # 50
        '--group-metadata-exclusion': {'valid': '', 'test_cases': {'invalid-unit-test': 'cloud add, "invalid-unit-test" failed - specified metadata_name "invalid-unit-test" does not exist.'}},
        '--vm-boot-volume': {'valid': '{"GBs_per_core": 10}', 'test_cases': {
            # 51
            'invalid-unit-test': 'cloud add value specified for "vm_boot_volume" must be a valid JSON string.',
            # 52
            '{"invalid-unit-test": 0}': 'cloud add dictionary specified for "vm_boot_volume" contains the following undefined keys: [\'invalid-unit-test\']'}
        },
        # 53
        '--vm-cores': {'valid': 0, 'test_cases': {'invalid-unit-test': 'cloud add value specified for "cores_ctl" must be an integer value.'}},
        # 54
        '--vm-flavor': {'valid': '', 'test_cases': {'invalid-unit-test': 'cloud add, "invalid-unit-test" failed - specified item does not exist: vm_flavor=invalid-unit-test, group_name={}, cloud_name=invalid-unit-test.'.format(ut_id(gvar, 'clg1'))}},
        # 55
        '--vm-image': {'valid': '', 'test_cases': {'invalid-unit-test': 'cloud add, "invalid-unit-test" failed - specified item does not exist: vm_image=invalid-unit-test, group_name={}, cloud_name=invalid-unit-test.'.format(ut_id(gvar, 'clg1'))}},
        # 56
        '--vm-keep-alive': {'valid': 0, 'test_cases': {'invalid-unit-test': 'cloud add value specified for "vm_keep_alive" must be an integer value.'}},
        # 57
        '--vm-keyname': {'valid': '', 'test_cases': {'invalid-unit-test': 'cloud add, "invalid-unit-test" failed - specified item does not exist: vm_keyname=invalid-unit-test, group_name={}, cloud_name=invalid-unit-test.'.format(ut_id(gvar, 'clg1'))}},
        # 58
        '--vm-ram': {'valid': 0, 'test_cases': {'invalid-unit-test': 'cloud add value specified for "ram_ctl" must be an integer value.'}},
    }

    parameters_commands(gvar, 'cloud', 'add', ut_id(gvar, 'clg1'), ut_id(gvar, 'clu3'), PARAMETERS)

    # 59
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: metadata-mime-type',
        ['cloud', 'add', '-mmt', 'invalid-unit-test', '-g', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu3')]
    )

    # 60
    execute_csv2_command(
        gvar, 0, None, 'cloud "{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc10')),
        ['cloud', 'add',
            '-cn', ut_id(gvar, 'clc10'),
            '-ca', gvar['cloud_credentials']['authurl'],
            '-cU', gvar['cloud_credentials']['username'],
            '-cpw', gvar['cloud_credentials']['password'],
            '-cr', gvar['cloud_credentials']['region'],
            '-cP', gvar['cloud_credentials']['project'],
            '-ct', 'local',
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

    # 61
    execute_csv2_command(
        gvar, 0, None, 'cloud "{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc11')),
        ['cloud', 'add',
            '-cn', ut_id(gvar, 'clc11'),
            '-ca', gvar['cloud_credentials']['authurl'],
            '-cU', gvar['cloud_credentials']['username'],
            '-cpw', gvar['cloud_credentials']['password'],
            '-cr', gvar['cloud_credentials']['region'],
            '-cP', gvar['cloud_credentials']['project'],
            '-ct', 'local',
            '-gme', ut_id(gvar, 'clm2,clm2.yaml'),
            '-su', ut_id(gvar, 'clu3')
        ]
    )

if __name__ == "__main__":
    main(None)
