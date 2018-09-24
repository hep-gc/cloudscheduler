from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id
import sys

def main(gvar, user_secret):
    if not gvar:
        gvar = {}
        if len(sys.argv) > 1:
            initialize_csv2_request(gvar, sys.argv[0], selections=sys.argv[1])
        else:
            initialize_csv2_request(gvar, sys.argv[0])
    
    execute_csv2_command(
        gvar, 1, None, 'No action specified for object "defaults"',
        ['cloudscheduler', 'defaults']
    )

    execute_csv2_command(
        gvar, 1, None, 'Invalid action "invalid-unit-test" for object "defaults"',
        ['cloudscheduler', 'defaults', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler defaults".',
        ['cloudscheduler', 'defaults', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'defaults', '-H']
    )

    #### SET ####

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'defaults', 'set']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'defaults', 'set', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler defaults set".',
        ['cloudscheduler', 'defaults', 'set', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'defaults', 'set', '-H']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'defaults', 'set', '-s', ut_id(gvar, 'cld1')]
    )

    #### LIST ####

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'defaults', 'list']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'defaults', 'list', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler defaults list".',
        ['cloudscheduler', 'defaults', 'list', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'defaults', 'list', '-H']
    )

    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'defaults', 'list', '-s', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Rows: 1',
        ['cloudscheduler', 'defaults', 'list', '-s', ut_id(gvar, 'cld1')]
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'defaults', 'list', '-ok'],
        list='', columns=[]
    )

    execute_csv2_command(
        gvar, 0, None, 'defaults list, table #1 columns: keys=server, columns=cloud-address,cloud-enabled,cloud-name,cloud-password,cloud-project,cloud-project-domain,cloud-region,cloud-spot-price,cloud-type,cloud-user,cloud-user-domain,config-category,default-job-group,delete-cycle-interval,enable-glint,expose-API,file-path,group,group-manager,group-metadata-exclusion,group-metadata-option,group-name,group-option,help,job-cores,job-disk,job-hold,job-id,job-image,job-priority,job-ram,job-request-cpus,job-request-disk,job-request-ram,job-request-swap,job-requirements,job-status,job-swap,job-target-clouds,job-user,log-file,log-level,long-help,metadata-enabled,metadata-mime-type,metadata-name,metadata-priority,no-limit-default,no-view,only-keys,rotate,server,server-address,server-cacerts,server-grid-cert,server-grid-key,server-password,server-user,sleep-interval-cleanup,sleep-interval-command,sleep-interval-flavor,sleep-interval-image,sleep-interval-job,sleep-interval-keypair,sleep-interval-limit,sleep-interval-machine,sleep-interval-main-long,sleep-interval-main-short,sleep-interval-network,sleep-interval-vm,super-user,text-editor,user-common-name,user-option,user-password,username,view,view-columns,vm-cores,vm-disk,vm-flavor,vm-foreign,vm-hostname,vm-image,vm-keep-alive,vm-keypair,vm-option,vm-ram,vm-status,vm-swap,yes',
        ['cloudscheduler', 'defaults', 'list', '-VC']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'defaults', 'list', '-NV'],
        list='Defaults', columns=['server', 'cloud-address', 'cloud-enabled', 'cloud-name', 'cloud-password', 'cloud-project', 'cloud-project-domain', 'cloud-region', 'cloud-spot-price', 'cloud-type', 'cloud-user', 'cloud-user-domain', 'expose-API', 'file-path', 'group', 'group-manager', 'group-name', 'group-option', 'help', 'job-cores', 'job-disk', 'job-ram', 'job-swap', 'long-help', 'metadata-enabled', 'metadata-mime-type', 'metadata-name', 'metadata-priority', 'no-view', 'only-keys', 'rotate', 'server-address', 'server-grid-cert', 'server-grid-key', 'server-password', 'server-user', 'super-user', 'text-editor', 'user-common-name', 'user-password', 'user_option', 'username', 'view', 'view-columns', 'vm-cores', 'vm-disk', 'vm-flavor', 'vm-foreign', 'vm-hostname', 'vm-image', 'vm-keep-alive', 'vm-keypair', 'vm-option', 'vm-ram', 'vm-status', 'vm-swap', 'yes']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'defaults', 'list', '-V', 'server-address,server-user'],
        list='Defaults', columns=['server', 'server-address', 'server-user']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'defaults', 'list'],
        list='Defaults', columns=['server', 'server-address', 'server-user']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'defaults', 'list', '-V', ''],
        list='Defaults', columns=['server', 'cloud-address', 'cloud-enabled', 'cloud-name', 'cloud-password', 'cloud-project', 'cloud-project-domain', 'cloud-region', 'cloud-spot-price', 'cloud-type', 'cloud-user', 'cloud-user-domain', 'expose-API', 'file-path', 'group', 'group-manager', 'group-name', 'group-option', 'help', 'job-cores', 'job-disk', 'job-ram', 'job-swap', 'long-help', 'metadata-enabled', 'metadata-mime-type', 'metadata-name', 'metadata-priority', 'no-view', 'only-keys', 'rotate', 'server-address', 'server-grid-cert', 'server-grid-key', 'server-password', 'server-user', 'super-user', 'text-editor', 'user-common-name', 'user-password', 'user_option', 'username', 'view', 'view-columns', 'vm-cores', 'vm-disk', 'vm-flavor', 'vm-foreign', 'vm-hostname', 'vm-image', 'vm-keep-alive', 'vm-keypair', 'vm-option', 'vm-ram', 'vm-status', 'vm-swap', 'yes']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'defaults', 'list', '-r'],
        list='Defaults', columns=['Key', 'Value']
    )

    #### DELETE ####

    execute_csv2_command(
        gvar, 1, None, 'the following mandatory parameters must be specfied on the command line',
        ['cloudscheduler', 'defaults', 'delete']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'defaults', 'delete', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler defaults delete".',
        ['cloudscheduler', 'defaults', 'delete', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'defaults', 'delete', '-H']
    )

    execute_csv2_command(
        gvar, 1, None, 'Settings for server "invalid-unit-test" do not exist.',
        ['cloudscheduler', 'defaults', 'delete', '-s', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'defaults', 'delete', '-s', ut_id(gvar, 'cld1'), '-Y']
    )

    execute_csv2_command(
        gvar, None, None, None,
        ['cloudscheduler', 'defaults', '-s', 'unit-test']
    )

if __name__ == "__main__":
    main(None)
