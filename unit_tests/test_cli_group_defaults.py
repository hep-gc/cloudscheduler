from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id
import sys

# lno: GV - error code identifier.

def main(gvar, user_secret):
    if not gvar:
        gvar = {}
        if len(sys.argv) > 1:
            initialize_csv2_request(gvar, sys.argv[0], selections=sys.argv[1])
        else:
            initialize_csv2_request(gvar, sys.argv[0])
    
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}'.format(ut_id(gvar, '')[:-1]),
        ['cloudscheduler', 'group', 'defaults']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'group', 'defaults', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: group-name',
        ['cloudscheduler', 'group', 'defaults', '-gn', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'user settings for server "invalid-unit-test" does not contain a URL value.',
        ['cloudscheduler', 'group', 'defaults', '-s', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'You are not authorized to access object "group";',
        ['cloudscheduler', 'group', 'defaults', '-s', 'unit-test-un']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'group', 'defaults', '-s', 'unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler group defaults".',
        ['cloudscheduler', 'group', 'defaults', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'group', 'defaults', '-H']
    )

    execute_csv2_command(
        gvar, 0, None, 'Expose API requested',
        ['cloudscheduler', 'group', 'defaults', '-xA']
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'group', 'defaults', '-g', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, '')[:-1], ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'group', 'defaults', '-g', ut_id(gvar, 'clg1')]
    )

    execute_csv2_command(
        gvar, 1, 'GV07', 'value specified for "job_cpus" must be an integer value.',
        ['cloudscheduler', 'group', 'defaults', '-jc', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'GV07', 'value specified for "job_disk" must be an integer value.',
        ['cloudscheduler', 'group', 'defaults', '-jd', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-jed\', \'invalid-unit-test\']',
        ['cloudscheduler', 'group', 'defaults', '-jed', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'GV07', 'value specified for "job_ram" must be an integer value.',
        ['cloudscheduler', 'group', 'defaults', '-jr', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'GV07', 'value specified for "job_swap" must be an integer value.',
        ['cloudscheduler', 'group', 'defaults', '-js', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'GV07', 'value specified for "vm_keep_alive" must be an integer value.',
        ['cloudscheduler', 'group', 'defaults', '-vka', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'group defaults "{}" successfully updated.'.format(ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'group', 'defaults', '-jc', '1', '-jd', '1', '-jr', '1', '-js', '1', '-vka', '1', '-vi', '', '-vf', '', '-vn', '']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'group', 'defaults', '-ok'],
        list='Active Group Defaults', columns=['Group']
    )

    execute_csv2_command(
        gvar, 0, None, 'group defaults, table #1 columns: keys=group_name, columns=',
        ['cloudscheduler', 'group', 'defaults', '-VC']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'group', 'defaults', '-NV'],
        list='Active Group Defaults', columns=['VM', 'Job', 'Group', 'Flavor', 'Image', 'Keep Alive', 'Cores', 'Disk (GBs)', 'RAM (MBs)', 'Swap (GBs)']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'group', 'defaults', '-V', 'job_ram,vm_keep_alive'],
        list='Active Group Defaults', columns=['VM', 'Job', 'Group', 'Keep Alive', 'RAM (MBs)']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'group', 'defaults'],
        list='Active Group Defaults', columns=['VM', 'Job', 'Group', 'Keep Alive', 'RAM (MBs)']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'group', 'defaults', '-r'],
        list='Active Group Defaults', columns=['Key', 'Value']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'group', 'defaults', '-V', ''],
        list='Active Group Defaults', columns=['VM', 'Job', 'Group', 'Flavor', 'Image', 'Keep Alive', 'Cores', 'Disk (GBs)', 'RAM (MBs)', 'Swap (GBs)']
    )

if __name__ == "__main__":
    main(None)