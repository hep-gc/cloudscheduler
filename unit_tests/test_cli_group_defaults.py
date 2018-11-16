from unit_test_common import execute_csv2_command, initialize_csv2_request, ut_id
from sys import argv

# lno: GV - error code identifier.

def main(gvar, user_secret):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv2_request(gvar, argv[0])
    
    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}'.format(ut_id(gvar, '')[:-1]),
        ['cloudscheduler', 'metadata', 'group-defaults']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-xx\', \'yy\']',
        ['cloudscheduler', 'metadata', 'group-defaults', '-xx', 'yy']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were invalid: group-name',
        ['cloudscheduler', 'metadata', 'group-defaults', '-gn', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'user settings for server "invalid-unit-test" does not contain a URL value.',
        ['cloudscheduler', 'metadata', 'group-defaults', '-s', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'metadata', 'group-defaults', '-s', 'unit-test-un']
    )

    execute_csv2_command(
        gvar, 0, None, 'Help requested for "cloudscheduler metadata group-defaults".',
        ['cloudscheduler', 'metadata', 'group-defaults', '-h']
    )

    execute_csv2_command(
        gvar, 0, None, 'General Commands Manual',
        ['cloudscheduler', 'metadata', 'group-defaults', '-H']
    )

    execute_csv2_command(
        gvar, 0, None, 'Expose API requested',
        ['cloudscheduler', 'metadata', 'group-defaults', '-xA']
    )

    execute_csv2_command(
        gvar, 1, None, 'cannot switch to invalid group "invalid-unit-test".',
        ['cloudscheduler', 'metadata', 'group-defaults', '-g', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'Server: unit-test, Active User: {}, Active Group: {}'.format(ut_id(gvar, '')[:-1], ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'metadata', 'group-defaults', '-g', ut_id(gvar, 'clg1')]
    )

    execute_csv2_command(
        gvar, 1, 'GV07', 'value specified for "job_cpus" must be an integer value.',
        ['cloudscheduler', 'metadata', 'group-defaults', '-jc', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'GV07', 'value specified for "job_disk" must be an integer value.',
        ['cloudscheduler', 'metadata', 'group-defaults', '-jd', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, None, 'The following command line arguments were unrecognized: [\'-jed\', \'invalid-unit-test\']',
        ['cloudscheduler', 'metadata', 'group-defaults', '-jed', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'GV07', 'value specified for "job_ram" must be an integer value.',
        ['cloudscheduler', 'metadata', 'group-defaults', '-jr', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'GV07', 'value specified for "job_swap" must be an integer value.',
        ['cloudscheduler', 'metadata', 'group-defaults', '-js', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 1, 'GV07', 'value specified for "vm_keep_alive" must be an integer value.',
        ['cloudscheduler', 'metadata', 'group-defaults', '-vka', 'invalid-unit-test']
    )

    execute_csv2_command(
        gvar, 0, None, 'group defaults "{}" successfully updated.'.format(ut_id(gvar, 'clg1')),
        ['cloudscheduler', 'metadata', 'group-defaults', '-jc', '1', '-jd', '1', '-jr', '1', '-js', '1', '-vka', '1', '-vi', '', '-vk', '', '-vf', '', '-vn', '']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'metadata', 'group-defaults', '-ok'],
        list='Active Group Defaults', columns=['Group']
    )

    execute_csv2_command(
        gvar, 0, None, 'group defaults, table #1 columns: keys=group_name, columns=',
        ['cloudscheduler', 'metadata', 'group-defaults', '-VC']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'metadata', 'group-defaults', '-NV'],
        list='Active Group Defaults', columns=['VM', 'Job', 'Group', 'Flavor', 'Image', 'Keep Alive', 'Cores', 'Disk (GBs)', 'RAM (MBs)', 'Swap (GBs)']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'metadata', 'group-defaults', '-V', 'job_ram,vm_keep_alive'],
        list='Active Group Defaults', columns=['VM', 'Job', 'Group', 'Keep Alive', 'RAM (MBs)']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'metadata', 'group-defaults'],
        list='Active Group Defaults', columns=['VM', 'Job', 'Group', 'Keep Alive', 'RAM (MBs)']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'metadata', 'group-defaults', '-r'],
        list='Active Group Defaults', columns=['Key', 'Value']
    )

    execute_csv2_command(
        gvar, 0, None, None,
        ['cloudscheduler', 'metadata', 'group-defaults', '-V', ''],
        list='Active Group Defaults', columns=['VM', 'Job', 'Group', 'Flavor', 'Image', 'Keep Alive', 'Cores', 'Disk (GBs)', 'RAM (MBs)', 'Swap (GBs)']
    )

if __name__ == "__main__":
    main(None)