from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id, sanity_commands, table_commands
from sys import argv

# lno: CV - error code identifier.

def main(gvar):

    # 01 - 14
    sanity_commands(gvar, 'cloud', 'list')

    # 15
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: metadata-mime-type',
        ['cloud', 'list', '-mmt', 'invalid-unit-test', '-g', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu3')]
    )

    # 16
    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloud', 'list', '-cn', 'valid-unit-test', '-su', ut_id(gvar, 'clu3')]
    )

    # 17
    execute_csv2_command(
        gvar, 0, None, 'Rows: 1',
        ['cloud', 'list', '-cn', ut_id(gvar, 'clc2'), '-su', ut_id(gvar, 'clu3')]
    )

    # 18
    execute_csv2_command(
        gvar, 0, None,
        'cloud list, 1. Clouds: keys=group_name,cloud_name, columns=enabled,cloud_priority,authurl,project,project_domain_name,project_domain_id,username,user_domain_name,user_domain_id,region,spot_price,cloud_type,cores_ctl,cores_softmax,cores_max,ram_ctl,ram_max,vm_boot_volume,vm_flavor,vm_image,vm_keep_alive,vm_keyname,vm_network,vm_security_groups,cascading_vm_flavor,cascading_vm_image,cascading_vm_keep_alive,cascading_vm_keyname,cascading_vm_network,cascading_vm_security_groups,cacertificate,flavor_exclusions,flavor_names,group_exclusions,metadata_names\n' +
        'cloud list, 2. Flavors (optional): keys=group_name,cloud_name, columns=name\n' +
        'cloud list, 3. Images (optional): keys=group_name,cloud_name, columns=name\n' +
        'cloud list, 4. Networks (optional): keys=group_name,cloud_name, columns=name\n' +
        'cloud list, 5. Security Groups (optional): keys=group_name,cloud_name, columns=name\n',
        ['cloud', 'list', '-VC', '-su', ut_id(gvar, 'clu3')]
    )

    table_headers = {
        'Clouds': ['Group', 'Cloud', 'Enabled', 'Priority', 'URL', 'Project', 'Name', 'Domain Name', 'Domain ID', 'User', 'Name', 'Domain Name', 'Domain ID', 'Region', 'Spot Price', 'Cloud Type', 'Cores', 'Control', 'SoftMax', 'Max', 'RAM', 'Control', 'Max', 'Cloud Default', 'Boot Volume', 'Flavor', 'Image', 'Keep Alive', 'Keyname', 'Network', 'Security Groups', 'Cascading Default', 'Flavor', 'Image', 'Keep Alive', 'Keyname', 'Network', 'Security Groups', 'CA Certificate', 'Cloud', 'Flavor Exclusions', 'Flavors', 'Metadata', 'Group Exclusions', 'Filenames']
    }

    # 19 - 25
    table_commands(gvar, 'cloud', 'list', ut_id(gvar, 'clg1'), ut_id(gvar, 'clu3'), table_headers)

if __name__ == "__main__":
    main(initialize_csv2_request(selections=argv[1] if len(argv) > 1 else ''))
