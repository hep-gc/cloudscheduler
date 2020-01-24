from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, condor_setup, condor_error
from sys import argv
import subprocess

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv2_request(gvar, argv[0])
    
    server_address = condor_setup(gvar)
    if not server_address:
        return
    # Remove all jobs submitted to dtg1
    # The return code is not checked because condor gives an error if there are no jobs to remove
    subprocess.run(['condor_rm', ut_id(gvar, 'dtg1'), '-name', server_address, '-pool', server_address], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 1
    execute_csv2_request(
        gvar, None, None, None,
        '/group/delete/', form_data={'group_name': ut_id(gvar, 'dtg1')}
    )

    # 2
    execute_csv2_request(
        gvar, None, None, None,
        '/user/delete/', form_data={'username': ut_id(gvar, 'dtu1')}
    )

if __name__ == "__main__":
    main(None)
