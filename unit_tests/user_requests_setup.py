#!/usr/bin/env python3
"""
Unit tests.
"""

from unit_test_common import execute_csv2_request, initialize_csv2_request, ut_id
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
        gvar, 0, None, 'group "%s" successfully added.' % ut_id(gvar, 'utg1'),
        '/group/add/', form_data={'group_name': ut_id(gvar, 'utg1'), 'condor_central_manager': 'unit-test-group-one.ca'}
        )

    execute_csv2_request(
        gvar, 0, None, 'group "%s" successfully added.' % ut_id(gvar, 'utg2'),
        '/group/add/', form_data={'group_name': ut_id(gvar, 'utg2'), 'condor_central_manager': 'unit-test-group-one.ca'}
        )

    execute_csv2_request(
        gvar, 0, None, 'group "%s" successfully added.' % ut_id(gvar, 'utg3'),
        '/group/add/', form_data={'group_name': ut_id(gvar, 'utg3'), 'condor_central_manager': 'unit-test-group-one.ca'}
        )

if __name__ == "__main__":
    main(None)

