from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, generate_secret, condor_setup, condor_error
from sys import argv
import subprocess
import db_requests_cleanup

def main(gvar, user_secret):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, argv[0], selections=argv[1])
        else:
            initialize_csv2_request(gvar, argv[0])
    if not user_secret:
        user_secret = generate_secret()

    db_requests_cleanup.main(gvar)

    # 3 The test runner is added to this group so that they can submit jobs to it
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'dtg1')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'dtg1'),
            'htcondor_fqdn': 'csv2-dev.heprc.uvic.ca',
            'username.1': gvar['user_settings']['server-user']
        }
    )

    # 4
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'dtu1')),
        '/user/add/'
, form_data={
            'username': ut_id(gvar, 'dtu1'),
            'password1': user_secret,
            'password2': user_secret,
            'cert_cn': '{} test user one'.format(ut_id(gvar, 'database')),
            'group_name.1': ut_id(gvar, 'dtg1')
        }
    )

    # 5
    execute_csv2_request(
        gvar, 0, None, 'cloud "{}::{}" successfully added.'.format(ut_id(gvar, 'dtg1'), ut_id(gvar, 'dtc1')),
        '/cloud/add/', group=ut_id(gvar, 'dtg1'), form_data={
            'cloud_name': ut_id(gvar, 'dtc1'),
            'authurl': 'csv2-dev.heprc.uvic.ca',
            'project': 'db-test-cloud-one',
            'username': ut_id(gvar, 'dtu1'),
            'password': user_secret,
            'region': ut_id(gvar, 'dtr1'),
            'cloud_type': 'openstack'
        },
        server_user=ut_id(gvar, 'dtu1'), server_pw=user_secret
    )

    job_path = 'db_job.sh'
    server_address = condor_setup(gvar)
    if not server_address:
        return
    # Change group in job to be submitted.
    try:
        with open(job_path) as job_file:
            job_lines = job_file.readlines()
    except FileNotFoundError:
        condor_error(gvar, 'job file {} not found'.format(job_path))
        return
    for i, line in enumerate(job_lines):
        if line.startswith('Requirements'):
            job_lines[i] = 'Requirements = group_name =?= "{}" && TARGET.Arch == "x86_64"\n'.format(ut_id(gvar, 'dtg1'))
            break
    with open(job_path, 'w') as job_file:
        job_file.writelines(job_lines)
    # Submit a job for /job/list/ to the unit-test server using condor
    if subprocess.run(['condor_submit', job_path, '-name', server_address, '-pool', server_address], stdout=subprocess.DEVNULL).returncode != 0:
        condor_error(gvar, 'condor_submit failed')
        return

if __name__ == "__main__":
    main(None, None)
