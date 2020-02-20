from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id
from sys import argv

# lno: GV - error code identifier.

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)
    
    # 01
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}'.format(ut_id(gvar, 'clu4')),
        ['cloudscheduler', 'metadata', 'group-defaults', '-su', ut_id(gvar, 'clu4')]
    )

    # 02
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'metadata', 'group-defaults', '-xx', 'yy', '-su', ut_id(gvar, 'clu4')]
    )

    # 03
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: group-name',
        ['cloudscheduler', 'metadata', 'group-defaults', '-gn', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 04
    execute_csv2_command(
        gvar, None, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'metadata', 'group-defaults', '-s', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')], timeout=8
    )

    # 05
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'metadata', 'group-defaults', '-su', ut_id(gvar, 'clu4')]
    )

    # 06
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler metadata group-defaults".',
        ['cloudscheduler', 'metadata', 'group-defaults', '-h', '-su', ut_id(gvar, 'clu4')]
    )

    # 07
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'metadata', 'group-defaults', '-H', '-su', ut_id(gvar, 'clu4')]
    )

    # 08
    execute_csv2_command(
        gvar, 0, None, 'Expose API requested',
        ['cloudscheduler', 'metadata', 'group-defaults', '-xA', '-su', ut_id(gvar, 'clu4')]
    )

    # 09
    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'metadata', 'group-defaults', '-g', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 10
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'clu4'), ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'metadata', 'group-defaults', '-g', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu4')]
    )

    # 11
    execute_csv2_command(
        gvar, 1, 'GV', 'default update/list value specified for "job_cpus" must be an integer value.',
        ['cloudscheduler', 'metadata', 'group-defaults', '-jc', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 12
    execute_csv2_command(
        gvar, 1, 'GV', 'default update/list value specified for "job_disk" must be an integer value.',
        ['cloudscheduler', 'metadata', 'group-defaults', '-jd', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 13
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-jed\', \'invalid-unit-test\']',
        ['cloudscheduler', 'metadata', 'group-defaults', '-jed', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 14
    execute_csv2_command(
        gvar, 1, 'GV', 'default update/list value specified for "job_ram" must be an integer value.',
        ['cloudscheduler', 'metadata', 'group-defaults', '-jr', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 15
    execute_csv2_command(
        gvar, 1, 'GV', 'default update/list value specified for "job_swap" must be an integer value.',
        ['cloudscheduler', 'metadata', 'group-defaults', '-js', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 16
    execute_csv2_command(
        gvar, 1, 'GV', 'default update/list value specified for "vm_keep_alive" must be an integer value.',
        ['cloudscheduler', 'metadata', 'group-defaults', '-vka', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 17
    execute_csv2_command(
        gvar, 0, None, 'group defaults "{}" successfully updated.'.format(ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'metadata', 'group-defaults', '-jc', '1', '-jd', '1', '-jr', '1', '-js', '1', '-vka', '1', '-vi', '', '-vk', '', '-vf', '', '-vn', '', '-su', ut_id(gvar, 'clu4')]
    )

    # 18
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'metadata', 'group-defaults', '-ok', '-su', ut_id(gvar, 'clu4')],
        expected_list='Active Group Defaults', columns=['Group']
    )

    # 19
    execute_csv2_command(
        gvar, 0, None, '''metadata group-defaults, 1. Active Group Defaults: keys=group_name, columns=htcondor_fqdn,htcondor_container_hostname,htcondor_other_submitters,vm_flavor,vm_image,vm_keep_alive,vm_keyname,vm_network,vm_security_groups,job_cpus,job_disk,job_ram,job_swap
metadata group-defaults, 2. Flavors (optional): keys=group_name,cloud_name, columns=name
metadata group-defaults, 3. Images (optional): keys=group_name,cloud_name, columns=name
metadata group-defaults, 4. Keypairs (optional): keys=group_name,cloud_name,key_name, columns=fingerprint,cloud_type
metadata group-defaults, 5. Networks (optional): keys=group_name,cloud_name, columns=name
metadata group-defaults, 6. Security Groups (optional): keys=group_name,cloud_name, columns=name''',
        ['cloudscheduler', 'metadata', 'group-defaults', '-VC', '-su', ut_id(gvar, 'clu4')]
    )

    # 20
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'metadata', 'group-defaults', '-NV', '-su', ut_id(gvar, 'clu4')],
        expected_list='Active Group Defaults', columns=['Group', 'HTCondor', 'FQDN', 'Container Hostname', 'Other Submitters', 'VM', 'Flavor', 'Image', 'Keep Alive', 'Keyname', 'Network', 'Security Groups', 'Job', 'Cores', 'Disk (GBs)', 'RAM (MBs)', 'Swap (GBs)']
    )

    # 21
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'metadata', 'group-defaults', '-V', 'job_ram,vm_keep_alive', '-su', ut_id(gvar, 'clu4')],
        expected_list='Active Group Defaults', columns=['Group', 'VM', 'Keep Alive', 'Job', 'RAM (MBs)']
    )

    # 22
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'metadata', 'group-defaults', '-su', ut_id(gvar, 'clu4')],
        expected_list='Active Group Defaults', columns=['Group', 'VM', 'Keep Alive', 'Job', 'RAM (MBs)']
    )

    # 23
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'metadata', 'group-defaults', '-r', '-su', ut_id(gvar, 'clu4')],
        expected_list='Active Group Defaults', columns=['Key', 'Value']
    )

    # 24
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'metadata', 'group-defaults', '-V', '', '-su', ut_id(gvar, 'clu4')],
        expected_list='Active Group Defaults', columns=['Group', 'HTCondor', 'FQDN', 'Container Hostname', 'Other Submitters', 'VM', 'Flavor', 'Image', 'Keep Alive', 'Keyname', 'Network', 'Security Groups', 'Job', 'Cores', 'Disk (GBs)', 'RAM (MBs)', 'Swap (GBs)']
    )

if __name__ == "__main__":
    main(None)
