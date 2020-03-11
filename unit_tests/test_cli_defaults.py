from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id, sanity_commands
from sys import argv

DEFAULTS_COLUMNS = ['alias-name', 'all', 'backup-key', 'backup-repository', 'cacerts', 'cloud-address', 'cloud-enabled', 'cloud-flavor-exclusion', 'cloud-flavor-option', 'cloud-name', 'cloud-option', 'cloud-password', 'cloud-priority', 'cloud-project', 'cloud-project-domain', 'cloud-project-domain-id', 'cloud-region', 'cloud-spot-price', 'cloud-type', 'cloud-user', 'cloud-user-domain', 'cloud-user-domain-id', 'comma-separated-values', 'comma-separated-values-separator', 'config-category', 'config-key-values', 'default-server', 'ec2-image-architectures', 'ec2-image-like', 'ec2-image-not-like', 'ec2-image-operating-systems', 'ec2-image-owner-aliases', 'ec2-image-owner-ids', 'ec2-instance-type-cores', 'ec2-instance-type-families', 'ec2-instance-type-memory-max-gigabytes-per-core', 'ec2-instance-type-memory-min-gigabytes-per-core', 'ec2-instance-type-operating-systems', 'ec2-instance-type-processor-manufacturers', 'ec2-instance-type-processors', 'expose-API', 'file-path', 'force', 'group', 'group-metadata-exclusion', 'group-metadata-option', 'group-name', 'group-option', 'help', 'htcondor-container-hostname', 'htcondor-fqdn', 'htcondor-users', 'job-cores', 'job-disk', 'job-hold', 'job-id', 'job-image', 'job-priority', 'job-ram', 'job-request-cpus', 'job-request-disk', 'job-request-ram', 'job-request-swap', 'job-requirements', 'job-status', 'job-swap', 'job-target-clouds', 'job-user', 'last-update', 'long-help', 'metadata-enabled', 'metadata-mime-type', 'metadata-name', 'metadata-priority', 'no-limit-default', 'no-view', 'only-keys', 'rotate', 'server', 'server-address', 'server-password', 'server-user', 'show-foreign-vms', 'show-global-status', 'show-jobs-by-target-alias', 'show-slot-detail', 'show-slot-flavors', 'status-refresh-interval', 'super-user', 'text-editor', 'user-common-name', 'user-option', 'user-password', 'username', 'version', 'view', 'view-columns', 'vm-boot-volume', 'vm-cores', 'vm-cores-softmax', 'vm-disk', 'vm-flavor', 'vm-foreign', 'vm-hosts', 'vm-image', 'vm-keep-alive', 'vm-keyname', 'vm-network', 'vm-option', 'vm-ram', 'vm-security-groups', 'vm-status', 'vm-swap', 'with', 'yes']

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)

    # 01 - 13
    sanity_commands(gvar, 'defaults')

    #### SET ####

    # 14 - 27
    sanity_commands(gvar, 'defaults', 'set')

    # 28 The defaults for this fake server are deleted by later tests.
    execute_csv2_command(
        gvar, 0, None, None,
        ['defaults', 'set', '-s', ut_id(gvar, 'cld1'), '-su', ut_id(gvar, 'clu3')]
    )

    #### LIST ####

    # 29 - 42
    sanity_commands(gvar, 'defaults', 'list')

    # 43
    execute_csv2_command(
        gvar, 0, None, None,
        ['defaults', 'list', '-su', ut_id(gvar, 'clu3')]
    )

    # 44
    execute_csv2_command(
        gvar, 0, None, 'Rows: 1',
        ['defaults', 'list', '-s', ut_id(gvar, 'cld1'), '-su', ut_id(gvar, 'clu3')]
    )

    # 45
    execute_csv2_command(
        gvar, 0, None, None,
        ['defaults', 'list', '-ok', '-su', ut_id(gvar, 'clu3')],
        expected_list='', columns=[]
    )

    # 46
    execute_csv2_command(
        gvar, 0, None, ': keys=server, columns=alias-name,all,backup-key,backup-repository,cacerts,cloud-address,cloud-enabled,cloud-flavor-exclusion,cloud-flavor-option,cloud-name,cloud-option,cloud-password,cloud-priority,cloud-project,cloud-project-domain,cloud-project-domain-id,cloud-region,cloud-spot-price,cloud-type,cloud-user,cloud-user-domain,cloud-user-domain-id,comma-separated-values,comma-separated-values-separator,config-category,config-key-values,default-server,ec2-image-architectures,ec2-image-like,ec2-image-not-like,ec2-image-operating-systems,ec2-image-owner-aliases,ec2-image-owner-ids,ec2-instance-type-cores,ec2-instance-type-families,ec2-instance-type-memory-max-gigabytes-per-core,ec2-instance-type-memory-min-gigabytes-per-core,ec2-instance-type-operating-systems,ec2-instance-type-processor-manufacturers,ec2-instance-type-processors,expose-API,file-path,force,group,group-metadata-exclusion,group-metadata-option,group-name,group-option,help,htcondor-container-hostname,htcondor-fqdn,htcondor-users,job-cores,job-disk,job-hold,job-id,job-image,job-priority,job-ram,job-request-cpus,job-request-disk,job-request-ram,job-request-swap,job-requirements,job-status,job-swap,job-target-clouds,job-user,last-update,long-help,metadata-enabled,metadata-mime-type,metadata-name,metadata-priority,no-limit-default,no-view,only-keys,rotate,server-address,server-password,server-user,show-foreign-vms,show-global-status,show-jobs-by-target-alias,show-slot-detail,show-slot-flavors,status-refresh-interval,super-user,text-editor,user-common-name,user-option,user-password,username,version,view,view-columns,vm-boot-volume,vm-cores,vm-cores-softmax,vm-disk,vm-flavor,vm-foreign,vm-hosts,vm-image,vm-keep-alive,vm-keyname,vm-network,vm-option,vm-ram,vm-security-groups,vm-status,vm-swap,with,yes',
        ['defaults', 'list', '-VC', '-su', ut_id(gvar, 'clu3')]
    )

    # 47
    execute_csv2_command(
        gvar, 0, None, None,
        ['defaults', 'list', '-NV', '-su', ut_id(gvar, 'clu3')],
        expected_list='Defaults', columns=DEFAULTS_COLUMNS
    )

    # 48
    execute_csv2_command(
        gvar, 0, None, None,
        ['defaults', 'list', '-V', 'server-address,server-user', '-su', ut_id(gvar, 'clu3')],
        expected_list='Defaults', columns=['server', 'server-address', 'server-user']
    )

    # 49
    execute_csv2_command(
        gvar, 0, None, None,
        ['defaults', 'list', '-su', ut_id(gvar, 'clu3')],
        expected_list='Defaults', columns=['server', 'server-address', 'server-user']
    )

    # 50
    execute_csv2_command(
        gvar, 0, None, '.',
        ['defaults', 'list', '-CSV', '', '-CSEP', '.', '-su', ut_id(gvar, 'clu3')],
    )

    # 51
    execute_csv2_command(
        gvar, 0, None, None,
        ['defaults', 'list', '-V', '', '-su', ut_id(gvar, 'clu3')],
        expected_list='Defaults', columns=DEFAULTS_COLUMNS
    )

    # 52
    execute_csv2_command(
        gvar, 0, None, None,
        ['defaults', 'list', '-r', '-su', ut_id(gvar, 'clu3')],
        expected_list='Defaults', columns=['Key', 'Value']
    )

    #### DELETE ####

    # 53 - 66
    sanity_commands(gvar, 'defaults', 'delete')

    # 67 Delete defaults created earlier.
    execute_csv2_command(
        gvar, 0, None, None,
        ['defaults', 'delete', '-s', ut_id(gvar, 'cld1'), '-Y', '-su', ut_id(gvar, 'clu3')]
    )

    # 68
    execute_csv2_command(
        gvar, None, None, None,
        ['cloudscheduler', 'defaults', '-su', ut_id(gvar, 'clu4')]
    )

if __name__ == "__main__":
    main(None)
