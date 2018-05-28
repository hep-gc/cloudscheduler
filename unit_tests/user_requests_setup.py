#!/usr/bin/env python3
"""
Unit tests.
"""

from unit_test_common import execute_csv2_request, initialize_csv2_request
import sys

import user_requests_cleanup

def main(gvar):
    if not gvar:
        gvar = {}
        if len(sys.argv) > 1:
            initialize_csv2_request(gvar, sys.argv[0], selections=sys.argv[1])
        else:
            initialize_csv2_request(gvar, sys.argv[0])

    user_requests_cleanup.main(gvar)

    execute_csv2_request(
        gvar, 0, None, 'group "utg1" successfully added.',
        '/group/add/', form_data={'group_name': 'utg1', 'condor_central_manager': 'unit-test-group-one.ca'}
        )

    execute_csv2_request(
        gvar, 0, None, 'group "utg2" successfully added.',
        '/group/add/', form_data={'group_name': 'utg2', 'condor_central_manager': 'unit-test-group-one.ca'}
        )

    execute_csv2_request(
        gvar, 0, None, 'group "utg3" successfully added.',
        '/group/add/', form_data={'group_name': 'utg3', 'condor_central_manager': 'unit-test-group-one.ca'}
        )

if __name__ == "__main__":
    main(None)

