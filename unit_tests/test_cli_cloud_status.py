from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id
import sys

# lno: CV - error code identifier.

def main(gvar, user_secret):
    if not gvar:
        gvar = {}
        if len(sys.argv) > 1:
            initialize_csv2_request(gvar, sys.argv[0], selections=sys.argv[1])
        else:
            initialize_csv2_request(gvar, sys.argv[0])

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'cloud', 'status', '-xx', 'yy', '-s', 'unit-test-un']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: metadata-mime-type',
        ['cloudscheduler', 'cloud', 'status', '-mmt', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'user settings for server "invalid-unit-test" does not contain a URL value.',
        ['cloudscheduler', 'cloud', 'status', '-s', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'status', '-s', 'unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler cloud status".',
        ['cloudscheduler', 'cloud', 'status', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'cloud', 'status', '-H']
    )

    execute_csv2_command(
        gvar, 0, None, 'Expose API requested',
        ['cloudscheduler', 'cloud', 'status', '-xA']
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'cloud', 'status', '-g', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, '')[:-1], ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'cloud', 'status', '-g', ut_id(gvar, 'clg1')]
    )

    execute_csv2_command(
        gvar, 0, None, 'Rows: 0',
        ['cloudscheduler', 'cloud', 'status', '-cn', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, ut_id(gvar, 'clc2'),
        ['cloudscheduler', 'cloud', 'status']
    )

    execute_csv2_command(
        gvar, 0, None, 'Rows: 1',
        ['cloudscheduler', 'cloud', 'status', '-cn', ut_id(gvar, 'clc2')]
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'status', '-ok'],
        list='Cloud status', columns=['Group', 'Cloud']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'status', '-ok'],
        list='Job status', columns=['Group']
    )

    execute_csv2_command(
        gvar, 0, None, 'cloud status, table #1 columns: keys=group_name, columns=Jobs,Idle,Running,Completed,Other\\ncloud status, table #2 columns: keys=group_name,cloud_name, columns=enabled,default_flavor,default_image,keep_alive,VMs,VMs_unregistered,VMs_running,VMs_retiring,VMs_manual,VMs_in_error,VMs_other,cores_max,cores_ctl,cores_idle,cores_native,ram_max,ram_ctl,ram_idle,ram_native,slots_max,slots_used,Foreign_VMs,cores_foreign,ram_foreign',
        ['cloudscheduler', 'cloud', 'status', '-VC']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'status', '-NV'],
        list='Cloud status', columns=['Defaults', 'VMs', 'Cores', 'Group', 'Cloud', 'Enabled', 'Flavor', 'Image', 'Keep Alive', 'Total', 'Unregistered', 'Running', 'Retiring', 'Manual', 'Error', 'Other', 'Setting', 'RAM', 'Slots', 'Foreign', 'Idle', 'Used']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'status', '-NV'],
        list='Job status', columns=['Group', 'Jobs', 'Idle', 'Running', 'Completed', 'Other']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'status', '-V', 'Jobs/enabled']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'status'],
        list='Cloud status', columns=['Defaults', 'Group', 'Cloud', 'Enabled']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'status'],
        list='Job status', columns=['Group', 'Jobs']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'status', '-r'],
        list='Cloud status', columns=['Key', 'Value']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'status', '-r'],
        list='Job status', columns=['Key', 'Value']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'cloud', 'status', '-V', '']
    )

if __name__ == "__main__":
    main(None)
