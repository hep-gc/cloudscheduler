from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id
from sys import argv

DEFAULTS_COLUMNS = {'alias-name', 'all', 'backup-key', 'backup-repository', 'cacerts', 'cloud-address', 'cloud-enabled', 'cloud-flavor-exclusion', 'cloud-flavor-option', 'cloud-name', 'cloud-option', 'cloud-password', 'cloud-priority', 'cloud-project', 'cloud-project-domain', 'cloud-project-domain-id', 'cloud-region', 'cloud-spot-price', 'cloud-type', 'cloud-user', 'cloud-user-domain', 'cloud-user-domain-id', 'comma-separated-values', 'comma-separated-values-separator', 'config-category', 'config-key-values', 'default-server', 'ec2-image-architectures', 'ec2-image-like', 'ec2-image-not-like', 'ec2-image-operating-systems', 'ec2-image-owner-aliases', 'ec2-image-owner-ids', 'ec2-instance-type-cores', 'ec2-instance-type-families', 'ec2-instance-type-memory-max-gigabytes-per-core', 'ec2-instance-type-memory-min-gigabytes-per-core', 'ec2-instance-type-operating-systems', 'ec2-instance-type-processor-manufacturers', 'ec2-instance-type-processors', 'expose-API', 'file-path', 'force', 'group', 'group-metadata-exclusion', 'group-metadata-option', 'group-name', 'group-option', 'help', 'htcondor-container-hostname', 'htcondor-fqdn', 'htcondor-users', 'job-cores', 'job-disk', 'job-hold', 'job-id', 'job-image', 'job-priority', 'job-ram', 'job-request-cpus', 'job-request-disk', 'job-request-ram', 'job-request-swap', 'job-requirements', 'job-status', 'job-swap', 'job-target-alias', 'job-user', 'last-update', 'long-help', 'metadata-enabled', 'metadata-mime-type', 'metadata-name', 'metadata-priority', 'no-limit-default', 'no-view', 'only-keys', 'rotate', 'server', 'server-address', 'server-password', 'server-user', 'show-foreign-vms', 'show-global-status', 'show-jobs-by-target-alias', 'show-slot-detail', 'show-slot-flavors', 'status-refresh-interval', 'super-user', 'text-editor', 'user-common-name', 'user-option', 'user-password', 'username', 'version', 'view', 'view-columns', 'vm-boot-volume', 'vm-cores', 'vm-cores-softmax', 'vm-disk', 'vm-flavor', 'vm-foreign', 'vm-hosts', 'vm-image', 'vm-keep-alive', 'vm-keyname', 'vm-network', 'vm-option', 'vm-ram', 'vm-security-groups', 'vm-status', 'vm-swap', 'with', 'yes', 'target-group', 'image-checksum', 'disk-format', 'image-name', 'image-index', 'image-path', 'image-date', 'image-format', 'use-x509-authentication', 'cloud-list', 'target-cloud', 'cloud-app-credentials-secret', 'cloud-app-credentials', 'user-id'}

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)
    
    # `defaults *` break the patterns that `sanity_commands()` relies on, so we cannot use it anywhere in this file.
    # 01
    execute_csv2_command(
        gvar, 1, None, 'No action specified for object "defaults"',
        ['defaults', '-su', ut_id(gvar, 'clu3')]
    )

    # 02
    execute_csv2_command(
        gvar, 1, None, 'Invalid action "invalid-unit-test" for object "defaults"',
        ['defaults', 'invalid-unit-test', '-su', ut_id(gvar, 'clu3')]
    )

    # 03
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler defaults".',
        ['defaults', '-h', '-su', ut_id(gvar, 'clu3')]
    )

    # 04
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['defaults', '-H', '-su', ut_id(gvar, 'clu3')]
    )

    #### SET ####

    # 05
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'--invalid-unit-test\', \'invalid-unit-test\']',
        ['defaults', 'set', '--invalid-unit-test', 'invalid-unit-test', '-g', ut_id(gvar, 'clg1'), '-su', ut_id(gvar, 'clu3')]
    )

    # 06
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler defaults set".',
        ['defaults', 'set', '-h', '-su', ut_id(gvar, 'clu3')]
    )

    # 07
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['defaults', 'set', '-H', '-su', ut_id(gvar, 'clu3')]
    )

    # 08 The defaults for this fake server are deleted by later tests.
    execute_csv2_command(
        gvar, 0, None, None,
        ['defaults', 'set', '-s', ut_id(gvar, 'cld1'), '--server-address', gvar['user_settings']['server-address'], '--cloud-enabled', 0, '-su', ut_id(gvar, 'clu3')]
    )

    #### LIST ####

    # 09
    execute_csv2_command(
        gvar, 0, None, None,
        ['defaults', 'list', '-su', ut_id(gvar, 'clu3')]
    )

    # 10
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'--invalid-unit-test\', \'invalid-unit-test\']',
        ['defaults', 'list', '--invalid-unit-test', 'invalid-unit-test', '-su', ut_id(gvar, 'clu3')]
    )

    # 11
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler defaults list".',
        ['defaults', 'list', '-h', '-su', ut_id(gvar, 'clu3')]
    )

    # 12
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['defaults', 'list', '-H', '-su', ut_id(gvar, 'clu3')]
    )

    # 13
    execute_csv2_command(
        gvar, None, None, 'the specified server "invalid-unit-test" does not exist in your defaults.',
        ['defaults', 'list', '-s', 'invalid-unit-test', '-su', ut_id(gvar, 'clu3')], timeout=8
    )

    # `defaults list` breaks the patterns that `table_commands()` relies on, so we cannot use it here.
    # 14
    execute_csv2_command(
        gvar, 0, None, ': keys=server, columns=alias-name,all,backup-key,backup-repository,cacerts,cloud-address,cloud-app-credentials,cloud-app-credentials-secret,cloud-enabled,cloud-flavor-exclusion,cloud-flavor-option,cloud-list,cloud-name,cloud-option,cloud-password,cloud-priority,cloud-project,cloud-project-domain,cloud-project-domain-id,cloud-region,cloud-spot-price,cloud-type,cloud-user,cloud-user-domain,cloud-user-domain-id,comma-separated-values,comma-separated-values-separator,config-category,config-key-values,default-server,disk-format,ec2-image-architectures,ec2-image-like,ec2-image-not-like,ec2-image-operating-systems,ec2-image-owner-aliases,ec2-image-owner-ids,ec2-instance-type-cores,ec2-instance-type-families,ec2-instance-type-memory-max-gigabytes-per-core,ec2-instance-type-memory-min-gigabytes-per-core,ec2-instance-type-operating-systems,ec2-instance-type-processor-manufacturers,ec2-instance-type-processors,expose-API,file-path,force,group,group-metadata-exclusion,group-metadata-option,group-name,group-option,help,htcondor-container-hostname,htcondor-fqdn,htcondor-users,image-checksum,image-date,image-format,image-index,image-name,image-path,job-cores,job-disk,job-hold,job-id,job-image,job-priority,job-ram,job-request-cpus,job-request-disk,job-request-ram,job-request-swap,job-requirements,job-status,job-swap,job-target-alias,job-user,last-update,long-help,metadata-enabled,metadata-mime-type,metadata-name,metadata-priority,no-limit-default,no-view,only-keys,rotate,server-address,server-password,server-user,show-foreign-vms,show-global-status,show-jobs-by-target-alias,show-slot-detail,show-slot-flavors,status-refresh-interval,super-user,target-cloud,target-group,text-editor,use-x509-authentication,user-common-name,user-id,user-option,user-password,username,version,view,view-columns,vm-boot-volume,vm-cores,vm-cores-softmax,vm-disk,vm-flavor,vm-foreign,vm-hosts,vm-image,vm-keep-alive,vm-keyname,vm-network,vm-option,vm-ram,vm-security-groups,vm-status,vm-swap,with,yes',
        ['defaults', 'list', '-VC', '-su', ut_id(gvar, 'clu3')]
    )

    # 15
    execute_csv2_command(
        gvar, 0, None, 'Rows: 1',
        ['defaults', 'list', '-s', ut_id(gvar, 'cld1'), '-su', ut_id(gvar, 'clu3')]
    )

    # 16
    execute_csv2_command(
        gvar, 0, None, None,
        ['defaults', 'list', '-ok', '-su', ut_id(gvar, 'clu3')],
        expected_list='', expected_columns={}
    )

    # 17
    execute_csv2_command(
        gvar, 0, None, None,
        ['defaults', 'list', '-NV', '-su', ut_id(gvar, 'clu3')],
        expected_list='Defaults', expected_columns=DEFAULTS_COLUMNS
    )

    # 18
    execute_csv2_command(
        gvar, 0, None, None,
        ['defaults', 'list', '-V', 'server-address,server-user', '-su', ut_id(gvar, 'clu3')],
        expected_list='Defaults', expected_columns={'server', 'server-address', 'server-user'}
    )

    # 19
    execute_csv2_command(
        gvar, 0, None, None,
        ['defaults', 'list', '-su', ut_id(gvar, 'clu3')],
        expected_list='Defaults', expected_columns={'server', 'server-address', 'server-user'}
    )

    # 20
    execute_csv2_command(
        gvar, 0, None, None,
        ['defaults', 'list', '-V', '', '-su', ut_id(gvar, 'clu3')],
        expected_list='Defaults', expected_columns=DEFAULTS_COLUMNS
    )

    # 21
    execute_csv2_command(
        gvar, 0, None, None,
        ['defaults', 'list', '-r', '-su', ut_id(gvar, 'clu3')],
        expected_list='Defaults', expected_columns={'Key', 'Value'}
    )

    #### DELETE ####

    # 22
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'--invalid-unit-test\', \'invalid-unit-test\']',
        ['defaults', 'delete', '--invalid-unit-test', 'invalid-unit-test', '-su', ut_id(gvar, 'clu3')]
    )

    # 23
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler defaults delete".',
        ['defaults', 'delete', '-h', '-su', ut_id(gvar, 'clu3')]
    )

    # 24
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['defaults', 'delete', '-H', '-su', ut_id(gvar, 'clu3')]
    )

    # 25
    execute_csv2_command(
        gvar, None, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['defaults', 'delete', '-s', 'invalid-unit-test', '-su', ut_id(gvar, 'clu3')], timeout=8
    )

    # 26 Delete defaults created earlier.
    execute_csv2_command(
        gvar, 0, None, None,
        ['defaults', 'delete', '-s', ut_id(gvar, 'cld1'), '-Y', '-su', ut_id(gvar, 'clu3')]
    )

    # 27
    execute_csv2_command(
        gvar, None, None, None,
        ['defaults', '-su', ut_id(gvar, 'clu3')]
    )

if __name__ == "__main__":
    main(None)
