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
        # 28 Omit name.
        '--cloud-name': {'valid': 'invalid-unit-test', 'test_cases': {
            # 29
            '': 'cloud add value specified for "cloud_name" must not be the empty string.',
            # 30
            'Invalid-Unit-Test': 'cloud add value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 31
            'invalid-unit--test': 'cloud add value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 32
            'invalid-unit-test-': 'cloud add value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 33
            'invalid-unit-test!': 'cloud add value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 34
            'invalid,unit,test': 'cloud add value specified for "cloud_name" must be all lowercase letters, digits, dashes, underscores, periods, and colons, and cannot contain more than one consecutive dash or start or end with a dash.',
            # 35
            'cloud-name-that-is-too-long-for-the-database': 'Data too long for column \'cloud_name\' at row 1',
            # 36 Attempt to create a cloud that already exists.
            ut_id(gvar, 'clc2'): 'Duplicate entry \'{}-{}\' for key \'PRIMARY\''.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc2'))
        }, 'mandatory': True},
        # 37 Omit type.
        # 38
        '--cloud-type': {'valid': 'openstack', 'test_cases': {'invalid-unit-test': 'cloud add value specified for "cloud_type" must be one of the following options: [\'amazon\', \'local\', \'openstack\'].'}, 'mandatory': True},
        # 39 Omit address.
        # 40
        '--cloud-address': {'valid': gvar['cloud_credentials']['authurl'], 'test_cases': {'': 'cloud add parameter "authurl" contains an empty string which is specifically disallowed.'}, 'mandatory': True},
        # 41
        '--cloud-user': {'valid': gvar['cloud_credentials']['username'], 'test_cases': {'': 'insufficient credentials to establish openstack v3 session, check if missing any user/project info'}},
        # 42
        '--cloud-password': {'valid': gvar['cloud_credentials']['password'], 'test_cases': {'': 'insufficient credentials to establish openstack v3 session, check if missing any user/project info'}},
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
        # 51
        '--vm-cores': {'valid': 0, 'test_cases': {'invalid-unit-test': 'cloud add value specified for "cores_ctl" must be an integer value.'}},
        # 52
        '--vm-flavor': {'valid': '', 'test_cases': {'invalid-unit-test': 'cloud add, "invalid-unit-test" failed - specified item does not exist: vm_flavor=invalid-unit-test, group_name={}, cloud_name=invalid-unit-test.'.format(ut_id(gvar, 'clg1'))}},
        # 53
        '--vm-image': {'valid': '', 'test_cases': {'invalid-unit-test': 'cloud add, "invalid-unit-test" failed - specified item does not exist: vm_image=invalid-unit-test, group_name={}, cloud_name=invalid-unit-test.'.format(ut_id(gvar, 'clg1'))}},
        # 54
        '--vm-keep-alive': {'valid': 0, 'test_cases': {'invalid-unit-test': 'cloud add value specified for "vm_keep_alive" must be an integer value.'}},
        # 55
        '--vm-keyname': {'valid': '', 'test_cases': {'invalid-unit-test': 'cloud add, "invalid-unit-test" failed - specified item does not exist: vm_keyname=invalid-unit-test, group_name={}, cloud_name=invalid-unit-test.'.format(ut_id(gvar, 'clg1'))}},
        # 56
        '--vm-ram': {'valid': 0, 'test_cases': {'invalid-unit-test': 'cloud add value specified for "ram_ctl" must be an integer value.'}},
        # 57
        '--boot-volume-type' : {'valid': 'None', 'test_cases' : {'invalid-unit-test': 'At least one of base size or size per core must be specified'}},
    }

    parameters_commands(gvar, 'cloud', 'add', ut_id(gvar, 'clg1'), ut_id(gvar, 'clu3'), parameters)

    base_options = ['cloud', 'add', 
        '-ca', gvar['cloud_credentials']['authurl'], 
        '-cr', gvar['cloud_credentials']['region'], 
        '-cP', gvar['cloud_credentials']['project'],
        '-ct', 'openstack',
        '-ce', 'yes',
        '-gme', ut_id(gvar, 'clm2'),
        '-su', ut_id(gvar, 'clu3')
    ]
    # 58
    execute_csv2_command(
        gvar, 1, None, 'At least one of base size or size per core must be specified',
        base_options + [
            '-bvt', 'invalid-unit-test',
            '-cn', ut_id(gvar, 'clc11'),
            '-cU', gvar['cloud_credentials']['username'],
            '-cpw', gvar['cloud_credentials']['password'],
        ]
    )

    # 59
    execute_csv2_command(
        gvar, 1, None, 'specified item does not exist: vm_boot_volume_type=invalid-unit-test',
        base_options + [
            '-bvt', 'invalid-unit-test',
            '-bvs', 20,
            '-cn', ut_id(gvar, 'clc11'),
            '-cU', gvar['cloud_credentials']['username'],
            '-cpw', gvar['cloud_credentials']['password'],
        ]
    )

    # 60
    execute_csv2_command(
        gvar, 1, None, 'specified item does not exist: vm_boot_volume_type=invalid-unit-test',
        base_options + [
            '-bvt', 'invalid-unit-test',
            '-bvc', 20,
            '-cn', ut_id(gvar, 'clc11'),
            '-cU', gvar['cloud_credentials']['username'],
            '-cpw', gvar['cloud_credentials']['password'],
        ]
    )

    # 61 Omit username
    execute_csv2_command(
        gvar, 1, None, 'cloud add request did not contain mandatory parameter "username"',
        base_options + ['-cn', ut_id(gvar, 'clc10'), '-cpw', gvar['cloud_credentials']['password']]    
    )

    # 62 Omit password
    execute_csv2_command(
        gvar, 1, None, 'cloud add request did not contain mandatory parameter "password"',
        base_options + ['-cn', ut_id(gvar, 'clc10'), '-cU', gvar['cloud_credentials']['username']]
    )

    # 63 Omit app credentials
    execute_csv2_command(
        gvar, 1, None, 'Insufficient credentials to establish openstack session, check if missing any applicaion credentials info',
        base_options + ['-cn', ut_id(gvar, 'clc10'), '-cas', gvar['cloud_credentials']['app_credentials_secret']]
    )

    # 64 Omit app credentials secret
    execute_csv2_command(
        gvar, 1, None, 'Insufficient credentials to establish openstack session, check if missing any applicaion credentials info',
        base_options + ['-cn', ut_id(gvar, 'clc10'), '-cac', gvar['cloud_credentials']['app_credentials']]
    )

    # 65 Omit userid
    execute_csv2_command(
        gvar, 1, None, 'Failed to get expire date of app creds, insufficient credentials to establish openstack session, check if missing userid or application credentials info',
        base_options + ['-cn', ut_id(gvar, 'clc10'), '-cac', gvar['cloud_credentials']['app_credentials'], '-cas', gvar['cloud_credentials']['app_credentials_secret']]
    )

    # 66
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: metadata-mime-type',
        ['cloud', 'add', '-mmt', 'invalid-unit-test', '-g', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu3')]
    )

    # 67
    execute_csv2_command(
        gvar, 0, None, 'cloud "{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc10')),
        base_options + [
            '-cn', ut_id(gvar, 'clc10'),
            '-cU', gvar['cloud_credentials']['username'],
            '-cpw', gvar['cloud_credentials']['password'],
            '-vi', '',
            '-vf', '',
            '-vk', '',
            '-vka', '10',
            '-vn', '',
            '-csp', '10',
        ]
    )

    # 68
    execute_csv2_command(
        gvar, 0, None, 'cloud "{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc11')),
        base_options + [
            '-bvt', 'None',
            '-cn', ut_id(gvar, 'clc11'),
            '-cU', gvar['cloud_credentials']['username'],
            '-cpw', gvar['cloud_credentials']['password'],
        ]
    )


    # 69
    execute_csv2_command(
        gvar, 0, None, 'cloud "{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc12')),
        base_options + [
            '-cn', ut_id(gvar, 'clc12'),
            '-cU', gvar['cloud_credentials']['username'],
            '-cpw', gvar['cloud_credentials']['password'],
        ]
    )

    # 70 Successful add cloud with app credential
    execute_csv2_command(
        gvar, 0, None, 'cloud "{}::{}" successfully added.'.format(ut_id(gvar, 'clg1'), ut_id(gvar, 'clc13')),
        base_options + [
            '-cn', ut_id(gvar, 'clc13'), 
            '-cac', gvar['cloud_credentials']['app_credentials'], 
            '-cas', gvar['cloud_credentials']['app_credentials_secret'],
            '-ui', gvar['cloud_credentials']['userid']
        ]
    )

if __name__ == "__main__":
    main(None)
