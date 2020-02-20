from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, generate_secret, condor_setup, condor_error, _requests
from sys import argv
import subprocess
from time import sleep
import db_requests_cleanup

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv2_request(gvar, argv[0])
    if not gvar['user_secret']:
        gvar['user_secret'] = generate_secret()

    db_requests_cleanup.main(gvar)

    # 05 The test runner is added to this group so that they can submit jobs to it.
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'dtg1')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'dtg1'),
            'htcondor_fqdn': gvar['fqdn'],
            'username.1': gvar['user_settings']['server-user']
        }
    )

    # 06 group with no users
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'dtg2')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'dtg2'),
            'htcondor_fqdn': gvar['fqdn'],
        }
    )

    # 07 unprivileged user in dtg1
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'dtu1')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'dtu1'),
            'password1': gvar['user_secret'],
            'password2': gvar['user_secret'],
            'cert_cn': '{} test user one'.format(ut_id(gvar, 'database')),
            'group_name.1': ut_id(gvar, 'dtg1')
        }
    )

    # 08 user in no groups
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'dtu2')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'dtu2'),
            'password1': gvar['user_secret'],
            'password2': gvar['user_secret'],
            'cert_cn': '{} test user two'.format(ut_id(gvar, 'database')),
        }
    )

    JOB_PATH = 'db_job.sh'
    # If condor_setup encounters an error, it reports it and returns None.
    SERVER_ADDRESS = condor_setup(gvar)
    if SERVER_ADDRESS:
        # Change group in job to be submitted
        try:
            with open(JOB_PATH) as job_file:
                job_lines = job_file.readlines()
        except FileNotFoundError:
            condor_error(gvar, 'job file {} not found'.format(JOB_PATH))
            return
        for i, line in enumerate(job_lines):
            if line.startswith('Requirements'):
                job_lines[i] = 'Requirements = group_name =?= "{}" && TARGET.Arch == "x86_64"\n'.format(ut_id(gvar, 'dtg1'))
                break
        with open(JOB_PATH, 'w') as job_file:
            job_file.writelines(job_lines)
        # Submit a job for /job/list/ to the unit-test server using condor
        if subprocess.run(['condor_submit', JOB_PATH, '-name', SERVER_ADDRESS, '-pool', SERVER_ADDRESS], stdout=subprocess.DEVNULL).returncode != 0:
            condor_error(gvar, 'condor_submit failed')
            return
        # We need to wait a while for the job to be added to the database
        config_list = _requests(gvar, '/server/config', group=ut_id(gvar, 'dtg1'))['config_list']
        SLEEP_INTERVAL = next(int(d['config_value']) for d in config_list if d['category'] == 'csjobs.py' and d['config_key'] == 'sleep_interval_job')
        WE_WAIT = round(SLEEP_INTERVAL * 1.8)
        print('Waiting {} seconds for the submitted job to be added to the database.'.format(WE_WAIT))
        sleep(WE_WAIT)
    
if __name__ == "__main__":
    main(None)
