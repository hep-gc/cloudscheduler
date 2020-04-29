from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, generate_secret
from sys import argv
import vm_requests_cleanup

def main(gvar):
    
    vm_requests_cleanup.main(gvar)

    # 05 group with users
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'vtg1')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'vtg1'),
            'htcondor_fqdn': gvar['fqdn']
        }
    )

    # 06 group without users
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'vtg2')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'vtg2'),
            'htcondor_fqdn': gvar['fqdn']
        }
    )

    # 07 unprivileged user in vtg1
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'vtu1')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'vtu1'),
            'password1': gvar['user_secret'],
            'password2': gvar['user_secret'],
            'cert_cn': ut_id(gvar, 'vm test user 1'),
            'group_name.1': ut_id(gvar, 'vtg1')
        }
    )
    
    # 08 unprivileged user in no groups
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'vtu2')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'vtu2'),
            'password1': gvar['user_secret'],
            'password2': gvar['user_secret'],
            'cert_cn': ut_id(gvar, 'vm test user 2')
        }
    )
    
if __name__ == "__main__":
    main(initialize_csv2_request(selections=argv[1] if len(argv) > 1 else ''))
