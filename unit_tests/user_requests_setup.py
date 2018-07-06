#!/usr/bin/env python3
"""
Unit tests.
"""

from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id, generate_secret
import sys

import user_requests_cleanup

def main(gvar, user_secret):
    if not gvar:
        gvar = {}
        if len(sys.argv) > 1:
            initialize_csv2_request(gvar, sys.argv[0], selections=sys.argv[1])
        else:
            initialize_csv2_request(gvar, sys.argv[0])
    
    if not user_secret:
        user_secret = generate_secret()

    user_requests_cleanup.main(gvar)

    # unprivileged user in no groups
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'utu1')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'utu1'),
            'password1': user_secret,
            'password2': user_secret,
            'cert_cn': ut_id(gvar, 'user test user one')
        }
    )

    # privileged user in no groups
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'utu2')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'utu2'),
            'password1': user_secret,
            'password2': user_secret,
            'cert_cn': ut_id(gvar, 'user test user two'),
            'is_superuser': 1
        }
    )

    # group with users
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'utg1')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'utg1'),
            'condor_central_manager': 'user-unit-test-one.ca'
        }
    )

    # group without users
    execute_csv2_request(
        gvar, 0, None, 'group "{}" successfully added.'.format(ut_id(gvar, 'utg2')),
        '/group/add/', form_data={
            'group_name': ut_id(gvar, 'utg2'),
            'condor_central_manager': 'user-unit-test-two.ca'
        }
    )

    # unprivileged user in utg1
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'utu3')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'utu3'),
            'password1': user_secret,
            'password2': user_secret,
            'cert_cn': ut_id(gvar, 'user test user three'),
            'group_name': ut_id(gvar, 'utg1')
        }
    )

    # privileged user in utg1
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'utu4')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'utu4'),
            'password': user_secret,
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
            'password': user_secret
        }
    )

    # user to be updated in test_user_update
    execute_csv2_request(
        gvar, 0, None, 'user "{}" successfully added.'.format(ut_id(gvar, 'utu6')),
        '/user/add/', form_data={
            'username': ut_id(gvar, 'utu6'),
            'password': user_secret
        }
    )

if __name__ == "__main__":
    main(None)

