from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id
from sys import argv

DEFAULTS_COLUMNS = ['alias-name', 'all', 'backup-key', 'backup-repository', 'cacerts', 'cloud-address', 'cloud-enabled', 'cloud-flavor-exclusion', 'cloud-flavor-option', 'cloud-name', 'cloud-option', 'cloud-password', 'cloud-priority', 'cloud-project', 'cloud-project-domain', 'cloud-project-domain-id', 'cloud-region', 'cloud-spot-price', 'cloud-type', 'cloud-user', 'cloud-user-domain', 'cloud-user-domain-id', 'comma-separated-values', 'comma-separated-values-separator', 'config-category', 'config-key-values', 'default-server', 'ec2-image-architectures', 'ec2-image-like', 'ec2-image-not-like', 'ec2-image-operating-systems', 'ec2-image-owner-aliases', 'ec2-image-owner-ids', 'ec2-instance-type-cores', 'ec2-instance-type-families', 'ec2-instance-type-memory-max-gigabytes-per-core', 'ec2-instance-type-memory-min-gigabytes-per-core', 'ec2-instance-type-operating-systems', 'ec2-instance-type-processor-manufacturers', 'ec2-instance-type-processors', 'expose-API', 'file-path', 'force', 'group', 'group-metadata-exclusion', 'group-metadata-option', 'group-name', 'group-option', 'help', 'htcondor-container-hostname', 'htcondor-fqdn', 'htcondor-users', 'job-cores', 'job-disk', 'job-hold', 'job-id', 'job-image', 'job-priority', 'job-ram', 'job-request-cpus', 'job-request-disk', 'job-request-ram', 'job-request-swap', 'job-requirements', 'job-status', 'job-swap', 'job-target-clouds', 'job-user', 'last-update', 'long-help', 'metadata-enabled', 'metadata-mime-type', 'metadata-name', 'metadata-priority', 'no-limit-default', 'no-view', 'only-keys', 'rotate', 'server', 'server-address', 'server-password', 'server-user', 'show-foreign-vms', 'show-global-status', 'show-jobs-by-target-alias', 'show-slot-detail', 'show-slot-flavors', 'status-refresh-interval', 'super-user', 'text-editor', 'user-common-name', 'user-option', 'user-password', 'username', 'version', 'view', 'view-columns', 'vm-boot-volume', 'vm-cores', 'vm-cores-softmax', 'vm-disk', 'vm-flavor', 'vm-foreign', 'vm-hosts', 'vm-image', 'vm-keep-alive', 'vm-keyname', 'vm-network', 'vm-option', 'vm-ram', 'vm-security-groups', 'vm-status', 'vm-swap', 'with', 'yes']

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)

    # 01
    execute_csv2_command(
        gvar, 1, None, 'No action specified for object "defaults"',
        ['cloudscheduler', 'defaults', '-su', ut_id(gvar, 'clu4')]
    )

    # 02
    execute_csv2_command(
        gvar, 1, None, 'Invalid action "invalid-unit-test" for object "defaults"',
        ['cloudscheduler', 'defaults', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')]
    )

    # 03
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler defaults".',
        ['cloudscheduler', 'defaults', '-h', '-su', ut_id(gvar, 'clu4')]
    )

    # 04
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'defaults', '-H', '-su', ut_id(gvar, 'clu4')]
    )

    #### SET ####

    # 05
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'defaults', 'set', '-xx', 'yy', '-su', ut_id(gvar, 'clu4')]
    )

    # 06
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler defaults set".',
        ['cloudscheduler', 'defaults', 'set', '-h', '-su', ut_id(gvar, 'clu4')]
    )

    # 07
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'defaults', 'set', '-H', '-su', ut_id(gvar, 'clu4')]
    )

    # 08 The defaults for this fake server are deleted by later tests.
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'defaults', 'set', '-s', ut_id(gvar, 'cld1'), '-su', ut_id(gvar, 'clu4')]
    )

    #### LIST ####

    # 09
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'defaults', 'list', '-su', ut_id(gvar, 'clu4')]
    )

    # 10
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'defaults', 'list', '-xx', 'yy', '-su', ut_id(gvar, 'clu4')]
    )

    # 11
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler defaults list".',
        ['cloudscheduler', 'defaults', 'list', '-h', '-su', ut_id(gvar, 'clu4')]
    )

    # 12
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'defaults', 'list', '-H', '-su', ut_id(gvar, 'clu4')]
    )

    # 13
    execute_csv2_command(
        gvar, None, None, 'the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'defaults', 'list', '-s', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')], timeout=8
    )

    # 14
    execute_csv2_command(
        gvar, 0, None, 'Rows: 1',
        ['cloudscheduler', 'defaults', 'list', '-s', ut_id(gvar, 'cld1'), '-su', ut_id(gvar, 'clu4')]
    )

    # 15
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'defaults', 'list', '-ok', '-su', ut_id(gvar, 'clu4')],
        expected_list='', columns=[]
    )

    # 16
    execute_csv2_command(
        gvar, 0, None, ': keys=server, columns=alias-name,all,backup-key,backup-repository,cacerts,cloud-address,cloud-enabled,cloud-flavor-exclusion,cloud-flavor-option,cloud-name,cloud-option,cloud-password,cloud-priority,cloud-project,cloud-project-domain,cloud-project-domain-id,cloud-region,cloud-spot-price,cloud-type,cloud-user,cloud-user-domain,cloud-user-domain-id,comma-separated-values,comma-separated-values-separator,config-category,config-key-values,default-server,ec2-image-architectures,ec2-image-like,ec2-image-not-like,ec2-image-operating-systems,ec2-image-owner-aliases,ec2-image-owner-ids,ec2-instance-type-cores,ec2-instance-type-families,ec2-instance-type-memory-max-gigabytes-per-core,ec2-instance-type-memory-min-gigabytes-per-core,ec2-instance-type-operating-systems,ec2-instance-type-processor-manufacturers,ec2-instance-type-processors,expose-API,file-path,force,group,group-metadata-exclusion,group-metadata-option,group-name,group-option,help,htcondor-container-hostname,htcondor-fqdn,htcondor-users,job-cores,job-disk,job-hold,job-id,job-image,job-priority,job-ram,job-request-cpus,job-request-disk,job-request-ram,job-request-swap,job-requirements,job-status,job-swap,job-target-clouds,job-user,last-update,long-help,metadata-enabled,metadata-mime-type,metadata-name,metadata-priority,no-limit-default,no-view,only-keys,rotate,server-address,server-password,server-user,show-foreign-vms,show-global-status,show-jobs-by-target-alias,show-slot-detail,show-slot-flavors,status-refresh-interval,super-user,text-editor,user-common-name,user-option,user-password,username,version,view,view-columns,vm-boot-volume,vm-cores,vm-cores-softmax,vm-disk,vm-flavor,vm-foreign,vm-hosts,vm-image,vm-keep-alive,vm-keyname,vm-network,vm-option,vm-ram,vm-security-groups,vm-status,vm-swap,with,yes',
        ['cloudscheduler', 'defaults', 'list', '-VC', '-su', ut_id(gvar, 'clu4')]
    )

    # 17
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'defaults', 'list', '-NV', '-su', ut_id(gvar, 'clu4')],
        expected_list='Defaults', columns=DEFAULTS_COLUMNS
    )

    # 18
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'defaults', 'list', '-V', 'server-address,server-user', '-su', ut_id(gvar, 'clu4')],
        expected_list='Defaults', columns=['server', 'server-address', 'server-user']
    )

    # 19
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'defaults', 'list', '-su', ut_id(gvar, 'clu4')],
        expected_list='Defaults', columns=['server', 'server-address', 'server-user']
    )

    # 20
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'defaults', 'list', '-V', '', '-su', ut_id(gvar, 'clu4')],
        expected_list='Defaults', columns=DEFAULTS_COLUMNS
    )

    # 21
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'defaults', 'list', '-r', '-su', ut_id(gvar, 'clu4')],
        expected_list='Defaults', columns=['Key', 'Value']
    )

    #### DELETE ####

    # 22
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'defaults', 'delete', '-xx', 'yy', '-su', ut_id(gvar, 'clu4')]
    )

    # 23
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler defaults delete".',
        ['cloudscheduler', 'defaults', 'delete', '-h', '-su', ut_id(gvar, 'clu4')]
    )

    # 24
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'defaults', 'delete', '-H', '-su', ut_id(gvar, 'clu4')]
    )

    # 25
    execute_csv2_command(
        gvar, None, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'defaults', 'delete', '-s', 'invalid-unit-test', '-su', ut_id(gvar, 'clu4')], timeout=8
    )

    # 26 Delete defaults created earlier.
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'defaults', 'delete', '-s', ut_id(gvar, 'cld1'), '-Y', '-su', ut_id(gvar, 'clu4')]
    )

    # 27
    execute_csv2_command(
        gvar, None, None, None,
        ['cloudscheduler', 'defaults', '-su', ut_id(gvar, 'clu4')]
    )

if __name__ == "__main__":
    main(None)
