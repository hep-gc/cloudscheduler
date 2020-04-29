from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, condor_setup
from sys import argv
import subprocess

def main(gvar):
    
    condor_setup(gvar)
    # Remove all jobs submitted by the test runner.
    # The return code is not checked because condor gives an error if there are no jobs to remove (and cleanup should not fail if run twice in a row).
    subprocess.run(['condor_rm', gvar['user_settings']['server-user'], '-name', gvar['fqdn'], '-pool', gvar['fqdn']], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 01
    execute_csv2_request(
        gvar, None, None, None,
        '/group/delete/', form_data={'group_name': ut_id(gvar, 'dtg1')}
    )

    # The test runner's active group might be dtg1, which we have just deleted. In this case we need to change their active group, but we don't know what the test runner's active group was before running the tests. So we just remove dtg1 and let the server figure out what group to make the active group.
    # Use .get() to avoid KeyErrors.
    if gvar['active_server_user_group'].get(gvar['user_settings']['server-address'], {}).get(gvar['user_settings']['server-user']) == ut_id(gvar, 'dtg1'):
        del gvar['active_server_user_group'][gvar['user_settings']['server-address']][gvar['user_settings']['server-user']]

    # 02
    execute_csv2_request(
        gvar, None, None, None,
        '/group/delete/', form_data={'group_name': ut_id(gvar, 'dtg2')}
    )

    # 03
    execute_csv2_request(
        gvar, None, None, None,
        '/user/delete/', form_data={'username': ut_id(gvar, 'dtu1')}
    )

    # 04
    execute_csv2_request(
        gvar, None, None, None,
        '/user/delete/', form_data={'username': ut_id(gvar, 'dtu2')}
    )

if __name__ == "__main__":
    main(initialize_csv2_request(selections=argv[1] if len(argv) > 1 else ''))
