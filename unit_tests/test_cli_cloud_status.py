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
        ['cloudscheduler', 'cloud', 'status', '-xx', 'yy', '-s', 'unit-test-un']
    )

    # 02
    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: metadata-mime-type',
        ['cloudscheduler', 'cloud', 'status', '-mmt', 'invalid-unit-test']
    )

    # 03
    execute_csv2_command(
        gvar, 1, None, 'Error: the specified server "invalid-unit-test" does not exist in your defaults.',
        ['cloudscheduler', 'cloud', 'status', '-s', 'invalid-unit-test']
    )

    # 04
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'status', '-s', 'unit-test-un']
    )

    # 05
    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler cloud status".',
        ['cloudscheduler', 'cloud', 'status', '-h']
    )

    # 06
    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'cloud', 'status', '-H']
    )

    # 07
    execute_csv2_command(
        gvar, 0, None, 'Expose API requested',
        ['cloudscheduler', 'cloud', 'status', '-xA']
    )

    # 08
    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'cloud', 'status', '-g', 'invalid-unit-test']
    )

    # 09
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test-un, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'test'), ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'cloud', 'status', '-g', ut_id(gvar, 'clg1')]
    )

    # 10
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, '')[:-1], ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'cloud', 'status', '-g', ut_id(gvar, 'clg1'), '-s', 'unit-test']
    )

    # 11
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test-un, Active User: {}, Active Group: {}'.format(ut_id(gvar, 'test'), ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'cloud', 'status', '-s', 'unit-test-un']
    )

    # 12
    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'cloud', 'status', '-cn', 'invalid-unit-test']
    )

    # 13
    execute_csv2_command(
        gvar, 0, None, ut_id(gvar, 'clc2'),
        ['cloudscheduler', 'cloud', 'status']
    )

    # 14
    execute_csv2_command(
        gvar, 0, None, 'Rows: 1',
        ['cloudscheduler', 'cloud', 'status', '-cn', ut_id(gvar, 'clc2')]
    )

    # 15
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'status', '-ok'],
        list='Cloud status', columns=['Group', 'Cloud']
    )

    # 16
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'status', '-ok'],
        list='Job status', columns=['Group', 'Group', 'Cloud']
    )

    # 17
    execute_csv2_command(
        gvar, 0, None, 'cloud status, 1. Job status: keys=group_name, columns=Jobs,Idle,Running,Completed,Other\\ncloud status, 2. Cloud status: keys=group_name,cloud_name, columns=enabled,default_flavor,default_image,keep_alive,VMs,VMs_starting,VMs_unregistered,VMs_idle,VMs_running,VMs_retiring,VMs_manual,VMs_in_error,VMs_other,cores_max,cores_limit,cores_ctl,cores_idle,cores_native,ram_max,ram_limit,ram_ctl,ram_idle,ram_native,slot_count,slot_core_count,slot_idle_core_count,Foreign_VMs,cores_foreign,ram_foreign',
        ['cloudscheduler', 'cloud', 'status', '-NV', '-VC']
    )

    # 18
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'status', '-NV'],
        list='Cloud status', columns=['Group', 'Jobs', 'Idle', 'Running', 'Completed', 'Other', 'Defaults', 'VMs', 'Cores', 'Group', 'Cloud', 'Enabled', 'Flavor', 'Image', 'Keep', 'Alive', 'Total', 'Starting', 'Unregistered', 'idle', 'Running', 'Retiring', 'Manual', 'Error', 'Other', 'Quota', 'Cores', 'RAM', 'Condor', 'Slots', 'Foreign', 'Group', 'Cloud', 'Limit', 'Setting', 'Idle', 'Used', 'Quota', 'Limit', 'Setting', 'Idle', 'Used', 'Busy', 'Busy', 'Cores', 'Idle', 'Cores', 'VMs', 'Foreign', 'Group', 'Cloud', 'Cores', 'RAM']
    )

    # 19
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'status', '-NV'],
        list='Job status', columns=['Group', 'Jobs', 'Idle', 'Running', 'Completed', 'Other', 'Defaults', 'VMs', 'Cores', 'Group', 'Cloud', 'Enabled', 'Flavor', 'Image', 'Keep', 'Alive', 'Total', 'Starting', 'Unregistered', 'idle', 'Running', 'Retiring', 'Manual', 'Error', 'Other', 'Quota', 'Cores', 'RAM', 'Condor', 'Slots', 'Foreign', 'Group', 'Cloud', 'Limit', 'Setting', 'Idle', 'Used', 'Quota', 'Limit', 'Setting', 'Idle', 'Used', 'Busy', 'Busy', 'Cores', 'Idle', 'Cores', 'VMs', 'Foreign', 'Group', 'Cloud', 'Cores', 'RAM']
    )

    # 20
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'status', '-V', 'Jobs/enabled']
    )

    # 21
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'status'],
        list='Cloud status', columns=['Group', 'Jobs', 'Defaults', 'Group', 'Cloud', 'Enabled']
    )

    # 22
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'status'],
        list='Job status', columns=['Group', 'Jobs', 'Defaults', 'Group', 'Cloud', 'Enabled']
    )

    # 23
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'status', '-r'],
        list='Cloud status', columns=['Key', 'Value']
    )

    # 24
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'status', '-r'],
        list='Job status', columns=['Key', 'Value']
    )

    # 25
    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'status', '-V', '']
    )

if __name__ == "__main__":
    main(None)
