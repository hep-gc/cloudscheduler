from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id
from sys import argv

# lno: CV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv2_request(gvar, argv[0])

    # 01
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'cloud', 'list', '-g', ut_id(gvar, 'clg1'), '-xx', 'yy', '-su', ut_id(gvar, 'clu4')]
    )

    # 02
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: metadata-mime-type',
        ['cloudscheduler', 'cloud', 'list', '-mmt', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 03
    execute_csv2_command(
        gvar, None, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'cloud', 'list', '-s', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')], timeout=8
    )

    # 04
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'list', '-su', ut_id(gvar, 'clu4')]
    )

    # 05
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler cloud list".',
        ['cloudscheduler', 'cloud', 'list', '-h', '-su', ut_id(gvar, 'clu4')]
    )

    # 06
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'cloud', 'list', '-H', '-su', ut_id(gvar, 'clu4')]
    )

    # 07
    execute_csv2_command(
        gvar, 0, None, 'Expose API requested',
        ['cloudscheduler', 'cloud', 'list', '-xA', '-su', ut_id(gvar, 'clu4')]
    )

    # 08
    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'cloud', 'list', '-g', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 09
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'clu4'), ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'cloud', 'list', '-su', ut_id(gvar, 'clu4')]
    )

    # 10
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'clu4'), ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'cloud', 'list', '-g', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu4')]
    )

    # 11
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'clu4'), ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'cloud', 'list', '-su', ut_id(gvar, 'clu4')]
    )

    # 12
    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'cloud', 'list', '-cn', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 13
    execute_csv2_command(
        gvar, 0, None, 'Rows: 1',
        ['cloudscheduler', 'cloud', 'list', '-cn', ut_id(gvar, 'clc2'), '-su', ut_id(gvar, 'clu4')]
    )

    # 14
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'list', '-ok', '-su', ut_id(gvar, 'clu4')],
        expected_list='Clouds', columns=['Group', 'Cloud']
    )

    # 15
    execute_csv2_command(
        gvar, 0, None,
        'cloud list, 1. Clouds: keys=group_name,cloud_name, columns=enabled,cloud_priority,authurl,project,project_domain_name,project_domain_id,username,user_domain_name,user_domain_id,region,spot_price,cloud_type,cores_ctl,cores_softmax,cores_max,ram_ctl,ram_max,vm_boot_volume,vm_flavor,vm_image,vm_keep_alive,vm_keyname,vm_network,vm_security_groups,cascading_vm_flavor,cascading_vm_image,cascading_vm_keep_alive,cascading_vm_keyname,cascading_vm_network,cascading_vm_security_groups,cacertificate,flavor_exclusions,flavor_names,group_exclusions,metadata_names\n' +
        'cloud list, 2. Flavors (optional): keys=group_name,cloud_name, columns=name\n' +
        'cloud list, 3. Images (optional): keys=group_name,cloud_name, columns=name\n' +
        'cloud list, 4. Networks (optional): keys=group_name,cloud_name, columns=name\n' +
        'cloud list, 5. Security Groups (optional): keys=group_name,cloud_name, columns=name\n',
        ['cloudscheduler', 'cloud', 'list', '-VC', '-su', ut_id(gvar, 'clu4')]
    )

    # 16
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'list', '-NV', '-su', ut_id(gvar, 'clu4')],
        expected_list='Clouds', columns=['Group', 'Cloud', 'Enabled', 'Priority', 'URL', 'Project', 'Name', 'Domain Name', 'Domain ID', 'User', 'Name', 'Domain Name', 'Domain ID', 'Region', 'Spot Price', 'Cloud Type', 'Cores', 'Control', 'SoftMax', 'Max', 'RAM', 'Control', 'Max', 'Cloud Default', 'Boot Volume', 'Flavor', 'Image', 'Keep Alive', 'Keyname', 'Network', 'Security Groups', 'Cascading Default', 'Flavor', 'Image', 'Keep Alive', 'Keyname', 'Network', 'Security Groups', 'CA Certificate', 'Cloud', 'Flavor Exclusions', 'Flavors', 'Metadata', 'Group Exclusions', 'Filenames']
    )

    # 17
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'list', '-V', 'enabled,authurl', '-su', ut_id(gvar, 'clu4')],
        expected_list='Clouds', columns=['Group', 'Cloud', 'Enabled', 'URL']
    )

    # 18
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'list', '-su', ut_id(gvar, 'clu4')],
        expected_list='Clouds', columns=['Group', 'Cloud', 'Enabled', 'URL']
    )

    # 19
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'list', '-r', '-su', ut_id(gvar, 'clu4')],
        expected_list='Clouds', columns=['Key', 'Value']
    )

if __name__ == "__main__":
    main(None)
