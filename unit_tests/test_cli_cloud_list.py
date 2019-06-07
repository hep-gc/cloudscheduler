from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id
from sys import argv

# lno: CV - error code identifier.

def main(gvar, user_secret):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv2_request(gvar, argv[0])

    # 01
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'cloud', 'list', '-xx', 'yy', '-s', 'unit-test-un']
    )

    # 02
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: metadata-mime-type',
        ['cloudscheduler', 'cloud', 'list', '-mmt', 'invalid-unit-test']
    )

    # 03
    execute_csv2_command(
        gvar, 1, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'cloud', 'list', '-s', 'invalid-unit-test']
    )

    # 04
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'list', '-s', 'unit-test-un']
    )

    # 05
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler cloud list".',
        ['cloudscheduler', 'cloud', 'list', '-h']
    )

    # 06
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'cloud', 'list', '-H']
    )

    # 07
    execute_csv2_command(
        gvar, 0, None, 'Expose API requested',
        ['cloudscheduler', 'cloud', 'list', '-xA']
    )

    # 08
    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'cloud', 'list', '-g', 'invalid-unit-test']
    )

    # 09
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test-un, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'test'), ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'cloud', 'list', '-g', ut_id(gvar, 'clg1')]
    )

    # 10
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, '')[:-1], ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'cloud', 'list', '-s', 'unit-test', '-g', ut_id(gvar, 'clg1')]
    )

    # 11
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test-un, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'test'), ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'cloud', 'list', '-s', 'unit-test-un']
    )

    # 12
    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'cloud', 'list', '-cn', 'invalid-unit-test']
    )

    # 13
    execute_csv2_command(
        gvar, 0, None, 'Rows: 1',
        ['cloudscheduler', 'cloud', 'list', '-cn', ut_id(gvar, 'clc2')]
    )

    # 14
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'list', '-ok'],
        list='Clouds', columns=['Group', 'Cloud']
    )

    # 15
    execute_csv2_command(
        gvar, 0, None, 'cloud list, 1. Clouds: keys=group_name,cloud_name, columns=enabled,cloud_priority,authurl,project,project_domain_name,project_domain_id,username,user_domain_name,user_domain_id,region,spot_price,cloud_type,cores_ctl,cores_softmax,cores_max,ram_ctl,ram_max,vm_flavor,vm_image,vm_keep_alive,vm_keyname,vm_network,vm_security_groups,cascading_vm_flavor,cascading_vm_image,cascading_vm_keep_alive,cascading_vm_keyname,cascading_vm_network,cascading_vm_security_groups,cacertificate,flavor_exclusions,flavor_names,group_exclusions,metadata_names\\ncloud list, 2. Flavors (optional): keys=group_name,cloud_name, columns=name\\ncloud list, 3. Images (optional): keys=group_name,cloud_name, columns=name\\ncloud list, 4. Networks (optional): keys=group_name,cloud_name, columns=name\\ncloud list, 5. Security Groups (optional): keys=group_name,cloud_name, columns=name',
        ['cloudscheduler', 'cloud', 'list', '-VC']
    )

    # 16
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'list', '-NV'],
        list='Clouds', columns=['Project', 'User', 'Cores', 'Group', 'Cloud', 'Enabled', 'Priority', 'URL', 'Name', 'Domain', 'Name', 'Domain', 'ID', 'Name', 'Domain', 'Name', 'Domain', 'ID', 'Region', 'Spot', 'Price', 'Cloud', 'Type', 'Control', 'Cores', 'RAM', 'Cloud', 'Default', 'Cascading', 'Default', 'Group', 'Cloud', 'SoftMax', 'Max', 'Control', 'Max', 'Flavor', 'Image', 'Keep', 'Alive', 'Keyname', 'Network', 'Security', 'Groups', 'Flavor', 'Image', 'Keep', 'Alive', 'Keyname', 'Cascading', 'Default', 'Cloud', 'Metadata', 'Group', 'Cloud', 'Network', 'Security', 'Groups', 'CA', 'Certificate', 'Flavor', 'Exclusions', 'Flavors', 'Group', 'Exclusions', 'Filenames']
    )

    # 17
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'list', '-V', 'enabled,authurl'],
        list='Clouds', columns=['Group', 'Cloud', 'Enabled', 'URL']
    )

    # 18
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'list'],
        list='Clouds', columns=['Group', 'Cloud', 'Enabled', 'URL']
    )

    # 19
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'list', '-r'],
        list='Clouds', columns=['Key', 'Value']
    )

    # 20
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'list', '-NV'],
        list='Clouds', columns= ['Project', 'User', 'Cores', 'Group', 'Cloud', 'Enabled', 'Priority', 'URL', 'Name', 'Domain', 'Name', 'Domain', 'ID', 'Name', 'Domain', 'Name', 'Domain', 'ID', 'Region', 'Spot', 'Price', 'Cloud', 'Type', 'Control', 'Cores', 'RAM', 'Cloud', 'Default', 'Cascading', 'Default', 'Group', 'Cloud', 'SoftMax', 'Max', 'Control', 'Max', 'Flavor', 'Image', 'Keep', 'Alive', 'Keyname', 'Network', 'Security', 'Groups', 'Flavor', 'Image', 'Keep', 'Alive', 'Keyname', 'Cascading', 'Default', 'Cloud', 'Metadata', 'Group', 'Cloud', 'Network', 'Security', 'Groups', 'CA', 'Certificate', 'Flavor', 'Exclusions', 'Flavors', 'Group', 'Exclusions', 'Filenames']
    )

if __name__ == "__main__":
    main(None)
