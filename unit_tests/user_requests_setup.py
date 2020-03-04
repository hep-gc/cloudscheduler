#!/usr/bin/env python3
"""
Unit tests.
"""

from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, generate_secret
from sys import argv

import user_requests_cleanup

def main(gvar):
    if not gvar:
        gvar = {}
        if len(argv) > 1:
            initialize_csv2_request(gvar, selections=argv[1])
        else:
            initialize_csv2_request(gvar)
    
    if not gvar['user_secret']:
        gvar['user_secret'] = generate_secret()

    user_requests_cleanup.main(gvar)

    # unprivileged user in no groups
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'utu1')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'utu1'),
            'password1': gvar['user_secret'],
            'password2': gvar['user_secret'],
            'cert_cn': ut_id(gvar, 'user test user 1')
        }
    )

    # privileged user in no groups
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'utu2')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'utu2'),
            'password1': gvar['user_secret'],
            'password2': gvar['user_secret'],
            'cert_cn': ut_id(gvar, 'user test user 2'),
            'is_superuser': 1
        }
    )

    # group with users
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'utg1')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'utg1'),
            'htcondor_fqdn': gvar['fqdn']
        }
    )

    # group without users
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'utg2')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'utg2'),
            'htcondor_fqdn': gvar['fqdn']
        }
    )

    # unprivileged user in utg1
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'utu3')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'utu3'),
            'password1': gvar['user_secret'],
            'password2': gvar['user_secret'],
            'cert_cn': ut_id(gvar, 'user test user three'),
            'group_name': ut_id(gvar, 'utg1')
        }
    )

    # privileged user in utg1
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'utu4')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'utu4'),
            'password': gvar['user_secret'],
            'cert_cn': '%s test user four' % ut_id(gvar, 'user'),
            'group_name': ut_id(gvar, 'utg1'),
            'is_superuser': 1
        }
    )

    # user to be deleted in test_user_delete
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'utu5')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'utu5'),
            'password': gvar['user_secret']
        }
    )

    # user to be updated in test_user_update
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'utu6')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'utu6'),
            'password': gvar['user_secret']
        }
    )

if __name__ == "__main__":
    main(None)
