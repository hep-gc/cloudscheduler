from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id, sanity_commands, parameters_commands, table_commands
from sys import argv

# lno: GV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)
    
    # 01 - 14
    sanity_commands(gvar, 'metadata', 'group-defaults')

    parameters = {
        # 15
        '--job-cores': {'valid': 0, 'test_cases': {'invalid-unit-test': 'default update/list value specified for "job_cpus" must be an integer value.'}},
        # 16
        '--job-disk': {'valid': 0, 'test_cases': {'invalid-unit-test': 'default update/list value specified for "job_disk" must be an integer value.'}},
        # 17
        '--job-ram': {'valid': 0, 'test_cases': {'invalid-unit-test': 'default update/list value specified for "job_ram" must be an integer value.'}},
        # 18
        '--job-swap': {'valid': 0, 'test_cases': {'invalid-unit-test': 'default update/list value specified for "job_swap" must be an integer value.'}},
        # 19
        '--vm-keep-alive': {'valid': 0, 'test_cases': {'invalid-unit-test': 'default update/list value specified for "vm_keep_alive" must be an integer value.'}},
        # 20
        '--public-visibility': {'valid': 0, 'test_cases': {'invalid-unit-test': 'default update/list boolean value specified for "public_visibility" must be one of the following: true, false, yes, no, 1, or 0.'}},
    }

    parameters_commands(gvar, 'metadata', 'group-defaults', ut_id(gvar, 'clg1'), ut_id(gvar, 'clu3'), parameters)

    # 21
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: group-name',
        ['metadata', 'group-defaults', '-gn', 'invalid-unit-test', '-g', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu3')]
    )

    # 22
    execute_csv2_command(
        gvar, 0, None, 'group defaults "{}" successfully updated.'.format(ut_id(gvar, 'clg1')),
        ['metadata', 'group-defaults',
            '--job-cores', '1',
            '--job-disk', '1',
            '--job-ram', '1',
            '--job-swap', '1',
            '--vm-keep-alive', '1',
            '--vm-image', '',
            '--vm-keyname', '',
            '--vm-flavor', '',
            '--vm-network', '',
            '--public-visibility', 'no',
            '-su', ut_id(gvar, 'clu3')]
    )

    # 23
    execute_csv2_command(
        gvar, 0, None, None,
        ['metadata', 'group-defaults', '-ok', '-su', ut_id(gvar, 'clu3')],
        expected_list='Active Group Defaults', expected_columns={'Group'}
    )

    table_headers = {
        # 24 - 30
        'Active Group Defaults': ['Group', 'HTCondor', 'FQDN', 'Container Hostname', 'Other Submitters', 'Public Visibility', 'VM', 'Flavor', 'Image', 'Keep Alive', 'Keyname', 'Network', 'Security Groups', 'Job', 'Cores', 'Disk (GBs)', 'RAM (MBs)', 'Swap (GBs)'],
        # 31 - 40
        'Flavors': ['Group', 'Cloud', 'Flavor'],
        # 41 - 50
        'Images': ['Group', 'Cloud', 'Flavor'],
        # The Keyname, Networks, and Security Groups tables have been omitted.
    }

    table_commands(gvar, 'metadata', 'group-defaults', ut_id(gvar, 'clg1'), ut_id(gvar, 'clu3'), table_headers)

    # 51
    execute_csv2_command(
        gvar, 0, None, '''metadata group-defaults, 1. Active Group Defaults: keys=group_name, columns=htcondor_fqdn,htcondor_container_hostname,htcondor_other_submitters,public_visibility,vm_flavor,vm_image,vm_keep_alive,vm_keyname,vm_network,vm_security_groups,job_cpus,job_disk,job_ram,job_swap
metadata group-defaults, 2. Flavors (optional): keys=group_name,cloud_name, columns=name
metadata group-defaults, 3. Images (optional): keys=group_name,cloud_name, columns=name
metadata group-defaults, 4. Keypairs (optional): keys=group_name,cloud_name,key_name, columns=fingerprint,cloud_type
metadata group-defaults, 5. Networks (optional): keys=group_name,cloud_name, columns=name
metadata group-defaults, 6. Security Groups (optional): keys=group_name,cloud_name, columns=name''',
        ['metadata', 'group-defaults', '-VC', '-su', ut_id(gvar, 'clu3')]
    )

    # 52
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'clu3'), ut_id(gvar, 'clg1')),
        ['metadata', 'group-defaults', '-NV', '-su', ut_id(gvar, 'clu3')],
        expected_list='Active Group Defaults', expected_columns={'Group', 'HTCondor', 'FQDN', 'Container Hostname', 'Other Submitters', 'Public Visibility', 'VM', 'Flavor', 'Image', 'Keep Alive', 'Keyname', 'Network', 'Security Groups', 'Job', 'Cores', 'Disk (GBs)', 'RAM (MBs)', 'Swap (GBs)'}
    )

if __name__ == "__main__":
    main(None)
