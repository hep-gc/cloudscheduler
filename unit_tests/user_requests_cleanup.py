#!/usr/bin/env python3
"""
Unit tests.
"""

from unit_test_common import execute_csv2_request, initialize_csv2_request
import sys

def main(gvar):
    if not gvar:
        gvar = {}
        if len(sys.argv) > 1:
            initialize_csv2_request(gvar, sys.argv[0], selections=sys.argv[1])
        else:
            initialize_csv2_request(gvar, sys.argv[0])

    execute_csv2_request(
        gvar, None, None, None,
        '/user/delete/', form_data={'username': 'utu1'}
        )

    execute_csv2_request(
        gvar, None, None, None,
        '/user/delete/', form_data={'username': 'utu2'}
        )

    execute_csv2_request(
        gvar, None, None, None,
        '/user/delete/', form_data={'username': 'utu3'}
        )

    execute_csv2_request(
        gvar, None, None, None,
        '/user/delete/', form_data={'username': 'utu4'}
        )

    execute_csv2_request(
        gvar, None, None, None,
        '/user/delete/', form_data={'username': 'utu5'}
        )

    execute_csv2_request(
        gvar, None, None, None,
        '/user/delete/', form_data={'username': 'utu6'}
        )

    execute_csv2_request(
        gvar, None, None, None,
        '/user/delete/', form_data={'username': 'utu7'}
        )

    execute_csv2_request(
        gvar, None, None, None,
        '/group/delete/', form_data={'group_name': 'utg1'}
        )

    execute_csv2_request(
        gvar, None, None, None,
        '/group/delete/', form_data={'group_name': 'utg2'}
        )

    execute_csv2_request(
        gvar, None, None, None,
        '/group/delete/', form_data={'group_name': 'utg3'}
        )

if __name__ == "__main__":
    main(None)

